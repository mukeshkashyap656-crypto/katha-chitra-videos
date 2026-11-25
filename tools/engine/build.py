"""Katha Chitra scene engine, part 2: the HyperFrames video (Bhag 3 look) + cover, from episode.json SHOTS.
Run (make_episode.sh does it): EP=/tmp/ep EPDIR=episodes/bhagN python3 tools/engine/build.py
Camera follows the film rules in NIYAM.md: headroom over the crown, eyes near the upper third,
speaker close-ups keep neighbours fully out of frame, wide shots keep everyone fully in.
"""
import json, html, os, re, sys, math, random, zlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import spec as SP

P = os.environ.get("EP", "/tmp/ep") + "/proj"
EPI = SP.load(os.path.join(os.environ["EPDIR"], "episode.json"))
lip = json.load(open(f"{P}/lip.json"))
FPS = 30
SHOTS = EPI["SHOTS"]; ORDER = list(EPI["LINES"])

# ---------- words with exact spoken times ----------
def norm(s): return re.sub(r"[^ऀ-ॣ०-ॿ\w]", "", s)
def align(k):
    toks = lip[k]["text"].split(); bw = lip[k]["words"]
    bstarts, acc = [], 0
    for w in bw: bstarts.append(acc); acc += max(1, len(norm(w[0])))
    Lb = acc; dstarts, acc = [], 0
    for t in toks: dstarts.append(acc); acc += len(norm(t))
    ratio = Lb / max(1, acc); out = []
    for t, p in zip(toks, dstarts):
        q = p * ratio; j = max(i for i, b in enumerate(bstarts) if b <= q + 1e-6)
        ln = max(1, len(norm(bw[j][0]))); out.append((t, bw[j][1] + min(1, (q - bstarts[j]) / ln) * bw[j][2]))
    return out

# ---------- timing: lines one after another, a little longer pause when the place changes ----------
D = {k: lip[k]["dur"] for k in ORDER}
first_shot = {}
for i, sh in enumerate(SHOTS): first_shot.setdefault(sh["line"], i)
T = {}; t = 0.35
for n, k in enumerate(ORDER):
    if n:
        i = first_shot[k]; changed = i > 0 and SHOTS[i]["bg"] != SHOTS[i - 1]["bg"]
        t = T[ORDER[n - 1]] + D[ORDER[n - 1]] + (0.6 if changed else 0.35)
    T[k] = t
E = {k: T[k] + D[k] for k in ORDER}
WT = {k: [(w, T[k] + o) for w, o in align(k)] for k in ORDER}
def wt(k, sub):
    for w, tt in WT[k]:
        if sub in w or norm(sub) in norm(w): return tt
    return None

LAST = ORDER[-1]
T_SUBIN = wt(LAST, "कमेंट") or (T[LAST] + D[LAST] * 0.45)
T_FING = WT[LAST][-1][1] - 0.15
T_BELL = T_FING + 0.8
END = round(max(T_BELL + 0.35 + 1.4 + 0.4, E[LAST] + 0.3), 2)

# shot start times (shots sharing a line without at_word share it equally)
starts = []
for i, sh in enumerate(SHOTS):
    k = sh["line"]; same = [j for j, s in enumerate(SHOTS) if s["line"] == k]
    if i == 0: st = 0.0
    elif sh.get("at_word") and wt(k, sh["at_word"]) is not None: st = wt(k, sh["at_word"]) - 0.1
    elif i == same[0]: st = T[k] - 0.15
    else:
        free = [j for j in same if not SHOTS[j].get("at_word")]
        n = free.index(i) if i in free else 0
        st = T[k] - 0.15 + (D[k] + 0.15) * n / max(1, len(free))
    starts.append(max(st, (starts[-1] + 0.6) if starts else 0))
ends = starts[1:] + [END]


# ---------- arms as separate pieces: shoulder + elbow rotate smoothly (real cut-out animation) ----------
PIVOTS = json.load(open(f"{P}/assets/pivots.json")) if os.path.exists(f"{P}/assets/pivots.json") else {}
POSE_ARMS = {"stand": (0.10, 0.06, -0.10, -0.06), "talk": (0.10, 0.10, 0.55, -0.95), "bless": (0.10, 0.10, 0.55, -0.95),
             "point": (0.10, 0.10, 1.25, 0.25), "raise": (0.10, 0.10, 2.45, 0.25), "namaste": (-0.1, 2.18, 0.1, -2.18),
             "angry": (0.6, 0.9, -0.6, -0.9)}
# talking gestures: (left a1,a2) / (right a1,a2); None = stay at rest
GESTURES = [(None, (0.60, -0.95)), ((0.30, 0.60), (0.95, -0.55)), (None, (1.05, -1.30)), ((-0.45, 0.85), (0.45, -0.85)),
            (None, (0.35, -1.35)), ((0.15, 1.0), (0.2, -1.0))]
def deg(a): return -a * 180 / math.pi

