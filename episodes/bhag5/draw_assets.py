"""Bhag 5 — Ram ko mile Divya Astra (Valmiki Bal Kand 27-28). Drawings, voices (lip), sound effects.
Run: EP=/tmp/ep VOICE_ZIP=/tmp/ep/voice.zip python3 draw_assets.py
"""
import sys, json, math, wave, random, os, subprocess, zipfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "template", "lib"))
import numpy as np, cairo
import chars as C
from chars import person, hexc, fill_stroke, ellipse, poly, OL

B = os.environ.get("EP", "/home/claude/ep"); OUT = f"{B}/proj/assets"; os.makedirs(OUT, exist_ok=True)
HS = 520; CW, CH = 560, 760; KS = 2.4615
ONLY = os.environ.get("ONLY", "")   # quick local tests: ONLY=chars / bg / icons

C.CHARS["ram"] = dict(fw=0.95, fh=1.0, build=0.98, eye=1.15, nose=0.9, kind="m", skin="#4a68a8", hair="#140c08",
                      tunic="#f2c230", sash="#c0392b", upper="#2f8a4a", lower="#f2c230", hem="#c0392b",
                      crown=True, jewel=True, bare=True, skirt=1.4, mous=None)
C.CHARS["lakshman"] = dict(fw=0.93, fh=1.02, build=0.96, eye=1.08, nose=0.95, browt=1.2, kind="m", skin="#e0a878", hair="#140c08",
                           tunic="#e0552a", sash="#f2c230", upper="#f6f0e2", lower="#e0552a", hem="#f2c230",
                           crown=True, jewel=True, bare=True, skirt=1.4, mous=None)
# astra devtas (Valmiki 27: some like burning coal, some like smoke, some bright like sun and moon) — bigger than humans, glowing
C.CHARS["dev_coal"] = dict(fw=1.02, fh=1.02, build=1.12, eye=1.05, nose=1.0, browt=1.3, kind="m", skin="#2e2c36", hair="#0c0b10",
                           tunic="#b8321f", sash="#ffb347", upper="#ff8a2a", lower="#8e1b1b", hem="#ffb347",
                           crown=True, jewel=True, bare=True, skirt=1.5, mous=None, bandcol="#ffb347")
C.CHARS["dev_smoke"] = dict(fw=0.98, fh=1.06, build=1.05, eye=1.0, nose=1.05, kind="m", skin="#9a9cab", hair="#4a4a58",
                            tunic="#e6e2f0", sash="#6a5aa8", upper="#b8b0dc", lower="#cfc8e6", hem="#6a5aa8",
                            crown=True, jewel=True, bare=True, skirt=1.5, mous=None)
C.CHARS["dev_sun"] = dict(fw=1.0, fh=1.0, build=1.1, eye=1.1, nose=0.95, kind="m", skin="#f0b440", hair="#1a0f0a",
                          tunic="#d9342b", sash="#fff0a0", upper="#f6f0e2", lower="#d9342b", hem="#fff0a0",
                          crown=True, jewel=True, bare=True, skirt=1.5, mous=None)

MOUTHS = ["X", "A", "B", "E", "O", "M"]
DEF = (0.12, 0.05, -0.12, -0.05)
NM = (-0.1, 2.18, 0.1, -2.18)            # folded hands (pranam) in front of the chest
TOUCH = (0.12, 0.05, 1.2, 0.3)        # right hand raised forward, palm towards the devtas (screen right)
VM_TALK = (0.12, 0.05, 0.55, -0.9)        # blessing hand (template look)
VM_GIVE = (0.12, 0.05, 2.45, 0.25)      # right hand raised high while giving the astras
def lerp(a, b, e): return tuple(x + (y - x) * e for x, y in zip(a, b))
def ease(f): return f * f * (3 - 2 * f)

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
    """Bow slung across the back (both hands are free to do pranam): top end above the left shoulder, lower end by the right leg."""
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

