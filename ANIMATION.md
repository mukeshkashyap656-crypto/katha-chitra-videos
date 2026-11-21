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
