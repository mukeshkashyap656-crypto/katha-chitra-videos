"""EXAMPLE from Bhag 4 test v4: HyperFrames composition in the Bhag 3 look. Copy and change shots/lines per episode.
Run: EP=/home/claude/ep python3 build_episode.py  -> proj/index.html and proj/cover/index.html
"""

import json, html, os
import os
P = os.environ.get("EP", "/home/claude/ep") + "/proj"
lip = json.load(open(f"{P}/lip.json"))
FPS = 30
T_RAM = 1.6; RAM_D = lip["ram"]["dur"]; R_END = T_RAM + RAM_D
T_VM = R_END + 0.55; VM_D = lip["vm"]["dur"]; V_END = T_VM + VM_D
T_SUB = V_END - 0.3; T_BELL = T_SUB + 0.8
END = round(T_BELL + 0.35 + 1.4 + 0.45, 2)
WALK_END = 1.3; T_TURN = T_VM - 0.45

KEYS = {"डरावना", "ताड़का", "हज़ार", "हाथियों"}
RAM_W = [(w, T_RAM + o) for w, o, d in lip["ram"]["words"]]
VM_W = [(w, T_VM + o) for w, o, d in lip["vm"]["words"]]
RAM_SHOW = ["गुरुदेव...", "ये", "इतना", "डरावना", "जंगल", "किसका", "है?"]
VM_SHOW = ["ये", "ताड़का", "का", "वन", "है,", "राम।", "उसमें", "हज़ार", "हाथियों", "जितनी", "ताक़त", "है!"]
T_TATAKA = VM_W[1][1]; T_RAMW = VM_W[5][1]; T_HAZAR = VM_W[7][1]; T_JITNI = VM_W[9][1]

def blink(t, off): return (t + off) % 3.4 < 0.12
def mouth(key, t, t0):
    sh = lip[key]["shapes"]; k = int((t - t0) * FPS)
    return sh[k] if 0 <= k < len(sh) else "X"
def walkf(pre, t): return f"{pre}_walk{int(t / 0.13) % 4}"
def lak_state(t):
    if t < WALK_END: return walkf("lak", t)
    if t < T_TATAKA + 0.25: return "lak_n_blink" if blink(t, 1.5) else "lak_n"
    return "lak_firm_blink" if blink(t, 1.5) else "lak_firm"
def ram_state(t):
    if t < WALK_END: return walkf("ram", t)
    if t < T_TATAKA:
        if T_RAM <= t < R_END: return f"ram_ask_{mouth('ram', t, T_RAM)}"
        return "ram_ask_blink" if blink(t, 0.4) else "ram_ask_X"
    return "ram_firm_blink" if blink(t, 0.4) else "ram_firm"
def vm_state(t):
    if t < WALK_END: return walkf("vm", t)
    if t < T_TURN: return "vm_stand_blink" if blink(t, 2.4) else "vm_stand"
    if t < T_TURN + 0.4: return f"vm_turn{min(4, int((t - T_TURN) / 0.1) + 1)}"
    if T_VM <= t < V_END: return f"vm_talk_{mouth('vm', t, T_VM)}"
    return "vm_talk_blink" if blink(t, 2.4) and t > V_END + 0.3 else "vm_talk_X"

W4 = [f"_walk{i}" for i in range(4)]
FEET = 1480; DW, DH = 689, 935          # character box in world px (HS 640)
CHARS = {
    "lak": (280, lak_state, [f"lak{w}" for w in W4] + ["lak_n", "lak_n_blink", "lak_firm", "lak_firm_blink"]),
    "ram": (640, ram_state, [f"ram{w}" for w in W4] + [f"ram_ask_{m}" for m in "XABEOM"] + ["ram_ask_blink", "ram_firm", "ram_firm_blink"]),
    "vm": (1060, vm_state, [f"vm{w}" for w in W4] + ["vm_stand", "vm_stand_blink"] + [f"vm_turn{i}" for i in range(1, 5)] + [f"vm_talk_{m}" for m in "XABEOM"] + ["vm_talk_blink"]),
}
sets = []; layers = []
for cid, (cx, fn, keys) in CHARS.items():
    imgs = "".join(f'<img id="{cid}-{k}" class="ci" src="assets/{k}.png" style="opacity:{1 if k == fn(0) else 0}">' for k in keys)
    layers.append(f'<div class="char walker" id="{cid}" style="left:{cx - DW/2:.0f}px;top:{FEET + 37 - DH}px">{imgs}</div>')
    prev = fn(0)
    for f in range(1, int(END * FPS)):
        t = f / FPS; s = fn(t)
        if s != prev:
            sets.append(f'tl.set("#{cid}-{prev}",{{opacity:0}},{t:.3f});tl.set("#{cid}-{s}",{{opacity:1}},{t:.3f});'); prev = s

