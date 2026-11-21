"""EXAMPLE from Bhag 4 test (Tataka ka van). Copy and change characters/states/background for each episode.
Run: EP=/home/claude/ep VOICE_ZIP=/path/voice.zip python3 draw_assets.py
"""

import sys, json, math, wave, random, os, subprocess, zipfile, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import numpy as np, cairo
import chars as C
from chars import person, hexc, fill_stroke, ellipse, poly, OL

B = os.environ.get("EP", "/home/claude/ep"); OUT = f"{B}/proj/assets"; os.makedirs(OUT, exist_ok=True)
HS = 520; CW, CH = 560, 760; KS = 2.4615   # drawn at 2.46x pixels, same proportions and line widths

C.CHARS["ram"] = dict(fw=0.95, fh=1.0, build=0.98, eye=1.15, nose=0.9, kind="m", skin="#4a68a8", hair="#140c08",
                      tunic="#f2c230", sash="#c0392b", upper="#2f8a4a", lower="#f2c230", hem="#c0392b",
                      crown=True, jewel=True, bare=True, skirt=1.4, mous=None)
C.CHARS["lakshman"] = dict(fw=0.93, fh=1.02, build=0.96, eye=1.08, nose=0.95, browt=1.2, kind="m", skin="#e0a878", hair="#140c08",
                           tunic="#e0552a", sash="#f2c230", upper="#f6f0e2", lower="#e0552a", hem="#f2c230",
                           crown=True, jewel=True, bare=True, skirt=1.4, mous=None)

def quiver(c, x, top, u, d=0):   # quiver on the back: top and feathers rise above the right shoulder
    c.save(); c.translate(x + (0.62 if not d else -0.34 * d) * u, top + 1.55 * u); c.rotate(0.32 if not d else -0.32 * d)
    for k in range(4):
        ax = -0.16 * u + k * 0.11 * u
        c.move_to(ax, -1.25 * u); c.line_to(ax, -1.05 * u); c.set_source_rgb(*OL); c.set_line_width(3); c.stroke()
        c.move_to(ax, -1.25 * u); c.line_to(ax - 0.07 * u, -1.55 * u); c.line_to(ax + 0.07 * u, -1.55 * u); c.close_path()
        fill_stroke(c, "#f6f0e2" if k % 2 else "#c0392b", 3)
    c.rectangle(-0.25 * u, -1.1 * u, 0.5 * u, 1.7 * u); fill_stroke(c, "#8a4a22", 4)
    for yy in (-1.1, -0.2, 0.45):
        c.rectangle(-0.25 * u, yy * u, 0.5 * u, 0.13 * u); fill_stroke(c, "#e8b730", 3)
    c.restore()

def bow_at(c, hx, hy, u, skin):   # bow gripped in the hand: grip at the fist, limbs curve outwards
    y0, y1 = hy - 1.55 * u, hy + 1.55 * u; bx = hx
    c.move_to(bx + 0.05 * u, y0); c.line_to(bx + 0.05 * u, y1); c.set_source_rgb(*hexc("#f6f0e2")); c.set_line_width(2.5); c.stroke()
    c.move_to(bx + 0.05 * u, y0); c.curve_to(bx - 0.5 * u, y0 + 0.6 * u, bx - 0.5 * u, y1 - 0.6 * u, bx + 0.05 * u, y1)
    c.set_source_rgb(*OL); c.set_line_width(15); c.stroke_preserve()
    c.set_source_rgb(*hexc("#a0662a")); c.set_line_width(8); c.stroke()
    gx = bx - 0.34 * u   # grip point on the curve, the fist closes over it
    c.arc(gx, hy, 0.13 * u, 0, 6.3); fill_stroke(c, skin, 4)
    c.move_to(gx - 0.1 * u, hy - 0.03 * u); c.line_to(gx + 0.1 * u, hy - 0.03 * u); c.move_to(gx - 0.1 * u, hy + 0.04 * u); c.line_to(gx + 0.1 * u, hy + 0.04 * u)
    c.set_source_rgb(*OL); c.set_line_width(2); c.stroke()

