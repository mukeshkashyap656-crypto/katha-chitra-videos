# Katha Chitra — Insaan ki body ke niyam (BODY.md)

Poora research BODY_FULL.md mein hai (sources ke saath). Ye uska kaam ka saar hai. Har episode mein ye sab pehle se lagte hain.
Pehle NIYAM.md aur SEEKH.md padho, phir ye. Naya sudhaar mile toh SEEKH.md mein joddo.

## Sabse bada niyam: har scene ke hisaab se body movement
- Body/chehra ki harkat hamesha scene ke hisaab se: kaun kiski taraf dekh raha hai, kis mood mein hai, kya kar raha hai (chalna, rukna, pranam, sunna, bolna, ladai).
- Chalne wala jis taraf ja raha hai, chehra aur body usi taraf. Samne khada insaan us aane wale ki taraf dekhe (person(turn=...)). Camera ki taraf koi nahi dekhta, jab tak kahani mein camera se baat na ho.
- Har scene ke liye pehle likho: kaun kahan, kis taraf mukh, kya harkat, kaisa bhav. Phir banao.

## Asli insaan ka data (motion capture) se liya hua
- Chalne ke angle ab asli logon ke motion capture (CMU, free for all uses) se liye gaye hain: `template/lib/chars.py` mein GAIT table (24 sample ka ek chakkar). Jaanghon ka swing ~+33 se -30 degree, ghutna swing mein ~60 degree mudta hai, paon zameen se ~0.2 pair-lambai uthta hai, kadam lamba hai (pehle ka lagbhag doguna), haath ~+-28 degree jhoolta aur kohni aage jaate waqt ~40 degree mudti hai.
- Paer phislein nahi: body ko har 12 frame (ek chakkar) mein 3.2*u aage badhao (u = insaan ki oonchai/5). Isse kam/zyada karoge to paer zameen par skate karte dikhenge.
- Rukna: asli 'walk, then stop' data (CMU 16_33) chars.py mein STOPT: draw_char(name, file, side=+1/-1, stop=0..1). Rukte waqt body thodi der aage badhti hai: C.stop_disp(stop)*u. Chalne ka aakhri frame stop ke pehle frame se milna chahiye (walk phase = 2*pi*11/24). Pranam mein side=±1 ke saath stop=1.0, arms=JOIN, fixarms=True, bend=..., bowpos=... do.
- Aur harkat chahiye toh `tools/gait.py` aur `tools/bvh.py` se kisi bhi CMU motion (baithna-uthna 13_01, ruk kar chalna 16_33, mudna 16_17, jhukna 02_06) ke angle nikaal kar chars.py mein table banao. Data: github.com/sfd158/cmu-mocap (data/<subject>/<file>.bvh).
- person(..., bend=radian) = kamar se jhukna (pranam). Pranam ke haath: arms=(0.1, 2.24, -0.1, -2.24). Pranam mein dhanush kandhe par (draw_char bowpos=0..1 se haath se peeth par dheere se). Khade character mein t=samay se halki saans.

## Naap (sab insaan ek size ke, bas chhote farq)
- Sar = 1 unit; bada insaan ~7.5 sar lamba. Bachcha 5-6 sar (sar bada), boodha thoda jhuka (~7).
- Kandhe ~2 sar chaude, kulhe ~1.5, haath ka sira jaangh ke beech tak. Aurat ke kulhe chaude, kandhe patle; aadmi ke kandhe chaude.
- Joint ki hadd: kohni peeche nahi mudti; ghutna sirf aage mudta hai (~150 degree); gardan ghumna ~80; kandha poora 180.

## Chalna
- 60% pair zameen par, 40% hawa mein. Ek pair zameen par hamesha (daudne mein dono hawa mein).
- Pair uthte hain, phisalte nahi. Haath pair ke ulte hilte hain. Sar seedha/level rehta hai.
- Kamar aur kandhe ulte ghoomte hain (kamar pehle). Body halka upar-neeche (zyada bounce nahi). Halka aage jhukaav.
- Shuru karne se pehle wazan thoda neeche. Rukte waqt ek chhota kadam, kamar pehle ruke, haath baad mein, kapde/gehne baad mein.
- Bachcha: chhote kadam, paon door-door. Boodha: dheere, chhote kadam, jhuka hua. Daudna: body aage, dono pair hawa mein.
- Side-view (bagal se) chalna: draw_char(..., walk=phase, side=+1/-1) (+1 = screen ke daayein dekhta hai). Chehra chalne ki disha mein ghoomta hai (person(turn=...) se koi bhi scene mein chehra jis taraf dekhna ho us taraf), tarkash peeth par, door wala haath-pair gehre rang mein. Chehra camera ki taraf nahi, scene ki disha mein.
- Engine mein ye `template/lib/chars.py` ke WALK code mein lag chuka hai (12 frame ka chakkar). Naya chalne wala scene 12 frame se banao, 4 se nahi.

## Mudna, baithna, uthna
- Pehle aankhen, phir sar, phir body. Mudne se pehle ulti taraf halki taiyari. Sar halka arc banata hai.
- Baithna/uthna: pehle dhad aage jhuke, phir kulhe uthein/baithein, phir seedhe. Jhatke se nahi. Boodhe zyada dheere, haath ke sahare.
- Aasan: sukhasana (paalthi), vajrasana (ediyon par), padmasana. Yagya/pooja mein paalthi maar kar.

