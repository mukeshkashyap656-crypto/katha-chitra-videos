import math, cairo

OL = (0.16, 0.07, 0.04)      # bold dark outline
LW = 5.0
WALK = None   # set to a phase (radians) to draw walking legs
SIDE = 0      # 0 = walk facing the camera; +1 / -1 = side-view walk facing screen right / left

def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def fill_stroke(ctx, col, lw=LW):
    ctx.set_source_rgb(*hexc(col) if isinstance(col, str) else col)
    ctx.fill_preserve()
    ctx.set_source_rgb(*OL)
    ctx.set_line_width(lw)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()

def ellipse(ctx, x, y, rx, ry):
    ctx.save(); ctx.translate(x, y); ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()

def poly(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


# ---- REAL human gait: average of two walkers from the CMU motion-capture database (free for all uses; BVH by B. Hahne).
# 24 samples per step cycle starting at left heel strike; angles in degrees from straight-down, + = forward.
GAIT = {"L_thigh": [33.1, 33.4, 34.1, 33.1, 27.6, 20.8, 14.7, 9.0, 5.3, 0.2, -7.7, -16.4, -23.0, -27.6, -25.1, -18.7, -7.6, 2.8, 12.2, 20.6, 27.4, 31.2, 31.4, 31.9], "L_shank": [18.0, 13.2, 6.0, -1.6, -6.2, -8.8, -11.2, -13.9, -18.1, -20.8, -21.0, -20.7, -23.0, -27.9, -37.8, -47.9, -57.5, -60.1, -56.3, -47.9, -35.4, -19.3, -1.3, 13.0], "R_thigh": [-18.7, -22.9, -24.0, -15.2, -5.3, 4.8, 13.8, 21.5, 27.9, 31.6, 32.8, 34.1, 36.5, 35.7, 35.4, 33.9, 28.2, 21.7, 15.8, 10.8, 6.7, 0.7, -5.3, -12.6], "R_shank": [-26.8, -31.8, -38.0, -49.9, -58.8, -61.3, -57.4, -49.2, -37.0, -21.5, -4.1, 9.3, 12.9, 8.5, 2.1, -5.5, -10.2, -13.3, -15.7, -18.8, -22.0, -23.6, -25.2, -25.6], "L_uarm": [-27.4, -29.6, -29.1, -26.5, -22.6, -16.7, -9.9, -3.3, 3.1, 9.7, 16.0, 20.5, 23.1, 22.2, 19.0, 14.1, 10.0, 6.6, 2.9, -1.2, -5.9, -11.4, -17.6, -23.0], "L_farm": [-19.7, -23.7, -24.8, -22.4, -17.5, -10.5, -1.2, 11.9, 25.9, 38.6, 50.4, 60.5, 68.1, 72.4, 72.7, 68.6, 60.4, 49.3, 36.6, 24.6, 12.3, 1.4, -6.9, -15.0], "R_uarm": [14.6, 15.7, 13.3, 8.9, 4.6, 1.2, -3.5, -7.7, -12.3, -16.4, -20.2, -24.2, -26.7, -27.3, -25.7, -23.0, -19.8, -15.0, -9.5, -4.3, 0.5, 5.8, 10.9, 14.9], "R_farm": [59.8, 62.4, 62.1, 58.9, 53.7, 46.5, 38.1, 29.1, 20.9, 12.6, 4.5, -1.5, -6.8, -10.9, -13.2, -12.4, -8.3, -2.3, 6.3, 16.3, 27.5, 38.1, 47.4, 55.5]}

# real "walk, then stop" from CMU 16_33 (24 samples, ~1.1 s). disp = forward travel of the pelvis in leg-lengths.
STOPT = {"L_thigh": [-8.1, -7.2, -2.5, 4.7, 12.1, 18.1, 23.0, 25.9, 26.3, 24.1, 19.6, 15.7, 14.2, 13.4, 12.6, 11.7, 11.1, 10.8, 10.6, 10.6, 10.3, 10.1, 10.1, 10.0], "L_shank": [-28.3, -33.8, -39.9, -45.7, -49.8, -50.8, -49.1, -45.4, -39.2, -31.4, -23.6, -19.3, -19.9, -19.7, -20.1, -20.4, -20.8, -21.1, -21.3, -21.5, -21.6, -21.7, -21.8, -22.0], "R_thigh": [26.3, 24.9, 21.8, 17.5, 12.9, 9.5, 7.5, 6.9, 8.2, 9.3, 10.9, 11.0, 10.1, 9.7, 8.6, 8.3, 8.3, 8.0, 7.7, 7.3, 7.2, 7.1, 7.1, 7.1], "R_shank": [6.2, 1.5, -1.6, -3.6, -3.8, -3.9, -4.4, -6.0, -9.0, -12.2, -15.5, -17.6, -18.5, -19.6, -20.0, -20.7, -21.1, -21.2, -21.4, -21.6, -22.1, -22.1, -22.1, -21.9], "L_uarm": [5.2, 3.5, 2.8, 1.7, 1.7, 1.3, -0.5, -1.6, -2.4, -3.1, -3.5, -3.6, -3.4, -1.8, -1.0, 0.3, 1.0, 1.6, 1.5, 1.8, 1.7, 1.4, 1.2, -0.1], "L_farm": [39.3, 37.3, 34.0, 31.5, 29.2, 27.4, 26.0, 24.2, 21.7, 19.1, 16.9, 15.9, 15.9, 16.2, 18.6, 22.1, 25.0, 29.4, 32.4, 33.4, 33.6, 32.5, 31.1, 30.2], "R_uarm": [-8.5, -7.2, -6.5, -6.2, -4.2, -1.6, 1.0, 3.8, 5.6, 7.0, 8.5, 9.3, 9.5, 8.5, 6.5, 5.2, 4.4, 3.2, 1.7, -1.3, -4.2, -6.1, -6.6, -6.7], "R_farm": [10.7, 11.8, 14.4, 18.5, 22.0, 26.1, 30.0, 34.6, 39.5, 44.3, 47.9, 50.5, 51.2, 49.1, 45.0, 39.0, 31.3, 24.1, 18.9, 16.8, 16.2, 16.0, 15.4, 14.8], "disp": [0.0, 0.053, 0.104, 0.151, 0.189, 0.222, 0.248, 0.272, 0.293, 0.314, 0.335, 0.354, 0.368, 0.38, 0.39, 0.399, 0.406, 0.411, 0.415, 0.42, 0.424, 0.426, 0.427, 0.427]}
GAITOV = None   # when set to a dict of angles, _gait() returns it instead of the walking table (used for the stop)

def stop_pose(t):
    """t = 0..1 through the stop. Real stopping angles, easing into a relaxed upright stance at the end."""
    t = max(0.0, min(1.0, t)); n = 24; f = t * (n - 1); i = int(min(f, n - 2)); w = f - i
    g = {k: v[i] * (1 - w) + v[i + 1] * w for k, v in STOPT.items()}
    rest = {"L_thigh": 3.0, "L_shank": 1.0, "R_thigh": 3.0, "R_shank": 1.0, "L_uarm": 4.0, "L_farm": 12.0, "R_uarm": -4.0, "R_farm": 12.0}
    b = max(0.0, (t - 0.55) / 0.45); b = b * b * (3 - 2 * b)    # settle into the standing pose
    for k, v in rest.items(): g[k] = g[k] * (1 - b) + v * b
    return g

def stop_disp(t):
    """forward travel (in units u, 1 u = height/5) the body should make during the stop up to t"""
    return stop_pose(t)["disp"] * 2.03

def _gait(phase):
    if GAITOV is not None: return GAITOV
    """phase (radians) -> dict of interpolated real joint angles (degrees)."""
    n = 24; f = (phase / (2 * math.pi) * n) % n; i = int(f); w = f - i; j = (i + 1) % n
    return {k: v[i] * (1 - w) + v[j] * w for k, v in GAIT.items()}

def _gait_legs(phase, seg):
    """real leg angles -> (dtop, {s: (thigh_rad, shank_rad, ext)}) ; dtop = how far the pelvis sits below straight-leg height"""
    g = _gait(phase); r = {}
    for s_, p in ((-1, "L"), (1, "R")):
        th, sh = math.radians(g[p + "_thigh"]), math.radians(g[p + "_shank"])
        r[s_] = (th, sh, seg * (math.cos(th) + math.cos(sh)))
    return max(v[2] for v in r.values()), r

def _dk(h, f=0.78):
    r, g, b = hexc(h)
    return "#%02x%02x%02x" % (int(r * f * 255), int(g * f * 255), int(b * f * 255))

def limb(ctx, pts, w, col):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_source_rgb(*OL); ctx.set_line_width(w + 2 * LW); ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc(col)); ctx.set_line_width(w); ctx.stroke()


