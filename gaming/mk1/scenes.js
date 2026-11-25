const OL='#120d1f', SKIN='#d89a6c', SKD='#b97a50', HOOD='#f4761f', HOODD='#c4560f', JEAN='#2d4a7c', JEAND='#213861';
const R=(a,b,t)=>a+(b-a)*t, C=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)), E=t=>{t=C(t);return t*t*(3-2*t)};
const P=(d,f,s=OL,w=6,ex='')=>`<path d="${d}" fill="${f}" stroke="${s}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round" ${ex}/>`;
const El=(x,y,rx,ry,f,s='none',w=0,ex='')=>`<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="${f}" stroke="${s}" stroke-width="${w}" ${ex}/>`;
const Rc=(x,y,w,h,f,rx=0,s='none',sw=0,ex='')=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${f}" stroke="${s}" stroke-width="${sw}" ${ex}/>`;
const G=(tr,body,ex='')=>`<g transform="${tr}" ${ex}>${body}</g>`;
const Tx=(x,y,s,txt,f='#fff',ex='')=>`<text x="${x}" y="${y}" font-family="Mukta" font-weight="800" font-size="${s}" fill="${f}" text-anchor="middle" ${ex}>${txt}</text>`;
function seg(pts,w,col){const d='M'+pts.map(p=>p.join(' ')).join(' L');
 return `<path d="${d}" fill="none" stroke="${OL}" stroke-width="${w+11}" stroke-linecap="round" stroke-linejoin="round"/><path d="${d}" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`}
const pol=(p,ang,len)=>[p[0]+Math.sin(ang)*len,p[1]+Math.cos(ang)*len]; // 0 = neeche, + = daayein
// haath: kalai (0,0), ungliyan +y ki taraf
function hand(w,ang,kind,side){let s='';
 const f=(x,y0,len,wd,rot)=>G(`rotate(${rot} ${x} ${y0})`,Rc(x-wd/2,y0,wd,len,SKIN,wd/2,OL,4)+`<path d="M${x-wd/2+3} ${y0+len*0.55} h${wd-6}" stroke="${SKD}" stroke-width="2.5"/>`);
 if(kind==='open'){[[-19,32,40,8],[-6,36,47,2],[7,36,45,-3],[19,32,36,-10]].forEach(([x,y,l,r])=>s+=f(x,y,l,13,r));
  s+=f(side*24,12,36,15,-side*48)+P('M-24 2 Q-30 36 -22 44 L22 44 Q30 36 24 2 Z',SKIN,OL,5)+`<path d="M${side*8} 10 Q${side*2} 28 ${side*16} 40" fill="none" stroke="${SKD}" stroke-width="3"/>`}
 else if(kind==='point'){s+=f(side*10,36,50,14,0)+P('M-22 0 Q-30 34 -16 48 L18 48 Q30 34 22 0 Z',SKIN,OL,5)+[-14,-2].map(x=>Rc(x-7,36,13,22,SKIN,6,OL,4)).join('')+f(side*22,12,30,14,-side*20)}
 else if(kind==='fist'){s+=P('M-22 0 Q-30 30 -20 44 L20 44 Q30 30 22 0 Z',SKIN,OL,5)+[-17,-6,6,17].map(x=>Rc(x-6.5,34,13,22,SKIN,6,OL,4)).join('')+f(side*20,16,30,14,side*32)}
 else {[[-15,32,30],[-4,34,36],[7,34,34],[17,31,28]].forEach(([x,y,l])=>s+=f(x,y,l,12,side*4));
  s+=P('M-21 0 Q-26 30 -19 42 L20 42 Q26 30 21 0 Z',SKIN,OL,5)+f(side*21,10,32,14,-side*16)}
 return G(`translate(${w[0]} ${w[1]}) rotate(${-ang*180/Math.PI})`,s)}