DCW, DCH = 680, 900; DHS = 650     # devtas: 1.25x human height
def draw_dev(name, file, glow, **kw):
    if ONLY and ONLY != "chars": return
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(DCW * KS), int(DCH * KS)); c = cairo.Context(s); c.scale(KS, KS)
    x, feet = DCW / 2, DCH - 30; u = DHS / 5; hy = feet - DHS + 0.5 * u
    rnd = random.Random(name)
    if glow == "coal":      # burning-coal glow: deep orange aura + ember sparks
        g = cairo.RadialGradient(x, hy + 1.5 * u, 0.4 * u, x, hy + 1.5 * u, 3.0 * u)
        g.add_color_stop_rgba(0, 1, 0.45, 0.08, 0.55); g.add_color_stop_rgba(1, 1, 0.3, 0.0, 0)
        c.set_source(g); c.paint()
        for k in range(26):
            c.arc(x + rnd.uniform(-2.2, 2.2) * u, hy + rnd.uniform(-0.6, 4.2) * u, rnd.uniform(2, 5), 0, 6.3); c.set_source_rgba(1, 0.6, 0.15, 0.8); c.fill()
    elif glow == "smoke":   # smoke-like: soft grey swirls around the body
        g = cairo.RadialGradient(x, hy + 1.5 * u, 0.4 * u, x, hy + 1.5 * u, 3.0 * u)
        g.add_color_stop_rgba(0, 0.85, 0.85, 0.95, 0.5); g.add_color_stop_rgba(1, 0.7, 0.7, 0.8, 0)
        c.set_source(g); c.paint()
        for k in range(16):
            cx_, cy_ = x + rnd.choice([-1, 1]) * rnd.uniform(0.9, 2.0) * u, hy + rnd.uniform(0.6, 4.3) * u; r = rnd.uniform(0.3, 0.55) * u
            g2 = cairo.RadialGradient(cx_, cy_, 0, cx_, cy_, r); g2.add_color_stop_rgba(0, 0.92, 0.92, 0.98, 0.55); g2.add_color_stop_rgba(1, 0.85, 0.85, 0.95, 0)
            c.set_source(g2); c.arc(cx_, cy_, r, 0, 6.3); c.fill()
    else:                   # sun-bright: golden rays
        c.save(); c.translate(x, hy)
        for k in range(24):
            c.rotate(math.pi * 2 / 24); c.move_to(-0.06 * u, 0); c.line_to(0.06 * u, 0); c.line_to(0, -(1.35 + 0.25 * (k % 2)) * u); c.close_path()
            c.set_source_rgba(1, 0.85, 0.3, 0.55); c.fill()
        c.restore()
        g = cairo.RadialGradient(x, hy + 1.5 * u, 0.4 * u, x, hy + 1.5 * u, 3.0 * u)
        g.add_color_stop_rgba(0, 1, 0.92, 0.5, 0.6); g.add_color_stop_rgba(1, 1, 0.8, 0.2, 0)
        c.set_source(g); c.paint()
    hg = cairo.RadialGradient(x, hy - 0.1 * u, 0.2 * u, x, hy - 0.1 * u, 1.0 * u)   # divine glow behind the head
    hg.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.75); hg.add_color_stop_rgba(1, 1, 0.8, 0.3, 0)
    c.set_source(hg); c.arc(x, hy - 0.1 * u, 1.0 * u, 0, 6.3); c.fill()
    person(c, name, x, feet, DHS, **kw)
    s.write_to_png(f"{OUT}/{file}.png")

# ---------------- characters ----------------
PH = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
for i, p in enumerate(PH):
    draw_char("lakshman", f"lak_walk{i}", walk=p, emo="neutral", look=0.8)
    draw_char("ram", f"ram_walk{i}", walk=p + 0.8, emo="neutral", look=0.8)
    draw_char("vishwamitra2", f"vm_walk{i}", walk=p + 1.6, emo="neutral", look=0.8)
# Ram
for st, emo in (("ram_n", "neutral"),):
    draw_char("ram", st, emo=emo, look=0.8); draw_char("ram", st + "_blink", emo=emo, look=0.8, blink=True)
for i in range(1, 4):   # hands slowly come together for pranam
    e = ease(i / 4); draw_char("ram", f"ram_nm{i}", emo="neutral", look=0.8, arms=lerp(DEF, NM, e))
    draw_char("lakshman", f"lak_nm{i}", emo="neutral", look=0.8, arms=lerp(DEF, NM, e))
draw_char("ram", "ram_nm", emo="smile", look=0.8, arms=NM); draw_char("ram", "ram_nm_blink", emo="smile", look=0.8, arms=NM, blink=True)
draw_char("lakshman", "lak_nm", emo="smile", look=0.8, arms=NM); draw_char("lakshman", "lak_nm_blink", emo="smile", look=0.8, arms=NM, blink=True)
for i in range(1, 5):   # from pranam, the right hand rises towards the devtas
    e = ease(i / 5); draw_char("ram", f"ram_tch{i}", emo="neutral", look=0.8, arms=lerp(NM, TOUCH, e))
