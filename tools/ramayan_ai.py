"""
Katha Chitra AI Helper - free. Pehle Gemini, busy ho to OpenRouter ke free AI, phir GitHub Models (koi alag key nahi). Sirf Katha Chitra (Ramayan).

Issue ya comment mein "@ai <kaam>" likho, jaise:
  "@ai Bhag 7 ka plan banao"                 -> plans/ mein shot list + lines (pehle tay, phir banao)
  "@ai plan theek hai, Bhag 7 banao"         -> episodes/bhag7/episode.json (sirf scene ki list), phir video
  "@ai Ram ka chehra chhota hai, theek karo" -> usi issue ki branch par sudhaar + naya video
  "@ai dobara koshish karo"                  -> bina badlaav ke video dobara

AI sirf ek chhoti list (episode.json) likhta hai; video tools/engine/ ka pakka sancha banata hai.
Har issue ki apni branch: ai/issue-<number>. Video ban jaane par link + AI director check issue mein.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

import requests
from google import genai
from google.genai import types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine"))
import spec as SP  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

REPO = os.environ["GITHUB_REPOSITORY"]
MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
MAX_FIX_ROUNDS = 3
STATE = "ai_state.json"
CONTEXT = ["NIYAM.md", "VIRAL.md", "SEEKH.md", "tools/engine/README.md"]


USED = []    # which AI answered (shown under each comment)
LEASE = {}   # branch -> remote commit we started from (safe overwrite of the issue branch)


class Busy(Exception):
    """Saare free AI abhi busy / limit khatam."""


# ---------------- chhote kaam ----------------
def run(args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {r.stderr.strip()[:500]}")
    return r.stdout


def comment(issue, text):
    if USED:
        text += f"\n\n<sub>AI: {USED[-1]} · OpenRouter sahara: {'hai' if os.environ.get('OPENROUTER_API_KEY', '').strip() else 'nahi'}</sub>"
    run(["gh", "issue", "comment", str(issue), "--repo", REPO, "--body", text], check=False)
    print(text)


def checkout_branch(branch):
    """Issue ki branch ho to uspe jao, warna auto-video se nayi banao."""
    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    run(["git", "checkout", "-b", branch])          # always start from the newest auto-video (newest engine + rules)
    if run(["git", "ls-remote", "--heads", "origin", branch]).strip():
        # bring over only this issue's own work: its state, plans and scene-list episodes (never old code)
        run(["git", "fetch", "--depth", "1", "origin", branch])
        LEASE[branch] = run(["git", "rev-parse", "FETCH_HEAD"]).strip()
        old = run(["git", "ls-tree", "-r", "--name-only", "FETCH_HEAD"]).split()
        keep = [f for f in old if f == STATE or f.startswith("plans/") or
                (re.match(r"^episodes/[a-z0-9_]+/episode\.json$", f) and '"SHOTS"' in run(["git", "show", f"FETCH_HEAD:{f}"]))]
        if keep:
            run(["git", "checkout", "FETCH_HEAD", "--"] + keep)


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(st):
    with open(STATE, "w") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)


def context_files():
    """Sirf niyam, sanche ka guide, plans aur episodes ki list (code nahi) -> chhota, tez prompt."""
    files = {}
    paths = CONTEXT + sorted(p for p in run(["git", "ls-files", "plans", "episodes"]).splitlines()
                             if p.endswith((".json", ".md")))
    for p in paths:
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                files[p] = f.read()
    return files


# ---------------- AI: pehle Gemini, busy ho to OpenRouter ke free model ----------------
def gemini(contents, want_json):
    c = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip(), http_options=types.HttpOptions(timeout=120000))
    cfg = types.GenerateContentConfig(temperature=0.3, max_output_tokens=32768,
                                      response_mime_type="application/json" if want_json else None)
    last = None
    for attempt in range(6):          # fail fast when busy; the job is queued for the quiet morning
        m = MODELS[attempt % len(MODELS)]
        try:
            txt = (c.models.generate_content(model=m, contents=contents, config=cfg).text or "").strip()
            if txt:
                print("Jawab:", m); USED.append(m)
                return txt
            raise ValueError("khaali jawab")
        except Exception as e:
            last = e
            busy = any(x in str(e) for x in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "overloaded"))
            w = min(90, (20 if busy else 8) * (attempt + 1))
            print(f"Gemini koshish {attempt + 1} ({m}) nahi chali: {str(e)[:160]}. {w}s baad phir...")
            time.sleep(w)
    raise Busy(f"Gemini: {str(last)[:200]}")


def openrouter_models():
    try:
        data = requests.get("https://openrouter.ai/api/v1/models", timeout=30).json()["data"]
    except Exception:
        return []
    free = [m for m in data if m["id"].endswith(":free") and (m.get("context_length") or 0) >= 60000]
    pref = ("deepseek", "qwen", "gemini", "llama", "mistral")
    free.sort(key=lambda m: next((i for i, p in enumerate(pref) if p in m["id"]), 9))
    return [m["id"] for m in free[:5]]


def openrouter(prompt_text, want_json):
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise Busy("Gemini busy hai aur OpenRouter key nahi hai")
    last = None
    for m in openrouter_models():
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", timeout=300,
                              headers={"Authorization": f"Bearer {key}"},
                              json={"model": m, "temperature": 0.3, "messages": [{"role": "user", "content": prompt_text}],
                                    **({"response_format": {"type": "json_object"}} if want_json else {})})
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt:
                print("Jawab (OpenRouter):", m); USED.append("OpenRouter " + m)
                return txt
        except Exception as e:
            last = e
            print(f"OpenRouter {m} nahi chala: {str(e)[:160]}")
    raise Busy(f"OpenRouter: {str(last)[:200]}")


GH_MODELS = ["openai/gpt-4.1-mini", "openai/gpt-4o-mini", "deepseek/DeepSeek-V3-0324", "meta/Llama-3.3-70B-Instruct"]


def github_models(prompt_text, want_json):
    """Teesra free sahara: GitHub Models (GitHub ka apna token, koi alag key nahi; workflow mein models: read)."""
    tok = os.environ.get("GH_TOKEN", "").strip()
    if not tok:
        raise Busy("GitHub token nahi")
    last = None
    for m in GH_MODELS:
        try:
            r = requests.post("https://models.github.ai/inference/chat/completions", timeout=300,
                              headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                              json={"model": m, "temperature": 0.3, "messages": [{"role": "user", "content": prompt_text}],
                                    **({"response_format": {"type": "json_object"}} if want_json else {})})
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt:
                print("Jawab (GitHub Models):", m); USED.append("GitHub " + m)
                return txt
        except Exception as e:
            last = e
            print(f"GitHub Models {m} nahi chala: {str(e)[:160]}")
    raise Busy(f"GitHub Models: {str(last)[:200]}")


def _openai_style(name, url, key, models, prompt_text, want_json):
    if not key:
        raise Busy(f"{name}: key nahi")
    last = None
    for m in models:
        try:
            r = requests.post(url, timeout=300, headers={"Authorization": f"Bearer {key}"},
                              json={"model": m, "temperature": 0.3,
                                    "messages": [{"role": "user", "content": prompt_text}],
                                    **({"response_format": {"type": "json_object"}} if want_json else {})})
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt:
                print(f"Jawab ({name}):", m); USED.append(f"{name} {m}")
                return txt
        except Exception as e:
            last = e
            print(f"{name} {m} nahi chala: {str(e)[:160]}")
    raise Busy(f"{name}: {str(last)[:200]}")


def groq(p, j):
    return _openai_style("Groq", "https://api.groq.com/openai/v1/chat/completions",
                         os.environ.get("GROQ_API_KEY", "").strip(),
                         ["llama-3.3-70b-versatile", "qwen/qwen3-32b"], p, j)


def cerebras(p, j):
    return _openai_style("Cerebras", "https://api.cerebras.ai/v1/chat/completions",
                         os.environ.get("CEREBRAS_API_KEY", "").strip(), ["llama-3.3-70b"], p, j)


def mistral(p, j):
    return _openai_style("Mistral", "https://api.mistral.ai/v1/chat/completions",
                         os.environ.get("MISTRAL_API_KEY", "").strip(), ["mistral-small-latest"], p, j)


def ask(prompt_text, image=None, want_json=True):
    imgs = image if isinstance(image, (list, tuple)) else ([image] if image else [])
    contents = [types.Part.from_bytes(data=i, mime_type="image/jpeg") for i in imgs] + [prompt_text] if imgs else prompt_text
    chain = [("Gemini", lambda p: gemini(contents if p == prompt_text else p, want_json))]
    if not imgs:   # tasveer sirf Gemini dekh sakta hai
        chain += [("OpenRouter", lambda p: openrouter(p, want_json)),
                  ("GitHub", lambda p: github_models(p, want_json)),
                  ("Groq", lambda p: groq(p, want_json)),
                  ("Cerebras", lambda p: cerebras(p, want_json)),
                  ("Mistral", lambda p: mistral(p, want_json))]
    prompt, errs = prompt_text, []
    for _round in range(2):                      # poori list do baar
        for name, fn in chain:
            try:
                txt = fn(prompt)
            except Exception as e:   # koi bhi dikkat: agle raaste par jao
                errs.append(f"{name}: {str(e)[:60]}"); continue
            if not want_json:
                return txt
            try:
                mt = re.search(r"\{.*\}", txt, re.DOTALL)
                data = json.loads(mt.group(0) if mt else txt)
                if data.get("action") not in ("change", "none"):
                    raise ValueError("action galat")
                data.setdefault("files", []); data.setdefault("summary", ""); data.setdefault("render", False)
                return data
            except ValueError as e:
                errs.append(f"{name}: JSON tooti")
                prompt = (prompt_text + "\n\n# YOUR LAST ANSWER WAS NOT VALID JSON (" + str(e)[:120] +
                          "). Answer again with ONLY valid JSON; escape every double quote inside strings.")
    raise Busy("Saare raaste try kiye: " + " | ".join(errs)[-300:])


RULES = """You are the film director of the "Katha Chitra" YouTube channel (Valmiki Ramayan Shorts in Hindi,
2D Indian folk-art storybook style). NIYAM.md holds EVERY rule of the owner: follow all of them strictly.
Valmiki Ramayan only; nothing added, nothing changed in the story. Hindi lines in today's simple spoken Hindi.