# Har character ka apna body-language (insaan sab alag hote hain): aaram ka pose, ishare ki gati/badai, saans, jhukaav.
#   rest = (la, le, ra, re); gest = GESTURES ke index; gap = ishare ke beech ka samay (sec); gs = ishare ki badai;
#   sway = hilna; tempo = saans ki gati (bada = dheema); lean = degree mein tirchha khada hona
STYLES = {
    "vishwamitra": dict(rest=(0.10, 0.22, -0.09, -0.10), gest=(0, 2), gap=2.4, gs=1.0, sway=0.5, tempo=1.3, lean=0.0, talkel=0.55, nod=0.6),   # kathor, kam ishare, kamandalu baayein haath mein
    "ram":         dict(rest=(0.10, 0.34, -0.10, -0.34), gest=(0, 4), gap=2.9, gs=0.7, sway=0.6, tempo=1.2, lean=0.0, talkel=0.6, nod=0.7),    # shaant, sanyat, haath dheele aage
    "lakshman":    dict(rest=(0.13, 0.10, -0.13, -0.10), gest=(0, 1, 3, 2), gap=1.2, gs=1.2, sway=1.4, tempo=0.8, lean=0.0, talkel=1.0, nod=1.4),  # tez, chaukanna
    "vasishtha":   dict(rest=(0.09, 0.16, -0.10, -0.18), gest=(0, 2), gap=3.2, gs=0.8, sway=0.4, tempo=1.6, lean=0.0, talkel=0.45, nod=0.5),   # buzurg, dheere
    "dasharatha":  dict(rest=(0.12, 0.28, -0.12, -0.28), gest=(1, 3), gap=2.6, gs=1.1, sway=0.5, tempo=1.4, lean=0.0, talkel=0.6, nod=0.8),    # raja, bhaari
    "_female":     dict(rest=(0.08, 0.40, -0.08, -0.40), gest=(4, 5, 0), gap=2.2, gs=0.8, sway=1.0, tempo=1.0, lean=0.0, talkel=0.85, nod=1.0),  # komal, haath aage
    "_devta":      dict(rest=(0.18, 0.08, -0.18, -0.08), gest=(3, 2, 0), gap=2.0, gs=1.25, sway=0.4, tempo=1.5, lean=0.0, talkel=0.4, nod=0.6), # bhavya, khule haath
    "_rakshas":    dict(rest=(0.30, 0.22, -0.30, -0.22), gest=(2, 1), gap=1.4, gs=1.3, sway=1.2, tempo=0.9, lean=0.0, talkel=0.7, nod=1.3),      # bhaari
    "_elder":      dict(rest=(0.09, 0.16, -0.10, -0.18), gest=(0, 2), gap=3.0, gs=0.8, sway=0.5, tempo=1.5, lean=0.0, talkel=0.5, nod=0.6),
    "_man":        dict(rest=(0.10, 0.12, -0.10, -0.12), gest=(0, 1, 2), gap=1.9, gs=1.0, sway=1.0, tempo=1.0, lean=0.0, talkel=0.7, nod=1.0),
}
def body_style(e, meta):
    who = e["who"]
    if who in STYLES: return STYLES[who]
    nc = EPI.get("NEW_CHARS", {}).get(who, {})
    if meta.get("rakshas"): return STYLES["_rakshas"]
    if meta.get("big"): return STYLES["_devta"]
    if nc.get("kind") == "f" or who.startswith("kanya") or who in ("sita", "urmila"): return STYLES["_female"]
    if nc.get("age", 0) >= 2 or who.startswith("rishi") or who in ("mantri",): return STYLES["_elder"]
    return STYLES["_man"]

def arm_js(cid, e, t0, t1, speak, rest_style, style=None):
    """GSAP for the 4 joints of one person: gentle idle sway + (while speaking) hand gestures with a smooth go / hold / return,
    all in this character's own style (STYLES)."""
    st = style or STYLES["_man"]
    pose = e.get("pose", "stand"); rest = list(POSE_ARMS[pose]); rnd = random.Random(zlib.crc32(cid.encode()))
    if pose in ("stand", "talk", "bless"):
        r0 = list(st["rest"])
        if pose == "stand": rest = r0
        else: rest = [r0[0], r0[1]] + rest[2:]            # talk/bless: right arm stays raised, left follows the character's own rest
    joints = ["uL", "fL", "uR", "fR"]; amp = {"u": 0.03 * st["sway"], "f": 0.055 * st["sway"]}
    if pose == "namaste": amp = {"u": 0.006, "f": 0.008}
    wp = {j: [(t0, rest[i])] for i, j in enumerate(joints)}      # waypoints (time, angle) per joint
    gest = []                                                      # (start, end) windows
    base_ = rest; talking = bool(speak and pose in ("stand", "talk", "bless") and speak[1] - speak[0] > 1.0)
    if talking:
        # HUMAN RULE: while talking, forearms come UP to belly / chest height (hands hanging down = a doll). Lift before the first word,
        # keep it while speaking, lower after the last word.
        el = st.get("talkel", 0.7)
        base_ = [rest[0] + 0.04, max(rest[1], el), rest[2] - 0.04, min(rest[3], -el)]
        a_, b_ = max(t0 + 0.05, speak[0] - 0.12), speak[0] + 0.30
        for i, j in enumerate(joints): wp[j] += [(a_, rest[i]), (b_, base_[i])]
        c_, d_ = speak[1], min(t1 - 0.02, speak[1] + 0.55)
        if d_ > c_ + 0.1:
            for i, j in enumerate(joints): wp[j] += [(c_, base_[i]), (d_, rest[i])]
        t = b_ + 0.45; k = 0                                       # BEATS: small flick of one forearm on the stress of the words, hands take turns
        while t < c_ - 0.4:
            jb = ("fL", "fR")[(k + zlib.crc32(cid.encode())) % 2]; ib = joints.index(jb); sgn = 1 if ib == 1 else -1
            wp[jb] += [(t, base_[ib]), (t + 0.11, base_[ib] + sgn * 0.20), (t + 0.34, base_[ib])]
            t += 0.55 + rnd.random() * 0.6; k += 1
    if talking:
        g = speak[0] + 0.7 + rnd.random() * 0.3; n = 0
        while g + 1.35 < speak[1]:
            gl, gr = GESTURES[st["gest"][(n + zlib.crc32(cid.encode())) % len(st["gest"])]]; n += 1
            gsc = st["gs"]
            for (tgt, j1, j2, ri) in ((gl, "uL", "fL", 0), (gr, "uR", "fR", 2)):
                if tgt is None: continue
                a1 = base_[ri] + (tgt[0] - base_[ri]) * gsc; a2 = base_[ri + 1] + (tgt[1] - base_[ri + 1]) * gsc
                wp[j1] += [(g, base_[ri]), (g + 0.38, a1), (g + 0.80, a1 + 0.10), (g + 1.25, base_[ri])]
                wp[j2] += [(g, base_[ri + 1]), (g + 0.38, a2), (g + 0.80, a2 - 0.10), (g + 1.25, base_[ri + 1])]
            gest.append((g, g + 1.25))
            g += 1.25 + st["gap"] * (0.7 + 0.6 * rnd.random())
    arm_js.last_gest = gest
    out = []
    for i, j in enumerate(joints):
        pts = wp[j]; a = amp[j[0]]
        t = t0 + 0.8 + rnd.random() * 0.8; idle = []
        while t < t1:
            if not any(gs - 0.5 <= t <= ge + 0.2 for gs, ge in gest) and not (talking and speak[0] - 0.3 <= t <= speak[1] + 0.6): idle.append((t, rest[i] + (rnd.random() * 2 - 1) * a))
            t += 1.3 + rnd.random() * 0.8
        allp = sorted([q for q in pts[1:] if q[1] is not None] + idle, key=lambda q: q[0])
        el = f"#{cid}{j}"; cur_t, cur_v = t0, rest[i]
        out.append(f'tl.set("{el}",{{rotation:{deg(rest[i]):.2f}}},0);')
        for (tt, vv) in allp:
            if tt <= cur_t + 0.05: continue
            ease = "power2.inOut" if any(gs - 0.01 <= tt <= ge + 0.01 for gs, ge in gest) else "sine.inOut"
            out.append(f'tl.to("{el}",{{rotation:{deg(vv):.2f},duration:{tt - cur_t:.2f},ease:"{ease}",immediateRender:false}},{cur_t:.3f});')
            cur_t, cur_v = tt, vv
    for (gs, ge) in gest:                                           # open hand while gesturing, relaxed otherwise
        if rest_style != "open":
            for sd in ("L", "R"):
                out.append(f'tl.set("#{cid}f{sd}-{rest_style}",{{opacity:0}},{gs + 0.1:.3f});tl.set("#{cid}f{sd}-open",{{opacity:1}},{gs + 0.1:.3f});')
                out.append(f'tl.set("#{cid}f{sd}-open",{{opacity:0}},{ge - 0.2:.3f});tl.set("#{cid}f{sd}-{rest_style}",{{opacity:1}},{ge - 0.2:.3f});')
    return out


