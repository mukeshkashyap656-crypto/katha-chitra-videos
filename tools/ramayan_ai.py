"""
Katha Chitra AI Helper - free (Gemini key se). Sirf Katha Chitra (Ramayan) ke liye.

Issue ya comment mein "@ai <kaam>" likho, jaise:
  "@ai Bhag 7 ka plan banao"            -> plans/ mein shot list + lines (pehle tay, phir banao)
  "@ai plans/bhag6 wala episode banao"   -> episodes/bhag6 banta hai, GitHub video render karta hai
  "@ai Ram ka chehra chhota hai, theek karo" -> usi issue ki branch par sudhaar + naya render

Har issue ki apni branch hoti hai: ai/issue-<number>. Video ban jaane par helper
check sheet dekh ke director check karta hai aur issue mein video ka link deta hai.
Render fail ho to khud 3 baar tak theek karke dobara chalata hai.
"""
import json
import os
import py_compile
import re
import subprocess
import sys
import tempfile
import time

from google import genai
from google.genai import types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

REPO = os.environ["GITHUB_REPOSITORY"]
BASE = "auto-video"
MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]
TEXT_EXT = (".py", ".json", ".md", ".sh", ".txt")
MAX_FILE_CHARS = 80000
MAX_FIX_ROUNDS = 3
STATE = "ai_state.json"


# ---------------- chhote kaam ----------------
def run(args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {r.stderr.strip()[:500]}")
    return r.stdout


def comment(issue, text):
    run(["gh", "issue", "comment", str(issue), "--repo", REPO, "--body", text], check=False)
    print(text)


def branch_for(issue):
    return f"ai/issue-{issue}"


def checkout_branch(branch):
    """Issue ki branch ho to uspe jao, warna auto-video se nayi banao."""
    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    if run(["git", "ls-remote", "--heads", "origin", branch]).strip():
        run(["git", "fetch", "--depth", "1", "origin", f"{branch}:{branch}"])
        run(["git", "checkout", branch])
    else:
        run(["git", "checkout", "-b", branch])


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(st):
    with open(STATE, "w") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)


def repo_files():
    files = {}
    for path in run(["git", "ls-files"]).splitlines():
        if not path.endswith(TEXT_EXT) or path.startswith("sfx/openverse/") or path == STATE:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                c = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        if len(c) <= MAX_FILE_CHARS:
            files[path] = c
    return files


# ---------------- Gemini ----------------
def client():
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip(),
                        http_options=types.HttpOptions(timeout=300000))


def ask(contents, want_json=True):
    c = client()
    last = None
    for attempt in range(8):
        m = MODELS[attempt % len(MODELS)]
        try:
            cfg = types.GenerateContentConfig(temperature=0.3, max_output_tokens=65536,
                                              response_mime_type="application/json" if want_json else None)
            res = c.models.generate_content(model=m, contents=contents, config=cfg)
            txt = (res.text or "").strip()
            if not want_json:
                if txt:
                    return txt
                raise ValueError("khaali jawab")
            mt = re.search(r"\{.*\}", txt, re.DOTALL)
            data = json.loads(mt.group(0) if mt else txt)
            if data.get("action") in ("change", "none"):
                data.setdefault("files", [])
                data.setdefault("summary", "")
                print("Jawab:", m)
                return data
            raise ValueError("action galat")
        except Exception as e:
            last = e
            w = min(60, 10 * (attempt + 1))
            print(f"Koshish {attempt + 1} ({m}) nahi chali: {e}. {w}s baad phir...")
            time.sleep(w)
    raise last or RuntimeError("Gemini se jawab nahi mila")


