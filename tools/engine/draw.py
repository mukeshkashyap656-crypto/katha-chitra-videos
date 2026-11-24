"""Katha Chitra scene engine, part 1: drawings + voices + sounds for ANY episode written as data.

The episode folder only needs episode.json with LINES + SHOTS (see tools/engine/README.md).
No episode code is needed, so a free AI only writes a small list, never Python.
Run (make_episode.sh does it): EP=/tmp/ep EPDIR=episodes/bhagN VOICE_ZIP=/tmp/ep/voice.zip python3 tools/engine/draw.py
"""
import sys, os, json, math, wave, random, subprocess, zipfile, shutil, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(REPO, "template", "lib"), HERE]
import numpy as np, cairo
import chars as C
from chars import person, hexc, fill_stroke, ellipse, poly, OL
import bglib
import spec as SP

B = os.environ.get("EP", "/tmp/ep"); OUT = f"{B}/proj/assets"; os.makedirs(OUT, exist_ok=True)
bglib.OUT = OUT
EPDIR = os.environ["EPDIR"]
EPI = SP.load(os.path.join(EPDIR, "episode.json"))

# ---------------- characters (fixed looks from the character bible) ----------------
C.CHARS["ram"] = dict(fw=0.95, fh=1.0, build=0.98, eye=1.15, nose=0.9, kind="m", skin="#4a68a8", hair="#140c08",
                      tunic="#f2c230", sash="#c0392b", upper="#2f8a4a", lower="#f2c230", hem="#c0392b",
                      crown=True, jewel=True, bare=True, skirt=1.4, mous=None)
C.CHARS["lakshman"] = dict(fw=0.93, fh=1.02, build=0.96, eye=1.08, nose=0.95, browt=1.2, kind="m", skin="#e0a878", hair="#140c08",
                           tunic="#e0552a", sash="#f2c230", upper="#f6f0e2", lower="#e0552a", hem="#f2c230",
                           crown=True, jewel=True, bare=True, skirt=1.4, mous=None)
# yagya rishis (bible): grey jata + saffron robe; black jata + white robe; both deer skin, rudraksha, tilak
C.CHARS["rishi_saffron"] = dict(C.CHARS["vasishtha"], fw=1.0, fh=1.0, stoop=0.1, age=2, hair="#9a9a9a", jatabun="#9a9a9a", beard="#b0b0b0",
                                mous="#b0b0b0", tunic="#e8902a", lower="#f2a03a", hem="#c0392b", ajina="#d8b07a")
C.CHARS["rishi_white"] = dict(C.CHARS["vasishtha"], fw=0.92, fh=1.06, stoop=0.0, age=1, hair="#1a0f0a", jatabun="#1a0f0a", beard="#2a1a10",
                              mous="#2a1a10", beardlen=1.2, tunic="#f6f0e2", lower="#f6f0e2", hem="#8a5a2a", ajina="#d8b07a")
# rakshasas (bible): Maricha blue skin, black clothes, red sash; Subahu maroon skin, dark beard, heavier, orange sash
C.CHARS["maricha"] = dict(fw=1.05, fh=1.05, build=1.15, eye=1.1, nose=1.1, browt=1.8, kind="m", skin="#3a5aa8", hair="#0c0b10",
                          tunic="#1a1a1e", sash="#c0392b", upper="#1a1a1e", lower="#1a1a1e", hem="#c0392b", jewel=True, bare=True,
                          skirt=1.4, mous="#0c0b10")
C.CHARS["subahu"] = dict(fw=1.12, fh=1.0, build=1.3, belly=1.2, eye=1.05, nose=1.15, browt=1.8, kind="m", skin="#7a2a2a", hair="#0c0b10",
                         tunic="#1a1a1e", sash="#e8902a", upper="#1a1a1e", lower="#1a1a1e", hem="#e8902a", jewel=True, bare=True,
                         skirt=1.4, mous="#0c0b10", beard="#0c0b10")
