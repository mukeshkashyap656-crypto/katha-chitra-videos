import math, random, cairo
from chars import hexc, fill_stroke, ellipse, poly, OL

SW, SH = 1000, 1220   # scene area size

def grad(ctx, y0, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *hexc(c0)); g.add_color_stop_rgb(1, *hexc(c1))
    return g

def swirl_cloud(ctx, x, y, s, col="#fbe3b0"):
    for dx, dy, r in ((-0.9, 0.1, 0.45), (-0.35, -0.2, 0.6), (0.3, -0.1, 0.55), (0.85, 0.12, 0.4)):
        ctx.arc(x + dx * s, y + dy * s, r * s, 0, 6.3); fill_stroke(ctx, col, 4)
    ctx.rectangle(x - 1.2 * s, y + 0.1 * s, 2.4 * s, 0.42 * s); ctx.set_source_rgb(*hexc(col)); ctx.fill()
    ctx.move_to(x - 1.3 * s, y + 0.5 * s); ctx.line_to(x + 1.25 * s, y + 0.5 * s); ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke()
    for dx in (-0.35, 0.3):  # inner swirls
        ctx.arc(x + dx * s, y - 0.1 * s, 0.22 * s, 3.4, 6.0); ctx.set_line_width(3); ctx.stroke()

def folk_sun(ctx, x, y, r, t=0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 0.1)
    for k in range(16):
        a = k * math.pi / 8
        poly(ctx, [(math.cos(a - 0.12) * r * 1.05, math.sin(a - 0.12) * r * 1.05), (math.cos(a) * r * 1.5, math.sin(a) * r * 1.5),
                   (math.cos(a + 0.12) * r * 1.05, math.sin(a + 0.12) * r * 1.05)])
        fill_stroke(ctx, "#f2a23a", 3)
    ctx.restore()
    ctx.arc(x, y, r, 0, 6.3); fill_stroke(ctx, "#f7c53f", 5)
    # face
    for s in (-1, 1):
        ctx.move_to(x + s * 0.45 * r - 0.15 * r, y - 0.1 * r); ctx.curve_to(x + s * 0.45 * r, y - 0.25 * r, x + s * 0.45 * r + 0.05 * r, y - 0.2 * r, x + s * 0.45 * r + 0.18 * r, y - 0.08 * r)
        ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(x, y + 0.2 * r, 0.3 * r, 0.4, math.pi - 0.4); ctx.stroke()

def tree(ctx, x, y, s, col="#2f6b3a"):
    poly(ctx, [(x - 0.12 * s, y), (x + 0.12 * s, y), (x + 0.08 * s, y - 0.9 * s), (x - 0.08 * s, y - 0.9 * s)]); fill_stroke(ctx, "#6b3a1e", 4)
    ellipse(ctx, x, y - 1.4 * s, 0.6 * s, 0.7 * s); fill_stroke(ctx, col, 5)
    ctx.set_source_rgb(*hexc("#e8b730"))
    for k in range(9):
        a = k * 0.7; rr = 0.35 * s * ((k % 3) + 1) / 3
        ellipse(ctx, x + math.cos(a) * rr, y - 1.4 * s + math.sin(a) * rr * 1.1, 0.06 * s, 0.1 * s); ctx.fill()

