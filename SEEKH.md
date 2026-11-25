# Katha Chitra — Seekh ki Kitaab (ab tak ke saare sudhaar)

Ye wo galtiyan aur sudhaar hain jo pichhle episodes (Bhag 2, 3, 4, 5) mein mile. **Har naye episode par ye sab pehle se lagte hain** (user ne kaha: "har video mein bolna nahi padna chahiye"). NIYAM.md aur VIRAL.md ke saath padho. Naya sudhaar mile toh yahin joddo.

## Hinsa/Harkat (movement)
- Insaan ki body ka poora gyaan BODY.md mein hai (naap, chalna, baithna, pranam, bolna, bhavna, dhanush). Chalna ab 12 frame ka, kamar-kandhe ke twist aur level sar ke saath (template/lib/chars.py).
- Chalte waqt pair baari-baari uthein, fisalna nahi.
- Baitha character pehle dheere-dheere khada ho, phir chale. Mudna aur haath uthana beech ke frames se (aar-paar dhundhla nahi).
- Yagya/puja mein sab aasan par paalthi maar kar kund ke chaaron taraf baithte hain (khade nahi).
- Rishi ko pranam = kamar se jhuk kar haath jod kar (sharir pichkana ya chhota sa sir hilana nahi). Rishi haath utha kar aashirvaad de. Itni jagah ho ki jhukte waqt kisi ko chhuye nahi.
- Ram aur Lakshman dhanush **mutthi mein** pakdein (hawa mein tairta hua nahi), tarkash kandhe ke upar dikhe.
- Ram shaant aur nidar; sawaal poochte waqt bhi dara hua nahi.
- Kahani ki zaroori cheez saaf dikhaao (divya purush dhakkan khol kar kheer dikhaye, phir band kare).

- (24 Nov 2026) Chalna ab engine mein: asli mocap ke 12 frame, side-view, dono haath jhoolte, raftaar se paer match, pahunch ke ruko, phir sar samne. Detail BODY.md "Abhi baaki". Purane episodes ko dobara mat banao.
- Seekh: ARMS list chalte waqt haath dabaa deti thi (haath body se chipak gaye) -> chalte waqt arms=None. Dheemi raftaar + tez chakkar = paer phisalte dikhte hain -> raftaar 3.2*u/sec hi rakho.

- (25 Nov 2026) HAATH: user ne kaha puppet jaisa lagta hai, ungli nahi dikhti. `draw_hand` (template/lib/chars.py) ab poora insaani haath hai: moti 3-jod ungliyan + knuckle line, palm kalaai se chauda, angootha palm se ugta hua, mutthi mein mudi ungliyan, namaste mein gol sire waali patti. Naya haath/pose banao to isi tarah: ek jura hua haath, gol goli + teeli ungliyan nahi. Styles: relaxed/open/point/fist/join. Test: kirdaar par person() se tasveer nikaal kar ungli zoom karke dekho.

## Jagah (background)
- "Ghor van" sach mein andhera aur ghana: bel, ullu, panchhi, kisi jaanwar ki chamakti aankhein; koi chamakdaar phal ke dot nahi. Rakshas ka naam aate hi laal-kaala ho jaaye.
- Peechhe ki cheezein (jaise ullu) poori frame ke andar, kinare par aadhi kati nahi.

## Frame aur camera
- Har insaan poora andar ya poora bahar (aadha kata nahi). Close-up mein sir ke upar jagah (jata/mukut/halo ko upar ka kinara na chhuye), padosi poora bahar.
- Aankhein upar ke teesre hisse par; jis taraf dekh/chal raha ho us taraf zyada jagah.
- Wide ya bada close-up: scene ki zaroorat ke hisaab se (insaan ek jaise size ke dikhein).
- Chip aur subscribe widget kabhi chehre ya pair na dhakein. Chip cut ke saath hat jaaye (agle scene mein dhundhla na ho).

## Subtitle, naam, awaaz
- Karaoke subtitle: poori line halki, har shabd theek bolne ke time par chamke. Purani line (aur bolne wale ka naam) poori hat jaaye tab nayi aaye; naam ki chip aapas mein na takraaye.
- Har line ki awaaz ek barabar zor ki (Vishwamitra/Ram narrator se dheemi na ho). Lambe chup ke gap kaat do.
- Jungle ki awaaz + dhol/whoosh/chamak ke effects (sfx/).
- Subscribe click aur ghanti ka ting sirf aakhir mein, kathan ke upar nahi. Subscribe se pehle koi khaali second nahi: ungli aakhri shabd par aaye.

## Cover
- Cover alag design hota hai (video ka frame nahi): bada chamakta "?", title box, Katha Chitra logo, khaas cheezein beech ke 3:4 hisse mein. Pehle 0.1 sec par lagta hai.