def head_js(cid, e, t0, t1, speak, st, seed, gest):
    """Head animation (2D-animator rules): the head lags behind the body (follow-through), dips a little BEFORE a hand gesture
    (anticipation), nods on the beat of speech, drifts when idle and settles into every shot with a tiny overshoot.
    Every key (time, y, rotation) goes into ONE sorted list and is played one after the other, so tweens never fight. st['nod'] = how much."""
    rnd = random.Random(zlib.crc32((cid + "h").encode())); amp = st.get("nod", 1.0); el = f"#{cid}h"
    sg = 1 if seed % 2 else -1; ev = []
    t = t0 + 0.9
    while t < t1 - 0.4:                                           # idle drift
        ev.append((t, (rnd.random() * 2 - 1) * 1.5, (rnd.random() * 2 - 1) * 0.9 * amp)); t += 1.4 + rnd.random() * 1.0
    if speak and speak[1] - speak[0] > 0.6:
        ev = [q for q in ev if not (speak[0] - 0.3 < q[0] < speak[1] + 0.2)]
        t = speak[0] + 0.15; k = 0
        while t < speak[1] - 0.3:                                 # nod on the beat of the words (uneven)
            ev.append((t, 2.6 * amp, (rnd.random() * 2 - 1) * 1.1 * amp)); ev.append((t + 0.22, -1.0 * amp, 0.0))
            t += 0.5 + rnd.random() * 0.5; k += 1
    for (gs, ge) in (gest or []):                                 # anticipation: chin dips just before the hand moves
        ev = [q for q in ev if not (gs - 0.35 < q[0] < gs + 0.5)]
        ev.append((max(t0 + 0.2, gs - 0.1), 3.0 * amp, 1.3 * sg * amp)); ev.append((gs + 0.3, -1.8 * amp, -0.7 * sg * amp))
    ev.sort(key=lambda q: q[0])
    out = [f'tl.fromTo("{el}",{{y:-7,rotation:{-1.3 * sg * amp:.2f}}},{{y:0,rotation:0,duration:0.55,ease:"back.out(2.2)",immediateRender:false}},{t0:.3f});']
    cur = t0 + 0.6
    for (tt, y, r) in ev:
        if tt < cur + 0.12 or tt > t1 - 0.05: continue
        out.append(f'tl.to("{el}",{{y:{y:.1f},rotation:{r:.2f},duration:{tt - cur:.2f},ease:"sine.inOut",immediateRender:false}},{cur:.3f});'); cur = tt
    return out


# ---------- characters ----------
DW, DH, DTOP = 689, 935, 582          # human picture size + top (feet stand on y=1480)
BW, BH, BTOP = 837, 1107, 409         # big (devta/rakshasa) picture
U_H, HEAD_H = 128, 904                # human: head unit + head centre (world px)
U_B, HEAD_B = 160, 760
def is_big(who): return bool(SP.char_meta(who, EPI).get("big"))
def blink(t, off): return (t + off) % 3.4 < 0.12
LIP_LEAD = 3            # animators: mouth shapes come 2-4 frames BEFORE the sound (see ANIMATION.md); tune here
def mouth(k, t):
    sh = lip[k]["shapes"]; f = int((t - T[k]) * FPS) + LIP_LEAD
    return sh[f] if 0 <= f < len(sh) else "X"