function shoe(x,y,dir){return dir===0?P(`M${x-44} ${y} Q${x-46} ${y-40} ${x} ${y-40} Q${x+46} ${y-40} ${x+44} ${y} Z`,'#f1f4fa')+Rc(x-47,y-4,94,16,'#c9d1e2',8,OL,5)+`<path d="M${x-16} ${y-30} h32 M${x-18} ${y-18} h36" stroke="#2ee6c9" stroke-width="5"/>`
 :G(`translate(${x} ${y}) scale(${dir} 1)`,P('M-34 4 Q-40 -40 -4 -36 L52 -14 Q70 -4 62 10 L-30 12 Z','#f1f4fa')+`<path d="M-32 8 L62 8" stroke="#2ee6c9" stroke-width="7"/>`)}
// chehra: emo = calm|worry|shock|sad|plead|wake
function head(o){const t=o.turn||0, emo=o.emo||'calm', m=o.mouth||0, bl=o.blink||0, ox=t*26; let s='';
 s+=P(`M-112 -30 Q-130 -160 0 -166 Q132 -164 114 -26 L96 40 L-96 40 Z`,'#171126');
 s+=El(-102+ox*0.2,6,19,28,SKIN,OL,5)+El(102+ox*0.2,6,19,28,SKIN,OL,5);
 s+=P('M-100 -40 Q-108 62 -52 98 Q0 128 52 98 Q108 62 100 -40 Q92 -118 0 -118 Q-92 -118 -100 -40 Z',SKIN);
 const open={calm:25,worry:29,shock:36,sad:21,plead:30,wake:34}[emo]*(1-bl);
 for(const k of [-1,1]){const ex=k*43+ox, ey=2;
  if(open<4) s+=`<path d="M${ex-27} ${ey} Q${ex} ${ey+12} ${ex+27} ${ey}" fill="none" stroke="${OL}" stroke-width="7" stroke-linecap="round"/>`;
  else {const pr=emo==='shock'?11:15; s+=El(ex,ey,28,open,'#fff',OL,5)+El(ex+(o.look||0)*11,ey+(o.lookY||0)*8,pr,Math.min(pr+2,open-3),'#4a2a17')+El(ex+(o.look||0)*11,ey+(o.lookY||0)*8,pr*0.5,Math.min(pr*0.6,open-4),'#0c0705')+El(ex+(o.look||0)*11+5,ey-6,4.5,4.5,'#fff')
   +`<path d="M${ex-30} ${ey-open*0.55} Q${ex} ${ey-open-9} ${ex+30} ${ey-open*0.55}" fill="none" stroke="${OL}" stroke-width="8" stroke-linecap="round"/>`}
  // bhaunh: andar wala sira
  const [inY,outY]={calm:[-50,-52],worry:[-68,-46],shock:[-74,-70],sad:[-66,-40],plead:[-72,-44],wake:[-68,-66]}[emo];
  s+=`<path d="M${ex-k*26} ${inY} Q${ex} ${(inY+outY)/2-9} ${ex+k*30} ${outY}" fill="none" stroke="#171126" stroke-width="13" stroke-linecap="round"/>`}
 s+=`<path d="M${ox*1.35-4} 14 Q${ox*1.35+14} 42 ${ox*1.35-8} 46" fill="none" stroke="${SKD}" stroke-width="6" stroke-linecap="round"/>`;
 const mx=ox*1.1, my=76;
 if(m>0.12){const h=8+m*26, w=24+(emo==='shock'?-4:5); s+=P(`M${mx-w} ${my-4} Q${mx} ${my-12} ${mx+w} ${my-4} Q${mx+w*0.8} ${my+h} ${mx} ${my+h} Q${mx-w*0.8} ${my+h} ${mx-w} ${my-4} Z`,'#4d1320',OL,5)+(h>16?El(mx,my+h-8,w*0.5,6,'#d9606a'):'')}
 else if(emo==='shock'||emo==='wake') s+=El(mx,my+4,15,19,'#4d1320',OL,5);
 else {const c={calm:12,worry:-9,sad:-14,plead:-7}[emo]; s+=`<path d="M${mx-26} ${my} Q${mx} ${my+c} ${mx+26} ${my}" fill="none" stroke="${OL}" stroke-width="7" stroke-linecap="round"/>`}
 s+=G(`translate(${-58+ox} 46) rotate(-22)`,Rc(-20,-8,40,16,'#f2dcc0',7,OL,3));
 // baal + ek hari-neeli lat
 s+=P(`M-108 -22 Q-128 -148 -30 -160 Q-12 -192 28 -164 Q104 -168 112 -86 Q126 -62 106 -20 Q98 -66 76 -78 L${66+ox*.4} -48 L${40+ox*.4} -90 L${12+ox*.5} -46 L${-6+ox*.4} -94 L${-48+ox*.3} -54 L-58 -90 Q-94 -72 -108 -22 Z`,'#1d1630');
 s+=P(`M6 -150 Q60 -152 ${70+ox*.4} -92 L${64+ox*.4} -56 L${42+ox*.4} -98 Q36 -128 6 -150 Z`,'#2ee6c9',OL,4);
 return s}