def tlimb(ctx, pts, ws, col, lw=None, bulge=0.0, open_start=False):
    """Tapered, organic limb along the polyline pts: width ws[i] at pts[i] (+ a soft muscle bulge between joints), round ends, one clean outline."""
    lw = LW if lw is None else lw
    cl, wd = [], []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        for k in range(8):
            t = k / 8; cl.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)); wd.append(ws[i] + (ws[i + 1] - ws[i]) * t + bulge * math.sin(math.pi * t))
    cl.append(pts[-1]); wd.append(ws[-1])
    L, R = [], []
    for i, (px, py) in enumerate(cl):
        a = cl[max(i - 1, 0)]; b = cl[min(i + 1, len(cl) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1.0; nx, ny = -dy / n, dx / n
        h = wd[i] / 2; L.append((px + nx * h, py + ny * h)); R.append((px - nx * h, py - ny * h))
    def dirang(i0, i1):
        return math.atan2(cl[i1][1] - cl[i0][1], cl[i1][0] - cl[i0][0])
    ctx.new_path(); ctx.move_to(*L[0])
    for q in L[1:]: ctx.line_to(*q)
    ph = dirang(len(cl) - 2, len(cl) - 1); ex_, ey_ = cl[-1]
    ctx.arc_negative(ex_, ey_, wd[-1] / 2, ph + math.pi / 2, ph - math.pi / 2)
    for q in reversed(R): ctx.line_to(*q)
    ph0 = dirang(0, 1); sx_, sy_ = cl[0]
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if open_start:                       # joint end has NO outline (elbow merges into the piece before it: no puppet seam)
        ctx.set_source_rgb(*OL); ctx.set_line_width(2 * lw); ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc(col)); ctx.fill()
        ctx.arc(sx_, sy_, max(1.0, wd[0] / 2 - 1.6 * lw), 0, 6.3); ctx.set_source_rgb(*hexc(col)); ctx.fill()      # soft elbow: fill only, no ring
        return
    ctx.arc_negative(sx_, sy_, wd[0] / 2, ph0 - math.pi / 2, ph0 - 3 * math.pi / 2)
    ctx.close_path()
    ctx.set_source_rgb(*OL); ctx.set_line_width(2 * lw)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc(col)); ctx.fill()


def draw_foot(ctx, x, y, u, skin, rot=0.0, side=0):
    """Foot with a sandal sole and toes. side 0 = seen from the front (toes along the bottom edge), +-1 = side view facing that way."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    if side:
        ellipse(ctx, 0.05 * u * side, 0.015 * u, 0.2 * u, 0.065 * u); fill_stroke(ctx, "#6b3a1e", 3.5)
        ellipse(ctx, 0.04 * u * side, -0.025 * u, 0.15 * u, 0.055 * u); fill_stroke(ctx, skin, 3)
        for k in range(4):
            ctx.arc((0.15 + 0.03 * k) * u * side, -0.02 * u + 0.01 * k * u, 0.026 * u, 0, 6.3); fill_stroke(ctx, skin, 2)
    else:
        ellipse(ctx, 0, 0.02 * u, 0.17 * u, 0.075 * u); fill_stroke(ctx, "#6b3a1e", 3.5)
        ellipse(ctx, 0, -0.01 * u, 0.125 * u, 0.06 * u); fill_stroke(ctx, skin, 3)
        for k in range(5):
            tx = (-0.09 + 0.045 * k) * u
            ctx.arc(tx, 0.045 * u + 0.012 * u * (1 - abs(k - 2) / 2.0) * -1, (0.028 - 0.002 * abs(k - 2)) * u, 0, 6.3); fill_stroke(ctx, skin, 2)
    ctx.restore()

def draw_hand(ctx, x, y, ang, u, skin, style, side):
    """Human-looking hand at the wrist point (x, y). ang = forearm direction (radians from straight down, + = screen right).
    style: relaxed | open | point | fist | join.  side: -1 left arm / +1 right arm (thumb toward the body)."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(-ang); ctx.scale(1.28, 1.28)     # a real hand is about as long as the face: bigger than a cartoon mitten
    th = -side
    FL = 2.4                                                                          # thin outline for fingers
    def fing(x0, y0, ln, a=0.0, curl=0.0, w=0.066):
        pts = [(x0 * u, y0 * u)]; ca = a
        for k in range(3):
            ca += curl * (0.6 + 0.4 * k)
            px, py = pts[-1]; pts.append((px + math.sin(ca) * ln / 3 * u, py + math.cos(ca) * ln / 3 * u))
        tlimb(ctx, pts, [w * u, w * 0.9 * u, w * 0.78 * u, w * 0.66 * u], skin, lw=FL)
    def palm(w0=0.21, w1=0.19, ln=0.15):
        tlimb(ctx, [(0, -0.03 * u), (0, ln * u)], [w0 * u, w1 * u], skin, lw=3.2)
    def thumb(ang_=0.55, ln=0.19, y0=0.03):
        pts = [(th * 0.09 * u, y0 * u), (th * (0.09 + 0.07 * math.sin(ang_)) * u, (y0 + 0.5 * ln * math.cos(ang_)) * u), (th * (0.09 + 0.13 * math.sin(ang_)) * u, (y0 + ln * math.cos(ang_)) * u)]
        tlimb(ctx, pts, [0.085 * u, 0.072 * u, 0.058 * u], skin, lw=FL)
    if style == "join":                          # palms pressed together (pranam): closed leaf, fingers together
        poly(ctx, [(-0.1 * u, 0.0), (-0.09 * u, 0.2 * u), (-0.045 * u, 0.4 * u), (0.0, 0.45 * u), (0.045 * u, 0.4 * u), (0.09 * u, 0.2 * u), (0.1 * u, 0.0)])
        fill_stroke(ctx, skin, 4)
        ctx.set_source_rgba(*OL, 0.8); ctx.set_line_width(2.2)
        for fx_ in (-0.045, 0.0, 0.045):
            ctx.move_to(fx_ * u, 0.24 * u); ctx.line_to(fx_ * u, (0.41 if fx_ == 0 else 0.38) * u); ctx.stroke()
    elif style == "fist":
        thumb(0.9, 0.14, 0.05)
        tlimb(ctx, [(0, 0.0), (0, 0.12 * u)], [0.24 * u, 0.22 * u], skin, lw=3.5)
        ctx.set_source_rgba(*OL, 0.9); ctx.set_line_width(2.4)
        for fx_ in (-0.06, -0.02, 0.02, 0.06):
            ctx.move_to(fx_ * u, 0.1 * u); ctx.line_to(fx_ * u, 0.17 * u); ctx.stroke()
    elif style == "point":                       # index finger out, the others curled into the palm, thumb across
        palm(0.21, 0.19, 0.17)
        fing(th * 0.0 - th * 0.0, 0.15, 0.30, a=th * 0.0, curl=0.0, w=0.066)
        for k, fx_ in enumerate((0.05, 0.085, 0.115)):
            ctx.arc(-th * fx_ * u, 0.2 * u, 0.04 * u, 0, 6.3); fill_stroke(ctx, skin, 2.4)
        thumb(0.9, 0.14, 0.06)
    elif style == "open":                        # fingers gently spread: blessing / explaining
        for fx_, ln, a_ in ((-0.075, 0.24, -0.34), (-0.026, 0.3, -0.11), (0.026, 0.31, 0.09), (0.075, 0.25, 0.3)):
            fing(fx_, 0.11, ln, a=a_, curl=-a_ * 0.12)
        thumb(0.95, 0.22, 0.04)
        palm(0.22, 0.2, 0.15)
    else:                                        # relaxed: four fingers, gently curled, thumb alongside
        for fx_, ln, c_ in ((-0.077, 0.24, 0.2), (-0.026, 0.29, 0.24), (0.026, 0.28, 0.26), (0.077, 0.22, 0.3)):
            fing(fx_, 0.11, ln, a=fx_ * 0.9, curl=c_ * -th * 0.35)
        thumb(0.5, 0.2, 0.02)
        palm(0.22, 0.2, 0.15)
    ctx.restore()

