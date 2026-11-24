#!/usr/bin/env python3
"""Daily Hindi mobile-gaming news blog bot (Blogger).
Roz: Google News se aaj ki khabar -> Gemini (Google Search grounding) se verify + apne shabdon mein post
-> quality jaanch -> Blogger par DRAFT (ya MODE=live par publish).
Env: GEMINI_API_KEY (+ optional OPENROUTER_API_KEY), BLOG_ID, BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET,
     BLOGGER_REFRESH_TOKEN, MODE=draft|live (default draft), N_POSTS (default 2), DRY_RUN=1 (Blogger ko kuch nahi bhejta)
"""
import html, json, os, re, sys, time, difflib
import urllib.parse, xml.etree.ElementTree as ET
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "posted.json")
OUT = os.path.join(HERE, "out")
QUERIES = ["मोबाइल गेमिंग न्यूज़", "BGMI Free Fire नया अपडेट", "गेमिंग स्मार्टफोन लॉन्च भारत", "नया मोबाइल गेम लॉन्च"]
MODE = os.environ.get("MODE", "draft")
N = int(os.environ.get("N_POSTS", "2"))
MIN_WORDS = 350


def log(*a):
    print(*a, flush=True)


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {"posted": []}


def save_state(st):
    st["posted"] = st["posted"][-300:]
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def news_items():
    items, seen = [], set()
    for q in QUERIES:
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": q + " when:1d", "hl": "hi", "gl": "IN", "ceid": "IN:hi"})
        for attempt in range(3):
            try:
                r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                for it in ET.fromstring(r.content).iter("item"):
                    t = (it.findtext("title") or "").strip()
                    if t and t not in seen:
                        seen.add(t)
                        items.append({"title": t, "link": it.findtext("link"),
                                      "source": (it.findtext("source") or "").strip()})
                break
            except Exception as e:
                log("RSS koshish", attempt + 1, "fail:", e)
                time.sleep(5 * (attempt + 1))
    return items


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio() > 0.6


PROMPT = """Tum ek imaandaar Hindi mobile-gaming patrakar ho. Aaj ki is khabar par ek apni post likho:
Khabar: {title}  (srot: {source})

Niyam (zaroori):
- Google Search se 2-3 bharosemand srot dekhkar tathya verify karo. Jo verify na ho wo mat likho.
- Post tumhare apne shabdon mein ho, kisi lekh ka text copy nahi. Aaj ki saaf bolchaal wali Hindi.
- Pehli 2 line mein hi sabse kaam ki baat (hook): kya naya hai aur player ke liye abhi kya zaroori hai. "Namaskar/aaj hum baat karenge" jaise shuruaat mana.
- Dhaancha: hook -> <h2> "Kya-kya naya aaya" (chhoti bullet list) -> <h2> "Tareekhein" (<table> mein: tareekh | kya) -> <h2> "Aaj hi karne wale kaam" (2-4 bullet, deadline wali baat sabse upar) -> <h2> "Aksar puchhe sawaal" (2-3 sawaal-jawab, jaise "update nahi dikh raha to?").
- Gamer wali seedhi bolchaal (tum/aap), chhote vaakya, ek paragraph mein 2-3 line se zyada nahi. Bhari-bharkam shabd mana.
- Heading seedhi aur sachchi, clickbait nahi.
- Daam/tareekh/spec/update ki details sirf tab jab srot mein ho.
- KABHI mat likho: cheat, hack, mod APK, pirated/crack game, free diamond/UC/redeem code ke jhoothe daave, ya account becha-kharida. Sirf khabar, update, review, tips jo game ke niyam ke andar hon.
- Game ke screenshot/logo ki baat sirf shabdon mein; tasveer tum nahi doge.
Sirf ek JSON do: {{"title": "...", "description": "150 akshar ka saar", "labels": ["Mobile Gaming","Gaming News"], "image_query": "english 2-3 words, generic (jaise smartphone gaming)", "official_video_url": "is event/update ka OFFICIAL YouTube trailer ka link (game company ke apne channel ka), na mile to khaali", "body_html": "..."}}"""


def gemini_models(client):
    names = []
    try:
        for m in client.models.list():
            n = m.name.replace("models/", "")
            if "flash" in n and not re.search(r"lite|image|tts|live|preview|exp|thinking|audio", n):
                names.append(n)
    except Exception as e:
        log("model list fail:", e)
    names.sort(reverse=True)
    return (os.environ.get("BLOG_MODELS", "").split(",") if os.environ.get("BLOG_MODELS") else []) + names[:3] + ["gemini-2.5-flash"]


