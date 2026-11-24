# Katha Chitra — 2D animation ke niyam (ANIMATION.md)

Ye normal cartoon / Disney ke 12 niyam aur cut-out animation ki aam galtiyon se bana hai. Har video se PEHLE ye padho aur BAAD mein har scene ko is list se jaancho. NIYAM.md, SEEKH.md, BODY.md ke saath lagta hai. Koi bhi galti mile toh video bhejne se pehle theek karo.
Sources: Thomas & Johnston ke 12 niyam (en.wikipedia.org/wiki/Twelve_basic_principles_of_animation, adobe.com/creativecloud/animation/discover/principles-of-animation), cut-out animation (docs.godotengine.org cutout_animation: rotation pivot galat ho toh body ghalat ghoomti hai), School of Motion ki aam galtiyan (schoolofmotion.com), CG Channel ki "10 subtle mistakes" (tube jaise seedhe haath-pair, akde kandhe).

## 12 niyam, apne kaam ke hisaab se
1. **Squash/stretch:** tez harkat ya takkar par shape thodi dabe/phele, par poori body ki matra (volume) wahi rahe.
2. **Anticipation (taiyari):** har badi harkat se pehle ulti taraf chhoti taiyari (rukne se pehle, jhukne se pehle, vaar se pehle).
3. **Staging:** ek scene mein ek hi baat saaf dikhe. Silhouette (kaali parchhai) dekho: pose pehchaana jaye, haath body ke saamne ulajh kar chhup na jaye. Kaun kis taraf dekh raha hai saaf ho.
4. **Pose to pose:** pehle bade poses (shuru, beech, ant) tay karo, phir beech ke frame. Kisi bhi frame mein character ka size ya jagah achanak na badle.
5. **Follow through / overlap:** body ke hisse alag samay par ruken (kamar pehle, kandhe, haath, phir kapde/gehne/jata sabse baad mein).
6. **Slow in / slow out:** har harkat dheere shuru ho, beech mein tez, dheere khatam. Seedhi barabar raftaar (linear) mat rakho.
7. **Arcs:** haath, sar, paon gol raaste (arc) par chalein, seedhi line mein nahi.
8. **Secondary action:** chhoti saath ki harkat (palak, saans, kapde ka hilna), par mukhya harkat se zyada na ho.
9. **Timing:** kam frame = tez, zyada frame = dheema/bhaari. Bhaari cheez (gada) dheemi.
10. **Exaggeration:** thoda badha kar dikhao taaki 9:16 ke chhote screen par bhi saaf dikhe, par character ka roop wahi rahe.
11. **Solid drawing:** body ka wazan (balance) dikhe: wazan jis pair par ho, body us par tiki ho. Girte hue na lage.
12. **Appeal:** saaf, pehchane jaane wale shape; har character ka apna andaaz.

## Cut-out (puppet) animation ki aam galtiyan: har frame mein dhoondho
- **Cheez chipki ho:** dhanush/tarkash/kamandalu kisi haath ya kandhe se juda ho. Hawa mein tairta nahi. Haath hat jaye toh uski mutthi bhi saath hat jaye (peeche akeli mutthi na chhoote).
- **Pivot sahi jagah:** haath kandhe se, kohni, ghutna, kamar se ghoome. Jod ke paas tukde alag-alag na dikhein.
- **Tube jaise sidhe haath-pair mat:** halka mod, kohni/ghutna thoda mudta hua.
- **Akde kandhe:** haath uthne par kandha bhi thoda uthe/aage jaye.
- **Pair zameen par:** chalte waqt paer phislein nahi (body ki raftaar paer ke ghatne-badhne se mile, BODY.md ka 3.2*u), neeche wala paer zameen ko chhuye, hawa mein tairta na lage.
- **Do character ek-doosre ke andar na ghuse:** jhukne wale ka sar/haath doosre ko na chhuye (jagah chhodo).
- **Chehra disha mein:** jis taraf dekh raha hai/ja raha hai, chehra aur aankhen usi taraf. Aankhen barabar aur seedhi (trichi nahi); do aankhon ka aakar ek jaisa.
- **Frame se bahar na kate:** haath ya sir frame ke kinare se aadha kata na ho.
- **Same character, same roop:** har frame mein wahi chehra, kapde, rang, size.
- **Achanak chhalaang (pop) nahi:** ek pose se doosre par beech ke frame se jao (jaise dhanush haath se peeth par dheere se).
- **Jyada symmetric mat:** dono haath bilkul ek jaise na hilein; thoda offset.
- **Rotoscope jaisa nakal nahi:** asli data se angle lo, par har cheez ko cartoon ki tarah saaf aur thoda badha kar dikhao.
- **Har character jam na jaye:** khade rehne par bhi saans, palak, wazan ka shift.