def fort(ctx, x, y, w, h, col="#c9955a", night=False):
    """fort on rock: base y, centre x"""
    # rock
    ctx.move_to(x - w * 0.75, y)
    ctx.curve_to(x - w * 0.6, y - h * 0.35, x - w * 0.3, y - h * 0.42, x, y - h * 0.4)
    ctx.curve_to(x + w * 0.3, y - h * 0.42, x + w * 0.6, y - h * 0.35, x + w * 0.75, y); ctx.close_path()
    fill_stroke(ctx, "#7a5236" if not night else "#4a3426")
    ctx.set_source_rgb(*OL); ctx.set_line_width(3)
    for k in range(7):
        xx = x - w * 0.5 + k * w * 0.16
        ctx.move_to(xx, y - h * 0.05); ctx.line_to(xx + 18, y - h * 0.2); ctx.line_to(xx + 40, y - h * 0.12); ctx.stroke()
    base = y - h * 0.38
    wc = col if not night else "#8a6a4a"
    # main wall
    ctx.rectangle(x - w * 0.42, base - h * 0.32, w * 0.84, h * 0.32); fill_stroke(ctx, wc)
    # crenellations
    for k in range(13):
        xx = x - w * 0.42 + k * w * 0.84 / 12.5
        ctx.rectangle(xx, base - h * 0.36, w * 0.035, h * 0.04); fill_stroke(ctx, wc, 3)
    # bastions
    for bx in (-0.42, 0.42, -0.12):
        ctx.rectangle(x + bx * w - w * 0.07, base - h * 0.45, w * 0.14, h * 0.45); fill_stroke(ctx, wc)
        for k in range(4):
            ctx.rectangle(x + bx * w - w * 0.07 + k * w * 0.04, base - h * 0.49, w * 0.025, h * 0.04); fill_stroke(ctx, wc, 3)
    # top palace with dome
    ctx.rectangle(x + w * 0.05, base - h * 0.55, w * 0.25, h * 0.23); fill_stroke(ctx, wc)
    ctx.arc(x + w * 0.175, base - h * 0.55, w * 0.08, math.pi, 0); fill_stroke(ctx, wc)
    # gate arch
    ctx.move_to(x - w * 0.06, base); ctx.line_to(x - w * 0.06, base - h * 0.12)
    ctx.curve_to(x - w * 0.06, base - h * 0.2, x + w * 0.06, base - h * 0.2, x + w * 0.06, base - h * 0.12)
    ctx.line_to(x + w * 0.06, base); ctx.close_path(); fill_stroke(ctx, "#3a1f12")
    # windows
    for wx in (-0.3, -0.22, 0.22, 0.3, 0.12, 0.2):
        ctx.move_to(x + wx * w - 8, base - h * 0.15); ctx.line_to(x + wx * w - 8, base - h * 0.2)
        ctx.arc(x + wx * w, base - h * 0.2, 8, math.pi, 0); ctx.line_to(x + wx * w + 8, base - h * 0.15); ctx.close_path()
        fill_stroke(ctx, "#f7c53f" if night else "#3a1f12", 3)
    return (x + w * 0.175, base - h * 0.55 - w * 0.08)   # flag pole base on dome

def flag(ctx, px, py, t, size=70):
    ctx.move_to(px, py); ctx.line_to(px, py - size * 1.5); ctx.set_source_rgb(*OL); ctx.set_line_width(5); ctx.stroke()
    top = py - size * 1.5
    ctx.move_to(px, top)
    n = 8
    pts = []
    for k in range(n + 1):
        xx = px + size * 1.2 * k / n
        pts.append((xx, top + math.sin(t * 5 + k * 0.8) * 6 * k / n))
    for p in pts: ctx.line_to(*p)
    ctx.line_to(px + size * 1.2, top + size * 0.35 + math.sin(t * 5 + 6.4) * 6)
    for k in range(n, -1, -1):
        xx = px + size * 1.2 * k / n
        ctx.line_to(xx, top + size * 0.7 + math.sin(t * 5 + k * 0.8) * 6 * k / n)
    ctx.close_path(); fill_stroke(ctx, "#f08a24", 4)

def cusped_arch(ctx, x, y, w, h, fill="#7a1f2b", edge="#e8b730"):
    """multifoil arch opening, bottom at y"""
    ctx.move_to(x - w / 2, y); ctx.line_to(x - w / 2, y - h * 0.6)
    lobes = 5
    for k in range(lobes):
        a0 = math.pi + k * math.pi / lobes; a1 = a0 + math.pi / lobes
        cx = x + math.cos(a0 + math.pi / lobes / 2) * w / 2 * 0.85
        cy = y - h * 0.6 + math.sin(a0 + math.pi / lobes / 2) * h * 0.4 * 0.85
        ctx.arc(cx, cy, w * 0.17, a0 - 0.3, a1 + 0.3)
    ctx.line_to(x + w / 2, y - h * 0.6); ctx.line_to(x + w / 2, y); ctx.close_path()
    fill_stroke(ctx, fill, 5)
    ctx.set_source_rgb(*hexc(edge)); ctx.set_line_width(3)