// saamne se poora ladka. pair (0,0) par. lambai ~ 900
function boy(o){const b=o.bob||0; let s='';
 s+=El(0,8,180,26,'#000','none',0,'opacity=".4"');
 for(const k of [-1,1]){s+=seg([[k*52,-385+b],[k*62,-205+b/2],[k*66,-42]],72,k<0?JEAND:JEAN)+shoe(k*68,-8,0)}
 const sh=[[-104,-600+b],[104,-600+b]], A=o.arms||[[-0.14,-0.06],[0.14,0.06]], H=o.hands||['rest','rest'];
 const torso=P(`M-130 ${-625+b} Q0 ${-668+b} 130 ${-625+b} Q142 ${-500+b} 112 ${-368+b} Q0 ${-346+b} -112 ${-368+b} Q-142 ${-500+b} -130 ${-625+b} Z`,HOOD)
  +P(`M-74 ${-452+b} L74 ${-452+b} L92 ${-384+b} L-92 ${-384+b} Z`,HOODD,OL,5)+P(`M-76 ${-640+b} Q0 ${-560+b} 76 ${-640+b} Q40 ${-668+b} 0 ${-660+b} Q-40 ${-668+b} -76 ${-640+b} Z`,HOODD,OL,5)
  +`<path d="M-22 ${-596+b} L-28 ${-520+b} M22 ${-596+b} L28 ${-520+b}" stroke="#f6f6f6" stroke-width="7" stroke-linecap="round"/>`;
 const arm=i=>{const k=i?1:-1,[a1,a2]=A[i], el=pol(sh[i],a1,150), wr=pol(el,a2,128);
  return seg([sh[i],el],64,HOOD)+seg([el,wr],52,HOOD)+El(sh[i][0]-k*14,sh[i][1]+6,25,27,HOOD)+hand(pol(wr,a2,4),a2,H[i],-k)};
 s+=Rc(-34,-690+b,68,70,SKD,20,OL,5)+torso;
 const front=o.armsBack?'':arm(0)+arm(1); if(o.armsBack) s=arm(0)+arm(1)+s;
 s+=G(`translate(${(o.turn||0)*14} ${-762+b+(o.headY||0)}) rotate(${o.tilt||0})`,head(o))+front;
 return s}