RULES = """You are the film director + Python engineer of the "Katha Chitra" YouTube channel
(Valmiki Ramayan Shorts in Hindi, 2D Indian folk-art storybook style). The repo renders each
episode on GitHub: episodes/<name>/episode.json (+ that episode's draw_assets.py and build_episode.py,
which import from template/lib) -> tools/make_episode.sh -> MP4. NIYAM.md holds every rule of the
owner: follow ALL of them strictly. Valmiki Ramayan only, nothing added or changed in the story.

Reply with ONLY valid JSON:
{"action": "change" | "none",
 "summary": "Hinglish, simple everyday words, short: kya kiya / kya jawab hai / owner ko kya karna hai",
 "files": [{"path": "...", "content": "THE COMPLETE FILE CONTENT"}]}

How to work:
- A NEW episode is planned first: write plans/<bhagN>_PLAN.md (shot list, every shot 2-3 s, who stands
  where, new character looks from Valmiki) and plans/<bhagN>_episode.json. Do NOT build the episode until
  the owner says the plan is OK / asks to build it ("pehle tay, phir banao").
- To BUILD an episode: create episodes/<bhagN>/episode.json (same keys as episodes/bhag5/episode.json:
  NAME, COVER_NAME, QUESTION, LINES id -> [hindi text, rate, pitch], VERSION) and that episode's
  draw_assets.py + build_episode.py, by copying the newest finished episode's scripts and changing them
  for the new shots, characters and background. Reuse template/lib functions that really exist; never
  call a function or file that does not exist in the repo.
- To FIX a render error or a look problem: change as little as possible, and bump VERSION in that
  episode.json by 1.
- Only these paths may be written: plans/... and episodes/... . Never anything else.
- Always return the FULL file, never a part, never "..." placeholders.
"""


def check_changes(changes, old):
    problems = []
    for it in changes:
        p, c = it.get("path", ""), it.get("content", "")
        if not p.startswith(("plans/", "episodes/")) or ".." in p:
            problems.append(f"{p}: sirf plans/ aur episodes/ mein likhne ki ijazat hai")
            continue
        o = old.get(p)
        if o is not None and len(c) < 0.6 * len(o):
            problems.append(f"{p}: nayi file purani se bahut chhoti hai (kati hui lagti hai) - poori file do")
        if p.endswith(".py"):
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as t:
                t.write(c)
            try:
                py_compile.compile(t.name, doraise=True)
            except py_compile.PyCompileError as e:
                problems.append(f"{p}: Python syntax galti: {str(e)[-300:]}")
            finally:
                os.unlink(t.name)
        if p.endswith(".json"):
            try:
                j = json.loads(c)
                if p.endswith("episode.json"):
                    if not j.get("NAME") or not isinstance(j.get("LINES"), dict) or not j["LINES"]:
                        problems.append(f"{p}: NAME aur LINES zaroori hain")
                    for k, v in (j.get("LINES") or {}).items():
                        if not (isinstance(v, list) and len(v) == 3):
                            problems.append(f"{p}: LINES[{k}] = [text, rate, pitch] hona chahiye")
            except ValueError as e:
                problems.append(f"{p}: JSON galat hai: {e}")
    return problems


def solve(task):
    old = repo_files()
    block = "\n\n".join(f"===== FILE: {p} =====\n{c}" for p, c in old.items())
    prompt = f"{RULES}\n\n# REPO FILES (branch as it is now)\n{block}\n\n# TASK\n{task}"
    for _ in range(3):
        data = ask(prompt)
        if data["action"] != "change" or not data["files"]:
            data["action"] = "none"
            return data
        problems = check_changes(data["files"], old)
        if not problems:
            return data
        print("Jaanch mein galti, dobara:", problems)
        prompt += "\n\n# YOUR ANSWER WAS REJECTED, fix and answer again:\n- " + "\n- ".join(problems)
    return {"action": "none", "files": [],
            "summary": "3 baar koshish ki par har baar jaanch mein galti mili, isliye kuch nahi badla. Ye issue Claude chat mein bhejiye."}


def write_and_push(data, branch, msg):
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
    before = run(["gh", "run", "list", "--repo", REPO, "--workflow", "make-video.yml", "--branch", branch,
                  "-L", "1", "--json", "databaseId", "-q", ".[0].databaseId"], check=False).strip()
    run(["gh", "workflow", "run", "make-video.yml", "--repo", REPO, "--ref", branch, "-f", f"episode={ep}"])
    run_id = ""
    for _ in range(30):
        time.sleep(10)
        run_id = run(["gh", "run", "list", "--repo", REPO, "--workflow", "make-video.yml", "--branch", branch,
                      "-L", "1", "--json", "databaseId", "-q", ".[0].databaseId"], check=False).strip()
        if run_id and run_id != before:
            break
    if not run_id or run_id == before:
        raise RuntimeError("Video ka run shuru nahi hua")
    ok = subprocess.run(["gh", "run", "watch", run_id, "--repo", REPO, "--exit-status", "-i", "30"],
                        capture_output=True, text=True).returncode == 0
    return run_id, ok


