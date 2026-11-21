"""
Roz ke asli views: YouTube (Katha Chitra) ke har video ke views / likes / comments Composio se laakar stats/STATS.md mein likhta hai.
Viral radar (tools/viral_radar.py) isi file ko padhkar seekhta hai ki kaun sa sawaal / title chala.

Raaste (ek na chale toh doosra):
  1) COMPOSIO_MULTI_EXECUTE_TOOL  (YOUTUBE_LIST_CHANNEL_VIDEOS -> YOUTUBE_GET_VIDEO_DETAILS_BATCH)
  2) COMPOSIO_REMOTE_WORKBENCH mein run_composio_tool (jaise post_youtube.py karta hai)
Kuch bhi na chale toh purani STATS.md waise hi rehti hai (kuch bigadta nahi).
"""
import datetime
import json
import os
import re
import sys

from composio_mcp import MCP

YT_ACCOUNT = "youtube_gair-habab"                 # Katha Chitra (@kathachitra_123)
CHANNEL_ID = "UC84cYc-GxPKoKB_wsMd6zvQ"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stats")


def _json_in(text):
    """Text mein se sabse bada JSON object nikaalo."""
    best = None
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[m.start():])
        except ValueError:
            continue
        if isinstance(obj, dict) and (best is None or len(json.dumps(obj)) > len(json.dumps(best))):
            best = obj
    return best


def _find(obj, key):
    """Nested JSON mein pehli 'key' wali list dhundho."""
    if isinstance(obj, dict):
        if isinstance(obj.get(key), list):
            return obj[key]
        for v in obj.values():
            r = _find(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find(v, key)
            if r is not None:
                return r
    return None


def _text(res):
    return "".join(c.get("text", "") for c in (res or {}).get("content", []) if isinstance(c, dict))


def via_multi_execute(m):
    def run(slug, args):
        r = m.call("COMPOSIO_MULTI_EXECUTE_TOOL", {
            "tools": [{"tool_slug": slug, "account": YT_ACCOUNT, "arguments": args}],
            "sync_response_to_workbench": False, "thought": "daily stats", "current_step": "STATS"})
        return _json_in(_text(r)) or {}
    lst = run("YOUTUBE_LIST_CHANNEL_VIDEOS", {"channelId": CHANNEL_ID, "maxResults": 50})
    ids = [((it.get("snippet") or {}).get("resourceId") or {}).get("videoId") for it in (_find(lst, "items") or [])]
    ids = [i for i in ids if i]
    if not ids:
        raise RuntimeError("video list khaali")
    det = run("YOUTUBE_GET_VIDEO_DETAILS_BATCH", {"id": ids, "parts": ["snippet", "statistics"]})
    items = [it for it in (_find(det, "items") or []) if it.get("statistics")]
    if not items:
        raise RuntimeError("stats khaali")
    return items


def via_workbench(m):
    code = f'''
import json
res, err = run_composio_tool("YOUTUBE_LIST_CHANNEL_VIDEOS", {{"channelId": "{CHANNEL_ID}", "maxResults": 50}}, account="{YT_ACCOUNT}")
items = (res or {{}}).get("items") or (res or {{}}).get("data", {{}}).get("items") or []
ids = [((i.get("snippet") or {{}}).get("resourceId") or {{}}).get("videoId") for i in items]
ids = [i for i in ids if i]
res2, err2 = run_composio_tool("YOUTUBE_GET_VIDEO_DETAILS_BATCH", {{"id": ids, "parts": ["snippet", "statistics"]}}, account="{YT_ACCOUNT}")
print("STATS_JSON=" + json.dumps(res2 or {{}}, ensure_ascii=False))
'''
    r = m.call("COMPOSIO_REMOTE_WORKBENCH", {"code_to_execute": code, "thought": "daily stats", "current_step": "STATS"})
    t = _text(r)
    mm = re.search(r"STATS_JSON=(\{.*\})", t, re.S)
    obj = json.loads(mm.group(1)) if mm else (_json_in(t) or {})
    items = [it for it in (_find(obj, "items") or []) if it.get("statistics")]
    if not items:
        raise RuntimeError("workbench se stats nahi mile")
    return items


def bhag_of(title):
    m = re.search(r"(?:भाग|Part)\s*(\d+)", title or "")
    return int(m.group(1)) if m else 0


def hook_of(title):
    """Title ka sawaal wala hissa (| se pehle, emoji ke bina)."""
    t = (title or "").split("|")[0]
    return re.sub(r"[\U0001F300-\U0001FAFF☀-➿]", "", t).strip()


def write_md(items, now):
    rows = []
    for it in items:
        sn, st = it.get("snippet", {}), it.get("statistics", {})
        try:
            pub = datetime.datetime.strptime(sn.get("publishedAt", ""), "%Y-%m-%dT%H:%M:%SZ")
            hrs = max(1.0, (now - pub).total_seconds() / 3600)
        except ValueError:
            hrs = 1.0
        v, l, c = int(st.get("viewCount", 0)), int(st.get("likeCount", 0)), int(st.get("commentCount", 0))
        rows.append((bhag_of(sn.get("title")), v, l, c, round(hrs), round(v / hrs, 2), hook_of(sn.get("title"))))
    rows.sort()
    md = ["# Katha Chitra — asli views (roz apne aap banti hai)",
          f"Update: {now:%Y-%m-%d %H:%M} UTC. Channel naya hai, kam views ka matlab pakka nahi; sirf 'views/ghanta' se tulna karo (naye aur purane video barabar tolne ke liye).",
          "", "| Bhag | Views | Likes | Comments | Ghante | Views/ghanta | Pehla sawaal (title) |", "|---|---|---|---|---|---|---|"]
    for b, v, l, c, h, vph, hook in rows:
        md.append(f"| {b} | {v} | {l} | {c} | {h} | {vph} | {hook} |")
    best = max(rows, key=lambda r: r[5]) if rows else None
    if best:
        md += ["", f"Abhi sabse tez: Bhag {best[0]} ({best[5]} views/ghanta): \"{best[6]}\""]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "STATS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(OUT, "stats.json"), "w", encoding="utf-8") as f:
        json.dump([dict(zip(("bhag", "views", "likes", "comments", "hours", "views_per_hour", "hook"), r)) for r in rows], f, ensure_ascii=False, indent=1)
    print("\n".join(md))


def main():
    m = MCP()
    items, errs = None, []
    for name, fn in (("multi_execute", via_multi_execute), ("workbench", via_workbench)):
        try:
            items = fn(m)
            print("stats mile:", name, len(items), "videos")
            break
        except Exception as e:
            errs.append(f"{name}: {str(e)[:150]}")
            print("raasta nahi chala:", errs[-1])
    if not items:
        print("Stats nahi mile; purani file waise hi rakhi.", errs)
        sys.exit(0)
    write_md(items, datetime.datetime.utcnow())


if __name__ == "__main__":
    main()
