# Scene engine — episode sirf list se (code nahi)

Naya episode = sirf ek file `episodes/bhagN/episode.json`. Usme `SHOTS` ho to video system apne aap
`tools/engine/` se chitra, awaaz, camera, subtitle, logo, subscribe widget aur cover bana deta hai.
Jaanch: `python3 tools/engine/spec.py episodes/bhagN/episode.json` → "OK" ya galtiyon ki list.
Poora udaharan: `episodes/bhag6/episode.json`.

## Keys
| key | kya |
|---|---|
| `NAME` | `Ramayan_BhagN_<Title_Words>` (video file ka naam) |
| `COVER_NAME` | `Ramayan_BhagN_Cover` |
| `BHAG` | number |
| `QUESTION` | upar title box ka sawaal (Hindi, chhota) |
| `LINES` | `id: [hindi text, rate, pitch]` — kram se. Kathavachak `n1, n2...` `"+0%","+0Hz"`; Ram `"+2%","+10Hz"`; Vishwamitra `"-12%","-16Hz"`; Lakshman `"+0%","+4Hz"`; devta `"-15%","-25Hz"`; rakshas `"-10%","-30Hz"`. Aakhri line kathavachak ki: agle bhaag ka sawaal + "कमेंट में लिखिए: जय श्री राम" |
| `SPEAKER` | `line id: character` (kathavachak wali lines mat likho) |
| `KEYWORDS` | `line id: [1-2 khaas shabd]` — subtitle mein peele |
| `NEW_CHARS` | naya character (neeche) |
| `SHOTS` | shot list (neeche) |
| `COVER` | `{"bg": ..., "tag": "chhoti line", "cast": [1-2 characters]}` |
| `VERSION` | sudhaar par 1 badhao |

## SHOTS — har shot
`{"line": "vm1", "bg": "cloudvan", "cam": "auto", "mood": "none", "chip": "2-3 shabd", "at_word": "...", "cast": [...]}`
- `line`: kaunsi line chal rahi hai. Ek line ke kai shot ho sakte hain; doosra shot `at_word` (us line ka koi shabd) se shuru hota hai, jaise naam pukaarte hi cut.
- `bg`: `morning` (subah ka jungle), `cloudvan` (pahad ke paas baadal jaisa van), `divine` (sunehra aakash, devta/avatar), `ghorvan` (ghana andhera jungle), `ashram` (ashram + yagya kund), `river` (nadi kinara, naav), `palace` (raj-darbar, gaddi + chhatra).
- `cam`: `auto` (khud tay karega) | `wide` (sab poore) | `speaker` (bolne wale ka close-up, padosi poora bahar) | `two` (bolne wala + paas wala).
- `mood` (rang se bhaav): `none, joy, sorrow, anger, fear, wonder, night`. anger/fear par dhol, wonder par chamak ki awaaz apne aap.
- `chip`: hisse ki chhoti Hindi heading (optional).
- `cast`: 0-4 log: `{"who": "ram", "x": 620, "pose": "stand", "face": "neutral", "look": "auto"}`
  - `x`: 150-1210 (beech 680). Do logon mein kam se kam 260 ka faasla (bade devta/rakshas ke saath 330) — koi kisi par na chadhe.
  - `pose`: `stand, namaste, talk, bless, point, raise, walk (+ "to_x"), sit, bow, angry`.
  - `face`: `neutral, smile, joy, sad, worry, angry, firm, stern, shock` — kahani ke us pal ke hisaab se, peechhe walon ka bhi.
  - `look`: `auto` (bolne wale ki taraf) | `left` | `right` | `front`.
  - `shadow: true` — rakshas pehli baar: kaali parchhai + laal aankhen. Agle shot mein bina shadow ke dikhao.

## Characters (pehle se bane — roop character bible wala, mat badlo)
`ram, lakshman, vishwamitra, vasishtha, dasharatha, rishi1` (sleti jata, bhagwa), `rishi2` (kaali jata, safed),
`mantri, darbari1-4, maricha, subahu` (rakshas: bade, seeng, daant, kaali-laal chamak).

## NEW_CHARS — naya character (roop Valmiki se tay karke)
`"vaman": {"name": "वामन", "kind": "m", "child": true, "skin": "#3a5aa0", "hair": "#140c08", "tunic": "#f2c230", "sash": "#f6f0e2", "upper": "#f2c230", "lower": "#f2c230", "hem": "#e8902a", "bare": true, "skirt": 1.3, "kamandalu": true, "tilak": true, "glow": "gold"}`
- `kind`: `m` / `f` (f ke liye `saree`, `blouse`, `border` rang). `name` Hindi mein zaroori.
- Devta: `"big": true, "glow": "gold"`. Rakshas: `"big": true, "glow": "dark", "rakshas": true`. Insaan: big/glow nahi (sab insaan ek size, sir ke peechhe chamak nahi).
- Aur cheezein: `crown, jewel, beard, mous, jatabun, tilak, mala, kamandalu, ajina` (mrigchhala rang), `tall, build, belly, age, fw, fh`.