for k, v in EPI.get("NEW_CHARS", {}).items():          # new characters described as data (colours, size, glow)
    C.CHARS[k] = {kk: vv for kk, vv in v.items() if kk not in SP.NEWCHAR_META}

KS = 2.4615
ARMS = {"stand": (0.12, 0.05, -0.12, -0.05), "namaste": (-0.1, 2.18, 0.1, -2.18), "talk": (0.12, 0.05, 0.55, -0.9),
        "bless": (0.12, 0.05, 0.55, -0.9), "point": (0.12, 0.05, 1.25, 0.25), "raise": (0.12, 0.05, 2.45, 0.25),
        "walk": (0.12, 0.05, -0.12, -0.05), "sit": (-0.1, 2.18, 0.1, -2.18), "bow": (-0.1, 2.18, 0.1, -2.18),
        "angry": (0.6, 0.9, -0.6, -0.9)}
MOUTHS = ["X", "A", "B", "E", "O", "M"]


def horns_fangs(c, x, top, u):
    """Rakshasa marks (character bible): horns on the head, two fangs."""
    hy = top + 0.5 * u
    for s in (-1, 1):
        c.move_to(x + s * 0.32 * u, hy - 0.42 * u); c.curve_to(x + s * 0.55 * u, hy - 0.8 * u, x + s * 0.62 * u, hy - 1.0 * u, x + s * 0.5 * u, hy - 1.2 * u)
        c.curve_to(x + s * 0.4 * u, hy - 0.95 * u, x + s * 0.25 * u, hy - 0.7 * u, x + s * 0.16 * u, hy - 0.5 * u); c.close_path()
        fill_stroke(c, "#e8dcc0", 3)
        poly(c, [(x + s * 0.07 * u, hy + 0.2 * u), (x + s * 0.11 * u, hy + 0.34 * u), (x + s * 0.15 * u, hy + 0.2 * u)]); fill_stroke(c, "#ffffff", 2)


def glow(c, x, hy, u, kind):
    if kind == "gold":     # devta: golden rays + glow
        c.save(); c.translate(x, hy)
        for k in range(24):
            c.rotate(math.pi * 2 / 24); c.move_to(-0.06 * u, 0); c.line_to(0.06 * u, 0); c.line_to(0, -(1.35 + 0.25 * (k % 2)) * u); c.close_path()
            c.set_source_rgba(1, 0.85, 0.3, 0.55); c.fill()
        c.restore()
        g = cairo.RadialGradient(x, hy + 1.5 * u, 0.4 * u, x, hy + 1.5 * u, 3.0 * u)
        g.add_color_stop_rgba(0, 1, 0.92, 0.5, 0.6); g.add_color_stop_rgba(1, 1, 0.8, 0.2, 0); c.set_source(g); c.paint()
    elif kind == "dark":   # rakshasa: dark red-black glow
        g = cairo.RadialGradient(x, hy + 1.5 * u, 0.4 * u, x, hy + 1.5 * u, 3.0 * u)
        g.add_color_stop_rgba(0, 0.55, 0.05, 0.05, 0.6); g.add_color_stop_rgba(1, 0.1, 0, 0, 0); c.set_source(g); c.paint()


