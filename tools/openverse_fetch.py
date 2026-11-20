"""Download free CC0 sounds (jungle, owl, dhol, wind...) from Openverse. Only CC0 = no copyright trouble.
Runs on GitHub's computer. Usage: python3 tools/openverse_fetch.py "jungle night" "owl" "dhol" --n 3 --out sfx/openverse
Writes each file plus sfx/openverse/credits.json (title, creator, source link) for our own record.
"""
import argparse, json, os, re, shlex, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("queries", nargs="*")
ap.add_argument("--from-env", action="store_true", help="read queries from $QUERIES")
ap.add_argument("--n", type=int, default=3)
ap.add_argument("--out", default="sfx/openverse")
ap.add_argument("--max-sec", type=float, default=60)
a = ap.parse_args()
if a.from_env:
    a.queries = shlex.split(os.environ.get("QUERIES", ""))
os.makedirs(a.out, exist_ok=True)
cred_path = f"{a.out}/credits.json"
credits = json.load(open(cred_path)) if os.path.exists(cred_path) else {}
UA = {"User-Agent": "katha-chitra-videos (github action)"}

for q in a.queries:
    url = "https://api.openverse.org/v1/audio/?" + urllib.parse.urlencode(
        {"q": q, "license": "cc0", "page_size": 20})
    data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
    got = 0
    for r in data.get("results", []):
        if got >= a.n:
            break
        if r.get("license") != "cc0" or not r.get("url"):
            continue
        if r.get("duration") and r["duration"] / 1000 > a.max_sec:
            continue
        ext = (r.get("filetype") or r["url"].rsplit(".", 1)[-1] or "mp3")[:4]
        name = re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_") + f"_{got + 1}.{ext}"
        try:
            urllib.request.urlretrieve(r["url"], f"{a.out}/{name}")
        except Exception as e:
            print("skip", r["url"], e)
            continue
        credits[name] = {"title": r.get("title"), "creator": r.get("creator"),
                         "license": "CC0", "source": r.get("foreign_landing_url")}
        got += 1
        print("ok", name, "-", r.get("title"))
json.dump(credits, open(cred_path, "w"), ensure_ascii=False, indent=1)