## Pranam
- Haath jodo, ungliyan upar, anguthe seene ke paas, kamar se halka jhukna. Bade ko maathe tak haath. Khade ya baithe dono mein.

## Bolna
- Mouth shapes awaaz se thoda pehle shuru: "a" bahut khula, "e" chauda, "i" honth khinche, "o" gol, "u" gol aur aage.
- Bolte waqt sar, bhawen aur haath bhi hilein. Zor wale shabd par halki hilaaki. Baar-baar ek hi gesture nahi.

## Aankhen, saans, khade rehna
- Palak ~har 2 second; band tez, khule dheere. Aankhen sar se pehle chalein. Poori tarah jami nazar nahi.
- Kabhi bilkul sthir nahi: saans (seena/kandha halke upar-neeche), wazan ka shift, kapde/jata halke hilein.

## Bhavna body se (chehra + body dono)
- Khushi: body phaili, gaal upar. Garv: seena phula, sar upar. Sharm/vinamrata: sar neeche, kandhe gol.
- Gussa: body aage, mutthi kasi, bhawen neeche-paas. Dar: pehle achanak jam jaana, kandhe upar, peeche jhukna, haath se bachaav, kaanpna.
- Dukh: dheeme, kandhe gire, sar neeche, haath latke. Roona: aansu, kandhe halke hilen; sob mein saans toote, jhukna.
- Navras ke rang-niyam NIYAM.md ke hisaab se.

## Dhanush, ladai, bhaari cheez
- Dhanush: paon kandhe ki chaudai par, dono haath T jaise, dori nak/thodi ke paas tak, chhodne ke baad halka follow-through.
- Bhaari hathiyar (gada): dheemi taiyari, dheemi recovery, wazan dikhe. Patli talwaar tez.
- Bhaari cheez uthana: zyada taiyari, ghutne mudein, chaudi stance.
- Girna: chhota girna, sambhalne mein zyada samay; body ke hisse alag samay par pahunchein.

## Sab movement ke niyam
1. Har harkat se pehle chhoti taiyari (anticipation), baad mein follow-through.
2. Alag hisse alag samay par: kamar pehle, kandhe baad mein, aankhen sar se pehle.
3. Jitna bhaari, utni dheemi taiyari aur recovery.
4. Pair zameen par phislein nahi. Body kabhi bilkul sthir nahi.
5. Har insaan/umar/mizaaj ki apni chaal (Ram shaant, boodhe dheere, bachche chhote kadam).

## Abhi baaki (24 Nov 2026 ko badla)
- Ho chuka (pehle): asli data se chalna + rukna, chehra disha mein, pranam (bend), dhanush kandhe par, saans.
- Ho chuka (24 Nov, branch `ai-fix-movement`, test episode `episodes/test_move` se jaancha): engine mein side-view chalna lag gaya.
  - spec.py: `WALK_N=12`; walk shot ke liye `<base>_walk0..11` ki 12 tasveerein + khade ki `<base>` + 3 `<base>_turn0..2` (aate hi sar dheere samne). `side` = chalne ki disha (to_x >= x -> +1, warna -1).
  - draw.py: `draw_state(..., walk, side, turn)`; chalte waqt `arms=None` (dono haath mocap se jhoolte, ARMS list nahi), chalte waqt side-view, baad mein C.WALK/C.SIDE reset.
  - build.py: chaal ki raftaar asli = body har 1.0 sec ke chakkar mein 3.2*u aage (u = oonchai/5; U_H=128, U_B=160). Doori/raftaar se chalne ka samay; samay kam ho toh chakkar tez (cyc), par shot ke 90% se zyada nahi. Pahunchte hi legs ruk kar khade, 0.1 sec ke 3 kadam mein sar samne. Har character ka chaal ka shuru alag (`woff`) taaki do log ek jaise kadam par na chalein. Movement tween `ease:"none"` (seedhi raftaar).
  - Jaanch ke niyam: do chalne wale ke beech 260 px se kam jagah nahi; ek doosre ko paar (overtake) karne wale na hon.
- Baaki: mudna (CMU 16_17 se), baithna-uthna (CMU 13_01), jude haath aur aashirvaad ka khula haath, tunic ka halka jhoolna, Lakshman/rishi/aurat/bachche/boodhe ki alag chaal, samne ya door chalna (front/away walk), phir `test_move` ka v3 render dekhna aur tabhi `auto-video` mein merge.
- Naya chalna sirf NAYE episodes mein lagta hai. Purane bane episodes (Bhag 2-6) dobara nahi bante; unko chhodo (user ka hukm, 24 Nov 2026).

- NAZAR: samne chalte/dekhte/bolte character ke pupil beech mein (look=0); kisi aur ko dekhna ho toh `turn` se sar modo. Details ANIMATION.md.

- BOLNA/MUDNA: bolte waqt sar halka nod-tilt (engine khud, `t` badlo); sar mudne par `turn_seq(p)` se pehle aankhen phir sar. Details ANIMATION.md.

- BOLNA: munh ka shape awaaz se 2-4 frame PEHLE, sirf accents par shape (zyada shape nahi), vaaky se pehle munh thoda khule. CHALNA: paer zameen par jame (phisle nahi), kamar paer ke ulte, haath paer ke ulte. Details ANIMATION.md.

- ENGINE (21 Nov): tools/engine/build.py mein LIP_LEAD=3 -> munh awaaz se 3 frame (30fps) pehle chalta hai; badalna ho toh wahi ek number.