def draw_state(file, who, pose="stand", face="neutral", look=0.0, mouth="X", blink=False, shadow=False, walk=None, side=0, big=False):
    meta = SP.char_meta(who, EPI)
    big = big or meta.get("big", False)
    CW, CH, HS = (680, 900, 650) if big else (560, 760, 520)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(CW * KS), int(CH * KS)); c = cairo.Context(s); c.scale(KS, KS)
    x, feet = CW / 2, CH - 30
    H = HS * C.CHARS[who].get("tall", 1.0); u = H / 5.0; top = feet - H
    if not shadow and meta.get("glow"):
        glow(c, x, top + 0.5 * u, u, meta["glow"])
    if who in ("ram", "lakshman"):
        bglib.bow_back(c, x, feet - HS, HS / 5); bglib.quiver(c, x, feet - HS, HS / 5)
    C.WALK = walk; C.SIDE = side if walk is not None else 0
    person(c, who, x, feet, HS, pose="sit" if pose == "sit" else "stand", arms=(None if walk is not None else ARMS.get(pose, ARMS["stand"])), mouth=mouth,
           blink=blink, emo=face, look=look, bow=1.0 if pose == "bow" else 0.0)
    C.WALK = None; C.SIDE = 0
    if meta.get("rakshas"):
        horns_fangs(c, x, top, u)
    if shadow:   # first entry of a rakshasa: black shadow with glowing red eyes
        c.set_operator(cairo.OPERATOR_ATOP); c.set_source_rgb(0.03, 0.01, 0.01); c.paint(); c.set_operator(cairo.OPERATOR_OVER)
        for ex in (-0.16, 0.16):
            eg = cairo.RadialGradient(x + ex * u, top + 0.45 * u, 1, x + ex * u, top + 0.45 * u, 0.22 * u)
            eg.add_color_stop_rgba(0, 1, 0.2, 0.05, 1); eg.add_color_stop_rgba(1, 1, 0, 0, 0)
            c.set_source(eg); c.arc(x + ex * u, top + 0.45 * u, 0.22 * u, 0, 6.3); c.fill()
            c.set_source_rgb(1, 0.25, 0.05); ellipse(c, x + ex * u, top + 0.45 * u, 0.08 * u, 0.04 * u); c.fill()
    s.write_to_png(f"{OUT}/{file}.png")


# ---------------- backgrounds ----------------
WW, WH, K = 1360, 1660, 2
def canvas():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, WW * K, WH * K); c = cairo.Context(s); c.scale(K, K); return s, c

def hut(c, x, y, w):
    poly(c, [(x - w, y), (x - w, y - 0.8 * w), (x + w, y - 0.8 * w), (x + w, y)]); fill_stroke(c, "#c9955a", 4)
    poly(c, [(x - 1.25 * w, y - 0.75 * w), (x, y - 1.7 * w), (x + 1.25 * w, y - 0.75 * w)]); fill_stroke(c, "#a8823a", 4)
    c.set_source_rgb(*hexc("#7a5a2a")); c.set_line_width(3)
    for k in range(1, 6):
        c.move_to(x - 1.25 * w + k * 0.42 * w, y - 0.75 * w); c.line_to(x, y - 1.7 * w); c.stroke()
    poly(c, [(x - 0.25 * w, y), (x - 0.25 * w, y - 0.5 * w), (x + 0.25 * w, y - 0.5 * w), (x + 0.25 * w, y)]); fill_stroke(c, "#3a2414", 3)

def yagya_kund(c, x, y, w=150, fire=True):
    poly(c, [(x - w, y), (x - 0.8 * w, y - 0.35 * w), (x + 0.8 * w, y - 0.35 * w), (x + w, y)]); fill_stroke(c, "#b5562e", 4)
    for k in range(5):
        c.rectangle(x - w + k * 0.4 * w, y - 0.12 * w, 0.4 * w, 0.12 * w); fill_stroke(c, "#e8b730" if k % 2 else "#c0392b", 2)
    if fire:
        for dx, hh, col in ((-0.3, 0.9, "#e0552a"), (0.3, 0.85, "#e0552a"), (0, 1.25, "#f6a623"), (0, 0.7, "#ffe27a")):
            c.move_to(x + (dx - 0.25) * w, y - 0.35 * w)
            c.curve_to(x + (dx - 0.3) * w, y - 0.8 * w, x + dx * w, y - hh * w, x + dx * w, y - (hh + 0.2) * w)
            c.curve_to(x + dx * w, y - hh * w, x + (dx + 0.3) * w, y - 0.8 * w, x + (dx + 0.25) * w, y - 0.35 * w); c.close_path()
            fill_stroke(c, col, 3)

