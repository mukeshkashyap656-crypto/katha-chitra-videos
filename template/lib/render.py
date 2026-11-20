import math, json, wave, subprocess, sys, os
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chars import person, hexc, fill_stroke, ellipse, poly, OL
import scenes as S

W, H, FPS = 1080, 1920, 30
SX, SY = 40, 230           # scene area origin
D = "/home/claude/lak"
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
PREVIEW = "--preview" in sys.argv

lines = json.load(open(f"{D}/audio/lines.json"))
L = {l["id"]: l for l in lines}

# ---------------- timeline ----------------
plan = [
    (1, [("l01", 0.6)], 0.5),
    (2, [("l02", 0.3), ("l03", 0.4)], 0.6),
    (3, [("l04", 0.5)], 0.5),
    (4, [("l05", 0.4)], 0.6),
    (5, [("l06", 0.3), ("l07", 0.5)], 0.5),
    (6, [("l08", 0.8)], 1.6),
    (7, [("l09", 0.5)], 3.0),
]
SCN = []   # (scene, start, end)
t = 0.0
for sc, ls, tail in plan:
    st = t
    for lid, gap in ls:
        t += gap
        L[lid]["start"] = t
        t += L[lid]["dur"]
        L[lid]["end"] = t
    t += tail
    SCN.append((sc, st, t))
TOTAL = t
NF = int(math.ceil(TOTAL * FPS))
print("total", round(TOTAL, 2), "frames", NF)

# ---------------- lip-sync analysis ----------------
def load_wav(p):
    w = wave.open(p); n = w.getnframes(); sr = w.getframerate()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    return a, sr

