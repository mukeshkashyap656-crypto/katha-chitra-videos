# Katha Chitra — Poori jaankari (KNOWLEDGE.md)

Ye file Claude ke paas jo bhi jaankari hai (owner se baatcheet, channel ka asli data, system ki baatein, seekh) ek jagah deti hai. NIYAM.md = kya banana; VIRAL.md = kaise chale; BODY.md / ANIMATION.md = harkat; SEEKH.md = galtiyan. Ye file un sab ke upar ka poora naksha hai. Naya pakka tathya mile toh yahin joddo. (Koi key/password yahan kabhi nahi likhna.)

## 1. Owner kaun aur kaise kaam karta hai
- Owner mobile phone se kaam karta hai (computer browser nahi). Hinglish (Hindi Roman) mein baat karta hai; jawab bhi Hinglish mein, aam bolchaal ke shabdon mein, technical/product naam nahi.
- Hukm hai: "har video mein bolna na pade" — koi bhi sudhaar ek video ke liye bola gaya ho toh wo saare video (aage ke) par lagta hai, bina dobara bole.
- Pehle scene tay karo (shot list), phir banao. Mushkil ya anjaan cheez mein web par khoj kar dekho. Kuch mumkin na ho toh options dekh kar khud tay karo.
- Kharcha: hamesha free tools pehle; paisa lage toh pehle batao aur owner ka saaf "haan" lo. Sabse kam usage/credit se kaam karo.
- Purane bane episodes (Bhag 2-6) dobara nahi bante (24 Nov 2026 ka hukm). Dusre chat mein ban rahe episode (Bhag 8) ko mat chhedo.
- Helper ke liye: jis cheez mein dikkat aaye uske bahut saare vikalp (fallback) hone chahiye (AI, retry, queue time).

## 2. Channel aur system ka nakshaa
- Channel: Katha Chitra (@kathachitra_123), Valmiki Ramayan Shorts, 13 Nov 2026 ko bana; Bhag 1 19 Nov ko public. Instagram: @kathachitra56 (sirf naye Ramayan Reels rakhne hain, purane hata do). Do aur channel alag hain: Katha (auto Bhakti Katha Shorts, repo auto-youtube) aur M.K.Gaming (Free Fire/gaming). Inhe Katha Chitra se mat milao.
- Repo: katha-chitra-videos (25 Nov 2026 se **public**: key/password kabhi file mein nahi). Branch `auto-video` = asli kaam; `main` = scripts/workflows. Voice page: public repo katha-chitra-voice (GitHub Pages), mic se Hindi bolkar "@ai" issue banta hai.
- Posting: naya episode shaam 7 baje IST public; wahi video YouTube Short aur Instagram Reel par. Instagram ka API schedule nahi karta (7 baje ke liye ek-baar ka scheduled task). Instagram raw GitHub link seedha nahi padh pata (504) — pehle file upload karke video_file se Reel banate hain. YouTube par upload private + saada title, phir title/description/tags/schedule Composio/vidIQ se.
- Audience: "not made for kids" pehle se set. Title/tag/comment ke niyam NIYAM.md section 12.
- Apps jude hain Composio ke zariye (YouTube Katha Chitra + M.K.Gaming, Instagram, GitHub, Gemini, Drive) aur vidIQ (free plan, ~150 credit/mahina; credit 0 hon toh 11 Dec 2026 tak wapas nahi). Credit wale vidIQ kaam hafte mein ek baar, kai episodes ek saath. YouTube Data API ka roz ka quota bhar sakta hai (sham tak ruk jaata hai) — tab dobara koshish baad mein, rok ko bypass mat karo.
- Video banne ka rasta: episode.json (SHOTS) -> tools/make_episode.sh -> awaaz (kathavachak Adam, baaki kirdaar free; NIYAM.md) -> chitra (tools/engine) -> HyperFrames render -> machine_checks -> AI director check -> PASS par post (poori video dekhe bina PASS nahi). Render ka branch `render-<naam>`; fetch: `git fetch --depth 1 origin render-<naam>` + `git archive FETCH_HEAD | tar -x`.

