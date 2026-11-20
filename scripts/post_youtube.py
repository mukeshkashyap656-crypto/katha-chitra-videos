import json, re
from composio_mcp import MCP

YT_ACCOUNT = "youtube_gair-habab"      # Katha Chitra (@kathachitra_123)
REPO = "mukeshkashyap656-crypto/katha-chitra-videos"


def wb(m, code, label):
    r = m.call("COMPOSIO_REMOTE_WORKBENCH", {"code_to_execute": code, "thought": label, "current_step": label})
    return "".join(c.get("text", "") for c in r.get("content", []))


def upload(m, ep, dry=False):
    # YouTube par public Short daalo. (ok, video_id) lautata hai.
    args = {"title": ep["title"], "description": ep["caption"], "tags": ep.get("tags", []),
            "categoryId": "24", "privacyStatus": "public"}
    code = f'''
import os, urllib.request
def g(o):
    return o[0] if isinstance(o, tuple) else o
fn = {json.dumps(ep["file"])}
meta = g(proxy_execute("GET", "/repos/{REPO}/contents/" + fn, "github", query_params={{"ref": "main"}}))
p = "/home/user/" + os.path.basename(fn)
urllib.request.urlretrieve(meta["download_url"], p)
size = os.path.getsize(p)
print("SIZE=" + str(size))
if size != {ep["size"]}:
    print("SIZE_MISMATCH")
else:
    up = g(upload_local_file(p))
    s3 = up.get("s3key") if isinstance(up, dict) else up
    print("S3KEY_OK=" + ("1" if s3 else "0"))
    ARGS = json.loads({json.dumps(json.dumps(args, ensure_ascii=False))})
    ARGS["videoFile"] = {{"name": os.path.basename(fn), "mimetype": "video/mp4", "s3key": s3}}
    if {bool(dry)}:
        print("DRY_RUN_OK")
    else:
        res, err = run_composio_tool("YOUTUBE_MULTIPART_UPLOAD_VIDEO", ARGS, account="{YT_ACCOUNT}")
        print("YT_ERR=" + str(err)[:300].replace("\\n", " "))
        print("YT_RES=" + str(res)[:700].replace("\\n", " "))
'''
    code = "import json\n" + code
    out = wb(m, code, "YOUTUBE_UPLOAD")
    print("youtube:", re.sub(r"\s+", " ", out)[:700])
    if dry:
        return ("DRY_RUN_OK" in out), None
    if "SIZE_MISMATCH" in out or "YT_RES=" not in out:
        return False, None
    err = re.search(r"YT_ERR=(.*)", out)
    if err and err.group(1).strip() not in ("None", ""):
        return False, None
    mm = re.search(r"['\"]id['\"]:\s*['\"]([A-Za-z0-9_-]{11})['\"]", out)
    return True, (mm.group(1) if mm else "UNKNOWN")