for m in MOUTHS: draw_char("ram", f"ram_tch_{m}", mouth=m, emo="neutral", look=0.8, arms=TOUCH)
draw_char("ram", "ram_tch_blink", emo="neutral", look=0.8, arms=TOUCH, blink=True)
draw_char("ram", "ram_front", emo="neutral", look=0.0); draw_char("ram", "ram_front_blink", emo="neutral", look=0.0, blink=True)
for i in range(1, 4):   # head/eyes turn to the guru
    draw_char("ram", f"ram_turn{i}", emo="neutral", look=0.8 * ease(i / 4))
for m in MOUTHS: draw_char("ram", f"ram_talk_{m}", mouth=m, emo="neutral", look=0.8)
draw_char("ram", "ram_talk_blink", emo="neutral", look=0.8, blink=True)
# Lakshman
draw_char("lakshman", "lak_n", emo="neutral", look=0.8); draw_char("lakshman", "lak_n_blink", emo="neutral", look=0.8, blink=True)
# Vishwamitra
draw_char("vishwamitra2", "vm_stand", emo="neutral", look=-0.8); draw_char("vishwamitra2", "vm_stand_blink", emo="neutral", look=-0.8, blink=True)
draw_char("vishwamitra2", "vm_smile", emo="smile", look=-0.8); draw_char("vishwamitra2", "vm_smile_blink", emo="smile", look=-0.8, blink=True)
for i in range(1, 4):
    e = ease(i / 4); draw_char("vishwamitra2", f"vm_up{i}", emo="smile", look=-0.8, arms=lerp(DEF, VM_TALK, e))
for m in MOUTHS: draw_char("vishwamitra2", f"vm_talk_{m}", mouth=m, emo="smile", look=-0.8, arms=VM_TALK)
draw_char("vishwamitra2", "vm_talk_blink", emo="smile", look=-0.8, arms=VM_TALK, blink=True)
for i in range(1, 4):
    e = ease(i / 4); draw_char("vishwamitra2", f"vm_g{i}", emo="neutral", look=-0.8, arms=lerp(VM_TALK, VM_GIVE, e))
draw_char("vishwamitra2", "vm_give", emo="neutral", look=-0.8, arms=VM_GIVE); draw_char("vishwamitra2", "vm_give_blink", emo="neutral", look=-0.8, arms=VM_GIVE, blink=True)
# devtas (all three speak together)
for nm_, gl in (("dev_coal", "coal"), ("dev_smoke", "smoke"), ("dev_sun", "sun")):
    for m in MOUTHS: draw_dev(nm_, f"{nm_}_{m}", gl, mouth=m, emo="smile", look=-0.6, arms=NM)
    draw_dev(nm_, f"{nm_}_blink", gl, emo="smile", look=-0.6, arms=NM, blink=True)

# ---------------- icons ----------------
def surf(w, h): s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); return s, cairo.Context(s)
def glowdisc(c, x, y, r, col, a=0.75):
    g = cairo.RadialGradient(x, y, 0, x, y, r); g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g); c.arc(x, y, r, 0, 6.3); c.fill()
def chakra(file, col, rim="#e8b730", W=360):
    s, c = surf(W, W); x = y = W / 2; R = W * 0.36
    glowdisc(c, x, y, W / 2, (1, 0.8, 0.25), 0.7)
    c.save(); c.translate(x, y)
    for k in range(16):    # sharp teeth
        c.rotate(math.pi / 8); c.move_to(R * 0.92, -R * 0.12); c.line_to(R * 1.22, 0); c.line_to(R * 0.92, R * 0.12); c.close_path(); fill_stroke(c, rim, 3)
    c.restore()
    c.arc(x, y, R, 0, 6.3); fill_stroke(c, rim, 5)
    c.arc(x, y, R * 0.78, 0, 6.3); fill_stroke(c, col, 4)
    c.set_source_rgb(*OL); c.set_line_width(4)
    for k in range(12):
        a = k * math.pi / 6; c.move_to(x + math.cos(a) * R * 0.22, y + math.sin(a) * R * 0.22); c.line_to(x + math.cos(a) * R * 0.76, y + math.sin(a) * R * 0.76); c.stroke()
    for k in range(12):
        a = k * math.pi / 6 + math.pi / 12; c.arc(x + math.cos(a) * R * 0.55, y + math.sin(a) * R * 0.55, R * 0.06, 0, 6.3); fill_stroke(c, rim, 2)
    c.arc(x, y, R * 0.24, 0, 6.3); fill_stroke(c, rim, 4)
    c.arc(x, y, R * 0.1, 0, 6.3); fill_stroke(c, "#c0392b", 3)
    s.write_to_png(f"{OUT}/{file}.png")