def bg_ashram(file):
    """Rishis' ashram in the forest: huts, tulsi, a yagya kund with fire in the middle."""
    rnd = random.Random(13); s, c = canvas()
    g = cairo.LinearGradient(0, 0, 0, 1100); g.add_color_stop_rgb(0, *hexc("#9cc9e0")); g.add_color_stop_rgb(1, *hexc("#f6dca8")); c.set_source(g); c.paint()
    bglib.folk_sun(c, 1120, 180, 80)
    for x, y, sc in ((280, 200, 100), (650, 140, 70)): bglib.swirl_cloud(c, x, y, sc)
    for y, sc, col, leaf, n in [(1000, 300, "#5f9a4a", "#3f7a34", 7), (1150, 340, "#4a8a3e", "#2f6a2a", 6)]:
        for k in range(n):
            bglib.tree(c, rnd, -60 + k * ((WW + 120) / (n - 1)) + rnd.uniform(-40, 40), y, sc * rnd.uniform(0.9, 1.1), col, leaf)
    for x, w in ((170, 120), (1190, 130)): hut(c, x, 1290, w)
    bglib.ground(c, rnd, 1380, "#9a7a4a", "#d9b47a", "#5a7a2a")
    yagya_kund(c, 680, 1500, 130)
    for x in (430, 930):   # tulsi on a small chaura
        c.rectangle(x - 45, 1430, 90, 60); fill_stroke(c, "#c0392b", 3)
        for k in range(7):
            ellipse(c, x + (k - 3) * 11, 1395 - abs(k - 3) * 8, 13, 22); fill_stroke(c, "#2f7a3a", 2)
    s.write_to_png(f"{OUT}/{file}.png")

def bg_river(file):
    """Folk river bank (Ganga / Sarayu / Shon): fish-scale waves, boat, trees on both banks."""
    rnd = random.Random(17); s, c = canvas()
    g = cairo.LinearGradient(0, 0, 0, 900); g.add_color_stop_rgb(0, *hexc("#8fc7e0")); g.add_color_stop_rgb(1, *hexc("#f6e2b0")); c.set_source(g); c.paint()
    bglib.folk_sun(c, 1080, 170, 75); bglib.swirl_cloud(c, 300, 170, 90)
    for k in range(9):
        bglib.tree(c, rnd, -40 + k * 175, 860, 220 * rnd.uniform(0.85, 1.1), "#4a8a3e", "#2f6a2a")
    c.rectangle(0, 860, WW, 460); c.set_source_rgb(*hexc("#3f8fc0")); c.fill()
    for row in range(9):          # fish-scale waves
        y = 890 + row * 48
        for k in range(-1, 30):
            c.arc(k * 52 + (26 if row % 2 else 0), y, 26, math.pi, 2 * math.pi)
            c.set_source_rgb(*hexc("#bfe3f2" if row % 2 else "#e8f6fb")); c.set_line_width(4); c.stroke()
    c.move_to(0, 860); c.line_to(WW, 860); c.set_source_rgb(*OL); c.set_line_width(4); c.stroke()
    bx, by = 980, 1020   # small boat
    c.move_to(bx - 130, by); c.curve_to(bx - 90, by + 50, bx + 90, by + 50, bx + 130, by); c.close_path(); fill_stroke(c, "#8a4a22", 4)
    c.move_to(bx, by); c.line_to(bx, by - 130); c.set_source_rgb(*OL); c.set_line_width(5); c.stroke()
    poly(c, [(bx + 4, by - 125), (bx + 90, by - 40), (bx + 4, by - 40)]); fill_stroke(c, "#f6f0e2", 3)
    bglib.ground(c, rnd, 1320, "#8a6a3a", "#d9b47a", "#5a7a2a")
    s.write_to_png(f"{OUT}/{file}.png")

