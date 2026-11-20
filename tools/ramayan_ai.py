"""
Katha Chitra AI Helper - free (Gemini key se; Gemini busy ho to OpenRouter ke free AI se). Sirf Katha Chitra (Ramayan).

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
CONTEXT = ["NIYAM.md", "tools/engine/README.md"]


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
    c = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip(), http_options=types.HttpOptions(timeout=240000))
    cfg = types.GenerateContentConfig(temperature=0.3, max_output_tokens=32768,
                                      response_mime_type="application/json" if want_json else None)
    last = None
    for attempt in range(9):
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


def ask(prompt_text, image=None, want_json=True):
    contents = [types.Part.from_bytes(data=image, mime_type="image/jpeg"), prompt_text] if image else prompt_text
    try:
        txt = gemini(contents, want_json)
    except Busy:
        if image:   # tasveer dekhna sirf Gemini se
            raise
        txt = openrouter(prompt_text, want_json)
    if not want_json:
        return txt
    mt = re.search(r"\{.*\}", txt, re.DOTALL)
    data = json.loads(mt.group(0) if mt else txt)
    if data.get("action") not in ("change", "none"):
        raise ValueError("action galat")
    data.setdefault("files", []); data.setdefault("summary", ""); data.setdefault("render", False)
    return data


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


# ---------------- mode: @ai kaam ----------------
def mode_task():
    issue = os.environ["ISSUE_NUMBER"]
    branch = f"ai/issue-{issue}"
    checkout_branch(branch)
    st = load_state()
    task = (f"Issue title: {os.environ.get('ISSUE_TITLE', '')}\n"
            f"Owner's message (Hinglish): {os.environ.get('REQUEST', '')}\n"
            f"Earlier work on this issue's branch: {json.dumps(st, ensure_ascii=False)}")
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
            deliver(issue, ep, run_url)
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


def deliver(issue, ep, run_url):
    rb = "render-" + os.path.basename(ep)
    run(["git", "fetch", "--depth", "1", "origin", f"{rb}:refs/remotes/origin/{rb}"])
    ref = f"origin/{rb}"
    names = run(["git", "ls-tree", "--name-only", ref]).split()
    mp4 = next((n for n in names if n.endswith(".mp4")), None)
    jpg = [n for n in names if n.endswith(".jpg") and n != "check_sheet.jpg"]
    sheet = subprocess.run(["git", "show", f"{ref}:check_sheet.jpg"], capture_output=True).stdout
    with open(f"{ep}/episode.json", encoding="utf-8") as f:
        ep_json = f.read()
    report = director_check(sheet, ep_json) if sheet else "(check sheet nahi mili)"
    link = lambda n: f"https://github.com/{REPO}/blob/{rb}/{n}"
    msg = "✅ **Video ban gaya!** (cover video ke pehle frame par bhi laga hai)\n"
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


if __name__ == "__main__":
    try:
        {"task": mode_task}[sys.argv[1]]()
    except Busy as e:
        comment(os.environ.get("ISSUE_NUMBER", ""),
                "⏳ Free AI abhi busy hai (Google ka server bheed mein hai / aaj ki free limit khatam). "
                "Thodi der baad (ya subah) yahin likhiye: `@ai dobara koshish karo`.\n\n"
                f"<sub>{str(e)[:200]}</sub>")
        sys.exit(1)
    except Exception as e:
        comment(os.environ.get("ISSUE_NUMBER", ""),
                "⚠️ Helper ke saath ek galti hui, kaam poora nahi hua. Yahin dobara `@ai ...` likhiye; "
                f"phir bhi na chale to ye issue Claude chat mein bhejiye.\n\n<sub>{str(e)[:300]}</sub>")
        raise
