import json, subprocess, os, base64, math, sys
import numpy as np
SR=48000; FPS=30
V=json.load(open('/tmp/gv/voice.json',encoding='utf-8'))
EXTRA={'l1':0.35,'l5':0.5,'l6':0.55,'l7':0.5,'l8':0.35,'l9':0.75,'l10':1.5}
def load(p):
    b=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(b,np.float32).copy()
scenes=[];t=0.0;clips=[]
for x in V:
    a=load(f"/tmp/gv/{x['id']}.mp3")
    last=x['words'][-1][1]+x['words'][-1][2]
    a=a[:int((last+0.25)*SR)]; a*=0.11/max(1e-6,np.sqrt(np.mean(a[np.abs(a)>0.02]**2)))
    a[-1200:]*=np.linspace(1,0,1200)
    lead=0.12; dur=round((lead+last+0.3+EXTRA.get(x['id'],0.1))*FPS)/FPS
    env=[float(min(1,np.sqrt(np.mean(a[int(i*SR/FPS):int((i+1)*SR/FPS)]**2 if int(i*SR/FPS)<len(a) else np.zeros(1)))*7)) for i in range(int(dur*FPS)+2)]
    scenes.append(dict(id=x['id'],start=t,dur=dur,who=x['who'],lead=lead,words=[[w[0],w[1]+lead,w[2]] for w in x['words']],text=x['text'],env=env))
    clips.append((t+lead,a)); t+=dur
N=int(t*SR); mix=np.zeros(N,np.float32); rng=np.random.default_rng(3)
def add(at,sig,g=1.0):
    i=int(at*SR); 
    if i<N: s=sig[:N-i]; mix[i:i+len(s)]+=s*g
tt=lambda d: np.arange(int(d*SR))/SR
def lown(d,k):
    n=rng.standard_normal(int(d*SR)+k); return np.convolve(n,np.ones(k)/k,'valid')[:int(d*SR)].astype(np.float32)
