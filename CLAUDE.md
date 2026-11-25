# Katha Chitra — Ramayan videos (GitHub par apne aap)

> Kahani ka niyam 26 Nov 2026 ko badla hai: NIYAM.md section 2 dekho (wahi sabse upar).

User se Hinglish mein, aam bolchaal ke shabdon mein baat karo. Memory ke saare Ramayan niyam (Valmiki, character bible, logo, subscribe widget, director check, delivery) yahan bhi lagte hain.

## Folder
- `template/` — Ramayan video sancha (pehle Drive par tha): setup.sh, character kit (`lib/`), Bhag 4 ke UDAHARAN `draw_assets.py` / `build_episode.py`, logo, frame, purane sound.
- `sfx/` — 135 free CC0 sound effects (SFX Kit, wyzowl): whoosh, cinematic hit, boom, impact, shimmer, riser, click, notification. Kaunsi awaaz kab: `sfx/catalogue_full.md`. Credit ki zaroorat nahi.
- `sfx/openverse/` — Openverse se laayi CC0 asli awaazein (jungle, ullu, dhol...), `credits.json` ke saath.
- `tools/make_voice.py` — kathavachak Adam, baaki kirdaar free awaaz (NIYAM.md) + har shabd ka time. GitHub ka computer seedha Microsoft ki awaaz tak pahunch jaata hai, Composio/Drive ki zaroorat nahi.
- `tools/make_episode.sh` — poora episode: awaaz → chitra → HyperFrames render → cover pehle 0.1 sec → `out/<NAME>.mp4`, `out/<COVER>.jpg`, `out/check_sheet.jpg`.
- `plans/` — user se pakke hue episode plan (shot list + lines). Naya episode banane se pehle yahan dekho.
- `episodes/<bhagN>/` — har episode ka folder: `episode.json` (NAME, COVER_NAME, LINES) + episode ke apne `draw_assets.py`, `build_episode.py` (template se copy karke badle hue).

## Scene engine (naya tareeka, code nahi)
- Naya episode = sirf `episodes/bhagN/episode.json` mein `SHOTS` wali list (format: `tools/engine/README.md`, udaharan `episodes/bhag6/episode.json`).
- `tools/make_episode.sh` list dekhte hi `tools/engine/draw.py` + `build.py` chalata hai: characters, background, camera (film ke niyam: sir ke upar jagah, close-up mein padosi bahar, lamba shot 2-3 sec ke tukdon mein), mood rang, chip, karaoke subtitle, logo, subscribe widget (subtitle box ke upar), cover.
- Jaanch: `python3 tools/engine/spec.py episodes/bhagN/episode.json`. Naya background/pose/character sancha mein jodna ho to `tools/engine/` badlo (tab VERSION badha ke render).

## Naya episode kaise (purana tareeka, episode ki apni scripts)
1. Valmiki se scene tay karo, shot list user ko dikhao (pehle tay, phir banao).
2. `episodes/bhagN/` banao: episode.json + dono script (template ke udaharan se copy). Scripts `template/lib` se import karti hain (PYTHONPATH apne aap lagta hai).
3. Branch `auto-video` (ya koi bhi branch) par commit + push. `Make Ramayan video` workflow apne aap chalta hai (~5 min).
4. `gh run watch <id>` se intezaar, phir `git fetch --depth 1 origin render-bhagN` + `git archive FETCH_HEAD | tar -x -C <dir>` se MP4, cover aur check sheet laao (Actions artifact ka download sandbox mein block hai). Sirf tools badle hon toh episode.json mein VERSION badha ke push karo, warna run nahi chalega.
5. Director check (check_sheet + zoom), kami ho toh theek karke dobara push. Phir chat mein MP4 + cover ek saath bhejo.

## Awaazein laana
Actions → "Fetch free CC0 sounds (Openverse)" → Run workflow → jo awaaz chahiye likho. Sirf CC0 aati hain.

