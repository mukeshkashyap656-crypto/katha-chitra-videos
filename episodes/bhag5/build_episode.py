"""Bhag 5 — Ram ko mile Divya Astra. HyperFrames composition in the Bhag 3 look (9 shots, plan in plans/bhag5_PLAN.md).
Run: EP=/tmp/ep python3 build_episode.py  -> proj/index.html and proj/cover/index.html
"""
import json, html, os, re
P = os.environ.get("EP", "/home/claude/ep") + "/proj"
lip = json.load(open(f"{P}/lip.json"))
FPS = 30

# ---------- words: display tokens with exact spoken times ----------
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

ORDER = ["n1", "n2", "vm", "n3", "dev", "ram1", "ram2", "ram3", "n4"]
D = {k: lip[k]["dur"] for k in ORDER}
T = {}
T["n1"] = 0.35
T["n2"] = T["n1"] + D["n1"] + 0.35
T["vm"] = T["n2"] + D["n2"] + 0.3
T["n3"] = T["vm"] + D["vm"] + 0.55
T["dev"] = T["n3"] + D["n3"] + 0.8
T["ram1"] = T["dev"] + D["dev"] + 0.65
ORB0 = T["ram1"] + D["ram1"] + 0.05; ORB_END = ORB0 + 1.1
T["ram2"] = ORB_END + 0.65
S8 = T["ram2"] + D["ram2"] + 0.35; WALK_D = 1.5
T["ram3"] = S8 + WALK_D + 0.25
T["n4"] = T["ram3"] + D["ram3"] + 0.4
E = {k: T[k] + D[k] for k in ORDER}
WT = {k: [(w, T[k] + o) for w, o in align(k)] for k in ORDER}
def wt(k, sub):
    for w, t in WT[k]:
        if sub in w: return t
    raise KeyError(f"{sub} not in {k}")

S2 = T["n2"] - 0.15
T_SMILE = wt("n2", "मुस्कुराए")
T_NM = wt("vm", "आज")
S4 = E["vm"] + 0.05
ICONS = [("दंड", "ic_chakra"), ("धर्म", "ic_chakra2"), ("काल", "ic_chakra3"), ("विष्णु", "ic_chakra4"), ("वज्र", "ic_vajra"), ("त्रिशूल", "ic_trishul")]
ICON_T = [wt("n3", s) for s, _ in ICONS]
T_BRAHMA = wt("n3", "ब्रह्मास्त्र")
S5 = T["dev"] - 0.75
S6 = T["ram1"] - 0.5
S7 = T["ram2"] - 0.6
T_BADAL = wt("ram3", "बादलों")
T_Q = T["n4"]
T_SUBIN = wt("n4", "कमेंट")
T_FING = WT["n4"][-1][1] - 0.15
T_BELL = T_FING + 0.8
END = round(max(T_BELL + 0.35 + 1.4 + 0.4, E["n4"] + 0.3), 2)

# ---------- character states ----------
def blink(t, off): return (t + off) % 3.4 < 0.12
def mouth(key, t):
    sh = lip[key]["shapes"]; k = int((t - T[key]) * FPS)
    return sh[k] if 0 <= k < len(sh) else "X"
def speaking(key, t): return T[key] <= t < E[key]
def walkf(pre, t): return f"{pre}_walk{int((t - S8) / 0.13) % 4}"
def ram_state(t):
    if t < T_NM: return "ram_n_blink" if blink(t, 0.4) else "ram_n"
    if t < T_NM + 0.3: return f"ram_nm{int((t - T_NM) / 0.1) + 1}"
    if t < S6: return "ram_nm_blink" if blink(t, 0.4) else "ram_nm"
    if t < S6 + 0.48: return f"ram_tch{min(4, int((t - S6) / 0.12) + 1)}"
    if t < S7:
        if speaking("ram1", t): return f"ram_tch_{mouth('ram1', t)}"
        return "ram_tch_blink" if blink(t, 0.4) else "ram_tch_X"
    if t < S7 + 0.15: return "ram_front"
    if t < S7 + 0.45: return f"ram_turn{int((t - S7 - 0.15) / 0.1) + 1}"
    if t < S8:
        if speaking("ram2", t): return f"ram_talk_{mouth('ram2', t)}"
        return "ram_talk_blink" if blink(t, 0.4) and t > E["ram2"] + 0.2 else "ram_talk_X"
    if t < S8 + WALK_D: return walkf("ram", t)
    if speaking("ram3", t): return f"ram_talk_{mouth('ram3', t)}"
    return "ram_talk_blink" if blink(t, 0.4) else "ram_talk_X"