def toran(ctx, x0, x1, y):
    ctx.move_to(x0, y); ctx.curve_to(x0 + (x1 - x0) * 0.3, y + 40, x0 + (x1 - x0) * 0.7, y + 40, x1, y)
    ctx.set_source_rgb(*hexc("#2f6b3a")); ctx.set_line_width(6); ctx.stroke()
    n = int((x1 - x0) / 34)
    for k in range(n + 1):
        tt = k / n; xx = x0 + (x1 - x0) * tt; yy = y + 40 * 4 * tt * (1 - tt) * 0.75
        ctx.arc(xx, yy + 10, 11, 0, 6.3); fill_stroke(ctx, "#f2a23a" if k % 2 else "#f7c53f", 2.5)
        if k % 2 == 0:
            poly(ctx, [(xx - 7, yy + 20), (xx + 7, yy + 20), (xx, yy + 46)]); fill_stroke(ctx, "#2f6b3a", 2.5)

def diya(ctx, x, y, t, s=1.0):
    ctx.move_to(x - 30 * s, y - 8 * s); ctx.curve_to(x - 25 * s, y + 14 * s, x + 25 * s, y + 14 * s, x + 30 * s, y - 8 * s); ctx.close_path()
    fill_stroke(ctx, "#b5541e", 4)
    fl = 1 + 0.12 * math.sin(t * 13 + x)
    g = cairo.RadialGradient(x, y - 22 * s, 2, x, y - 22 * s, 70 * s)
    g.add_color_stop_rgba(0, 1, 0.85, 0.4, 0.45); g.add_color_stop_rgba(1, 1, 0.7, 0.2, 0)
    ctx.set_source(g); ctx.arc(x, y - 22 * s, 70 * s, 0, 6.3); ctx.fill()
    ctx.move_to(x, y - 10 * s); ctx.curve_to(x - 10 * s, y - 20 * s, x - 2 * s, y - 34 * s * fl, x, y - 42 * s * fl)
    ctx.curve_to(x + 2 * s, y - 34 * s * fl, x + 10 * s, y - 20 * s, x, y - 10 * s); fill_stroke(ctx, "#f7c53f", 3)

def rangoli_floor(ctx, y0, col="#c98a4a", night=False):
    ctx.rectangle(0, y0, SW, SH - y0); ctx.set_source_rgb(*hexc(col)); ctx.fill()
    ctx.move_to(0, y0); ctx.line_to(SW, y0); ctx.set_source_rgb(*OL); ctx.set_line_width(5); ctx.stroke()
    ctx.set_line_width(3)
    for row in range(4):
        yy = y0 + 50 + row * 90
        for k in range(-1, 12):
            xx = k * 100 + (row % 2) * 50
            poly(ctx, [(xx, yy - 30), (xx + 30, yy), (xx, yy + 30), (xx - 30, yy)])
            ctx.set_source_rgb(*hexc("#e8b730" if not night else "#a08030")); ctx.stroke()
    ctx.rectangle(0, y0, SW, 14); ctx.set_source_rgb(*hexc("#7a1f2b")); ctx.fill()