## Har scene ke baad ye jaanch (haan/nahi, sab haan hone chahiye)
1. Koi cheez hawa mein tair rahi ya haath se alag toh nahi?
2. Haath-pair ulajh kar ek-doosre ya body ke andar toh nahi?
3. Chehra aur aankhen scene ki sahi disha mein?
4. Silhouette saaf: pose pehchaana jata hai?
5. Paer zameen par, phisal nahi rahe?
6. Beech ke frame hain, koi pop/chhalaang nahi?
7. Koi aadha kata nahi, koi character doosre ke upar nahi?
8. Wazan dikhta hai, taiyari aur follow-through hai?
9. Phone ke chhote screen par saaf dikhta hai?
Ek bhi nahi toh sudharo, phir dobara jaancho.

## Nazar (gaze) ka niyam — aankhen wahin jahan chehra/body
- Samne (camera ki taraf) chalta, dekhta ya baat karta character: DONO pupil seedhe beech mein (purani Katha Chitra style). Pupil ek kone mein khinche nahi.
- Kisi aur ki taraf dekhna ho (Ram rishi ko): sar mod do (`turn=+1/-1`) aur body usi taraf; sirf pupil mat khischo. Engine bina `turn` ke pupil ko +-0.25 se zyada hone nahi deta.
- Dekhne wale ki taraf hi dekha jaye: dono character ek-doosre ki taraf (A→B toh B bhi A ki taraf).
- Chalte waqt sar seedha (level) rahe, tedha nahi; chehra ghoom kar camera se na hate jab tak scene na maange.

## Tutorials se seekha (walk, chehra/aankhen, bolna) — 21 Nov 2026
Sources: Adobe walk cycle, BMCC 2D animation walk cycles, LinkedIn Learning 2D walk basics, Tuts+ head turn, Animator Island eyes, Animation Mentor blinks/eyes, Bloop eyes, Clip Studio eye angles, Pluralsight lip sync, Peachpit dialogue, RMCAD lip sync.
(YouTube transcript tool ke credits khatam the, isliye wahi sikhaaye jaane wale tutorials likhe hue roop mein padhe.)

### Chalna (walk cycle)
- 4 mukhya pose: contact (aage ka pair pehli baar zameen par), down (sabse neeche, wazan girta hai), passing (pair ek-doosre ko paar karte hain), up (sabse upar). Fir ulta pair. Sirf pair nahi: haath, dhad aur sar bhi har pose mein hilte hain.
- Sar down pose mein sabse neeche, up pose mein sabse upar. Contact aur down thoda zyada der rakho, passing/up kam der.
- Mood chal se dikhta hai: udaas = haath latke (peeche-aage kam), thoda aage jhuka, uchhal kam. Khush/akad = uchhal zyada, haath zyada.
- Alag-alag character ki chal alag (budhe dheere, bacche chhote tez kadam, yodha seena tana).

### Sar ghumana aur aankhen
- Sar ghumate waqt aakar (mass) aur sar ki oonchai wahi rahe; aankh-naak-munh ek saath sahi jagah par khisken. Sar kabhi seedhi line mein nahi ghoomta; thoda arc (neeche-upar) hota hai.
- Aankhen aksar sar se PEHLE mudti hain, phir sar, aur palak jhapakna sar ghumne/nazar badalne ke saath hota hai.
- 3/4 view mein door wali aankh thodi chhoti aur naak ke paas hoti hai.
- Aankhon ki disha aur sar ki disha ka mel (sync) na ho toh matlab badal jaata hai (shak, chhup kar dekhna). Normal scene mein dono ek disha mein.
- Der tak ek taraf dekhna ho toh aankh halki si idhar-udhar (dart) kare, par disha wahi rahe.
- Camera/darshak ko dekhna ho toh pupil seedhe beech mein.