sets = []; layers = []; moves = []
for si, sh in enumerate(SHOTS):
    t0, t1 = starts[si], ends[si]; k = sh["line"]; sp = SP.speaker(k, EPI)
    html_c = []
    for ci, e in enumerate(sh.get("cast", [])):
        base, p = SP.state_base(e, sh, EPI); keys = list(SP.shot_states(e, sh, EPI))
        lay = SP.layered(e, sh) and p["who"] in PIVOTS
        hb = f"{base}_h" if lay else base                     # layered people: only the HEAD picture changes (blink / mouth)
        off = (ci * 1.3 + si * 0.7) % 3.4
        def state(t, e=e, base=hb, p=p, keys=keys, off=off):
            if p["pose"] == "walk": return f"{base}_walk{int((t - t0) / 0.13) % 4}"
            if sp == e["who"] and T[k] - LIP_LEAD / FPS <= t < E[k] and not p["shadow"]:
                m = mouth(k, t); return base if m == "X" else f"{base}_{m}"
            return f"{base}_blink" if blink(t, off) and f"{base}_blink" in keys else base
        cid = f"s{si}c{ci}"; big = is_big(e["who"]); w_, h_, top = (BW, BH, BTOP) if big else (DW, DH, DTOP)
        top -= e.get("lift", 0)
        first = state(t0)
        _mk = lambda kk: f'<img id="{cid}-{kk}" class="ci" src="assets/{kk}.png" style="width:{w_}px;height:{h_}px;opacity:{1 if kk == first else 0}">'
        if lay:
            _hx, _hy = [v * (w_ / PIVOTS[p["who"]]["cw"]) for v in PIVOTS[p["who"]]["head"]]
            imgs = _mk(base) .replace('opacity:0', 'opacity:1') + (f'<div id="{cid}h" style="position:absolute;left:0;top:0;width:{w_}px;height:{h_}px;transform-origin:{_hx:.1f}px {_hy:.1f}px">'
                    + "".join(_mk(kk) for kk in keys if kk.startswith(hb)) + '</div>')
        else:
            imgs = "".join(_mk(kk) for kk in keys)
        arms_html = ""
        if SP.layered(e, sh) and p["who"] in PIVOTS:
            kit = p["who"]; pv = PIVOTS[kit]; fs = w_ / pv["cw"]; rs = SP.HAND_BY_POSE.get(e.get("pose", "stand"), "relaxed")
            for sd, ix in (("L", 0), ("R", 1)):
                sx, sy, ex, ey = [v * fs for v in pv["piv"][ix]]
                fimgs = "".join(f'<img id="{cid}f{sd}-{st}" class="ci" src="assets/arm_{kit}_f{sd}_{st}.png" style="width:{w_}px;height:{h_}px;opacity:{1 if st == rs else 0}">' for st in SP.hand_styles(e))
                arms_html += (f'<div id="{cid}u{sd}" style="position:absolute;left:0;top:0;width:{w_}px;height:{h_}px;transform-origin:{sx:.1f}px {sy:.1f}px">'
                              f'<img class="ci" src="assets/arm_{kit}_u{sd}.png" style="width:{w_}px;height:{h_}px">'
                              f'<div id="{cid}f{sd}" style="position:absolute;left:0;top:0;width:{w_}px;height:{h_}px;transform-origin:{ex:.1f}px {ey:.1f}px">{fimgs}</div></div>')
            _spk = (max(t0, T[k]), min(t1, E[k])) if sp == e["who"] else None
            moves.extend(arm_js(cid, e, t0, t1, _spk, rs, body_style(e, SP.char_meta(p["who"], EPI) | SP.char_meta(e["who"], EPI))))
        html_c.append(f'<div class="char" id="{cid}" style="left:{e["x"] - w_ / 2:.0f}px;top:{top}px;width:{w_}px;height:{h_}px"><div id="{cid}i" style="position:absolute;left:0;top:0;width:{w_}px;height:{h_}px;transform-origin:50% 96%">{imgs}{arms_html}</div></div>')
        if e.get("tilt"):      # wounded / leaning: the whole person leans a little (about the feet), e.g. a dying warrior propped on the ground
            moves.append(f'tl.set("#{cid}",{{rotation:{e["tilt"]},transformOrigin:"50% 96%"}},{t0:.3f});')
        # ---- life (puppet fix): breathing, slow weight sway, and a small nod on every beat while this person speaks ----
        _dur = max(0.4, t1 - t0); _bs = body_style(e, SP.char_meta(p["who"], EPI) | SP.char_meta(e["who"], EPI))
        _pb = (1.9 + 0.35 * ((ci + si) % 3)) * _bs["tempo"]     # each person breathes at his own pace
        moves.append(f'tl.to("#{cid}i",{{scaleY:1.016,scaleX:0.997,duration:{_pb / 2:.2f},ease:"sine.inOut",yoyo:true,repeat:{max(1, int(_dur / (_pb / 2)))},immediateRender:false}},{t0:.3f});')
        _ps = 3.2 + 0.5 * ((ci * 2 + si) % 3); _sg = 1 if (ci + si) % 2 else -1; _ln = _bs["lean"]; _am = 0.18 * _bs["sway"]
        moves.append(f'tl.fromTo("#{cid}i",{{rotation:{_ln - _am * _sg:.2f}}},{{rotation:{_ln + _am * _sg:.2f},duration:{_ps / 2:.2f},ease:"sine.inOut",yoyo:true,repeat:{max(1, int(_dur / (_ps / 2)))},immediateRender:false}},{t0:.3f});')
        if lay:
            moves.extend(head_js(cid, e, t0, t1, (max(t0, T[k]), min(t1, E[k])) if sp == e["who"] else None, _bs, ci + si, arm_js.last_gest))
        elif sp == e["who"] and not p["shadow"] and p["pose"] != "walk":
            _s0, _s1 = max(t0, T[k]), min(t1, E[k])
            if _s1 - _s0 > 0.6:
                _per = 0.62
                moves.append(f'tl.fromTo("#{cid}i",{{y:0}},{{y:-3,duration:{_per / 2:.2f},ease:"sine.inOut",yoyo:true,repeat:{max(1, int((_s1 - _s0) / (_per / 2)))},immediateRender:false}},{_s0:.3f});')
        prev = first
        for f in range(int(t0 * FPS) + 1, int(t1 * FPS) + 1):
            s_ = state(f / FPS)
            if s_ != prev:
                sets.append(f'tl.set("#{cid}-{prev}",{{opacity:0}},{f / FPS:.3f});tl.set("#{cid}-{s_}",{{opacity:1}},{f / FPS:.3f});'); prev = s_
        if p["pose"] == "walk":
            moves.append(f'tl.fromTo("#{cid}",{{x:0}},{{x:{e["to_x"] - e["x"]},duration:{(t1 - t0) * 0.9:.3f},ease:"none",immediateRender:false}},{t0:.3f});')
    layers.append(f'<div class="lay shot" id="shot{si}" style="opacity:{1 if si == 0 else 0}"><img class="wfull" src="assets/bg_{sh["bg"]}.png">{"".join(html_c)}</div>')

# ---------- fx: astra (glowing arrow) with result, rain ----------
fx_html = {}; fx_js = []; fx_aud = []
def chest(e):
    lift = e.get("lift", 0)
    return (e["x"], (950 if is_big(e["who"]) else 1090) - lift)