def click(): x=tt(0.07); return (rng.standard_normal(len(x))*np.exp(-x*110)+np.sin(2*np.pi*1800*x)*np.exp(-x*80)).astype(np.float32)
def whoosh(d=0.5): x=tt(d); return (lown(d,14)*np.sin(np.pi*x/d)**2*3).astype(np.float32)
def boom(): x=tt(1.2); return (np.sin(2*np.pi*(70*x-18*x*x))*np.exp(-x*3.2)).astype(np.float32)
def ding(f=1320): x=tt(0.9); return ((np.sin(2*np.pi*f*x)+0.5*np.sin(2*np.pi*f*1.5*x))*np.exp(-x*5)).astype(np.float32)
def step(): x=tt(0.12); return (lown(0.12,30)*np.exp(-x*35)*5).astype(np.float32)
def clank(): x=tt(0.5); return sum(np.sin(2*np.pi*f*x) for f in (523,1187,1960,2750)).astype(np.float32)*np.exp(-x*11).astype(np.float32)/4
def buzz(): x=tt(0.35); return (np.sign(np.sin(2*np.pi*150*x))*0.5*np.minimum(1,(0.35-x)*20)).astype(np.float32)
# dheema rahasya wala pichhla sur
x=tt(t); pad=(np.sin(2*np.pi*110*x)+0.7*np.sin(2*np.pi*164.8*x)+0.4*np.sin(2*np.pi*220.6*x))*(0.75+0.25*np.sin(2*np.pi*0.18*x))
add(0,(pad.astype(np.float32)+lown(t,60)*1.2)*0.012*np.minimum(1,np.minimum(x/1.0,(t-x)/1.2)).astype(np.float32))
S={s['id']:s['start'] for s in scenes}
add(S['l1']+1.75,click(),0.35); add(S['l2']+0.75,boom(),0.28); add(S['l2']+0.72,whoosh(0.4),0.15)
for k in ('l3','l5','l6','l7','l8','l9','l10'): add(S[k]-0.18,whoosh(0.4),0.12)
d5=[s for s in scenes if s['id']=='l5'][0]['dur']
for i in range(int(d5*11.5/math.pi)): add(S['l5']+(i+0.5)*math.pi/11.5,step(),0.22)
add(S['l6']+2.05,clank(),0.2); add(S['l6']+2.45,boom(),0.2); add(S['l8']+1.57,ding(),0.2); add(S['l8']+1.57,boom(),0.15)
add(S['l10']+0.5,buzz(),0.1); add(S['l10']+0.95,buzz(),0.1)
ten=[s for s in scenes if s['id']=='l10'][0]
SUBAT=S['l10']+ten['words'][-3][1]
add(SUBAT+1.0,click(),0.3); add(SUBAT+1.55,ding(1760),0.16); add(SUBAT+1.75,ding(2100),0.12)
for at,a in clips: add(at,a)
mix*=min(1,0.97/np.abs(mix).max())
open('/tmp/mk/a.f32','wb').write(mix.tobytes())
font=base64.b64encode(open('/tmp/mk/node/node_modules/@fontsource/mukta/files/mukta-devanagari-800-normal.woff2','rb').read()).decode()
font2=base64.b64encode(open('/tmp/mk/node/node_modules/@fontsource/mukta/files/mukta-latin-800-normal.woff2','rb').read()).decode()
js=open('/tmp/mk/src/s.js',encoding='utf-8').read()
html='''<!doctype html><meta charset="utf-8"><style>@font-face{font-family:Mukta;font-weight:800;src:url(data:font/woff2;base64,%s);unicode-range:U+0900-097F,U+200C-200D,U+25CC}@font-face{font-family:Mukta;font-weight:800;src:url(data:font/woff2;base64,%s)}body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#000;font-family:Mukta;font-weight:800}#s{position:absolute;left:0;top:0}
.box{position:absolute;left:60px;right:60px;text-align:center}#q{top:96px;background:#0b0918e8;border:5px solid #2ee6c9;border-radius:36px;color:#fff;font-size:56px;line-height:1.35;padding:14px 20px}#q b{color:#ffd23f;font-weight:800}
#tag{position:absolute;right:44px;top:312px;color:#fff;font-size:34px;background:#f4761fdd;border-radius:30px;padding:2px 24px}
#sub{bottom:290px;font-size:62px;line-height:1.5}#sub span.in{display:inline-block;background:#0b0918e0;border-radius:30px;padding:10px 34px}#sub i{font-style:normal;color:#ffffff80}#sub i.on{color:#fff}#sub i.now{color:#ffd23f}
#cta{position:absolute;left:90px;width:900px;bottom:140px;height:112px;white-space:nowrap;border-radius:60px;background:#ffffffee;display:flex;align-items:center;justify-content:center;gap:24px;font-size:48px;color:#14101f}#btn{background:#e8212e;color:#fff;border-radius:40px;padding:6px 30px}</style>
<svg id="s" width="1080" height="1920" viewBox="0 0 1080 1920"></svg><div class="box" id="q">गेम बंद करने के बाद<br><b>प्लेयर क्या करता है?</b></div><div id="tag">MK Gaming</div><div class="box" id="sub"></div><div id="cta"></div>
<script>%s
const SCN=%s, SUBAT=%f;
const DEFS='<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0b2a"/><stop offset=".6" stop-color="#2d2468"/><stop offset="1" stop-color="#7a3a7e"/></linearGradient><linearGradient id="room" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b1640"/><stop offset="1" stop-color="#0c0a1e"/></linearGradient><radialGradient id="close" cx=".5" cy=".45" r=".7"><stop offset="0" stop-color="#2b3f74"/><stop offset="1" stop-color="#07060f"/></radialGradient><radialGradient id="vig" cx=".5" cy=".48" r=".72"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient><filter id="blur" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="28"/></filter></defs>';
function frame(T){let s=SCN[SCN.length-1];for(const c of SCN){if(T<c.start+c.dur-1e-6){s=c;break}}
 const u=T-s.start, i=Math.floor(u*30); let m=s.who==='p'?(s.env[Math.min(s.env.length-1,i+2)]||0):0;
 const fade=s.id==='l1'?0:C(1-u/0.2);
 document.getElementById('s').innerHTML=DEFS+SC[s.id](u,s.dur,T,m)+Rc(0,0,1080,1920,'url(#vig)')+Rc(0,0,1080,1920,'#000',0,'none',0,'opacity="'+fade*0.7+'"');
 // subtitle: lambi line do hisson mein
 const W=s.words, parts=[];let cur=[];W.forEach((w,k)=>{cur.push(w);if(cur.length>=9){parts.push(cur);cur=[]}});if(cur.length)parts.push(cur);
 let pi=0;parts.forEach((p,k)=>{if(u>=p[0][1]-0.05)pi=k});
 const sub=document.getElementById('sub');
 sub.innerHTML=u<W[0][1]-0.05?'':'<span class="in">'+(s.who==='p'?'<i class="on" style="color:#2ee6c9">प्लेयर: </i>':'')+parts[pi].map((w,k,a)=>{const nx=a[k+1]?a[k+1][1]:w[1]+w[2]+0.2;return '<i class="'+(u>=w[1]&&u<nx?'now':u>=nx?'on':'')+'">'+w[0]+'</i>'}).join(' ')+'</span>';
 const c=document.getElementById('cta'), a=E((T-SUBAT)/0.35); c.style.display=a>0?'flex':'none'; c.style.transform='translateY('+(1-a)*300+'px)';
 const done=T>SUBAT+1.0, bell=T>SUBAT+1.55?Math.sin((T-SUBAT-1.55)*38)*22*C(1-(T-SUBAT-1.55)/0.9):0;
 c.innerHTML='<span>MK Gaming</span><span id="btn" style="background:'+(done?'#555':'#e8212e')+'">'+(done?'✓ SUBSCRIBED':'SUBSCRIBE')+'</span><span style="display:inline-block;transform:rotate('+bell+'deg)">🔔</span>'+(T>SUBAT+0.65&&T<SUBAT+1.25?'<span style="position:absolute;left:560px;top:'+(done?40:56)+'px;font-size:86px">👆</span>':'');
}
</script>'''%(font,font2,js,json.dumps(scenes,ensure_ascii=False),SUBAT)
open('/tmp/mk/page.html','w',encoding='utf-8').write(html)
json.dump(dict(total=t,scenes=[[s['id'],round(s['start'],2),round(s['dur'],2)] for s in scenes]),open('/tmp/mk/meta.json','w'))
print(round(t,2),[(s['id'],round(s['start'],2),round(s['dur'],2)) for s in scenes])