### Bolna (lip sync / dialogue)
- Munh ka shape sirf 10-20% asar hai; asli asar sar, body, chehre aur aankhon se aata hai. Bolte waqt sar halka jhatke (accent), bhaunh uthe, haath ishaara kare.
- Munh jawab (awaaz) se 1-2 frame PEHLE khule taaki dikhe ki awaaz usi se aayi; band hone wale shabdon (m, b, p) par munh sach mein band ho.
- Cartoon ke liye kam shape kaafi: band, khula, chauda, "oo" gol. Thoda badha-chadha kar (exaggerate) dikhao.
- Mauun/ruki hui jagah par munh band, par aankhen aur saans chalti rahein.

### Body/weight
- Line of action (S ya C curve): har pose mein ek behta hua rekha; seedha khada khamba nahi.
- Wazan: khade/chalte waqt wazan ek pair par shift ho, kandha-kamar ulte jhuken. Bhaari cheez dheemi, halki tez.
- Drag/overlap: kapde, jata, dupatta baad mein ruken.

### Aur seekha + engine mein laga diya (21 Nov 2026)
Sources: Animator Island eyes, Pluralsight 12 steps walk cycle.
- Aankhen sar se pehle mudti hain; tez chhoti chhoti nazar-badal (dart) se "dekh raha/soch raha" lagta hai; par bina maksad pupil idhar-udhar tairna ya sar mud jaye aur aankh ek jagah atki rahe, ye galtiyan hain. Bahut der aankh bilkul na hile toh character "murda" lagta hai (palak/halki nazar chahiye). Nazar ka badlav tab dikhao jab body ruk jaye.
- Chalte waqt: uchhal zyada nahi, kamar paer ke theek upar rahe; contact par ghutna halka mudha; haath ki harkat kandhe se kohni se kalai tak kramse; seena tabhi hile jab haath hilein; paer hawa se zameen par 1-2 frame mein aaye.
- ENGINE: `chars.turn_seq(p)` (p=0..1) dega (turn, look, blink): pehle aankhen, phir sar, shuru mein palak, slow-in/slow-out. Sar mudne wale scene mein isi se `turn=`, `look=`, `blink=` do.
- ENGINE: `mouth` "X" ke alawa kuch ho (bol raha) toh sar/body mein halka nod-tilt apne aap aata hai (`t` badalte raho); chup khade par nahi.
- Jab vidIQ ke credits wapas aayein: YouTube tutorials ke transcript khud padho (vidiq_youtube_search + vidiq_video_transcript), seekhi baatein yahin likho, user se pooche bina.

### YouTube transcripts se seekha (21 Nov 2026) — cut-out walk (Harmony puppet rig), head turn (BaM Animation), walk basics
Ye khaas hamare kaam ka hai kyunki wo cut-out/puppet rig ki walk hai (humari engine bhi aisi hi hai).
**Walk (cut-out rig):**
- Pehle contact poses, phir passing, phir down, phir up (sab ek saath seedhe shuru se nahi). Ek kadam = 4 poses, do kadam = 8 drawings.
- 24 fps par "twos" (har pose 2 frame) = 16 frame ka chakkar. Kam fps par ones. Koi bhi galat nahi, bas mood ke hisaab se.
- Asli chal ko tracing karo toh "tairti" lagti hai; isliye up/down thoda badha kar dikhao. (Humne mocap angle liye hain, isliye up-down ko thoda exaggerate karna).
- Ek hi jagah chalte raho (treadmill): pehle chakkar ban jaye, phir poore character ko raste par ek barabar raftaar se chalao taaki paer phisle nahi (hamara 3.2*u niyam).
- Quarter (3/4) view mein chalna profile se zyada achha lagta hai (zyada dikhta hai); idle/bolte waqt bhi 3/4 achha.
- Contact par pichhla paer thoda uncha aur aage ka seedha; passing par kamar upar (paer seedha), down par sabse neeche (ghutna mudha). Dono passing ki oonchai barabar. Ghutne par thoda mod rakho (knee pop se bachne ke liye).
- Haath paer se ULTI disha mein, par timing alag (pe pehle, haath 2-3 frame baad). Haath mein halka mod; kandha-kohni-kalai kramse (drag/overlap), haath ke ant mein follow-through.
- Kamar/pair ek taraf mudte hain, kandhe ulte, sar kandhe ke saath balance karta hai. Sar down par thoda neeche, up par thoda upar. Sar aur haath ki harkat 2-3 frame der se.
- Paer zameen se uthte waqt ease out; haath ke peak par ease. Spacing barabar rakho taaki jhatke na lagein. Zameen se door wala paer door-door aaraam se, zameen wala paer barabar doori par.
- 3/4 view mein kamar chauri, paer/haath beech ki taraf aate-jaate; kapde mein halka squash/stretch.
**Sar mudna (head turn):**
- Mudne se pehle halka anticipation (thoda neeche ya ulti taraf), phir mud kar; beech wala drawing BILKUL beech mein mat rakho (barabar doori = robot). Pehle frame ke paas rakho: dheere shuru, phir tezi se jhatke se mudna, phir settle.
- Palak jhapakna: character mudte waqt aksar palak jhapakta hai.
- Sar ghumne par sar ya dhad ka aakar na badle (sar "lamba" ya body chhoti-badi na ho); apne drawings ko dobara jaanch lo.
- Baal/kapde sar ke baad ruke (secondary): sar mud jaye tab bhi thoda aage chalein, phir settle. Isse "plastic ka putla" nahi lagta.
- Zyada baarik details (freckles, extra lines) animation ke liye hata do, shape saaf rakho.
- Key pose sabse zaroori; breakdown/inbetween thode ajeeb dikh sakte hain, wo theek hai.
- Kisi ki baat par sudhar karo, apni zid mat rakho.