def vajra(file, W=360):
    s, c = surf(W, W); x = y = W / 2
    glowdisc(c, x, y, W / 2, (0.6, 0.8, 1), 0.7)
    for sgn in (-1, 1):
        for dx in (-1, 0, 1):   # three prongs each end
            c.move_to(x + dx * 18, y + sgn * 40); c.curve_to(x + dx * 60, y + sgn * 80, x + dx * 40, y + sgn * 120, x + dx * 8, y + sgn * 150)
            c.set_source_rgb(*OL); c.set_line_width(16); c.stroke_preserve(); c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(9); c.stroke()
        ellipse(c, x, y + sgn * 40, 34, 16); fill_stroke(c, "#e8b730", 4)
    c.rectangle(x - 16, y - 40, 32, 80); fill_stroke(c, "#d9a020", 4)
    for yy in (-20, 0, 20):
        c.move_to(x - 16, y + yy); c.line_to(x + 16, y + yy); c.set_source_rgb(*OL); c.set_line_width(3); c.stroke()
    s.write_to_png(f"{OUT}/{file}.png")
def trishul(file, W=360):
    s, c = surf(W, W); x = W / 2
    glowdisc(c, x, W / 2, W / 2, (1, 0.9, 0.6), 0.6)
    c.rectangle(x - 9, 120, 18, 220); fill_stroke(c, "#8a5a32", 4)
    c.move_to(x - 90, 70); c.curve_to(x - 85, 150, x - 40, 165, x, 165); c.curve_to(x + 40, 165, x + 85, 150, x + 90, 70)
    c.set_source_rgb(*OL); c.set_line_width(20); c.stroke_preserve(); c.set_source_rgb(*hexc("#e6e6ee")); c.set_line_width(11); c.stroke()
    for px in (-90, 90):
        poly(c, [(x + px - 16, 80), (x + px, 30), (x + px + 16, 80)]); fill_stroke(c, "#e6e6ee", 4)
    poly(c, [(x - 20, 140), (x, 18), (x + 20, 140)]); fill_stroke(c, "#e6e6ee", 4)
    ellipse(c, x, 190, 26, 20); fill_stroke(c, "#c0392b", 4)   # damru-knot band
    s.write_to_png(f"{OUT}/{file}.png")
def brahmastra(file, W=520):
    s, c = surf(W, W); x = y = W / 2
    glowdisc(c, x, y, W / 2, (1, 0.75, 0.2), 0.95)
    c.save(); c.translate(x, y)
    for k in range(32):
        c.rotate(math.pi / 16); c.move_to(-5, 0); c.line_to(5, 0); c.line_to(0, -(W * 0.47 if k % 2 else W * 0.34)); c.close_path(); c.set_source_rgba(1, 0.9, 0.4, 0.7); c.fill()
    c.rotate(-0.78)   # arrow pointing up-right
    c.rectangle(-8, -150, 16, 300); fill_stroke(c, "#f2c230", 4)
    poly(c, [(-40, -150), (0, -235), (40, -150)]); fill_stroke(c, "#ffe27a", 5)
    for yy in (120, 150):
        poly(c, [(-8, yy - 40), (-38, yy), (-8, yy - 10)]); fill_stroke(c, "#c0392b", 3)
        poly(c, [(8, yy - 40), (38, yy), (8, yy - 10)]); fill_stroke(c, "#c0392b", 3)
    c.restore()
    glowdisc(c, x - 235 * math.sin(0.78), y - 235 * math.cos(0.78), 70, (1, 1, 0.8), 0.9)
    s.write_to_png(f"{OUT}/{file}.png")
def orb(file, col, W=140):
    s, c = surf(W, W); glowdisc(c, W / 2, W / 2, W / 2, col, 1.0); glowdisc(c, W / 2, W / 2, W / 5, (1, 1, 1), 1.0); s.write_to_png(f"{OUT}/{file}.png")
def qmark(file, W=520, H=640):
    s, c = surf(W, H); glowdisc(c, W / 2, H / 2, W / 2, (1, 0.75, 0.2), 0.6); s.write_to_png(f"{OUT}/{file}.png")
if not ONLY or ONLY == "icons":
    chakra("ic_chakra", "#c0392b"); chakra("ic_chakra2", "#2f8a4a"); chakra("ic_chakra3", "#26346a"); chakra("ic_chakra4", "#f2c230", rim="#ffe27a")
    vajra("ic_vajra"); trishul("ic_trishul"); brahmastra("ic_brahma")
    orb("orb_coal", (1, 0.45, 0.1)); orb("orb_smoke", (0.8, 0.8, 0.95)); orb("orb_sun", (1, 0.85, 0.3)); qmark("q_glow")