## Jaanch ka tareeka
- Check sheet se shuru karo (har 0.25 sec ka frame); jahan galti dikhe wahan bade size mein dekho: chehre, haath, cheezein, kinare.
- Pichhle version se milao: kuch kharab toh nahi hua?
- Galti mile toh turant theek karo, phir dobara jaancho; PASS hone par hi aage badho.

## Character ke tay roop
NIYAM.md section 4 "Tay roop (character bible)" mein hain. Har character ka alag chehra, sharir aur khade hone ka dhang. Naya character aaye toh uska roop pehle Valmiki se tay karke NEW_CHARS mein joddo, phir har scene mein wahi.
- (24 Nov 2026) Bolte waqt forearm uthao (talkel) + beat flick; sir alag layer se nod/anticipation (nod); kohni par outline ring nahi (open_start); haath chehre jitna. Detail: ANIMATION.md "Insaan kaise bolta hai", NIYAM 17.

- (25 Nov 2026) Poori video dekhe bina PASS/auto-post nahi; adhoori jaanch 'jaanch-baaki' list mein, sirf jaanch dobara.
- (25 Nov 2026) GitHub Models 30 July 2026 ko band ho chuka, chain se hataya. gemini-2.5-pro naye user ke liye band, hataya. Free AI fail ho toh log mein HTTP code aur asli jawab dikhta hai.
- (25 Nov 2026) Viral seekh se film/actor/comedy/AI-tool wale video chhante jaate hain.

- ## Claude jaisa kaam karne ka tareeka (26 Nov 2026, owner ka hukm: "tum jaise kaam karte ho waise sab niyam sikhao")

NIYAM.md ke saare niyam waise hi lagu hain. Neeche kaam karne ka kram hai.

### A. Banane se pehle
1. Valmiki Ramayan ka sarga padho. Kahani mein kuch jodna ya badalna nahi. Paath na mile ya shak ho to andaza mat lagao, dhoondh kar jaancho.
2. Har line ke saamne likho: kaun dikhega, kitne log, sharir ki haalat, kya ho raha hai, chehre ka bhaav. Poora tay hone ke baad hi banao.
3. Har kirdaar aur devta ka roop, rang, kapde pehle se tay roop se lo. Har scene mein wahi rahe.
4. Koi pose ya cheez engine mein na ho to usse milti-julti cheez se kaam mat chalao. Naya pose banao. Na ban sake to owner ko saaf batao.

### B. Scene aur awaaz ka mel
5. "Sau" ya bheed bola jaye to bahut saare log dikhein, sirf ek-do nahi.
6. Sharir mein badlav (kubda, behosh, ghayal, phir se theek) bola jaye to pehle aur baad ka fark saaf dikhe, sirf chehra badalna kaafi nahi.
7. Jiska naam bola jaye (devta, raja, dulha) wo scene mein pehchaan mein aaye.
8. Cover aur title ka sawaal video ke andar dikhaya jaye.
9. Kirdaar gudiya jaise na lagein: poore haath aur ungliyan, jude hue jod, apni alag harkat. Bhaav chehre aur sharir se dikhein, cheezon se nahi.
10. Awaaz: narrator = ElevenLabs Adam; baaki kirdaar = free awaazein. Adam na mile to chupchap awaaz mat badlo, owner ko batao.

### C. Post se pehle jaanch
11. Har line ke samay ka frame nikaalo aur A-2 wali list se ek-ek karke milao. Har line ke aage PASS ya FAIL likho. Ek bhi FAIL ho to video PASS nahi.
12. Sirf score ya "sab theek" par bharosa mat karo. Jo frame mein sach mein dikhe wahi maano.
13. Poori video dekho: overlap, kate hue log, badalta roop, jhatke wali chaal, khali ya kaale frame, subtitle, logo, subscribe widget, awaaz.
14. Galti mile to theek karo, dobara banao aur dobara jaancho. Jo dekh ya sun nahi paaye use PASS mat maano.
15. Pehle se "taiyaar" video bhi post se kaafi pehle isi tarah jaancho.
16. Caption mein ek hi sawaal do baar na ho.
17. YouTube se video ID na mile to "posted" mat maano. Dobara upload se pehle channel par dekho.

### D. Seekhna aur sach batana
18. Har nayi galti ke baad is file mein ek chhoti line jodo: galti, hal, aur agli baar kaise pakdein.
19. Jo kaam nahi hua ya jo tum badal nahi sakte, use "ho gaya" mat likho. Owner ko saaf aur chhote shabdon mein Hinglish mein batao.
20. Ek episode ek hi jagah banao.
