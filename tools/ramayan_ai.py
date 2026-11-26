"""
Katha Chitra AI Helper - free. Pehle Gemini, busy ho to OpenRouter ke free AI, phir doosre free AI. Sirf Katha Chitra (Ramayan).

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
import yaad as YD  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

REPO = os.environ["GITHUB_REPOSITORY"]
MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
MAX_FIX_ROUNDS = 5
STATE = "ai_state.json"
CONTEXT = ["NIYAM.md", "VIRAL.md", "VIRAL_LEARN.md", "FESTIVAL.md", "RESEARCH_24NOV.md", "KNOWLEDGE.md", "SEEKH.md", "YAAD.md", "SEEKH_ROZ.md", "BODY.md", "ANIMATION.md", "tools/engine/README.md"]


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


SHORT_RULES = "AI_NIYAM.md"     # chhoti niyam file; ye file hata do to purana tareeka (saari kitaabein) wapas
NEW_LESSON = "## Nayi seekh (26 Nov 2026 ke baad; AI ko yahi hissa jaata hai)"


def _read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def new_lessons():
    """SEEKH.md ka sirf naya hissa (chhoti file banne ke baad jo jooda)."""
    t = _read("SEEKH.md") if os.path.exists("SEEKH.md") else ""
    return t[t.index(NEW_LESSON):] if NEW_LESSON in t else ""


def short_rules():
    if not os.path.exists(SHORT_RULES):
        return _read("NIYAM.md")
    return _read(SHORT_RULES) + "\n\n" + new_lessons()


def task_bhags(task):
    nums = [title_bhag()] + re.findall(r"(?:bhag|भाग)[\s_-]*(\d{1,3})", task, re.I)
    out = []
    for n in nums:
        if str(n).isdigit() and int(n) not in out:
            out.append(int(n))
    return out[:3]


def context_files(task="", code=False):
    """Sirf zaroori cheezein: chhote niyam, aaj ki yaad, kahani ki list, chalu episode aur ek namoona."""
    tracked = sorted(p for p in run(["git", "ls-files", "plans", "episodes"]).splitlines() if p.endswith((".json", ".md")))
    if os.path.exists(SHORT_RULES):
        paths = [SHORT_RULES, "YAAD.md", "SEEKH_ROZ.md", "tools/engine/README.md",
                 "plans/STORY_QUEUE.json", "plans/SERIAL_REF.md", "plans/SERIAL_CHARACTERS.md"]
        if re.search(r"tyohar|festival|jayanti|त्योहार|जयंती", task, re.I):
            paths.append("FESTIVAL.md")
        if code:
            paths += ["BODY.md", "ANIMATION.md"]
        have = sorted({int(m.group(1)) for p in tracked for m in [re.match(r"episodes/bhag(\d+)/", p)] if m})
        want = task_bhags(task) or have[-1:]
        want = set(want) | {n - 1 for n in want} | ({8} if 8 in have else set(have[-1:]))   # pichhla bhaag + ek achha namoona
        for p in tracked:
            m = re.search(r"bhag(\d+)", p)
            folder = p.split("/")[1] if p.startswith("episodes/") else ""
            if (m and int(m.group(1)) in want) or (folder and not folder.startswith("bhag") and folder in task):
                paths.append(p)
    else:
        paths = CONTEXT + tracked
    files = {}
    for p in dict.fromkeys(paths):
        if os.path.exists(p):
            files[p] = _read(p)
    if os.path.exists(SHORT_RULES) and new_lessons():
        files["SEEKH.md (sirf naya hissa; poori file yahan nahi hai)"] = new_lessons()
    return files


# ---------------- posting ka haal: AI se nahi, seedha record se ----------------
def posting_record():
    raw = run(["gh", "api", f"repos/{REPO}/contents/episodes.json?ref=main", "-H", "Accept: application/vnd.github.raw+json"], check=False)
    try:
        eps = json.loads(raw)
        keys = sorted((k for k in eps if k.isdigit() and eps[k].get("date")), key=int)[-5:]
    except (ValueError, AttributeError, TypeError):
        return "POSTING RECORD abhi padh nahi paaye, isliye posting ka haal pata nahi."
    lines = []
    for k in keys:
        e = eps[k]
        if not e.get("youtube_id"):
            yt = "upload ka record nahi"
        elif e.get("youtube_pending"):
            yt = ("upload hua, " + (f"schedule record mein hai ({e['youtube_publish_at']} UTC)" if e.get("youtube_publish_at")
                  else "schedule ka record nahi") + ", public hona record mein nahi")
        else:
            yt = "video ID record mein hai"
        ig = "post ID record mein hai" if e.get("instagram_id") else "post ka record nahi"
        auto = "chalu" if e.get("auto") else "ruka hua"
        lines.append(f"Bhag {k} (tarikh {e['date']}, auto post {auto}, status {e.get('status', '?')}): YouTube - {yt}; Instagram - {ig}.")
    return "\n".join(lines) + "\n(Ye sirf posting file ka record hai; YouTube/Instagram kholkar milaan nahi kiya.)"


_POSTWORD = re.compile(r"post|upload|publish|schedule|youtube|insta|पोस्ट|अपलोड|यूट्यूब|इंस्टा", re.I)
_STATUSASK = re.compile(r"\?|\b(kya|kab|status|haal|batao|hua|hui|gaya|gayi)\b|क्या|कब|हाल|हुआ|गया", re.I)
_CHANGEASK = re.compile(r"bana|theek|thik|sudh|badl|badal|render|likh|jod|hata|mita|delete|karo|kar do|kardo|chalao|bhejo|karna|karni|jaye|jaaye|"
                        r"daal|dalo|rok|fix|change|add|remove|बना|ठीक|सुधार|बदल|लिख|जोड़|हटा|करो|कर दो|चलाओ|भेजो|डाल|रोक", re.I)


def owner_words(request):
    return re.sub(r"@ai\b", " ", request.split("---- Pichli baat-cheet")[0], flags=re.I).strip()


def status_question(request):
    t = owner_words(request)
    return bool(t) and len(t) <= 200 and bool(_POSTWORD.search(t)) and bool(_STATUSASK.search(t)) and not _CHANGEASK.search(t)


# ---------------- AI: pehle Gemini, busy ho to OpenRouter ke free model ----------------
_LIVE = {}


def live_gemini_models(c):
    """Google se abhi chalte models: ("flash" wale tez, "pro" wale zyada sochne wale). Naam badle tab bhi helper na ruke."""
    if "m" not in _LIVE:
        try:
            names = [m.name.split("/")[-1] for m in c.models.list()
                     if "generateContent" in (getattr(m, "supported_actions", None) or ["generateContent"])]
            bad = ("gemini-2.5-pro", "image", "tts", "live", "audio", "thinking-exp", "preview-0", "embed", "vision", "robotics", "computer")
            ok = [n for n in names if not any(x in n for x in bad)]
            _LIVE["m"] = sorted((n for n in ok if "flash" in n), reverse=True)[:4]
            _LIVE["pro"] = sorted((n for n in ok if "pro" in n), reverse=True)[:2]
        except Exception as e:
            print("Gemini model list nahi mili:", str(e)[:100])
            _LIVE["m"], _LIVE["pro"] = [], []
    return _LIVE["m"]


FAST = False    # sirf chhote sawal ka jawab: sabse halka model pehle, atke to jaldi hato


_DEAD = set()   # jo model 404 "no longer available" bole (jaise gemini-2.5-pro): is run mein dobara kabhi nahi


def gemini_model_list(c, hard=False):
    out = [m for m in MODELS if m not in _DEAD]
    for m in live_gemini_models(c):
        if m not in out:
            out.append(m)
    if hard:     # mushkil kaam (episode likhna, jaanch, video dekhna): pehle sabse zyada sochne wala "pro" model, free limit kam hai toh flash par
        out = [m for m in _LIVE.get("pro", []) if m not in out[:0]] + out
    if FAST:
        out = sorted(out, key=lambda m: "lite" not in m)
    if hard:     # likhna/sudhaarna/jaanchna: "lite" model kabhi nahi
        return [m for m in out if m not in _DEAD and "lite" not in m]
    return [m for m in out if m not in _DEAD] or out


def gemini(contents, want_json, hard=False):
    c = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip(), http_options=types.HttpOptions(timeout=20000 if FAST else 120000))
    mlist = gemini_model_list(c, hard)
    cfg = types.GenerateContentConfig(temperature=0.3, max_output_tokens=32768,
                                      response_mime_type="application/json" if want_json else None)
    last = None
    patient = os.environ.get("PATIENT") == "1"      # shaant samay (queue) mein sabr; warna jaldi hatke doosre AI par
    if not mlist:
        raise Busy("Gemini: koi achha model nahi mila")
    for attempt in range(max(6, len(mlist) + 2) if patient else max(3, len(mlist) if hard else 0)):
        if not mlist:
            break
        m = mlist[attempt % len(mlist)]
        try:
            txt = (c.models.generate_content(model=m, contents=contents, config=cfg).text or "").strip()
            if txt:
                print("Jawab:", m); USED.append(m)
                return txt
            raise ValueError("khaali jawab")
        except Exception as e:
            last = e
            if "404" in str(e) or "NOT_FOUND" in str(e):
                _DEAD.add(m)
                mlist = [x for x in mlist if x not in _DEAD] or ([] if hard else mlist)
                print(f"Gemini {m} ab nahi milta: hata diya.")
                continue
            busy = any(x in str(e) for x in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "overloaded"))
            w = min(90, (20 if busy else 8) * (attempt + 1)) if patient else (0 if FAST else (3 if busy else 2) * (attempt + 1))
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
                try:
                    txt = (r.json()["choices"][0]["message"]["content"] or "").strip()
                except (KeyError, IndexError, TypeError, ValueError):
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]!r}")
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
                  ["nvidia/nemotron-3-ultra-550b-a55b", "mistralai/mistral-large-4-1t-a52b"], p, j)


def zai(p, j):
    return _extra("ZAI", "https://api.z.ai/api/paas/v4/chat/completions", "ZAI_API_KEY",
                  ["glm-4.7-flash", "glm-4.5-flash"], p, j)


# ---------------- bina chaabi wale reserve raaste (25 Nov 2026) ----------------
# Inhe sirf public repo ki baatein jaati hain. Free model jawab ko log / seekhne mein istemal kar sakte hain.
def _keyless(name, base, models, prompt_text, want_json):
    last = None
    for m in models:
        try:
            r = requests.post(base + "/chat/completions", timeout=120,
                              json={"model": m, "temperature": 0.3, "messages": [{"role": "user", "content": prompt_text}]})
            try:
                txt = (r.json()["choices"][0]["message"]["content"] or "").strip()
            except (KeyError, IndexError, TypeError, ValueError):
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]!r}")
            if txt:
                print(f"Jawab ({name}):", m); USED.append(f"{name} {m}")
                return txt
            raise RuntimeError("khaali jawab")
        except Exception as e:
            last = e
            print(f"{name} {m} nahi chala: {str(e)[:200]}")
    raise Busy(f"{name}: {str(last)[:200]}")


OVH_URL = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"      # OVHcloud: bina chaabi, 2 sawaal/minute har model
KILO_URL = "https://ai-gateway.kilo.ai/api/v1"                     # Kilo: bina chaabi, fre
