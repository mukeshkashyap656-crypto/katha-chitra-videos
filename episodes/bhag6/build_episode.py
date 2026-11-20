import json, html, os, re
P = os.environ.get("EP", "/home/claude/ep") + "/proj"
lip = json.load(open(f"{P}/lip.json"))
FPS = 30

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

ORDER = ["n1", "vm1", "vm2", "n2", "n3", "vm3", "n4", "ram", "n5"]
D = {k: lip[k]["dur"] for k in ORDER}
T = {}
T["n1"] = 0.35
for i in range(1, len(ORDER)):
    T[ORDER[i]] = T[ORDER[i - 1]] + D[ORDER[i - 1]] + 0.35
E = {k: T[k] + D[k] for k in ORDER}
WT = {k: [(w, T[k] + o) for w, o in align(k)] for k in ORDER}

END = round(E["n5"] + 1.0, 2)

CSS = """
@font-face{font-family:Mukta;font-weight:800;src:url(%(nm)s/@fontsource/mukta/files/mukta-devanagari-800-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mukta,sans-serif}
#win{position:absolute;left:36px;top:226px;width:1008px;height:1228px;overflow:hidden;background:#2a1a10}
#cam{position:absolute;left:0;top:0;width:1360px;height:1660px;transform-origin:0 0}
.wfull{position:absolute;left:0;top:0;width:1360px;height:1660px}
#frame{position:absolute;left:0;top:0;width:1080px;height:1920px}
#t1{position:absolute;top:58px;left:0;right:0;text-align:center;color:#ffd65a;font-size:40px;font-weight:800;line-height:1}
#t2{position:absolute;top:110px;left:0;right:0;text-align:center;color:#fff;font-size:62px;font-weight:800;line-height:1;white-space:nowrap}
#t2 b{display:inline-block;color:#ffcf3a;text-shadow:0 0 24px #ff9a00,0 0 50px #ff6a00}
#logo{position:absolute;right:56px;top:246px;width:104px;height:104px;border-radius:50%%}
"""

sub_html = []
sub_js = []
for k in ORDER:
    spans = "".join(f'<span id="w{k}{i}" class="w">{html.escape(w)}</span> ' for i, (w, t) in enumerate(WT[k]))
    sub_html.append(f'<div class="sline" id="L{k}">{spans}</div>')
    sub_js.append(f'tl.set("#L{k}",{{opacity:1}},{T[k] - 0.2:.3f});tl.set("#L{k}",{{opacity:0}},{E[k] + 0.1:.3f});')
    for i, (w, t) in enumerate(WT[k]):
        sub_js.append(f'tl.to("#w{k}{i}",{{opacity:1,duration:0.08}},{t:.3f});')

doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{CSS % {"nm": "node_modules"}}
.sline{{position:absolute;left:70px;right:70px;top:1566px;text-align:center;color:#fff;font-size:64px;font-weight:800;line-height:1.28;opacity:0}}
.w{{display:inline-block;opacity:.32}}
.w.key{{color:#ffd23a;text-shadow:0 0 14px #ff9a00}}
</style></head>
<body>
<div id="root" data-composition-id="root" data-width="1080" data-height="1920" data-start="0" data-duration="{END}">
 <div id="win"><div id="cam">
  <img class="wfull" src="assets/bg_cloudvan.png">
 </div></div>
 <img id="frame" src="assets/frame_b3.png">
 <div id="t1">रामायण · भाग 6</div>
 <div id="t2">भगवान ने कहाँ तप किया था<b>?</b></div>
 <img id="logo" src="assets/katha_chitra_logo.png">
 {''.join(sub_html)}
 {''.join(f'<audio id="v-{k}" src="assets/{k}.wav" data-start="{T[k]:.3f}" data-duration="{D[k]:.3f}"></audio>' for k in ORDER)}
</div>
<script src="node_modules/gsap/dist/gsap.min.js"></script>
<script>
const tl = gsap.timeline({{paused:true}});
{''.join(sub_js)}
tl.set({{}},{{}},{END});
window.__timelines = window.__timelines || {{}};
window.__timelines["root"] = tl;
</script>
</body></html>"""
open(f"{P}/index.html", "w").write(doc)

cov = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS % {"nm": "fonts"}}
#q{{position:absolute;left:0;right:0;top:300px;margin:auto;width:max-content;color:#fff8e0;font-size:360px;font-weight:800;line-height:1;-webkit-text-stroke:12px #4a1200;paint-order:stroke fill;text-shadow:0 0 40px #ff9a00,0 0 90px #ff5a00}}
#tag{{position:absolute;top:1490px;left:0;right:0;text-align:center;color:#ffd23a;font-size:84px;font-weight:800}}
</style></head><body>
<div id="root" data-composition-id="cover" data-width="1080" data-height="1920" data-start="0" data-duration="1">
 <div id="win">
  <img src="assets/bg_cloudvan.png" style="position:absolute;left:0;top:0;width:1008px;height:1230px">
 </div>
 <img id="frame" src="assets/frame_b3.png">
 <div id="t1">रामायण · भाग 6</div>
 <div id="t2">भगवान ने कहाँ तप किया था<b>?</b></div>
 <div id="q">?</div>
 <img id="logo" src="assets/katha_chitra_logo.png">
 <div id="tag">वाल्मीकि रामायण</div>
</div>
<script src="fonts/gsap/dist/gsap.min.js"></script>
<script>const tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},1);window.__timelines={{cover:tl}};</script>
</body></html>"""
open(f"{P}/cover/index.html", "w").write(cov)
print("END", END)
