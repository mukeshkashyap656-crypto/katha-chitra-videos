"""Katha Chitra auto-post.
YouTube: episode ki tarikh par shaam 7 baje IST. Pehle chale to private upload karke 7 baje par schedule.
Instagram: YouTube ke 1 din baad shaam 7 baje IST.
"""
import argparse, datetime, json, re, subprocess, sys, time
from composio_mcp import MCP
import post_youtube

EP = "../episodes.json"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
POST_TIME = datetime.time(19, 0)
MAX_WAIT = 90 * 60     # 7 baje se itni der pehle chale to 7 baje tak ruko
SCHEDULE_GAP = 5 * 60  # 7 baje mein itna samay bacha ho tabhi schedule karo


def now_ist():
    return datetime.datetime.now(IST)


def at_seven(day):
    return datetime.datetime.combine(day, POST_TIME, IST)


def save(eps, msg):
    json.dump(eps, open(EP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    subprocess.run(["git", "add", "episodes.json"], cwd="..", check=False)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd="..").returncode != 0:
        subprocess.run(["git", "commit", "-m", msg], cwd="..", check=False)
        for _ in range(3):
            if subprocess.run(["git", "push"], cwd="..").returncode == 0:
                return
            subprocess.run(["git", "pull", "--rebase"], cwd="..", check=False)
        raise SystemExit("episodes.json push nahi hua; dohri post se bachne ke liye ruk rahe hain")


def episode_day(e):
    try:
        return datetime.date.fromisoformat(e.get("date", ""))
    except ValueError:
        return None


def pending(eps):
    return [(k, eps[k]) for k in sorted(eps, key=lambda x: int(x))
            if eps[k].get("auto") and eps[k].get("status") != "posted" and episode_day(eps[k])]


def youtube_early(m, eps, k, e, now, dry):
    """YouTube upload. True = theek."""
    slot = at_seven(episode_day(e))
    checked, vid = post_youtube.find_existing(m, e["title"])
    if not checked:
        print(f"Bhag {k}: channel ki list nahi mili, dohri video se bachne ke liye upload roka")
        return False
    if vid:
        print(f"Bhag {k}: yeh video channel par pehle se hai ({vid}), dobara upload nahi")
        if not dry:
            e["youtube_id"] = vid
            e["youtube_pending"] = True    # neeche jaanch hogi ki public hai ya nahi
            save(eps, f"Bhag {k}: YouTube par pehle se tha ({vid})")
        return True
    early = (slot - now).total_seconds() > SCHEDULE_GAP
    # 7 baje se bilkul pehle: private daalo, neeche 7 baje public hoga
    privacy = "private" if now < slot else "public"
    ok, vid = post_youtube.upload(m, e, privacy=privacy, dry=dry)
    if not ok:
        return False
    if dry:
        return True
    e["youtube_id"] = vid
    if privacy == "private":
        e["youtube_pending"] = True
    save(eps, f"Bhag {k}: YouTube par upload hua ({vid}, {privacy})")
    if privacy == "private" and early:
        utc = slot.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if post_youtube.schedule(m, vid, utc):
            e["youtube_publish_at"] = utc
            save(eps, f"Bhag {k}: YouTube par 7 baje ke liye schedule")
        else:
            print(f"Bhag {k}: schedule nahi hua; 7 baje wali run ise public karegi")
    return True


def instagram(eps, k, e, dry):
    cmd = [sys.executable, "post_instagram.py", "--bhag", k] + (["--dry-run"] if dry else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-1500:], r.stderr[-500:])
    mm = re.search(r"POSTED media_id (\d+)", r.stdout)
    if mm and not dry:
        e["instagram_id"] = mm.group(1)
        save(eps, f"Bhag {k}: Instagram par post ho gaya ({mm.group(1)})")
    elif "ALREADY_POSTED" in r.stdout and not dry:
        e["instagram_id"] = "already"
        save(eps, f"Bhag {k}: Instagram par pehle se tha")
    elif not ("DRY_RUN" in r.stdout and dry):
        return "ALREADY_POSTED" in r.stdout and dry
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.date and not a.dry_run:
        # haath se date dene par bhi asli ghadi chalegi, taaki samay se pehle post na ho
        print("Note: asli post mein date input nahi maana jata")
    eps = json.load(open(EP, encoding="utf-8"))
    cache = {}

    def client():
        if "m" not in cache:
            cache["m"] = MCP()
        return cache["m"]

    def clock():
        if a.dry_run and a.date:
            return at_seven(datetime.date.fromisoformat(a.date)) - datetime.timedelta(hours=6)
        return now_ist()

    failed = []

    # 1) Aaj (ya chhooti hui purani tarikh) ki YouTube video upload
    for k, e in pending(eps):
        if episode_day(e) <= clock().date() and not e.get("youtube_id"):
            if not youtube_early(client(), eps, k, e, clock(), a.dry_run):
                failed.append(f"Bhag {k}: YouTube")

    # 2) 7 baje wala kaam paas ho to ruko
    if not a.dry_run:
        now = now_ist()
        slot = at_seven(now.date())
        due_today = any(
            (e.get("youtube_pending") and episode_day(e) == now.date()) or
            (e.get("youtube_id") and not e.get("instagram_id")
             and episode_day(e) + datetime.timedelta(days=1) == now.date())
            for _, e in pending(eps))
        wait = (slot - now).total_seconds()
        if due_today and 0 < wait <= MAX_WAIT:
            print(f"7 baje tak {int(wait // 60)} minute ruk rahe hain")
            time.sleep(wait + 20)

    # 3) YouTube public pakka karo, aur 1 din purane bhaag Instagram par
    for k, e in pending(eps):
        now = clock()
        if e.get("youtube_pending") and now >= at_seven(episode_day(e)) and not a.dry_run:
            if post_youtube.make_public(client(), e["youtube_id"]):
                e.pop("youtube_pending", None)
                save(eps, f"Bhag {k}: YouTube par public")
            else:
                failed.append(f"Bhag {k}: YouTube public nahi hua")
        ig_due = at_seven(episode_day(e) + datetime.timedelta(days=1))
        if e.get("youtube_id") and not e.get("youtube_pending") and not e.get("instagram_id") and now >= ig_due:
            if not instagram(eps, k, e, a.dry_run):
                failed.append(f"Bhag {k}: Instagram")
        if e.get("youtube_id") and not e.get("youtube_pending") and e.get("instagram_id") and not a.dry_run:
            e["status"] = "posted"
            save(eps, f"Bhag {k}: dono jagah post poora")

    if failed:
        print("FAIL:", failed)
        sys.exit(1)
    print("Theek")


if __name__ == "__main__":
    main()