def lak_state(t):
    if t < T_NM + 0.1: return "lak_n_blink" if blink(t, 1.5) else "lak_n"
    if t < T_NM + 0.4: return f"lak_nm{int((t - T_NM - 0.1) / 0.1) + 1}"
    if t < S8: return "lak_nm_blink" if blink(t, 1.5) else "lak_nm"
    if t < S8 + WALK_D: return walkf("lak", t)
    return "lak_n_blink" if blink(t, 1.5) else "lak_n"
def vm_state(t):
    if t < T_SMILE: return "vm_stand_blink" if blink(t, 2.4) else "vm_stand"
    if t < T["vm"] - 0.35: return "vm_smile_blink" if blink(t, 2.4) else "vm_smile"
    if t < T["vm"] - 0.05: return f"vm_up{int((t - T['vm'] + 0.35) / 0.1) + 1}"
    if t < E["vm"] + 0.1:
        if speaking("vm", t): return f"vm_talk_{mouth('vm', t)}"
        return "vm_talk_X"
    if t < E["vm"] + 0.4: return f"vm_g{int((t - E['vm'] - 0.1) / 0.1) + 1}"
    if t < S8: return "vm_give_blink" if blink(t, 2.4) else "vm_give"
    if t < S8 + WALK_D: return walkf("vm", t)
    return "vm_stand_blink" if blink(t, 2.4) else "vm_stand"
def dev_state(pre, off):
    def f(t):
        if speaking("dev", t): return f"{pre}_{mouth('dev', t)}"
        return f"{pre}_blink" if blink(t, off) else f"{pre}_X"
    return f

W4 = [f"_walk{i}" for i in range(4)]; MS = "XABEOM"
FEET = 1480; DW, DH = 689, 935
CHARS = {
    "lak": (320, lak_state, [f"lak{w}" for w in W4] + ["lak_n", "lak_n_blink", "lak_nm1", "lak_nm2", "lak_nm3", "lak_nm", "lak_nm_blink"]),
    "ram": (650, ram_state, [f"ram{w}" for w in W4] + ["ram_n", "ram_n_blink", "ram_nm1", "ram_nm2", "ram_nm3", "ram_nm", "ram_nm_blink"]
            + [f"ram_tch{i}" for i in range(1, 5)] + [f"ram_tch_{m}" for m in MS] + ["ram_tch_blink", "ram_front", "ram_front_blink"]
            + [f"ram_turn{i}" for i in range(1, 4)] + [f"ram_talk_{m}" for m in MS] + ["ram_talk_blink"]),
    "vm": (1100, vm_state, [f"vm{w}" for w in W4] + ["vm_stand", "vm_stand_blink", "vm_smile", "vm_smile_blink"] + [f"vm_up{i}" for i in range(1, 4)]
           + [f"vm_talk_{m}" for m in MS] + ["vm_talk_blink"] + [f"vm_g{i}" for i in range(1, 4)] + ["vm_give", "vm_give_blink"]),
}
DDW, DDH = 837, 1107; DFEET = 1500
DEVS = {"dc": (300, dev_state("dev_coal", 0.7), "dev_coal"), "ds": (680, dev_state("dev_sun", 1.9), "dev_sun"), "dm": (1060, dev_state("dev_smoke", 2.8), "dev_smoke")}
sets = []; layers = []; dlayers = []
def track(cid, fn, keys, layer, left, top, cls):
    imgs = "".join(f'<img id="{cid}-{k}" class="ci" src="assets/{k}.png" style="opacity:{1 if k == fn(0) else 0}">' for k in keys)
    layer.append(f'<div class="{cls}" id="{cid}" style="left:{left:.0f}px;top:{top:.0f}px">{imgs}</div>')
    prev = fn(0)
    for f in range(1, int(END * FPS) + 1):
        t = f / FPS; s = fn(t)
        assert s in keys, (cid, s)
        if s != prev:
            sets.append(f'tl.set("#{cid}-{prev}",{{opacity:0}},{t:.3f});tl.set("#{cid}-{s}",{{opacity:1}},{t:.3f});'); prev = s