# ---------------- character specs (fixed for whole series) ----------------
CHARS = {
    "rani_m": dict(kind="f", skin="#d99a6c", hair="#1a0f0a", blouse="#2f6b3a", saree="#8e1b2b",
                   border="#e8b730", bindi=True, jewel=True),
    "rani_w": dict(kind="f", skin="#d99a6c", hair="#1a0f0a", blouse="#f3ead8", saree="#f6f0e2",
                   border="#c9a227", bindi=False, jewel=False),
    "gangadhar": dict(kind="m", skin="#c98c62", hair="#9a9a9a", tunic="#f2ead6", sash="#c0392b",
                      pagdi="#b5262e", pagdi2="#e8b730", beard=False, mous="#8c8c8c", lower="#f2ead6"),
    "damodar": dict(kind="m", skin="#d9a070", hair="#1a0f0a", tunic="#e9902a", sash="#2f6b3a",
                    pagdi="#c0392b", pagdi2="#e8b730", beard=False, mous=None, lower="#f6f0e2", child=True),
    "dasharatha": dict(fw=1.08, fh=1.0, build=1.12, belly=1.2, age=3, eye=1.08, nose=1.1, jowl=True, kind="m", skin="#c98c62", hair="#f4f1ea", tunic="#e9b22e", sash="#2f8a4a", upper="#c0392b",
                       beard="#f8f6f0", mous="#f8f6f0", lower="#f6f0e2", crown=True, jewel=True, bare=True,
                       skirt=1.55, hem="#c0392b"),
    "rishi": dict(kind="m", skin="#c98c62", hair="#f4f1ea", tunic="#f6f0e2", sash="#8a5a2a", upper="#e8902a",
                  beard="#f8f6f0", mous="#f8f6f0", lower="#f6f0e2", jata="#f8f6f0", halo=True, jewel=True, bare=True,
                  skirt=1.6, hem="#e8902a"),
    "mantri": dict(kind="m", skin="#c98c62", hair="#c98c62", tunic="#a0663a", sash="#8e1b2b", upper="#e8902a",
                   lower="#f08a24", jewel=True, bare=True, skirt=1.3, hem="#8e1b2b", mous="#3a2a20"),
    "darbari": dict(fw=1.12, fh=0.98, build=1.15, belly=1.25, eye=0.95, nose=1.15, kind="m", skin="#b97d55", hair="#1a0f0a", tunic="#f6f0e2", sash="#c0392b", upper="#2f8a4a",
                    pagdi="#f6f0e2", pagdi2="#e8b730", lower="#f6f0e2", mous="#1a0f0a", beard="#1a0f0a", jewel=True, bare=True, skirt=1.3, hem="#2f8a4a"),
    "mantri2": dict(fw=0.9, fh=1.08, build=0.88, age=3, eye=0.9, nose=1.2, hook=True, kind="m", skin="#b97d55", hair="#b97d55", tunic="#2f6b3a", sash="#e8b730", upper="#c0392b",
                    lower="#f6f0e2", jewel=True, bare=True, skirt=1.3, hem="#e8b730", mous="#e8e4dc", beard="#e8e4dc"),
    "darbari2": dict(fw=0.92, fh=1.0, build=0.92, eye=1.15, nose=0.85, tall=1.02, kind="m", skin="#d09468", hair="#1a0f0a", tunic="#3a5a9a", sash="#e8b730", upper="#f08a24",
                     pagdi="#d9342b", pagdi2="#f2c230", lower="#f6f0e2", mous="#1a0f0a", jewel=True, bare=True, skirt=1.3, hem="#f2c230"),
    "vishwamitra": dict(kind="m", skin="#c98c62", hair="#c98c62", tunic="#a0663a", sash="#8e1b2b", upper="#e8902a",
                        lower="#f08a24", jewel=True, bare=True, skirt=1.3, hem="#8e1b2b", mous=None),
    "darbari3": dict(fw=1.15, fh=0.95, build=1.18, belly=1.35, jowl=True, eye=0.85, nose=1.2, age=1, kind="m", skin="#c08055", hair="#1a0f0a", tunic="#8e1b2b", sash="#f2c230", upper="#f6f0e2",
                     pagdi="#f2c230", pagdi2="#d9342b", lower="#f6f0e2", mous="#6b6b6b", jewel=True, bare=True, skirt=1.3, hem="#f2c230"),
    "darbari4": dict(fw=1.0, fh=1.05, build=1.05, eye=1.0, nose=1.1, browt=1.5, age=1, kind="m", skin="#d09468", hair="#1a0f0a", tunic="#f6f0e2", sash="#2f6b3a", upper="#d9342b",
                     pagdi="#2f8a4a", pagdi2="#f2c230", lower="#f6f0e2", mous="#1a0f0a", jewel=True, bare=True, skirt=1.3, hem="#2f6b3a"),
    "vishwamitra2": dict(fw=0.9, fh=1.1, build=0.95, tall=1.04, hook=True, nose=1.3, browt=1.7, browcol="#3a2a20", eye=0.92, eyeh=0.8, age=2, kind="m", skin="#b97a50", hair="#4a3a30", tunic="#8a5a32", sash="#5a3a1e", ajina="#d8b07a",
                         beard="#6a5a50", beardlen=1.55, mous="#6a5a50", lower="#c98a4a", jatabun="#4a3a30", tilak=True, mala=True,
                         bare=True, skirt=1.7, hem="#5a3a1e", kamandalu=True, bandcol="#7a3e1c", halo=True),
    "vasishtha": dict(fw=0.95, fh=1.05, build=0.92, stoop=0.35, eye=0.9, eyeh=0.85, age=3, nose=1.05, kind="m", skin="#c98c62", hair="#f4f1ea", tunic="#e9c48a", sash="#8a5a2a", ajina="#e2c08e",
                      beard="#f8f6f0", beardlen=1.6, mous="#f8f6f0", lower="#f6f0e2", jatabun="#f4f1ea", tilak=True, mala=True,
                      halo=True, bare=True, skirt=1.75, hem="#8a5a2a", bandcol="#7a3e1c"),
    "ellis": dict(kind="b", skin="#f0c8a8", hair="#7a4a22", coat="#b3202a", trim="#e8b730",
                  belt="#f4f1ea", trouser="#2b2b3a", mous="#7a4a22"),
    "dalhousie": dict(kind="b", skin="#f0c8a8", hair="#a0522d", coat="#1f2a44", trim="#c9c9c9",
                      belt=None, trouser="#1f1f2a", mous=None, cravat=True),
}