# ---------------- backgrounds (world 1360x1660, drawn at 2x) ----------------
WW, WH, K = 1360, 1660, 2
def folk_sun(c, x, y, r, face=True):
    c.save(); c.translate(x, y)
    for k in range(20):
        c.rotate(math.pi / 10); poly(c, [(-0.18 * r, -0.95 * r), (0, -1.55 * r), (0.18 * r, -0.95 * r)]); fill_stroke(c, "#f6a623" if k % 2 else "#f2c230", 3)
    c.restore()
    c.arc(x, y, r, 0, 6.3); fill_stroke(c, "#f7c948", 5)
    c.arc(x, y, r * 0.8, 0, 6.3); c.set_source_rgb(*hexc("#e8902a")); c.set_line_width(4); c.stroke()
    if face:
        for s_ in (-1, 1):
            ellipse(c, x + s_ * 0.3 * r, y - 0.1 * r, 0.13 * r, 0.07 * r); fill_stroke(c, "#fbf6ee", 3)
            c.arc(x + s_ * 0.3 * r, y - 0.1 * r, 0.05 * r, 0, 6.3); c.set_source_rgb(*OL); c.fill()
        c.arc(x, y + 0.2 * r, 0.25 * r, 0.3, math.pi - 0.3); c.set_source_rgb(*OL); c.set_line_width(4); c.stroke()
        c.arc(x, y - 0.42 * r, 0.05 * r, 0, 6.3); c.set_source_rgb(*hexc("#c0392b")); c.fill()
def swirl_cloud(c, x, y, s, col="#fbf3e0"):
    for dx, dy, r in ((-0.6, 0.05, 0.35), (-0.2, -0.15, 0.45), (0.25, -0.1, 0.4), (0.62, 0.06, 0.32)):
        c.arc(x + dx * s, y + dy * s, r * s, 0, 6.3); fill_stroke(c, col, 4)
    c.rectangle(x - 0.9 * s, y + 0.02 * s, 1.8 * s, 0.25 * s); c.set_source_rgb(*hexc(col)); c.fill()
    c.move_to(x - 0.95 * s, y + 0.27 * s); c.line_to(x + 0.95 * s, y + 0.27 * s); c.set_source_rgb(*OL); c.set_line_width(4); c.stroke()
    for dx in (-0.2, 0.25):
        c.arc(x + dx * s, y - 0.05 * s, 0.15 * s, 0.5, 5.2); c.set_source_rgb(*hexc("#e0c690")); c.set_line_width(4); c.stroke()
def tree(c, rnd, x, y, s, col, leaf, flower="#e0552a"):
    c.move_to(x - 0.16 * s, y); c.curve_to(x - 0.05 * s, y - 0.5 * s, x - 0.2 * s, y - 0.8 * s, x - 0.07 * s, y - 1.1 * s)
    c.line_to(x + 0.07 * s, y - 1.1 * s); c.curve_to(x + 0.2 * s, y - 0.8 * s, x + 0.05 * s, y - 0.5 * s, x + 0.16 * s, y); c.close_path()
    fill_stroke(c, "#6b4422", 4)
    for k in range(3):
        yy = y - 0.25 * s - k * 0.28 * s
        c.move_to(x - 0.12 * s, yy); c.line_to(x + 0.12 * s, yy - 0.04 * s); c.set_source_rgb(*hexc("#9a6a3a")); c.set_line_width(5); c.stroke()
    for dx, dy, r in ((-0.45, -1.35, 0.5), (0.45, -1.4, 0.52), (0, -1.75, 0.6), (-0.2, -1.2, 0.45), (0.25, -1.15, 0.45)):
        ellipse(c, x + dx * s, y + dy * s, r * s, r * 0.85 * s); fill_stroke(c, col, 4)
    c.set_source_rgb(*hexc(leaf))
    for k in range(24):
        a = rnd.uniform(0, 6.28); rr = rnd.uniform(0.1, 0.7) * s
        lx, ly = x + math.cos(a) * rr, y - 1.45 * s + math.sin(a) * rr * 0.6
        c.save(); c.translate(lx, ly); c.rotate(a); ellipse(c, 0, 0, 0.09 * s, 0.035 * s); c.restore(); c.fill()
    for k in range(4):
        fx, fy = x + rnd.uniform(-0.6, 0.6) * s, y - 1.45 * s + rnd.uniform(-0.3, 0.3) * s
        for p in range(5):
            a = p * 1.2566; ellipse(c, fx + math.cos(a) * 9, fy + math.sin(a) * 9, 6, 6); c.set_source_rgb(*hexc(flower)); c.fill()
        c.arc(fx, fy, 5, 0, 6.3); c.set_source_rgb(*hexc("#f2c230")); c.fill()