for cid, (cx, fn, keys) in CHARS.items(): track(cid, fn, keys, layers, cx - DW / 2, FEET + 37 - DH, "char")
for cid, (cx, fn, pre) in DEVS.items():
    track(cid, fn, [f"{pre}_{m}" for m in MS] + [f"{pre}_blink"], dlayers, cx - DDW / 2, DFEET + 37 * DDH / DH - DDH, "dev")

# ---------- subtitles: line container (speaker name) + chunks with karaoke words ----------
NAMES = {"vm": "महर्षि विश्वामित्र", "dev": "दिव्य अस्त्रों के देवता", "ram1": "श्रीराम", "ram2": "श्रीराम", "ram3": "श्रीराम"}
KEYS = {"देवताओं", "एक", "सुबह", "मुस्कुराए", "दिव्य", "अस्त्र", "चक्र", "वज्र", "त्रिशूल", "ब्रह्मास्त्र", "सेवक", "याद", "वापस", "बादलों", "भगवान", "जय", "श्री", "राम"}
NOKEY = {"ram1", "ram2", "vm"}   # only highlight a few words per line
LINEKEYS = {"n1": {"देवताओं", "सुबह"}, "n2": {"मुस्कुराए"}, "vm": {"दिव्य", "अस्त्र"}, "n3": {"चक्र", "वज्र", "त्रिशूल", "ब्रह्मास्त्र"},
            "dev": {"सेवक"}, "ram1": {"याद"}, "ram2": {"वापस"}, "ram3": {"बादलों"}, "n4": {"भगवान", "जय", "श्री", "राम"}}
def chunks(k):
    out, cur, ln = [], [], 0
    for i, (w, t) in enumerate(WT[k]):
        cur.append(i); ln += len(w) + 1
        if ln > 30 or w.endswith(("।", "!", "?", "...", ",")) and ln > 12:
            out.append(cur); cur, ln = [], 0
    if cur:
        if out and sum(len(WT[k][i][0]) + 1 for i in cur) < 9: out[-1] += cur
        else: out.append(cur)
    return out
# old line fully gone before the next one shows (next line shows at T - 0.2)
LINE_OFF = {k: (min(E[k] + 0.25, T[ORDER[i + 1]] - 0.36) if i + 1 < len(ORDER) else E[k] + 0.25) for i, k in enumerate(ORDER)}
sub_html = []; sub_js = []
for k in ORDER:
    cs = chunks(k); body = []
    for ci, idx in enumerate(cs):
        spans = "".join(f'<span id="w{k}{i}" class="w{" key" if norm(WT[k][i][0]).rstrip("ा") in LINEKEYS[k] or norm(WT[k][i][0]) in LINEKEYS[k] or any(norm(WT[k][i][0]).startswith(x) for x in LINEKEYS[k]) else ""}">{html.escape(WT[k][i][0])}</span> ' for i in idx)
        body.append(f'<div class="chunk" id="c{k}{ci}">{spans}</div>')
        t_on = T[k] - 0.18 if ci == 0 else WT[k][idx[0]][1] - 0.08
        t_off = (WT[k][cs[ci + 1][0]][1] - 0.16) if ci + 1 < len(cs) else LINE_OFF[k]
        sub_js.append(f'tl.to("#c{k}{ci}",{{opacity:1,duration:0.08}},{t_on:.3f});tl.to("#c{k}{ci}",{{opacity:0,duration:0.07}},{t_off:.3f});')
    nm = f'<div class="name">{NAMES[k]}</div>' if k in NAMES else ""
    sub_html.append(f'<div class="sline" id="L{k}">{nm}{"".join(body)}</div>')
    sub_js.append(f'tl.set("#L{k}",{{opacity:1}},{T[k] - 0.2:.3f});tl.set("#L{k}",{{opacity:0}},{LINE_OFF[k] + 0.08:.3f});')
    for i, (w, t) in enumerate(WT[k]): sub_js.append(f'tl.to("#w{k}{i}",{{opacity:1,duration:0.08}},{t:.3f});')

# ---------- camera: world 1360x1660 in a 1008x1228 window ----------
WW, WH, VW, VH = 1360, 1660, 1008, 1228; S0 = VW / WW
def cam(px, py, z):
    s = S0 * z; x = VW / 2 - s * px; y = VH / 2 - s * py
    x = min(0, max(VW - WW * s, x)); y = min(0, max(VH - WH * s, y))
    return f"x:{x:.1f},y:{y:.1f},scale:{s:.4f}"
