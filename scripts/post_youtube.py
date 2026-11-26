import json
from composio_mcp import MCP

YT_ACCOUNT = "youtube_gair-habab"      # Katha Chitra (@kathachitra_123)
REPO = "mukeshkashyap656-crypto/katha-chitra-videos"
MARK = "KC_RESULT="

# Workbench ke andar chalne wale chhote helper
HELPERS = '''
import json
def g(o):
    return o[0] if isinstance(o, tuple) else o
def walk(x):
    if isinstance(x, dict):
        yield x
        for v in x.values():
            yield from walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from walk(v)
def out(**kw):
    print("KC_RESULT=" + json.dumps(kw))
'''


def parse_result(text):
    """Workbench ke jawab se KC_RESULT wali line nikalo. Na mile to None."""
    try:
        stdout = json.loads(text)["data"]["stdout"]
    except (ValueError, KeyError, TypeError):
        stdout = text
    for line in reversed(str(stdout).splitlines()):
        if line.startswith(MARK):
            return json.loads(line[len(MARK):])
    return None


def wb(m, code, label):
    r = m.call("COMPOSIO_REMOTE_WORKBENCH", {"code_to_execute": HELPERS + code, "thought": label, "current_step": label})
    text = "".join(c.get("text", "") for c in r.get("content", []))
    res = parse_result(text)
    print(label, ":", res if res is not None else "jawab samajh nahi aaya: " + text[-600:])
    return res or {"ok": False, "unknown": True}


def find_existing(m, title):
    """Isi title ki video channel par pehle se hai kya (private bhi). (jaanch_hui, video_id)"""
    code = f'''
title = {title!r}
res, err = run_composio_tool("YOUTUBE_LIST_CHANNEL_VIDEOS", {{"mine": True, "maxResults": 20}}, account="{YT_ACCOUNT}")
lists = [d["items"] for d in walk(res) if isinstance(d.get("items"), list)]
if err or not lists:
    out(ok=False, error=str(err)[:300])
else:
    vid = None
    for it in lists[0]:
        s = it.get("snippet", {{}})
        if s.get("title") == title:
            vid = s.get("resourceId", {{}}).get("videoId")
            break
    out(ok=True, id=vid)
'''
    res = wb(m, code, "YOUTUBE_CHECK_EXISTING")
    return res.get("ok", False), res.get("id")


def upload(m, ep, privacy="public", dry=False):
    """Video daalo. (ok, video_id) lautata hai."""
    args = {"title": ep["title"], "description": ep["caption"], "tags": ep.get("tags", []),
            "categoryId": "24", "privacyStatus": privacy}
    code = f'''
import os, urllib.request
fn = {ep["file"]!r}
meta = g(proxy_execute("GET", "/repos/{REPO}/contents/" + fn, "github", query_params={{"ref": "main"}}))
p = "/home/user/" + os.path.basename(fn)
urllib.request.urlretrieve(meta["download_url"], p)
size = os.path.getsize(p)
if size != {int(ep["size"])}:
    out(ok=False, error="SIZE_MISMATCH %s" % size)
else:
    up = g(upload_local_file(p))
    s3 = up.get("s3key") if isinstance(up, dict) else up
    if not s3:
        out(ok=False, error="s3key nahi mila")
    elif {bool(dry)}:
        out(ok=True, dry=True)
    else:
        ARGS = json.loads({json.dumps(args, ensure_ascii=False)!r})
        ARGS["videoFile"] = {{"name": os.path.basename(fn), "mimetype": "video/mp4", "s3key": s3}}
        res, err = run_composio_tool("YOUTUBE_MULTIPART_UPLOAD_VIDEO", ARGS, account="{YT_ACCOUNT}")
        vid = None
        for d in walk(res):
            v = d.get("video")
            if isinstance(v, dict) and v.get("id"):
                vid = v["id"]
                break
            if d.get("kind") == "youtube#video" and d.get("id"):
                vid = d["id"]
                break
        out(ok=bool(vid), id=vid, error=str(err)[:300])
'''
    res = wb(m, code, "YOUTUBE_UPLOAD")
    return res.get("ok", False), res.get("id")


def schedule(m, vid, publish_at_utc):
    """Private video ko tay samay par YouTube khud public kare. True = schedule ho gaya."""
    body = {"id": vid, "status": {"privacyStatus": "private", "publishAt": publish_at_utc,
                                  "selfDeclaredMadeForKids": False, "embeddable": True,
                                  "license": "youtube", "publicStatsViewable": True}}
    code = f'''
data, err = proxy_execute("PUT", "https://www.googleapis.com/youtube/v3/videos", "youtube",
                          query_params={{"part": "status"}}, body=json.loads({json.dumps(body)!r}))
ok = any(d.get("publishAt") for d in walk(data))
out(ok=ok and not err, error=str(err)[:300], res="" if ok else str(data)[:300])
'''
    return wb(m, code, "YOUTUBE_SCHEDULE").get("ok", False)


def make_public(m, vid):
    """Video public na ho to public karo. True = ab public hai."""
    code = f'''
def status():
    res, err = run_composio_tool("YOUTUBE_GET_VIDEO_DETAILS_BATCH", {{"id": [{vid!r}], "parts": ["status"]}}, account="{YT_ACCOUNT}")
    for d in walk(res):
        if d.get("privacyStatus"):
            return d["privacyStatus"]
    return None
now = status()
if now != "public" and now is not None:
    run_composio_tool("YOUTUBE_UPDATE_VIDEO", {{"video_id": {vid!r}, "privacy_status": "public"}}, account="{YT_ACCOUNT}")
    now = status()
out(ok=now == "public", status=now)
'''
    return wb(m, code, "YOUTUBE_PUBLIC_CHECK").get("ok", False)