def ground(c, rnd, top, col_soil, col_path, grass):
    c.rectangle(0, top, WW, WH - top); c.set_source_rgb(*hexc(col_soil)); c.fill()
    poly(c, [(0, top + 70), (WW, top + 40), (WW, WH - 20), (0, WH)]); fill_stroke(c, col_path, 4)
    for k in range(70):
        x = rnd.uniform(0, WW); y = rnd.choice([rnd.uniform(top + 5, top + 60), rnd.uniform(WH - 60, WH)])
        for d in (-12, 0, 12):
            c.move_to(x, y); c.line_to(x + d, y - 30 - abs(d)); c.set_source_rgb(*hexc(grass)); c.set_line_width(4); c.stroke()
    for k in range(14):   # little folk flowers along the path
        fx, fy = rnd.uniform(20, WW - 20), rnd.choice([rnd.uniform(top + 10, top + 50), rnd.uniform(WH - 50, WH - 10)])
        for p in range(5):
            a = p * 1.2566; ellipse(c, fx + math.cos(a) * 8, fy + math.sin(a) * 8, 6, 6); c.set_source_rgb(*hexc("#f6f0e2" if k % 2 else "#e0552a")); c.fill()
        c.arc(fx, fy, 4, 0, 6.3); c.set_source_rgb(*hexc("#f2c230")); c.fill()
def bg_morning(file):
    rnd = random.Random(5)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, WW * K, WH * K); c = cairo.Context(s); c.scale(K, K)
    g = cairo.LinearGradient(0, 0, 0, 1100)   # soft dawn sky (east glows)
    g.add_color_stop_rgb(0, *hexc("#8fc7e0")); g.add_color_stop_rgb(0.55, *hexc("#f6d9a0")); g.add_color_stop_rgb(1, *hexc("#f4b97a"))
    c.set_source(g); c.paint()
    folk_sun(c, 1010, 190, 90)     # rising sun, in the east
    for x, y, sc in ((260, 220, 110), (620, 150, 80)): swirl_cloud(c, x, y, sc)
    for y, sc, col, leaf, n in [(1000, 290, "#5f9a4a", "#3f7a34", 7), (1180, 350, "#4a8a3e", "#2f6a2a", 6), (1350, 390, "#3a7a36", "#245a22", 5)]:
        for k in range(n):
            xx = -60 + k * ((WW + 120) / (n - 1)) + rnd.uniform(-40, 40)
            if 880 < xx < 1140 and y < 1300: continue   # keep the sun clear
            tree(c, rnd, xx, y, sc * rnd.uniform(0.9, 1.1), col, leaf)
    ground(c, rnd, 1380, "#7a5a34", "#c9a066", "#5a7a2a")
    for x, w in ((140, 34), (520, 26), (930, 30), (1270, 38)):
        c.move_to(x - w, 1455); c.curve_to(x - w, 1455 - 0.7 * w, x + w * 0.6, 1455 - 0.8 * w, x + w, 1455); c.close_path(); fill_stroke(c, "#8a7a6a", 4)
    s.write_to_png(f"{OUT}/{file}.png")
def bg_divine(file):
    rnd = random.Random(7)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, WW * K, WH * K); c = cairo.Context(s); c.scale(K, K)
    g = cairo.RadialGradient(WW / 2, 760, 40, WW / 2, 760, 1150)
    g.add_color_stop_rgb(0, *hexc("#fff2b8")); g.add_color_stop_rgb(0.35, *hexc("#f2b33a")); g.add_color_stop_rgb(0.75, *hexc("#a8521c")); g.add_color_stop_rgb(1, *hexc("#4a1a10"))
    c.set_source(g); c.paint()
    c.save(); c.translate(WW / 2, 760)
    for k in range(36):
        c.rotate(math.pi / 18); c.move_to(-14, 0); c.line_to(14, 0); c.line_to(0, -1300); c.close_path(); c.set_source_rgba(1, 0.95, 0.7, 0.13); c.fill()
    c.restore()
    for x, y, sc in ((180, 320, 120), (1180, 260, 110), (240, 1250, 140), (1140, 1290, 150), (680, 1420, 170)):
        swirl_cloud(c, x, y, sc, "#fff4d8")
    for k in range(40):
        c.arc(rnd.uniform(0, WW), rnd.uniform(0, WH), rnd.uniform(2, 5), 0, 6.3); c.set_source_rgba(1, 1, 0.85, 0.7); c.fill()
    s.write_to_png(f"{OUT}/{file}.png")