## 3. Channel ka asli haal (24 Nov 2026, Studio ka data)
- Pahunch (reach) theek: ~92.8% views Shorts feed se. Dikkat **ruk kar dekhna** (retention): sirf 30.2% log ruke, 69.8% ne swipe kiya; aausat dekhna ~6 sec (video 40-60 sec ka). 0 subscriber kyunki aakhir ke widget tak koi pahunchta nahi.
- Sabse achha video ~472 views, sawaal se shuru hua. Bhag 6 ki pehli line 17 shabd ki thi aur asli chaunkane wali baat line ke end mein — log tab tak chale gaye.
- Isliye: (1) pehli line <=12 shabd, chaunkane wali baat/sawaal pehle shabdon mein; (2) awaaz 0.0-0.3 sec se, pehle 1 sec mein harkat, pehla cut 2.5 sec se pehle; (3) beech (~15-20 sec) mein naya mod/sawaal; (4) subscribe ki baat bhi pehle 6 sec ki tarah chhoti aur seedhi; (5) har episode ke baad Studio ka "Stayed to watch" aur aausat dekhna `stats/STATS.md` mein likho; lakshya 30% se upar, phir 50%. Detail VIRAL.md section 1.
- Viral pattern: ek tarah ke viral Ramayan Shorts ka pattern: upar tika sawaal banner, har 2-3 sec par cut ya camera harkat, shabd-dar-shabd subtitle (khaas shabd peela), har character ki alag awaaz, whoosh/dhol/chamak, takraav + chhote counter (putra 0 -> 4), majboot aakhri line, koi "aapne dekha" wala recap nahi, ~40-60 sec (75 tak). Lekin kahani Valmiki ki hi, viral ke liye bhi Tulsidas ya apni cheez nahi.

## 4. Kahani aur character
- Sirf Valmiki Ramayan (Tulsidas nahi); kahani bilkul waisi, apni taraf se kuch jodna ya badalna nahi; sargas ke kram mein. Har devta/naye character ka roop, rang, kapde pehle Valmiki ke text se tay karo, phir wahi har scene mein.
- Character ke tay roop NIYAM.md section 4 mein: Ram (shyam neela, no halo, pitambar), Lakshman (gora, orange-lal), Dasharatha, Vishwamitra (patla, jata, valkal+mrigchhala, kamandalu), Vasishtha, Maricha/Subahu (rakshas bade, laal-kaali chamak, pehle parchhai + laal aankhein), yagya ke rishi, divya purush (bada, sunehri kirnein). Sab insaan ek size ke; devta/rakshas khaas bade + chamak. Ram-Lakshman insaan hain, sir ke peechhe halo nahi.
- Style: Ramayan ka tay look — maroon-sunehri nakkashi wali border, upar title box "रामायण · भाग X" + bada sawaal, neeche subtitle box (bolne wale ka naam sunehri), sab character badey aur saaf, saaf outline, lok-kala waale rangeen background. Style badalna mana.
- Darbar asli darbar jaisa: ooncha singhasan + chhatra, darbari dono taraf (peechhe ooncha manch), sab alag-alag chehre wale.
- Bhavna chehre aur body se dikhao, cheezon se nahi. Har character (peechhe wale bhi) ka chehra kirdaar aur pal ke hisaab se.
- Story ki zaroori cheezein saaf dikhao; yagya mein sab paalthi maarkar baithte hain; rishi ko pranam kamar se jhuk kar haath jod kar; rishi haath uthakar aashirvaad deta hai.

## 5. Film ke niyam (director ki tarah)
- Shuruaat sawaal ya sabse chaunkane wali baat se. Dhaancha: hook -> peechhe ki baat -> mod -> raaz -> nateeja -> bhavuk aakhri line -> agle bhaag ka sawaal.
- Raftaar scene ke hisaab se: ladai/khulasa tez (1-2 sec shot), dukh/vidaai dheema aur lamba, jagah dikhana chauda aur aaram se, baatcheet mein bolne wale par cut.
- Navras ke rang: khushi garam-chamakdaar, karuna dhundhla-neela, raudra laal, bhay laal-kaala, adbhut sunehra. Aasman ka rang samay badalta hai. Cut match-cut ya halke dissolve se.
- Camera: sir ke upar jagah, aankhein upar ke teesre hisse par, jis taraf dekh/chal raha us taraf zyada jagah, har insaan poora andar ya poora bahar, close-up mein padosi bahar. Chip/subscribe widget chehre ya pair na dhakein; chip cut ke saath hat jaaye.
- Subtitle karaoke: poori line halki, har shabd bolne ke theek time par chamke; purani line (aur naam) poori hat jaaye tab nayi aaye. Har line ki awaaz ek barabar zor ki; lambe chup kaat do; hook line theatrical.
- Aakhir mein chhota modern subscribe widget (logo, SUBSCRIBE, ghanti): ungli click ("click" awaaz) -> "✓ SUBSCRIBED" -> ghanti chamke/hile ("ting-ting"); kathan ke upar nahi, aakhri shabd par ungli aaye, koi khaali second nahi, aakhri frame ghanti ki awaaz tak ruke.
- Logo har video mein dayein chhota, poore video mein. Cover pehle 0.1 sec par; cover alag design (bada chamakta "?", title box, logo, cheezein beech ke 3:4 mein).
- Delivery: naya video + cover ek saath, naam `Ramayan_BhagX_<Title>.mp4` / `Ramayan_BhagX_Cover.jpg`, neeche numbered list. Drive/link nahi. Sirf wahi file jo is baar bani.

