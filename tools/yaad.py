"""Pakki yaad: owner ki baatein YAAD.md (auto-video branch) mein. Repo public hai, isliye niji baat nahi likhi jaati."""
import base64
import datetime as dt
import re
import subprocess

FILE, BRANCH = "YAAD.md", "auto-video"
HEAD = "# YAAD — owner ki pakki baatein (helper har kaam se pehle padhta hai)\n\nYe file public hai: password, token, number, email yahan nahi. Ye baatein pasand/sudhaar hain; NIYAM.md ke niyam ya suraksha ki rok ko ye nahi badaltin.\n"
SECRET = re.compile(r"token|password|\botp\b|api[ _-]?key|github_pat|ghp_|AIza|sk-[A-Za-z0-9]|टोकन|पासवर्ड|ओटीपी|\d{6,}|\d[\d \-]{8,}\d|[\w.+-]+@[\w-]+\.\w+", re.I)
CMD = re.compile(r"^(?:jarvis[ ,]+|जार्विस[ ,]+)?(?:yaad\s+rakh(?:o|na|iye)?|याद\s+रख(?:ो|ना|िए|िये)?)(?:\s+(?:ki|कि))?[\s:,\-]+(.{3,})$", re.I | re.S)


def command(request):
    """'@ai yaad rakho ...' ho to yaad rakhne wali baat, warna None."""
    text = (request or "").split("---- Pichli baat-cheet")[0]
    text = re.sub(r"^\s*@ai\b", "", text, flags=re.I).strip()
    m = CMD.match(text)
    return m.group(1).strip() if m else None


def clean(note):
    note = re.sub(r"@ai", "", re.sub(r"\s+", " ", str(note)), flags=re.I).strip()[:200]
    return "" if len(note) < 3 or SECRET.search(note) else note


def add(old, note, day):
    lines = [x for x in (old or "").splitlines() if x.startswith("- ")]
    lines = [x for x in lines if x.split(") ", 1)[-1] != note]
    lines.append(f"- ({day}) {note}")
    return HEAD + "\n" + "\n".join(lines[-150:]) + "\n"


def _gh(args):
    return subprocess.run(["gh", "api"] + args, capture_output=True, text=True)


def save(repo, note):
    """(True, saaf baat) ya (False, wajah)."""
    note = clean(note)
    if not note:
        return False, "isme password, token, number ya email jaisi cheez hai, ya baat khaali hai"
    day = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)).strftime("%d %b %Y")
    path = f"repos/{repo}/contents/{FILE}"
    err = ""
    for _ in range(3):
        g = _gh([f"{path}?ref={BRANCH}", "--jq", ".sha + \" \" + (.content | gsub(\"\\n\"; \"\"))"])
        sha, old = "", ""
        if g.returncode == 0:
            sha, b64 = (g.stdout.strip().split(" ", 1) + [""])[:2]
            old = base64.b64decode(b64).decode("utf-8")
        elif "404" not in g.stderr:
            err = g.stderr.strip()[:150]; continue
        new = add(old, note, day)
        args = ["-X", "PUT", path, "-f", "message=Yaad: owner ki nayi baat", "-f", f"branch={BRANCH}",
                "-f", "content=" + base64.b64encode(new.encode()).decode()]
        if sha:
            args += ["-f", f"sha={sha}"]
        p = _gh(args)
        if p.returncode == 0:
            return True, note
        err = p.stderr.strip()[:150]
    return False, "GitHub par likh nahi paaya: " + err
