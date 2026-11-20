import sys, math, wave, subprocess
sys.argv = ['x']; sys.path.insert(0, '/home/claude/lak')
import numpy as np, cairo
from PIL import Image
from chars import person, hexc, fill_stroke, ellipse, poly, OL
import scenes as S
import render as R
import ramtest as T

W, H, FPS = 1080, 1920, 30
SX, SY, SW, SH = 40, 230, 1000, 1220
D = "/home/claude/r10"
PREVIEW = "--preview" in sys.argv[1:] or (len(sys.argv) > 1)

def load(p):
    w = wave.open(p); sr = w.getframerate()
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, sr

vm, sr = load(f"{D}/audio/vm.wav"); nr, _ = load(f"{D}/audio/nr.wav")
VM0 = 0.7; VM1 = VM0 + len(vm) / sr
NR0 = VM1 + 0.45; NR1 = NR0 + len(nr) / sr
TOTAL = NR1 + 1.2
NF = int(TOTAL * FPS)
print("total", round(TOTAL, 2))

# ---- lip-sync shapes for Vishwamitra ----
def shapes_for(a):
    win = int(sr * 0.045); n = int(len(a) / sr * FPS) + 1; feats = []
    for k in range(n):
        c = int(k / FPS * sr); seg = a[max(0, c - win // 2): c + win // 2]
        if len(seg) < 64: feats.append((0, 0, 0)); continue
        rms = float(np.sqrt(np.mean(seg ** 2)))
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); fr = np.fft.rfftfreq(len(seg), 1 / sr)
        lo = sp[(fr > 200) & (fr < 900)].sum() + 1e-9
        feats.append((rms, sp[(fr > 900) & (fr < 2000)].sum() / lo, sp[(fr > 2000) & (fr < 4500)].sum() / lo))
    ref = np.percentile([f[0] for f in feats], 90) + 1e-9
    voiced = [f for f in feats if f[0] / ref >= 0.33] or feats
    m_lo = np.percentile([f[1] for f in voiced], 25); h_hi = np.percentile([f[2] for f in voiced], 80)
    rr = [f[0] / ref for f in feats]; out = []
    for k, (rms, m, h) in enumerate(feats):
        r = rr[k]
        if r < 0.13: s = "X"
        elif 0 < k < len(rr) - 1 and r < 0.55 and rr[k - 1] > r and rr[k + 1] > r: s = "M"
        elif r < 0.33: s = "A"
        elif h >= h_hi: s = "E"
        elif m <= m_lo: s = "O"
        elif r > 0.75: s = "B"
        else: s = "A"
        out.append(s)
    for k in range(1, len(out) - 1):
        if out[k - 1] == out[k + 1] != out[k]: out[k] = out[k - 1]
    return out
VMS = shapes_for(vm)

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def blink(t, off):
    return (t + off) % 3.6 < 0.12

# ---- camera keyframes (time, zoom, cx, cy) in scene coords ----
CAM = [(0, 1.0, 500, 610), (VM0, 1.0, 500, 610), (VM0 + 0.8, 1.45, 410, 905), (VM0 + 2.9, 1.5, 405, 905),
       (VM0 + 3.5, 1.4, 450, 905), (NR0 + 0.2, 1.4, 470, 915), (NR0 + 1.2, 1.45, 520, 935), (NR1, 1.2, 510, 820), (TOTAL, 1.15, 510, 800)]
def camera(t):
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM, CAM[1:]):
        if t0 <= t <= t1:
            p = ease((t - t0) / max(1e-6, t1 - t0))
            z = z0 + (z1 - z0) * p; cx = x0 + (x1 - x0) * p; cy = y0 + (y1 - y0) * p
            break
    else:
        _, z, cx, cy = CAM[-1]
    cx = min(max(cx, SW / 2 / z), SW - SW / 2 / z); cy = min(max(cy, SH / 2 / z), SH - SH / 2 / z)
    return z, cx, cy

HS = 420
BACK = [(80, "darbari"), (205, "darbari3"), (795, "darbari2"), (920, "darbari4")]
FRONT = [(90, "mantri2"), (910, "darbari")]