### Poses aur acting (YouTube: owenferny "Acting and Body Mechanics" review se, 21 Nov 2026)
- TWINNING mat karo: dono haath/kandhe/paer ek jaise sheesha-tasveer na hon. Ek haath/kandha doosre se alag ooncha, alag kona; ek haath pehle ruke ya hate (natural offset).
- Reedh/dhad mein seedhi line nahi: C ya S curve. Kamar (hips) ek taraf uthi toh seena (chest) ulti taraf; sar un dono ke balance mein. Silhouette (kaali parchhai) mein shape saaf badle, upar-neeche sidhi line nahi.
- Wazan dikhao: jis haath par tika hai wo zameen/sathah par pehle jame (plant) hua; kandha us taraf jhuke; sar usi ke upar balance mein.
- Negative space (body aur haath ke beech khali jagah) saaf dikhe; par pose balanced bhi lage, ek taraf bharkar nahi.
- Acting dialogue ke bhaav se mile: ek sa bhaav poore dialogue mein (jaise vyangya ya gussa) ho toh body ke chhote tez/ya dheere harkat bhi usi ke hisaab se; bhaav ka jhootha badlav na daalo.
- Har harkat ek hi "formula" (pose → anticipation → overshoot → settle) na ho; kuch harkat seedhi, kuch ruki hui, taaki roboti na lage.
- Aankhon ki palak seedhi ya ek taraf jhuki rakho (gol/oval nahi); munh mein ek taraf ka kona thoda uthao (chehra ek taraf se khulta hai).