def words_html(show, pre):
    return "".join(f'<span id="{pre}{i}" class="w{" key" if any(k in x for k in KEYS) else ""}">{html.escape(x)}</span> ' for i, x in enumerate(show))
word_sets = [f'tl.to("#rw{i}",{{opacity:1,duration:0.1}},{t:.3f});' for i, (_, t) in enumerate(RAM_W)]
word_sets += [f'tl.to("#vw{i}",{{opacity:1,duration:0.1}},{t:.3f});' for i, (_, t) in enumerate(VM_W)]

# camera: world 1360x1660 shown in a 1008x1228 window; zoom z relative to the full view
WW, WH, VW, VH = 1360, 1660, 1008, 1228; S0 = VW / WW
def cam(px, py, z):
    s = S0 * z; x = VW / 2 - s * px; y = VH / 2 - s * py
    x = min(0, max(VW - WW * s, x)); y = min(0, max(VH - WH * s, y))
    return f"x:{x:.1f},y:{y:.1f},scale:{s:.4f}"
WIDE = cam(680, 830, 1.0)
TWO = cam(455, 1190, 1.766); TWO2 = cam(470, 1170, 1.86)          # Ram + Lakshman, Vishwamitra fully out
VMC = cam(1105, 1075, 2.6); VMC2 = cam(1105, 1068, 2.72)          # Vishwamitra close-up, Ram fully out
ENDS = cam(680, 860, 1.06)

