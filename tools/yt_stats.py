"""Apne channel ke asli views. Kai raaste, jo chale wahi:
 1. YouTube RSS (koi key nahi) — channel ke pichhle ~15 video, views ke saath
 2. YOUTUBE_API_KEY (agar secret ho) — YouTube Data API, public stats
 3. COMPOSIO_API_KEY + COMPOSIO_YT_ACCOUNT (agar secret ho) — Composio se juda YouTube
 4. stats/STATS.md (haath se/Claude ne daala)
`python tools/yt_stats.py` -> stats/STATS.md likh deta hai (kuch na mile toh purani file chhod deta hai)."""
import json, os, re, sys, urllib.request, xml.etree.ElementTree as ET

CHANNEL = os.environ.get("YT_CHANNEL_ID", "UC84cYc-GxPKoKB_wsMd6zvQ")
OUT = "stats/STATS.md"
UA = {"User-Agent": "Mozilla/5.0"}

def _get(url, headers=None, data=None, timeout=25):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})}, data=data)
    return urllib.request.urlopen(req, timeout=timeout).read()

def via_rss():
    x = _get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}")
    ns = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/", "y": "http://www.youtube.com/xml/schemas/2015"}
    rows = []
    for e in ET.fromstring(x).findall("a:entry", ns):
        st = e.find("m:group/m:community/m:statistics", ns)
        rt = e.find("m:group/m:community/m:starRating", ns)
        rows.append((e.findtext("a:published", "", ns)[:10], int(st.get("views", 0)) if st is not None else 0,
                     int(rt.get("count", 0)) if rt is not None else 0, e.findtext("a:title", "", ns)))
    return rows

def via_api():
    key = os.environ["YOUTUBE_API_KEY"]
    up = "UU" + CHANNEL[2:]
    pl = json.loads(_get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={up}&key={key}"))
    ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
    v = json.loads(_get(f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(ids)}&key={key}"))
    return [(i["snippet"]["publishedAt"][:10], int(i["statistics"].get("viewCount", 0)), int(i["statistics"].get("likeCount", 0)), i["snippet"]["title"]) for i in v.get("items", [])]

def via_composio():
    key, acc = os.environ["COMPOSIO_API_KEY"], os.environ["COMPOSIO_YT_ACCOUNT"]
    def call(slug, args):
        body = json.dumps({"connected_account_id": acc, "arguments": args}).encode()
        r = json.loads(_get(f"https://backend.composio.dev/api/v3/tools/execute/{slug}", {"x-api-key": key, "Content-Type": "application/json"}, body))
        return r.get("data", {}).get("data", r.get("data", {}))
    pl = call("YOUTUBE_LIST_CHANNEL_VIDEOS", {"channelId": CHANNEL, "maxResults": 50})
    ids = [i["snippet"]["resourceId"]["videoId"] for i in pl.get("items", [])]
    v = call("YOUTUBE_GET_VIDEO_DETAILS_BATCH", {"id": ids, "part": "snippet,statistics"})
    return [(i["snippet"]["publishedAt"][:10], int(i["statistics"].get("viewCount", 0)), int(i["statistics"].get("likeCount", 0)), i["snippet"]["title"]) for i in v.get("items", [])]

def fetch():
    errs = []
    for name, fn, need in (("rss", via_rss, None), ("api", via_api, "YOUTUBE_API_KEY"), ("composio", via_composio, "COMPOSIO_API_KEY")):
        if need and not os.environ.get(need):
            continue
        try:
            rows = fn()
            if rows:
                return name, sorted(rows, reverse=True)
        except Exception as e:
            errs.append(f"{name}: {str(e)[:80]}")
    return None, errs

def main():
    name, rows = fetch()
    if not name:
        print("views nahi mile:", rows); return 1
    import datetime
    md = f"# Katha Chitra asli views ({name} se, {datetime.date.today():%d %b %Y})\n\n| Tarikh | Views | Like/Rating | Title |\n|---|---|---|---|\n"
    md += "".join(f"| {d} | {v} | {l} | {t[:90]} |\n" for d, v, l, t in rows)
    os.makedirs("stats", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(md)
    print(md[:600]); return 0

if __name__ == "__main__":
    sys.exit(main())