for si, sh in enumerate(SHOTS):
    t0, t1 = starts[si], ends[si]; k = sh["line"]; cast = sh.get("cast", []); parts = []
    for fi, fx in enumerate(sh.get("fx", [])):
        tf = (wt(k, fx["at_word"]) if fx.get("at_word") else None) or (t0 + 0.5)
        tf = max(t0 + 0.2, min(tf, t1 - 1.0))
        if fx["type"] == "rain":
            col = fx.get("color", "#b0101a"); import random as _r; rr = _r.Random(si * 7 + fi)
            for d in range(70):
                x0 = rr.uniform(0, 1360); dl = rr.uniform(0, 0.7); ln = rr.uniform(30, 60)
                did = f"rn{si}_{fi}_{d}"
                parts.append(f'<div id="{did}" style="position:absolute;left:{x0:.0f}px;top:-80px;width:5px;height:{ln:.0f}px;border-radius:3px;background:{col};opacity:.85;transform:rotate(8deg)"></div>')
                fx_js.append(f'tl.fromTo("#{did}",{{y:0}},{{y:1760,duration:0.75,ease:"none",repeat:{max(1, int((t1 - t0) / 0.75))},immediateRender:false}},{t0 + dl:.3f});')
            continue
        src = next(e for e in cast if e["who"] == fx["from"]); dst = next(e for e in cast if e["who"] == fx["to"])
        (ax, ay), (bx, by) = chest(src), chest(dst)
        d = 1 if bx > ax else -1; ax += d * 90; bx -= d * 60
        import math as _m; ang = _m.degrees(_m.atan2(by - ay, bx - ax))
        col = fx.get("color", "#9fe0ff"); aid = f"as{si}_{fi}"; fid = f"fl{si}_{fi}"; fly = 0.34; hit = tf + fly
        parts.append(f'<div id="{aid}" style="position:absolute;left:{ax:.0f}px;top:{ay:.0f}px;width:0;height:0;opacity:0">'
                     f'<div style="position:absolute;left:-230px;top:-9px;width:260px;height:18px;transform-origin:230px 9px;transform:rotate({ang:.1f}deg);'
                     f'border-radius:9px;background:linear-gradient(90deg,rgba(255,255,255,0),{col} 55%,#fff);box-shadow:0 0 22px {col},0 0 48px {col}"></div></div>')
        parts.append(f'<div id="{fid}" style="position:absolute;left:{bx - 160:.0f}px;top:{by - 160:.0f}px;width:320px;height:320px;border-radius:50%;'
                     f'background:radial-gradient(circle,#fff 0%,{col} 35%,rgba(255,255,255,0) 70%);opacity:0"></div>')
        fx_js.append(f'tl.set("#{aid}",{{opacity:1,x:0,y:0}},{tf:.3f});tl.to("#{aid}",{{x:{bx - ax:.0f},y:{by - ay:.0f},duration:{fly},ease:"power1.in"}},{tf:.3f});tl.set("#{aid}",{{opacity:0}},{hit:.3f});')
        fx_js.append(f'tl.fromTo("#{fid}",{{opacity:1,scale:0.2}},{{opacity:0,scale:2.3,duration:0.55,ease:"power2.out",immediateRender:false}},{hit:.3f});')
        fx_aud.append(f'<audio id="sw{si}_{fi}" src="assets/sfx_swish.wav" data-start="{tf:.3f}" data-duration="0.25" data-volume="0.9"></audio>')
        fx_aud.append(f'<audio id="im{si}_{fi}" src="assets/sfx_impact.wav" data-start="{hit:.3f}" data-duration="1.0" data-volume="0.85"></audio>')
        ci = cast.index(dst); cid = f"s{si}c{ci}"
        if fx.get("result") == "thrown":       # flies far away (e.g. Maricha into the sea)
            fx_js.append(f'tl.to("#{cid}",{{x:{d * 950},y:-760,rotation:{d * 40},scale:0.12,duration:1.15,ease:"power2.in"}},{hit + 0.08:.3f});tl.set("#{cid}",{{opacity:0}},{hit + 1.25:.3f});')
            fx_aud.append(f'<audio id="wb{si}_{fi}" src="assets/sfx_whoosh_big.wav" data-start="{hit + 0.05:.3f}" data-duration="1.02" data-volume="0.7"></audio>')
        elif fx.get("result") == "fall":       # falls down and fades (no blood)
            fx_js.append(f'tl.to("#{cid}",{{rotation:{d * 82},transformOrigin:"50% 92%",duration:0.75,ease:"power2.in"}},{hit + 0.1:.3f});tl.to("#{cid}",{{opacity:0,duration:0.7}},{hit + 1.0:.3f});')
            fx_aud.append(f'<audio id="th{si}_{fi}" src="assets/sfx_thunder.wav" data-start="{hit + 0.8:.3f}" data-duration="1.5" data-volume="0.5"></audio>')
    if parts: fx_html[si] = "".join(parts)
for si, extra in fx_html.items():
    l = layers[si]; layers[si] = l[:-len("</div>")] + extra + "</div>"

# ---------- camera: world 1360x1660 seen through a 1008x1228 window ----------
WW, WH, VW, VH = 1360, 1660, 1008, 1228; S0 = VW / WW
def cam(px, py, z):
    s = S0 * z; x = VW / 2 - s * px; y = VH / 2 - s * py
    x = min(0, max(VW - WW * s, x)); y = min(0, max(VH - WH * s, y))
    return f"x:{x:.1f},y:{y:.1f},scale:{s:.4f}"
def half_w(who): return 145 if is_big(who) else 118
def wide(cast, z_max=1.25):
    if not cast: return (680, 830, 1.0)
    # walkers: the whole path (start and end) stays in frame; lifted (flying) people: their raised top too
    lo = min(min(e["x"], e.get("to_x", e["x"])) - half_w(e["who"]) for e in cast) - 70
    hi = max(max(e["x"], e.get("to_x", e["x"])) + half_w(e["who"]) for e in cast) + 70
    z = max(1.0, min(z_max, WW / max(1, hi - lo)))
    vh = VH / (S0 * z); top_need = min((BTOP if is_big(e["who"]) else DTOP + 180) - e.get("lift", 0) for e in cast)   # whole body + crown inside
    cy = min(1480 + 60 - vh / 2, max(top_need - 40 + vh / 2, 830))
    return ((lo + hi) / 2, cy, z)
def closeup(e, cast, zs=(2.6, 2.8, 3.0, 3.3, 3.6, 3.9)):
    big = is_big(e["who"]); u, hy = (U_B, HEAD_B) if big else (U_H, HEAD_H)
    sx, sb = e["x"], half_w(e["who"])
    for z in zs:
        hw = VW / (S0 * z) / 2; vh = VH / (S0 * z)
        lo, hi = sx + sb - hw, sx - sb + hw          # camera x range keeping the speaker inside
        for o in cast:
            if o is e: continue
            ob = half_w(o["who"]) + 60       # bow tips / raised arms stick out beyond the body
            if o["x"] > sx: hi = min(hi, o["x"] - ob - hw)   # neighbour on the right fully out
            else: lo = max(lo, o["x"] + ob + hw)             # neighbour on the left fully out
        if lo <= hi:
            cx = min(max(sx, lo), hi)
            cy = hy + 0.17 * vh                        # eyes near the upper third
            cy = max(cy, hy - 1.75 * u + vh / 2)       # headroom: a forehead of space above crown / jata
            return (cx, cy, z)
    return None
def two(e, cast):
    near = sorted((o for o in cast if o is not e), key=lambda o: abs(o["x"] - e["x"]))[:1]
    return wide([e] + near, z_max=1.6)
def medium(e, cast):      # knee-up shot of one person (neighbours fully out)
    return closeup(e, cast, zs=(1.7, 1.85, 2.0, 2.2, 2.4))