def bg_palace(file):
    """Royal darbar: raised throne under a chhatra, cusped arches, diamond pillars, marigold torans, rangoli."""
    s, c = canvas()
    g = cairo.LinearGradient(0, 0, 0, WH); g.add_color_stop_rgb(0, *hexc("#7a1f2b")); g.add_color_stop_rgb(1, *hexc("#3a0e14")); c.set_source(g); c.paint()
    for k in range(4):   # cusped arches with a warm glow inside
        x = 170 + k * 340; c.move_to(x - 130, 1300); c.line_to(x - 130, 520)
        for j in range(5): c.arc(x - 104 + j * 52, 520 - 26 * math.sin(math.pi * (j + 0.5) / 5), 26, math.pi, 2 * math.pi)
        c.line_to(x + 130, 1300); c.close_path(); fill_stroke(c, "#f3c977", 5)
    for x in range(0, WW + 1, 340):   # diamond pillars
        c.rectangle(x - 34, 380, 68, 940); fill_stroke(c, "#c0392b", 4)
        for y in range(420, 1300, 80): poly(c, [(x, y), (x + 24, y + 40), (x, y + 80), (x - 24, y + 40)]); fill_stroke(c, "#e8b730", 3)
    c.rectangle(0, 330, WW, 60); fill_stroke(c, "#e8b730", 4)
    for k in range(28):   # marigold toran
        c.arc(25 + k * 50, 410 + 18 * math.sin(k), 16, 0, 6.3); fill_stroke(c, "#f6a623" if k % 2 else "#e0552a", 2)
    tx, ty = 680, 1180   # throne on steps under a royal umbrella
    for k in range(3): c.rectangle(tx - 260 + k * 40, ty + 110 - k * 40, 520 - k * 80, 40); fill_stroke(c, "#e8b730", 4)
    c.rectangle(tx - 120, ty - 200, 240, 200); fill_stroke(c, "#c0392b", 5)
    poly(c, [(tx - 140, ty - 200), (tx, ty - 330), (tx + 140, ty - 200)]); fill_stroke(c, "#e8b730", 5)
    poly(c, [(tx - 230, ty - 470), (tx, ty - 560), (tx + 230, ty - 470)]); fill_stroke(c, "#f6f0e2", 5)
    c.move_to(tx, ty - 470); c.line_to(tx, ty - 330); c.set_source_rgb(*OL); c.set_line_width(6); c.stroke()
    c.rectangle(0, 1320, WW, WH - 1320); c.set_source_rgb(*hexc("#c98a4a")); c.fill()
    for k in range(7):   # rangoli on the floor
        x = 100 + k * 195
        for r, col in ((70, "#c0392b"), (50, "#f2c230"), (30, "#2f8a4a")): ellipse(c, x, 1500, r, r * 0.4); fill_stroke(c, col, 3)
    s.write_to_png(f"{OUT}/{file}.png")

BG_FUNCS = {"morning": bglib.bg_morning, "divine": bglib.bg_divine, "cloudvan": bglib.bg_cloudvan,
            "ghorvan": lambda f: bglib.forest(f), "ashram": bg_ashram, "river": bg_river, "palace": bg_palace}

# ---------------- what has to be drawn (from the shot list) ----------------
for bg in sorted({sh["bg"] for sh in EPI["SHOTS"]} | {EPI["COVER"]["bg"]}):
    BG_FUNCS[bg](f"bg_{bg}")
print("backgrounds ok")

done = set()
for key, st in SP.all_states(EPI).items():
    if key in done: continue
    draw_state(key, **st); done.add(key)
print("characters:", len(done), "pictures")