def background(c, t):
    T.dotted_wall(c, 0, SH); T.river(c, 640, 900)
    for ax in (190, 520, 850): T.round_arch(c, ax, 190, 300, 900)
    T.bunting(c, 60)
    T.garland(c, 60, 390, 150, 110); T.garland(c, 400, 700, 150, 110); T.garland(c, 700, 990, 150, 110)
    for px in (355, 690): T.diamond_pillar(c, px, 230, 900)
    T.sleepy_sun(c, 850, 300, 52)
    c.rectangle(0, 900, SW, SH - 900); c.set_source(S.grad(c, 900, SH, "#e07a3a", "#c8582a")); c.fill()
    c.set_source_rgba(*hexc("#f2c230"), 0.5); c.set_line_width(3)
    for k in range(-8, 14):
        c.move_to(k * 90, 900); c.line_to(k * 90 - 220, SH); c.stroke()
    c.rectangle(0, 850, SW, 40); fill_stroke(c, "#d9342b", 4)
    c.rectangle(0, 890, SW, 26); fill_stroke(c, "#8e1b2b", 4)
    c.set_source_rgb(*hexc("#f2c230"))
    for k in range(25): c.arc(20 + k * 40, 870, 5, 0, 6.3); c.fill()
    for k, (w_, y_) in enumerate(((330, 880), (280, 850))):
        c.rectangle(500 - w_ / 2, y_, w_, 32); fill_stroke(c, "#f2c230" if k else "#8e1b2b", 4)
    c.save(); c.translate(500, 862); c.scale(0.62, 0.62); T.throne(c, 0, 0); c.restore()
    T.chhatra(c, 500, 330, 190)

def scene(c, t):
    background(c, t)
    asked = t > VM0 + 1.3          # "bada putra Shriram" heard
    ten_days = t > VM0 + 3.2
    fainted = t > NR0 + 0.5
    # courtiers react: neutral -> worry -> shock, each a bit different
    for i, (x, who) in enumerate(BACK + FRONT):
        fy = 870 if (x, who) in BACK else 1190
        emo = "neutral"
        if asked: emo = "worry" if i % 2 else "sad"
        if t > VM1 + 0.1: emo = "shock" if i % 3 != 1 else "worry"
        look = 0.8 if x < 500 else -0.8
        ellipse(c, x, fy, 76, 16); fill_stroke(c, "#f2a23a", 3)
        person(c, who, x, fy - 4, HS, pose="sit", arms=(-0.15, 2.1, 0.15, -2.1), emo=emo, look=look,
               blink=blink(t, i * 0.7) and emo != "shock")
    # Vishwamitra (speaking)
    k = int((t - VM0) * FPS)
    vmm = VMS[min(k, len(VMS) - 1)] if VM0 <= t < VM1 else "X"
    gest = VM0 + 0.2 < t < VM1 + 0.3
    person(c, "vishwamitra2", 355, 1190, HS, arms=(0.12, 0.05, 0.55, -0.9) if gest else (0.12, 0.05, 0.15, -2.1),
           mouth=vmm, emo="stern" if gest else "neutral", look=0.8, blink=blink(t, 0.2))
    # Dasharatha: joy -> worry -> shock -> faints (sits down, head bowed)
    d_emo = "joy"
    if asked: d_emo = "worry"
    if ten_days: d_emo = "shock"
    d_mouth = "O" if ten_days and not fainted else "X"
    p = ease((t - (NR0 + 0.3)) / 0.45)
    if p <= 0:
        person(c, "dasharatha", 500, 1195, HS, arms=(-0.15, 2.1, 0.15, -2.1) if not ten_days else (0.35, -0.6, -0.35, 0.6),
               mouth=d_mouth, emo=d_emo, look=-0.8, blink=blink(t, 1.1) and d_emo != "shock")
    else:
        if p < 1:
            c.push_group()
            person(c, "dasharatha", 500, 1195 + p * 60, HS, arms=(0.35, -0.6, -0.35, 0.6), mouth="O", emo="shock", look=-0.8)
            c.pop_group_to_source(); c.paint_with_alpha(1 - p)
        c.push_group()
        person(c, "dasharatha", 500, 1195, HS, pose="sit", arms=(0.1, 0.1, -0.1, -0.1), emo="ill", bow=1.6,
               blink=True)
        c.pop_group_to_source(); c.paint_with_alpha(p)
    # Vasishtha: calm -> worried, leans toward the king after he faints
    v_emo = "neutral" if not asked else "worry"
    person(c, "vasishtha", 645, 1190, HS, arms=(-0.15, 2.1, 0.15, -2.1),
           emo=v_emo, look=-0.8, blink=blink(t, 2.3), bow=0.6 if fainted else 0)
    S.diya(c, 250, 1205, t); S.diya(c, 750, 1205, t)

# ---- static frame (border, title, logo, panel) ----
def static_frame():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source_rgb(*hexc("#7a1424")); c.paint()
    c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(4); c.rectangle(10, 10, W - 20, H - 20); c.stroke()
    for k in range(0, H, 40):
        for x in (22, W - 22):
            poly(c, [(x, k), (x + 9, k + 20), (x, k + 40), (x - 9, k + 20)]); fill_stroke(c, "#f2c230", 2)
    for k in range(0, W, 40):
        for y in (22, H - 22):
            poly(c, [(k, y), (k + 20, y - 9), (k + 40, y), (k + 20, y + 9)]); fill_stroke(c, "#f2c230", 2)
    c.rectangle(250, 48, 580, 150); c.set_source_rgb(*hexc("#5a0c18")); c.fill_preserve(); c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(5); c.stroke()
    c.rectangle(262, 60, 556, 126); c.set_line_width(2); c.stroke()
    t1 = R.text_surface("रामायण", 70, (255, 214, 90), maxw=520); t2 = R.text_surface("भाग 3 · विश्वामित्र के साथ राम", 34, (255, 244, 220), maxw=540)
    c.set_source_surface(t1, W / 2 - t1.get_width() / 2, 46); c.paint(); c.set_source_surface(t2, W / 2 - t2.get_width() / 2, 138); c.paint()
    py = SY + SH + 30
    c.rectangle(50, py, W - 100, H - 80 - py); c.set_source_rgb(*hexc("#3a0a10")); c.fill_preserve(); c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(5); c.stroke()
    c.rectangle(64, py + 14, W - 128, H - 80 - py - 28); c.set_line_width(2); c.stroke()
    return s, py