def bg_cloudvan(file):
    """Valmiki 28: near a mountain, a lovely forest that looks like a cloud (megha-sankasha) — birds, deer."""
    rnd = random.Random(9)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, WW * K, WH * K); c = cairo.Context(s); c.scale(K, K)
    g = cairo.LinearGradient(0, 0, 0, 1100)
    g.add_color_stop_rgb(0, *hexc("#7fb8dc")); g.add_color_stop_rgb(1, *hexc("#f6e2b0"))
    c.set_source(g); c.paint()
    folk_sun(c, 1150, 170, 70)
    swirl_cloud(c, 300, 180, 90)
    for (px, pk, col) in ((250, 330, "#6a7fa0"), (760, 230, "#5a6f92"), (1180, 360, "#6a7fa0")):   # folk mountains
        poly(c, [(px - 430, 1000), (px - 60, pk + 40), (px, pk), (px + 60, pk + 40), (px + 430, 1000)]); fill_stroke(c, col, 5)
        poly(c, [(px - 60, pk + 40), (px, pk), (px + 60, pk + 40), (px + 20, pk + 70), (px - 25, pk + 60)]); fill_stroke(c, "#f6f0e2", 3)
        c.set_source_rgba(*OL, 0.35); c.set_line_width(3)
        for k in range(4):
            c.move_to(px - 40 - k * 60, pk + 90 + k * 140); c.line_to(px - 10 - k * 40, pk + 150 + k * 140); c.stroke()
    c.rectangle(0, 1000, WW, 400); c.set_source_rgb(*hexc("#8fbf5a")); c.fill()      # open meadow in front of the forest
    c.move_to(0, 1000); c.line_to(WW, 1000); c.set_source_rgb(*OL); c.set_line_width(4); c.stroke()
    # the cloud-like forest: one big mass of round puffs, dark blue-green like a rain cloud
    puffs = [(400, 930, 130), (520, 860, 150), (660, 820, 170), (810, 850, 155), (940, 920, 130), (470, 990, 120), (620, 975, 140), (780, 980, 140), (920, 995, 115), (590, 720, 120), (740, 730, 115)]
    for cx_, cy_, r in puffs:
        ellipse(c, cx_, cy_, r, r * 0.82); fill_stroke(c, "#2f6a4e", 5)
    for cx_, cy_, r in puffs:
        c.arc(cx_ - r * 0.2, cy_ - r * 0.1, r * 0.45, 3.4, 5.5); c.set_source_rgba(1, 1, 1, 0.3); c.set_line_width(6); c.stroke()
        for k in range(5):
            a = rnd.uniform(0, 6.28); c.arc(cx_ + math.cos(a) * r * 0.5, cy_ + math.sin(a) * r * 0.4, 5, 0, 6.3); c.set_source_rgb(*hexc("#f6f0e2")); c.fill()
    c.rectangle(300, 1040, 760, 60); c.set_source_rgb(*hexc("#8fbf5a")); c.fill()
    for y, sc, col, leaf, n in [(1180, 330, "#4a8a3e", "#2f6a2a", 6), (1350, 380, "#3a7a36", "#245a22", 5)]:
        for k in range(n):
            xx = -60 + k * ((WW + 120) / (n - 1)) + rnd.uniform(-30, 30)
            if 160 < xx < 1200: continue   # only at the edges, so the cloud forest stays visible
            tree(c, rnd, xx, y, sc * rnd.uniform(0.9, 1.1), col, leaf, flower="#f6f0e2")
    for x, y in ((875, 1372),):   # a deer in the meadow, in the gap between Ram and Vishwamitra
        ellipse(c, x, y, 34, 18); fill_stroke(c, "#c98a4a", 3)
        for lx in (-20, -8, 12, 24):
            c.move_to(x + lx, y + 10); c.line_to(x + lx, y + 38); c.set_source_rgb(*OL); c.set_line_width(4); c.stroke()
        c.move_to(x + 28, y - 6); c.line_to(x + 40, y - 34); c.set_line_width(9); c.stroke_preserve(); c.set_source_rgb(*hexc("#c98a4a")); c.set_line_width(5); c.stroke()
        ellipse(c, x + 44, y - 38, 12, 8); fill_stroke(c, "#c98a4a", 3)
        c.move_to(x + 42, y - 44); c.line_to(x + 36, y - 62); c.move_to(x + 46, y - 44); c.line_to(x + 52, y - 62); c.set_source_rgb(*OL); c.set_line_width(3); c.stroke()
    ground(c, rnd, 1380, "#7a5a34", "#c9a066", "#5a7a2a")
    s.write_to_png(f"{OUT}/{file}.png")
