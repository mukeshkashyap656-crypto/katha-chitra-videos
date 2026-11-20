import argparse, json, re, sys, time
from composio_mcp import MCP

IG_ACCOUNT = "instagram_metal-swain"
IG_USER = "40092398070406737"
REPO = "mukeshkashyap656-crypto/katha-chitra-videos"

FIND_ID = '''
def find_id(x):
    if isinstance(x, dict):
        for k in ("creation_id", "id"):
            v = x.get(k)
            if isinstance(v, (str, int)) and str(v).isdigit():
                return str(v)
        for v in x.values():
            r = find_id(v)
            if r:
                return r
    elif isinstance(x, (list, tuple)):
        for v in x:
            r = find_id(v)
            if r:
                return r
    return None
'''


def wb(m, code, label):
    r = m.call("COMPOSIO_REMOTE_WORKBENCH", {"code_to_execute": code, "thought": label, "current_step": label})
    return "".join(c.get("text", "") for c in r.get("content", []))


def already_posted(m, first_line):
    code = f'''
first = {json.dumps(first_line, ensure_ascii=False)}
res, err = run_composio_tool("INSTAGRAM_GET_IG_USER_MEDIA", {{"ig_user_id": "me", "limit": 30, "fields": "id,caption,timestamp"}}, account="{IG_ACCOUNT}")
if err:
    res, err = run_composio_tool("INSTAGRAM_GET_IG_USER_MEDIA", {{"ig_user_id": "me", "limit": 30}}, account="{IG_ACCOUNT}")
s = str(res)
print("LISTLEN=", len(s))
print("FOUND=" + ("1" if first in s else "0"))
print("PREVIEW=", s[:200].replace("\\n", " "))
'''
    out = wb(m, code, "CHECK_ALREADY_POSTED")
    print("check:", re.sub(r"\s+", " ", out)[:400])
    return "FOUND=1" in out


def make_container(m, ep):
    code = FIND_ID + f'''
import os, urllib.request
def g(o):
    return o[0] if isinstance(o, tuple) else o
fn = {json.dumps(ep["file"])}
meta = g(proxy_execute("GET", "/repos/{REPO}/contents/" + fn, "github", query_params={{"ref": "main"}}))
p = "/home/user/" + fn
urllib.request.urlretrieve(meta["download_url"], p)
size = os.path.getsize(p)
print("SIZE=" + str(size))
if size != {ep["size"]}:
    print("SIZE_MISMATCH")
else:
    up = g(upload_local_file(p))
    s3 = up.get("s3key") if isinstance(up, dict) else up
    print("S3KEY_OK=" + ("1" if s3 else "0"))
    res, err = run_composio_tool("INSTAGRAM_POST_IG_USER_MEDIA", {{"ig_user_id": "{IG_USER}", "media_type": "REELS", "video_file": {{"name": fn, "mimetype": "video/mp4", "s3key": s3}}, "caption": {json.dumps(ep["caption"], ensure_ascii=False)}, "share_to_feed": True, "thumb_offset": 0}}, account="{IG_ACCOUNT}")
    cid = find_id(res)
    print("CREATION_ID=" + str(cid))
    print("CREATE_ERR=", str(err)[:300])
    print("CREATE_RES=", str(res)[:300].replace("\\n", " "))
'''
    out = wb(m, code, "CREATE_CONTAINER")
    print("create:", re.sub(r"\s+", " ", out)[:700])
    mm = re.search(r"CREATION_ID=(\d+)", out)
    return mm.group(1) if mm else None


def publish(m, cid):
    for attempt in range(6):
        code = FIND_ID + f'''
res, err = run_composio_tool("INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH", {{"ig_user_id": "{IG_USER}", "creation_id": "{cid}", "max_wait_seconds": 120}}, account="{IG_ACCOUNT}")
mid = find_id(res)
print("MEDIA_ID=" + str(mid))
print("PUB_ERR=", str(err)[:300])
print("PUB_RES=", str(res)[:400].replace("\\n", " "))
'''
        out = wb(m, code, "PUBLISH")
        print("publish try", attempt + 1, ":", re.sub(r"\s+", " ", out)[:600])
        mm = re.search(r"MEDIA_ID=(\d+)", out)
        if mm and mm.group(1) != cid:
            return mm.group(1)
        time.sleep(20)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bhag", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    eps = json.load(open("../episodes.json", encoding="utf-8"))
    ep = eps[a.bhag]
    m = MCP()
    first = ep["caption"].split("\n")[0]
    if already_posted(m, first):
        print("ALREADY_POSTED - kuch nahi kiya")
        return
    cid = make_container(m, ep)
    if not cid:
        print("FAIL: container nahi bana")
        sys.exit(1)
    print("CONTAINER_READY", cid)
    if a.dry_run:
        print("DRY_RUN: publish nahi kiya")
        return
    mid = publish(m, cid)
    if not mid:
        print("FAIL: publish nahi hua")
        sys.exit(1)
    print("POSTED media_id", mid)


main()