### YouTube transcripts se aur seekha (21 Nov 2026): Doodley (legs/weight), Aaron Blaise (Disney, dialogue), mouth shapes, anticipation, timing & spacing
**Wazan aur paer (Doodley):**
- Paer zameen par "jame" rahein (2D mein ise feet register karna kehte hain): jab tak chhalaang na lage paer apni jagah se na khiske, nahi toh wazan chala jata hai.
- Bhaari/bada character: chhalaang se pehle bada wind-up, aur dheema; jitna bada, utni dheemi harkat.
- Chalna = aage ki taraf girna, paer har baar sambhal lete hain; up pose par sabse upar, contact par girna.
- Contact: aage ka paer seedha aur edi pehle, peeche ka mudha. Down: aage ka paer poora zameen par. Passing: ek paer doosre ko paar karta hai.
- Kamar (hips) paer ke ulte: jo paer uthta hai uski taraf ka kamar kinara neeche; passing par seedhi, contact par ulti taraf. Kamar side-to-side bhi hilti hai (figure-8 jaisi, upar-neeche + side).
- Paer zameen se uthte waqt edi pehle (foot roll: edi uthe, panje ki gaand par ghume). Paer ki raftaar zameen chhoone tak barabar rahe (ease-in na karo).
- Upar ka badan paer se ulta: haath paer ke ulte, seena kamar ke ulta ghume. Kabhi haath-paer ek hi taraf nahi.
- Mizaaj chal se: gussa = badan aage, chauda kadam; garv/khushi = badan peeche, seena khula; sidha-sadha adhikari = ekdum kendra; nasha/beemari = kendra idhar-udhar. Jis taraf ja raha ho usse mu mod lo toh shak/darr dikhe.
**Bolna (Aaron Blaise):**
- Munh ka shape awaaz se 2 se 4 frame PEHLE (insaan pehle munh banata hai phir awaaz aati hai). Poora vaaky shuru hone se pehle munh 16-24 frame pehle khulne lage (bolne ki taiyari).
- Har aawaz ka shape mat banao: bas accent par banao. Zyadatar shabdon mein munh ek shape se doosre mein behta hai. "I don't have any shoes" jaise vaaky mein sirf ~4 shape kaafi.
- Muppets jaisa: sirf khula/band bhi accents par theek baithe toh lip-sync achha lagta hai. Baaki shape (f, v, o) upar ki sajaavat hai.
- Munh ke shape: a/e = chauda munh, oo/o = gol gaanth, b/m/p = honth bilkul band (dabe hue), f/v = upar ka dant neeche ke honth par, l = jeebh upar. Bhaav ke saath shape badal jata hai (gussa = dant kase).
**Taiyari (anticipation):** badi harkat se pehle chhoti ulti harkat (baseball swing se pehle haath peeche, kudne se pehle jhukna). Harkat jitni tez, taiyari utni zyada. Subtle bhi: aankh pehle, sar baad mein. Bojh uthane se pehle lambi saans, seena phulao. Taiyari se bhaar (power) aur irada dikhta hai.
**Timing aur spacing:** timing = drawing kab (kaun sa frame), spacing = kahan. 24 fps film; "twos" = har drawing 2 frame (12 drawings/sec) kaam aadha, achha chalta hai; tez harkat (daud) ones par. Barabar doori ka beech wala frame mat rakho, shuru/ant ke paas rakho (slow in/out).
**Pose to pose:** pehle badi pose (shuru, beech, ant), phir beech ke breakdown/inbetween (zyadatar kaam ke liye theek); straight-ahead mein size/jagah badalne ka khatra.

### Poora padha: baaki transcripts ka saar (21 Nov 2026)
**Chalna/daudna/khade rehna (Doodley):**
- Hamesha kam se kam EK paer zameen par (chalte/ladkhadate waqt bhi); dono paer hawa mein sirf daudte (run) waqt, jo "up" pose mein hota hai. Dono hawa mein bina wajah ke ho toh wazan-santulan galat lagta hai.
- Daud: paer zyada door, badan zyada upar, down par bada gira, haath andar ki taraf santulan banate hain; paer ka raasta bhi 8 ki shakl banata hai. Koi kyun daud raha hai (darr/jaldi) wo pose mein dikhao.
- Chalne ka mizaaj: bada kadam jhoolta = aaram-pasand; patakna = gussa; panjon par = nazuk/chup chaap; dheere uthana = chup chaap/dara hua.
- Khade rehna: paer thode bahar, ghutne thoda mudhe (neutral). Kuch der baad wazan ek paer se doosre par jaye (idle loop) — isse chup khada character "jinda" lagta hai.
- Santulan khona: tezi se paer badalna, ghabrahat mein; paer ka sthan kendra (center of gravity) ke saath badle: jhukao toh paer us taraf.
**Cut-out (BaM) walk:** 10 drawings ek chakkar, twos par ~20 frame. Badan ko ek "symbol" bana kar upar-neeche chalao, har pose alag mat banao. Haath beech mein tez, mod par dheere (spacing). Sar thoda offset (der se) taaki badan ke upar uchhle. Sirf contact aur passing sabse zaroori. Dost se dikhao, feedback lo.
**Bolna, practical (Dong, Japani animation):**
- Teen munh: band, aadha khula, poora khula (aadha khula beech ka frame hota hai). Munh alag layer par, baaki chehra rukha (held).
- Timing: shabd kab shuru, kitne frame (jaise "no" ~6 frame, "I" ~12). Munh ko twos ya threes par chalao.
- Bade/josheele bolne par munh ka shape 8-16 frame pehle bana do; chhoti baat-cheet mein 2-4 frame pehle.
- Poore badan ko bhi munh ke saath hilao: poora khula shape par sar thoda upar, aankhen thodi badi, baal phaile, seena upar, haath neeche, mutthi hilao.
- Bolte hue sar mudna ho toh mudne ke beech aankhen band (palak), phir sar poora mud kar munh ke shape chalu. Beech ke frame mein bhi munh ka shape likh do.
**Timing aur spacing (6UXjRCORV44):**
- Do tarah ki gati: barabar (har frame ki doori same) aur tezi/ dheeme hona (doori badhti/ghat-ti). Beech ke frame banane ke 3 tareeke: halves (aadhi doori), thirds (ek tihai, tez-tarra), favors (thoda sa manzil ki taraf, sabse jhatke-daar).
- Vaktu kaise tay karo: wo harkat khud kar ke stopwatch se naapo; seconds x fps = frame (24 fps par ~1 sec = 24 frame).
- Har badi pose ke beech ek chart: ease in, ease out, ya dono, ya seedha.
- Animation theek na lage toh aksar timing/spacing ka masla hota hai.
**Pose to pose vs straight ahead:** pose to pose (key, breakdown, phir inbetween) kam galti (size/jagah nahi badalti), time bachta hai; straight ahead mein jaan/jaadu par bhatakne ka khatra. Computer tween (puppet rig) mein bhi easing curve (slow-in/out) manao warna doori barabar aur seedhi line ban jati hai; squash/stretch alag key se do.