if not ONLY or ONLY == "bg":
    bg_morning("bg_morning"); bg_divine("bg_divine"); bg_cloudvan("bg_cloudvan")
    s, c = surf(300, 120)   # a few flying birds (light, morning)
    for bx, by, sc in ((40, 60, 1.0), (140, 30, 0.8), (230, 75, 0.9)):
        c.move_to(bx - 30 * sc, by - 8 * sc); c.curve_to(bx - 15 * sc, by - 20 * sc, bx - 5 * sc, by - 5 * sc, bx, by)
        c.curve_to(bx + 5 * sc, by - 5 * sc, bx + 15 * sc, by - 20 * sc, bx + 30 * sc, by - 8 * sc)
        c.set_source_rgb(0.25, 0.18, 0.12); c.set_line_width(6 * sc); c.stroke()
    s.write_to_png(f"{OUT}/birds.png")
if ONLY: sys.exit(0)

# ---------------- voices: wav + lip shapes + exact word timings ----------------
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
    lip[k] = {"shapes": sh, "dur": d, "words": words[k]}
lines = json.load(open(os.path.join(HERE, "episode.json"), encoding="utf-8"))["LINES"]
for k in lip: lip[k]["text"] = lines[k][0]
json.dump(lip, open(f"{B}/proj/lip.json", "w"), ensure_ascii=False)

# ---------------- sound effects ----------------
for src, dst in (("shimmers/shimmer-short-sparkle", "sfx_spark"), ("shimmers/shimmer-long-bright", "sfx_shimmer_long"),
                 ("shimmers/shimmer-medium-bright", "sfx_shimmer"), ("cinematic-hits/cinematic-drum-big", "sfx_drum"),
                 ("whooshes/whoosh-medium-medium", "sfx_whoosh"), ("appear-and-vanish/appear-materialise", "sfx_appear"),
                 ("whooshes/whoosh-slow-soft", "sfx_whoosh_soft")):
    shutil.copy(os.path.join(REPO, "sfx", src + ".wav"), f"{OUT}/{dst}.wav")
def save(name, x):
    x = np.clip(x, -1, 1); w = wave.open(f"{OUT}/{name}.wav", "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
rng = np.random.default_rng(3)
t = np.arange(int(SR * 60)) / SR    # morning forest: soft breeze + bird chirps
amb = lowpass(rng.standard_normal(len(t)), 0.012) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t)) * 0.45
for k in range(70):
    t0 = rng.uniform(0, 59); f0 = rng.uniform(2600, 4200); i0 = int(t0 * SR)
    for j in range(rng.integers(2, 5)):
        tt = np.arange(int(0.07 * SR)) / SR; st = i0 + int(j * 0.11 * SR)
        if st + len(tt) < len(amb):
            amb[st:st + len(tt)] += np.sin(2 * np.pi * (f0 + 900 * tt / 0.07) * tt) * np.sin(np.pi * tt / 0.07) * 0.05
save("sfx_morning", amb)
t = np.arange(int(SR * 12)) / SR    # divine pad: soft drone with shimmer
pad = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((220, 0.08), (330, 0.06), (440, 0.04), (660, 0.02))) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.3 * t))
pad *= np.minimum(1, t / 0.6) * np.minimum(1, (12 - t) / 1.0)
save("sfx_pad", pad)
tt = np.arange(int(SR * 0.08)) / SR
save("sfx_click", (rng.standard_normal(len(tt)) * np.exp(-tt * 90) * 0.7 + np.sin(2 * np.pi * 1600 * tt) * np.exp(-tt * 70) * 0.4))
tt = np.arange(int(SR * 1.4)) / SR
ting = sum((np.sin(2 * np.pi * 2093 * (tt - d)) + 0.5 * np.sin(2 * np.pi * 4186 * (tt - d))) * np.exp(-(tt - d) * 4) * (tt > d) for d in (0, 0.28)) * 0.25
save("sfx_ting", ting)
print("ok", {k: round(v["dur"], 2) for k, v in lip.items()})
