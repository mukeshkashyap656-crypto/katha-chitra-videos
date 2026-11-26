"""Katha Chitra — sab channel par video upload (YouTube + Instagram + episodes.json update).
publish.yml se chalta hai; ramayan_ai.py PASS hone par trigger karta hai.
Koi key na ho toh wo channel skip ho jaata hai, baaki chalte rehte hain."""
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse

REPO = os.environ.get("GITHUB_REPOSITORY", "")
IST_OFFSET = 5 * 3600 + 30 * 60  # +5:30


def run(args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {r.stderr.strip()[:500]}")
    return r.stdout


def comment(issue, text):
    if not issue:
        return
    run(["gh", "issue", "comment", str(issue), "--repo", REPO, "--body", text], check=False)
    print(text)


# ---- YouTube upload ----
def yt_get_access_token():
    cid = os.environ.get("YT_CLIENT_ID", "")
    secret = os.environ.get("YT_CLIENT_SECRET", "")
    refresh = os.environ.get("YT_REFRESH_TOKEN", "")
    if not (cid and refresh):
        return None
    data = urllib.parse.urlencode({
        "client_id": cid, "client_secret": secret,
        "refresh_token": refresh, "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data,
                                headers={"Content-Type": "application/x-www-form-urlencoded"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp["access_token"]


def yt_upload(video_path, title, description, tags, publish_at=None):
    """YouTube Data API v3 se video upload. Returns video_id ya None."""
    token = yt_get_access_token()
    if not token:
        print("YouTube: YT_CLIENT_ID / YT_REFRESH_TOKEN nahi hai, skip")
        return None

    snippet = {"title": title[:100], "description": description, "tags": tags[:30],
               "categoryId": "22", "defaultLanguage": "hi", "defaultAudioLanguage": "hi"}
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    if publish_at:
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at

    metadata = json.dumps({"snippet": snippet, "status": status}).encode()

    # Step 1: resumable upload init
    init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    req = urllib.request.Request(init_url, data=metadata, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4",
    })
    resp = urllib.request.urlopen(req, timeout=60)
    upload_url = resp.headers["Location"]

    # Step 2: upload video bytes
    file_size = os.path.getsize(video_path)
    with open(video_path, "rb") as f:
        req2 = urllib.request.Request(upload_url, data=f.read(), headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size),
        })
        resp2 = json.loads(urllib.request.urlopen(req2, timeout=300).read())

    vid = resp2.get("id")
    print(f"YouTube upload done: {vid}")
    return vid


# ---- Instagram Reel post ----
def ig_upload(video_path, caption):
    """Instagram Graph API se Reel post. Returns media_id ya None.
    Video pehle accessible URL par hona chahiye — GitHub raw link 504 deta hai,
    isliye pehle tmpfiles.org jaisi jagah upload karte hain."""
    token = os.environ.get("IG_ACCESS_TOKEN", "")
    ig_user = os.environ.get("IG_USER_ID", "")
    if not (token and ig_user):
        print("Instagram: IG_ACCESS_TOKEN / IG_USER_ID nahi hai, skip")
        return None

    # Video ko temporary public URL par upload karo
    video_url = _upload_temp_video(video_path)
    if not video_url:
        print("Instagram: temporary video URL nahi bana, skip")
        return None

    # Step 1: Create media container
    data = urllib.parse.urlencode({
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": token,
    }).encode()
    req = urllib.request.Request(f"https://graph.facebook.com/v21.0/{ig_user}/media", data=data)
    resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
    container_id = resp.get("id")
    if not container_id:
        print(f"Instagram container fail: {resp}")
        return None

    # Step 2: Wait for video processing
    for _ in range(30):
        time.sleep(10)
        check = json.loads(urllib.request.urlopen(
            f"https://graph.facebook.com/v21.0/{container_id}?fields=status_code&access_token={token}",
            timeout=30).read())
        if check.get("status_code") == "FINISHED":
            break
        if check.get("status_code") == "ERROR":
            print(f"Instagram processing error: {check}")
            return None
    else:
        print("Instagram: video processing timeout")
        return None

    # Step 3: Publish
    pub_data = urllib.parse.urlencode({
        "creation_id": container_id,
        "access_token": token,
    }).encode()
    req3 = urllib.request.Request(f"https://graph.facebook.com/v21.0/{ig_user}/media_publish", data=pub_data)
    resp3 = json.loads(urllib.request.urlopen(req3, timeout=60).read())
    media_id = resp3.get("id")
    print(f"Instagram post done: {media_id}")
    return media_id


def _upload_temp_video(video_path):
    """Video ko temporary public URL par daalo (file.io — free, 1 download ke baad delete)."""
    import http.client
    boundary = "----KathaChitraBoundary"
    filename = os.path.basename(video_path)
    with open(video_path, "rb") as f:
        file_data = f.read()
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
        f"Content-Type: video/mp4\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    conn = http.client.HTTPSConnection("file.io", timeout=120)
    conn.request("POST", "/?expires=1h", body=body,
                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                          "Content-Length": str(len(body))})
    resp = json.loads(conn.getresponse().read())
    conn.close()
    if resp.get("success"):
        print(f"Temp upload: {resp.get('link')}")
        return resp.get("link")
    print(f"Temp upload fail: {resp}")
    return None


