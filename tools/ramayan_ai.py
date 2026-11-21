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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import viral_radar as VR  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

REPO = os.environ["GITHUB_REPOSITORY"]
MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
MAX_FIX_ROUNDS = 5
STATE = "ai_state.json"
CONTEXT = ["NIYAM.md", "VIRAL.md", "SEEKH.md", "BODY.md", "tools/engine/README.md"]


BASE = {}    # auto-video ka commit jahan se is issue ka kaam shuru hua
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
    BASE["sha"] = run(["git", "rev-parse", "HEAD"]).strip()      # auto-video ka wo commit jahan se shuru kiya (promote ke waqt milaya jaata hai)
    run(["git", "checkout", "-b", branch])          # always start from the newest auto-video (newest engine + rules)
    if run(["git", "ls-remote", "--heads", "origin", branch]).strip():
        # bring over only this issue's own work: its state, plans and scene-list episodes (never old code)
        run(["git", "fetch", "--depth", "1", "origin", branch])
        LEASE[branch] = run(["git", "rev-parse", "FETCH_HEAD"]).strip()
        old = run(["git", "ls-tree", "-r", "--name-only", "FETCH_HEAD"]).split()
        keep = [f for f in old if f == STATE or f.startswith("plans/") or
                (re.match(r"^episodes/[a-z0-9_]+/episode\.json$", f) and '"SHOTS"' in run(["git", "show", f"FETCH_HEAD:{f}"]))]
        try:      # is issue ke apne engine/code badlaav bhi saath laao (state mein likhe hain)
            prev = json.loads(run(["git", "show", f"FETCH_HEAD:{STATE}"]))
            keep += [f for f in prev.get("code_files", []) if f in old and (is_code_path(f) or f in DOC_PATHS)]
            if prev.get("base"):
                BASE["sha"] = prev["base"]
        except Exception:
            pass
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
_LIVE = {}


def live_gemini_models(c):
    """Google se abhi chalte models: ("flash" wale tez, "pro" wale zyada sochne wale). Naam badle tab bhi helper na ruke."""
    if "m" not in _LIVE:
        try:
            names = [m.name.split("/")[-1] for m in c.models.list()
                     if "generateContent" in (getattr(m, "supported_actions", None) or ["generateContent"])]
            bad = ("image", "tts", "live", "audio", "thinking-exp", "preview-0", "embed", "vision", "robotics", "computer")
            ok = [n for n in names if not any(x in n for x in bad)]
            _LIVE["m"] = sorted((n for n in ok if "flash" in n), reverse=True)[:4]
            _LIVE["pro"] = sorted((n for n in ok if "pro" in n), reverse=True)[:2]
        except Exception as e:
            print("Gemini model list nahi mili:", str(e)[:100])
            _LIVE["m"], _LIVE["pro"] = [], []
    return _LIVE["m"]


def gemini_model_list(c, hard=False):
    out = list(MODELS)
    for m in live_gemini_models(c):
        if m not in out:
            out.append(m)
    if hard:     # mushkil kaam (episode likhna, jaanch, video dekhna): pehle sabse zyada sochne wala "pro" model, free limit kam hai toh flash par
        out = [m for m in _LIVE.get("pro", []) if m not in out[:0]] + out
    return out


def gemini(contents, want_json, hard=False):
    c = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip(), http_options=types.HttpOptions(timeout=120000))
    mlist = gemini_model_list(c, hard)
    cfg = types.GenerateContentConfig(temperature=0.3, max_output_tokens=32768,
                                      response_mime_type="application/json" if want_json else None)
    last = None
    patient = os.environ.get("PATIENT") == "1"      # shaant samay (queue) mein sabr; warna jaldi hatke doosre AI par
    for attempt in range(max(6, len(mlist) + 2) if patient else 3):
        m = mlist[attempt % len(mlist)]
        try:
            txt = (c.models.generate_content(model=m, contents=contents, config=cfg).text or "").strip()
            if txt:
                print("Jawab:", m); USED.append(m)
                return txt
            raise ValueError("khaali jawab")
        except Exception as e:
            last = e
            busy = any(x in str(e) for x in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "overloaded"))
            w = min(90, (20 if busy else 8) * (attempt + 1)) if patient else (3 if busy else 2) * (attempt + 1)
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


PREF = re.compile(r"(gpt-oss-120b|llama-?3\.3-70b|qwen.*(235|72|32)b|deepseek-v3|mistral-(large|medium)|command-a|gemma.*(27|70)b)", re.I)


def _discover(url, key):
    """Provider ki apni model list se kaam ke bade models dhoondho (model ka naam badal jaaye tab bhi chale)."""
    try:
        base = url.rsplit("/chat/completions", 1)[0]
        data = requests.get(base + "/models", headers={"Authorization": f"Bearer {key}"}, timeout=30).json()
        ids = [m.get("id", "") for m in (data.get("data") if isinstance(data, dict) else data) or []]
        return [i for i in ids if PREF.search(i) and "embed" not in i.lower() and "guard" not in i.lower()][:4]
    except Exception:
        return []