An episode is ONLY data: episodes/<bhagN>/episode.json in the scene-list format of tools/engine/README.md
(example: episodes/bhag6/episode.json). A fixed engine turns it into the video. You never write code.

Reply with ONLY valid JSON:
{"action": "change" | "none",
 "render": true | false,
 "summary": "Hinglish, simple everyday words, short: kya kiya / kya jawab hai / owner ko kya karna hai",
 "files": [{"path": "...", "content": "THE COMPLETE FILE CONTENT"}]}

How to work:
- NEW episode: first a plan only: plans/<bhagN>_PLAN.md (shot list in Hinglish, every shot 2-3 s, who stands where,
  new character looks from Valmiki) + plans/<bhagN>_episode.json (the scene list). Show it in summary and ask
  for OK. Do NOT create episodes/ until the owner says the plan is OK / asks to build ("pehle tay, phir banao").
- BUILD: write episodes/<bhagN>/episode.json (copy the plan's scene list). "render": true.
- FIX a look/render problem: change as little as possible in that episode.json, bump VERSION, "render": true.
- Owner only wants the video made again without changes: "action": "none", "render": true.
- Question only: "action": "none", "render": false, answer in summary.
- Only plans/... and episodes/<name>/episode.json may be written. Always the FULL file.
- Use only backgrounds, poses, faces, moods and characters listed in tools/engine/README.md; a new character goes in
  NEW_CHARS with its look decided from Valmiki. Keep people at least 260 apart (330 with a big devta/rakshas).
"""


def check_changes(changes):
    problems = []
    for it in changes:
        p, c = it.get("path", ""), it.get("content", "")
        ok_path = p.startswith("plans/") or re.match(r"^episodes/[a-z0-9_]+/episode\.json$", p)
        if not ok_path or ".." in p:
            problems.append(f"{p}: sirf plans/ aur episodes/<naam>/episode.json likhne ki ijazat hai (code nahi)")
            continue
        if p.endswith(".json"):
            try:
                j = json.loads(c)
            except ValueError as e:
                problems.append(f"{p}: JSON galat hai: {e}"); continue
            if p.endswith("episode.json") and (p.startswith("episodes/") or "SHOTS" in j):
                with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as t:
                    t.write(c)
                try:
                    problems += [f"{p}: {x}" for x in SP.check(SP.load(t.name))]
                except Exception as e:
                    problems.append(f"{p}: list padh nahi paaye: {e}")
                finally:
                    os.unlink(t.name)
    return problems


def solve(task):
    files = context_files()
    block = "\n\n".join(f"===== FILE: {p} =====\n{c}" for p, c in files.items())
    prompt = f"{RULES}\n\n# FILES\n{block}\n\n# TASK\n{task}"
    for _ in range(3):
        data = ask(prompt)
        if data["action"] != "change" or not data["files"]:
            data["action"] = "none"; data["files"] = []
            return data
        problems = check_changes(data["files"])
        if not problems:
            return data
        print("Jaanch mein galti, dobara:", problems)
        prompt += "\n\n# YOUR ANSWER WAS REJECTED, fix these and answer again:\n- " + "\n- ".join(problems[:30])
    return {"action": "none", "render": False, "files": [],
            "summary": "3 baar koshish ki par har baar list ki jaanch mein galti mili, isliye kuch nahi badla. "
                       "Thoda saaf likh kar dobara `@ai` boliye, ya ye issue Claude chat mein bhejiye."}


def write_files(data):
    eps = set()
    for it in data["files"]:
        d = os.path.dirname(it["path"])
        if d:
            os.makedirs(d, exist_ok=True)
        with open(it["path"], "w", encoding="utf-8") as f:
            f.write(it["content"])
        run(["git", "add", it["path"]])
        if it["path"].startswith("episodes/"):
            eps.add("/".join(it["path"].split("/")[:2]))
    return eps


def start_render(branch, ep):
    """Video ka run shuru karo aur khatam hone tak ruko. (run_id, safal?) lautata hai."""
    q = ["gh", "run", "list", "--repo", REPO, "--workflow", "make-video.yml", "--branch", branch,
         "-L", "1", "--json", "databaseId", "-q", ".[0].databaseId"]
    before = run(q, check=False).strip()
    run(["gh", "workflow", "run", "make-video.yml", "--repo", REPO, "--ref", branch, "-f", f"episode={ep}"])
    run_id = ""
    for _ in range(30):
        time.sleep(10)
        run_id = run(q, check=False).strip()
        if run_id and run_id != before:
            break
    if not run_id or run_id == before:
        raise RuntimeError("Video ka run shuru nahi hua")
    ok = subprocess.run(["gh", "run", "watch", run_id, "--repo", REPO, "--exit-status", "-i", "30"],
                        capture_output=True, text=True).returncode == 0
    return run_id, ok


def commit_push(branch, msg):
    run(["git", "add", STATE])
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
        run(["git", "commit", "-m", msg])
        run(["git", "push", f"--force-with-lease={branch}:{LEASE.get(branch, '')}", "origin", f"HEAD:refs/heads/{branch}"])
        LEASE[branch] = run(["git", "rev-parse", "HEAD"]).strip()   # next push in the same run starts from here


# ---------------- mode: @ai kaam ----------------

# ---------------- roz ki kataar, Valmiki jaanch, apne aap shuru (AUTOPOST) ----------------
def queue_item(bhag):
    try:
        q = json.load(open("plans/STORY_QUEUE.json", encoding="utf-8"))
    except OSError:
        return None
    return next((x for x in q.get("episodes", []) if str(x["bhag"]) == str(bhag)), None)


def title_bhag():
    m = re.match(r"\s*Bhag\s+(\d+)", os.environ.get("ISSUE_TITLE", ""))
    return m.group(1) if m else None


def fetch_valmiki(sargas):
    """Valmiki ke sarga ka paath laane ki koshish (GitHub ka computer internet se jud sakta hai). Na mile toh ''."""
    m = re.match(r"1\.(\d+)(?:-1\.(\d+))?", sargas or "")
    if not m:
        return ""
    lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
    out = []
    for n in range(lo, min(hi, lo + 6) + 1):
        for u in (f"https://www.valmikiramayan.net/utf8/baala/sarga{n}/bala_{n}_prose.htm",
                  f"https://www.valmikiramayan.net/utf8/baala/sarga{n}/baala_{n}_frame.htm"):
            try:
                t = requests.get(u, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
                if t.status_code == 200 and len(t.text) > 800:
                    body = re.sub(r"(?is)<(script|style).*?</\1>", "", t.text)
                    body = re.sub(r"(?s)<[^>]+>", " ", body)
                    out.append(f"--- Sarga 1.{n} ---\n" + re.sub(r"\s+", " ", body)[:6000])
                    break
            except requests.RequestException:
                continue
    return "\n".join(out)


def autopost_brief():
    b = title_bhag()
    if not (autopost_on() and b):
        return ""
    it = queue_item(b) or {}
    text = fetch_valmiki(it.get("sargas", ""))
    st_txt = ("The Valmiki text below is the ONLY source; use nothing else:\n" + text) if text else \
             ("Valmiki's full text could not be fetched. Use only what you are SURE is in Valmiki Ramayan Bala Kanda; "
              "if unsure, leave it out. Do not add anything.")
    return ("\n\nAUTOPOST: the owner already approved everything; the strict director review and the Valmiki check will "
            "judge the result, so do NOT ask for an OK. In ONE answer write plans/bhag{b}_PLAN.md, plans/bhag{b}_episode.json AND "
            "episodes/bhag{b}/episode.json (action change, render true). Episode: Bhag {b}; topic: {t}; Valmiki Bala Kanda "
            "sargas (approx.): {s}. Follow VIRAL.md (hook in the first line, QUESTION banner, scene-wise pace, ending with the "
            "next part's question + comment call) and SEEKH.md. About 35-45 seconds. Story exactly as in Valmiki, nothing added.\n"
            ).format(b=b, t=it.get("topic", "?"), s=it.get("sargas", "?")) + st_txt


def story_check(ep_json, bhag):
    """Valmiki se mel. Sirf PAKKI galti (Valmiki se seedha ulta ya apni taraf se joda hua) maani jaati hai.
    Shuru/aakhir ka sawaal, 'kamment karein: jai shri ram' aur 'agle bhaag' wali lines galti nahi hain."""
    it = queue_item(bhag) or {}
    try:
        lines = json.loads(ep_json).get("LINES", {})
    except ValueError:
        return [{"line": "?", "what": "episode.json padhi nahi gayi", "fix": "episode.json theek karo"}]
    txt = "\n".join(f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in lines.items())
    prompt = ("You are a scholar of Valmiki Ramayan (Bala Kanda only, NOT Tulsidas, NOT TV serials). Below are the narration "
              "lines of a short Hindi video. Topic: {t}; sargas (approx.): {s}.\n"
              "Find ONLY lines that clearly CONTRADICT Valmiki Ramayan or add an event/fact that is certainly NOT in it. "
              "Do NOT flag: simple everyday Hindi wording, the opening hook question, the ending question about the next part, "
              "the 'comment: जय श्री राम' call, short natural dialogue that only restates the story, or anything you are not "
              "100% sure about. Do not think aloud and do not explain; no 'Wait' or 'Let me check'.\n"
              "Reply with ONLY valid JSON, at most 3 items, each 'what' under 25 words: "
              '{{"problems":[{{"line":"<line id>","confidence":"high","what":"Hinglish","fix":"exact change"}}]}}. '
              "If nothing is certainly wrong: {{\"problems\":[]}}\n\nLINES:\n{l}").format(t=it.get("topic", "?"), s=it.get("sargas", "?"), l=txt)
    for _ in range(3):
        raw = ask(prompt, want_json=False)
        mt = re.search(r"\{.*\}", raw, re.DOTALL)
        try:
            items = list(json.loads(mt.group(0) if mt else raw).get("problems") or [])
        except ValueError:
            continue
        return [p for p in items if str(p.get("confidence", "")).lower() == "high"
                and 0 < len(str(p.get("what", ""))) <= 300 and "wait" not in str(p.get("what", "")).lower()][:3]
    return [{"line": "?", "what": "Valmiki jaanch ka jawab samajh nahi aaya", "fix": "line dobara jaancho"}]


def mode_daily():
    """Roz subah: aane wale dino ke bhaag ke issue khud banao aur banwao (title mein [AUTOPOST])."""
    import datetime
    q = json.load(open("plans/STORY_QUEUE.json", encoding="utf-8"))
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)).date()
    ahead = int(os.environ.get("DAILY_AHEAD", "2") or 2)
    forced = os.environ.get("FORCE_BHAG", "").strip()
    base = run(["git", "rev-parse", "HEAD"]).strip()
    for it in q["episodes"]:
        d = datetime.date.fromisoformat(it["date"])
        if forced:
            if str(it["bhag"]) != forced:
                continue
        elif not (today <= d <= today + datetime.timedelta(days=ahead)):
            continue
        n = it["bhag"]
        found = json.loads(run(["gh", "issue", "list", "--repo", REPO, "--state", "all", "--limit", "100",
                                "--json", "number,title"]) or "[]")
        if any(re.match(rf"\s*Bhag\s+{n}\b", x["title"]) for x in found):
            print(f"Bhag {n}: issue pehle se hai, chhod diya")
            continue
        title = f"Bhag {n} [AUTOPOST]"
        url = run(["gh", "issue", "create", "--repo", REPO, "--title", title,
                   "--body", f"@ai Bhag {n} apne aap: {it['topic']} (Valmiki {it['sargas']}). Post: {it['date']} shaam 7 baje."]).strip()
        num = re.search(r"/issues/(\d+)", url).group(1)
        os.environ.update(ISSUE_NUMBER=num, ISSUE_TITLE=title, REQUEST=f"Bhag {n} banao")
        run(["git", "checkout", "-q", "-f", base])
        USED.clear(); LEASE.clear()
        try:
            mode_task()
        except (Busy, ValueError) as e:
            queue_issue(num, str(e))
        except Exception as e:
            comment(num, f"⚠️ Roz wali koshish mein galti hui, kal dobara ya yahin `@ai ...` likhiye.\n\n<sub>{str(e)[:300]}</sub>")


def mode_task():
    issue = os.environ["ISSUE_NUMBER"]
    branch = f"ai/issue-{issue}"
    checkout_branch(branch)
    st = load_state()
    task = (f"Issue title: {os.environ.get('ISSUE_TITLE', '')}\n"
            f"Owner's message (Hinglish): {os.environ.get('REQUEST', '')}\n"
            f"Earlier work on this issue's branch: {json.dumps(st, ensure_ascii=False)}" + autopost_brief())
    data = solve(task)
    msg = data["summary"] or "Ho gaya."
    st["issue"] = int(issue)
    if data["action"] == "change":
        eps = write_files(data)
        if eps:
            st["episode"] = sorted(eps)[0]
        st["fix_rounds"] = 0
        save_state(st)
        commit_push(branch, f"AI Helper (issue {issue}): {os.environ.get('ISSUE_TITLE', '')[:60]}")
        msg += f"\n\n📁 Badlaav branch `{branch}` par rakhe hain."
    if data.get("render") and st.get("episode"):
        save_state(st); commit_push(branch, f"AI Helper (issue {issue}): state")
        msg += "\n🎬 Video banna shuru ho gaya (~5-10 min). Banne par yahin link aur director check milega."
        comment(issue, msg)
        render_loop(issue, branch, st)
        return
    comment(issue, msg)


def director_check(img_bytes, ep_json):
    prompt = ("You are the strict film director of Katha Chitra. This image is a contact sheet of the finished "
              "Ramayan Short (one frame every 0.25 s, left-to-right, top-to-bottom). Check it against the rules "
              "below and the episode. List only REAL problems you can see (cut-off people at edges, characters "
              "overlapping, changing looks, halo on humans, empty/black frames, subtitle covering faces, missing logo, "
              "missing subscribe widget at the end, wrong mood colour). For each problem also write the exact '@ai ...' "
              "line the owner can paste to fix it. Answer in Hinglish, short numbered list; if all is fine say so in one line."
              "\n\n# RULES\n" + open("NIYAM.md", encoding="utf-8").read() + "\n\n# EPISODE\n" + ep_json)
    try:
        return ask(prompt, image=img_bytes, want_json=False)
    except Exception as e:
        return f"(AI director check abhi nahi ho paya: {str(e)[:120]}. Check sheet khud dekh lijiye.)"


def render_loop(issue, branch, st):
    ep = st["episode"]
    run_url = ""
    for rnd in range(MAX_FIX_ROUNDS + 1):
        run_id, ok = start_render(branch, ep)
        run_url = f"https://github.com/{REPO}/actions/runs/{run_id}"
        if ok:
            finish(issue, branch, st, ep, run_url)
            return
        if rnd == MAX_FIX_ROUNDS:
            break
        log = run(["gh", "run", "view", run_id, "--repo", REPO, "--log-failed"], check=False)
        tail = "\n".join(re.sub(r"^[^\t]*\t[^\t]*\t\S+Z ", "", l) for l in log.splitlines()[-120:])
        data = solve(f"The video of {ep} FAILED while rendering. Fix {ep}/episode.json so it renders "
                     f"(change as little as possible, bump VERSION, render true).\n\n# FAILED LOG\n{tail}")
        if data["action"] != "change":
            comment(issue, f"❌ Video nahi bana aur main fix nahi dhoondh paya. [Run]({run_url})\n\n{data['summary']}")
            return
        write_files(data)
        st["fix_rounds"] = rnd + 1
        save_state(st)
        commit_push(branch, f"AI Helper: render fix {rnd + 1} for {ep}")
        comment(issue, f"🔧 Video banate waqt galti aayi, maine theek karke dobara chalaya hai "
                       f"(koshish {rnd + 1}/{MAX_FIX_ROUNDS}).\n\n{data['summary']}")
    comment(issue, f"❌ Video {MAX_FIX_ROUNDS} baar theek karne ke baad bhi nahi bana. [Run dekhiye]({run_url}). "
                   "Ye issue Claude chat mein bhejiye.")



# ---------------- kadi jaanch + apne aap sudhaar (VIRAL.md section 6) ----------------
MAX_REVIEW_ROUNDS = 3
PASS_SCORE = 56
SCORE_KEYS = ["hook", "structure", "pace", "emotion", "mood", "ending", "camera"]


def fetch_sheet(ep):
    """(poori video ki sheet, antim sheet, cover-pehla-frame jaanch ka natija)"""
    rb = "render-" + os.path.basename(ep)
    run(["git", "fetch", "--depth", "1", "origin", f"+{rb}:refs/remotes/origin/{rb}"])
    show = lambda n: subprocess.run(["git", "show", f"origin/{rb}:{n}"], capture_output=True).stdout
    return show("check_sheet.jpg"), show("ending_sheet.jpg"), show("first_frame_check.txt").decode("utf-8", "ignore").strip()


def review_once(sheets, ep_json):
    viral = open("VIRAL.md", encoding="utf-8").read()
    prompt = (
        "You are the STRICT film director and reviewer of the Katha Chitra channel. Image 1 is a contact sheet of the finished "
        "Ramayan Short spread over the WHOLE video (about 100 frames, left-to-right, top-to-bottom). Image 2 (if given) is the LAST "
        "5 seconds at 4 frames per second. Judge ONLY what you can really see. "
        "Use section 6 of VIRAL.md below and the rules of NIYAM.md and SEEKH.md. "
        "IMPORTANT facts about our machine: it ALWAYS adds the small Katha Chitra logo at the top-right corner of every frame, the "
        "title box at the top and the subtitle box at the bottom; the cover as first frame and the sound level are checked by "
        "separate machine tests, so do NOT judge hard-fail rules 8 and 10 and do not judge the logo. Judge the subscribe widget "
        "(finger, SUBSCRIBE button, bell) ONLY from image 2. Things you cannot judge from pictures (voice loudness, voice-subtitle "
        "sync) must NOT be failures; put them in cannot_check. Never invent a problem; when unsure, do not list it. "
        "Identical consecutive frames while someone speaks are a weakness for 'pace' and 'emotion' only, not a hard fail.\n"
        "Reply with ONLY valid JSON:\n"
        '{"hard_fails":[{"rule":<1-10>,"what":"Hinglish: kya dikh raha hai aur kis frame/jagah","fix":"exact change in episode.json"}],'
        '"scores":{"hook":0-10,"structure":0-10,"pace":0-10,"emotion":0-10,"mood":0-10,"ending":0-10,"camera":0-10},'
        '"weak":[{"what":"...","fix":"..."}],"cannot_check":["..."],"summary":"Hinglish, 2 short lines"}\n\n'
        "# VIRAL.md\n" + viral + "\n\n# NIYAM.md\n" + open("NIYAM.md", encoding="utf-8").read() + "\n\n# SEEKH.md\n"
        + open("SEEKH.md", encoding="utf-8").read() + "\n\n# EPISODE\n" + ep_json)
    for _ in range(3):
        txt = ask(prompt, image=sheets, want_json=False)
        mt = re.search(r"\{.*\}", txt, re.DOTALL)
        try:
            d = json.loads(mt.group(0) if mt else txt)
            sc = d.get("scores") or {}
            if not all(k in sc for k in SCORE_KEYS):
                raise ValueError("scores adhoore")
            d["scores"] = {k: max(0, min(10, int(sc[k]))) for k in SCORE_KEYS}
            return d
        except (ValueError, TypeError):
            continue
    return None


def review(sheet, ep_json):
    """Kadi PASS/FAIL jaanch. Do baar jaanchta hai: seedha FAIL tabhi jab DONO baar wahi galti (niyam number) mile;
    number dono ka ausat. Jawab samajh na aaye, sheet na mile ya cover pehla frame na ho toh PASS nahi."""
    bad = lambda why: {"pass": False, "score": 0, "hard_fails": [why], "fix_text": why, "text": f"❌ {why}", "cannot_check": []}
    main_sheet, end_sheet, first_check = sheet if isinstance(sheet, tuple) else (sheet, b"", "")
    if not main_sheet:
        return bad("check sheet nahi mili")
    sheets = [main_sheet] + ([end_sheet] if end_sheet else [])
    runs = [review_once(sheets, ep_json) for _ in range(2)]
    runs = [r for r in runs if r]
    if not runs:
        return bad("jaanch ka jawab samajh nahi aaya, isliye PASS nahi")
    keys = {}
    for r in runs:
        for h in r.get("hard_fails") or []:
            keys.setdefault(str(h.get("rule")), []).append(h)
    hard = [v[0] for k, v in keys.items() if len(v) >= len(runs) and k not in ("8", "10")]
    if first_check.startswith("FAIL"):
        hard.append({"rule": 10, "what": "cover video ka pehla frame nahi hai (machine jaanch)", "fix": "cover ko pehle 0.1 sec par lagao"})
    sc = {k: round(sum(r["scores"][k] for r in runs) / len(runs)) for k in SCORE_KEYS}
    total = sum(sc.values())
    ok = (not hard) and total >= PASS_SCORE
    weak = [w for r in runs for w in (r.get("weak") or [])][:6]
    cant = sorted({str(c) for r in runs for c in (r.get("cannot_check") or [])})
    lines = [f"**Faisla: {'✅ PASS' if ok else '❌ FAIL'}** — number {total}/70 (chahiye {PASS_SCORE}+, {len(runs)} jaanch ka ausat): " +
             ", ".join(f"{k} {v}" for k, v in sc.items())]
    for h in hard:
        lines.append(f"- ❌ Niyam {h.get('rule')}: {h.get('what')}")
    single = [h for k, v in keys.items() if len(v) < len(runs) for h in v[:1]]
    for h in single:
        lines.append(f"- ⚠️ (sirf ek jaanch ne kaha, isliye FAIL nahi) Niyam {h.get('rule')}: {h.get('what')}")
    for w in weak:
        lines.append(f"- ⚠️ {w.get('what')}")
    if cant:
        lines.append("- ℹ️ Sirf tasveer se nahi dekh paya: " + "; ".join(cant))
    if runs[0].get("summary"):
        lines.append(str(runs[0]["summary"]))
    fixes = [f"RULE {h.get('rule')}: {h.get('what')} -> {h.get('fix')}" for h in hard] + \
            [f"WEAK: {w.get('what')} -> {w.get('fix')}" for w in weak]
    if not hard and total < PASS_SCORE:
        fixes.append(f"Score {total}/70 is below {PASS_SCORE}; improve the weakest scores: " + str(sc))
    return {"pass": ok, "score": total, "hard_fails": hard, "fix_text": "\n".join(fixes), "text": "\n".join(lines),
            "cannot_check": cant}


def autopost_on():
    return "[AUTOPOST]" in os.environ.get("ISSUE_TITLE", "")


def finish(issue, branch, st, ep, run_url):
    """Video ban gaya: kadi jaanch -> galti ho toh khud theek karke dobara -> PASS par (AUTOPOST ho toh) post."""
    ep_json = open(f"{ep}/episode.json", encoding="utf-8").read()
    verdict = None
    for rv in range(MAX_REVIEW_ROUNDS + 1):
        verdict = review(fetch_sheet(ep), ep_json)
        bh = title_bhag() or re.sub(r"\D", "", os.path.basename(ep))
        sc_problems = story_check(ep_json, bh)
        if sc_problems:
            verdict["pass"] = False
            verdict["hard_fails"] = list(verdict.get("hard_fails") or []) + [{"rule": 9, **p} for p in sc_problems]
            verdict["text"] = verdict["text"].replace("✅ PASS", "❌ FAIL (Valmiki jaanch)") + "\n" + "\n".join(f"- ❌ Niyam 9 (Valmiki): {p.get('line')}: {p.get('what')}" for p in sc_problems)
            verdict["fix_text"] = (verdict.get("fix_text", "") + "\n" + "\n".join(
                f"RULE 9: line {p.get('line')}: {p.get('what')} -> {p.get('fix')}" for p in sc_problems)).strip()
        print(f"Jaanch round {rv}: pass={verdict['pass']} score={verdict['score']}")
        if verdict["pass"] or rv == MAX_REVIEW_ROUNDS:
            break
        data = solve(f"The strict director review of the finished video of {ep} found problems. Fix them in {ep}/episode.json "
                     f"(change as little as needed, bump VERSION, render true). Problems:\n{verdict['fix_text']}")
        if data["action"] != "change":
            break
        write_files(data)
        st["review_rounds"] = rv + 1
        save_state(st)
        commit_push(branch, f"AI Helper: director fix {rv + 1} for {ep}")
        comment(issue, f"🔧 Jaanch mein galti mili, khud theek karke dobara bana raha hu (koshish {rv + 1}/{MAX_REVIEW_ROUNDS}).\n\n"
                       f"{verdict['text']}\n\n{data['summary']}")
        run_id, ok = start_render(branch, ep)
        run_url = f"https://github.com/{REPO}/actions/runs/{run_id}"
        if not ok:
            verdict = {"pass": False, "score": 0, "hard_fails": [], "text": "❌ Sudhaar ke baad video nahi bana.", "fix_text": ""}
            break
        ep_json = open(f"{ep}/episode.json", encoding="utf-8").read()
    deliver(issue, ep, run_url, verdict)
    if not autopost_on():
        return
    if verdict["pass"]:
        n = re.sub(r"\D", "", os.path.basename(ep))
        run(["gh", "workflow", "run", "publish.yml", "--repo", REPO, "--ref", "main",
             "-f", f"episode={ep}", "-f", f"bhag={n}", "-f", f"issue={issue}"])
        comment(issue, "🚀 Jaanch PASS. Shaam 7 baje YouTube + Instagram par apne aap jaayega.")
    else:
        run(["gh", "label", "create", "dekhna-hai", "--repo", REPO, "--color", "d93f0b", "--force",
             "--description", "Jaanch fail: post nahi hua"], check=False)
        run(["gh", "issue", "edit", str(issue), "--repo", REPO, "--add-label", "dekhna-hai"], check=False)
        comment(issue, "⛔ Jaanch 3 baar sudhaar ke baad bhi PASS nahi hui, isliye aaj **post nahi hoga**. "
                       "Upar ki list dekhiye; theek karwana ho toh yahin `@ai ...` likhiye.")


def deliver(issue, ep, run_url, verdict=None):
    rb = "render-" + os.path.basename(ep)
    run(["git", "fetch", "--depth", "1", "origin", f"+{rb}:refs/remotes/origin/{rb}"])
    ref = f"origin/{rb}"
    names = run(["git", "ls-tree", "--name-only", ref]).split()
    mp4 = next((n for n in names if n.endswith(".mp4")), None)
    jpg = [n for n in names if n.endswith(".jpg") and n != "check_sheet.jpg"]
    sheet = subprocess.run(["git", "show", f"{ref}:check_sheet.jpg"], capture_output=True).stdout
    with open(f"{ep}/episode.json", encoding="utf-8") as f:
        ep_json = f.read()
    report = verdict["text"] if verdict else (director_check(sheet, ep_json) if sheet else "(check sheet nahi mili)")
    link = lambda n: f"https://github.com/{REPO}/blob/{rb}/{n}"
    eng = subprocess.run(["git", "show", f"{ref}:voice_engine.txt"], capture_output=True, text=True).stdout.strip() or "madhur"
    msg = "✅ **Video ban gaya!** (cover video ke pehle frame par bhi laga hai)\n"
    if eng == "piper":
        msg += "\n⚠️ Is baar Madhur awaaz nahi chali, isliye **sahara wali Piper awaaz** lagi hai. Madhur chahiye to baad mein yahin `@ai dobara koshish karo` likhiye.\n"
    k = 1
    if mp4:
        msg += f"\n{k}. Video: [{mp4}]({link(mp4)})"; k += 1
    for j in jpg:
        msg += f"\n{k}. Cover: [{j}]({link(j)})"; k += 1
    msg += f"\n{k}. Director check sheet: [check_sheet.jpg]({link('check_sheet.jpg')})"
    msg += (f"\n\n**Download:** link kholiye → upar right **⤓ (Download raw file)**, ya **⋯ → Download**. "
            f"Ya [run]({run_url}) ke neeche **video** zip (video + cover dono).")
    msg += f"\n\n🎬 **Director check (AI):**\n{report}\n\nKuch theek karwana ho to yahin `@ai` likhkar bataiye."
    comment(issue, msg)


QUEUE = "baad-mein"   # issues waiting for a quiet time (free AI busy); done by the morning schedule


def queue_issue(issue, why):
    run(["gh", "label", "create", QUEUE, "--repo", REPO, "--color", "f2c230", "--force",
         "--description", "Free AI busy tha; subah apne aap dobara"], check=False)
    run(["gh", "issue", "edit", str(issue), "--repo", REPO, "--add-label", QUEUE], check=False)
    comment(issue, "⏳ Free AI abhi busy hai (raat ko Google ke server par bheed hoti hai). Ye kaam **baad-mein** list mein "
                   "daal diya hai: **subah 5:37 baje** (aur dopahar 3:07 baje) main apne aap dobara karunga. "
                   "Aapko kuch likhne ki zaroorat nahi.\n\n" f"<sub>{why[:200]}</sub>")


def mode_queue():
    """Morning schedule: redo every queued issue with the owner's last @ai request."""
    owner = REPO.split("/")[0]
    base = run(["git", "rev-parse", "HEAD"]).strip()
    nums = json.loads(run(["gh", "api", f"repos/{REPO}/issues?labels={QUEUE}&state=open", "-q", "[.[].number]"]) or "[]")
    print("baad-mein list:", nums)
    for n in nums:
        iss = json.loads(run(["gh", "api", f"repos/{REPO}/issues/{n}"]))
        cms = json.loads(run(["gh", "api", f"repos/{REPO}/issues/{n}/comments?per_page=100"]))
        asks = [c["body"] for c in cms if c["user"]["login"] == owner and "@ai" in c["body"]]
        os.environ.update(ISSUE_NUMBER=str(n), ISSUE_TITLE=iss["title"], REQUEST=(asks[-1] if asks else iss["body"] or ""))
        run(["gh", "issue", "edit", str(n), "--repo", REPO, "--remove-label", QUEUE], check=False)
        run(["git", "checkout", "-q", "-f", base])
        run(["git", "branch", "-D", f"ai/issue-{n}"], check=False)
        USED.clear(); LEASE.clear()
        try:
            mode_task()
        except (Busy, ValueError) as e:
            queue_issue(n, str(e)); return          # still busy: keep the rest for the next slot
        except Exception as e:
            comment(n, f"⚠️ Subah wali koshish mein galti hui. Yahin dobara `@ai ...` likhiye.\n\n<sub>{str(e)[:300]}</sub>")


if __name__ == "__main__":
    try:
        {"task": mode_task, "queue": mode_queue, "daily": mode_daily}[sys.argv[1]]()
    except (Busy, ValueError) as e:      # free AI busy or kept sending broken answers: queue for the morning
        if os.environ.get("ISSUE_NUMBER"):
            queue_issue(os.environ["ISSUE_NUMBER"], str(e))
        sys.exit(0)
    except Exception as e:
        comment(os.environ.get("ISSUE_NUMBER", ""),
                "⚠️ Helper ke saath ek galti hui, kaam poora nahi hua. Yahin dobara `@ai ...` likhiye; "
                f"phir bhi na chale to ye issue Claude chat mein bhejiye.\n\n<sub>{str(e)[:300]}</sub>")
        raise
