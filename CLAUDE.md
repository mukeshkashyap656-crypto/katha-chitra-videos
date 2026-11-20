# Katha Chitra — Ramayan videos (GitHub par apne aap)

User se Hinglish mein, aam bolchaal ke shabdon mein baat karo. Memory ke saare Ramayan niyam (Valmiki, character bible, logo, subscribe widget, director check, delivery) yahan bhi lagte hain.

## Folder
- `template/` — Ramayan video sancha (pehle Drive par tha): setup.sh, character kit (`lib/`), Bhag 4 ke UDAHARAN `draw_assets.py` / `build_episode.py`, logo, frame, purane sound.
- `sfx/` — 135 free CC0 sound effects (SFX Kit, wyzowl): whoosh, cinematic hit, boom, impact, shimmer, riser, click, notification. Kaunsi awaaz kab: `sfx/catalogue_full.md`. Credit ki zaroorat nahi.
- `sfx/openverse/` — Openverse se laayi CC0 asli awaazein (jungle, ullu, dhol...), `credits.json` ke saath.
- `tools/make_voice.py` — Madhur awaaz + har shabd ka time. GitHub ka computer seedha Microsoft ki awaaz tak pahunch jaata hai, Composio/Drive ki zaroorat nahi.
- `tools/make_episode.sh` — poora episode: awaaz → chitra → HyperFrames render → cover pehle 0.1 sec → `out/<NAME>.mp4`, `out/<COVER>.jpg`, `out/check_sheet.jpg`.
- `plans/` — user se pakke hue episode plan (shot list + lines). Naya episode banane se pehle yahan dekho.
- `episodes/<bhagN>/` — har episode ka folder: `episode.json` (NAME, COVER_NAME, LINES) + episode ke apne `draw_assets.py`, `build_episode.py` (template se copy karke badle hue).

## Naya episode kaise
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