## Niyam aur free AI Helper
- `NIYAM.md` — Katha Chitra ke saare niyam ek jagah (kisi bhi AI ko do). Naya niyam bane toh yahan bhi jodo.
- `tools/ramayan_ai.py` + `.github/workflows/ai_helper.yml` (main branch par bhi) — free Gemini helper: Issue/comment mein `@ai <kaam>`. Har issue ki branch `ai/issue-N`, `ai_state.json` mein us issue ka episode. Video render ka intezaar karke link + AI director check issue mein deta hai, fail ho toh 3 baar tak khud theek karta hai.
- Katha (auto Bhakti Shorts, `auto-youtube` repo) alag channel hai — use yahan mat milao.

## Naya (21 Nov 2026): zyada smart helper
- `tools/machine_checks.py` — video par sachchi ginti (kaali screen, ruka video, lambi khamoshi, awaaz ka zor). `make_episode.sh` har video ke saath `machine_report.json/.txt` banata hai; kaali/ruki screen ya awaaz ki galti = seedha FAIL (niyam 5 / 8).
- Review ab ASLI video dekhta-sunta hai (`watch_video`, Gemini Files API, free): bol, subtitle ka mel, dheemi line, jhatke. 2+ pakki dikkat = FAIL + khud sudhaar; sirf 1 = chetavni.
- `tools/viral_radar.py` — episode se pehle free signals (YouTube autocomplete, Google Trends India, `stats/STATS.md`) dekhkar sabse zordaar pehla sawaal chunta hai (`plans/radar/bhagN.json`). Kahani nahi badalta. Kuch na chale toh chup-chaap chhod deta hai.
- Free AI sahare: Gemini (model list khud dhundhta hai) -> OpenRouter -> Cloudflare -> Groq -> Cerebras -> Mistral -> SambaNova -> NVIDIA -> Cohere -> HuggingFace. Har ek ki key GitHub secret mein daaloge tabhi chalta hai (GROQ_API_KEY, CEREBRAS_API_KEY, MISTRAL_API_KEY, SAMBANOVA_API_KEY, NVIDIA_API_KEY). Model ka naam badle toh secret `<NAAM>_MODELS` ya khud-khoj.
- Code ki azadi (21 Nov 2026): helper engine ka code (`tools/engine`, `template/lib`, `episodes/<n>/*.py`) aur `SEEKH.md` bhi badal sakta hai ("need_code" -> engine source dekhkar chhote edits). Guard: sirf issue ki branch par; naye code mein network/secret/git/eval mana (apne aap rad); render wale computer par koi secret nahi. PASS ke baad hi shared `auto-video` mein jaata hai (sabhi purane episodes ki spec jaanch, `engine-backup-<tarikh>` tag, auto-video beech mein aage badha ho toh nahi). Workflows, scripts/, NIYAM.md, VIRAL.md, ramayan_ai.py khud helper nahi badal sakta. Galti nikle toh `git checkout engine-backup-<tarikh>` se wapas.
- AI jawab ki kul samay-seema 5 minute; uske baad kaam subah wali queue mein.
- Poori azadi (21 Nov 2026, owner ka hukm): helper owner se kabhi OK ya sawaal nahi poochhta; khud soch-samajhkar tay karta hai, maanyataayein summary mein likhta hai, ek hi baar mein plan + episode banata hai. Sudhaar ke round 5-5 tak.

## Naya (21 Nov 2026, shaam): kabhi na rukne wala + roz ka report
- Gemini ab mushkil kaam (episode likhna, review, video dekhna) ke liye pehle "pro" model, phir flash (model list khud dhundhta hai).
- Aakhri sahara `local_ai()` (tools/ramayan_ai.py): jab Gemini + sab free cloud AI fail ho jaayein, GitHub ke computer par Ollama laga kar chhota model (qwen2.5:3b, mushkil kaam par 7b) chalata hai. Koi key/limit nahi, dheema hai. Model badalna ho toh secret/env `LOCAL_MODEL`. Report jaise halke kaam par band (`NO_LOCAL`).
- `python tools/ramayan_ai.py report` + main par `.github/workflows/collect_stats.yml`: roz subah 8:30 IST asli views `stats/STATS.md` mein, phir issue "📊 Roz ka report" mein comment (24 ghante ke run, kaun sa AI chala, queue, views, agle episode ki salaah). Radar `stats/STATS.md` main branch se padhta hai.