cam_js = []
SEG = 2.8                # a cut / new framing about every 2-3 s (NIYAM: cut or camera move every 2-3 s)
for si, sh in enumerate(SHOTS):
    cast = sh.get("cast", []); sp = SP.speaker(sh["line"], EPI); mode = sh.get("cam", "auto")
    spe = next((e for e in cast if e["who"] == sp), None)
    main = spe or (min(cast, key=lambda e: abs(e["x"] - 680)) if cast else None)
    if mode == "auto":
        new_place = si == 0 or SHOTS[si - 1]["bg"] != sh["bg"]
        mode = "speaker" if spe and not new_place and len(cast) > 1 else ("speaker" if spe and len(cast) == 1 else "wide")
    target = None
    if mode == "speaker" and spe: target = closeup(spe, cast)
    if mode == "two" and spe: target = two(spe, cast)
    if target is None: target = wide(cast)
    alt = None             # second framing for long shots
    action = sh.get("fx") or any(e.get("pose") == "walk" for e in cast)
    if action: target = wide(cast)   # astra / walking: everyone (and the whole path) stays in view
    if main is not None and not action:
        alt = (medium(main, cast) or closeup(main, cast)) if target[2] < 1.6 else wide(cast)
    t0, t1 = starts[si], ends[si]; dur = t1 - t0
    n = 1 if dur <= 3.6 else max(2, round(dur / SEG))
    last = si == len(SHOTS) - 1
    for g in range(n):
        a = t0 + dur * g / n; b = t0 + dur * (g + 1) / n
        odd = ((n - 1 - g) if last else g) % 2 == 1          # last shot ends on its main (wide) framing, big '?' visible
        x, y, z = (alt if (odd and alt) else target)
        if not alt and odd and not action: z *= 1.18        # nobody to cut to: gentle push-in instead
        if last and g == n - 1 and z < 2:                     # last framing: feet above the subscribe widget
            y = WH - VH / (S0 * z) / 2
        cam_js.append(f'tl.set("#cam",{{{cam(x, y, z)}}},{a:.3f});tl.to("#cam",{{{cam(x, y - 6, z * 1.05)},duration:{max(0.1, b - a - 0.02):.3f},ease:"none"}},{a:.3f});')

# ---------- shots switch, mood colour, chips, birds ----------
TINT = {"none": "rgba(0,0,0,0)", "joy": "rgba(255,190,80,.12)", "sorrow": "rgba(60,80,130,.32)", "anger": "rgba(200,25,10,.26)",
        "fear": "rgba(70,0,0,.42)", "wonder": "rgba(255,210,90,.18)", "night": "rgba(10,20,60,.45)"}
shot_js = []; chip_html = []
for si, sh in enumerate(SHOTS):
    t0, t1 = starts[si], ends[si]
    if si: shot_js.append(f'tl.set("#shot{si - 1}",{{opacity:0}},{t0:.3f});tl.set("#shot{si}",{{opacity:1}},{t0:.3f});')
    shot_js.append(f'tl.set("#tint",{{background:"{TINT[sh.get("mood", "none")]}"}},{t0:.3f});')
    if sh.get("chip"):
        chip_html.append(f'<div class="chip" id="chip{si}">{html.escape(sh["chip"])}</div>')
        shot_js.append(f'tl.fromTo("#chip{si}",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.25,immediateRender:false}},{t0 + 0.1:.3f});tl.set("#chip{si}",{{opacity:0}},{t1:.3f});')
    if sh["bg"] in ("morning", "cloudvan", "ashram", "river") and (si == 0 or SHOTS[si - 1]["bg"] != sh["bg"]):
        shot_js.append(f'tl.fromTo("#birds",{{x:0,y:0,opacity:1}},{{x:1750,y:-120,opacity:1,duration:5,ease:"none",immediateRender:false}},{t0:.3f});')

# ---------- subtitles: speaker name + karaoke words ----------
NAMES = {k: SP.hindi_name(SP.speaker(k, EPI), EPI) for k in ORDER if SP.speaker(k, EPI)}
LINEKEYS = {k: set(EPI["KEYWORDS"].get(k, [])) for k in ORDER}
LINEKEYS[LAST] |= {"जय", "श्री", "राम"}
def is_key(k, w):
    n = norm(w); return any(n == norm(x) or n.rstrip("ा") == norm(x) or n.startswith(norm(x)) for x in LINEKEYS[k] if norm(x))
def chunks(k):
    out, cur, ln = [], [], 0
    for i, (w, _) in enumerate(WT[k]):
        cur.append(i); ln += len(w) + 1
        if ln > 30 or w.endswith(("।", "!", "?", "...", ",")) and ln > 12:
            out.append(cur); cur, ln = [], 0
    if cur:
        if out and sum(len(WT[k][i][0]) + 1 for i in cur) < 9: out[-1] += cur
        else: out.append(cur)
    return out
LINE_OFF = {k: (min(E[k] + 0.25, T[ORDER[i + 1]] - 0.36) if i + 1 < len(ORDER) else E[k] + 0.25) for i, k in enumerate(ORDER)}
sub_html = []; sub_js = []
for k in ORDER:
    cs = chunks(k); body = []
    for ci, idx in enumerate(cs):
        spans = "".join(f'<span id="w{k}{i}" class="w{" key" if is_key(k, WT[k][i][0]) else ""}">{html.escape(WT[k][i][0])}</span> ' for i in idx)
        body.append(f'<div class="chunk" id="c{k}{ci}">{spans}</div>')
        t_on = T[k] - 0.18 if ci == 0 else WT[k][idx[0]][1] - 0.08
        t_off = (WT[k][cs[ci + 1][0]][1] - 0.16) if ci + 1 < len(cs) else LINE_OFF[k]
        sub_js.append(f'tl.to("#c{k}{ci}",{{opacity:1,duration:0.08}},{t_on:.3f});tl.to("#c{k}{ci}",{{opacity:0,duration:0.07}},{t_off:.3f});')
    nm = f'<div class="name">{html.escape(NAMES[k])}</div>' if k in NAMES else ""
    sub_html.append(f'<div class="sline" id="L{k}">{nm}{"".join(body)}</div>')
    sub_js.append(f'tl.set("#L{k}",{{opacity:1}},{T[k] - 0.2:.3f});tl.set("#L{k}",{{opacity:0}},{LINE_OFF[k] + 0.08:.3f});')
    for i, (w, tt) in enumerate(WT[k]): sub_js.append(f'tl.to("#w{k}{i}",{{opacity:1,duration:0.08}},{tt:.3f});')

# ---------- sounds ----------
AMB = {"morning": ("sfx_morning", 0.6), "cloudvan": ("sfx_morning", 0.6), "ashram": ("sfx_morning", 0.55), "river": ("sfx_morning", 0.55),
       "ghorvan": ("sfx_dark", 0.75), "divine": ("sfx_pad", 0.6), "palace": ("sfx_pad", 0.4)}
