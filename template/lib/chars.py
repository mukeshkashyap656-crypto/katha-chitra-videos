import math, cairo

OL = (0.16, 0.07, 0.04)      # bold dark outline
LW = 5.0
WALK = None   # set to a phase (radians) to draw walking legs

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

def limb(ctx, pts, w, col):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_source_rgb(*OL); ctx.set_line_width(w + 2 * LW); ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc(col)); ctx.set_line_width(w); ctx.stroke()

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
                       beard="#f8f6f0", mous="#f8f6f0", lower="#f6f0e2", crown=True, halo=True, jewel=True, bare=True,
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

def face(ctx, c, hx, hy, u, mouth="X", blink=False, emo="neutral", look=0.0):
    rx, ry = 0.40 * u * c.get("fw", 1.0), 0.48 * u * c.get("fh", 1.0)
    kind = c["kind"]
    if kind == "f":
        ellipse(ctx, hx, hy - 0.05 * u, rx * 1.08, ry * 1.02); fill_stroke(ctx, c["hair"])
        ellipse(ctx, hx, hy - 0.52 * u, 0.2 * u, 0.15 * u); fill_stroke(ctx, c["hair"])
    for s in (-1, 1):
        ellipse(ctx, hx + s * rx * 0.98, hy + 0.02 * u, 0.07 * u, 0.11 * u); fill_stroke(ctx, c["skin"], 4)
        if c.get("jewel"):
            if kind == "m":
                ctx.arc(hx + s * rx * 1.0, hy + 0.15 * u, 0.06 * u, 0, 6.3); ctx.set_source_rgb(*OL); ctx.set_line_width(7); ctx.stroke_preserve()
                ctx.set_source_rgb(*hexc("#f2c230")); ctx.set_line_width(4); ctx.stroke()
            else:
                ctx.arc(hx + s * rx * 0.98, hy + 0.16 * u, 0.04 * u, 0, 6.3); fill_stroke(ctx, "#e8b730", 3)
    ellipse(ctx, hx, hy, rx, ry); fill_stroke(ctx, c["skin"])
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
    # brows by emotion
    for s in (-1, 1):
        ex = hx + s * 0.16 * u; ey = hy - 0.17 * u - (0.06 * u if emo == "shock" else 0)
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
        ex = hx + s * 0.16 * u; ey = hy - 0.04 * u
        w, h = 0.12 * u * c.get("eye", 1.0), 0.065 * u * c.get("eye", 1.0) * c.get("eyeh", 1.0)
        if blink:
            ctx.move_to(ex - w, ey); ctx.curve_to(ex - w * 0.4, ey + h * 0.7, ex + w * 0.4, ey + h * 0.7, ex + w, ey)
            ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke(); continue
        def eyepath():
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
           look=0.0, bow=0.0, prop=None, t=0.0):
    """arms = (l_sh, l_el, r_sh, r_el) radians from straight-down; positive -> screen right."""
    c = CHARS[cname]
    H = H * c.get("tall", 1.0)
    bow = bow + c.get("stoop", 0.0)
    u = H / 5.0
    if c.get("child"):
        u = H / 4.2
    kind = c["kind"]
    top = feet - H
    if pose == "sit":
        top = feet - H * 0.72
    hx, hy = x, top + 0.5 * u + bow * u * 0.25
    sh_y = top + 1.12 * u
    sh_w = (0.62 * u if kind != "f" else 0.52 * u) * c.get("build", 1.0)
    bw = 0.45 * c.get("belly", 1.0)
    waist_y = top + 2.35 * u
    if arms is None:
        arms = (0.12, 0.05, -0.12, -0.05)
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
                    lift = dx = 0.0
                    if WALK is not None:   # walking: legs lift in turn, foot swings forward
                        ph = WALK + (0 if s < 0 else math.pi)
                        lift = max(0.0, math.sin(ph)) * 0.28 * u; dx = math.cos(ph) * 0.12 * u
                    fy = feet - lift
                    poly(ctx, [(x + s * 0.05 * u, waist_y + 0.6 * u), (x + s * 0.38 * u, waist_y + 0.6 * u),
                               (x + s * 0.28 * u + dx, fy - 0.05 * u), (x + s * 0.1 * u + dx, fy - 0.05 * u)])
                    fill_stroke(ctx, c["lower"])
                    ellipse(ctx, x + s * 0.24 * u + dx * 1.3, fy - 0.04 * u, 0.17 * u, 0.07 * u); fill_stroke(ctx, "#6b3a1e", 4)
                sk = c.get("skirt", 1.0)
                poly(ctx, [(x - (bw - 0.03) * u, waist_y), (x + (bw - 0.03) * u, waist_y), (x + (bw + 0.05 + 0.12 * sk) * u, waist_y + sk * u), (x - (bw + 0.05 + 0.12 * sk) * u, waist_y + sk * u)])
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
    # ---- head ----
    face(ctx, c, hx, hy, u, mouth, blink, emo, look)
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
    # ---- arms ----
    la, le, ra, re = arms
    sleeve = {"f": c.get("blouse"), "m": c.get("tunic"), "b": c.get("coat")}[kind]
    L1, L2 = 0.75 * u, 0.7 * u
    hands = []
    for s, a1, a2 in ((-1, la, le), (1, ra, re)):
        sx, sy = x + s * sh_w * 0.88, sh_y + 0.12 * u
        ex, ey = sx + math.sin(a1) * L1, sy + math.cos(a1) * L1
        hx2, hy2 = ex + math.sin(a1 + a2) * L2, ey + math.cos(a1 + a2) * L2
        limb(ctx, [(sx, sy), (ex, ey)], 0.24 * u, c["skin"] if c.get("bare") else sleeve)
        if c.get("bare"):
            mx_, my_ = (sx + ex) / 2, (sy + ey) / 2
            ctx.move_to(mx_ - math.cos(a1) * 0.13 * u, my_ + math.sin(a1) * 0.13 * u); ctx.line_to(mx_ + math.cos(a1) * 0.13 * u, my_ - math.sin(a1) * 0.13 * u)
            ctx.set_source_rgb(*hexc(c.get("bandcol", "#f2c230"))); ctx.set_line_width(0.07 * u); ctx.stroke()
        limb(ctx, [(ex, ey), (hx2, hy2)], 0.2 * u if kind != "f" else 0.15 * u, sleeve if kind == "b" else c["skin"])
        if kind == "f" or c.get("bare"):
            bx, by = ex + math.sin(a1 + a2) * L2 * 0.8, ey + math.cos(a1 + a2) * L2 * 0.8
            col = c.get("bandcol") or ("#e8b730" if (c.get("jewel") or c.get("bare")) else "#d9cfb8")
            ctx.arc(bx, by, 0.08 * u if kind == "f" else 0.1 * u, 0, 6.3); ctx.set_source_rgb(*hexc(col)); ctx.set_line_width(5); ctx.stroke()
        ctx.arc(hx2, hy2, 0.11 * u, 0, 6.3); fill_stroke(ctx, c["skin"], 4)
        hands.append((hx2, hy2))
    if c.get("kamandalu") and prop != "none":
        kx, ky = hands[0]
        ky += 0.18 * u
        ellipse(ctx, kx, ky + 0.12 * u, 0.2 * u, 0.17 * u); fill_stroke(ctx, "#5a3a1e", 4)
        ctx.rectangle(kx - 0.08 * u, ky - 0.06 * u, 0.16 * u, 0.06 * u); fill_stroke(ctx, "#5a3a1e", 3)
        ctx.move_to(kx + 0.17 * u, ky + 0.06 * u); ctx.line_to(kx + 0.32 * u, ky - 0.04 * u)
        ctx.set_source_rgb(*OL); ctx.set_line_width(0.06 * u + 5); ctx.stroke_preserve(); ctx.set_source_rgb(*hexc("#5a3a1e")); ctx.set_line_width(0.06 * u); ctx.stroke()
        ctx.arc(kx, ky - 0.06 * u, 0.14 * u, math.pi, 0); ctx.set_source_rgb(*OL); ctx.set_line_width(4); ctx.stroke()
        ctx.arc(kx, ky - 0.18 * u, 0.11 * u, 0, 6.3); fill_stroke(ctx, c["skin"], 4)
    return dict(head=(hx, hy), u=u, hands=hands, top=top - 0.3 * u)