def _openai_style(name, url, key, models, prompt_text, want_json, timeout=300):
    if not key:
        raise Busy(f"{name}: key nahi")
    last = None
    tried = set()
    for stage in range(2):                       # pehle tay naam, phir provider ki list se khud dhundhe naam
        for m in models:
            if m in tried:
                continue
            tried.add(m)
            try:
                body = {"model": m, "temperature": 0.3, "messages": [{"role": "user", "content": prompt_text}]}
                r = requests.post(url, timeout=timeout, headers={"Authorization": f"Bearer {key}"},
                                  json={**body, **({"response_format": {"type": "json_object"}} if want_json else {})})
                if want_json and r.status_code >= 400:    # kuch jagah JSON-mode nahi hota: bina uske dobara
                    r = requests.post(url, timeout=timeout, headers={"Authorization": f"Bearer {key}"}, json=body)
                txt = r.json()["choices"][0]["message"]["content"].strip()
                if txt:
                    print(f"Jawab ({name}):", m); USED.append(f"{name} {m}")
                    return txt
            except Exception as e:
                last = e
                print(f"{name} {m} nahi chala: {str(e)[:160]}")
        if stage == 0:
            models = _discover(url, key)
            if not models:
                break
    raise Busy(f"{name}: {str(last)[:200]}")


def _extra(name, url, key_env, models, p, j):
    """Free raaste jinki key ho to chalte hain. Model badalna ho to secret <NAAM>_MODELS (comma se) daalo."""
    custom = os.environ.get(name.upper() + "_MODELS", "").strip()
    models = [x.strip() for x in custom.split(",") if x.strip()] or models
    return _openai_style(name, url, os.environ.get(key_env, "").strip(), models, p, j)




def cloudflare(p, j):
    acc = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    if not acc:
        raise Busy("Cloudflare: account id nahi")
    return _extra("Cloudflare", f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/v1/chat/completions",
                  "CLOUDFLARE_API_TOKEN", ["@cf/meta/llama-3.3-70b-instruct-fp8-fast", "@cf/openai/gpt-oss-120b"], p, j)


def cohere(p, j):
    return _extra("Cohere", "https://api.cohere.ai/compatibility/v1/chat/completions", "COHERE_API_KEY",
                  ["command-a-03-2025", "command-r-plus"], p, j)


def huggingface(p, j):
    return _extra("HuggingFace", "https://router.huggingface.co/v1/chat/completions", "HF_TOKEN",
                  ["meta-llama/Llama-3.3-70B-Instruct", "Qwen/Qwen2.5-72B-Instruct"], p, j)