## 6. Awaaz
- Awaaz (25 Nov 2026 ka aakhri faisla): sirf kathavachak = Adam, baaki sab kirdaar free awaaz. Script aaj ki saaf bolchaal ki Hindi mein, smooth flow; bhaari kitaabi shabd nahi. Awaaz ke saath jungle/dhol/whoosh sfx (`sfx/`, CC0). Kaun si awaaz kiske liye — owner ko batao.

## 7. Harkat (movement) — ab tak ki seekh
- Mocap (CMU, free) se asli chaal: 12 frame ka chakkar; body har chakkar mein 3.2*u aage (u = oonchai/5) warna paer phisalte hain. Dono haath paer ke ulte (arms=None, ARMS list chalte waqt mat lagao). Rukna asli data se (stop). Mudne mein pehle aankhein, phir sar, phir body.
- Chalte waqt chehra chalne ki disha mein; samne chalne/dekhne wale ke pupil beech mein (look=0), kisi aur ko dekhna ho toh `turn` se sar modo. Camera ki taraf koi nahi dekhta.
- 24 Nov 2026 (branch ai-fix-movement, test `episodes/test_move`): engine mein side-view walk lag gaya (spec.py: 12 walk tasveerein + 3 turn tasveerein; draw.py: walk/side/turn; build.py: raftaar = asli, pahunch kar ruk, phir sar samne). Test frames mein paer, haath, chehra sahi dikhe. Merge `auto-video` mein Bhag 8 ke baad, test render PASS par.
- Baaki: mudna (16_17), baithna-uthna (13_01), jude haath/aashirvaad ka haath, tunic ka halka jhoolna, har character ki alag chaal, samne/door chalna.
- Bolte waqt munh awaaz se 3 frame pehle (LIP_LEAD=3), sirf accents par shape; sar halka nod-tilt.
- Poora detail: BODY.md, BODY_FULL.md, ANIMATION.md (12 principles, 9-point scene check).

## 8. Jaanch aur galtiyan jo pehle hui
- Director check: poora video khud dekho (har 0.25 sec ka frame, chehre/haath/dhanush/kinare zoom), pichhle version se milao, awaaz-subtitle ka mel, level. Galti mile toh turant theek karo, phir dobara jaancho; PASS par hi bhejo.
- Seedhe FAIL: aadha kata insaan; overlap; character ka roop badalna; halo; kaali/ruki screen; subtitle/chip chehre par; logo/widget gayab; awaaz-subtitle mel nahi; Valmiki se alag; cover pehli frame par nahi; hook 12 shabd se lamba (VIRAL.md section 6).
- Pehle ki galtiyan: Vishwamitra/Ram ki awaaz narrator se dheemi; naam chip aapas mein takraana; subscribe se pehle khaali second; ullu aadha frame se bahar; dhanush haath mein nahi tairta; ghor van chamakdaar phal ke dot ke saath (andhera aur ghana hona chahiye); rishi ko pranam sirf sir hilakar; pranam ke waqt haath dhanush par chhoota hua; Bhag 5 purane tareeke ka episode hai (SHOTS nahi), engine spec uspar nahi chalta.
- Galti ka naya sabak: jo cheez "theek hai" bolne se pehle khud frame mein zoom karke dekho; thumbnail par ghalat andaaza lag sakta hai (rishi ka chehra thumbnail mein samne dikha, zoom par mudta nikla).

## 9. Free AI helper (tum khud)
- Tum sirf wahi jaante ho jo in files mein likha hai; har naya niyam/seekh SEEKH.md (ya BODY.md) mein likho taaki agli baar yaad rahe.
- Tum owner se kabhi OK nahi poochhte; khud sochkar tay karo, maanyataayein summary mein likho. Free AI ka silsila: Gemini -> OpenRouter -> Cloudflare -> Groq -> Cerebras -> Mistral -> SambaNova -> NVIDIA -> Cohere -> HuggingFace -> aakhir mein local Ollama. Samay-seema 5 min/jawab; baaki subah ki queue mein.