ARMS_BOW = (-0.42, 0.22, -0.12, -0.05)   # left (screen-left) arm slightly out, holding the bow

def draw_char(name, file, walk=None, side=0, **kw):
    # side = +1 / -1: side-view walk facing screen right / left; kw turn= head turn, bend= bow from waist (pranam),
    # bowpos = 0 bow in hand ... 1 bow slung on the back (smooth hand-over for pranam)
    C.WALK = walk; C.SIDE = side
    bowpos = kw.pop("bowpos", 0.0)
    stop = kw.pop("stop", None)       # 0..1 = real 'walk, then stop' (use with side=+-1); body travel = C.stop_disp(stop) * u
    if stop is not None:
        C.GAITOV = C.stop_pose(stop); walk = 0.0; C.WALK = 0.0
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(CW * KS), int(CH * KS)); c = cairo.Context(s); c.scale(KS, KS)
    x, feet = CW / 2, CH - 30
    archer = name in ("ram", "lakshman")
    turn = kw.get("turn"); bend = kw.get("bend", 0.0)
    d = side or (0 if not turn else (1 if turn > 0 else -1))
    tall = C.CHARS[name].get("tall", 1.0); u = HS * tall / 5.0; waist_y = feet - HS * tall + 2.35 * u
    if archer:
        kw.setdefault("arms", ARMS_BOW)
        tmp = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, CW, CH))
        info = person(tmp, name, x, feet, HS, **kw)
        c.save()
        if bend: c.translate(x, waist_y); c.rotate(bend); c.translate(-x, -waist_y)
        quiver(c, x, feet - HS, HS / 5, d)
        c.restore()
    info = person(c, name, x, feet, HS, **kw)
    if archer:
        hx, hy = info["hands"][0]; hx += 0.34 * info["u"]          # grip lands on the fist
        if bowpos:
            tx, ty = x - 0.55 * u * (d or 1), feet - HS * 0.5      # slung behind the back
            if bend:
                ca, sa = math.cos(bend), math.sin(bend); dx, dy = tx - x, ty - waist_y
                tx, ty = x + dx * ca - dy * sa, waist_y + dx * sa + dy * ca
            hx, hy = hx + (tx - hx) * bowpos, hy + (ty - hy) * bowpos
        bow_at(c, hx, hy, info["u"], C.CHARS[name]["skin"])
    s.write_to_png(f"{OUT}/{file}.png"); C.WALK = None; C.SIDE = 0; C.GAITOV = None

MOUTHS = ["X", "A", "B", "E", "O", "M"]
PH = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
for i, p in enumerate(PH):
    draw_char("lakshman", f"lak_walk{i}", walk=p, emo="neutral", look=0.8)
    draw_char("ram", f"ram_walk{i}", walk=p + 0.8, emo="neutral", look=0.8)
    draw_char("vishwamitra2", f"vm_walk{i}", walk=p + 1.6, emo="neutral", look=0.8)
# Ram asks calmly (curious, not scared), then firm and alert
for m in MOUTHS: draw_char("ram", f"ram_ask_{m}", mouth=m, emo="neutral", look=0.8)
draw_char("ram", "ram_ask_blink", emo="neutral", look=0.8, blink=True)
draw_char("ram", "ram_firm", emo="firm", look=0.8)
draw_char("ram", "ram_firm_blink", emo="firm", look=0.8, blink=True)
draw_char("lakshman", "lak_n", emo="neutral", look=0.8)
draw_char("lakshman", "lak_n_blink", emo="neutral", look=0.8, blink=True)
draw_char("lakshman", "lak_firm", emo="firm", look=0.8)
draw_char("lakshman", "lak_firm_blink", emo="firm", look=0.8, blink=True)
draw_char("vishwamitra2", "vm_stand", emo="neutral", look=0.8)
draw_char("vishwamitra2", "vm_stand_blink", emo="neutral", look=0.8, blink=True)
for i in range(1, 5):   # in-between frames: head turns to Ram and the hand rises smoothly
    f = i / 5; e = f * f * (3 - 2 * f)
    draw_char("vishwamitra2", f"vm_turn{i}", emo="stern" if f > 0.5 else "neutral", look=0.8 - 1.6 * e,
              arms=(0.12, 0.05, -0.12 + 0.67 * e, -0.05 - 0.85 * e))