// bagal se daudta ladka (daayein ki taraf)
function runner(ph){let s=El(0,10,190,24,'#000','none',0,'opacity=".4"');
 const bob=-Math.abs(Math.sin(ph))*34, hip=[0,-360+bob];
 const leg=(p,col)=>{const th=Math.sin(p)*0.85, bend=C(Math.cos(p),0,1)*1.55+0.18, kn=pol(hip,th,190), ft=pol(kn,th-bend,186); return seg([hip,kn],76,col)+seg([kn,ft],58,col)+G(`translate(${ft[0]} ${ft[1]+10}) rotate(${C(-(th-bend)*40,-35,60)})`,shoe(0,0,1))};
 const sh=[52,-585+bob];
 const arm=(p,col)=>{const a=Math.sin(p)*0.95, el=pol(sh,a,135), wr=pol(el,a+1.45,112); return seg([sh,el],60,col)+seg([el,wr],48,col)+hand(wr,a+1.45,'fist',1)};
 s+=arm(ph,HOODD)+leg(ph+Math.PI,JEAND)+leg(ph,JEAN);
 s+=P(`M-78 ${-372+bob} Q-70 ${-560+bob} 6 ${-638+bob} Q120 ${-650+bob} 124 ${-560+bob} Q90 ${-440+bob} 70 ${-356+bob} Q0 ${-330+bob} -78 ${-372+bob} Z`,HOOD);
 s+=P(`M2 ${-634+bob} Q-80 ${-640+bob} -92 ${-560+bob} Q-30 ${-560+bob} 26 ${-606+bob} Z`,HOODD,OL,5);
 // bagal wala sir
 let h=El(0,0,96,108,SKIN,OL,6)+P('M80 -8 Q122 24 90 38 Z',SKIN,OL,5)+P('M-104 40 Q-150 -90 -40 -126 Q-10 -156 30 -130 Q108 -128 102 -50 L70 -62 L56 -36 L30 -74 Q-20 -60 -22 6 Q-36 74 -104 40 Z','#1d1630')+P('M6 -122 Q74 -124 96 -62 L74 -62 Q54 -104 6 -122 Z','#2ee6c9',OL,4)
  +El(-26,16,17,24,SKIN,OL,5)+El(52,-2,17,23,'#fff',OL,5)+El(58,-1,9,11,'#2a160b')+`<path d="M30 -38 Q56 -52 84 -34" fill="none" stroke="#171126" stroke-width="12" stroke-linecap="round"/><path d="M52 66 Q70 56 84 62" fill="none" stroke="${OL}" stroke-width="7" stroke-linecap="round"/>`;
 s+=G(`translate(108 ${-726+bob}) rotate(8)`,h)+arm(ph+Math.PI,HOOD);
 return s}
const rnd=i=>{const x=Math.sin(i*127.1)*43758.5453;return x-Math.floor(x)};
function city(t){let s=Rc(-200,-200,1480,2320,'url(#sky)');
 for(let i=0;i<70;i++) s+=El(rnd(i)*1080,rnd(i+99)*700,2+rnd(i+5)*2,2+rnd(i+5)*2,'#fff','none',0,`opacity="${0.3+0.5*Math.abs(Math.sin(t*1.5+i))}"`);
 s+=El(850,520,86,86,'#e8f3ff')+El(850,520,130,130,'#bcd8ff','none',0,'opacity=".14"');
 for(const [base,col,seed,hmin] of [[1330,'#1c1d4a',3,330],[1440,'#12122f',40,250]]) { let x=-80,i=seed; while(x<1160){const w=130+rnd(i)*110,h=hmin+rnd(i+1)*330; s+=Rc(x,base-h,w,h+200,col,4,OL,4);
   for(let yy=base-h+30;yy<base-40;yy+=62)for(let xx=x+22;xx<x+w-34;xx+=48) if(rnd(xx*7+yy+seed)>0.7) s+=Rc(xx,yy,22,32,rnd(xx+yy)>0.5?'#ffd873':'#7ee8ff',3,'none',0,'opacity=".8"'); x+=w+6;i+=3}}
 s+=Rc(-200,1440,1480,700,'#232044')+Rc(-200,1440,1480,16,'#4b457e');
 for(let i=0;i<6;i++) s+=P(`M${-100+i*260} 1760 l150 0 l-16 34 l-150 0 Z`,'#6a64a8','none',0);
 s+=Rc(110,880,18,580,'#0c0b1e',6)+P('M70 880 Q119 836 168 880 Z','#0c0b1e')+El(119,892,38,15,'#ffe9a8')+P('M96 896 L-40 1470 L300 1470 L142 896 Z','#ffe9a8','none',0,'opacity=".12"');
 return s}
