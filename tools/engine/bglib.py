"""Background + prop drawings for the Katha Chitra scene engine.
Copied unchanged from episodes/bhag5/draw_assets.py (morning, divine, cloud-forest, quiver, bow)
and template/draw_assets.py (dark "ghor van" forest). Set bglib.OUT before calling.
"""
import math, random, cairo
from chars import hexc, fill_stroke, ellipse, poly, OL
OUT = "."
WW, WH, K = 1360, 1660, 2
rnd = random.Random(11)


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

def surf(w, h): s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); return s, cairo.Context(s)

def glowdisc(c, x, y, r, col, a=0.75):
    g = cairo.RadialGradient(x, y, 0, x, y, r); g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g); c.arc(x, y, r, 0, 6.3); c.fill()

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