for m in MOUTHS:
    draw_char("vishwamitra2", f"vm_talk_{m}", mouth=m, emo="stern", look=-0.8, arms=(0.12, 0.05, 0.55, -0.9))
draw_char("vishwamitra2", "vm_talk_blink", emo="stern", look=-0.8, arms=(0.12, 0.05, 0.55, -0.9), blink=True)

# ---- background: world 1360x1660, drawn at 2x; dense dark folk-art forest, richly decorated ----
WW, WH, K = 1360, 1660, 2
rnd = random.Random(11)
def dark_tree(c, x, y, s, col, leaf):
    c.move_to(x - 0.16 * s, y); c.curve_to(x - 0.05 * s, y - 0.5 * s, x - 0.2 * s, y - 0.8 * s, x - 0.07 * s, y - 1.1 * s)
    c.line_to(x + 0.07 * s, y - 1.1 * s); c.curve_to(x + 0.2 * s, y - 0.8 * s, x + 0.05 * s, y - 0.5 * s, x + 0.16 * s, y); c.close_path()
    fill_stroke(c, "#3a2414", 4)
    for k in range(3):   # folk pattern bands on the trunk
        yy = y - 0.25 * s - k * 0.28 * s
        c.move_to(x - 0.12 * s, yy); c.line_to(x + 0.12 * s, yy - 0.04 * s); c.set_source_rgb(*hexc("#6b4422")); c.set_line_width(5); c.stroke()
    for dx, dy, r in ((-0.45, -1.35, 0.5), (0.45, -1.4, 0.52), (0, -1.75, 0.6), (-0.2, -1.2, 0.45), (0.25, -1.15, 0.45)):
        ellipse(c, x + dx * s, y + dy * s, r * s, r * 0.85 * s); fill_stroke(c, col, 4)
    c.set_source_rgb(*hexc(leaf))
    for k in range(22):
        a = rnd.uniform(0, 6.28); rr = rnd.uniform(0.1, 0.7) * s
        lx, ly = x + math.cos(a) * rr, y - 1.45 * s + math.sin(a) * rr * 0.6
        c.save(); c.translate(lx, ly); c.rotate(a); ellipse(c, 0, 0, 0.09 * s, 0.035 * s); c.restore(); c.fill()
    for k in range(3):   # small dull folk flowers
        fx, fy = x + rnd.uniform(-0.6, 0.6) * s, y - 1.45 * s + rnd.uniform(-0.3, 0.3) * s
        for p in range(5):
            a = p * 1.2566; ellipse(c, fx + math.cos(a) * 9, fy + math.sin(a) * 9, 6, 6); c.set_source_rgb(*hexc("#8a3a2a")); c.fill()
        c.arc(fx, fy, 5, 0, 6.3); c.set_source_rgb(*hexc("#c99a2a")); c.fill()
def vine(c, x, y0, ln):
    c.move_to(x, y0)
    for k in range(6):
        c.curve_to(x + 14, y0 + ln * (k + 0.3) / 6, x - 14, y0 + ln * (k + 0.7) / 6, x, y0 + ln * (k + 1) / 6)
    c.set_source_rgb(*hexc("#16301e")); c.set_line_width(6); c.stroke()
    for k in range(6):
        ellipse(c, x + (9 if k % 2 else -9), y0 + ln * (k + 0.5) / 6, 11, 6); c.fill()