def parse_json(txt):
    m = re.search(r"\{.*\}", txt, re.DOTALL)
    return json.loads(m.group(0))


def write_post(item):
    """Returns (post dict, sources list). Gemini grounded -> OpenRouter fallback."""
    prompt = PROMPT.format(**item)
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        try:
            from google import genai
            from google.genai import types
            c = genai.Client(api_key=key)
            for model in gemini_models(c):
                for attempt in range(2):
                    try:
                        r = c.models.generate_content(
                            model=model, contents=prompt,
                            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]))
                        post = parse_json(r.text)
                        srcs = []
                        try:
                            for ch in r.candidates[0].grounding_metadata.grounding_chunks:
                                if ch.web and ch.web.uri:
                                    srcs.append((ch.web.title or ch.web.uri, ch.web.uri))
                        except Exception:
                            pass
                        log("Gemini", model, "ok, srot:", len(srcs))
                        return post, srcs
                    except Exception as e:
                        log("Gemini", model, "fail:", str(e)[:150]); time.sleep(8)
        except Exception as e:
            log("Gemini poora fail:", e)
    okey = os.environ.get("OPENROUTER_API_KEY")
    if okey:   # sahara: bina search ke, isliye srot sirf wahi jo khabar ka link hai
        for model in ["meta-llama/llama-3.3-70b-instruct:free", "google/gemma-3-27b-it:free", "mistralai/mistral-small-3.2-24b-instruct:free"]:
            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", timeout=180,
                                  headers={"Authorization": "Bearer " + okey},
                                  json={"model": model, "messages": [{"role": "user", "content":
                                        prompt + "\nDhyan: tumhare paas search nahi hai, isliye sirf wahi likho jo khabar ke shirshak se pakka ho."}]})
                post = parse_json(r.json()["choices"][0]["message"]["content"])
                log("OpenRouter", model, "ok")
                return post, []
            except Exception as e:
                log("OpenRouter", model, "fail:", str(e)[:120])
    return None, []


def plain(h):
    return re.sub(r"<[^>]+>", " ", html.unescape(h))


def quality_ok(post, srcs, item):
    why = []
    if not post or not post.get("title") or not post.get("body_html"):
        return ["post khaali"]
    words = len(plain(post["body_html"]).split())
    if words < MIN_WORDS: why.append(f"sirf {words} shabd")
    if not srcs and not item.get("link"): why.append("srot nahi")
    if re.search(r"(?i)\b(shocking|you won't believe|chaunk|चौंक)", post["title"]): why.append("clickbait heading")
    if "<h1" in post["body_html"].lower(): why.append("h1 mana")
    if re.search(r"(?i)(mod apk|hack|cheat|crack|free (diamond|uc|redeem)|redeem code|हैक|चीट)", post["title"] + " " + plain(post["body_html"])): why.append("mana wala vishay (hack/cheat/mod/redeem)")
    return why


def find_image(q):
    """CC0 / public-domain image >=1200px from Openverse. None if nothing good."""
    try:
        r = requests.get("https://api.openverse.org/v1/images/", timeout=30, params={
            "q": q, "license": "cc0,pdm", "page_size": 20, "aspect_ratio": "wide"})
        for im in r.json().get("results", []):
            if (im.get("width") or 0) >= 1200 and im.get("url"):
                return {"url": im["url"], "title": im.get("title") or q,
                        "page": im.get("foreign_landing_url") or im["url"]}
    except Exception as e:
        log("tasveer nahi mili:", e)
    return None


OFFICIAL = [x.strip().lower() for x in os.environ.get(
    "OFFICIAL_CHANNELS", "battlegrounds mobile india,bgmi,krafton,free fire,garena,pubg mobile,supercell,activision,riot games,epic games").split(",")]


def official_video(url):
    """Sirf game company ke apne YouTube channel ka video (oEmbed se channel ka naam jaanch ke). Embed karna allowed hai, copy nahi."""
    m = re.search(r"(?:youtu\.be/|v=|/embed/|/shorts/)([A-Za-z0-9_-]{11})", url or "")
    if not m: return None
    try:
        r = requests.get("https://www.youtube.com/oembed", timeout=20,
                         params={"url": "https://www.youtube.com/watch?v=" + m.group(1), "format": "json"})
        r.raise_for_status()
        author = r.json().get("author_name", "").lower()
        if any(o in author for o in OFFICIAL):
            return {"id": m.group(1), "title": r.json().get("title", ""), "author": r.json().get("author_name", "")}
        log("video official channel ka nahi:", author)
    except Exception as e:
        log("video jaanch fail:", e)
    return None


