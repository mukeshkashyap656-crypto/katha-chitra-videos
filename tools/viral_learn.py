"""
Hafte mein ek baar: humare topic (Ramayan / katha) ke un Shorts ko dhoondhta hai jo CHHOTE channel par bhi bahut chale,
unki shuruaat (hook) ka pattern AI se samjhata hai, aur VIRAL_LEARN.md mein likh deta hai. Helper isse seekhta hai.

Raaste (ek na chale toh agla):
  1) YouTube Data API (free key YOUTUBE_API_KEY, roz 10,000 units): chhote channel ke sabse chale Shorts
  2) bina key: YouTube autocomplete (log kya type karte hain) + Google Trends (viral_radar wale raaste)
  3) transcript (pehli line) milti hai toh use, nahi toh title + description ki pehli line
Kahani KABHI nahi badalti: ye sirf pehli line / title / sawaal ka dhang seekhta hai.
"""
import datetime as dt
import json
import os
import re
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

QUERIES = ["ramayan shorts", "ramayan katha hindi", "valmiki ramayan", "ram sita katha", "hanuman shorts hindi", "ramayan facts hindi"]
MAX_SUBS = 50000       # "chhota channel"
MIN_VIEWS = 5000
OUT = "VIRAL_LEARN.md"
API = "https://www.googleapis.com/youtube/v3"


def yt(path, **params):
    params["key"] = os.environ["YOUTUBE_API_KEY"].strip()
    r = requests.get(f"{API}/{path}", params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"YouTube API {path} HTTP {r.status_code}: {r.text[:120]}")
    return r.json()


def find_outliers():
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = {}
    for q in QUERIES:
        try:
            d = yt("search", part="snippet", q=q, type="video", videoDuration="short", order="viewCount",
                   publishedAfter=since, regionCode="IN", relevanceLanguage="hi", maxResults=25)
        except Exception as e:
            print("search fail:", q, str(e)[:120])
            if "403" in str(e) or "quota" in str(e).lower():
                break
            continue
        for it in d.get("items", []):
            ids[it["id"]["videoId"]] = it["snippet"]
    if not ids:
        return []
    vids = {}
    keys = list(ids)
    for i in range(0, len(keys), 50):
        d = yt("videos", part="snippet,statistics,contentDetails", id=",".join(keys[i:i + 50]))
        for v in d.get("items", []):
            vids[v["id"]] = v
    chans = {}
    cids = list({v["snippet"]["channelId"] for v in vids.values()})
    for i in range(0, len(cids), 50):
        d = yt("channels", part="statistics", id=",".join(cids[i:i + 50]))
        for c in d.get("items", []):
            chans[c["id"]] = int(c["statistics"].get("subscriberCount") or 0)
    rows = []
    for vid, v in vids.items():
        views = int(v["statistics"].get("viewCount") or 0)
        subs = chans.get(v["snippet"]["channelId"], 0)
        if views < MIN_VIEWS or subs > MAX_SUBS:
            continue
        rows.append({"id": vid, "title": v["snippet"]["title"], "views": views, "subs": subs,
                     "score": round(views / max(subs, 200), 1), "channel": v["snippet"]["channelTitle"],
                     "desc": (v["snippet"].get("description") or "").strip().split("\n")[0][:160]})
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows[:12]


def first_line(vid):
    """Video ki pehli bolne wali line (transcript). Na mile toh None (YouTube cloud machine ko kabhi rok deta hai)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        t = api.fetch(vid, languages=["hi", "en"])
        txt = " ".join(s.text for s in t)[:240]
        return txt
    except Exception:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            t = YouTubeTranscriptApi.get_transcript(vid, languages=["hi", "en"])
            return " ".join(s["text"] for s in t)[:240]
        except Exception:
            return None


def fallback_ideas():
    out = []
    try:
        import viral_radar as vr
        for q in QUERIES[:4]:
            for s in (vr.autocomplete(q, "hi") or [])[:6]:
                out.append(s)
    except Exception as e:
        print("autocomplete nahi chala:", str(e)[:100])
    return out


def main():
    now = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)
    lines = [f"# Viral seekh (khud likha, {now:%d %b %Y}) — hook aur topic", "",
             "Ye file har hafte apne aap badalti hai. Kahani Valmiki se hi rehti hai; yahan sirf shuruaat (hook) ka dhang aur log kya khoj rahe hain.", ""]
    rows, why = [], ""
    if os.environ.get("YOUTUBE_API_KEY", "").strip():
        try:
            rows = find_outliers()
        except Exception as e:
            why = str(e)[:150]
            print("API raasta fail:", why)
    else:
        why = "YOUTUBE_API_KEY secret nahi hai (free: Google Cloud Console -> YouTube Data API v3 -> key)"
    if rows:
        for r in rows[:8]:
            r["line1"] = first_line(r["id"])
        lines.append("## Chhote channel (50K subscriber tak) ke sabse chale Shorts (pichhle 60 din)")
        lines.append("Score = views / subscribers; zyada matlab chhote channel par bhi bahut chala.")
        for r in rows:
            lines.append(f"- {r['views']:,} views, {r['subs']:,} subs, score {r['score']}: \"{r['title']}\"" +
                         (f" | pehli line: \"{r['line1']}\"" if r.get("line1") else (f" | desc: {r['desc']}" if r["desc"] else "")))
        try:
            from ramayan_ai import ask
            os.environ["NO_LOCAL"] = "1"
            data = "\n".join(lines[5:])
            txt = ask("Neeche Ramayan/katha ke un Shorts ki list hai jo chhote channel par bhi bahut chale. Inki shuruaat (title / pehli line) "
                      "dekh ke Hinglish mein 5 chhote, kaam ke niyam likho: kaise shuru karte hain (sawaal, ankda, raaz, chaunkane wali baat), "
                      "kitne shabd, kaun se shabd baar baar aate hain. Har niyam ek line, example ke saath. Kahani badalne ki baat KABHI nahi. "
                      "Sirf bullet list do, aur kuch nahi.\n\n" + data, want_json=False)
            lines += ["", "## Seekh (AI ne in Shorts se nikali)", txt.strip()[:1800]]
        except Exception as e:
            lines += ["", f"(AI ne seekh nahi nikali: {str(e)[:100]}; list upar hai, helper khud padh lega)"]
    else:
        lines.append(f"## Abhi chhote channel wali list nahi bani: {why or 'koi Short filter mein nahi aaya'}")
        ideas = fallback_ideas()
        if ideas:
            lines += ["", "## Log abhi YouTube pe ye type kar rahe hain (autocomplete)"] + [f"- {s}" for s in ideas[:20]]
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines)[:2500])


if __name__ == "__main__":
    main()