SHOTS = [  # (start, from, to)
    (0, cam(680, 760, 1.0), cam(680, 760, 1.12)),                 # 1 golden chakras
    (S2, cam(680, 830, 1.0), cam(700, 900, 1.1)),                # 2 calm morning, all three
    (T_SMILE - 0.05, cam(1085, 958, 3.4), cam(1085, 955, 3.5)),  # 2b Vishwamitra smiles (close-up)
    (T_NM - 0.05, cam(700, 1030, 1.15), cam(700, 1030, 1.2)),     # 3 guru gives, Ram & Lakshman pranam
    (S4, cam(710, 1000, 1.2), cam(710, 990, 1.25)),                # 4 astras appear in the sky
    (S5, cam(680, 900, 1.0), cam(680, 900, 1.07)),                # 5 the astra devtas
    (S6, cam(560, 1140, 1.7), cam(560, 1140, 1.76)),              # 6 Ram touches, devtas merge into him
    (S7, cam(690, 1010, 3.0), cam(690, 1010, 3.12)),              # 7 Ram close-up, turns to guru
    (S8, cam(680, 830, 1.0), cam(680, 830, 1.0)),                 # 8 walking, cloud-like forest
    (T["ram3"] - 0.1, cam(880, 1140, 1.7), cam(880, 1140, 1.75)), # 8b Ram asks Vishwamitra
    (T_BADAL - 0.05, cam(710, 1000, 1.15), cam(710, 1000, 1.15)),     # 9 the forest + question
]
cam_js = []
for i, (t0, a, b) in enumerate(SHOTS):
    t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else END
    cam_js.append(f'tl.set("#cam",{{{a}}},{t0:.3f});tl.to("#cam",{{{b},duration:{max(0.1, t1 - t0 - 0.02):.3f},ease:"none"}},{t0:.3f});')

ICON_POS = [(200, 630), (370, 570), (555, 535), (805, 535), (990, 570), (1130, 650)]
icon_html = "".join(f'<img id="ic{i}" class="icon" src="assets/{f}.png" style="left:{x - 95}px;top:{y - 95}px">' for i, ((_, f), (x, y)) in enumerate(zip(ICONS, ICON_POS)))
icon_js = []
for i, t in enumerate(ICON_T):
    icon_js.append(f'tl.fromTo("#ic{i}",{{opacity:0,scale:0.2,rotation:-90}},{{opacity:1,scale:1,rotation:0,duration:0.35,ease:"back.out(2)",immediateRender:false}},{t:.3f});')
    icon_js.append(f'tl.set("#cnt",{{innerText:"{i + 1}"}},{t + 0.05:.3f});')
    if "chakra" in ICONS[i][1]:
        icon_js.append(f'tl.to("#ic{i}",{{rotation:360,duration:2.2,repeat:{int((T_BRAHMA - t) / 2.2) + 1},ease:"none"}},{t + 0.35:.3f});')
for j, n in enumerate((7, 8, 9)):
    icon_js.append(f'tl.set("#cnt",{{innerText:"{n}"}},{ICON_T[-1] + 0.25 + j * 0.12 + (T_BRAHMA - ICON_T[-1] - 0.7) * j / 3:.3f});')
icon_js.append(f'tl.set("#cnt",{{innerText:"10+"}},{T_BRAHMA + 0.05:.3f});')
icon_js.append(f'tl.to(".icon",{{opacity:0,scale:0.6,duration:0.3}},{T_BRAHMA:.3f});')
icon_js.append(f'tl.fromTo("#brahma",{{opacity:0,scale:0.2}},{{opacity:1,scale:1,duration:0.5,ease:"back.out(1.6)",immediateRender:false}},{T_BRAHMA:.3f});')
icon_js.append(f'tl.to("#brahma",{{scale:1.08,duration:0.45,yoyo:true,repeat:{max(1, int((S5 - T_BRAHMA - 0.5) / 0.45))},ease:"sine.inOut"}},{T_BRAHMA + 0.5:.3f});')
icon_js.append(f'tl.fromTo("#flash",{{opacity:0}},{{opacity:0.55,duration:0.08,yoyo:true,repeat:1,immediateRender:false}},{T_BRAHMA:.3f});')