def owl(c, x, y):
    ellipse(c, x, y, 34, 44); fill_stroke(c, "#2a1a10", 4)
    poly(c, [(x - 30, y - 30), (x - 22, y - 58), (x - 8, y - 36)]); fill_stroke(c, "#2a1a10", 3)
    poly(c, [(x + 30, y - 30), (x + 22, y - 58), (x + 8, y - 36)]); fill_stroke(c, "#2a1a10", 3)
    for ex in (-13, 13):
        c.arc(x + ex, y - 12, 11, 0, 6.3); fill_stroke(c, "#e8b730", 3)
        c.arc(x + ex, y - 12, 4, 0, 6.3); c.set_source_rgb(0, 0, 0); c.fill()
def rock(c, x, y, w):
    c.move_to(x - w, y); c.curve_to(x - w, y - 0.7 * w, x + w * 0.6, y - 0.8 * w, x + w, y); c.close_path(); fill_stroke(c, "#4a4038", 4)
    c.move_to(x - w * 0.4, y - 0.3 * w); c.line_to(x + w * 0.2, y - 0.45 * w); c.set_source_rgb(*hexc("#6a5a4a")); c.set_line_width(3); c.stroke()
def forest(file, dread=0.0):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, WW * K, WH * K); c = cairo.Context(s); c.scale(K, K)
    g = cairo.LinearGradient(0, 0, 0, WH)
    g.add_color_stop_rgb(0, *hexc("#0e1d18")); g.add_color_stop_rgb(0.6, *hexc("#16301f")); g.add_color_stop_rgb(1, *hexc("#2a1d12"))
    c.set_source(g); c.paint()
    for y, sc, col, leaf, n in [(1020, 300, "#122a1c", "#0c1f14", 7), (1190, 360, "#18382a", "#0f2a1c", 6), (1340, 400, "#1d4430", "#123222", 5)]:
        for k in range(n):
            dark_tree(c, -60 + k * ((WW + 120) / (n - 1)) + rnd.uniform(-40, 40), y, sc * rnd.uniform(0.9, 1.1), col, leaf)
    for x in (90, 300, 560, 820, 1100, 1290): vine(c, x, 0, rnd.uniform(420, 760))
    c.move_to(0, 660); c.curve_to(120, 675, 220, 660, 300, 672); c.set_source_rgb(*hexc("#3a2414")); c.set_line_width(16); c.stroke()
    owl(c, 200, 622)
    c.rectangle(0, 1380, WW, WH - 1380); c.set_source_rgb(*hexc("#33241a")); c.fill()
    poly(c, [(0, 1450), (WW, 1420), (WW, 1640), (0, 1660)]); fill_stroke(c, "#7a5534", 4)
    for k in range(60):
        x = rnd.uniform(0, WW); y = rnd.choice([rnd.uniform(1385, 1440), rnd.uniform(1600, 1660)])
        for d in (-12, 0, 12):
            c.move_to(x, y); c.line_to(x + d, y - 30 - abs(d)); c.set_source_rgb(*hexc("#4a5a2a")); c.set_line_width(4); c.stroke()
    for x, w in ((150, 40), (470, 28), (900, 34), (1250, 42)): rock(c, x, 1452, w)
    for x in (60, 1300):
        ellipse(c, x, 1420, 150, 85); fill_stroke(c, "#122a1c", 5)
        c.set_source_rgb(*OL)
        for k in range(14):
            a = math.pi * (1 + k / 13); c.move_to(x + math.cos(a) * 140, 1420 + math.sin(a) * 78); c.line_to(x + math.cos(a) * 172, 1420 + math.sin(a) * 96)
        c.set_line_width(4); c.stroke()
    for ex in (48, 82):
        c.arc(ex, 1402, 7, 0, 6.3); c.set_source_rgb(1, 0.8, 0.2); c.fill()
    for k in range(18):   # faint fireflies
        c.arc(rnd.uniform(0, WW), rnd.uniform(500, 1350), 3, 0, 6.3); c.set_source_rgba(1, 0.9, 0.4, 0.55); c.fill()
    if dread:
        c.set_source_rgba(0.38, 0.02, 0.02, 0.42 * dread); c.paint()
    s.write_to_png(f"{OUT}/{file}.png")