def palace_wall(ctx, wall="#f1dcb0", night=False, arches=3, ah=620, y_floor=900):
    ctx.rectangle(0, 0, SW, y_floor); ctx.set_source(grad(ctx, 0, y_floor, wall, "#e2c28a" if not night else "#5a4030")); ctx.fill()
    # frieze top
    ctx.rectangle(0, 0, SW, 70); ctx.set_source_rgb(*hexc("#7a1f2b")); ctx.fill()
    ctx.set_source_rgb(*hexc("#e8b730"))
    for k in range(26):
        ctx.arc(20 + k * 40, 35, 9, 0, 6.3); ctx.fill()
    ctx.move_to(0, 70); ctx.line_to(SW, 70); ctx.set_source_rgb(*OL); ctx.set_line_width(5); ctx.stroke()
    xs = [SW * (k + 0.5) / arches for k in range(arches)]
    for x in xs:
        cusped_arch(ctx, x, y_floor - 10, SW / arches * 0.62, ah, fill="#5a1620" if not night else "#2a0c12")
        # pillars
    for k in range(arches + 1):
        px = SW * k / arches
        ctx.rectangle(px - 22, 70, 44, y_floor - 70); fill_stroke(ctx, "#d9a85a" if not night else "#7a5a3a", 4)
        for j in range(5):
            ctx.rectangle(px - 28, 130 + j * 160, 56, 16); fill_stroke(ctx, "#e8b730" if not night else "#8a7030", 3)
    toran(ctx, 20, SW - 20, 78)


def bg_fort(ctx, t, night=False):
    if night:
        ctx.set_source(grad(ctx, 0, SH, "#14183a", "#3a2a5a")); ctx.paint()
        random.seed(3)
        for k in range(60):
            x, y = random.uniform(0, SW), random.uniform(0, 650)
            r = random.uniform(1.5, 3.5) * (0.7 + 0.3 * math.sin(t * 3 + k))
            ctx.arc(x, y, r, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.8); ctx.fill()
        ctx.arc(780, 210, 70, 0, 6.3); fill_stroke(ctx, "#f6efcf", 5)
        ctx.arc(808, 195, 62, 0, 6.3); ctx.set_source(grad(ctx, 0, SH, "#14183a", "#3a2a5a")); ctx.fill()
    else:
        ctx.set_source(grad(ctx, 0, SH * 0.8, "#e9783a", "#f7c46a")); ctx.paint()
        folk_sun(ctx, 790, 250, 75, t)
        swirl_cloud(ctx, 260, 330 + math.sin(t * 0.6) * 6, 70)
        swirl_cloud(ctx, 560 + t * 3, 200, 50)
    # distant hills
    ctx.move_to(0, 760); ctx.curve_to(200, 640, 380, 700, 520, 690); ctx.curve_to(700, 660, 850, 600, SW, 680)
    ctx.line_to(SW, SH); ctx.line_to(0, SH); ctx.close_path()
    fill_stroke(ctx, "#a35a3a" if not night else "#2a2440")
    pole = fort(ctx, 500, 1000, 660, 760, night=night)
    flag(ctx, pole[0], pole[1], t, 60)
    # foreground ground + trees
    ctx.move_to(0, 1000); ctx.curve_to(300, 960, 700, 980, SW, 950); ctx.line_to(SW, SH); ctx.line_to(0, SH); ctx.close_path()
    fill_stroke(ctx, "#5f7a2f" if not night else "#1f2a20")
    tree(ctx, 90, 1130, 120, "#2f6b3a" if not night else "#1c3a24")
    tree(ctx, 920, 1150, 105, "#3f7a3a" if not night else "#1c3a24")


def bg_room(ctx, t, night=False):
    palace_wall(ctx, night=night, arches=3, ah=600, y_floor=860)
    rangoli_floor(ctx, 860, night=night)
    if night:
        ctx.rectangle(0, 0, SW, SH); ctx.set_source_rgba(0.05, 0.03, 0.12, 0.35); ctx.fill()

