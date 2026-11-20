import sys, json, math, wave, random, os, subprocess, zipfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "template", "lib"))
import numpy as np, cairo
import chars as C
from chars import person, hexc, fill_stroke, ellipse, poly, OL

B = os.environ.get("EP", "/home/claude/ep"); OUT = f"{B}/proj/assets"; os.makedirs(OUT, exist_ok=True)
HS = 520; CW, CH = 560, 760; KS = 2.4615
ONLY = os.environ.get("ONLY", "")

C.CHARS["ram"] = dict(fw=0.95, fh=1.0, build=0.98, eye=1.15, nose=0.9, kind="m", skin="#4a68a8", hair="#140c08",
                      tunic="#f2c230", sash="#c0392b", upper="#2f8a4a", lower="#f2c230", hem="#c0392b",
                      crown=True, jewel=True, bare=True, skirt=1.4, mous=None)
C.CHARS["lakshman"] = dict(fw=0.93, fh=1.02, build=0.96, eye=1.08, nose=0.95, browt=1.2, kind="m", skin="#e0a878", hair="#140c08",
                           tunic="#e0552a", sash="#f2c230", upper="#f6f0e2", lower="#e0552a", hem="#f2c230",
                           crown=True, jewel=True, bare=True, skirt=1.4, mous=None)
C.CHARS["vaman"] = dict(fw=0.82, fh=0.85, build=0.85, eye=1.0, nose=0.9, kind="m", skin="#4a68a8", hair="#140c08",
                        tunic="#f6f0e2", sash="#f2c230", upper="#f2c230", lower="#f2c230", hem="#c0392b",
                        crown=False, jewel=True, bare=True, skirt=1.2, mous=None, janeu=True)
C.CHARS["bali"] = dict(fw=1.1, fh=1.05, build=1.15, eye=1.0, nose=1.1, kind="m", skin="#2e5c48", hair="#140c08",
                       tunic="#8e1b2b", sash="#f2c230", upper="#2e1b2b", lower="#8e1b2b", hem="#f2c230",
                       crown=True, jewel=True, bare=True, skirt=1.5, mous=None)

MOUTHS = ["X", "A", "B", "E", "O", "M"]
DEF = (0.12, 0.05, -0.12, -0.05)
NM = (-0.1, 2.18, 0.1, -2.18)

def quiver(c, x, top, u):
    c.save(); c.translate(x + 0.62 * u, top + 1.55 * u); c.rotate(0.32)
    for k in range(4):
        ax = -0.16 * u + k * 0.11 * u
        c.move_to(ax, -1.25 * u); c.line_to(ax, -1.05 * u); c.set_source_rgb(*OL); c.set_line_width(3); c.stroke()
        c.move_to(ax, -1.25 * u); c.line_to(ax - 0.07 * u, -1.55 * u); c.line_to(ax + 0.07 * u, -1.55 * u); c.close_path()
        fill_stroke(c, "#f6f0e2" if k % 2 else "#c0392b", 3)
    c.rectangle(-0.25 * u, -1.1 * u, 0.5 * u, 1.7 * u); fill_stroke(c, "#8a4a22", 4)
    for yy in (-1.1, -0.2, 0.45):
        c.rectangle(-0.25 * u, yy * u, 0.5 * u, 0.13 * u); fill_stroke(c, "#e8b730", 3)
    c.restore()

def bow_back(c, x, top, u):
    c.save(); c.translate(x - 0.1 * u, top + 2.2 * u); c.rotate(-0.42)
    L = 1.75 * u
    c.move_to(0.32 * u, -L); c.line_to(0.32 * u, L); c.set_source_rgb(*hexc("#f6f0e2")); c.set_line_width(2.5); c.stroke()
    c.move_to(0.32 * u, -L); c.curve_to(-0.3 * u, -L + 0.7 * u, -0.3 * u, L - 0.7 * u, 0.32 * u, L)
    c.set_source_rgb(*OL); c.set_line_width(15); c.stroke_preserve(); c.set_source_rgb(*hexc("#a0662a")); c.set_line_width(8); c.stroke()
    for yy in (-L + 0.05 * u, L - 0.05 * u):
        c.arc(0.3 * u, yy, 0.06 * u, 0, 6.3); fill_stroke(c, "#e8b730", 3)
    c.restore()

def draw_char(name, file, walk=None, **kw):
    if ONLY and ONLY != "chars": return
    C.WALK = walk
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(CW * KS), int(CH * KS)); c = cairo.Context(s); c.scale(KS, KS)
    x, feet = CW / 2, CH - 30
    if name in ("ram", "lakshman"):
        bow_back(c, x, feet - HS, HS / 5); quiver(c, x, feet - HS, HS / 5)
    person(c, name, x, feet, HS, **kw)
    s.write_to_png(f"{OUT}/{file}.png"); C.WALK = None