def surf(w, h): s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); return s, cairo.Context(s)
s, c = surf(520, 640); bglib.glowdisc(c, 260, 320, 260, (1, 0.75, 0.2), 0.6); s.write_to_png(f"{OUT}/q_glow.png")
s, c = surf(300, 120)
for bx, by, sc in ((40, 60, 1.0), (140, 30, 0.8), (230, 75, 0.9)):
    c.move_to(bx - 30 * sc, by - 8 * sc); c.curve_to(bx - 15 * sc, by - 20 * sc, bx - 5 * sc, by - 5 * sc, bx, by)
    c.curve_to(bx + 5 * sc, by - 5 * sc, bx + 15 * sc, by - 20 * sc, bx + 30 * sc, by - 8 * sc)
    c.set_source_rgb(0.25, 0.18, 0.12); c.set_line_width(6 * sc); c.stroke()
s.write_to_png(f"{OUT}/birds.png")

# ---------------- voices: same loudness, short pauses, mouth shapes from the sound ----------------
z = zipfile.ZipFile(os.environ["VOICE_ZIP"]); z.extractall(f"{B}/audio2")
words = json.load(open(f"{B}/audio2/words.json"))
FPS = 30; SR = 44100
def to_wav(k):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{B}/audio2/{k}.mp3", "-ar", str(SR), "-ac", "1", f"{OUT}/{k}.wav"], check=True)
    w = wave.open(f"{OUT}/{k}.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close()
    ws = words[k]
    for i in range(1, len(ws)):   # shorten long pauses between words to 0.4 s
        gap = ws[i][1] - (ws[i - 1][1] + ws[i - 1][2])
        if gap > 0.55:
            cut = gap - 0.4; c0 = ws[i - 1][1] + ws[i - 1][2] + 0.18
            a = np.concatenate([a[:int(c0 * SR)], a[int((c0 + cut) * SR):]])
            for j in range(i, len(ws)): ws[j][1] -= cut
    st = max(0.0, ws[0][1] - 0.06)    # trim leading silence
    if st > 0.02:
        a = a[int(st * SR):]
        for j in range(len(ws)): ws[j][1] -= st
    end = ws[-1][1] + ws[-1][2] + 0.22; a = a[:int(end * SR)]
    a[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    fr = a[:len(a) // 441 * 441].reshape(-1, 441); e = np.sqrt((fr ** 2).mean(1))   # same loudness for every voice
    voiced = fr[e > e.max() * 0.15]; rms = np.sqrt((voiced ** 2).mean()) if len(voiced) else 0.1
    a = a * min(0.17 / max(rms, 1e-4), 0.97 / max(np.abs(a).max(), 1e-4))
    w = wave.open(f"{OUT}/{k}.wav", "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    return a
O_V = set("ोौूुउऊओऔ"); E_V = set("ेैिीइईएऐ")
lip = {}
for k in words:
    a = to_wav(k); d = len(a) / SR; n = int(d * FPS) + 1; win = int(SR * 0.045)
    rr = []
    for f in range(n):
        cc = int(f / FPS * SR); seg = a[max(0, cc - win // 2): cc + win // 2]
        rr.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) > 64 else 0)
    ref = np.percentile(rr, 90) + 1e-9; rr = [r / ref for r in rr]
    sh = []
    for f in range(n):
        t = f / FPS; wd = next((w for w in words[k] if w[1] <= t < w[1] + w[2]), None)
        if wd is None or rr[f] < 0.12: sh.append("X"); continue
        txt = wd[0]; pos = (t - wd[1]) / max(wd[2], 1e-3)
        vow = [ch for ch in txt if ch in O_V or ch in E_V]
        v = vow[min(int(pos * len(vow)), len(vow) - 1)] if vow else None
        if rr[f] < 0.35: s_ = "M" if txt[:1] in "मबपभ" and pos < 0.2 else "A"
        elif v in O_V: s_ = "O"
        elif v in E_V: s_ = "E"
        elif rr[f] > 0.8: s_ = "B"
        else: s_ = "A"
        sh.append(s_)
    for f in range(1, len(sh) - 1):
        if sh[f - 1] == sh[f + 1] != sh[f]: sh[f] = sh[f - 1]
    lip[k] = {"shapes": sh, "dur": d, "words": words[k], "text": EPI["LINES"][k][0]}
json.dump(lip, open(f"{B}/proj/lip.json", "w"), ensure_ascii=False)

# ---------------- sounds ----------------
for src, dst in (("shimmers/shimmer-short-sparkle", "sfx_spark"), ("shimmers/shimmer-medium-bright", "sfx_shimmer"),
                 ("cinematic-hits/cinematic-drum-big", "sfx_drum"), ("whooshes/whoosh-medium-medium", "sfx_whoosh"),
                 ("appear-and-vanish/appear-materialise", "sfx_appear"), ("whooshes/whoosh-slow-soft", "sfx_whoosh_soft"),
                 ("whooshes/whoosh-fast-hard", "sfx_swish"), ("impacts/impact-heavy-hard", "sfx_impact"),
                 ("cinematic-hits/cinematic-thunder-big", "sfx_thunder"), ("whooshes/whoosh-slow-hard", "sfx_whoosh_big")):
    f_ = os.path.join(REPO, "sfx", src + ".wav")
    if os.path.exists(f_): shutil.copy(f_, f"{OUT}/{dst}.wav")
    else:   # a missing sound must never stop the video: use a quiet stand-in
        print("awaaz nahi mili, chup wali laga rahe hain:", src); shutil.copy(os.path.join(REPO, "sfx", "whooshes/whoosh-slow-soft.wav"), f"{OUT}/{dst}.wav")
def save(name, x):
    x = np.clip(x, -1, 1); w = wave.open(f"{OUT}/{name}.wav", "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
rng = np.random.default_rng(3)
t = np.arange(int(SR * 60)) / SR    # morning forest: breeze + birds
amb = lowpass(rng.standard_normal(len(t)), 0.012) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t)) * 0.45
for k in range(70):
    t0 = rng.uniform(0, 59); f0 = rng.uniform(2600, 4200); i0 = int(t0 * SR)
    for j in range(rng.integers(2, 5)):
        tt = np.arange(int(0.07 * SR)) / SR; st = i0 + int(j * 0.11 * SR)
        if st + len(tt) < len(amb):
            amb[st:st + len(tt)] += np.sin(2 * np.pi * (f0 + 900 * tt / 0.07) * tt) * np.sin(np.pi * tt / 0.07) * 0.05
save("sfx_morning", amb)
dark = lowpass(rng.standard_normal(len(t)), 0.004) * 0.9 + np.sin(2 * np.pi * 55 * t) * 0.05   # dark forest drone
for k in range(10):
    i0 = int(rng.uniform(1, 57) * SR); tt = np.arange(int(0.5 * SR)) / SR
    dark[i0:i0 + len(tt)] += np.sin(2 * np.pi * 420 * tt) * np.exp(-tt * 6) * 0.08   # owl-like hoot
save("sfx_dark", dark)
pad = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((220, 0.08), (330, 0.06), (440, 0.04), (660, 0.02))) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.3 * t))
save("sfx_pad", pad)
tt = np.arange(int(SR * 0.08)) / SR
save("sfx_click", (rng.standard_normal(len(tt)) * np.exp(-tt * 90) * 0.7 + np.sin(2 * np.pi * 1600 * tt) * np.exp(-tt * 70) * 0.4))
tt = np.arange(int(SR * 1.4)) / SR
save("sfx_ting", sum((np.sin(2 * np.pi * 2093 * (tt - d)) + 0.5 * np.sin(2 * np.pi * 4186 * (tt - d))) * np.exp(-(tt - d) * 4) * (tt > d) for d in (0, 0.28)) * 0.25)
print("ok", {k: round(v["dur"], 2) for k, v in lip.items()})