MOUTH = {}
for l in lines:
    a, sr = load_wav(f"{D}/audio/{l['id']}.wav")
    l["_a"], l["_sr"] = a, sr
    if l["spk"] == "N":
        continue
    nfr = int(l["dur"] * FPS) + 1
    win = int(sr * 0.045)
    feats = []
    for k in range(nfr):
        c = int(k / FPS * sr)
        seg = a[max(0, c - win // 2): c + win // 2]
        if len(seg) < 64:
            feats.append((0, 0, 0)); continue
        rms = float(np.sqrt(np.mean(seg ** 2)))
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        fr = np.fft.rfftfreq(len(seg), 1 / sr)
        lo = sp[(fr > 200) & (fr < 900)].sum() + 1e-9
        mid = sp[(fr > 900) & (fr < 2000)].sum()
        hi = sp[(fr > 2000) & (fr < 4500)].sum()
        feats.append((rms, mid / lo, hi / lo))
    ref = np.percentile([f[0] for f in feats], 90) + 1e-9
    voiced = [f for f in feats if f[0] / ref >= 0.33] or feats
    m_lo = np.percentile([f[1] for f in voiced], 25)
    h_hi = np.percentile([f[2] for f in voiced], 80)
    rr = [f[0] / ref for f in feats]
    shapes = []
    for k, (rms, m, h) in enumerate(feats):
        r = rr[k]
        if r < 0.13: s = "X"
        elif 0 < k < len(rr) - 1 and r < 0.55 and rr[k - 1] > r and rr[k + 1] > r: s = "M"
        elif r < 0.33: s = "A"
        elif h >= h_hi: s = "E"
        elif m <= m_lo: s = "O"
        elif r > 0.75: s = "B"
        else: s = "A"
        shapes.append(s)
    # smooth: avoid 1-frame flicker
    for k in range(1, len(shapes) - 1):
        if shapes[k - 1] == shapes[k + 1] != shapes[k]:
            shapes[k] = shapes[k - 1]
    # closed lips briefly between words (M) when X sits between open shapes for 1 frame
    MOUTH[l["id"]] = shapes

SPEAKER_CHAR = {"G": "gangadhar", "E": "ellis", "R": "rani_w"}

def mouth_for(cname, tt):
    for l in lines:
        if l["spk"] != "N" and SPEAKER_CHAR[l["spk"]] == cname and l["start"] <= tt < l["end"]:
            k = int((tt - l["start"]) * FPS)
            sh = MOUTH[l["id"]]
            return sh[min(k, len(sh) - 1)]
    return "X"

def blink(tt, off):
    p = (tt + off) % 3.7
    return p < 0.12

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

# ---------------- text images ----------------
def text_surface(txt, size, col, font=FONT, maxw=900, align="center", lh=1.35, shadow=None):
    f = ImageFont.truetype(font, size, layout_engine=ImageFont.Layout.RAQM)
    words = txt.split(" "); rows = []; cur = ""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    for w_ in words:
        test = (cur + " " + w_).strip()
        if tmp.textlength(test, font=f) <= maxw: cur = test
        else: rows.append(cur); cur = w_
    rows.append(cur)
    rh = int(size * lh)
    im = Image.new("RGBA", (maxw + 20, rh * len(rows) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, r in enumerate(rows):
        tw = d.textlength(r, font=f)
        x = 10 + ((maxw - tw) / 2 if align == "center" else 0)
        if shadow:
            d.text((x + 3, 10 + i * rh + 3), r, font=f, fill=shadow)
        d.text((x, 10 + i * rh), r, font=f, fill=col)
    p = f"/tmp/txt_{abs(hash((txt, size, col)))}.png"
    im.save(p)
    return cairo.ImageSurface.create_from_png(p)

NAMES = {"G": "महाराजा गंगाधर राव", "E": "मेजर एलिस", "R": "रानी लक्ष्मीबाई"}
SUB = {}
for l in lines:
    clean = l["text"].replace("...", ",").replace(",,", ",")
    SUB[l["id"]] = (text_surface(clean, 50, (255, 244, 220), maxw=900, lh=1.45),
                    text_surface(NAMES[l["spk"]], 40, (240, 190, 60), maxw=900) if l["spk"] != "N" else None)

CAPS = {
    1: text_surface("झाँसी, 1853", 46, (255, 240, 210), maxw=420),
    3: text_surface("21 नवंबर 1853", 46, (255, 240, 210), maxw=420),
    4: text_surface("कलकत्ता", 46, (255, 240, 210), maxw=420),
    5: text_surface("मार्च 1854", 46, (255, 240, 210), maxw=420),
}
END1 = text_surface("आगे क्या हुआ?", 76, (255, 214, 90), maxw=900, shadow=(40, 10, 5))
END2 = text_surface("भाग 2 — जल्द आ रहा है", 52, (255, 244, 220), maxw=900, shadow=(40, 10, 5))
TITLE = text_surface("झाँसी की रानी", 66, (255, 226, 120), maxw=700)
TITLE2 = text_surface("भाग 1", 36, (255, 244, 220), maxw=300)

# ---------------- static frame (border, title, panel) ----------------
def make_frame():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source_rgb(*hexc("#6e1420")); c.paint()
    # inner pattern band
    c.set_source_rgb(*hexc("#8e1b2b")); c.rectangle(14, 14, W - 28, H - 28); c.fill()
    c.set_source_rgb(*hexc("#e8b730")); c.set_line_width(5); c.rectangle(16, 16, W - 32, H - 32); c.stroke()
    c.set_line_width(2.5); c.rectangle(28, 28, W - 56, H - 56); c.stroke()
    # dotted motifs along border
    for x in range(40, W - 30, 34):
        for y in (21, H - 21):
            c.arc(x, y, 3.5, 0, 6.3); c.fill()
    for y in range(40, H - 30, 34):
        for x in (21, W - 21):
            c.arc(x, y, 3.5, 0, 6.3); c.fill()
    # corner rosettes
    for cx, cy in ((34, 34), (W - 34, 34), (34, H - 34), (W - 34, H - 34)):
        for k in range(8):
            a = k * math.pi / 4
            ellipse(c, cx + math.cos(a) * 18, cy + math.sin(a) * 18, 10, 10); fill_stroke(c, "#f2a23a", 2.5)
        c.arc(cx, cy, 13, 0, 6.3); fill_stroke(c, "#e8b730", 3)
    # title cartouche
    c.move_to(150, 120); c.curve_to(150, 60, 220, 50, 300, 50); c.line_to(780, 50); c.curve_to(860, 50, 930, 60, 930, 120)
    c.curve_to(930, 180, 860, 200, 780, 200); c.line_to(300, 200); c.curve_to(220, 200, 150, 180, 150, 120); c.close_path()
    c.set_source_rgb(*hexc("#4a0c14")); c.fill_preserve(); c.set_source_rgb(*hexc("#e8b730")); c.set_line_width(5); c.stroke()
    for sx in (110, 970):
        ellipse(c, sx, 125, 26, 26); fill_stroke(c, "#e8b730", 3)
        ellipse(c, sx, 125, 12, 12); fill_stroke(c, "#b5262e", 2)
    c.set_source_surface(TITLE, W / 2 - TITLE.get_width() / 2, 52); c.paint()
    c.set_source_surface(TITLE2, W / 2 - TITLE2.get_width() / 2, 138); c.paint()
    # scene window border
    c.set_source_rgb(*hexc("#e8b730")); c.set_line_width(8)
    c.rectangle(SX - 6, SY - 6, S.SW + 12, S.SH + 12); c.stroke()
    # dialogue panel
    py = SY + S.SH + 34
    c.move_to(70, py); c.line_to(W - 70, py); c.curve_to(W - 40, py, W - 40, py + 30, W - 40, py + 60)
    c.line_to(W - 40, H - 120); c.curve_to(W - 40, H - 90, W - 70, H - 80, W - 100, H - 80)
    c.line_to(100, H - 80); c.curve_to(70, H - 80, 40, H - 90, 40, H - 120); c.line_to(40, py + 60)
    c.curve_to(40, py + 30, 40, py, 70, py); c.close_path()
    c.set_source_rgb(*hexc("#3a0a10")); c.fill_preserve(); c.set_source_rgb(*hexc("#e8b730")); c.set_line_width(5); c.stroke()
    c.set_line_width(2); c.rectangle(56, py + 14, W - 112, H - 80 - py - 28); c.stroke()
    return s, py

FRAME, PANEL_Y = make_frame()

# ---------------- scene drawing ----------------
def idle(tt, off=0, amp=3):
    return math.sin(tt * 2.2 + off) * amp

def draw_scene(c, sc, tt, lt):
    """tt = global time, lt = time since scene start"""
    if sc == 1:
        S.bg_fort(c, tt)
    elif sc == 2:
        S.bg_room(c, tt)
        S.diya(c, 70, 1150, tt); S.diya(c, 930, 1150, tt)
        S.stool(c, 150, 1060, 240, 150)
        S.bed(c, 480, 1080, 360)
        # Gangadhar propped in bed (upper body)
        gm = mouth_for("gangadhar", tt)
        speaking = gm != "X" or L["l03"]["start"] <= tt < L["l03"]["end"]
        g_arm = (0.25, 0.1, 1.2 if speaking else -0.25, -0.2 if speaking else -0.1)
        person(c, "gangadhar", 480, 1150 + idle(tt, 1, 2), 780, pose="bed", arms=g_arm, mouth=gm,
               blink=blink(tt, 0.4), emo="ill", look=0.5 if speaking else 0.0)
        S.quilt(c, 480, 1080, 360)
        # Rani (married look) seated on stool, looking at husband
        person(c, "rani_m", 150, 935 + idle(tt, 2, 2), 700, pose="sit", arms=(0.35, -0.9, -0.35, 0.9),
               blink=blink(tt, 1.3), emo="sad", look=0.6)
        # Damodar standing near bed
        person(c, "damodar", 735, 1110 + idle(tt, 3, 1.5), 400, blink=blink(tt, 2.1), look=-0.6)
        # Major Ellis witnessing
        person(c, "ellis", 900, 1150 + idle(tt, 4, 2), 780, arms=(0.15, 0.1, -0.15, -0.1), blink=blink(tt, 0.9),
               emo="neutral", look=-0.7)
    elif sc == 3:
        S.bg_room(c, tt, night=True)
        S.diya(c, 560, 920, tt, 1.1)
        writing = lt > 3.2
        # Rani in widow's white, seated behind low desk
        bow = 1.0 if not writing else 0.4
        hand_mv = math.sin(tt * 9) * 0.06 if writing else 0
        info = person(c, "rani_w", 380, 1130, 820, pose="sit",
                      arms=(0.2, 0.05, -1.0 + hand_mv, -0.75) if writing else (0.3, -0.8, -0.3, 0.8),
                      blink=blink(tt, 0.7), emo="sad", look=0.3 if writing else 0.0, bow=bow)
        S.desk(c, 400, 1170, 560, 250)
        S.inkpot(c, 600, 920)
        n_letters = 0 if not writing else min(4, int((lt - 3.2) / 1.2) + 1)
        for k in range(n_letters):
            S.letter_prop(c, 230 + k * 14, 905 - k * 12, ang=-0.08 + k * 0.05)
        if writing:
            S.letter_prop(c, 420, 915, 190, 120, ang=0.02, seal=False)
            hx, hy = info["hands"][1]
            S.quill(c, hx, hy, -0.5)
        person(c, "damodar", 800, 1150 + idle(tt, 3, 1.5), 420, blink=blink(tt, 2.5), emo="sad", look=-0.7)
    elif sc == 4:
        S.bg_office(c, tt)
        # Dalhousie behind desk: reads letter, shakes head, puts down
        shake = math.sin(lt * 10) * 0.35 if 1.6 < lt < 2.8 else 0.0
        reading = lt < 2.9
        arms = (-0.55, 1.45, 0.55, -1.45) if reading else (0.2, 0.6, -0.4, -0.8)
        c.save()
        info = person(c, "dalhousie", 500, 1180, 900, arms=arms, blink=blink(tt, 1.0),
                      emo="stern", look=shake * 2)
        c.restore()
        if reading:
            (x1, y1), (x2, y2) = info["hands"]
            S.letter_prop(c, (x1 + x2) / 2, (y1 + y2) / 2 + 60, 200, 140, ang=0)
        S.desk(c, 500, 1200, 700, 300)
        S.inkpot(c, 300, 900)
        if not reading:
            # letter set aside with a cross-mark of refusal (no text)
            S.letter_prop(c, 690, 885, 190, 120, ang=0.25)
    elif sc == 5:
        S.bg_darbar(c, tt)
        S.gaddi(c, 300, 1120, 440)
        rani_emo = "neutral"
        if tt > L["l07"]["start"] + 1.5: rani_emo = "firm"
        if tt > L["l07"]["start"] + 4.5: rani_emo = "angry"
        person(c, "rani_w", 300, 1040 + idle(tt, 2, 2), 780, pose="sit", arms=(0.35, -0.9, -0.35, 0.9),
               blink=blink(tt, 1.6), emo=rani_emo, look=0.7)
        person(c, "damodar", 560, 1120 + idle(tt, 3, 1.5), 420, blink=blink(tt, 2.2), look=0.7,
               emo="sad" if rani_emo == "angry" else "neutral")
        # Ellis walks in from the right during l06, then reads
        walk_end = L["l06"]["end"]
        p = ease((tt - L["l06"]["start"]) / max(0.1, walk_end - L["l06"]["start"]))
        ex = 1150 - (1150 - 830) * p
        walking = 0 < p < 1
        step = math.sin(tt * 8) * 6 if walking else 0
        reading = tt >= L["l07"]["start"] - 0.2
        arms = (-0.55, 1.45, 0.55, -1.45) if reading else (0.15 + step * 0.03, 0.1, -0.15 - step * 0.03, -0.1)
        info = person(c, "ellis", ex, 1170 - abs(step), 800, arms=arms, mouth=mouth_for("ellis", tt),
                      blink=blink(tt, 0.3), emo="stern", look=-0.8)
        if reading:
            S.scroll_prop(c, info["hands"], tt)
    elif sc == 6:
        # close-up: background darbar enlarged
        c.save(); c.translate(S.SW / 2, S.SH / 2); c.scale(1.6, 1.6); c.translate(-S.SW / 2, -S.SH / 2 + 120)
        S.bg_darbar(c, tt); c.restore()
        c.rectangle(0, 0, S.SW, S.SH); c.set_source_rgba(0.3, 0.05, 0.05, 0.25); c.fill()
        rise = ease(lt / 0.6)
        zoom = 1.0 + 0.06 * ease((lt - 0.5) / 3)
        c.save(); c.translate(S.SW / 2, S.SH * 0.55); c.scale(zoom, zoom); c.translate(-S.SW / 2, -S.SH * 0.55)
        person(c, "rani_w", 500, 2650 - rise * 60, 2600, arms=(0.12, 0.05, -0.12, -0.05),
               mouth=mouth_for("rani_w", tt), blink=blink(tt, 1.1) and tt < L["l08"]["start"], emo="angry")
        c.restore()
    elif sc == 7:
        S.bg_fort(c, tt, night=True)
        a = ease((lt - 0.3) / 0.8)
        c.save(); c.rectangle(0, 0, S.SW, S.SH); c.set_source_rgba(0, 0, 0, 0.35 * a); c.fill(); c.restore()
        if lt > L["l09"]["end"] - SCN[6][1] - 2.4:
            b = ease((lt - (L["l09"]["end"] - SCN[6][1] - 2.4)) / 0.6)
            c.set_source_surface(END1, S.SW / 2 - END1.get_width() / 2, 380); c.paint_with_alpha(b)
            c.set_source_surface(END2, S.SW / 2 - END2.get_width() / 2, 500); c.paint_with_alpha(b)

def caption(c, sc, lt):
    if sc in CAPS:
        a = ease(lt / 0.5) * (1 - ease((lt - 3.5) / 0.5))
        if a <= 0: return
        cs = CAPS[sc]; w = cs.get_width(); h = cs.get_height()
        c.save()
        c.rectangle(24, 24, w - 40 + 40, h + 6); c.set_source_rgba(*hexc("#4a0c14"), 0.85 * a); c.fill_preserve()
        c.set_source_rgba(*hexc("#e8b730"), a); c.set_line_width(4); c.stroke()
        c.set_source_surface(cs, 34 - 10 + (w - 40 + 40 - w) / 2, 27); c.paint_with_alpha(a)
        c.restore()

def current_line(tt):
    best = None
    for l in lines:
        if l["start"] - 0.15 <= tt < l["end"] + 0.35:
            best = l
    return best

def render_frame(fi):
    tt = fi / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    c.set_source_surface(FRAME, 0, 0); c.paint()
    sc, st, en = next(s for s in SCN if s[1] <= tt < s[2] or s is SCN[-1])
    lt = tt - st
    c.save(); c.translate(SX, SY); c.rectangle(0, 0, S.SW, S.SH); c.clip()
    # gentle camera push per scene
    z = 1.0 + 0.04 * (lt / max(1, en - st)) if sc != 6 else 1.0
    c.translate(S.SW / 2, S.SH / 2); c.scale(z, z); c.translate(-S.SW / 2, -S.SH / 2)
    draw_scene(c, sc, tt, lt)
    c.identity_matrix(); c.translate(SX, SY)
    caption(c, sc, lt)
    # fade between scenes
    fade = 0.0
    if lt < 0.35 and sc != 1: fade = 1 - lt / 0.35
    if en - tt < 0.35 and sc != SCN[-1][0]: fade = max(fade, 1 - (en - tt) / 0.35)
    if sc == 1 and lt < 0.5: fade = 1 - lt / 0.5
    if sc == SCN[-1][0] and en - tt < 0.6: fade = max(fade, 1 - (en - tt) / 0.6)
    if fade > 0:
        c.rectangle(0, 0, S.SW, S.SH); c.set_source_rgba(0.05, 0.01, 0.01, min(1, fade)); c.fill()
    c.restore()
    # subtitle
    l = current_line(tt)
    if l:
        a = min(1, (tt - (l["start"] - 0.15)) / 0.2, (l["end"] + 0.35 - tt) / 0.2)
        txt, nm = SUB[l["id"]]
        top = PANEL_Y + 30
        if nm:
            c.set_source_surface(nm, W / 2 - nm.get_width() / 2, top); c.paint_with_alpha(a); top += 62
        else:
            top += 18
        c.set_source_surface(txt, W / 2 - txt.get_width() / 2, top); c.paint_with_alpha(a)
    return surf

# ---------------- audio ----------------
def build_audio(path):
    sr = 44100
    n = int(TOTAL * sr) + sr
    mix = np.zeros(n, np.float32)
    for l in lines:
        a, s0 = l["_a"], l["_sr"]
        i = int(l["start"] * sr); mix[i:i + len(a)] += a * 0.95
    tt = np.arange(n) / sr
    # soft tanpura-like drone (D and A) with slow swell
    drone = np.zeros(n, np.float32)
    for f, amp in ((146.83, 1.0), (220.0, 0.6), (293.66, 0.5), (73.4, 0.5)):
        for h in range(1, 6):
            drone += (amp / h ** 1.3) * np.sin(2 * np.pi * f * h * tt + h) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * tt + f))
    drone /= np.abs(drone).max()
    env = np.clip(tt / 2.0, 0, 1) * np.clip((TOTAL - tt) / 2.0, 0, 1)
    duck = np.ones(n, np.float32)
    for l in lines:
        i0, i1 = int((l["start"] - 0.2) * sr), int((l["end"] + 0.2) * sr)
        duck[max(0, i0):i1] = 0.55
    duck = np.convolve(duck, np.ones(4410) / 4410, mode="same")
    mix += drone * env * duck * 0.10
    # drum hits (low thump): scene 1 start, Rani's line, end card
    def thump(at, gain=0.6):
        i = int(at * sr); k = np.arange(int(0.6 * sr)) / sr
        s = np.sin(2 * np.pi * (60 + 50 * np.exp(-k * 18)) * k) * np.exp(-k * 7) * gain
        mix[i:i + len(s)] += s[:max(0, min(len(s), n - i))]
    thump(0.3, 0.5); thump(L["l08"]["start"] - 0.25, 0.8); thump(SCN[4][1] + 0.1, 0.4)
    thump(L["l09"]["end"] - 2.3, 0.5)
    mix = mix[:int(TOTAL * sr)]
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    if PREVIEW:
        pts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        for p in pts:
            render_frame(int(p * FPS)).write_to_png(f"{D}/prev_{p:05.1f}.png")
        sys.exit()
    build_audio(f"{D}/mix.wav")
    out = f"{D}/lakshmibai_bhag1_test.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", f"{D}/mix.wav", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", out],
                          stdin=subprocess.PIPE)
    for fi in range(NF):
        ff.stdin.write(bytes(render_frame(fi).get_data()))
        if fi % 300 == 0: print("frame", fi, flush=True)
    ff.stdin.close(); ff.wait()
    print("done", out)
