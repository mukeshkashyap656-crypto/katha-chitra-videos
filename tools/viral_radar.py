"""
Viral radar (free): episode banane se pehle dekhta hai ki log asal mein kya khoj rahe hain,
aur us hisaab se sabse zordaar pehla sawaal (hook / title) chunta hai.

Sab kuch free aur bina key ke:
  - YouTube ka autocomplete (log kya type karte hain)         suggestqueries.google.com
  - Google Trends India (aaj kya chal raha hai)               trends.google.com/trending/rss
  - apne pichhle videos ke asli views                         stats/STATS.md (agar bana ho)
Koi bhi source na chale toh baaki se kaam chalta hai; sab na chalein toh radar chup-chaap "kuch nahi" lautata hai
aur episode normal tareeke se banta hai (radar kabhi video rokta nahi).

Kahani KABHI nahi badalti: radar sirf pehle sawaal, title ke shabd aur tags chunta hai. Kahani Valmiki se hi rehti hai.
"""
import json
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET

import requests

UA = {"User-Agent": "Mozilla/5.0"}


def autocomplete(q, hl):
    """YouTube autocomplete: kisi shabd ke aage log kya likhte hain."""
    try:
        r = requests.get("https://suggestqueries.google.com/complete/search",
                         params={"client": "firefox", "ds": "yt", "hl": hl, "q": q}, headers=UA, timeout=20)
        data = json.loads(r.text)
        return [str(x) for x in data[1]][:8]
    except Exception:
        return []


def trends_india():
    """Google Trends India ki aaj ki trending khoj (RSS)."""
    for url in ("https://trends.google.com/trending/rss?geo=IN", "https://trends.google.com/trends/trendingsearches/daily/rss?geo=IN"):
        try:
            r = requests.get(url, headers=UA, timeout=20)
            root = ET.fromstring(r.content)
            out = [(it.findtext("title") or "").strip() for it in root.iter("item")]
            out = [x for x in out if x]
            if out:
                return out[:20]
        except Exception:
            continue
    return []


def seeds_from_topic(topic):
    """Topic (Hinglish line) se 2-3 khoj-shabd: 'ramayan <naam>'."""
    parts = re.split(r"[,:;()]| ki | ka | ke | aur | ko ", topic or "")
    names = []
    for p in parts:
        w = p.strip().split()
        if w:
            names.append(" ".join(w[:2]))
    out = ["valmiki ramayan"]
    for n in names[:3]:
        out.append(f"ramayan {n}")
    return out


def stats_text(path="stats/STATS.md"):
    """Apne asli views: local file, warna main branch se (wahan roz ki workflow likhti hai)."""
    try:  # pehle taza views (RSS/API/Composio), phir file
        import yt_stats
        n, rows = yt_stats.fetch()
        if n:
            return "\n".join(f"{d} views={v} like={l} {t[:70]}" for d, v, l, t in rows)[-3000:]
    except Exception:
        pass
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()[-3000:]
    except OSError:
        pass
    try:
        import subprocess
        subprocess.run(["git", "fetch", "--depth", "1", "origin", "main"], capture_output=True, timeout=60)
        r = subprocess.run(["git", "show", f"FETCH_HEAD:{path}"], capture_output=True, text=True, timeout=30)
        return r.stdout[-3000:] if r.returncode == 0 else ""
    except Exception:
        return ""


def gather(topic):
    sig = {"autocomplete": {}, "trends": [], "stats": ""}
    for s in seeds_from_topic(topic):
        got = autocomplete(s, "hi") + autocomplete(s, "en")
        seen, uniq = set(), []
        for g in got:
            if g.lower() not in seen:
                seen.add(g.lower()); uniq.append(g)
        if uniq:
            sig["autocomplete"][s] = uniq[:10]
    sig["trends"] = trends_india()
    sig["stats"] = stats_text()
    return sig


def advise(ask, bhag, topic, sargas, today, viral_md, sig=None, valmiki_text=""):
    """Signals dekhkar AI se: sabse zordaar pehla sawaal + 2 vikalp + tags. Kuch na mile toh {}."""
    sig = sig if sig is not None else gather(topic)
    if not (sig["autocomplete"] or sig["trends"] or sig["stats"]):
        return {}
    prompt = (
        "You are the growth director of the Hindi channel Katha Chitra (Valmiki Ramayan Shorts). Today is {today} (IST). "
        "Episode: Bhag {b}; topic: {t}; Valmiki sargas (approx.): {s}.\n"
        "Below are FREE real signals: what people type on YouTube (autocomplete), what is trending in India today, and our own past "
        "video results (if any). Choose the best opening QUESTION for this episode, the one that makes a stranger stop scrolling.\n"
        "Rules: the story stays exactly as in Valmiki, nothing is added or changed; the question must be TRUE to the episode "
        "(no clickbait that the episode does not answer); Hindi in simple spoken Devanagari, under 60 characters; no film/actor/TV names. "
        "If a trending item or a festival/date of today really connects to this episode, you may use it as the angle; otherwise ignore the trends. "
        "Prefer the wording people actually search (see autocomplete). Follow VIRAL.md section 1 and 5.\n"
        "THE STORY COMES FIRST: the question may only be about something that really happens in the VALMIKI TEXT below and is answered in it. "
        "Trends and search words only decide the WORDING; they never decide what the episode is about, never add or change a scene. "
        "If no signal fits the story, take the most natural question from the story itself.\n"
        "Reply with ONLY valid JSON: "
        '{{"question":"...","alternatives":["...","..."],"search_words":["valmiki ramayan ..."],"angle":"Hinglish, 1 line","reason":"Hinglish, 1 line: kis signal ki wajah se"}}\n\n'
        "# VALMIKI TEXT\n{vt}\n\n# AUTOCOMPLETE\n{ac}\n\n# TRENDS INDIA TODAY\n{tr}\n\n# OUR STATS\n{st}\n\n# VIRAL.md\n{v}"
    ).format(today=today, b=bhag, t=topic, s=sargas, ac=json.dumps(sig["autocomplete"], ensure_ascii=False),
             tr=", ".join(sig["trends"]) or "(not available)", st=sig["stats"] or "(none yet)", v=viral_md[:4000], vt=(valmiki_text or "(not available: use only what you are sure is in Valmiki Bala Kanda)")[:3500])
    for _ in range(2):
        try:
            raw = ask(prompt, want_json=False)
            mt = re.search(r"\{.*\}", raw, re.DOTALL)
            d = json.loads(mt.group(0) if mt else raw)
            q = str(d.get("question", "")).strip()
            if 5 <= len(q) <= 80:
                d["question"] = q
                d["signals_used"] = {"autocomplete_seeds": list(sig["autocomplete"]), "trends": len(sig["trends"]),
                                     "stats": bool(sig["stats"])}
                return d
        except Exception:
            continue
    return {}


def brief_text(d):
    """AI ke liye chhota nirdesh (autopost brief mein jodne ke liye)."""
    if not d:
        return ""
    alts = "; ".join(d.get("alternatives") or [])
    return ("\n\nVIRAL RADAR (free real signals checked): use this QUESTION as the banner/title question and as the idea of the "
            "first spoken line (still true to Valmiki; the episode must answer it): \"{q}\". Other options if it does not fit the "
            "story: {a}. Angle: {g}. Why: {r}.").format(q=d["question"], a=alts or "-", g=d.get("angle", ""), r=d.get("reason", ""))