forest("bg_forest"); forest("bg_dread", 1.0)

# flying birds layer (crows), animated across the sky
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 120); c = cairo.Context(s)
for bx, by, sc in ((40, 60, 1.0), (140, 30, 0.8), (230, 75, 0.9)):
    c.move_to(bx - 30 * sc, by - 8 * sc); c.curve_to(bx - 15 * sc, by - 20 * sc, bx - 5 * sc, by - 5 * sc, bx, by)
    c.curve_to(bx + 5 * sc, by - 5 * sc, bx + 15 * sc, by - 20 * sc, bx + 30 * sc, by - 8 * sc)
    c.set_source_rgb(0.03, 0.03, 0.03); c.set_line_width(7 * sc); c.stroke()
s.write_to_png(f"{OUT}/birds.png")

# Tataka teaser: huge black silhouette, wild hair, red eyes
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 700, 900); c = cairo.Context(s)
rg = cairo.RadialGradient(350, 420, 60, 350, 420, 420)
rg.add_color_stop_rgba(0, 0.45, 0.02, 0.02, 0.55); rg.add_color_stop_rgba(1, 0.2, 0, 0, 0)
c.set_source(rg); c.paint(); c.set_source_rgb(0.04, 0.02, 0.02)
for k in range(22):
    a = math.pi * (1.05 + k * 0.9 / 21); L = 260 + 50 * (k % 3)
    c.move_to(350 + math.cos(a - 0.08) * 170, 300 + math.sin(a - 0.08) * 170); c.line_to(350 + math.cos(a) * L, 300 + math.sin(a) * L)
    c.line_to(350 + math.cos(a + 0.08) * 170, 300 + math.sin(a + 0.08) * 170); c.close_path(); c.fill()
ellipse(c, 350, 320, 150, 170); c.fill()
poly(c, [(150, 900), (190, 520), (260, 450), (440, 450), (510, 520), (550, 900)]); c.fill()
for ex in (295, 405):
    eg = cairo.RadialGradient(ex, 320, 2, ex, 320, 40)
    eg.add_color_stop_rgba(0, 1, 0.25, 0.1, 1); eg.add_color_stop_rgba(1, 1, 0, 0, 0)
    c.set_source(eg); c.arc(ex, 320, 40, 0, 6.3); c.fill()
    c.set_source_rgb(1, 0.2, 0.05); ellipse(c, ex, 320, 22, 11); c.fill()
s.write_to_png(f"{OUT}/tataka_shadow.png")