# ---------------- mode 1: @ai kaam ----------------
def mode_task():
    issue = os.environ["ISSUE_NUMBER"]
    branch = branch_for(issue)
    checkout_branch(branch)
    st = load_state()
    task = (f"Issue title: {os.environ.get('ISSUE_TITLE', '')}\n"
            f"Owner's message (Hinglish): {os.environ.get('REQUEST', '')}\n"
            f"Earlier work on this issue's branch: {json.dumps(st, ensure_ascii=False)}")
    data = solve(task)
    msg = data["summary"] or "Ho gaya."
    if data["action"] == "change":
        eps = write_and_push(data, branch, "")
        st.update({"issue": int(issue), "fix_rounds": 0})
        if eps:
            st["episode"] = sorted(eps)[0]
        save_state(st)
        run(["git", "add", STATE])
        run(["git", "commit", "-m", f"AI Helper (issue {issue}): {os.environ.get('ISSUE_TITLE', '')[:60]}"])
        run(["git", "push", "origin", branch])
        msg += f"\n\n📁 Badlaav branch `{branch}` par rakhe hain."
        if eps:
            msg += "\n🎬 Video banna shuru ho gaya (~5-10 min). Banne par yahin link aur director check milega."
            comment(issue, msg)
            render_loop(issue, branch, st)
            return
    comment(issue, msg)


# ---------------- mode 2: render khatam hua ----------------
def director_check(img_bytes, ep_json):
    prompt = ("You are the strict film director of Katha Chitra. This image is a contact sheet of the finished "
              "Ramayan Short (one frame every 0.25 s, left-to-right, top-to-bottom). Check it against the rules "
              "below and the episode lines. List only REAL problems you can see (cut-off people at edges, "
              "characters overlapping, changing looks, halo on humans, empty/black frames, subtitle covering "
              "faces, missing logo, missing subscribe widget at the end, wrong mood colour). Answer in Hinglish, "
              "short numbered list; if all is fine say so in one line.\n\n# RULES\n"
              + open("NIYAM.md", encoding="utf-8").read() + "\n\n# EPISODE\n" + ep_json)
    parts = [types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"), prompt]
    try:
        return ask(parts, want_json=False)
    except Exception as e:
        return f"(Director check nahi ho paya: {e})"


def render_loop(issue, branch, st):
    ep = st["episode"]
    for rnd in range(MAX_FIX_ROUNDS + 1):
        run_id, ok = start_render(branch, ep)
        run_url = f"https://github.com/{REPO}/actions/runs/{run_id}"
        if ok:
            deliver(issue, ep, run_url)
            return
        if rnd == MAX_FIX_ROUNDS:
            break
        log = run(["gh", "run", "view", run_id, "--repo", REPO, "--log-failed"], check=False)
        tail = "\n".join(re.sub(r"^[^\t]*\t[^\t]*\t\S+Z ", "", l) for l in log.splitlines()[-200:])
        data = solve(f"The render of {ep} FAILED. Fix the episode files so it renders. Bump VERSION.\n\n# FAILED LOG\n{tail}")
        if data["action"] != "change":
            comment(issue, f"❌ Video nahi bana aur main fix nahi dhoondh paya. [Run]({run_url})\n\n{data['summary']}")
            return
        write_and_push(data, branch, "")
        st["fix_rounds"] = rnd + 1
        save_state(st)
        run(["git", "add", STATE])
        run(["git", "commit", "-m", f"AI Helper: render fix {rnd + 1} for {ep}"])
        run(["git", "push", "origin", branch])
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
    msg = "✅ **Video ban gaya!**\n"
    k = 1
    if mp4:
        msg += f"\n{k}. Video: [{mp4}]({link(mp4)})"; k += 1
    for j in jpg:
        msg += f"\n{k}. Cover: [{j}]({link(j)})"; k += 1
    msg += f"\n{k}. Director check sheet: [check_sheet.jpg]({link('check_sheet.jpg')})"
    msg += f"\n\n(Link kholke **⋯ → Download** dabaiye. Ya [run]({run_url}) ke neeche **video** zip.)"
    msg += f"\n\n🎬 **Director check (AI):**\n{report}\n\nKuch theek karwana ho to yahin `@ai` likhkar bataiye."
    comment(issue, msg)


if __name__ == "__main__":
    {"task": mode_task}[sys.argv[1]]()