def bed(ctx, x, y, w):
    # palang with posts; y = floor
    for s in (-1, 1):
        ctx.rectangle(x + s * w / 2 - 14, y - 560, 28, 560); fill_stroke(ctx, "#8a4a22")
        ctx.arc(x + s * w / 2, y - 565, 20, 0, 6.3); fill_stroke(ctx, "#e8b730", 4)
    ctx.rectangle(x - w / 2, y - 560, w, 24); fill_stroke(ctx, "#8a4a22")
    # headboard drapery
    ctx.move_to(x - w / 2 + 14, y - 536); ctx.curve_to(x - w / 4, y - 470, x + w / 4, y - 470, x + w / 2 - 14, y - 536); ctx.close_path()
    fill_stroke(ctx, "#7a1f2b", 4)
    # mattress
    ctx.rectangle(x - w / 2, y - 260, w, 120); fill_stroke(ctx, "#8a4a22")
    for s in (-0.42, 0.42):
        ctx.rectangle(x + s * w - 14, y - 140, 28, 140); fill_stroke(ctx, "#8a4a22")
    # pillow
    ellipse(ctx, x, y - 400, w * 0.33, 55); fill_stroke(ctx, "#f6f0e2")

def quilt(ctx, x, y, w, col="#b5262e"):
    ctx.move_to(x - w / 2 - 10, y - 380); ctx.curve_to(x - w / 4, y - 395, x + w / 4, y - 395, x + w / 2 + 10, y - 380)
    ctx.line_to(x + w / 2 + 20, y - 200); ctx.line_to(x - w / 2 - 20, y - 200); ctx.close_path(); fill_stroke(ctx, col)
    ctx.set_source_rgb(*hexc("#e8b730")); ctx.set_line_width(10)
    ctx.move_to(x - w / 2 - 15, y - 225); ctx.line_to(x + w / 2 + 15, y - 225); ctx.stroke()
    for k in range(5):
        ctx.arc(x - w * 0.35 + k * w * 0.175, y - 300, 14, 0, 6.3); fill_stroke(ctx, "#e8b730", 3)

def stool(ctx, x, y, w=220, h=120, col="#8a4a22"):
    ctx.rectangle(x - w / 2, y - h, w, 26); fill_stroke(ctx, col)
    for s in (-1, 1):
        ctx.rectangle(x + s * (w / 2 - 20) - 10, y - h + 26, 20, h - 26); fill_stroke(ctx, col)

def desk(ctx, x, y, w=520, h=230):
    ctx.rectangle(x - w / 2, y - h, w, 36); fill_stroke(ctx, "#7a3e1c")
    ctx.rectangle(x - w / 2 + 20, y - h + 36, w - 40, h - 36); fill_stroke(ctx, "#8a4a22")
    ctx.set_source_rgb(*hexc("#e8b730")); ctx.set_line_width(4)
    ctx.rectangle(x - w / 2 + 50, y - h + 70, w - 100, h - 110); ctx.stroke()

def bg_office(ctx, t):
    ctx.set_source(grad(ctx, 0, 860, "#c9d3d9", "#9fb0bb")); ctx.rectangle(0, 0, SW, 860); ctx.fill()
    # tall window
    ctx.rectangle(330, 150, 340, 560); fill_stroke(ctx, "#f2e6c8")
    ctx.rectangle(350, 170, 300, 520); ctx.set_source(grad(ctx, 170, 690, "#9ad0e8", "#e9f4f8")); ctx.fill_preserve()
    ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(500, 170); ctx.line_to(500, 690); ctx.move_to(350, 430); ctx.line_to(650, 430); ctx.stroke()
    # columns
    for px in (140, 860):
        ctx.rectangle(px - 45, 100, 90, 760); fill_stroke(ctx, "#eae2d0")
        ctx.set_source_rgb(*OL); ctx.set_line_width(2.5)
        for k in range(-2, 3):
            ctx.move_to(px + k * 15, 130); ctx.line_to(px + k * 15, 830); ctx.stroke()
        ctx.rectangle(px - 60, 80, 120, 40); fill_stroke(ctx, "#eae2d0")
    ctx.rectangle(0, 860, SW, SH - 860); ctx.set_source_rgb(*hexc("#5a3a2a")); ctx.fill()
    ctx.set_source_rgb(*hexc("#7a1f2b"))
    ctx.rectangle(80, 900, SW - 160, 280); ctx.fill()  # carpet
    ctx.set_source_rgb(*hexc("#e8b730")); ctx.set_line_width(6); ctx.rectangle(100, 920, SW - 200, 240); ctx.stroke()
    ctx.move_to(0, 860); ctx.line_to(SW, 860); ctx.set_source_rgb(*OL); ctx.set_line_width(5); ctx.stroke()