# ---- voices (v2, exact word timings) ----
z = zipfile.ZipFile(os.environ["VOICE_ZIP"]); z.extractall(f"{B}/audio2")   # zip from voice_workbench.py, downloaded via Drive
words = json.load(open(f"{B}/audio2/words.json"))
FPS = 30; SR = 44100
def to_wav(k):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{B}/audio2/{k}.mp3", "-ar", str(SR), "-ac", "1", f"{OUT}/{k}.wav"], check=True)
    w = wave.open(f"{OUT}/{k}.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close()
    ws = words[k]
    for i in range(1, len(ws)):   # shorten long pauses between words to 0.45 s
        gap = ws[i][1] - (ws[i - 1][1] + ws[i - 1][2])
        if gap > 0.6:
            cut = gap - 0.45; c0 = ws[i - 1][1] + ws[i - 1][2] + 0.2
            a = np.concatenate([a[:int(c0 * SR)], a[int((c0 + cut) * SR):]])
            for j in range(i, len(ws)): ws[j][1] -= cut
    end = ws[-1][1] + ws[-1][2] + 0.25; a = a[:int(end * SR)]
    a[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    w = wave.open(f"{OUT}/{k}.wav", "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    return a
O_V = set("ोौूुउऊओऔ"); E_V = set("ेैिीइईएऐ")
lip = {}
for k in ("ram", "vm"):
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
        if rr[f] < 0.35: s_ = "M" if txt[0] in "मबपभ" and pos < 0.2 else "A"
        elif v in O_V: s_ = "O"
        elif v in E_V: s_ = "E"
        elif rr[f] > 0.8: s_ = "B"
        else: s_ = "A"
        sh.append(s_)
    for f in range(1, len(sh) - 1):
        if sh[f - 1] == sh[f + 1] != sh[f]: sh[f] = sh[f - 1]
    lip[k] = {"shapes": sh, "dur": d, "words": words[k]}
json.dump(lip, open(f"{B}/proj/lip.json", "w"), ensure_ascii=False)

# ---- sound effects, made in code ----
def save(name, x):
    x = np.clip(x, -1, 1); w = wave.open(f"{OUT}/{name}.wav", "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0; aa = np.broadcast_to(np.asarray(a, dtype=float), x.shape)
    for i in range(len(x)): acc += aa[i] * (x[i] - acc); y[i] = acc
    return y
rng = np.random.default_rng(3)
t = np.arange(int(SR * 16)) / SR   # forest ambience: low wind + far crickets + an owl hoot
wind = lowpass(rng.standard_normal(len(t)), 0.01) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t)) * 2.2
crick = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 28 * t) > 0.6) * (np.sin(2 * np.pi * 0.5 * t) > 0.2) * 0.03
amb = wind * 0.25 + crick
for t0 in (2.2, 2.75):
    i0 = int(t0 * SR); tt = np.arange(int(0.35 * SR)) / SR
    amb[i0:i0 + len(tt)] += np.sin(2 * np.pi * (390 - 40 * tt) * tt) * np.sin(np.pi * tt / 0.35) * 0.18
save("sfx_forest", amb)
tt = np.arange(int(SR * 1.6)) / SR   # Tataka reveal: deep drum boom + low rumble
boom = np.sin(2 * np.pi * (70 * np.exp(-tt * 2.5) + 38) * tt) * np.exp(-tt * 2.2) * 0.9
boom += lowpass(rng.standard_normal(len(tt)), 0.02) * np.exp(-tt * 1.5) * 1.5
save("sfx_boom", boom)
tt = np.arange(int(SR * 0.6)) / SR   # whoosh
wh = rng.standard_normal(len(tt)); wh = lowpass(wh, 0.05 + 0.25 * np.sin(np.pi * tt / 0.6)) * np.sin(np.pi * tt / 0.6) ** 2 * 1.6
save("sfx_whoosh", wh)
tt = np.arange(int(SR * 0.7)) / SR   # sparkle for the strength chip
sp = sum(np.sin(2 * np.pi * f * tt) * np.exp(-(tt - d) * 9) * (tt > d) for f, d in ((1800, 0), (2400, 0.07), (3000, 0.14), (3600, 0.2))) * 0.12
save("sfx_sparkle", sp)
tt = np.arange(int(SR * 0.08)) / SR   # subscribe click
save("sfx_click", (rng.standard_normal(len(tt)) * np.exp(-tt * 90) * 0.7 + np.sin(2 * np.pi * 1600 * tt) * np.exp(-tt * 70) * 0.4))
tt = np.arange(int(SR * 1.4)) / SR   # bell ting-ting
ting = sum((np.sin(2 * np.pi * 2093 * (tt - d)) + 0.5 * np.sin(2 * np.pi * 4186 * (tt - d))) * np.exp(-(tt - d) * 4) * (tt > d) for d in (0, 0.28)) * 0.25
save("sfx_ting", ting)
print("ok", {k: round(v["dur"], 2) for k, v in lip.items()})
