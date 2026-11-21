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