FRAME, PY = static_frame()
Image.open('/home/claude/cmp/logo_crop.png').save('/tmp/logo.png')
LOGO = cairo.ImageSurface.create_from_png('/tmp/logo.png')
SUBS = [(VM0, VM1, R.text_surface("महर्षि विश्वामित्र", 42, (240, 190, 60), maxw=900),
         R.text_surface("महाराज, मुझे आपका बड़ा पुत्र श्रीराम चाहिए, सिर्फ़ दस दिनों के लिए।", 50, (255, 244, 220), maxw=900, lh=1.45)),
        (NR0, NR1, None, R.text_surface("यह सुनते ही, राजा दशरथ बेहोश हो गए।", 50, (255, 244, 220), maxw=900, lh=1.45))]

def frame_at(fi):
    t = fi / FPS
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source_surface(FRAME, 0, 0); c.paint()
    c.save(); c.translate(SX, SY); c.rectangle(0, 0, SW, SH); c.clip()
    z, cx, cy = camera(t)
    c.translate(SW / 2, SH / 2); c.scale(z, z); c.translate(-cx, -cy)
    scene(c, t)
    c.restore()
    if t < 0.4:
        c.rectangle(SX, SY, SW, SH); c.set_source_rgba(0.05, 0.01, 0.01, 1 - t / 0.4); c.fill()
    if TOTAL - t < 0.4:
        c.rectangle(SX, SY, SW, SH); c.set_source_rgba(0.05, 0.01, 0.01, 1 - (TOTAL - t) / 0.4); c.fill()
    c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(8); c.rectangle(SX - 4, SY - 4, SW + 8, SH + 8); c.stroke()
    # logo small, right side, always
    c.save(); c.translate(925, 250); c.scale(0.55, 0.55); c.arc(100, 100, 98, 0, 6.3); c.clip(); c.set_source_surface(LOGO, 0, 0); c.paint(); c.restore()
    for a0, a1, nm, tx in SUBS:
        if a0 - 0.15 <= t < a1 + 0.4:
            al = min(1, (t - (a0 - 0.15)) / 0.2, (a1 + 0.4 - t) / 0.2)
            top = PY + 30
            if nm: c.set_source_surface(nm, W / 2 - nm.get_width() / 2, top); c.paint_with_alpha(al); top += 62
            else: top += 18
            c.set_source_surface(tx, W / 2 - tx.get_width() / 2, top); c.paint_with_alpha(al)
    return s

def audio(path):
    n = int(TOTAL * sr); mix = np.zeros(n + sr, np.float32)
    mix[int(VM0 * sr):int(VM0 * sr) + len(vm)] += vm; mix[int(NR0 * sr):int(NR0 * sr) + len(nr)] += nr * 0.95
    tt = np.arange(len(mix)) / sr
    drone = sum((a / h ** 1.3) * np.sin(2 * np.pi * f * h * tt + h) for f, a in ((146.83, 1), (220, .6), (73.4, .5)) for h in range(1, 6))
    drone = drone / np.abs(drone).max() * np.clip(tt / 1.5, 0, 1) * np.clip((TOTAL - tt) / 1.0, 0, 1)
    mix += drone.astype(np.float32) * 0.07
    def thump(at, g):
        i = int(at * sr); k = np.arange(int(0.6 * sr)) / sr
        x = np.sin(2 * np.pi * (60 + 50 * np.exp(-k * 18)) * k) * np.exp(-k * 7) * g; mix[i:i + len(x)] += x
    thump(VM0 + 3.2, 0.55); thump(NR0 + 0.35, 0.8)
    mix = mix[:n]; mix /= max(1, np.abs(mix).max() / 0.95)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    import sys as _s
    args = _s.argv_real if hasattr(_s, 'argv_real') else []
    out = f"{D}/ramayan_ram_maangna_10sec.mp4"
    audio(f"{D}/mix.wav")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", f"{D}/mix.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fi in range(NF):
        ff.stdin.write(bytes(frame_at(fi).get_data()))
    ff.stdin.close(); ff.wait(); print("done", out)