CHEST = (650, 1045)
orb_html = "".join(f'<img id="o{i}" class="orb" src="assets/orb_{n}.png">' for i, n in enumerate(("coal", "smoke", "sun")))
orb_js = []
for i in range(3):
    t0 = ORB0 + i * 0.18; sy = 760 + i * 120
    orb_js.append(f'tl.fromTo("#o{i}",{{x:{1010 - 70},y:{sy - 70},opacity:0,scale:1}},{{opacity:1,duration:0.1,immediateRender:false}},{t0:.3f});')
    orb_js.append(f'tl.to("#o{i}",{{x:{CHEST[0] - 70},y:{CHEST[1] - 70},scale:0.35,duration:0.6,ease:"power2.in"}},{t0:.3f});')
    orb_js.append(f'tl.to("#o{i}",{{opacity:0,duration:0.08}},{t0 + 0.6:.3f});')
orb_js.append(f'tl.fromTo("#chest",{{opacity:0,scale:0.4}},{{opacity:1,scale:1.15,duration:0.25,immediateRender:false}},{ORB0 + 0.95:.3f});')
orb_js.append(f'tl.to("#chest",{{opacity:0,scale:0.8,duration:0.5}},{ORB0 + 1.25:.3f});')

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
.char{position:absolute;width:689px;height:935px}
.char .ci{position:absolute;left:0;top:0;width:689px;height:935px}
.dev{position:absolute;width:837px;height:1107px}
.dev .ci{position:absolute;left:0;top:0;width:837px;height:1107px}
#frame{position:absolute;left:0;top:0;width:1080px;height:1920px}
#t1{position:absolute;top:58px;left:0;right:0;text-align:center;color:#ffd65a;font-size:40px;font-weight:800;line-height:1}
#t2{position:absolute;top:110px;left:0;right:0;text-align:center;color:#fff;font-size:62px;font-weight:800;line-height:1;white-space:nowrap}
#t2 b{display:inline-block;color:#ffcf3a;text-shadow:0 0 24px #ff9a00,0 0 50px #ff6a00}
#logo{position:absolute;right:56px;top:246px;width:104px;height:104px;border-radius:50%%}
"""
doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{CSS % {"nm": nm}}
#birds{{position:absolute;left:-320px;top:250px;width:300px;height:120px}}
#birds2{{position:absolute;left:-320px;top:420px;width:240px;height:96px}}
.chak{{position:absolute}}
.icon{{position:absolute;width:190px;height:190px;opacity:0}}
#brahma{{position:absolute;left:{690 - 170}px;top:{600 - 170}px;width:340px;height:340px;opacity:0}}
.orb{{position:absolute;left:0;top:0;width:140px;height:140px;opacity:0}}
#chest{{position:absolute;left:{CHEST[0] - 130}px;top:{CHEST[1] - 130}px;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(255,250,210,.95),rgba(255,200,60,.55) 40%,rgba(255,160,0,0) 70%);opacity:0}}
#qbox{{position:absolute;left:{700 - 200}px;top:{555 - 240}px;width:400px;height:480px;opacity:0}}
#qbox img{{position:absolute;left:0;top:0;width:400px;height:480px}}
#qbox div{{position:absolute;left:0;right:0;top:40px;text-align:center;color:#ffcf3a;font-size:350px;font-weight:800;line-height:1;text-shadow:0 0 40px #ff9a00,0 0 90px #ff5a00,0 6px 0 #6a2a00}}
#flash{{position:absolute;left:0;top:0;width:1008px;height:1228px;background:#fff6d0;opacity:0}}
#counter{{position:absolute;left:66px;top:262px;width:330px;background:#1a0a06;border:5px solid #ffcf3a;border-radius:30px;color:#fff;font-size:50px;font-weight:800;padding:6px 0;text-align:center;box-shadow:0 0 30px #ff7a00;opacity:0}}
#counter b{{color:#ffcf3a}}
.sline{{position:absolute;left:0;top:0;width:1080px;height:1920px;opacity:0}}
.name{{position:absolute;top:1500px;left:0;right:0;text-align:center;color:#f0be3c;font-size:44px;font-weight:800;line-height:1}}
.chunk{{position:absolute;left:70px;right:70px;top:1566px;text-align:center;color:#fff;font-size:64px;font-weight:800;line-height:1.28;opacity:0}}
.w{{display:inline-block;opacity:.32}}
.w.key{{color:#ffd23a;text-shadow:0 0 14px #ff9a00}}
#sub{{position:absolute;left:150px;top:1330px;width:780px;height:100px;background:rgba(18,18,22,.93);border:2px solid rgba(255,255,255,.2);border-radius:52px;box-shadow:0 8px 24px rgba(0,0,0,.6);opacity:0}}
#sub img.l{{position:absolute;left:12px;top:12px;width:76px;height:76px;border-radius:50%}}
#sub .ch{{position:absolute;left:102px;top:16px;color:#fff;font-size:34px;font-weight:800;line-height:1}}
#sub .hd{{position:absolute;left:102px;top:58px;color:#aaa;font-size:24px;font-weight:800;line-height:1}}
#btn,#btn2{{position:absolute;left:432px;top:18px;width:236px;height:64px;border-radius:34px;font-weight:800;line-height:64px;text-align:center}}
#btn{{background:#e62117;color:#fff;font-size:30px}}
#btn2{{background:#3a3a40;color:#ddd;font-size:26px;opacity:0}}
#bell{{position:absolute;left:684px;top:18px;width:64px;height:64px;border-radius:50%;background:#3a3a40}}
#bell svg{{position:absolute;left:13px;top:12px;width:38px;height:40px}}
#finger{{position:absolute;left:669px;top:1379px;width:70px;height:100px;opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="root" data-width="1080" data-height="1920" data-start="0" data-duration="{END}">
 <div id="win"><div id="cam">
  <img class="wfull" id="bgm" src="assets/bg_morning.png">
  <img class="wfull" id="bgc" src="assets/bg_cloudvan.png" style="opacity:0">
  <img id="birds" src="assets/birds.png"><img id="birds2" src="assets/birds.png">
  <div class="lay" id="qbox"><img src="assets/q_glow.png"><div>?</div></div>
  <div class="lay" id="chars">{''.join(layers)}</div>
  <div class="lay" id="icons">{icon_html}<img id="brahma" src="assets/ic_brahma.png"></div>
  <div class="lay" id="orbs">{orb_html}<div id="chest"></div></div>
  <div class="lay" id="divine">
   <img class="wfull" src="assets/bg_divine.png">
   <div class="lay" id="chaks">
    <img class="chak" id="ch1" src="assets/ic_chakra4.png" style="left:{680 - 300}px;top:{700 - 300}px;width:600px;height:600px">
    <img class="chak" id="ch2" src="assets/ic_chakra.png" style="left:{250 - 150}px;top:{1130 - 150}px;width:300px;height:300px">
    <img class="chak" id="ch3" src="assets/ic_chakra2.png" style="left:{1110 - 150}px;top:{1130 - 150}px;width:300px;height:300px">
    <img class="chak" id="ch4" src="assets/ic_chakra3.png" style="left:{240 - 110}px;top:{330 - 110}px;width:220px;height:220px">
   </div>
   <div class="lay" id="devs" style="opacity:0">{''.join(dlayers)}</div>
  </div>
 </div><div id="flash"></div></div>
 <img id="frame" src="assets/frame_b3.png">
 <div id="t1">रामायण · भाग 5</div>
 <div id="t2">राम को कौन-से दिव्य अस्त्र मिले<b>?</b></div>
 <img id="logo" src="assets/katha_chitra_logo.png">
 <div id="counter">अस्त्र: <b id="cnt">0</b></div>
 {''.join(sub_html)}
 <div id="sub"><img class="l" src="assets/katha_chitra_logo.png"><div class="ch">Katha Chitra</div><div class="hd">@kathachitra_123</div>
  <div id="btn">SUBSCRIBE</div><div id="btn2">✓ SUBSCRIBED</div>
  <div id="bell"><svg viewBox="0 0 24 24"><path id="bellp" fill="#fff" d="M12 22a2.5 2.5 0 0 0 2.4-2h-4.8A2.5 2.5 0 0 0 12 22zm7-6V11a7 7 0 0 0-5.5-6.8V3.5a1.5 1.5 0 0 0-3 0v.7A7 7 0 0 0 5 11v5l-2 2v1h18v-1z"/></svg></div>
 </div>
 <img id="finger" src="assets/finger.png">
 <audio id="a-pad1" src="assets/sfx_pad.wav" data-start="0" data-duration="{S2:.3f}" data-volume="0.6" data-fade-out="0.4"></audio>
 <audio id="a-morn1" src="assets/sfx_morning.wav" data-start="{S2:.3f}" data-duration="{S5 - S2:.3f}" data-volume="0.7"></audio>
 <audio id="a-pad2" src="assets/sfx_pad.wav" data-start="{S5:.3f}" data-duration="{S6 - S5:.3f}" data-volume="0.6" data-fade-out="0.3"></audio>
 <audio id="a-morn2" src="assets/sfx_morning.wav" data-start="{S6:.3f}" data-duration="{END - S6:.3f}" data-volume="0.7" data-fade-out="0.8"></audio>
 <audio id="a-sh1" src="assets/sfx_shimmer.wav" data-start="0.05" data-duration="1.1" data-volume="0.5"></audio>
 <audio id="a-wh1" src="assets/sfx_whoosh_soft.wav" data-start="{S2 - 0.45:.3f}" data-duration="1.05" data-volume="0.5"></audio>
 {''.join(f'<audio id="a-sp{i}" src="assets/sfx_spark.wav" data-start="{t:.3f}" data-duration="0.53" data-volume="0.55"></audio>' for i, t in enumerate(ICON_T))}
 <audio id="a-drum" src="assets/sfx_drum.wav" data-start="{T_BRAHMA:.3f}" data-duration="2.18" data-volume="0.75"></audio>
 <audio id="a-shl" src="assets/sfx_shimmer_long.wav" data-start="{T_BRAHMA + 0.05:.3f}" data-duration="2.07" data-volume="0.5"></audio>
 <audio id="a-app" src="assets/sfx_appear.wav" data-start="{S5:.3f}" data-duration="1.21" data-volume="0.6"></audio>
 <audio id="a-wh2" src="assets/sfx_whoosh.wav" data-start="{S6 - 0.2:.3f}" data-duration="0.52" data-volume="0.45"></audio>
 <audio id="a-sh2" src="assets/sfx_shimmer.wav" data-start="{ORB0 + 0.6:.3f}" data-duration="1.1" data-volume="0.6"></audio>
 <audio id="a-wh3" src="assets/sfx_whoosh_soft.wav" data-start="{S8 - 0.45:.3f}" data-duration="1.05" data-volume="0.5"></audio>
 <audio id="a-sp9" src="assets/sfx_spark.wav" data-start="{T_Q:.3f}" data-duration="0.53" data-volume="0.6"></audio>
 {''.join(f'<audio id="v-{k}" src="assets/{k}.wav" data-start="{T[k]:.3f}" data-duration="{D[k]:.3f}"></audio>' for k in ORDER)}
 <audio id="a-click" src="assets/sfx_click.wav" data-start="{T_FING + 0.35:.3f}" data-duration="0.08"></audio>
 <audio id="a-ting" src="assets/sfx_ting.wav" data-start="{T_BELL + 0.35:.3f}" data-duration="1.4"></audio>
</div>
<script src="{nm}/gsap/dist/gsap.min.js"></script>
<script>
const tl = gsap.timeline({{paused:true}});
{''.join(cam_js)}
// scene layers
tl.set("#chars",{{opacity:0}},0); tl.set("#chars",{{opacity:1}},{S2:.3f});
tl.set("#divine",{{opacity:0}},{S2:.3f}); tl.set("#chaks",{{opacity:0}},{S2:.3f});
tl.set("#divine",{{opacity:1}},{S5:.3f}); tl.set("#chars",{{opacity:0}},{S5:.3f});
tl.fromTo("#devs",{{opacity:0,scale:0.9,transformOrigin:"680px 1200px"}},{{opacity:1,scale:1,duration:0.7,ease:"power2.out",immediateRender:false}},{S5 + 0.05:.3f});
tl.set("#divine",{{opacity:0}},{S6:.3f}); tl.set("#chars",{{opacity:1}},{S6:.3f});
tl.set("#icons",{{opacity:0}},{S5:.3f});
tl.set("#bgc",{{opacity:1}},{S8:.3f});
// golden chakras spin (shot 1)
tl.to("#ch1",{{rotation:360,duration:3.2,repeat:3,ease:"none"}},0);
tl.to("#ch2",{{rotation:-360,duration:2.4,repeat:4,ease:"none"}},0);
tl.to("#ch3",{{rotation:360,duration:2.4,repeat:4,ease:"none"}},0);
tl.to("#ch4",{{rotation:-360,duration:2.0,repeat:5,ease:"none"}},0);
tl.fromTo(".chak",{{scale:0.6,opacity:0}},{{scale:1,opacity:1,duration:0.6,ease:"back.out(1.6)",stagger:0.12}},0);
// birds
tl.fromTo("#birds",{{x:0,y:0}},{{x:1750,y:-120,duration:5,ease:"none"}},{S2:.3f});
tl.fromTo("#birds2",{{x:0,y:0}},{{x:1750,y:-60,duration:6,ease:"none"}},{S8:.3f});
// walking (shot 8)
tl.set(".char",{{x:-150}},{S8:.3f}); tl.to(".char",{{x:0,duration:{WALK_D},ease:"none"}},{S8:.3f});
// astras
tl.fromTo("#counter",{{opacity:0,scale:0.5}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)",immediateRender:false}},{ICON_T[0] - 0.1:.3f});
tl.to("#counter",{{opacity:0,duration:0.2}},{S5:.3f});
{''.join(icon_js)}
// devtas merge into Ram
{''.join(orb_js)}
// question over the forest
tl.fromTo("#qbox",{{opacity:0,scale:0.3}},{{opacity:1,scale:1,duration:0.5,ease:"back.out(1.8)",immediateRender:false}},{T_Q:.3f});
tl.to("#qbox",{{scale:1.07,duration:0.5,yoyo:true,repeat:{int((END - T_Q - 0.5) / 0.5)},ease:"sine.inOut"}},{T_Q + 0.5:.3f});
tl.fromTo("#t2 b",{{scale:1}},{{scale:1.15,duration:0.5,yoyo:true,repeat:{int(END / 0.5) - 1},ease:"sine.inOut"}},0);
// subtitles
{''.join(sub_js)}
// subscribe widget (slides in during the last line)
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

cov = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS % {"nm": "fonts"}}
#q{{position:absolute;left:0;right:0;top:300px;margin:auto;width:max-content;color:#fff8e0;font-size:360px;font-weight:800;line-height:1;-webkit-text-stroke:12px #4a1200;paint-order:stroke fill;text-shadow:0 0 40px #ff9a00,0 0 90px #ff5a00,0 10px 0 #3a0e00}}
#tag{{position:absolute;top:1490px;left:0;right:0;text-align:center;color:#ffd23a;font-size:84px;font-weight:800;line-height:1.1;text-shadow:0 4px 0 #4a1a00}}
#tag2{{position:absolute;top:1610px;left:0;right:0;text-align:center;color:#fff;font-size:52px;font-weight:800}}
</style></head><body>
<div id="root" data-composition-id="cover" data-width="1080" data-height="1920" data-start="0" data-duration="1">
 <div id="win">
  <img src="assets/bg_divine.png" style="position:absolute;left:0;top:0;width:1008px;height:1230px">
  <img src="assets/ic_chakra4.png" style="position:absolute;left:224px;top:20px;width:560px;height:560px">
  <img src="assets/ic_brahma.png" style="position:absolute;left:345px;top:610px;width:310px;height:310px">
  <img src="assets/ram_nm.png" style="position:absolute;left:-170px;top:330px;width:760px;height:1031px">
  <img src="assets/vm_give.png" style="position:absolute;left:420px;top:320px;width:760px;height:1031px">
 </div>
 <img id="frame" src="assets/frame_b3.png">
 <div id="t1">रामायण · भाग 5</div>
 <div id="t2">राम को कौन-से दिव्य अस्त्र मिले<b>?</b></div>
 <div id="q">?</div>
 <img id="logo" src="assets/katha_chitra_logo.png">
 <div id="tag">ब्रह्मास्त्र भी मिला!</div>
 <div id="tag2">वाल्मीकि रामायण</div>
</div>
<script src="fonts/gsap/dist/gsap.min.js"></script>
<script>const tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},1);window.__timelines={{cover:tl}};</script>
</body></html>"""
open(f"{P}/cover/index.html", "w").write(cov)
print("END", END, {k: round(T[k], 2) for k in ORDER}, "S5", round(S5, 2), "S8", round(S8, 2))