def bg_darbar(ctx, t):
    palace_wall(ctx, arches=3, ah=700, y_floor=880)
    rangoli_floor(ctx, 880, col="#b5541e")

def gaddi(ctx, x, y, w=420):
    # canopy
    ctx.rectangle(x - w / 2 - 20, y - 900, 24, 900); fill_stroke(ctx, "#e8b730")
    ctx.rectangle(x + w / 2 - 4, y - 900, 24, 900); fill_stroke(ctx, "#e8b730")
    ctx.move_to(x - w / 2 - 40, y - 900); ctx.curve_to(x - w / 4, y - 1000, x + w / 4, y - 1000, x + w / 2 + 40, y - 900)
    ctx.close_path(); fill_stroke(ctx, "#b5262e")
    # bolster + seat
    ctx.rectangle(x - w * 0.42, y - 560, w * 0.84, 440); fill_stroke(ctx, "#b5262e")
    ctx.set_source_rgb(*hexc("#e8b730")); ctx.set_line_width(5); ctx.rectangle(x - w * 0.42 + 14, y - 546, w * 0.84 - 28, 412); ctx.stroke()
    ctx.rectangle(x - w / 2, y - 130, w, 130); fill_stroke(ctx, "#7a1f2b")
    ctx.set_source_rgb(*hexc("#e8b730")); ctx.set_line_width(6); ctx.rectangle(x - w / 2 + 15, y - 115, w - 30, 100); ctx.stroke()

def scroll_prop(ctx, hands, t):
    (x1, y1), (x2, y2) = hands
    if x1 > x2: x1, x2 = x2, x1
    ry = (y1 + y2) / 2
    poly(ctx, [(x1 - 10, ry), (x2 + 10, ry), (x2 + 10, ry + 230), (x1 - 10, ry + 230)]); fill_stroke(ctx, "#f3e2b0", 4)
    ctx.set_source_rgb(*OL); ctx.set_line_width(3)
    for k in range(5):
        ctx.move_to(x1 + 12, ry + 40 + k * 36); ctx.line_to(x2 - 12 - (k % 2) * 25, ry + 40 + k * 36); ctx.stroke()
    for yy in (ry, ry + 230):
        ctx.rectangle(x1 - 34, yy - 11, x2 - x1 + 68, 22); fill_stroke(ctx, "#8a4a22", 4)

def letter_prop(ctx, x, y, w=150, h=110, ang=0.0, seal=True):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    ctx.rectangle(-w / 2, -h / 2, w, h); fill_stroke(ctx, "#f6ecd2", 4)
    ctx.set_source_rgb(*OL); ctx.set_line_width(2.5)
    for k in range(4):
        ctx.move_to(-w / 2 + 15, -h / 2 + 22 + k * 20); ctx.line_to(w / 2 - 15 - (k % 2) * 25, -h / 2 + 22 + k * 20); ctx.stroke()
    if seal:
        ctx.arc(w / 2 - 25, h / 2 - 22, 14, 0, 6.3); fill_stroke(ctx, "#b5262e", 3)
    ctx.restore()

def quill(ctx, hx, hy, ang=-0.6):
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(ang)
    ctx.move_to(0, 0); ctx.curve_to(-14, -60, -8, -120, 6, -150); ctx.curve_to(14, -110, 12, -50, 0, 0)
    fill_stroke(ctx, "#f6f0e2", 3); ctx.restore()

def inkpot(ctx, x, y):
    ctx.rectangle(x - 22, y - 40, 44, 40); fill_stroke(ctx, "#1f2a44", 4)
    ctx.rectangle(x - 12, y - 52, 24, 14); fill_stroke(ctx, "#1f2a44", 3)