for st, emo in (("ram_n", "neutral"), ("ram_firm", "firm"), ("lak_n", "neutral"), ("vm_stand", "neutral"), ("vaman_n", "neutral")):
    draw_char("ram" if "ram" in st else ("lakshman" if "lak" in st else ("vishwamitra2" if "vm" in st else "vaman")), st, emo=emo, look=0.8 if "ram" in st else -0.8)
    draw_char("ram" if "ram" in st else ("lakshman" if "lak" in st else ("vishwamitra2" if "vm" in st else "vaman")), st + "_blink", emo=emo, look=0.8 if "ram" in st else -0.8, blink=True)
for m in MOUTHS:
    draw_char("vishwamitra2", f"vm_talk_{m}", mouth=m, emo="neutral", look=-0.8)
    draw_char("ram", f"ram_talk_{m}", mouth=m, emo="neutral", look=0.8)
draw_char("vishwamitra2", "vm_talk_blink", emo="neutral", look=-0.8, blink=True)
draw_char("ram", "ram_talk_blink", emo="neutral", look=0.8, blink=True)

# Backgrounds
WW, WH, K = 1360, 1660, 2
def bg_cloudvan(file):
    rnd = random.Random(9)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, WW * K, WH * K); c = cairo.Context(s); c.scale(K, K)
    g = cairo.LinearGradient(0, 0, 0, 1100)
    g.add_color_stop_rgb(0, *hexc("#7fb8dc")); g.add_color_stop_rgb(1, *hexc("#f6e2b0"))
    c.set_source(g); c.paint()
    c.rectangle(0, 1000, WW, 400); c.set_source_rgb(*hexc("#8fbf5a")); c.fill()
    puffs = [(400, 930, 130), (520, 860, 150), (660, 820, 170), (810, 850, 155), (940, 920, 130)]
    for cx_, cy_, r in puffs:
        ellipse(c, cx_, cy_, r, r * 0.82); fill_stroke(c, "#2f6a4e", 5)
    s.write_to_png(f"{OUT}/{file}.png")
bg_cloudvan("bg_cloudvan")
bg_cloudvan("bg_siddhashram")

s, c = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 120), cairo.Context(s)
for bx, by, sc in ((40, 60, 1.0), (140, 30, 0.8), (230, 75, 0.9)):
    c.move_to(bx - 30 * sc, by - 8 * sc); c.curve_to(bx - 15 * sc, by - 20 * sc, bx - 5 * sc, by - 5 * sc, bx, by)
    c.curve_to(bx + 5 * sc, by - 5 * sc, bx + 15 * sc, by - 20 * sc, bx + 30 * sc, by - 8 * sc)
    c.set_source_rgb(0.25, 0.18, 0.12); c.set_line_width(6 * sc); c.stroke()
s.write_to_png(f"{OUT}/birds.png")

if ONLY: sys.exit(0)
z = zipfile.ZipFile(os.environ["VOICE_ZIP"]); z.extractall(f"{B}/audio2")
words = json.load(open(f"{B}/audio2/words.json"))
FPS = 30; SR = 44100
def to_wav(k):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{B}/audio2/{k}.mp3", "-ar", str(SR), "-ac", "1", f"{OUT}/{k}.wav"], check=True)
    w = wave.open(f"{OUT}/{k}.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close()
    st = max(0.0, words[k][0][1] - 0.06)
    if st > 0.02:
        a = a[int(st * SR):]
        for j in range(len(words[k])): words[k][j][1] -= st
    end = words[k][-1][1] + words[k][-1][2] + 0.22; a = a[:int(end * SR)]
    w = wave.open(f"{OUT}/{k}.wav", "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    return a

lip = {}
for k in words:
    a = to_wav(k); d = len(a) / SR; n = int(d * FPS) + 1; win = int(SR * 0.045)
    sh = ["X" for _ in range(n)]
    lip[k] = {"shapes": sh, "dur": d, "words": words[k]}
lines = json.load(open(os.path.join(HERE, "episode.json"), encoding="utf-8"))["LINES"]
for k in lip: lip[k]["text"] = lines[k][0]
json.dump(lip, open(f"{B}/proj/lip.json", "w"), ensure_ascii=False)

for src, dst in (("shimmers/shimmer-short-sparkle", "sfx_spark"), ("cinematic-hits/cinematic-drum-big", "sfx_drum"), ("whooshes/whoosh-medium-medium", "sfx_whoosh")):
    shutil.copy(os.path.join(REPO, "sfx", src + ".wav"), f"{OUT}/{dst}.wav")