function brick(base,mortar){let s=Rc(-200,-200,1480,2320,base);for(let r=0;r<34;r++)for(let c=-2;c<9;c++){s+=Rc(c*170+(r%2)*85,r*62,162,54,mortar,5,'none',0,`opacity="${0.18+rnd(r*31+c)*0.35}"`)}return s}
function phone(x,y,w,h,screen,glow=0){return Rc(x-w/2-20,y-h/2-20,w+40,h+40,'#2ee6c9',74,'none',0,`opacity="${glow*0.45}" filter="url(#blur)"`)+Rc(x-w/2,y-h/2,w,h,'#15131f',62,'#6d6a85',8)+`<clipPath id="ph"><rect x="${x-w/2+24}" y="${y-h/2+24}" width="${w-48}" height="${h-48}" rx="40"/></clipPath>`+`<g clip-path="url(#ph)">${screen}</g>`+Rc(x-60,y-h/2+38,120,26,'#000',13)}
function bedroom(){return Rc(-200,-200,1480,2320,'url(#room)')+Rc(690,330,280,380,'#2b3a7a',8,'#0b0a18',12)+El(880,420,40,40,'#dfeaff')+`<path d="M830 330 v380 M690 520 h280" stroke="#0b0a18" stroke-width="10"/>`
 +P('M-60 1330 Q300 1230 620 1320 Q900 1390 1160 1290 L1160 2000 L-60 2000 Z','#2a2358')+P('M-60 1560 Q400 1470 760 1560 Q960 1600 1160 1530','none','#3d3478',12)}