## Puppet jaisa na lage (24 Nov 2026, user ki shikayat: "ungali nhi hai, jaan nhi hai")
- **Haath mein ungliyan:** gol goley nahi. `draw_hand` (template/lib/chars.py): relaxed (ungli-rekha + angootha), open (khuli hatheli, bless/raise), point (ek ungli), fist (angry), join (pranam). Engine pose se apne aap chunta hai (`HANDS`, tools/engine/draw.py).
- **Jaan:** har character PNG ke upar saans (halka upar-neeche phulna), dheema wazan-hilna (+-0.5 degree), aur bolte waqt har ~0.6 sec par chhota nod (build.py, "life" block). Paer zameen par tike rehte hain (origin kamar/paer).
- Dikkat dikhe (chaadar jaisa hilna, paer uthna) toh amplitude build.py mein kam karo, band mat karo.

## Insaan jaisa roop (24 Nov 2026, dusri shikayat: "realistic nahi, haath-pair, ungali, body language")
- Haath-pair ab nali jaise nahi: `tlimb` (template/lib/chars.py) — kandhe se kalai tak patle hote, kohni/pindli par halka ubhaar, ek saaf outline. Kandhe .31u -> kohni .24u -> kalai .15u; pair .38u -> .19u.
- Haath: hatheli + 4 alag ungliyan + angootha (relaxed/open/point/fist/join). Paon: chappal ka talwa + paon + 5 ungliyan, thoda bahar ki taraf mude, ek pair par wazan (thoda asymmetric).
- Sir: jo kisi aur ki taraf dekh raha ho (look |0.4| se zyada) uska chehra 3/4 mudta hai (engine `turn`), sirf putli nahi.
- Aaram ke haath ek jaise nahi: 3 tareeke (latke, aage dheele, ek haath thoda aage) character ke hisaab se.

## Insaan kaise bolta hai (24 Nov 2026, padhai se) — har video par lagta hai
- Bolte waqt haath neeche latakte nahi: forearm belly/chest tak UTHTE hain (bolne se pehle uthte, aakhri shabd ke baad utarte). `STYLES[...]["talkel"]` = kitna uthe (Lakshman zyada, Vasishtha kam).
- Gesture ke 5 prakaar (McNeill): iconic (cheez dikhana), metaphoric (vichaar), deictic (ishara/pointing), pragmatic (baat dena/rokna), beat (shabdon ke zor par chhoti jhatak). Beat sabse aam hai: ek forearm ki chhoti flick, dono haath baari-baari.
- Animation niyam: anticipation (harkat se pehle halka peeche/neeche), follow-through + overlapping (sharir pehle, haath, phir sir, kuch der se), slow-in/slow-out, arcs. Sir har baat par alag se thoda jhukta hai (`head_js`).
- Koi cheez ek saath nahi rukti; dono haath ek jaise nahi hilte; har character ki apni matra (`nod`, `talkel`, `gs`).
- Jod (kohni) par ring/outline nahi: `tlimb(..., open_start=True)`; haath chehre jitna lamba (draw_hand scale 1.28).
