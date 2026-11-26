# Blog bot ki seekh (owner ki "Google Blogger Guide", 26 Nov 2026, Google ke niyam se milaakar)

Bot har post likhne se pehle sirf "SEEKH SHURU" aur "SEEKH KHATAM" ke beech ki lines padhta hai. Nayi seekh wahin jodo.

<!-- SEEKH SHURU -->
- Heading post ka asli saar bataye. Zaroori baat chhupakar jigyasa paida mat karo; sansani, gussa ya "jaankar hairan" jaisi bhasha nahi.
- Vishay taaza ho aur abhi logon ke kaam ka ho.
- Sirf khabar dobara mat likho: apni taraf se saaf samjhao ki iska padhne wale par kya asar hai aur use kya karna chahiye. Naya tathya mat banao.
- Lambai ka koi tay lakshya nahi: sawaal ka poora jawab do, bharaav aur dohraav mat karo.
- Ek hi shabd ya vaakyansh baar-baar thoons kar mat likho.
- description lagbhag 150 akshar ka saaf saar ho.
- image_query aur photo_queries post ke vishay se judi hon; aisi photo khojo jisme bada likha text ya logo na ho.
- Heading aur cover photo jo vaada karein, wo cheez lekh ke andar saaf mile.
- Sarkari yojana, naukri ya pariksha ki khabar ho to rajya ya vibhag ka naam saaf likho aur batao ki ye kiske liye hai.
- body_html mein har h3 subheading ke shuru mein usi vishay se juda ek icon (emoji) lagao; icon ki bharmaar nahi.
- image_query aur photo_queries usi cheez ki asli photo maangein jis par lekh hai; wahi cheez na mile to vishay se judi asli photo, aur use us cheez ki photo mat batao.
- Post kisi app, brand ya cheez par ho (jaise WhatsApp) to usi ka icon aur usi se judi asli photo lagao; image_query aur photo_queries mein uska naam zaroor ho. Bejod photo se behtar hai post rokna.
- Har post par uske vishay ka icon ho, sirf app wali post par nahi: shuru mein ek bada vishay-icon (app/brand ho to uska asli official icon, warna sahi emoji) aur har h3 par us hisse se juda icon.
- Roz alag vishay: pichhli 3 post wala vishay aur pichhli 5 post wali cheez ya brand dobara mat lo.
- Kai phone/product wali post mein har ek ka usi exact model ka real visual ho (free licence photo, warna company ke official YouTube channel ki video, warna official page ka link). Amazon, Flipkart ya Google se photo utha kar nahi.
<!-- SEEKH KHATAM -->

## Code khud lagata hai
- Cover ke liye 1200px ya usse chaudi asli photo ko pehle chuna jaata hai (Google Discover ki sifarish). Aisi na mile to pehli asli photo lagti hai aur log mein likha jaata hai.

## Guide ki ye baatein bot ke niyam NAHI banin
- "600-1000 shabd": Google kehta hai uski koi pasandida shabd-ginti nahi hai. Zabardasti lamba likhne se bharaav aur galti ka khatra.
- "AdSense ke liye 20-25 post": AdSense ke eligibility page par post ki koi ginti nahi di. Maulik aur kaam ka content, niyam-paalan, 18+ aur site ke code tak pahunch likhi hai.
- "Canva ya khud banayi tasveer": owner ka niyam sirf asli photo hai.
- YouTube channels: bot videos nahi dekhta; unse kuch seekhne ka dawa nahi.
- Theme, domain, Search Console, robots, legal pages, Web Stories: ye blog ki setting ya alag kaam hain, post likhne wala bot inhe nahi karta.
- Chhota English permalink: bot ke bhejne wale raaste se permalink set nahi hota.

## YouTube se seekh (26 Nov 2026)
Padhi gayi: Satish K Videos, "50k Daily Traffic From Google Discover" (youtube.com/watch?v=fwdzihbUn98, 3 saal purani), poori likhi baatein (transcript).
- Li: heading/photo aakarshak par lekh se mel khati; rajya-wise yojana/pariksha jaisi khabar saaf likhna.
- Insaan ke karne ki (bot nahi): apni nayi post apne WhatsApp/Telegram channel par daalna, site ko phone par tez rakhna, lagataar post karna.
- Nahi li: "bahar se traffic bhejo to Discover pakka" (ek vyakti ka tajurba, Google ne aisa vaada nahi kiya); "AMP zaroori" (Google ke Discover page mein AMP sirf ek raasta hai); paid notification tool (video mein affiliate link tha); video ka "sona sasta, jaldi dekhein warna pachhtayenge" jaisa udaharan (clickbait).
- Baaki guide ke link: @ISHANGURU aur @mybigguide ke pate par "404 Not Found" aaya; @SaddamKassim ka page khaali khula. Inse kuch nahi seekha gaya.

## Khabar Saathi (blog ka assistant) ke niyam

**User ke tay niyam (26 Nov 2026)**
- Assistant ki ek hi awaaz: Piper Hindi `pratham` ki recording. Phone/browser ki awaaz (`speechSynthesis`) ya koi doosri awaaz kabhi nahi.
- Har page khulte hi samay ke hisab se greeting: "गुड मॉर्निंग सर / गुड आफ़्टरनून सर / गुड ईवनिंग सर", raat ko "नमस्ते सर"।
- "samay kya hua" wala option nahi.
- Mic ek baar dabane par baat-cheet chalti rahe; sawaal ka jawab turant.

**Files**
- Code: `blog/gadget/khabar_saathi.html`. Badlav ke baad `python3 blog/gadget/make_gadget.py` chalao; blog par `khabar_saathi_blogger.txt` jata hai (Layout > pehla HTML/JavaScript gadget). Repo mein badalne se live blog apne aap NAHI badalta.
- Recording: `blog/awaaz_banao.py` banata hai; mp3 aur `list.json` branch `blog-awaaz` mein. `list.json` ka `base` us commit ka pata hai jisme mp3 hain.
- Gadget ka koi tay jawab badlo to `awaaz_banao.py` ki `TAY` list bhi badlo. `norm/code/sentences` dono jagah ek jaise rahein.
- Nayi post ki recording abhi apne aap NAHI banti. Jab tak na bane, assistant likha jawab dikhata hai aur batata hai ki awaaz tayyar nahi.

**Takneeki seekh**
- Blogger gadget script mein Hindi/emoji seedhe likhne par live blog par `&#...;` dikhta hai; isliye build sirf ASCII (\uXXXX) banata hai.
- Phone bina chhue awaaz rok sakta hai; tab "ek baar chhuein" ka ishara dikhe.

**Suraksha (hamesha)**
- Koi key, password, token ya secret link code, log, issue ya chat mein nahi.
- Apni permission badhana, naya apne-aap chalne wala kaam jodna, ya secret badalna: sirf user ki saaf haan ke baad.
- Awaaz ki shart CC BY-NC-SA 4.0 (bina kamai wala istemaal): blog par ads/kamai shuru hone se pehle yeh awaaz hatani/badalni hai.