function gameScreen(x,y){return Rc(x-300,y-600,600,1200,'url(#sky)')+Rc(x-300,y+190,600,420,'#232044')+G(`translate(${x} ${y+330}) scale(.55)`,boy({emo:'calm'}))+Rc(x-230,y-430,460,22,'#222',11,'#fff',4)+Rc(x-226,y-426,300,14,'#4be36a',7)+El(x-160,y+440,58,58,'#ffffff33','#fff',5)+El(x+130,y+440,40,40,'#ff4d6d88','#fff',5)+El(x+205,y+370,32,32,'#4dd2ff88','#fff',5)}
// bada angootha (dekhne wale ka), power button dabata hua
function thumb(x,y){return G(`translate(${x} ${y})`,P('M0 -34 Q70 -52 150 -6 Q250 40 330 130 L520 330 L330 520 L170 300 Q120 250 90 180 Q30 90 -4 40 Q-30 -8 0 -34 Z',SKIN,OL,9)+P('M6 -22 Q50 -34 96 -8 Q74 26 34 20 Q4 8 6 -22 Z','#eec1a4',SKD,5)+`<path d="M112 96 q34 -28 66 -36 M138 124 q30 -22 58 -28" fill="none" stroke="${SKD}" stroke-width="6" stroke-linecap="round"/>`)}
const blinkAt=t=>{const p=(t+0.7)%3.1;return p<0.16?Math.sin(p/0.16*Math.PI):0};
const cam=(z,cx,cy,body)=>G(`translate(540 960) scale(${z}) translate(${-cx} ${-cy})`,body);
const SC={
l1(u,d,t,m){const off=u>1.75; const press=E((u-1.2)/0.45)*(1-E((u-2.1)/0.5));
 let scr=off?Rc(200,300,700,1400,'#030306')+P('M300 900 L560 620 L620 620 L360 900 Z','#ffffff','none',0,'opacity=".05"'):gameScreen(510,1010);
 if(u>1.75&&u<1.95) scr+=Rc(300,1000,420,10,'#fff',5);
 return cam(R(1,1.07,u/d),540,960,bedroom()+phone(510,1010,540,1060,scr,off?0:0.8)+thumb(R(900,792,press),R(900,800,press)))},
l2(u,d,t){const o=E((u-0.75)/0.18), z=R(1,1.16,E(u/d));
 let s=Rc(-200,-200,1480,2320,'#030308');
 for(let i=0;i<26;i++) s+=Rc(rnd(i)*1080,(rnd(i+3)*1920+u*90*(1+rnd(i)))%1920,4,40+rnd(i)*60,'#2ee6c9',2,'none',0,`opacity="${0.18*o}"`);
 s+=G('translate(540 1010) scale(3.1)',G('',head({emo:u<0.75?'calm':'wake',blink:1-o,look:0})),`opacity="${R(0.28,1,o)}"`);
 if(u>0.75) s+=Rc(-200,-200,1480,2320,'#bffcf2',0,'none',0,`opacity="${C(0.5-(u-0.75)*1.8)}"`);
 return cam(z,540,960,s)},
l3(u,d,t){const k=u/d; const turn=k<0.18?0:k<0.34?R(0,-1,E((k-0.18)/0.16)):k<0.55?-1:k<0.75?R(-1,1,E((k-0.55)/0.2)):1;
 return cam(R(1.0,1.08,k),540,1060,G('translate(0 -130)',city(t))+Rc(-200,1700,1480,500,'#232044')+G('translate(540 1420) scale(.96)',boy({emo:'worry',turn,look:turn,blink:blinkAt(t),tilt:turn*3,bob:Math.sin(t*3)*3})))},
l4(u,d,t){const a=E((u-0.5)/0.8); const A=[[R(-0.14,-0.55,a),R(-0.06,-3.503,a)],[R(0.14,0.55,a),R(0.06,3.503,a)]];
 const turnH=u>2.0?E((u-2.0)/0.5):0;
 return cam(R(1.5,1.68,E(u/d)),540,990,city(t)+G('translate(540 1640)',boy({emo:u<1?'worry':'shock',arms:A,hands:[a>0.5?'open':'rest',a>0.5?'open':'rest'],lookY:a,headY:a*12,tilt:Math.sin(turnH*Math.PI*2)*5,blink:blinkAt(t+1),bob:Math.sin(t*3)*3})))},
l5(u,d,t){const k=C(u/d); let s=brick('#241b3f','#4a3a72');
 for(let i=0;i<3;i++){const x=((i*620-u*430)%1860+1860)%1860-300; s+=Rc(x,420,190,250,'#0e0a1d',10,'#6a58a0',8)+El(x+95,300,40,18,'#ffd873')}
 s+=Rc(-200,1330,1480,800,'#17132c')+Rc(-200,1330,1480,14,'#43376e');
 for(let i=0;i<7;i++){const x=((i*260-u*620)%1820+1820)%1820-300; s+=El(x,1470+(i%3)*150,70,12,'#3a3166')}
 const dx=R(1750,880,E((u-d*0.45)/(d*0.55)));
 s+=Rc(dx-175,610,350,725,'#120c20',12,'#8b73c9',14)+Rc(dx-140,650,280,685,'#5a3320',8,OL,8)+El(dx,770,16,16,'#2ee6c9');
 const x=R(120,500,E(k)); const ph=u*11.5;
 for(let i=0;i<5;i++) s+=Rc(x-330-((u*700+i*90)%260),820+i*92,150,8,'#fff',4,'none',0,'opacity=".25"');
 s+=G(`translate(${x} 1420)`,runner(ph));
 return cam(1,540,960,s)},
l6(u,d,t){const reach=E((u-0.9)/0.8), fall=C((u-2.05)/0.45); let s=brick('#1e1735','#3d3062')+Rc(-200,1390,1480,800,'#141028');
 s+=Rc(200,470,680,930,'#0f0a1a',18,'#8b73c9',18)+Rc(240,510,600,890,'#5a3320',10,OL,9);
 for(let i=1;i<5;i++) s+=`<path d="M${240+i*120} 515 V1395" stroke="#3c200f" stroke-width="7"/>`;
 s+=`<path d="M240 600 q90 20 0 110 M240 600 q60 70 130 0 M240 660 q50 10 66 -56" fill="none" stroke="#cfd4ea" stroke-width="3" opacity=".7"/>`;
 // zanjeer + taala
 const chain=(x1,y1,x2,y2)=>{let c='';for(let i=0;i<=11;i++){const x=R(x1,x2,i/11),y=R(y1,y2,i/11)+Math.sin(i/11*Math.PI)*30;c+=G(`translate(${x} ${y}) rotate(${i%2?20:-20})`,El(0,0,i%2?38:24,i%2?17:26,'none','#9aa0b8',12))}return c};
 s+=G(`translate(0 ${fall*fall*520})`,chain(240,960,560,1050)+chain(840,960,560,1050)+G(`translate(560 1070) rotate(${Math.sin(u*20)*(reach>0.9?5:0)+fall*40})`,`<path d="M-34 0 v-36 a34 34 0 0 1 68 0 v36" fill="none" stroke="#c8cde0" stroke-width="18"/>`+Rc(-58,-6,116,100,'#d8a62e',16,OL,7)+El(0,34,13,13,'#2a1a07')+Rc(-5,36,10,30,'#2a1a07',4)),`opacity="${1-C((fall-0.7)/0.3)}"`);
 const beam=fall>0?Rc(540,515,6+fall*26,880,'#ffe9a8',4,'none',0,`opacity="${fall*0.9}"`):'';
 s+=beam;
 s+=Rc(350,640,380,120,'#b98b3c',16,OL,7)+Tx(540,726,72,'PLAYER','#2a1a07');
  const A=[[-0.14,-0.06],[R(0.14,1.0,reach),R(0.06,1.08,reach)]];
 s+=G('translate(220 1430) scale(.86)',boy({emo:fall>0?'shock':'worry',turn:0.85,look:1,arms:A,hands:['rest',reach>0.4?'point':'rest'],blink:blinkAt(t),bob:Math.sin(t*3)*2}));
 return cam(R(1.0,1.1,E(u/d)),540,1060,s)},
l7(u,d,t){let s=brick('#2a1220','#5c2a3c')+Rc(-200,1540,1480,600,'#170a14');
 const rows=[['आख़िरी पल में हार','#ff8fa0'],['नेट चला गया','#ffd27a'],['1% से हारा','#8fd8ff'],['साथी ने छोड़ दिया','#c9a8ff']];
 rows.forEach(([w,c],i)=>{const a=E((u-0.25-i*0.45)/0.35); s+=G(`translate(${540+(i%2?60:-60)} ${540+i*112}) rotate(${i%2?3:-3})`,Tx(0,0,66,w,c,`opacity="${a}"`))});
 for(let g=0;g<14;g++){const gx=70+(g%7)*148, gy=g<7?420:965; if(u>g*0.12) s+=[0,1,2,3].map(i=>`<path d="M${gx+i*22} ${gy} l6 70" stroke="#f3e6ee" stroke-width="7" opacity=".55"/>`).join('')+`<path d="M${gx-12} ${gy+52} l96 -34" stroke="#ff4d6d" stroke-width="7" opacity=".8"/>`}
 const a=E((u-1.5)/0.8);
 s+=G('translate(540 2200) scale(1.2)',boy({emo:u<1.3?'shock':'sad',turn:u<1.3?Math.sin(u*4)*0.6:0,look:u<1.3?Math.sin(u*4):0,lookY:u<1.3?-0.8:0.9,headY:a*26,arms:[[R(-0.14,-0.06,a),-0.02],[R(0.14,0.06,a),0.02]],blink:u>2.2?0.45:blinkAt(t),bob:a*10}));
 return cam(R(1.02,1.1,E(u/d)),540,990,s)},
l8(u,d,t){const on=C((u-1.55)/0.2); let s=brick('#170d22','#33204a')+Rc(-200,1540,1480,600,'#0d0816');
 s+=Rc(190,420,700,500,'#2ee6c9',40,'none',0,`opacity="${on*0.35}" filter="url(#blur)"`)+Rc(220,450,640,440,'#05060d',28,'#8b73c9',14);
 if(on>0) s+=G(`translate(540 670) scale(${R(0.6,1,E((u-1.55)/0.3))})`,Rc(-230,-120,460,240,'#0f2b36',26,'#2ee6c9',8)+Rc(-70,-82,140,90,'none',10,'#fff',9)+`<path d="M-70 -78 L0 -26 L70 -78" fill="none" stroke="#fff" stroke-width="9"/>`+El(76,-84,26,26,'#ff3b5c')+Tx(76,-71,38,'1')+Tx(0,82,62,'1 नया मैसेज','#bffcf2'),`opacity="${on}"`);
 s+=G('translate(540 2230) scale(1.2)',boy({emo:on>0?'shock':'sad',lookY:on>0?-0.9:0.7,headY:on>0?-10:20,arms:on>0?[[-0.5,-0.2],[0.5,0.2]]:[[-0.1,-0.02],[0.1,0.02]],hands:on>0?['open','open']:['rest','rest'],blink:on>0?0:blinkAt(t),bob:on>0?-14*Math.sin(C((u-1.55)/0.4)*Math.PI):6}))+Rc(-200,-200,1480,2320,'#2ee6c9',0,'none',0,`opacity="${on*0.07}"`);
 return cam(R(1.0,1.12,E(u/d)),540,1000,s)},
l9(u,d,t,m){let s=Rc(-200,-200,1480,2320,'url(#close)');
 for(let i=0;i<30;i++) s+=El(rnd(i)*1080,(rnd(i+8)*1920-u*30*(1+rnd(i))+1920)%1920,4+rnd(i)*8,4+rnd(i)*8,'#2ee6c9','none',0,`opacity="${0.12+rnd(i+2)*0.2}"`);
 const a=E((u-1.3)/0.9);
 s+=G('translate(540 2400) scale(2.05)',boy({emo:'plead',mouth:m,arms:[[-0.14,-0.06],[R(0.14,0.42,a),R(0.06,-2.62,a)]],hands:['rest',a>0.5?'open':'rest'],blink:blinkAt(t+2),bob:Math.sin(t*2.6)*2,tilt:-3*a}));
 return cam(R(1.0,1.09,E(u/d)),540,1060,s)},
l10(u,d,t){const on=E((u-0.5)/0.3);
 const scr=on<0.05?Rc(200,300,700,1400,'#030306'):G('',gameScreen(540,900)+G(`translate(540 590)`,Rc(-215,-95,430,190,'#07121aee',24,'#2ee6c9',6)+Tx(0,-18,52,'आप क्या करोगे?')+Tx(0,58,46,'▶ फिर से खेलो','#ffd873')),`opacity="${on}"`);
 const shake=(u>0.5&&u<1.3)?Math.sin(u*70)*7:0;
 return cam(R(1.0,1.05,u/d),540,960,bedroom()+G(`translate(${shake} 0)`,phone(540,880,540,1020,scr,on*(0.7+0.3*Math.sin(t*5)))))}
};

function cover(){const q=Tx(900,900,330,'?','#ffd23f','stroke="#120d1f" stroke-width="22" paint-order="stroke" filter="drop-shadow(0 0 40px #ffd23f)"');
 return Rc(-200,-200,1480,2320,'url(#close)')+Rc(150,560,780,1300,'#2ee6c9',90,'none',0,'opacity=".35" filter="url(#blur)"')+Rc(180,590,720,1500,'#0c0b18',80,'#6d6a85',14)+Rc(430,622,220,42,'#000',20)
 +G('translate(500 2330) scale(1.75)',boy({emo:'shock',arms:[[-0.14,-0.06],[0.62,-2.75]],hands:['rest','open'],tilt:-4}))+q
 +Rc(70,270,940,270,'#0b0918f0',44,'#2ee6c9',8)+Tx(540,385,100,'गेम बंद किया...')+Tx(540,500,92,'पर प्लेयर नहीं रुका!','#ffd23f')+Rc(340,1560,400,100,'#f4761f',50,'#120d1f',8)+Tx(540,1630,62,'MK Gaming')+Rc(0,0,1080,1920,'url(#vig)')}