def build_html(post, srcs, item, img):
    parts = []
    vid = official_video(post.get("official_video_url"))
    if vid:
        parts.append(f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden"><iframe src="https://www.youtube.com/embed/{vid["id"]}" '
                     f'title="{html.escape(vid["title"])}" style="position:absolute;top:0;left:0;width:100%;height:100%" frameborder="0" allowfullscreen></iframe></div>'
                     f'<p><small>Official video: {html.escape(vid["author"])} (YouTube)</small></p>')
    if img and not vid:
        parts.append(f'<p><img src="{html.escape(img["url"])}" alt="{html.escape(post["title"])}" style="width:100%;height:auto"/>'
                     f'<br/><small>Tasveer: <a href="{html.escape(img["page"])}" rel="nofollow">{html.escape(img["title"])}</a> (CC0/Public Domain)</small></p>')
    parts.append(post["body_html"])
    links = [(item.get("source") or "Khabar", item["link"])] if item.get("link") else []
    links += srcs[:4]
    seen, lis = set(), []
    for t, u in links:
        if u in seen: continue
        seen.add(u); lis.append(f'<li><a href="{html.escape(u)}" rel="nofollow noopener">{html.escape(t)}</a></li>')
    parts.append("<h2>Srot</h2><ul>" + "".join(lis) + "</ul>")
    parts.append("<p><small>Ye post AI ki madad se likhi gayi aur upar ke sroton se milayi gayi hai.</small></p>")
    return "\n".join(parts)


def access_token():
    r = requests.post("https://oauth2.googleapis.com/token", timeout=30, data={
        "client_id": os.environ["BLOGGER_CLIENT_ID"], "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"], "grant_type": "refresh_token"})
    r.raise_for_status()
    return r.json()["access_token"]


def publish(title, content, labels):
    if os.environ.get("DRY_RUN") == "1" or not os.environ.get("BLOGGER_REFRESH_TOKEN"):
        log("DRY_RUN / Blogger key nahi: post sirf blog/out/ mein rakhi")
        return "dry-run"
    last = None
    for attempt in range(4):
        try:
            r = requests.post(
                f"https://www.googleapis.com/blogger/v3/blogs/{os.environ['BLOG_ID']}/posts",
                params={"isDraft": "false" if MODE == "live" else "true"},
                headers={"Authorization": "Bearer " + access_token()}, timeout=60,
                json={"kind": "blogger#post", "title": title, "content": content, "labels": labels})
            r.raise_for_status()
            return r.json().get("url") or r.json().get("id")
        except Exception as e:
            last = e; log("Blogger koshish", attempt + 1, "fail:", str(e)[:150]); time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Blogger par nahi gayi: {last}")


def main():
    os.makedirs(OUT, exist_ok=True)
    st = load_state()
    done_titles = [p["title"] for p in st["posted"]]
    items = [i for i in news_items() if not any(similar(i["title"], t) for t in done_titles)]
    log("naye khabar:", len(items))
    made = 0
    for item in items:
        if made >= N: break
        for attempt in range(2):
            post, srcs = write_post(item)
            bad = quality_ok(post, srcs, item)
            if not bad: break
            log("quality fail:", bad, "-", item["title"][:60])
        if bad: continue
        img = find_image(post.get("image_query") or "smartphone gaming")
        content = build_html(post, srcs, item, img)
        slug = re.sub(r"\W+", "-", post["title"])[:40]
        open(os.path.join(OUT, f"{time.strftime('%Y%m%d')}-{slug}.html"), "w", encoding="utf-8").write(content)
        url = publish(post["title"], content, post.get("labels") or ["Mobile Gaming"])
        st["posted"].append({"title": item["title"], "blog_title": post["title"], "date": time.strftime("%Y-%m-%d"), "url": url, "mode": MODE})
        save_state(st); made += 1
        log("POST:", post["title"], "->", url, "(", MODE, ")")
    log(f"aaj {made} post bani")
    return 0


if __name__ == "__main__":
    sys.exit(main())