aud = []; seg0 = 0
for si in range(1, len(SHOTS) + 1):
    if si == len(SHOTS) or SHOTS[si]["bg"] != SHOTS[seg0]["bg"]:
        f, v = AMB[SHOTS[seg0]["bg"]]; a, b = starts[seg0], (starts[si] if si < len(SHOTS) else END)
        aud.append(f'<audio id="amb{seg0}" src="assets/{f}.wav" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-volume="{v}" data-fade-out="0.4"></audio>')
        if si < len(SHOTS): aud.append(f'<audio id="wh{si}" src="assets/sfx_whoosh_soft.wav" data-start="{max(0, starts[si] - 0.45):.3f}" data-duration="1.05" data-volume="0.5"></audio>')
        seg0 = si
for si, sh in enumerate(SHOTS):
    md = sh.get("mood", "none"); prev = SHOTS[si - 1].get("mood", "none") if si else "none"
    if md in ("anger", "fear") and prev not in ("anger", "fear"):
        aud.append(f'<audio id="dr{si}" src="assets/sfx_drum.wav" data-start="{starts[si]:.3f}" data-duration="2.18" data-volume="0.75"></audio>')
    if md == "wonder" and prev != "wonder":
        aud.append(f'<audio id="sh{si}" src="assets/sfx_shimmer.wav" data-start="{starts[si] + 0.05:.3f}" data-duration="1.1" data-volume="0.5"></audio>')
aud += fx_aud
aud.append(f'<audio id="sp-q" src="assets/sfx_spark.wav" data-start="{T[LAST]:.3f}" data-duration="0.53" data-volume="0.6"></audio>')
aud += [f'<audio id="v-{k}" src="assets/{k}.wav" data-start="{T[k]:.3f}" data-duration="{D[k]:.3f}"></audio>' for k in ORDER]
aud.append(f'<audio id="a-click" src="assets/sfx_click.wav" data-start="{T_FING + 0.35:.3f}" data-duration="0.08"></audio>')
aud.append(f'<audio id="a-ting" src="assets/sfx_ting.wav" data-start="{T_BELL + 0.35:.3f}" data-duration="1.4"></audio>')

