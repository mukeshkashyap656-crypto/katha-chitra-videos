import argparse, datetime, json, re, subprocess, sys
from composio_mcp import MCP
import post_youtube

EP = "../episodes.json"


def save(eps, msg):
    json.dump(eps, open(EP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    subprocess.run(["git", "add", "episodes.json"], cwd="..", check=False)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd="..").returncode != 0:
        subprocess.run(["git", "commit", "-m", msg], cwd="..", check=False)
        for _ in range(3):
            if subprocess.run(["git", "push"], cwd="..").returncode == 0:
                break
            subprocess.run(["git", "pull", "--rebase"], cwd="..", check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    today = a.date or str(ist.date())
    eps = json.load(open(EP, encoding="utf-8"))
    todo = [k for k, e in eps.items() if e.get("auto") and e.get("status") != "posted" and e.get("date", "9999") <= today]
    print("Aaj", today, "post hone wale bhaag:", todo)
    failed = False
    m = MCP() if todo else None
    for k in sorted(todo, key=int):
        e = eps[k]
        if not e.get("youtube_id"):
            ok, vid = post_youtube.upload(m, e, dry=a.dry_run)
            if ok and not a.dry_run:
                e["youtube_id"] = vid
                save(eps, f"Bhag {k}: YouTube par post ho gaya ({vid})")
            elif not ok:
                print(f"Bhag {k}: YouTube FAIL"); failed = True
        if not e.get("instagram_id"):
            cmd = [sys.executable, "post_instagram.py", "--bhag", k] + (["--dry-run"] if a.dry_run else [])
            r = subprocess.run(cmd, capture_output=True, text=True)
            print(r.stdout[-1500:], r.stderr[-500:])
            mm = re.search(r"POSTED media_id (\d+)", r.stdout)
            if mm and not a.dry_run:
                e["instagram_id"] = mm.group(1)
                save(eps, f"Bhag {k}: Instagram par post ho gaya ({mm.group(1)})")
            elif "ALREADY_POSTED" in r.stdout and not a.dry_run:
                e["instagram_id"] = "already"
                save(eps, f"Bhag {k}: Instagram par pehle se tha")
            elif "DRY_RUN" in r.stdout:
                pass
            else:
                print(f"Bhag {k}: Instagram FAIL"); failed = True
        if e.get("youtube_id") and e.get("instagram_id") and not a.dry_run:
            e["status"] = "posted"
            save(eps, f"Bhag {k}: dono jagah post poora")
    if failed:
        sys.exit(1)


main()