# ---- episodes.json update ----
def update_episodes_json(bhag, youtube_id=None, instagram_id=None, publish_at=None):
    """main branch par episodes.json mein record daalo."""
    try:
        raw = run(["gh", "api", f"repos/{REPO}/contents/episodes.json?ref=main",
                   "-H", "Accept: application/vnd.github.raw+json"], check=False)
        eps = json.loads(raw) if raw.strip().startswith("{") else {}
    except Exception:
        eps = {}

    key = str(bhag)
    if key not in eps:
        eps[key] = {}
    import datetime
    eps[key]["date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    eps[key]["auto"] = True
    if youtube_id:
        eps[key]["youtube_id"] = youtube_id
        eps[key]["youtube_pending"] = True
        if publish_at:
            eps[key]["youtube_publish_at"] = publish_at
    if instagram_id:
        eps[key]["instagram_id"] = instagram_id
    eps[key]["status"] = "posted"

    import base64
    content_b64 = base64.b64encode(json.dumps(eps, indent=2, ensure_ascii=False).encode()).decode()
    try:
        existing = json.loads(run(["gh", "api", f"repos/{REPO}/contents/episodes.json?ref=main"]))
        sha = existing.get("sha", "")
    except Exception:
        sha = ""

    import tempfile
    payload = {"message": f"Bhag {bhag} posting record update", "content": content_b64, "branch": "main"}
    if sha:
        payload["sha"] = sha
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        f.flush()
        tmppath = f.name
    try:
        run(["gh", "api", f"repos/{REPO}/contents/episodes.json", "-X", "PUT", "--input", tmppath])
        print(f"episodes.json updated for Bhag {bhag}")
    except Exception as e:
        print(f"episodes.json update fail: {e}")
    finally:
        os.unlink(tmppath)


# ---- Main: sab channel par publish ----
def main():
    episode = os.environ.get("EPISODE", "")  # e.g. episodes/bhag7
    bhag = os.environ.get("BHAG", "")        # e.g. 7
    issue = os.environ.get("ISSUE", "")       # issue number
    test_mode = os.environ.get("TEST_MODE", "") == "1"

    if not episode:
        print("EPISODE env nahi hai"); sys.exit(1)
    if not bhag:
        import re
        bhag = re.sub(r"\D", "", os.path.basename(episode)) or "0"

    # Rendered video fetch karo
    branch = f"render-{os.path.basename(episode)}"
    print(f"Video fetch: branch {branch}")
    try:
        run(["git", "fetch", "--depth", "1", "origin", branch])
    except Exception:
        print(f"Branch {branch} nahi mila, kya video bana hai?")
        comment(issue, f"Video branch `{branch}` nahi mila. Pehle video banao, phir publish.")
        sys.exit(1)

    os.makedirs("publish_out", exist_ok=True)
    run(["git", "--work-tree=publish_out", "checkout", "FETCH_HEAD", "--", "."], check=False)
    # alternative: git archive
    run(["bash", "-c", "cd publish_out && git archive FETCH_HEAD | tar -x"], check=False)

    # Video file dhundho
    video = None
    cover = None
    for root, dirs, files in os.walk("publish_out"):
        for f in files:
            if f.endswith(".mp4") and not video:
                video = os.path.join(root, f)
            if (f.endswith(".jpg") or f.endswith(".png")) and "cover" in f.lower():
                cover = os.path.join(root, f)
    if not video:
        # out/ folder mein bhi dekho
        for root, dirs, files in os.walk("publish_out/out"):
            for f in files:
                if f.endswith(".mp4"):
                    video = os.path.join(root, f)
                    break

    if not video:
        print("Koi .mp4 file nahi mili!")
        comment(issue, "Video file (.mp4) render branch mein nahi mili.")
        sys.exit(1)

    print(f"Video: {video} ({os.path.getsize(video) / 1024 / 1024:.1f} MB)")
    if cover:
        print(f"Cover: {cover}")

    # Title aur description banao
    title = f"रामायण · भाग {bhag} 😱 #shorts"
    description = (f"भाग {bhag} — वाल्मीकि रामायण हिंदी\n\n"
                   f"Katha Chitra — Ramayan Shorts\n"
                   f"#ramayan #valmikiramayan #kathachitra #shorts")
    tags = ["ramayan", "valmiki ramayan", "hindi", "shorts", "katha chitra",
            "रामायण", "वाल्मीकि", "राम", "सीता"]
    caption = f"रामायण · भाग {bhag}\n\n#ramayan #valmikiramayan #kathachitra #hindishorts #ram"

    # Publish time: aaj ya kal shaam 7 baje IST
    import datetime
    now_utc = datetime.datetime.utcnow()
    ist_now = now_utc + datetime.timedelta(seconds=IST_OFFSET)
    target_ist = ist_now.replace(hour=19, minute=0, second=0, microsecond=0)
    if ist_now.hour >= 18:  # 6 PM ke baad ho toh kal 7 PM
        target_ist += datetime.timedelta(days=1)
    publish_at_utc = target_ist - datetime.timedelta(seconds=IST_OFFSET)
    publish_at = publish_at_utc.strftime("%Y-%m-%dT%H:%M:%S.0Z")

    if test_mode:
        print(f"TEST MODE: upload nahi hoga, sirf dry run")
        print(f"  YouTube title: {title}")
        print(f"  Publish at: {publish_at} UTC (7 PM IST)")
        print(f"  Instagram caption: {caption}")
        print(f"  Video size: {os.path.getsize(video)} bytes")
        comment(issue, f"🧪 **Test mode** — sab taiyaar hai:\n"
                       f"- Video: {os.path.basename(video)} ({os.path.getsize(video) / 1024 / 1024:.1f} MB)\n"
                       f"- YouTube title: {title}\n"
                       f"- Schedule: {publish_at} UTC (7 PM IST)\n"
                       f"- Instagram caption ready\n"
                       f"- YouTube key: {'hai' if os.environ.get('YT_CLIENT_ID') else 'NAHI'}\n"
                       f"- Instagram key: {'hai' if os.environ.get('IG_ACCESS_TOKEN') else 'NAHI'}")
        return

    results = []

    # 1. YouTube upload
    try:
        yt_id = yt_upload(video, title, description, tags, publish_at)
        if yt_id:
            results.append(f"✅ YouTube: uploaded (ID: {yt_id}), {publish_at} UTC ko public hoga")
        else:
            results.append("⏭️ YouTube: key nahi, skip")
    except Exception as e:
        results.append(f"❌ YouTube fail: {str(e)[:200]}")
        yt_id = None

    # 2. Instagram Reel
    try:
        ig_id = ig_upload(video, caption)
        if ig_id:
            results.append(f"✅ Instagram: posted (ID: {ig_id})")
        else:
            results.append("⏭️ Instagram: key nahi ya upload fail, skip")
    except Exception as e:
        results.append(f"❌ Instagram fail: {str(e)[:200]}")
        ig_id = None

    # 3. episodes.json update
    try:
        update_episodes_json(bhag, youtube_id=yt_id, instagram_id=ig_id, publish_at=publish_at)
        results.append("✅ episodes.json updated")
    except Exception as e:
        results.append(f"❌ episodes.json fail: {str(e)[:200]}")

    summary = "\n".join(results)
    print(summary)
    comment(issue, f"📤 **Bhag {bhag} posting result:**\n\n{summary}")


if __name__ == "__main__":
    main()