def face(ctx, c, hx, hy, u, mouth="X", blink=False, emo="neutral", look=0.0, turn=0.0):
    rx, ry = 0.40 * u * c.get("fw", 1.0), 0.48 * u * c.get("fh", 1.0)
    kind = c["kind"]
    if kind == "f":
        ellipse(ctx, hx, hy - 0.05 * u, rx * 1.08, ry * 1.02); fill_stroke(ctx, c["hair"])
        ellipse(ctx, hx, hy - 0.52 * u, 0.2 * u, 0.15 * u); fill_stroke(ctx, c["hair"])
    for s in (-1, 1):
        if abs(turn) > 0.5 and s * turn > 0: continue      # far ear hidden when the head is turned
        ellipse(ctx, hx + s * rx * 0.98, hy + 0.02 * u, 0.07 * u, 0.11 * u); fill_stroke(ctx, c["skin"], 4)
        if c.get("jewel"):
            if kind == "m":
                ctx.arc(hx + s * rx * 1.0, hy + 0.15 * u, 0.06 * u, 0, 6.3); ctx.set_source_rgb(*OL); ctx.set_line_width(7); ctx.stroke_preserve()
                ctx.set_source_rgb(*hexc("#f2c230")); ctx.set_line_width(4); ctx.stroke()
            else:
                ctx.arc(hx + s * rx * 0.98, hy + 0.16 * u, 0.04 * u, 0, 6.3); fill_stroke(ctx, "#e8b730", 3)
    ellipse(ctx, hx, hy, rx, ry); fill_stroke(ctx, c["skin"])
    if abs(turn) > 0.5:                                # nose sticks out past the cheek line in the direction of the look
        _sg = 1 if turn > 0 else -1
        ellipse(ctx, hx + _sg * rx * 1.0, hy + 0.07 * u, 0.065 * u, 0.085 * u); fill_stroke(ctx, c["skin"], 4)
        ellipse(ctx, hx + _sg * rx * 0.78, hy + 0.0 * u, 0.12 * u, 0.2 * u); fill_stroke(ctx, c["skin"], 0.1)
    if c.get("jowl"):
        for s_ in (-1, 1):
            ctx.arc(hx + s_ * rx * 0.55, hy + ry * 0.45, 0.12 * u, (0.2 if s_ > 0 else 1.6), (1.5 if s_ > 0 else 2.9))
            ctx.set_source_rgb(*OL); ctx.set_line_width(2.5); ctx.stroke()
    if c.get("age"):
        ctx.set_source_rgba(*OL, 0.7); ctx.set_line_width(2.2)
        for k in range(c["age"]):
            yy = hy - ry * (0.62 - k * 0.09)
            ctx.move_to(hx - rx * 0.4, yy); ctx.curve_to(hx - rx * 0.15, yy - 0.02 * u, hx + rx * 0.15, yy - 0.02 * u, hx + rx * 0.4, yy); ctx.stroke()
        for s_ in (-1, 1):
            ctx.move_to(hx + s_ * rx * 0.72, hy - 0.06 * u); ctx.line_to(hx + s_ * rx * 0.85, hy - 0.1 * u)
            ctx.move_to(hx + s_ * rx * 0.72, hy - 0.02 * u); ctx.line_to(hx + s_ * rx * 0.86, hy - 0.01 * u); ctx.stroke()
    if kind == "f":
        ctx.move_to(hx - rx * 1.02, hy - 0.02 * u)
        ctx.curve_to(hx - rx, hy - ry * 1.15, hx + rx, hy - ry * 1.15, hx + rx * 1.02, hy - 0.02 * u)
        ctx.curve_to(hx + rx * 0.75, hy - ry * 0.55, hx + 0.08 * u, hy - ry * 0.75, hx, hy - ry * 0.62)
        ctx.curve_to(hx - 0.08 * u, hy - ry * 0.75, hx - rx * 0.75, hy - ry * 0.55, hx - rx * 1.02, hy - 0.02 * u)
        ctx.close_path(); fill_stroke(ctx, c["hair"], 4)
        ctx.move_to(hx, hy - ry * 0.62); ctx.line_to(hx, hy - ry * 1.0)
        ctx.set_source_rgb(*hexc("#c0392b") if c.get("bindi") else hexc(c["skin"])); ctx.set_line_width(3); ctx.stroke()
    elif kind == "b":
        ctx.move_to(hx - rx * 1.02, hy)
        ctx.curve_to(hx - rx * 1.1, hy - ry * 1.25, hx + rx * 1.1, hy - ry * 1.25, hx + rx * 1.02, hy)
        ctx.curve_to(hx + rx * 0.9, hy - ry * 0.5, hx + 0.1 * u, hy - ry * 0.85, hx - rx * 0.3, hy - ry * 0.6)
        ctx.curve_to(hx - rx * 0.7, hy - ry * 0.55, hx - rx * 0.9, hy - ry * 0.3, hx - rx * 1.02, hy)
        ctx.close_path(); fill_stroke(ctx, c["hair"], 4)
        for s in (-1, 1):
            poly(ctx, [(hx + s * rx * 0.98, hy - 0.1 * u), (hx + s * rx * 0.8, hy - 0.1 * u),
                       (hx + s * rx * 0.85, hy + 0.15 * u), (hx + s * rx * 0.97, hy + 0.12 * u)])
            fill_stroke(ctx, c["hair"], 3)
    if c.get("beard"):
        bl = c.get("beardlen", 1.0)
        ctx.move_to(hx - rx * 0.97, hy + 0.02 * u)
        ctx.curve_to(hx - rx * 0.95, hy + ry * 1.05 * bl, hx - 0.25 * u, hy + ry * 1.35 * bl, hx, hy + ry * 1.32 * bl)
        ctx.curve_to(hx + 0.25 * u, hy + ry * 1.35 * bl, hx + rx * 0.95, hy + ry * 1.05 * bl, hx + rx * 0.97, hy + 0.02 * u)
        ctx.curve_to(hx + rx * 0.6, hy + 0.3 * u, hx + 0.2 * u, hy + 0.2 * u, hx, hy + 0.2 * u)
        ctx.curve_to(hx - 0.2 * u, hy + 0.2 * u, hx - rx * 0.6, hy + 0.3 * u, hx - rx * 0.97, hy + 0.02 * u)
        ctx.close_path(); fill_stroke(ctx, c["beard"], 4)
        ctx.set_source_rgb(*OL); ctx.set_line_width(2.5)
        for k in (-0.22, 0.0, 0.22):
            ctx.arc(hx + k * u, hy + ry * 1.12 * bl, 0.06 * u, 0.3, math.pi - 0.3); ctx.stroke()
        if bl > 1.2:
            for k in (-0.12, 0.12):
                ctx.move_to(hx + k * u, hy + ry * 0.75); ctx.curve_to(hx + k * 1.4 * u, hy + ry * 1.0 * bl, hx + k * 0.8 * u, hy + ry * 1.15 * bl, hx + k * 0.4 * u, hy + ry * 1.25 * bl); ctx.stroke()
    # head turned (3/4 view): face features slide toward the direction the character looks
    hx = hx + 0.20 * u * turn; _ef = 1 - 0.3 * min(1.0, abs(turn))
    look = look + 0.45 * turn                         # pupils lean toward the direction, not jammed in the corner
    # brows by emotion
    for s in (-1, 1):
        ex = hx + s * 0.16 * u * _ef; ey = hy - 0.17 * u - (0.06 * u if emo == "shock" else 0)
        inner_dy = {"neutral": 0, "angry": 0.05, "sad": -0.05, "firm": 0.035, "ill": -0.03, "stern": 0.02, "shock": -0.03, "worry": -0.04, "joy": -0.01}.get(emo, 0) * u
        ctx.move_to(ex + s * 0.1 * u, ey - 0.01 * u)
        ctx.line_to(ex - s * 0.08 * u, ey + inner_dy)
        ctx.set_source_rgb(*(hexc(c["beard"]) if c.get("beard") else OL))
        if c.get("beard"):
            bt = c.get("browt", 1.0)
            ctx.set_source_rgb(*OL); ctx.set_line_width(0.05 * u * bt); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke_preserve()
            ctx.set_source_rgb(*hexc(c.get("browcol", c["beard"]))); ctx.set_line_width(0.03 * u * bt); ctx.stroke()
        else:
            ctx.set_line_width(0.035 * u * c.get("browt", 1.0)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    lid = {"sad": 0.35, "ill": 0.6, "firm": 0.15, "angry": 0.2, "worry": 0.15}.get(emo, 0.0)
    for s in (-1, 1):
        ex = hx + s * 0.16 * u * _ef; ey = hy - 0.04 * u
        w, h = 0.12 * u * c.get("eye", 1.0), 0.065 * u * c.get("eye", 1.0) * c.get("eyeh", 1.0)
        if turn and s * turn > 0: w *= 1 - 0.18 * min(1.0, abs(turn))
        if blink:
            ctx.move_to(ex - w, ey); ctx.curve_to(ex - w * 0.4, ey + h * 0.7, ex + w * 0.4, ey + h * 0.7, ex + w, ey)
            ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke(); continue
        def eyepath():
            if turn:                                    # turned head: calm, symmetric almond eye (no slanted/pointed corners)
                ctx.move_to(ex - w, ey + h * 0.1); ctx.curve_to(ex - w * 0.6, ey - h * 1.7, ex + w * 0.6, ey - h * 1.7, ex + w, ey + h * 0.1)
                ctx.curve_to(ex + w * 0.6, ey + h * 1.5, ex - w * 0.6, ey + h * 1.5, ex - w, ey + h * 0.1); ctx.close_path(); return
            ctx.move_to(ex - w, ey); ctx.curve_to(ex - w * 0.4, ey - h * 1.5, ex + w * 0.5, ey - h * 1.4, ex + w, ey - h * 0.1)
            ctx.curve_to(ex + w * 0.4, ey + h * 1.2, ex - w * 0.4, ey + h * 1.2, ex - w, ey); ctx.close_path()
        eyepath(); fill_stroke(ctx, "#fbf6ee", 3.5)
        ctx.save(); eyepath(); ctx.clip()
        ctx.arc(ex + look * w * 0.5, ey, h * 0.95, 0, 6.3); ctx.set_source_rgb(0.12, 0.07, 0.04); ctx.fill()
        ctx.arc(ex + look * w * 0.5 + h * 0.3, ey - h * 0.35, h * 0.25, 0, 6.3); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        if lid > 0:
            ctx.rectangle(ex - w * 1.2, ey - h * 2, w * 2.4, h * (0.6 + lid * 2.2)); ctx.set_source_rgb(*hexc(c["skin"])); ctx.fill()
            ctx.move_to(ex - w * 1.1, ey - h * 1.4 + h * lid * 2.2); ctx.line_to(ex + w * 1.1, ey - h * 1.4 + h * lid * 2.2)
            ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke()
        ctx.restore()
        if kind == "f":
            ctx.move_to(ex + s * w, ey - h * 0.1 if s > 0 else ey); ctx.line_to(ex + s * w * 1.35, ey - h * 0.6)
            ctx.set_source_rgb(*OL); ctx.set_line_width(3); ctx.stroke()
    nz = c.get("nose", 1.0)
    if c.get("hook"):
        ctx.move_to(hx - 0.01 * u, hy - 0.06 * u); ctx.curve_to(hx + 0.07 * u * nz, hy + 0.02 * u, hx + 0.08 * u * nz, hy + 0.14 * u * nz, hx + 0.0 * u, hy + 0.15 * u * nz)
        ctx.curve_to(hx - 0.04 * u, hy + 0.15 * u * nz, hx - 0.05 * u, hy + 0.12 * u * nz, hx - 0.03 * u, hy + 0.11 * u * nz)
    else:
        ctx.move_to(hx + 0.015 * u, hy); ctx.curve_to(hx + 0.05 * u * nz, hy + 0.1 * u * nz, hx + 0.04 * u * nz, hy + 0.13 * u * nz, hx - 0.03 * u * nz, hy + 0.13 * u * nz)
    ctx.set_source_rgb(*OL); ctx.set_line_width(3); ctx.stroke()
    if c.get("tilak"):
        for k in range(3):
            ctx.move_to(hx - 0.2 * u, hy - 0.33 * u + k * 0.035 * u); ctx.curve_to(hx - 0.07 * u, hy - 0.35 * u + k * 0.035 * u, hx + 0.07 * u, hy - 0.35 * u + k * 0.035 * u, hx + 0.2 * u, hy - 0.33 * u + k * 0.035 * u)
            ctx.set_source_rgb(0.97, 0.95, 0.9); ctx.set_line_width(0.022 * u); ctx.stroke()
        ctx.arc(hx, hy - 0.295 * u, 0.025 * u, 0, 6.3); ctx.set_source_rgb(*hexc("#c0392b")); ctx.fill()
    if c.get("bindi"):
        ctx.arc(hx, hy - 0.25 * u, 0.028 * u, 0, 6.3); ctx.set_source_rgb(*hexc("#c0392b")); ctx.fill()
    mx, my = hx, hy + 0.29 * u
    # mouth (lip-sync shapes) drawn before moustache so moustache sits over upper lip
    if mouth == "X":
        curve = {"sad": -0.035, "ill": -0.02, "firm": -0.01, "angry": -0.03, "stern": -0.015, "smile": 0.04, "joy": 0.045, "worry": -0.03, "shock": -0.02}.get(emo, 0.012) * u
        ctx.move_to(mx - 0.08 * u, my); ctx.curve_to(mx - 0.03 * u, my + curve, mx + 0.03 * u, my + curve, mx + 0.08 * u, my)
        ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke()
    else:
        w, h = {"A": (0.07, 0.04), "B": (0.085, 0.085), "O": (0.05, 0.065), "E": (0.1, 0.035), "M": (0.08, 0.008)}[mouth]
        w *= u; h *= u
        if mouth == "M":
            ctx.move_to(mx - w, my); ctx.line_to(mx + w, my); ctx.set_source_rgb(*OL); ctx.set_line_width(5); ctx.stroke()
        else:
            ellipse(ctx, mx, my + h * 0.3, w, h); fill_stroke(ctx, "#5a1414", 3.5)
            ctx.save(); ellipse(ctx, mx, my + h * 0.3, w, h); ctx.clip()
            ellipse(ctx, mx, my + h * 1.2, w * 0.7, h * 0.6); ctx.set_source_rgb(*hexc("#d9605a")); ctx.fill()
            if mouth in ("B", "E", "A"):
                ctx.rectangle(mx - w, my + h * 0.3 - h, w * 2, h * 0.45); ctx.set_source_rgb(1, 1, 1); ctx.fill()
            ctx.restore()
    if c.get("mous"):
        my2 = hy + 0.19 * u
        ctx.move_to(hx, my2 - 0.02 * u)
        ctx.curve_to(hx - 0.1 * u, my2 - 0.05 * u, hx - 0.2 * u, my2 - 0.02 * u, hx - 0.24 * u, my2 - 0.07 * u)
        ctx.curve_to(hx - 0.2 * u, my2 + 0.04 * u, hx - 0.08 * u, my2 + 0.03 * u, hx, my2 + 0.01 * u)
        ctx.curve_to(hx + 0.08 * u, my2 + 0.03 * u, hx + 0.2 * u, my2 + 0.04 * u, hx + 0.24 * u, my2 - 0.07 * u)
        ctx.curve_to(hx + 0.2 * u, my2 - 0.02 * u, hx + 0.1 * u, my2 - 0.05 * u, hx, my2 - 0.02 * u)
        fill_stroke(ctx, c["mous"], 2.5)


def person(ctx, cname, x, feet, H, pose="stand", arms=None, mouth="X", blink=False, emo="neutral",
           look=0.0, bow=0.0, prop=None, t=0.0, turn=None, bend=0.0, fixarms=False, hand=None, part="all"):
    """arms = (l_sh, l_el, r_sh, r_el) radians from straight-down; positive -> screen right."""
    c = CHARS[cname]
    # part: "all" (whole picture) | "body" (everything but the arms) | "uL","uR" (upper arm, hanging straight) | "fL","fR" (forearm+hand, hanging straight).
    # Arm pieces are drawn hanging down so the engine can rotate them smoothly (shoulder / elbow pivots) = real cut-out animation.
    _real = ctx
    _dummy = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4))
    if part not in ("all", "body"):
        ctx = _dummy
    if turn is None:
        turn = 1.0 * SIDE if (SIDE and WALK is not None) else 0.0   # side-view walkers look where they walk
    _walking = WALK is not None and pose == "stand"
    # GAZE RULE: eyes always go where the head/body goes. Head to the front (walking toward the viewer, talking to the viewer)
    # -> both pupils centred (old Katha Chitra style). To look at someone off to the side, turn the head (turn=+-1), do not push the pupils alone.
    if not turn:
        look = 0.0 if (_walking and not SIDE) else max(-0.25, min(0.25, look))
    if _walking:
        if SIDE:
            ctx.save(); ctx.translate(x, feet); ctx.rotate(0.07 * SIDE)           # side view: lean forward, no side sway
        else:
            ctx.save(); ctx.translate(x + 0.05 * (H / 5.0) * math.sin(WALK), feet)   # weight shifts over the standing leg
            ctx.rotate(0.035 + 0.045 * math.sin(WALK))       # slight forward lean + side-to-side sway
        ctx.translate(-x, -feet)
    H = H * c.get("tall", 1.0)
    bow = bow + c.get("stoop", 0.0)
    u = H / 5.0
    if c.get("child"):
        u = H / 4.2
    kind = c["kind"]
    top = feet - H
    if pose == "sit":
        top = feet - H * 0.72
    if WALK is not None and pose == "stand":      # walking: body dips at footfall, rises mid-step
        if SIDE:
            _extmax, _lg = _gait_legs(WALK, 1.015 * u)
            top += 2.0 * u - _extmax                 # real data: pelvis height follows the leg angles so the lower foot stays on the ground
        else:
            top += 0.10 * u * (1 - abs(math.sin(WALK)))
    if pose == "stand" and WALK is None and t:
        top += 0.012 * u * math.sin(t)                 # idle breathing: whole upper body rises/falls a little
    hx, hy = x, top + 0.5 * u + bow * u * 0.25
    sh_y = top + 1.12 * u
    sh_w = (0.62 * u if kind != "f" else 0.52 * u) * c.get("build", 1.0)
    bw = 0.45 * c.get("belly", 1.0)
    waist_y = top + 2.35 * u
    free_arms = arms is None
    if arms is None:
        arms = (0.12, 0.05, -0.12, -0.05)
    if WALK is not None and pose == "stand" and not fixarms:      # arms swing opposite to the legs (bow arm stays put)
        _sw = -math.cos(WALK)
        _la, _le, _ra, _re = arms
        if SIDE and free_arms:                    # side view: real mocap arm swing (upper arm + elbow fold)
            _g = _gait(WALK); _r = math.radians
            arms = (_r(_g["L_uarm"]) * SIDE, _r(_g["L_farm"] - _g["L_uarm"]) * SIDE, _r(_g["R_uarm"]) * SIDE, _r(_g["R_farm"] - _g["R_uarm"]) * SIDE)
        elif free_arms:
            arms = (_la - 0.34 * _sw, _le + 0.12 + 0.10 * max(0.0, -_sw), _ra + 0.34 * _sw, _re + 0.12 + 0.10 * max(0.0, _sw))
        else:
            if SIDE:
                _g = _gait(WALK); _r = math.radians
                arms = (_la, _le, _r(_g["R_uarm"]) * SIDE, _r(_g["R_farm"] - _g["R_uarm"]) * SIDE)
            else:
                arms = (_la, _le, _ra + 0.20 * _sw, _re + 0.08 + 0.06 * max(0.0, _sw))
    if c.get("halo"):
        g = cairo.RadialGradient(hx, hy - 0.1 * u, 0.2 * u, hx, hy - 0.1 * u, 0.95 * u)
        g.add_color_stop_rgba(0, 1, 0.85, 0.3, 0.55); g.add_color_stop_rgba(1, 1, 0.8, 0.2, 0)
        ctx.set_source(g); ctx.arc(hx, hy - 0.1 * u, 0.95 * u, 0, 6.3); ctx.fill()
        ctx.set_source_rgb(*hexc("#e8902a"))
        for k in range(28):
            a = k * math.pi * 2 / 28
            ctx.arc(hx + math.cos(a) * 0.78 * u, hy - 0.1 * u + math.sin(a) * 0.78 * u, 0.025 * u, 0, 6.3); ctx.fill()
    # ---- lower body ----
    if kind == "f":
        if pose == "sit":
            poly(ctx, [(x - 0.5 * u, waist_y), (x + 0.5 * u, waist_y), (x + 0.95 * u, feet), (x - 0.95 * u, feet)])
        else:
            poly(ctx, [(x - 0.45 * u, waist_y), (x + 0.45 * u, waist_y), (x + 0.75 * u, feet), (x - 0.75 * u, feet)])
        fill_stroke(ctx, c["saree"])
        ctx.set_source_rgb(*hexc(c["border"])); ctx.set_line_width(0.09 * u)
        hw = 0.95 * u if pose == "sit" else 0.75 * u
        ctx.move_to(x - hw + 6, feet - 0.06 * u); ctx.line_to(x + hw - 6, feet - 0.06 * u); ctx.stroke()
        ctx.set_source_rgb(*OL); ctx.set_line_width(2.5)
        for k in (-1, 0, 1):
            ctx.move_to(x + k * 0.12 * u, waist_y + 0.1 * u); ctx.line_to(x + k * 0.25 * u, feet - 0.12 * u); ctx.stroke()
    elif kind == "m":
        if pose != "bed":
            if pose == "sit":
                poly(ctx, [(x - (bw + 0.05) * u, waist_y), (x + (bw + 0.05) * u, waist_y), (x + (bw + 0.4) * u, feet), (x - (bw + 0.4) * u, feet)])
                fill_stroke(ctx, c["lower"])
            else:
                for s in (-1, 1):
                    if WALK is not None:
                        if SIDE:
                            # REAL mocap angles: forward kinematics from the hip (thigh) to the knee to the foot
                            _th, _sh, _ext = _lg[s]; seg = 1.015 * u
                            hip = (x + s * 0.03 * u, waist_y + 0.6 * u)
                            knee = (hip[0] + SIDE * seg * math.sin(_th), hip[1] + seg * math.cos(_th))
                            foot = (knee[0] + SIDE * seg * math.sin(_sh), knee[1] + seg * math.cos(_sh))
                            _w = max(0.0, 1.0 - (_extmax - _ext) / (0.25 * u))       # 1 while the foot is on the ground
                            toe = max(-0.55, min(0.55, -0.6 * _sh * _w))
                        else:
                            # ground foot slides BACK under the body, swing foot lifts and goes FORWARD; knee bends (two-bone IK)
                            q = (WALK + (0 if s < 0 else math.pi)) % (2 * math.pi)
                            A = (0.40 if SIDE else 0.19) * u
                            if q < math.pi:
                                t = q / math.pi; e = t * t * (3 - 2 * t)
                                dx = -A + 2 * A * e; lift = 0.16 * u * math.sin(math.pi * t); toe = 0.35 * (1 - 2 * t)
                            else:
                                t = (q - math.pi) / math.pi
                                dx = A - 2 * A * t; lift = 0.0; toe = 0.0
                            if SIDE:
                                dx *= SIDE; lift *= 1.25
                                hip = (x + s * 0.03 * u, waist_y + 0.6 * u); foot = (x + s * 0.02 * u + dx, feet - 0.05 * u - lift)
                            else:
                                hip = (x + s * 0.17 * u, waist_y + 0.6 * u)
                                foot = (x + s * 0.19 * u + dx, feet - 0.05 * u - lift)
                            seg = 1.015 * u
                            ddx, ddy = foot[0] - hip[0], foot[1] - hip[1]
                            d = min(math.hypot(ddx, ddy), 2 * seg - 1)
                            vx, vy = ddx / math.hypot(ddx, ddy), ddy / math.hypot(ddx, ddy)
                            hh = math.sqrt(max(seg * seg - (d / 2) ** 2, 0.0))
                            _bd = SIDE if SIDE else 1
                            knee = (hip[0] + vx * d / 2 + vy * hh * _bd, hip[1] + vy * d / 2 - vx * hh * _bd)
                        tlimb(ctx, [hip, knee, foot], [0.36 * u, 0.27 * u, 0.19 * u], _dk(c["lower"]) if (SIDE and s < 0) else c["lower"], bulge=0.015 * u)
                        draw_foot(ctx, foot[0] + 0.05 * u * (SIDE or 1), foot[1] + 0.01 * u, u, c["skin"], rot=toe * (SIDE or 1), side=SIDE)
                        continue
                    lift = dx = 0.0
                    fy = feet - lift
                    _hipp = (x + s * 0.2 * u, waist_y + 0.6 * u)
                    _ank = (x + s * (0.26 if s > 0 else 0.30) * u + dx, fy - 0.07 * u)          # a little asymmetric: weight on one leg
                    _kn = (_hipp[0] + (_ank[0] - _hipp[0]) * 0.5 + s * (0.015 if s > 0 else 0.05) * u, _hipp[1] + (_ank[1] - _hipp[1]) * 0.5)
                    tlimb(ctx, [_hipp, _kn, _ank], [0.38 * u, 0.28 * u, 0.19 * u], c["lower"], bulge=0.015 * u)
                    draw_foot(ctx, _ank[0] + s * 0.02 * u, fy - 0.03 * u, u, c["skin"], rot=s * (0.16 if s > 0 else 0.26))
                sk = c.get("skirt", 1.0) * (0.84 if (SIDE and WALK is not None) else 1.0)
                _sway = 0.05 * u * math.sin(WALK) if (WALK is not None and not SIDE) else 0.0
                poly(ctx, [(x - (bw - 0.03) * u, waist_y), (x + (bw - 0.03) * u, waist_y), (x + (bw + 0.05 + 0.12 * sk) * u + _sway, waist_y + sk * u), (x - (bw + 0.05 + 0.12 * sk) * u + _sway, waist_y + sk * u)])
                fill_stroke(ctx, c["tunic"])
                if c.get("hem"):
                    ctx.move_to(x - (0.5 + 0.12 * sk) * u + 6, waist_y + sk * u - 0.06 * u); ctx.line_to(x + (0.5 + 0.12 * sk) * u - 6, waist_y + sk * u - 0.06 * u)
                    ctx.set_source_rgb(*hexc(c["hem"])); ctx.set_line_width(0.08 * u); ctx.stroke()
    elif kind == "b":
        if pose != "desk":
            for s in (-1, 1):
                poly(ctx, [(x + s * 0.04 * u, waist_y + 0.2 * u), (x + s * 0.4 * u, waist_y + 0.2 * u),
                           (x + s * 0.32 * u, feet - 0.08 * u), (x + s * 0.08 * u, feet - 0.08 * u)])
                fill_stroke(ctx, c["trouser"])
                ellipse(ctx, x + s * 0.24 * u, feet - 0.05 * u, 0.19 * u, 0.08 * u); fill_stroke(ctx, "#111111", 4)
            poly(ctx, [(x - 0.46 * u, waist_y - 0.1 * u), (x + 0.46 * u, waist_y - 0.1 * u), (x + 0.5 * u, waist_y + 0.55 * u), (x - 0.5 * u, waist_y + 0.55 * u)])
            fill_stroke(ctx, c["coat"])
    # ---- torso ----
    if bend:                                       # bow from the waist (pranam): torso, head and arms rotate together about the hips
        ctx.save(); ctx.translate(x, waist_y); ctx.rotate(bend); ctx.translate(-x, -waist_y)
    if _walking:                                   # shoulders twist against the hips (front view: torso narrows at max twist)
        _tw = math.cos(WALK) ** 2
        ctx.save(); ctx.translate(x, 0); ctx.scale(0.74 if SIDE else 1 - 0.13 * _tw, 1); ctx.translate(-x, 0)
        if not SIDE: ctx.translate(x, waist_y); ctx.rotate(-0.05 * math.sin(WALK)); ctx.translate(-x, -waist_y)   # shoulders tilt against the hips
    neck_w = 0.13 * u
    poly(ctx, [(x - neck_w, hy + 0.35 * u), (x + neck_w, hy + 0.35 * u), (x + neck_w, sh_y + 0.05 * u), (x - neck_w, sh_y + 0.05 * u)])
    fill_stroke(ctx, c["skin"], 4)
    torso_col = {"f": c.get("blouse"), "m": c.get("tunic"), "b": c.get("coat")}[kind]
    ctx.move_to(x - sh_w, sh_y + 0.1 * u)
    ctx.curve_to(x - sh_w, sh_y - 0.05 * u, x - sh_w * 0.6, sh_y - 0.06 * u, x - neck_w * 1.3, sh_y - 0.04 * u)
    ctx.line_to(x + neck_w * 1.3, sh_y - 0.04 * u)
    ctx.curve_to(x + sh_w * 0.6, sh_y - 0.06 * u, x + sh_w, sh_y - 0.05 * u, x + sh_w, sh_y + 0.1 * u)
    if c.get("belly", 1.0) > 1.05:
        ctx.curve_to(x + sh_w * 1.05, sh_y + 0.6 * u, x + bw * 1.1 * u, waist_y - 0.3 * u, x + bw * u, waist_y)
    else:
        ctx.line_to(x + bw * u, waist_y)
    ctx.line_to(x - bw * u, waist_y)
    if c.get("belly", 1.0) > 1.05:
        ctx.curve_to(x - bw * 1.1 * u, waist_y - 0.3 * u, x - sh_w * 1.05, sh_y + 0.6 * u, x - sh_w, sh_y + 0.1 * u)
    ctx.close_path()
    fill_stroke(ctx, torso_col)
    if kind == "f":
        poly(ctx, [(x - sh_w * 0.95, sh_y - 0.02 * u), (x - sh_w * 0.35, sh_y - 0.05 * u), (x + 0.47 * u, waist_y - 0.25 * u), (x + 0.45 * u, waist_y + 0.05 * u), (x + 0.15 * u, waist_y + 0.05 * u)])
        fill_stroke(ctx, c["saree"])
        ctx.move_to(x - sh_w * 0.35, sh_y - 0.05 * u); ctx.line_to(x + 0.47 * u, waist_y - 0.25 * u)
        ctx.set_source_rgb(*hexc(c["border"])); ctx.set_line_width(0.07 * u); ctx.stroke()
        if c.get("jewel"):
            ctx.arc(x, sh_y + 0.02 * u, 0.16 * u, 0.3, math.pi - 0.3); ctx.set_source_rgb(*hexc("#e8b730")); ctx.set_line_width(0.04 * u); ctx.stroke()
    elif kind == "m" and c.get("ajina"):
        ctx.set_source_rgba(*OL, 0.45); ctx.set_line_width(2)
        for k in range(-3, 4):
            ctx.move_to(x + k * 0.12 * u, sh_y + 0.1 * u); ctx.curve_to(x + k * 0.12 * u + 6, sh_y + 0.6 * u, x + k * 0.12 * u - 6, sh_y + 0.9 * u, x + k * 0.12 * u, waist_y - 0.05 * u); ctx.stroke()
        poly(ctx, [(x - sh_w * 0.95, sh_y - 0.03 * u), (x - sh_w * 0.3, sh_y - 0.06 * u), (x + 0.47 * u, waist_y - 0.35 * u), (x + 0.47 * u, waist_y + 0.05 * u), (x + 0.1 * u, waist_y + 0.05 * u)])
        fill_stroke(ctx, c["ajina"], 4)
        ctx.set_source_rgb(*hexc("#5a3a1e"))
        for (px, py) in ((-0.35, 0.15), (-0.1, 0.45), (0.1, 0.8), (0.3, 1.0), (-0.2, 0.3), (0.2, 1.15), (0.0, 0.62)):
            ellipse(ctx, x + px * u, sh_y + py * u, 0.035 * u, 0.025 * u); ctx.fill()
        poly(ctx, [(x - 0.46 * u, waist_y - 0.12 * u), (x + 0.46 * u, waist_y - 0.12 * u), (x + 0.44 * u, waist_y + 0.05 * u), (x - 0.44 * u, waist_y + 0.05 * u)])
        fill_stroke(ctx, c["sash"], 4)
    elif kind == "m":
        ctx.move_to(x - neck_w, sh_y - 0.02 * u); ctx.curve_to(x + 0.1 * u, sh_y + 0.4 * u, x + 0.25 * u, sh_y + 0.6 * u, x + 0.3 * u, waist_y)
        ctx.set_source_rgb(*OL); ctx.set_line_width(3); ctx.stroke()
        if c.get("upper"):
            for col, wd in ((OL, 0.16 * u + 7), (hexc(c["upper"]), 0.16 * u)):
                ctx.move_to(x - sh_w * 0.75, sh_y - 0.02 * u); ctx.line_to(x + 0.42 * u, waist_y - 0.15 * u)
                ctx.set_source_rgb(*col); ctx.set_line_width(wd); ctx.stroke()
        poly(ctx, [(x - (bw + 0.01) * u, waist_y - 0.15 * u), (x + (bw + 0.01) * u, waist_y - 0.15 * u), (x + (bw - 0.01) * u, waist_y + 0.05 * u), (x - (bw - 0.01) * u, waist_y + 0.05 * u)])
        fill_stroke(ctx, c["sash"], 4)
    elif kind == "b":
        if c.get("belt"):
            for col, wd in ((OL, 0.13 * u + 6), (hexc(c["belt"]), 0.13 * u)):
                ctx.move_to(x - sh_w * 0.7, sh_y); ctx.line_to(x + 0.4 * u, waist_y - 0.1 * u)
                ctx.set_source_rgb(*col); ctx.set_line_width(wd); ctx.stroke()
        for k in range(4):
            ctx.arc(x - 0.12 * u, sh_y + 0.25 * u + k * 0.28 * u, 0.035 * u, 0, 6.3); fill_stroke(ctx, c["trim"], 2)
        poly(ctx, [(x - neck_w * 1.4, sh_y - 0.05 * u), (x + neck_w * 1.4, sh_y - 0.05 * u), (x + neck_w * 1.2, sh_y - 0.22 * u), (x - neck_w * 1.2, sh_y - 0.22 * u)])
        fill_stroke(ctx, "#ffffff" if c.get("cravat") else c["trim"], 3)
        for s in (-1, 1):
            ellipse(ctx, x + s * sh_w * 0.85, sh_y + 0.02 * u, 0.16 * u, 0.06 * u); fill_stroke(ctx, c["trim"], 3)
    if _walking: ctx.restore()
    ctx = _dummy if part == "body" else (_real if part == "head" else ctx)     # head is its own picture (part="head"): body part skips it
    if _walking:                                   # head stays level: cancels the body sway, small nod with each step
        ctx.save(); ctx.translate(hx, hy + 0.4 * u); ctx.rotate(-0.07 * SIDE + 0.012 * math.cos(2 * WALK) if SIDE else -0.045 * math.sin(WALK) - 0.035 + 0.012 * math.cos(2 * WALK)); ctx.translate(-hx, -(hy + 0.4 * u))
    _talk = (mouth != "X") and not _walking and part == "all"          # TALKING: head/body speak too (mouth is only 10-20% of the effect): small nod + tilt accents
    if _talk:
        ctx.save(); ctx.translate(0, 0.012 * u * math.sin(t * 4.1)); ctx.translate(hx, hy + 0.4 * u)
        ctx.rotate(0.018 * math.sin(t * 2.3) + 0.008 * math.sin(t * 5.1)); ctx.translate(-hx, -(hy + 0.4 * u))
    # ---- head ----
    face(ctx, c, hx, hy, u, mouth, blink, emo, look, turn)
    if c.get("mala"):
        for k in range(15):
            a = math.pi * 0.15 + k * math.pi * 0.7 / 14
            ctx.arc(x + math.cos(a) * 0.3 * u, sh_y + 0.05 * u + math.sin(a) * 0.55 * u, 0.035 * u, 0, 6.3); fill_stroke(ctx, "#7a3e1c", 1.5)
    if c.get("jatabun"):
        jc = c["jatabun"]
        ctx.move_to(hx - 0.41 * u, hy + 0.0 * u)
        ctx.curve_to(hx - 0.45 * u, hy - 0.62 * u, hx + 0.45 * u, hy - 0.62 * u, hx + 0.41 * u, hy + 0.0 * u)
        ctx.curve_to(hx + 0.3 * u, hy - 0.3 * u, hx - 0.3 * u, hy - 0.3 * u, hx - 0.41 * u, hy); ctx.close_path(); fill_stroke(ctx, jc, 4)
        # coiled jata bun on top (stacked coils)
        for k, (wv, yv) in enumerate(((0.33, 0.5), (0.3, 0.64), (0.25, 0.77), (0.17, 0.88))):
            ellipse(ctx, hx, hy - yv * u, wv * u, 0.1 * u); fill_stroke(ctx, jc, 3.5)
            ctx.move_to(hx - wv * 0.6 * u, hy - yv * u); ctx.curve_to(hx - 0.05 * u, hy - (yv + 0.05) * u, hx + 0.05 * u, hy - (yv - 0.05) * u, hx + wv * 0.6 * u, hy - yv * u)
            ctx.set_source_rgb(*OL); ctx.set_line_width(2); ctx.stroke()
        for k in range(9):  # rudraksha band
            ctx.arc(hx - 0.24 * u + k * 0.06 * u, hy - 0.42 * u, 0.025 * u, 0, 6.3); fill_stroke(ctx, "#7a3e1c", 1.5)
        for s_ in (-1, 1):  # locks falling behind ears
            ctx.move_to(hx + s_ * 0.4 * u, hy - 0.05 * u); ctx.curve_to(hx + s_ * 0.5 * u, hy + 0.3 * u, hx + s_ * 0.46 * u, hy + 0.6 * u, hx + s_ * 0.52 * u, hy + 0.9 * u)
            ctx.set_source_rgb(*OL); ctx.set_line_width(0.1 * u + 6); ctx.stroke_preserve(); ctx.set_source_rgb(*hexc(jc)); ctx.set_line_width(0.1 * u); ctx.stroke()
    if c.get("crown"):
        cy = hy - 0.36 * u
        poly(ctx, [(hx - 0.36 * u, cy + 0.08 * u), (hx - 0.4 * u, cy - 0.3 * u), (hx - 0.18 * u, cy - 0.15 * u), (hx, cy - 0.62 * u),
                   (hx + 0.18 * u, cy - 0.15 * u), (hx + 0.4 * u, cy - 0.3 * u), (hx + 0.36 * u, cy + 0.08 * u)])
        fill_stroke(ctx, "#f2c230")
        ctx.rectangle(hx - 0.4 * u, cy, 0.8 * u, 0.12 * u); fill_stroke(ctx, "#f2c230", 4)
        ctx.set_source_rgb(1, 0.97, 0.85)
        for k in range(9):
            ctx.arc(hx - 0.34 * u + k * 0.085 * u, cy + 0.06 * u, 0.018 * u, 0, 6.3); ctx.fill()
        ctx.arc(hx, cy - 0.22 * u, 0.065 * u, 0, 6.3); fill_stroke(ctx, "#c0392b", 3)
        for sx in (-0.22, 0.22):
            ctx.arc(hx + sx * u, cy - 0.08 * u, 0.04 * u, 0, 6.3); fill_stroke(ctx, "#2f8a4a", 3)
        ctx.arc(hx, cy - 0.66 * u, 0.04 * u, 0, 6.3); fill_stroke(ctx, "#c0392b", 3)
        if c.get("feather"):   # mor pankh (Krishna): thin stem + eye-shaped feather leaning to the right of the crown
            fx0, fy0 = hx + 0.1 * u, cy - 0.6 * u
            ctx.move_to(fx0, fy0); ctx.curve_to(fx0 + 0.08 * u, fy0 - 0.25 * u, fx0 + 0.16 * u, fy0 - 0.4 * u, fx0 + 0.22 * u, fy0 - 0.55 * u)
            ctx.set_source_rgb(*OL); ctx.set_line_width(0.035 * u + 3); ctx.stroke()
            ellipse(ctx, fx0 + 0.24 * u, fy0 - 0.66 * u, 0.1 * u, 0.17 * u); fill_stroke(ctx, "#1f9a8a", 3)
            ellipse(ctx, fx0 + 0.24 * u, fy0 - 0.66 * u, 0.055 * u, 0.1 * u); fill_stroke(ctx, "#2a58b8", 2)
            ellipse(ctx, fx0 + 0.24 * u, fy0 - 0.66 * u, 0.025 * u, 0.045 * u); fill_stroke(ctx, "#f2c230", 1.5)
    elif c.get("jata"):
        cy = hy - 0.32 * u
        ctx.move_to(hx - 0.42 * u, cy + 0.1 * u)
        ctx.curve_to(hx - 0.5 * u, cy - 0.45 * u, hx + 0.5 * u, cy - 0.45 * u, hx + 0.42 * u, cy + 0.1 * u)
        ctx.close_path(); fill_stroke(ctx, c["jata"])
        ctx.rectangle(hx - 0.44 * u, cy, 0.88 * u, 0.12 * u); fill_stroke(ctx, "#b8a07a", 4)
        ctx.arc(hx, cy - 0.42 * u, 0.12 * u, 0, 6.3); fill_stroke(ctx, c["jata"], 4)
        ctx.arc(hx, cy - 0.58 * u, 0.04 * u, 0, 6.3); fill_stroke(ctx, "#c0392b", 3)
    elif kind == "m" and c.get("pagdi"):
        py = hy - 0.38 * u
        ctx.move_to(hx - 0.46 * u, py + 0.12 * u)
        ctx.curve_to(hx - 0.5 * u, py - 0.35 * u, hx + 0.5 * u, py - 0.38 * u, hx + 0.48 * u, py + 0.1 * u)
        ctx.curve_to(hx + 0.2 * u, py + 0.02 * u, hx - 0.2 * u, py + 0.02 * u, hx - 0.46 * u, py + 0.12 * u)
        ctx.close_path(); fill_stroke(ctx, c["pagdi"])
        for k in range(3):
            ctx.move_to(hx - 0.42 * u, py + 0.02 * u - k * 0.11 * u); ctx.curve_to(hx - 0.1 * u, py - 0.06 * u - k * 0.1 * u, hx + 0.15 * u, py - 0.07 * u - k * 0.1 * u, hx + 0.44 * u, py - k * 0.1 * u)
            ctx.set_source_rgb(*hexc(c["pagdi2"])); ctx.set_line_width(0.035 * u); ctx.stroke()
        ellipse(ctx, hx + 0.42 * u, py - 0.12 * u, 0.1 * u, 0.14 * u); fill_stroke(ctx, c["pagdi"], 4)
    if _walking or _talk: ctx.restore()
    ctx = _real if part in ("all", "body") else _dummy
    if _walking:
        ctx.save(); ctx.translate(x, 0); ctx.scale(1.0 if SIDE else 1 - 0.13 * math.cos(WALK) ** 2, 1); ctx.translate(-x, 0)
        if not SIDE: ctx.translate(x, waist_y); ctx.rotate(-0.05 * math.sin(WALK)); ctx.translate(-x, -waist_y)
    # ---- arms ----
    la, le, ra, re = arms
    _piv = []
    if part != "all":
        la = le = ra = re = 0.0
        arms = (0.0, 0.0, 0.0, 0.0)
    if part == "body":
        ctx = _dummy
    sleeve = {"f": c.get("blouse"), "m": c.get("tunic"), "b": c.get("coat")}[kind]
    L1, L2 = 0.75 * u, 0.7 * u
    hands = []
    for s, a1, a2 in ((-1, la, le), (1, ra, re)):
        _far = bool(SIDE and _walking and s < 0)
        _sl = _dk(sleeve) if _far else sleeve
        _skn = _dk(c["skin"]) if _far else c["skin"]
        sx, sy = x + s * sh_w * (0.18 if (SIDE and _walking) else 0.88), sh_y + 0.12 * u
        _f1 = _f2 = 1.0
        if _walking and free_arms and not SIDE:                  # front view: a swinging arm shortens (foreshortening), forearm folds up when forward
            _sv = (-_sw if s < 0 else _sw)
            _f1 = 1 - 0.10 * abs(_sv); _f2 = 1 - 0.30 * max(0.0, _sv)
            sy -= 0.05 * u * max(0.0, _sv)
        ex, ey = sx + math.sin(a1) * L1 * _f1, sy + math.cos(a1) * L1 * _f1
        hx2, hy2 = ex + math.sin(a1 + a2) * L2 * _f2, ey + math.cos(a1 + a2) * L2 * _f2
        _piv.append((sx, sy, ex, ey))
        _side = "L" if s < 0 else "R"
        if part not in ("all", "body"): ctx = _real if part == "u" + _side else _dummy
        elif part == "all": ctx = _real
        tlimb(ctx, [(sx, sy), (ex, ey)], [0.31 * u, 0.24 * u], _skn if c.get("bare") else _sl, bulge=0.012 * u)
        if c.get("bare"):
            mx_, my_ = (sx + ex) / 2, (sy + ey) / 2
            ctx.move_to(mx_ - math.cos(a1) * 0.13 * u, my_ + math.sin(a1) * 0.13 * u); ctx.line_to(mx_ + math.cos(a1) * 0.13 * u, my_ - math.sin(a1) * 0.13 * u)
            ctx.set_source_rgb(*hexc(c.get("bandcol", "#f2c230"))); ctx.set_line_width(0.07 * u); ctx.stroke()
        if part not in ("all", "body"): ctx = _real if part == "f" + _side else _dummy
        tlimb(ctx, [(ex, ey), (hx2, hy2)], [0.23 * u, 0.15 * u] if kind != "f" else [0.18 * u, 0.115 * u], _sl if kind == "b" else _skn, bulge=0.015 * u, open_start=True)
        if kind == "f" or c.get("bare"):
            bx, by = ex + math.sin(a1 + a2) * L2 * 0.8, ey + math.cos(a1 + a2) * L2 * 0.8
            col = c.get("bandcol") or ("#e8b730" if (c.get("jewel") or c.get("bare")) else "#d9cfb8")
            ctx.arc(bx, by, 0.08 * u if kind == "f" else 0.1 * u, 0, 6.3); ctx.set_source_rgb(*hexc(col)); ctx.set_line_width(5); ctx.stroke()
        _hs = (hand[0] if s < 0 else hand[1]) if isinstance(hand, (tuple, list)) else hand
        if _hs:
            draw_hand(ctx, hx2, hy2, a1 + a2, u, _skn, _hs, s)
        else:
            ctx.arc(hx2, hy2, 0.11 * u, 0, 6.3); fill_stroke(ctx, _skn, 4)
        hands.append((hx2, hy2))
    if part not in ("all", "body"): ctx = _real if part == "fL" else _dummy
    elif part == "body": ctx = _dummy
    if c.get("kamandalu") and prop != "none":
        kx, ky = hands[0]
        ky += 0.18 * u
        ellipse(ctx, kx, ky + 0.12 * u, 0.2 * u, 0.17 * u); fill_stroke(ctx, "#5a3a1e", 4)
        ctx.rectangle(kx - 0.08 * u, ky - 0.06 * u, 0.16 * u, 0.06 * u); fill_stroke(ctx, "#5a3a1e", 3)
        ctx.move_to(kx + 0.17 * u, ky + 0.06 * u); ctx.line_to(kx + 0.32 * u, ky - 0.04 * u)
        ctx.set_source_rgb(*OL); ctx.set_line_width(0.06 * u + 5); ctx.stroke_preserve(); ctx.set_source_rgb(*hexc("#5a3a1e")); ctx.set_line_width(0.06 * u); ctx.stroke()
        ctx.arc(kx, ky - 0.06 * u, 0.14 * u, math.pi, 0); ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke()
        ctx.arc(kx, ky - 0.18 * u, 0.11 * u, 0, 6.3); fill_stroke(ctx, c["skin"], 4)
    ctx = _real
    if _walking: ctx.restore()
    if bend: ctx.restore()
    if _walking: ctx.restore()
    return dict(head=(hx, hy), u=u, hands=hands, top=top - 0.3 * u, pivots=_piv, headpiv=(hx, hy + 0.4 * u))


def turn_seq(p):
    """Head turn the way animators do it: the EYES reach the target first, then the head follows (eases in/out), blink at the start.
    p = 0..1 progress of the turn. Returns (turn, look, blink) for person(): turn=-1..1 head direction (sign = target side), look = pupil lead, blink bool."""
    p = max(0.0, min(1.0, p))
    e = lambda q: q * q * (3 - 2 * q)                       # slow in / slow out
    look = e(min(1.0, p / 0.35))                            # eyes arrive in the first third
    turn = e(max(0.0, (p - 0.15) / 0.85))                   # head starts a little later, settles slowly
    return turn, look, (0.08 < p < 0.22)