# ---------- page ----------
Q = EPI["QUESTION"].rstrip("?？ ")
QFS = min(62, int(960 / (0.56 * max(1, len(Q) + 1))))
nm = "node_modules"
CSS = """
@font-face{font-family:Mukta;font-weight:800;src:url(%(nm)s/@fontsource/mukta/files/mukta-devanagari-800-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mukta,sans-serif}
#win{position:absolute;left:36px;top:226px;width:1008px;height:1228px;overflow:hidden;background:#2a1a10}
#cam{position:absolute;left:0;top:0;width:1360px;height:1660px;transform-origin:0 0}
.wfull{position:absolute;left:0;top:0;width:1360px;height:1660px}
.lay{position:absolute;left:0;top:0;width:1360px;height:1660px}
.char{position:absolute}
.char .ci{position:absolute;left:0;top:0}
#frame{position:absolute;left:0;top:0;width:1080px;height:1920px}
#t1{position:absolute;top:58px;left:0;right:0;text-align:center;color:#ffd65a;font-size:40px;font-weight:800;line-height:1}
#t2{position:absolute;top:110px;left:0;right:0;text-align:center;color:#fff;font-size:%(qfs)spx;font-weight:800;line-height:1;white-space:nowrap}
#t2 b{display:inline-block;color:#ffcf3a;text-shadow:0 0 24px #ff9a00,0 0 50px #ff6a00}
#logo{position:absolute;right:56px;top:246px;width:104px;height:104px;border-radius:50%%}
"""
doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{CSS % {"nm": nm, "qfs": QFS}}
#birds{{position:absolute;left:-320px;top:250px;width:300px;height:120px;opacity:0}}
#tint{{position:absolute;left:0;top:0;width:1008px;height:1228px;pointer-events:none}}
.chip{{position:absolute;left:70px;top:262px;background:#1a0a06;border:5px solid #ffcf3a;border-radius:30px;color:#fff;font-size:46px;font-weight:800;padding:4px 30px;box-shadow:0 0 30px #ff7a00;opacity:0}}
#qbox{{position:absolute;left:{680 - 200}px;top:{555 - 240}px;width:400px;height:480px;opacity:0}}
#qbox img{{position:absolute;left:0;top:0;width:400px;height:480px}}
#qbox div{{position:absolute;left:0;right:0;top:40px;text-align:center;color:#ffcf3a;font-size:350px;font-weight:800;line-height:1;text-shadow:0 0 40px #ff9a00,0 0 90px #ff5a00,0 6px 0 #6a2a00}}
.sline{{position:absolute;left:0;top:0;width:1080px;height:1920px;opacity:0}}
.name{{position:absolute;top:1500px;left:0;right:0;text-align:center;color:#f0be3c;font-size:44px;font-weight:800;line-height:1}}
.chunk{{position:absolute;left:70px;right:70px;top:1566px;text-align:center;color:#fff;font-size:64px;font-weight:800;line-height:1.28;opacity:0}}
.w{{display:inline-block;opacity:.32}}
.w.key{{color:#ffd23a;text-shadow:0 0 14px #ff9a00}}
#sub{{position:absolute;left:150px;top:1462px;width:780px;height:100px;background:rgba(18,18,22,.93);border:2px solid rgba(255,255,255,.2);border-radius:52px;box-shadow:0 8px 24px rgba(0,0,0,.6);opacity:0}}
#sub img.l{{position:absolute;left:12px;top:12px;width:76px;height:76px;border-radius:50%}}
#sub .ch{{position:absolute;left:102px;top:16px;color:#fff;font-size:34px;font-weight:800;line-height:1}}
#sub .hd{{position:absolute;left:102px;top:58px;color:#aaa;font-size:24px;font-weight:800;line-height:1}}
#btn,#btn2{{position:absolute;left:432px;top:18px;width:236px;height:64px;border-radius:34px;font-weight:800;line-height:64px;text-align:center}}
#btn{{background:#e62117;color:#fff;font-size:30px}}
#btn2{{background:#3a3a40;color:#ddd;font-size:26px;opacity:0}}
#bell{{position:absolute;left:684px;top:18px;width:64px;height:64px;border-radius:50%;background:#3a3a40}}
#bell svg{{position:absolute;left:13px;top:12px;width:38px;height:40px}}
#finger{{position:absolute;left:669px;top:1511px;width:70px;height:100px;opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="root" data-width="1080" data-height="1920" data-start="0" data-duration="{END}">
 <div id="win"><div id="cam">
  {''.join(layers)}
  <img id="birds" src="assets/birds.png">
  <div class="lay" id="qbox"><img src="assets/q_glow.png"><div>?</div></div>
 </div><div id="tint"></div></div>
 <img id="frame" src="assets/frame_b3.png">
 <div id="t1">{html.escape(EPI.get("SERIES", "रामायण"))} · {EPI.get("PART_WORD", "भाग")} {EPI["BHAG"]}</div>
 <div id="t2">{html.escape(Q)}<b>?</b></div>
 <img id="logo" src="assets/katha_chitra_logo.png">
 {''.join(chip_html)}
 {''.join(sub_html)}
 <div id="sub"><img class="l" src="assets/katha_chitra_logo.png"><div class="ch">Katha Chitra</div><div class="hd">@kathachitra_123</div>
  <div id="btn">SUBSCRIBE</div><div id="btn2">✓ SUBSCRIBED</div>
  <div id="bell"><svg viewBox="0 0 24 24"><path id="bellp" fill="#fff" d="M12 22a2.5 2.5 0 0 0 2.4-2h-4.8A2.5 2.5 0 0 0 12 22zm7-6V11a7 7 0 0 0-5.5-6.8V3.5a1.5 1.5 0 0 0-3 0v.7A7 7 0 0 0 5 11v5l-2 2v1h18v-1z"/></svg></div>
 </div>
 <img id="finger" src="assets/finger.png">
 {''.join(aud)}
</div>
<script src="{nm}/gsap/dist/gsap.min.js"></script>
<script>
const tl = gsap.timeline({{paused:true}});
{''.join(cam_js)}
{''.join(shot_js)}
{''.join(moves)}
{''.join(fx_js)}
// question over the last scene
tl.fromTo("#qbox",{{opacity:0,scale:0.3}},{{opacity:1,scale:1,duration:0.5,ease:"back.out(1.8)",immediateRender:false}},{T[LAST]:.3f});
tl.to("#qbox",{{scale:1.07,duration:0.5,yoyo:true,repeat:{max(1, int((END - T[LAST] - 0.5) / 0.5))},ease:"sine.inOut"}},{T[LAST] + 0.5:.3f});
tl.fromTo("#t2 b",{{scale:1}},{{scale:1.15,duration:0.5,yoyo:true,repeat:{int(END / 0.5) - 1},ease:"sine.inOut"}},0);
{''.join(sub_js)}
// subscribe widget slides in during the last line
tl.fromTo("#sub",{{opacity:0,y:50}},{{opacity:1,y:0,duration:0.4,ease:"power2.out",immediateRender:false}},{T_SUBIN:.3f});
tl.fromTo("#finger",{{opacity:0,x:120,y:70}},{{opacity:1,x:0,y:0,duration:0.35,ease:"power2.out",immediateRender:false}},{T_FING:.3f});
tl.to("#finger",{{scale:0.88,duration:0.08,yoyo:true,repeat:1}},{T_FING + 0.35:.3f});
tl.to("#btn",{{scale:0.92,duration:0.08,yoyo:true,repeat:1}},{T_FING + 0.35:.3f});
tl.to("#btn2",{{opacity:1,duration:0.12}},{T_FING + 0.45:.3f});
tl.to("#finger",{{x:166,duration:0.35,ease:"power2.inOut"}},{T_BELL:.3f});
tl.to("#finger",{{scale:0.88,duration:0.08,yoyo:true,repeat:1}},{T_BELL + 0.35:.3f});
tl.to("#bellp",{{fill:"#ffd23a",duration:0.1}},{T_BELL + 0.4:.3f});
tl.to("#bell",{{boxShadow:"0 0 30px #ffb000",duration:0.15}},{T_BELL + 0.4:.3f});
tl.fromTo("#bell",{{rotation:0}},{{rotation:16,duration:0.08,yoyo:true,repeat:9,ease:"sine.inOut",immediateRender:false}},{T_BELL + 0.4:.3f});
tl.to("#finger",{{opacity:0,y:-60,duration:0.3}},{T_BELL + 0.9:.3f});
{''.join(sets)}
tl.set({{}},{{}},{END});
window.__timelines = window.__timelines || {{}};
window.__timelines["root"] = tl;
</script>
</body></html>"""
open(f"{P}/index.html", "w").write(doc)

# ---------- cover (own small composition) ----------
cv = EPI["COVER"]; cimgs = []
ccast = cv["cast"][:2]
for i, e in enumerate(ccast):
    base, _ = SP.state_base(e, {"line": "_cover", "cast": ccast}, EPI)
    left = [-170, 420][i] if len(ccast) == 2 else 124
    cimgs.append(f'<img src="assets/{base}.png" style="position:absolute;left:{left}px;top:330px;width:760px;height:1031px">')
cov = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS % {"nm": "fonts", "qfs": QFS}}
#q{{position:absolute;left:0;right:0;top:300px;margin:auto;width:max-content;color:#fff8e0;font-size:360px;font-weight:800;line-height:1;-webkit-text-stroke:12px #4a1200;paint-order:stroke fill;text-shadow:0 0 40px #ff9a00,0 0 90px #ff5a00,0 10px 0 #3a0e00}}
#tag{{position:absolute;top:1490px;left:0;right:0;text-align:center;color:#ffd23a;font-size:84px;font-weight:800;line-height:1.1;text-shadow:0 4px 0 #4a1a00}}
#tag2{{position:absolute;top:1610px;left:0;right:0;text-align:center;color:#fff;font-size:52px;font-weight:800}}
</style></head><body>
<div id="root" data-composition-id="cover" data-width="1080" data-height="1920" data-start="0" data-duration="1">
 <div id="win">
  <img src="assets/bg_{cv["bg"]}.png" style="position:absolute;left:-200px;top:-200px;width:1360px;height:1660px">
  {''.join(cimgs)}
 </div>
 <img id="frame" src="assets/frame_b3.png">
 <div id="t1">{html.escape(EPI.get("SERIES", "रामायण"))} · {EPI.get("PART_WORD", "भाग")} {EPI["BHAG"]}</div>
 <div id="t2">{html.escape(Q)}<b>?</b></div>
 <div id="q">?</div>
 <img id="logo" src="assets/katha_chitra_logo.png">
 <div id="tag">{html.escape(cv.get("tag", ""))}</div>
 <div id="tag2">{html.escape(EPI.get("TAG", "वाल्मीकि रामायण"))}</div>
</div>
<script src="fonts/gsap/dist/gsap.min.js"></script>
<script>const tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},1);window.__timelines={{cover:tl}};</script>
</body></html>"""
os.makedirs(f"{P}/cover", exist_ok=True)
open(f"{P}/cover/index.html", "w").write(cov)
print("END", END, "shots", [round(s, 2) for s in starts])
