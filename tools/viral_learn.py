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


def gemini_watch(vid):
    """Gemini seedha YouTube link dekhta hai: pehle 3 second mein kya bolta/dikhta hai. Na chale toh None."""
    try:
        from google import genai
        from google.genai import types
        import ramayan_ai as ra
        c = genai.Client(api_key=os.environ["GEMINI_API_KEY"].strip(), http_options=types.HttpOptions(timeout=90000))
        for m in ra.gemini_model_list(c)[:3]:
            try:
                r = c.models.generate_content(model=m, contents=types.Content(parts=[
                    types.Part(file_data=types.FileData(file_uri=f"https://www.youtube.com/watch?v={vid}")),
                    types.Part(text="Is video ke pehle 3 second mein kya bolta aur dikhta hai? Hinglish mein sirf ek chhoti line (30 shabd tak): "
                                    "pehle shabd/sawaal kya hai aur screen par kya hai. Aur kuch mat likho.")]))
                t = (r.text or "").strip()
                if t:
                    return t[:260]
            except Exception as e:
                print("gemini_watch", m, str(e)[:100])
                if any(x in str(e) for x in ("404", "429", "503", "UNAVAILABLE")):
                    continue
                break
    except Exception as e:
        print("gemini_watch nahi chala:", str(e)[:100])
    return None


def comment_questions(rows):
    """Viral videos ke comments mein jo sawaal log poochh rahe hain (agle hook ke liye)."""
    out = []
    for r in rows[:5]:
        try:
            d = yt("commentThreads", part="snippet", videoId=r["id"], order="relevance", maxResults=30, textFormat="plainText")
        except Exception as e:
            print("comments fail:", str(e)[:100]); continue
        for it in d.get("items", []):
            sn = it["snippet"]["topLevelComment"]["snippet"]
            t = re.sub(r"\s+", " ", sn.get("textDisplay", "")).strip()
            if ("?" in t or "kya" in t.lower() or "kaun" in t.lower() or "kyu" in t.lower()) and 12 <= len(t) <= 140:
                out.append((sn.get("likeCount", 0), t))
    out.sort(reverse=True)
    seen, res = set(), []
    for _, t in out:
        k = t.lower()[:30]
        if k not in seen:
            seen.add(k); res.append(t)
    return res[:12]


WIKI = ["Ramayana", "Mandodari", "Ravana", "Hanuman", "Sita", "Lakshmana", "Bharata_(Ramayana)", "Kaikeyi", "Ahalya", "Shabari", "Jatayu",
        "Vali_(Ramayana)", "Sugriva", "Vibhishana", "Kumbhakarna", "Indrajit", "Dasharatha", "Vishvamitra", "Tataka", "Shurpanakha",
        "Valmiki", "Urmila", "Kausalya", "Sumitra", "Shatrughna", "Angada", "Jambavan", "Sampati", "Trijata", "Marich"]


def wiki_trending():
    """Wikipedia ke free pageviews: kaun sa kirdaar pichhle 7 din mein pehle se zyada khoja ja raha hai. Key nahi chahiye."""
    end = dt.date.today() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=37)
    rows = []
    for a in WIKI:
        try:
            r = requests.get("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
                             f"{a}/daily/{start:%Y%m%d}00/{end:%Y%m%d}00", headers={"User-Agent": "katha-chitra-bot/1.0 (github)"}, timeout=20)
            v = [x["views"] for x in r.json()["items"]]
            if len(v) < 20:
                continue
            last7 = sum(v[-7:]) / 7
            before = sum(v[:-7]) / max(1, len(v) - 7)
            rows.append((last7 / max(before, 1), int(last7), a.replace("_", " ")))
        except Exception:
            continue
    rows.sort(reverse=True)
    return rows


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
        for n, r in enumerate(rows[:8]):
            r["line1"] = first_line(r["id"])
            if not r["line1"] and n < 4 and os.environ.get("GEMINI_API_KEY", "").strip():
                r["line1"] = gemini_watch(r["id"])
        lines.append("## Chhote channel (50K subscriber tak) ke sabse chale Shorts (pichhle 60 din)")
        lines.append("Score = views / subscribers; zyada matlab chhote channel par bhi bahut chala.")
        for r in rows:
            lines.append(f"- {r['views']:,} views, {r['subs']:,} subs, score {r['score']}: \"{r['title']}\"" +
                         (f" | pehli line: \"{r['line1']}\"" if r.get("line1") else (f" | desc: {r['desc']}" if r["desc"] else "")))
        extra = []
        try:
            qs = comment_questions(rows)
            if qs:
                extra += ["", "## Viral videos ke comments mein log ye poochh rahe hain (hook ke liye)"] + [f"- {q}" for q in qs]
        except Exception as e:
            print("comments:", str(e)[:100])
        lines += extra
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
    try:
        wt = wiki_trending()
        if wt:
            lines += ["", "## Wikipedia pe abhi kaun sa kirdaar zyada khoja ja raha hai (pichhle 7 din / pehle ke 30 din, roz ke views)"]
            lines += [f"- {n}: {x:.1f} guna ({v} views roz)" for x, v, n in wt[:8]]
    except Exception as e:
        print("wiki nahi chala:", str(e)[:100])
    if not rows:
        lines.append(f"## Abhi chhote channel wali list nahi bani: {why or 'koi Short filter mein nahi aaya'}")
        ideas = fallback_ideas()
        if ideas:
            lines += ["", "## Log abhi YouTube pe ye type kar rahe hain (autocomplete)"] + [f"- {s}" for s in ideas[:20]]
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines)[:2500])


if __name__ == "__main__":
    main()