CSS = """
@font-face{font-family:Mukta;font-weight:800;src:url(%(nm)s/@fontsource/mukta/files/mukta-devanagari-800-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mukta,sans-serif}
#win{position:absolute;left:36px;top:226px;width:1008px;height:1228px;overflow:hidden;background:#0e1d18}
#cam{position:absolute;left:0;top:0;width:1360px;height:1660px;transform-origin:0 0}
.wfull{position:absolute;left:0;top:0;width:1360px;height:1660px}
.char{position:absolute;width:689px;height:935px}
.ci{position:absolute;left:0;top:0;width:689px;height:935px}
#frame{position:absolute;left:0;top:0;width:1080px;height:1920px}
#t1{position:absolute;top:58px;left:0;right:0;text-align:center;color:#ffd65a;font-size:40px;font-weight:800;line-height:1}
#t2{position:absolute;top:104px;left:0;right:0;text-align:center;color:#fff;font-size:78px;font-weight:800;line-height:1}
#t2 b{display:inline-block;color:#ffcf3a;text-shadow:0 0 24px #ff9a00,0 0 50px #ff6a00}
#logo{position:absolute;right:56px;top:246px;width:104px;height:104px;border-radius:50%%}
"""
nm = "node_modules"
doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{CSS % {"nm": nm}}
#shadow{{position:absolute;left:180px;top:170px;width:1000px;height:1290px;opacity:0;-webkit-mask-image:linear-gradient(#000 55%,transparent 80%);mask-image:linear-gradient(#000 55%,transparent 80%)}}
#birds{{position:absolute;left:-320px;top:260px;width:300px;height:120px}}
.name{{position:absolute;top:1508px;left:0;right:0;text-align:center;color:#f0be3c;font-size:44px;font-weight:800;line-height:1}}
.line{{position:absolute;left:84px;right:84px;top:1572px;text-align:center;color:#fff;font-size:64px;font-weight:800;line-height:1.3;opacity:0}}
.w{{display:inline-block;opacity:.32}}
.w.key{{color:#ffd23a;text-shadow:0 0 14px #ff9a00}}
#chip{{position:absolute;left:0;right:0;margin:auto;top:380px;width:420px;background:#1a0a06;border:5px solid #ffcf3a;border-radius:30px;color:#fff;font-size:52px;font-weight:800;padding:8px 0;text-align:center;box-shadow:0 0 30px #ff7a00;opacity:0}}
#chip b{{color:#ffcf3a}}
#sub{{position:absolute;left:150px;top:1340px;width:780px;height:100px;background:rgba(18,18,22,.93);border:2px solid rgba(255,255,255,.2);border-radius:52px;box-shadow:0 8px 24px rgba(0,0,0,.6);opacity:0}}
#sub img.l{{position:absolute;left:12px;top:12px;width:76px;height:76px;border-radius:50%}}
#sub .ch{{position:absolute;left:102px;top:16px;color:#fff;font-size:34px;font-weight:800;line-height:1}}
#sub .hd{{position:absolute;left:102px;top:58px;color:#aaa;font-size:24px;font-weight:800;line-height:1}}
#btn,#btn2{{position:absolute;left:432px;top:18px;width:236px;height:64px;border-radius:34px;font-weight:800;line-height:64px;text-align:center}}
#btn{{background:#e62117;color:#fff;font-size:30px}}
#btn2{{background:#3a3a40;color:#ddd;font-size:26px;opacity:0}}
#bell{{position:absolute;left:684px;top:18px;width:64px;height:64px;border-radius:50%;background:#3a3a40}}
#bell svg{{position:absolute;left:13px;top:12px;width:38px;height:40px}}
#finger{{position:absolute;left:669px;top:1389px;width:70px;height:100px;opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="root" data-width="1080" data-height="1920" data-start="0" data-duration="{END}">
 <div id="win"><div id="cam">
  <img class="wfull" id="bg" src="assets/bg_forest.png">
  <img class="wfull" id="dread" src="assets/bg_dread.png" style="opacity:0">
  <img id="birds" src="assets/birds.png">
  <img id="shadow" src="assets/tataka_shadow.png">
  {''.join(layers)}
 </div></div>
 <img id="frame" src="assets/frame_b3.png">
 <div id="t1">रामायण · भाग 4</div>
 <div id="t2">ताड़का कौन थी<b>?</b></div>
 <img id="logo" src="assets/katha_chitra_logo.png">
 <div id="chip">बल = <b>1000</b> हाथी</div>
 <div class="name" id="n1" style="opacity:0">श्रीराम</div><div class="name" id="n2" style="opacity:0">महर्षि विश्वामित्र</div>
 <div class="line" id="l1">{words_html(RAM_SHOW, "rw")}</div>
 <div class="line" id="l2">{words_html(VM_SHOW, "vw")}</div>
 <div id="sub"><img class="l" src="assets/katha_chitra_logo.png"><div class="ch">Katha Chitra</div><div class="hd">@kathachitra_123</div>
  <div id="btn">SUBSCRIBE</div><div id="btn2">✓ SUBSCRIBED</div>
  <div id="bell"><svg viewBox="0 0 24 24"><path id="bellp" fill="#fff" d="M12 22a2.5 2.5 0 0 0 2.4-2h-4.8A2.5 2.5 0 0 0 12 22zm7-6V11a7 7 0 0 0-5.5-6.8V3.5a1.5 1.5 0 0 0-3 0v.7A7 7 0 0 0 5 11v5l-2 2v1h18v-1z"/></svg></div>
 </div>
 <img id="finger" src="assets/finger.png">
 <audio id="sfx-forest" src="assets/sfx_forest.wav" data-start="0" data-duration="{END}" data-volume="0.55" data-fade-out="0.8"></audio>
 <audio id="voice-ram" src="assets/ram.wav" data-start="{T_RAM:.3f}" data-duration="{RAM_D:.3f}"></audio>
 <audio id="sfx-whoosh" src="assets/sfx_whoosh.wav" data-start="{T_TURN - 0.15:.3f}" data-duration="0.6" data-volume="0.5"></audio>
 <audio id="voice-vm" src="assets/vm.wav" data-start="{T_VM:.3f}" data-duration="{VM_D:.3f}"></audio>
 <audio id="sfx-boom" src="assets/sfx_boom.wav" data-start="{T_TATAKA:.3f}" data-duration="1.6" data-volume="0.8"></audio>
 <audio id="sfx-sparkle" src="assets/sfx_sparkle.wav" data-start="{T_HAZAR:.3f}" data-duration="0.7" data-volume="0.6"></audio>
 <audio id="sfx-click" src="assets/sfx_click.wav" data-start="{T_SUB + 0.35:.3f}" data-duration="0.08"></audio>
 <audio id="sfx-ting" src="assets/sfx_ting.wav" data-start="{T_BELL + 0.35:.3f}" data-duration="1.4"></audio>
</div>
<script src="{nm}/gsap/dist/gsap.min.js"></script>
<script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo(".walker",{{x:-110}},{{x:0,duration:{WALK_END},ease:"none"}},0);
tl.fromTo("#birds",{{x:0,y:0}},{{x:1700,y:-140,duration:4.5,ease:"none"}},0.2);
// shots
tl.set("#cam",{{{WIDE}}},0);
tl.to("#cam",{{{cam(680, 860, 1.06)}, duration:{T_RAM - 0.45:.2f},ease:"none"}},0);
tl.to("#cam",{{{TWO}, duration:0.45,ease:"power2.inOut"}},{T_RAM - 0.45:.3f});
tl.to("#cam",{{{TWO2}, duration:{T_TURN - T_RAM - 0.15:.2f},ease:"none"}},{T_RAM:.3f});
tl.set("#cam",{{{VMC}}},{T_TURN - 0.15:.3f});
tl.to("#cam",{{{VMC2}, duration:{T_TATAKA - T_TURN:.2f},ease:"none"}},{T_TURN - 0.15:.3f});
tl.set("#cam",{{{WIDE}}},{T_TATAKA:.3f});
tl.set("#cam",{{{TWO}}},{T_RAMW - 0.05:.3f});
tl.to("#cam",{{{TWO2}, duration:{T_HAZAR - T_RAMW:.2f},ease:"none"}},{T_RAMW - 0.05:.3f});
tl.set("#cam",{{{WIDE}}},{T_HAZAR - 0.05:.3f});
tl.fromTo("#shadow",{{scale:1}},{{scale:1.04,duration:0.8,yoyo:true,repeat:{int((END - T_TATAKA) / 0.8):d},ease:"sine.inOut"}},{T_TATAKA + 0.9:.3f});
// Vishwamitra steps toward Ram while turning
tl.to("#vm",{{x:-26,duration:0.4,ease:"power1.inOut"}},{T_TURN:.3f});
// Tataka
tl.to("#dread",{{opacity:1,duration:0.6}},{T_TATAKA:.3f});
tl.fromTo("#shadow",{{opacity:0,scale:0.85,y:50}},{{opacity:0.92,scale:1,y:0,duration:0.9,ease:"power2.out"}},{T_TATAKA:.3f});
tl.fromTo("#win",{{x:0}},{{x:6,duration:0.05,yoyo:true,repeat:7}},{T_TATAKA + 0.05:.3f});
tl.set("#win",{{x:0}},{T_TATAKA + 0.5:.3f});
// strength chip
tl.fromTo("#chip",{{opacity:0,scale:0.4}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(2)"}},{T_HAZAR:.3f});
tl.to("#chip",{{opacity:0,scale:0.6,duration:0.25}},{V_END + 0.1:.3f});
tl.fromTo("#t2 b",{{scale:1}},{{scale:1.15,duration:0.5,yoyo:true,repeat:{int(END / 0.5) - 1},ease:"sine.inOut"}},0);
// subtitles
tl.to("#n1",{{opacity:1,duration:0.2}},{T_RAM - 0.3:.3f});
tl.to("#l1",{{opacity:1,duration:0.2}},{T_RAM - 0.3:.3f});
tl.to("#l1",{{opacity:0,duration:0.12}},{T_TURN - 0.2:.3f});
tl.to("#n1",{{opacity:0,duration:0.12}},{T_TURN - 0.2:.3f});
tl.to("#n2",{{opacity:1,duration:0.15}},{T_VM - 0.22:.3f});
tl.to("#l2",{{opacity:1,duration:0.15}},{T_VM - 0.22:.3f});
{''.join(word_sets)}
// subscribe widget
tl.fromTo("#sub",{{opacity:0,y:50}},{{opacity:1,y:0,duration:0.4,ease:"power2.out"}},{T_JITNI:.3f});
tl.fromTo("#finger",{{opacity:0,x:120,y:70}},{{opacity:1,x:0,y:0,duration:0.35,ease:"power2.out"}},{T_SUB:.3f});
tl.to("#finger",{{scale:0.88,duration:0.08,yoyo:true,repeat:1}},{T_SUB + 0.35:.3f});
tl.to("#btn",{{scale:0.92,duration:0.08,yoyo:true,repeat:1}},{T_SUB + 0.35:.3f});
tl.to("#btn2",{{opacity:1,duration:0.12}},{T_SUB + 0.45:.3f});
tl.to("#finger",{{x:166,duration:0.35,ease:"power2.inOut"}},{T_BELL:.3f});
tl.to("#finger",{{scale:0.88,duration:0.08,yoyo:true,repeat:1}},{T_BELL + 0.35:.3f});
tl.to("#bellp",{{fill:"#ffd23a",duration:0.1}},{T_BELL + 0.4:.3f});
tl.to("#bell",{{boxShadow:"0 0 30px #ffb000",duration:0.15}},{T_BELL + 0.4:.3f});
tl.fromTo("#bell",{{rotation:0}},{{rotation:16,duration:0.08,yoyo:true,repeat:9,ease:"sine.inOut"}},{T_BELL + 0.4:.3f});
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
#q{{position:absolute;left:0;right:0;top:330px;margin:auto;width:max-content;color:#ffcf3a;font-size:330px;font-weight:800;line-height:1;text-shadow:0 0 40px #ff9a00,0 0 90px #ff5a00}}
#tag{{position:absolute;top:1560px;left:0;right:0;text-align:center;color:#ffd23a;font-size:84px;font-weight:800;line-height:1.1}}
#tag2{{position:absolute;top:1680px;left:0;right:0;text-align:center;color:#fff;font-size:52px;font-weight:800}}
</style></head><body>
<div id="root" data-composition-id="cover" data-width="1080" data-height="1920" data-start="0" data-duration="1">
 <div id="win">
  <img src="assets/bg_dread.png" style="position:absolute;left:0;top:0;width:1008px;height:1230px">
  <img src="assets/tataka_shadow.png" style="position:absolute;left:104px;top:60px;width:800px;height:1030px">
  <img src="assets/ram_firm.png" style="position:absolute;left:-150px;top:330px;width:760px;height:1031px">
  <img src="assets/vm_talk_X.png" style="position:absolute;left:400px;top:330px;width:760px;height:1031px">
 </div>
 <img id="frame" src="assets/frame_b3.png">
 <div id="t1">रामायण · भाग 4</div>
 <div id="t2">ताड़का कौन थी<b>?</b></div>
 <div id="q">?</div>
 <img id="logo" src="assets/katha_chitra_logo.png">
 <div id="tag">1000 हाथियों का बल!</div>
 <div id="tag2">वाल्मीकि रामायण</div>
</div>
<script src="fonts/gsap/dist/gsap.min.js"></script>
<script>const tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},1);window.__timelines={{cover:tl}};</script>
</body></html>"""
open(f"{P}/cover/index.html", "w").write(cov)
print("END", END, "tataka", round(T_TATAKA, 2), "hazar", round(T_HAZAR, 2), "turn", round(T_TURN, 2))