def groq(p, j):
    return _extra("Groq", "https://api.groq.com/openai/v1/chat/completions", "GROQ_API_KEY",
                  ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"], p, j)


def cerebras(p, j):
    return _extra("Cerebras", "https://api.cerebras.ai/v1/chat/completions", "CEREBRAS_API_KEY",
                  ["gpt-oss-120b", "llama-3.3-70b"], p, j)


def mistral(p, j):
    return _extra("Mistral", "https://api.mistral.ai/v1/chat/completions", "MISTRAL_API_KEY",
                  ["mistral-large-latest", "mistral-small-latest"], p, j)


def sambanova(p, j):
    return _extra("SambaNova", "https://api.sambanova.ai/v1/chat/completions", "SAMBANOVA_API_KEY",
                  ["Meta-Llama-3.3-70B-Instruct", "DeepSeek-V3.1"], p, j)


def nvidia(p, j):
    return _extra("NVIDIA", "https://integrate.api.nvidia.com/v1/chat/completions", "NVIDIA_API_KEY",
                  ["meta/llama-3.3-70b-instruct", "qwen/qwen2.5-coder-32b-instruct"], p, j)


# ---------------- aakhri sahara: GitHub ke computer par hi chhota AI (Ollama), koi key/limit nahi ----------------
LOCAL_URL = "http://127.0.0.1:11434"


def _local_up():
    try:
        return requests.get(LOCAL_URL + "/api/tags", timeout=3).status_code == 200
    except Exception:
        return False


def local_ai(p, j, hard=False):
    """Baaki sab AI na chalein tab. Pehli baar Ollama install + model download (kuch minute), phir CPU par chalta hai: dheema par kabhi band nahi."""
    if os.environ.get("NO_LOCAL"):
        raise Busy("Local AI: is kaam ke liye band")
    model = os.environ.get("LOCAL_MODEL", "").strip() or ("qwen2.5:7b" if hard else "qwen2.5:3b")
    if not _local_up():
        if not (os.environ.get("GITHUB_ACTIONS") or os.environ.get("LOCAL_AI")):
            raise Busy("Local AI: sirf GitHub computer par")
        print("Local AI: Ollama laga raha hoon...")
        if subprocess.run(["sh", "-c", "command -v ollama >/dev/null || curl -fsSL https://ollama.com/install.sh | sh"],
                          capture_output=True, text=True, timeout=900).returncode != 0:
            raise Busy("Local AI: Ollama install nahi hua")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(40):
            if _local_up():
                break
            time.sleep(2)
        else:
            raise Busy("Local AI: server shuru nahi hua")
    have = requests.get(LOCAL_URL + "/api/tags", timeout=10).json().get("models", [])
    if not any(m.get("name", "").startswith(model.split(":")[0]) and m.get("name", "") == model for m in have):
        print("Local AI: model utaar raha hoon:", model)
        r = subprocess.run(["ollama", "pull", model], capture_output=True, text=True, timeout=1500)
        if r.returncode != 0:
            raise Busy("Local AI: model nahi utra: " + r.stderr[-120:])
    return _openai_style("Local", LOCAL_URL + "/v1/chat/completions", "local", [model], p, j, timeout=1500 if hard else 900)


def ask(prompt_text, image=None, want_json=True, hard=False):
    imgs = image if isinstance(image, (list, tuple)) else ([image] if image else [])
    contents = [types.Part.from_bytes(data=i, mime_type="image/jpeg") for i in imgs] + [prompt_text] if imgs else prompt_text
    chain = [("Gemini", lambda p: gemini(contents if p == prompt_text else p, want_json, hard))]
    if not imgs:   # tasveer sirf Gemini dekh sakta hai
        chain += [("OpenRouter", lambda p: openrouter(p, want_json)),
                  ("GitHub", lambda p: github_models(p, want_json)),
                  ("Cloudflare", lambda p: cloudflare(p, want_json)),
                  ("Groq", lambda p: groq(p, want_json)),
                  ("Cerebras", lambda p: cerebras(p, want_json)),
                  ("Mistral", lambda p: mistral(p, want_json)),
                  ("SambaNova", lambda p: sambanova(p, want_json)),
                  ("NVIDIA", lambda p: nvidia(p, want_json)),
                  ("Cohere", lambda p: cohere(p, want_json)),
                  ("HuggingFace", lambda p: huggingface(p, want_json))]
    def parse(txt):
        mt = re.search(r"\{.*\}", txt, re.DOTALL)
        data = json.loads(mt.group(0) if mt else txt)
        if data.get("action") not in ("change", "none", "need_code"):
            raise ValueError("action galat")
        data.setdefault("files", []); data.setdefault("summary", ""); data.setdefault("render", False)
        return data

    import queue
    import threading
    prompt, errs = prompt_text, []
    for _round in range(2):                      # poori list do baar
        # 1) Gemini pehle (sabse achha, tasveer/video bhi dekhta hai)
        name, fn = chain[0]
        try:
            txt = fn(prompt)
            if not want_json:
                return txt
            try:
                return parse(txt)
            except ValueError as e:
                errs.append(f"{name}: JSON tooti")
                prompt = (prompt_text + "\n\n# YOUR LAST ANSWER WAS NOT VALID JSON (" + str(e)[:120] +
                          "). Answer again with ONLY valid JSON; escape every double quote inside strings.")
        except Exception as e:
            errs.append(f"{name}: {str(e)[:60]}")
        # 2) baaki free AI ek saath daudte hain: jo pehle sahi jawab de wahi jeeta (line se ek-ek karke nahi)
        rest = chain[1:]
        if not rest:
            continue
        q = queue.Queue()

        def worker(nm, f, pr):
            try:
                t = f(pr)
                q.put((nm, parse(t) if want_json else t, None))
            except Exception as ex:
                q.put((nm, None, str(ex)[:60]))
        for nm, f in rest:
            threading.Thread(target=worker, args=(nm, f, prompt), daemon=True).start()
        deadline = time.time() + 300      # kul 5 minute: tab tak jawab nahi aaya toh Busy -> kaam 'baad-mein' queue mein
        for _ in rest:
            try:
                nm, res, err = q.get(timeout=max(1, deadline - time.time()))
            except queue.Empty:
                errs.append("baaki AI 5 min mein jawab nahi de paaye"); break
            if err is None:
                print("Daud ka jeetne wala AI:", nm)
                return res
            errs.append(f"{nm}: {err}")
    if not imgs:                                  # sab free AI fail: aakhri sahara, apne computer par chhota AI
        try:
            t = local_ai(prompt_text, want_json, hard)
            return parse(t) if want_json else t
        except Exception as e:
            errs.append(f"Local: {str(e)[:60]}")
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
- NEW episode: the owner has given you FULL FREEDOM. Never ask the owner for an OK or a question; decide yourself, think it through,
  and state your assumptions in the summary. In ONE answer write plans/<bhagN>_PLAN.md (shot list, every shot 2-3 s, who stands where,
  new character looks from Valmiki) + plans/<bhagN>_episode.json AND episodes/<bhagN>/episode.json (render true). Plan first in your
  head like a film director (every scene decided from the story), then build.
- When something is unclear, decide the most sensible way yourself (look at the rules in NIYAM.md/SEEKH.md/VIRAL.md) and go on.
- BUILD: write episodes/<bhagN>/episode.json (copy the plan's scene list). "render": true.
- FIX a look/render problem: change as little as possible in that episode.json, bump VERSION, "render": true.
- Owner only wants the video made again without changes: "action": "none", "render": true.
- Question only: "action": "none", "render": false, answer in summary.
- Normally only plans/... and episodes/<name>/episode.json may be written (always the FULL file).
- If the story or a review problem needs something the engine cannot do yet (new background, pose, effect, camera move, or an engine bug),
  do NOT work around it badly: reply {"action": "need_code", "render": false, "summary": "what is missing and what you will add", "files": []}.
  You will then get the engine source and may change it (see CODE RULES).
- You may also learn: when a real problem and its fix are now clear, add one short Hinglish line to SEEKH.md (an edit, see CODE RULES).
- Use only backgrounds, poses, faces, moods and characters listed in tools/engine/README.md; a new character goes in
  NEW_CHARS with its look decided from Valmiki. Keep people at least 260 apart (330 with a big devta/rakshas).
"""



# ---------------- code ki azadi (guard ke saath) ----------------
# Helper ab engine ka code bhi badal sakta hai (naya background/pose/effect, bug fix) aur SEEKH.md mein seekh likh sakta hai.
# Par: sirf apni issue ki branch par; render wale computer ke paas koi secret nahi; naye code mein khatarnaak cheezein mana;
# jaanch (PASS) ke baad hi shared engine mein jaata hai, peechhe backup tag ke saath.
CODE_PATHS = [r"^tools/engine/[A-Za-z0-9_]+\.py$", r"^tools/(?!ramayan_ai\.py$)[A-Za-z0-9_]+\.(py|sh)$", r"^template/lib/[A-Za-z0-9_]+\.py$", r"^episodes/[a-z0-9_]+/[A-Za-z0-9_]+\.py$"]
DOC_PATHS = ["SEEKH.md", "BODY.md", "tools/engine/README.md"]
DENY = re.compile(
    r"(GITHUB_TOKEN|GH_TOKEN|github\.token|extraheader|COMPOSIO|[A-Z_]*(API_KEY|SECRET|TOKEN)\b|\.git/|git\s+(push|remote|config)|"
    r"import\s+(requests|urllib|socket|http|ftplib|smtplib|paramiko|aiohttp|httpx)|from\s+(requests|urllib|socket|http)\b|"
    r"curl\b|wget\b|\bssh\b|\beval\(|\bexec\(|__import__|environ\s*\.\s*(items|keys|values|copy)|dict\(\s*os\.environ|"
    r"shutil\.rmtree|rm\s+-rf|os\.(remove|unlink|rmdir)\(\s*['\"]/)", re.I)


def is_code_path(p):
    return any(re.match(x, p) for x in CODE_PATHS)


def materialize(changes):
    """Badlaav ki list (poori file ya edits) ko {path: naya content} mein badlo. (contents, problems)."""
    out, problems = {}, []
    for it in changes:
        p = it.get("path", "")
        if ".." in p:
            problems.append(f"{p}: galat path"); continue
        if "old" in it:
            if not (is_code_path(p) or p in DOC_PATHS):
                problems.append(f"{p}: edits sirf engine/lib/episode ke .py aur SEEKH.md par"); continue
            cur = out.get(p)
            if cur is None:
                try:
                    with open(p, encoding="utf-8") as f:
                        cur = f.read()
                except OSError:
                    problems.append(f"{p}: file nahi mili"); continue
            old, new = str(it["old"]), str(it.get("new", ""))
            if cur.count(old) != 1:
                problems.append(f"{p}: 'old' text {cur.count(old)} jagah mila (ek hi baar hona chahiye)"); continue
            out[p] = cur.replace(old, new, 1)
        else:
            out[p] = it.get("content", "")
    return out, problems


def scan_new_code(p, old_text, new_text):
    """Sirf NAYE jode gaye hisse mein khatarnaak cheezein dhundho (purana code jaisa hai waisa rehta hai)."""
    added = [l for l in new_text.splitlines() if l not in set(old_text.splitlines())]
    bad = DENY.search("\n".join(added))
    return [f"{p}: mana hai (khatarnaak cheez): {bad.group(0)[:40]}"] if bad else []


RULES_CODE = """
CODE RULES (you may now change the engine yourself; you are free, but careful):
- Allowed: edits to tools/engine/*.py, template/lib/*.py, episodes/<name>/*.py, tools/*.py and tools/*.sh (voice, render script, machine checks, viral radar; NOT tools/ramayan_ai.py), SEEKH.md, tools/engine/README.md, plus episode.json/plans as before.
- For code ALWAYS use small edits, never a whole file: {"path": "...", "old": "EXACT text that occurs ONCE in the file", "new": "replacement"}.
  (A new small .py file may be given whole as {"path","content"}.) Several edits per file are applied in order.
- Keep everything that works. Do not change how existing characters, backgrounds and episodes look. Only ADD or FIX.
- The new code must run on the render machine: Python 3.12, pycairo, numpy, pillow, ffmpeg; no internet, no secrets.
  Forbidden (rejected automatically): network libraries, reading API keys/tokens/environment lists, git commands, eval/exec, deleting outside the work folder.
- After your edit the engine checks (spec.py) and the render must still pass for ALL existing episodes; bump VERSION in the episode so it renders.
- Explain in "summary" (Hinglish, simple words) what you added and why.
"""


def check_changes(changes):
    problems = []
    contents, pr = materialize(changes)
    problems += pr
    for p, c in contents.items():
        if p in DOC_PATHS:
            continue
        ok_path = p.startswith("plans/") or re.match(r"^episodes/[a-z0-9_]+/episode\.json$", p) or is_code_path(p)
        if not ok_path:
            problems.append(f"{p}: yahan likhne ki ijazat nahi (sirf plans/, episodes/<naam>/episode.json, engine/lib ka code)")
            continue
        if is_code_path(p):
            try:
                with open(p, encoding="utf-8") as f:
                    old = f.read()
            except OSError:
                old = ""
            problems += scan_new_code(p, old, c)
            try:
                compile(c, p, "exec")
            except SyntaxError as e:
                problems.append(f"{p}: Python galat hai: {e}")
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


def engine_sources():
    out = []
    for pat in ("tools/engine", "template/lib"):
        for fn in sorted(os.listdir(pat)):
            if fn.endswith(".py"):
                with open(os.path.join(pat, fn), encoding="utf-8") as f:
                    out.append(f"===== CODE: {pat}/{fn} =====\n{f.read()}")
    return "\n\n".join(out)


def solve(task, code=False):
    files = context_files()
    block = "\n\n".join(f"===== FILE: {p} =====\n{c}" for p, c in files.items())
    prompt = f"{RULES}\n\n# FILES\n{block}\n\n# TASK\n{task}"
    if code:
        prompt = f"{RULES}\n{RULES_CODE}\n\n# ENGINE SOURCE (you may edit these)\n{engine_sources()}\n\n# FILES\n{block}\n\n# TASK\n{task}"
    for _ in range(3):
        data = ask(prompt, hard=True)
        if data["action"] == "need_code" and not code:
            print("AI ko engine mein badlaav chahiye:", data.get("summary", "")[:200])
            return solve(task + "\n\nYou said the engine needs: " + data.get("summary", "") + "\nNow write the engine edits and the episode files.", code=True)
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


CODE_TOUCHED = set()


def write_files(data):
    eps = set()
    contents, _ = materialize(data["files"])
    for path, content in contents.items():
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        run(["git", "add", path])
        if path.startswith("episodes/") and path.endswith("episode.json"):
            eps.add("/".join(path.split("/")[:2]))
        if is_code_path(path) or path in DOC_PATHS:
            CODE_TOUCHED.add(path)
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
    radar = {}
    if os.path.exists(f"episodes/bhag{b}/episode.json"):
        print("Episode pehle se bana hai: radar kahani/sawaal nahi badlega.")
    else:
      try:      # radar kabhi video nahi rokta: kuch bhi atke toh bina radar ke chalega
          import datetime
          today = (datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)).date()
          radar = VR.advise(ask, b, it.get("topic", "?"), it.get("sargas", "?"), today, open("VIRAL.md", encoding="utf-8").read(), valmiki_text=text)
          if radar:
              os.makedirs("plans/radar", exist_ok=True)
              with open(f"plans/radar/bhag{b}.json", "w", encoding="utf-8") as fh:
                  json.dump(radar, fh, ensure_ascii=False, indent=1)
              run(["git", "add", f"plans/radar/bhag{b}.json"], check=False)
              print("Viral radar:", radar.get("question"))
      except Exception as e:
          print("Viral radar nahi chala (koi baat nahi):", str(e)[:150])
    st_txt = ("The Valmiki text below is the ONLY source; use nothing else:\n" + text) if text else \
             ("Valmiki's full text could not be fetched. Use only what you are SURE is in Valmiki Ramayan Bala Kanda; "
              "if unsure, leave it out. Do not add anything.")
    return ("\n\nAUTOPOST: the owner already approved everything; the strict director review and the Valmiki check will "
            "judge the result, so do NOT ask for an OK. In ONE answer write plans/bhag{b}_PLAN.md, plans/bhag{b}_episode.json AND "
            "episodes/bhag{b}/episode.json (action change, render true). Episode: Bhag {b}; topic: {t}; Valmiki Bala Kanda "
            "sargas (approx.): {s}. Follow VIRAL.md (hook in the first line, QUESTION banner, scene-wise pace, ending with the "
            "next part's question + comment call) and SEEKH.md. About 35-45 seconds. Story exactly as in Valmiki, nothing added; every scene must follow the Valmiki text in the order it happens.\n"
            ).format(b=b, t=it.get("topic", "?"), s=it.get("sargas", "?")) + VR.brief_text(radar) + st_txt


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
        st.setdefault("base", BASE.get("sha", ""))
        if CODE_TOUCHED:
            st["code_files"] = sorted(set(st.get("code_files", [])) | CODE_TOUCHED)
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
MAX_REVIEW_ROUNDS = 5
PASS_SCORE = 56
SCORE_KEYS = ["hook", "structure", "pace", "emotion", "mood", "ending", "camera"]


def fetch_sheet(ep):
    """(poori video ki sheet, antim sheet, cover-pehla-frame jaanch ka natija)"""
    rb = "render-" + os.path.basename(ep)
    run(["git", "fetch", "--depth", "1", "origin", f"+{rb}:refs/remotes/origin/{rb}"])
    show = lambda n: subprocess.run(["git", "show", f"origin/{rb}:{n}"], capture_output=True).stdout
    try:
        machine = json.loads(show("machine_report.json").decode("utf-8", "ignore") or "{}")
    except ValueError:
        machine = {}
    return show("check_sheet.jpg"), show("ending_sheet.jpg"), show("first_frame_check.txt").decode("utf-8", "ignore").strip(), machine


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
        + open("SEEKH.md", encoding="utf-8").read() + "\n\n# BODY.md\n" + open("BODY.md", encoding="utf-8").read() + "\n\n# EPISODE\n" + ep_json)
    for _ in range(3):
        txt = ask(prompt, image=sheets, want_json=False, hard=True)
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



def fetch_video(ep):
    """Render branch se asli MP4 laao (AI ko poora video dekhne-sunne ke liye). Na mile toh None."""
    rb = "render-" + os.path.basename(ep)
    try:
        names = run(["git", "ls-tree", "--name-only", f"origin/{rb}"]).split()
        mp4 = next((n for n in names if n.endswith(".mp4")), None)
        if not mp4:
            return None
        data = subprocess.run(["git", "show", f"origin/{rb}:{mp4}"], capture_output=True).stdout
        if len(data) < 100000:
            return None
        path = os.path.join(tempfile.gettempdir(), "watch_" + os.path.basename(mp4))
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception as e:
        print("video laane mein dikkat:", str(e)[:150])
        return None


def watch_video(path, ep_json):
    """AI ASLI video dekhta aur sunta hai (Gemini Files API, free): awaaz, bol, subtitle ka mel, jhatke, bhaav.
    Sirf Gemini video dekh sakta hai; koi bhi dikkat ho (busy, upload fail) toh None -> baaki jaanch chalti rehti hai."""
    if not path or not os.environ.get("GEMINI_API_KEY", "").strip():
        return None
    try:
        lines = json.loads(ep_json).get("LINES", {})
    except ValueError:
        lines = {}
    script = "\n".join(f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in lines.items())
    prompt = (
        "You are the strict director of the Katha Chitra channel. WATCH and LISTEN to this finished Hindi Ramayan Short "
        "(vertical, about 40-60 s). Below is the narration script it was built from. Judge ONLY what you really see and hear; "
        "never invent. Timestamps as mm:ss.\n"
        "Check: (1) does the spoken Hindi match the script, any line skipped, repeated or mispronounced (2) do the karaoke subtitles "
        "match the voice timing (3) is any line clearly quieter/louder than the rest (4) sudden jumps/teleporting of characters, "
        "characters overlapping, a person cut by the edge (5) do faces and bodies show the right emotion (6) is the first 2 seconds "
        "a hook (7) any dead/empty moment (8) is the subscribe widget (finger, button, bell) shown near the end.\n"
        "Reply with ONLY valid JSON: "
        '{"problems":[{"kind":"voice|sync|loudness|jump|overlap|emotion|hook|dead|widget|other","time":"mm:ss",'
        '"confidence":"high|medium","what":"Hinglish, short","fix":"exact change to episode.json (shot/line/pause)"}],'
        '"scores":{"hook":0-10,"pace":0-10,"emotion":0-10},"summary":"Hinglish, 1-2 lines"}. '
        "At most 6 problems; list a problem as high only if you are sure.\n\n# SCRIPT\n" + script)
    try:
        c = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip(), http_options=types.HttpOptions(timeout=300000))
        f = c.files.upload(file=path, config=types.UploadFileConfig(mime_type="video/mp4"))
        for _ in range(40):                      # Google video ko tayyar karta hai: ACTIVE hone tak ruko
            st = getattr(getattr(f, "state", None), "name", str(getattr(f, "state", "")))
            if "ACTIVE" in st:
                break
            if "FAILED" in st:
                raise RuntimeError("video upload fail")
            time.sleep(6)
            f = c.files.get(name=f.name)
        last = None
        mlist = gemini_model_list(c, True)
        for attempt in range(max(6, len(mlist) + 2)):
            m = mlist[attempt % len(mlist)]
            try:
                r = c.models.generate_content(model=m, contents=[f, prompt], config=types.GenerateContentConfig(
                    temperature=0.2, max_output_tokens=8192, response_mime_type="application/json"))
                mt = re.search(r"\{.*\}", r.text or "", re.DOTALL)
                d = json.loads(mt.group(0))
                USED.append(m + " (video dekha)")
                try:
                    c.files.delete(name=f.name)
                except Exception:
                    pass
                return d
            except Exception as e:
                last = e
                print(f"Video dekhne ki koshish {attempt + 1} ({m}): {str(e)[:150]}")
                time.sleep(min(60, 15 * (attempt + 1)))
        print("Video dekhna nahi ho paya:", str(last)[:150])
    except Exception as e:
        print("Video dekhna nahi ho paya:", str(e)[:200])
    return None


def review(sheet, ep_json, video_path=None):
    """Kadi PASS/FAIL jaanch. Do baar jaanchta hai: seedha FAIL tabhi jab DONO baar wahi galti (niyam number) mile;
    number dono ka ausat. Jawab samajh na aaye, sheet na mile ya cover pehla frame na ho toh PASS nahi."""
    bad = lambda why: {"pass": False, "score": 0, "hard_fails": [why], "fix_text": why, "text": f"❌ {why}", "cannot_check": []}
    main_sheet, end_sheet, first_check, machine = (tuple(sheet) + ({},))[:4] if isinstance(sheet, tuple) else (sheet, b"", "", {})
    if not main_sheet:
        return bad("check sheet nahi mili")
    sheets = [main_sheet] + ([end_sheet] if end_sheet else [])
    # teeno jaanch (2 baar chitra + asli video) ek saath, line se nahi: samay aadha
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as ex:
        f1, f2 = ex.submit(review_once, sheets, ep_json), ex.submit(review_once, sheets, ep_json)
        fw = ex.submit(watch_video, video_path, ep_json)
        runs = [f1.result(), f2.result()]
        watch = fw.result()
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
    # machine ki ginti AI ki raay se upar: kaali/ruki screen = niyam 5, awaaz/khamoshi = niyam 8
    for f in (machine or {}).get("fails", []):
        rule = 8 if any(w in f for w in ("awaaz", "khamoshi")) else 5
        hard.append({"rule": rule, "what": f"(machine jaanch) {f}", "fix": "us hisse ke shot/lines badlo ya chhota karo, VERSION badhao"})
    sc = {k: round(sum(r["scores"][k] for r in runs) / len(runs)) for k in SCORE_KEYS}
    total = sum(sc.values())
    watch_high = [pr for pr in ((watch or {}).get("problems") or [])[:6]
                  if str(pr.get("confidence", "")).lower() == "high" and pr.get("what")]
    # ek akeli "pakki" raay se video nahi rukta (free AI ghalat bhi ho sakta hai); 2 ya zyada pakki dikkatein = sudhaar zaroori
    ok = (not hard) and total >= PASS_SCORE and len(watch_high) < 2
    weak = [w for r in runs for w in (r.get("weak") or [])][:6]
    for pr in watch_high:
        weak.append({"what": f"(video dekha-suna {pr.get('time', '')}, {pr.get('kind', '')}) {pr['what']}", "fix": pr.get("fix", "")})
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
    for w in (machine or {}).get("warns", [])[:4]:
        lines.append(f"- ⚠️ (machine) {w}")
    if cant:
        lines.append("- ℹ️ Sirf tasveer se nahi dekh paya: " + "; ".join(cant))
    if runs[0].get("summary"):
        lines.append(str(runs[0]["summary"]))
    if watch and watch.get("summary"):
        lines.append("🎧 Asli video dekh-sunkar: " + str(watch["summary"]))
    fixes = [f"RULE {h.get('rule')}: {h.get('what')} -> {h.get('fix')}" for h in hard] + \
            [f"WEAK: {w.get('what')} -> {w.get('fix')}" for w in weak]
    if not hard and total >= PASS_SCORE and len(watch_high) >= 2:
        fixes.append("The real video (watched and heard) has 2+ sure problems; fix them (see WEAK lines above).")
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
        sheet = fetch_sheet(ep)
        bh = title_bhag() or re.sub(r"\D", "", os.path.basename(ep))
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as ex:      # Valmiki jaanch aur video jaanch saath-saath
            fs = ex.submit(story_check, ep_json, bh)
            verdict = review(sheet, ep_json, fetch_video(ep))
            sc_problems = fs.result()
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
    if verdict["pass"]:
        try:
            promote_engine(issue, branch, st)
        except Exception as e:
            print("promote nahi hua:", str(e)[:200])
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



def promote_engine(issue, branch, st):
    """PASS ke baad: is issue ke engine/SEEKH badlaav shared auto-video mein. Pehle sabhi purane episodes ki jaanch,
    peechhe backup tag, aur tabhi jab auto-video beech mein aage na badha ho."""
    files = [f for f in st.get("code_files", []) if os.path.exists(f)]
    if not files:
        return
    code = [f for f in files if is_code_path(f)]
    problems = []
    for f in code:
        try:
            compile(open(f, encoding="utf-8").read(), f, "exec")
        except SyntaxError as e:
            problems.append(f"{f}: {e}")
    import glob
    for ej in sorted(glob.glob("episodes/*/episode.json")):
        try:
            if '"SHOTS"' in open(ej, encoding="utf-8").read():
                problems += [f"{ej}: {x}" for x in SP.check(SP.load(ej))]
        except Exception as e:
            problems.append(f"{ej}: {str(e)[:100]}")
    if problems:
        comment(issue, "⛔ Engine badlaav shared engine mein **nahi** gaya: purane episodes ki jaanch mein dikkat aayi.\n- " +
                "\n- ".join(problems[:8]) + f"\n\nBadlaav sirf branch `{branch}` par hai.")
        return
    run(["git", "fetch", "--depth", "1", "origin", "auto-video"])
    head = run(["git", "rev-parse", "FETCH_HEAD"]).strip()
    if st.get("base") and head != st["base"]:
        comment(issue, f"⏸️ Engine badlaav taiyaar hai par auto-video beech mein aage badh chuka hai, isliye apne aap nahi daala. "
                       f"Badlaav branch `{branch}` par hai; Claude chat mein ye issue bhejiye, wo mila dega.")
        return
    import datetime
    tag = "engine-backup-" + datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    wt = tempfile.mkdtemp(prefix="promo_")
    try:
        run(["git", "worktree", "add", "--detach", wt, head])
        for f in files:
            os.makedirs(os.path.dirname(os.path.join(wt, f)) or wt, exist_ok=True)
            with open(f, encoding="utf-8") as src, open(os.path.join(wt, f), "w", encoding="utf-8") as dst:
                dst.write(src.read())
        run(["git", "-C", wt, "add", "-A"])
        if subprocess.run(["git", "-C", wt, "diff", "--cached", "--quiet"]).returncode == 0:
            return
        run(["git", "-C", wt, "-c", "user.name=github-actions[bot]", "-c", "user.email=github-actions[bot]@users.noreply.github.com",
             "commit", "-m", f"AI Helper (issue {issue}): engine/seekh badlaav, jaanch PASS ke baad"])
        run(["git", "tag", tag, head]); run(["git", "push", "origin", tag])
        run(["git", "-C", wt, "push", "origin", "HEAD:refs/heads/auto-video"])
        comment(issue, "🛠️ Engine/seekh ke badlaav jaanch PASS hone par **shared engine (auto-video) mein daal diye** gaye: " +
                       ", ".join(f"`{f}`" for f in files) + f".\nGalti nikle toh wapas jaane ke liye backup tag: `{tag}`.")
    except Exception as e:
        comment(issue, f"⚠️ Engine badlaav auto-video mein daalte waqt dikkat aayi, badlaav branch `{branch}` par safe hai.\n\n<sub>{str(e)[:200]}</sub>")
    finally:
        run(["git", "worktree", "remove", "--force", wt], check=False)


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
    os.environ["PATIENT"] = "1"      # shaant samay hai: Gemini ke liye zyada sabr
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


def mode_report():
    """Roz ka report: pichhle 24 ghante mein kya bana, kaun sa AI chala, asli views, aur agla kadam. Ek hi issue mein comment."""
    os.environ["NO_LOCAL"] = "1"          # report ke liye bhaari local AI na lagao
    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc).replace(tzinfo=None)
    since = (now - _dt.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"## 📊 Katha Chitra roz ka report — {now + _dt.timedelta(hours=5, minutes=30):%d %b %Y}", ""]
    try:
        runs = json.loads(run(["gh", "api", f"repos/{REPO}/actions/runs?per_page=100"]))["workflow_runs"]
        rc = {}
        for r in runs:
            if r["created_at"] >= since and r["conclusion"] in ("success", "failure"):
                k = r["name"]; rc.setdefault(k, [0, 0]); rc[k][0 if r["conclusion"] == "success" else 1] += 1
        lines.append("**Pichhle 24 ghante ke kaam** (theek / kharab):")
        lines += [f"- {k}: {a} / {b}" for k, (a, b) in sorted(rc.items())] or ["- kuch nahi chala"]
    except Exception as e:
        lines.append(f"- (runs nahi mile: {str(e)[:80]})")
    try:
        cms = json.loads(run(["gh", "api", f"repos/{REPO}/issues/comments?since={since}&per_page=100"]))
        ai = {}
        for c in cms:
            m = re.search(r"<sub>AI: (\S+)", c.get("body", ""))
            if m:
                ai[m.group(1)] = ai.get(m.group(1), 0) + 1
        lines += ["", "**Kaun sa AI chala:** " + (", ".join(f"{k} ×{v}" for k, v in sorted(ai.items(), key=lambda x: -x[1])) or "koi kaam nahi aaya")]
    except Exception:
        pass
    try:
        q = json.loads(run(["gh", "api", f"repos/{REPO}/issues?labels={QUEUE}&state=open", "-q", "[.[].number]"]) or "[]")
        lines.append(f"**'Baad-mein' queue mein:** {len(q)} kaam" + (f" ({', '.join('#' + str(n) for n in q)})" if q else ""))
    except Exception:
        pass
    st = VR.stats_text()
    if st.strip():
        lines += ["", "**Asli views (YouTube):**", "", st.strip()[:1800]]
    try:
        tip = ask("Below are the real YouTube stats of a new channel of Valmiki Ramayan Hindi Shorts (Katha Chitra). In 2-3 short lines of simple "
                  "Hinglish (everyday words), say which hook/title style seems to work best and one small thing to try in the next episode. "
                  "Do not change the Ramayan story. Do not invent numbers; if the data is too small say so.\n\n" + st[:2500], want_json=False)
        lines += ["", "**Agle episode ke liye salaah:** " + tip.strip()[:600]]
    except Exception:
        pass
    title = "📊 Roz ka report"
    num = run(["gh", "api", f"repos/{REPO}/issues?state=open&per_page=100", "-q", f'[.[]|select(.title=="{title}")|.number][0] // empty']).strip()
    if not num:
        num = run(["gh", "api", "-X", "POST", f"repos/{REPO}/issues", "-f", f"title={title}",
                   "-f", "body=Helper roz yahan apna report likhta hai. Yahan @ai mat likhna; kaam ke liye naya issue banao.", "-q", ".number"]).strip()
    comment(num, "\n".join(lines))


if __name__ == "__main__":
    try:
        {"task": mode_task, "queue": mode_queue, "daily": mode_daily, "report": mode_report}[sys.argv[1]]()
    except (Busy, ValueError) as e:      # free AI busy or kept sending broken answers: queue for the morning
        if os.environ.get("ISSUE_NUMBER"):
            queue_issue(os.environ["ISSUE_NUMBER"], str(e))
        sys.exit(0)
    except Exception as e:
        comment(os.environ.get("ISSUE_NUMBER", ""),
                "⚠️ Helper ke saath ek galti hui, kaam poora nahi hua. Yahin dobara `@ai ...` likhiye; "
                f"phir bhi na chale to ye issue Claude chat mein bhejiye.\n\n<sub>{str(e)[:300]}</sub>")
        raise
