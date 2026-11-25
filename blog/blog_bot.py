#!/usr/bin/env python3
"""Daily Hindi news blog bot (gaming, tech, AI, khel, film, desh-duniya; sensitive vishay band) (Blogger).
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
CATS = {   # label -> Google News sawaal. Bot baari-baari se vishay badalta hai.
    "Mobile Gaming": ["मोबाइल गेमिंग न्यूज़", "BGMI Free Fire नया अपडेट", "नया मोबाइल गेम लॉन्च"],
    "Mobile & Tech": ["नया स्मार्टफोन लॉन्च भारत", "टेक न्यूज़ भारत", "मोबाइल अपडेट एंड्रॉयड आईफोन"],
    "AI & Apps": ["AI नया टूल", "नया ऐप लॉन्च भारत", "ChatGPT Gemini नया फीचर"],
    "Cricket & Khel": ["क्रिकेट न्यूज़ आज", "IPL न्यूज़", "भारत खेल समाचार"],
    "Film & OTT": ["नई फिल्म रिलीज़", "OTT नई वेब सीरीज़", "बॉलीवुड न्यूज़"],
    "Desh Duniya": ["भारत सरकार नई योजना", "आज की बड़ी खबर भारत", "विज्ञान अंतरिक्ष ISRO न्यूज़"],
}
# In vishayon par bot kabhi post nahi banata (galti se nuksaan / sensitive): sehat-ilaaj, paisa-share-nivesh, chunaav-rajneeti, hatya-balatkar-hadsa, dharm-vivaad
BLOCKED = re.compile(r"(?i)(हत्या|मौत|मृत|रेप|बलात्कार|हादसा|आत्महत्या|चुनाव|वोट|पार्टी|भाजपा|कांग्रेस|शेयर|सेंसेक्स|निवेश|क्रिप्टो|बिटकॉइन|इलाज|दवा|बीमारी|कैंसर|टीका|वैक्सीन|दंगा|धर्म|मंदिर|मस्जिद|murder|rape|election|stock|sensex|invest|crypto|bitcoin|cancer|vaccine|riot)")
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


def news_items(queries):
    items, seen = [], set()
    for q in queries:
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": q + " when:1d", "hl": "hi", "gl": "IN", "ceid": "IN:hi"})
        for attempt in range(3):
            try:
                r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                for it in ET.fromstring(r.content).iter("item"):
                    t = (it.findtext("title") or "").strip()
                    if t and t not in seen and not BLOCKED.search(t):
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


PROMPT = """Tum ek imaandaar Hindi khabar-patrakar ho (vishay: {cat}). Aaj ki is khabar par ek apni post likho:
Khabar: {title}  (srot: {source})

Niyam (zaroori):
- Google Search se 2-3 bharosemand srot dekhkar tathya verify karo. Jo verify na ho wo mat likho.
- Post tumhare apne shabdon mein ho, kisi lekh ka text copy nahi. Aaj ki saaf bolchaal wali Hindi.
- Pehli 2 line mein hi sabse kaam ki baat (hook): kya naya hai aur player ke liye abhi kya zaroori hai. "Namaskar/aaj hum baat karenge" jaise shuruaat mana.
- Dhaancha: hook -> <h2> "Kya-kya naya aaya" (chhoti bullet list) -> <h2> "Tareekhein" (<table> mein: tareekh | kya) -> <h2> "Aaj hi karne wale kaam" (2-4 bullet, deadline wali baat sabse upar) -> <h2> "Aksar puchhe sawaal" (2-3 sawaal-jawab, jaise "update nahi dikh raha to?").
- Gamer wali seedhi bolchaal (tum/aap), chhote vaakya, ek paragraph mein 2-3 line se zyada nahi. Bhari-bharkam shabd mana.
- Heading seedhi aur sachchi, clickbait nahi.
- Daam/tareekh/spec/update ki details sirf tab jab srot mein ho.
- Sehat/ilaaj, paisa/share/nivesh, chunaav/rajneeti, hatya/hadsa, dharm-vivaad par kuch mat likho. Aisi khabar aaye to {{"skip": true}} do.
- Gaming mein KABHI mat likho: cheat, hack, mod APK, pirated/crack game, free diamond/UC/redeem code ke jhoothe daave, ya account becha-kharida. Sirf khabar, update, review, tips jo game ke niyam ke andar hon.
- Game ke screenshot/logo ki baat sirf shabdon mein; tasveer tum nahi doge.
Sirf ek JSON do: {{"title": "...", "description": "150 akshar ka saar", "labels": ["...", "..."], "image_query": "english 2-3 words, generic (jaise smartphone gaming)", "banner_title": "English, max 4 shabd, jaise BGMI 4.7 UPDATE", "banner_sub": "English, max 6 shabd", "chips": ["English, 3 tak: 24 NOV: GALA REGISTRATION ENDS"], "official_video_url": "is event/update ka OFFICIAL YouTube trailer ka link (game company ke apne channel ka), na mile to khaali", "body_html": "..."}}"""


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


FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]


def _font(size):
    from PIL import ImageFont
    for f in FONTS:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def make_banner(post, path):
    """Apni khud ki (original) 1280x720 gaming-style tasveer: gradient + shapes + chhota English text. Hindi text nahi (shaping ka dar)."""
    from PIL import Image, ImageDraw
    import hashlib, random
    W, H = 1280, 720
    seed = int(hashlib.md5(post["title"].encode()).hexdigest()[:8], 16)
    rnd = random.Random(seed)
    palettes = [((8, 12, 40), (0, 200, 255)), ((25, 8, 40), (255, 60, 150)), ((6, 30, 30), (60, 255, 170)), ((35, 15, 5), (255, 170, 30))]
    bg, ac = palettes[seed % len(palettes)]
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im, "RGBA")
    for y in range(H):   # tirchhi gradient
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(bg[0] + (ac[0] - bg[0]) * t * .35), int(bg[1] + (ac[1] - bg[1]) * t * .35), int(bg[2] + (ac[2] - bg[2]) * t * .35), 255))
    for _ in range(14):  # neon tirchhi patti
        x = rnd.randint(-200, W); w = rnd.randint(8, 60)
        d.polygon([(x, H), (x + w, H), (x + w + 360, 0), (x + 360, 0)], fill=ac + (rnd.randint(18, 55),))
    d.rectangle([60, 60, 70, H - 60], fill=ac + (255,))
    title = (post.get("banner_title") or "GAMING NEWS").upper()[:34]
    sub = (post.get("banner_sub") or "").upper()[:48]
    size = 110 if len(title) < 16 else 84 if len(title) < 26 else 66
    f = _font(size)
    words, lines, cur = title.split(), [], ""
    for w_ in words:
        if d.textlength((cur + " " + w_).strip(), font=f) > W - 220 and cur: lines.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    lines.append(cur)
    y = 150
    for ln in lines[:3]:
        d.text((104, y + 4), ln, font=f, fill=(0, 0, 0, 160)); d.text((100, y), ln, font=f, fill=(255, 255, 255)); y += size + 10
    if sub: d.text((100, y + 10), sub, font=_font(38), fill=ac + (255,)); y += 70
    cy = max(y + 30, 430)
    for chip in (post.get("chips") or [])[:3]:
        txt = str(chip).upper()[:40]; fw = d.textlength(txt, font=_font(30))
        d.rounded_rectangle([100, cy, 100 + fw + 50, cy + 56], radius=28, fill=ac + (70,), outline=ac + (255,), width=3)
        d.text((125, cy + 9), txt, font=_font(30), fill=(255, 255, 255)); cy += 68
    d.text((W - 380, H - 70), "GAMING NEWS · HINDI", font=_font(26), fill=(255, 255, 255, 170))
    im.save(path, "JPEG", quality=90)
    return path


def make_ai_image(post, path):
    """AI se apni nayi tasveer banao (copyright-free, kisi ki photo nahi). Raaste: 1) Cloudflare Workers AI (FLUX), 2) Hugging Face (FLUX).
    Env: CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN, ya HF_TOKEN. Kuch na chale to False (tab apna card banta hai)."""
    import base64
    q = (post.get("image_query") or post.get("banner_title") or "smartphone").strip()[:120]
    prompt = f"high quality editorial photo, {q}, clean modern look, soft studio lighting, no text, no logos, no watermark"
    acc, ctok, hf = os.environ.get("CLOUDFLARE_ACCOUNT_ID"), os.environ.get("CLOUDFLARE_API_TOKEN"), os.environ.get("HF_TOKEN")
    if acc and ctok:
        for attempt in range(2):
            try:
                r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                                  headers={"Authorization": "Bearer " + ctok}, json={"prompt": prompt, "steps": 6}, timeout=120)
                r.raise_for_status()
                open(path, "wb").write(base64.b64decode(r.json()["result"]["image"]))
                return True
            except Exception as e:
                log("Cloudflare AI tasveer fail:", str(e)[:120]); time.sleep(5)
    if hf:
        for model in ("black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0"):
            try:
                r = requests.post(f"https://router.huggingface.co/hf-inference/models/{model}",
                                  headers={"Authorization": "Bearer " + hf}, json={"inputs": prompt}, timeout=180)
                if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                    open(path, "wb").write(r.content); return True
                log("HF AI tasveer", model, r.status_code)
            except Exception as e:
                log("HF AI tasveer fail:", str(e)[:120])
    return False


def host_image(path):
    """Tasveer ko public jagah chadhao taaki post mein URL lag sake: public repo (GitHub Pages / jsDelivr) par.
    Env: BLOG_IMG_TOKEN (us repo mein Contents write), BLOG_IMG_REPO (default mukeshkashyap656-crypto/katha-chitra-voice)."""
    tok = os.environ.get("BLOG_IMG_TOKEN")
    if not tok: return None
    import base64
    repo = os.environ.get("BLOG_IMG_REPO", "mukeshkashyap656-crypto/katha-chitra-voice")
    name = "blog-img/" + os.path.basename(path)
    for attempt in range(3):
        try:
            r = requests.put(f"https://api.github.com/repos/{repo}/contents/{name}", timeout=60,
                             headers={"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json"},
                             json={"message": "blog image", "content": base64.b64encode(open(path, "rb").read()).decode()})
            if r.status_code in (200, 201):
                return f"https://cdn.jsdelivr.net/gh/{repo}@main/{name}"
            log("image upload", r.status_code, r.text[:100])
        except Exception as e:
            log("image upload fail:", e)
        time.sleep(5)
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


def build_html(post, srcs, item, img, banner_url=None, ai_used=False):
    parts = []
    if banner_url:
        parts.append(f'<p><img src="{html.escape(banner_url)}" alt="{html.escape(post["title"])}" style="width:100%;height:auto"/>' + ('<br/><small>Yeh tasveer AI se banayi gayi hai, asli product alag dikh sakta hai.</small>' if ai_used else '') + '</p>')
    vid = official_video(post.get("official_video_url"))
    if vid:
        parts.append(f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden"><iframe src="https://www.youtube.com/embed/{vid["id"]}" '
                     f'title="{html.escape(vid["title"])}" style="position:absolute;top:0;left:0;width:100%;height:100%" frameborder="0" allowfullscreen></iframe></div>'
                     f'<p><small>Official video: {html.escape(vid["author"])} (YouTube)</small></p>')
    if img and not vid and not banner_url:
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


def publish_mail(title, content):
    """Raasta 2 (bina Google Cloud): Blogger ka khufiya email pata (Settings > Email). Draft ya publish, Blogger ki apni setting se tay hota hai.
    Env: BLOGGER_MAIL_TO (jaise naam.secret@blogger.com), SMTP_USER (Gmail), SMTP_APP_PASSWORD (Gmail app password)."""
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    msg = MIMEText(content, "html", "utf-8")
    msg["Subject"] = Header(title, "utf-8"); msg["From"] = os.environ["SMTP_USER"]; msg["To"] = os.environ["BLOGGER_MAIL_TO"]
    last = None
    for attempt in range(4):
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as sm:
                sm.login(os.environ["SMTP_USER"], os.environ["SMTP_APP_PASSWORD"])
                sm.sendmail(os.environ["SMTP_USER"], [os.environ["BLOGGER_MAIL_TO"]], msg.as_string())
            return "email-bheji"
        except Exception as e:
            last = e; log("email koshish", attempt + 1, "fail:", str(e)[:150]); time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"email nahi gayi: {last}")


def publish_script(title, content, labels):
    """Raasta 1 (sabse aasaan): Google Apps Script ka Web app. Wo post ko Blogger ke khufiya email par bhejta hai.
    Env (GitHub Secrets): BLOG_POST_URL (Web app ka /exec URL), BLOG_POST_TOKEN (script ke upar TOKEN wali value).
    Dhyan: draft ya live, Blogger ki Settings > Email wali setting se tay hota hai, MODE se nahi."""
    last = None
    for attempt in range(4):
        try:
            clean = lambda v: v.strip().rstrip(";").strip().strip("'\"`").strip()  # galti se ' ' ya ; ke saath daala ho to bhi chale
            r = requests.post(clean(os.environ["BLOG_POST_URL"]), timeout=90, allow_redirects=True,
                              json={"token": clean(os.environ["BLOG_POST_TOKEN"]), "title": title, "html": content, "labels": labels or []})
            r.raise_for_status()
            j = r.json()
            if not j.get("ok"):
                raise RuntimeError(str(j.get("error"))[:150])
            return "script-se-bheji"
        except Exception as e:
            last = e; log("Apps Script koshish", attempt + 1, "fail:", str(e)[:150]); time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Apps Script se nahi gayi: {last}")


def publish(title, content, labels):
    if os.environ.get("DRY_RUN") != "1" and os.environ.get("BLOG_POST_URL") and os.environ.get("BLOG_POST_TOKEN"):
        try:
            return publish_script(title, content, labels)
        except Exception as e:
            log("Apps Script raasta fail, agla raasta:", str(e)[:150])
    if os.environ.get("DRY_RUN") != "1" and os.environ.get("BLOGGER_MAIL_TO") and os.environ.get("SMTP_APP_PASSWORD") and not os.environ.get("BLOGGER_REFRESH_TOKEN"):
        return publish_mail(title, content)
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
    cats = list(CATS)
    start = len(st["posted"]) % len(cats)
    order = cats[start:] + cats[:start]
    made = 0
    for cat in order:
        if made >= N: break
        items = [i for i in news_items(CATS[cat]) if not any(similar(i["title"], t) for t in done_titles)]
        log(cat, "- naye khabar:", len(items))
        for item in items[:6]:
            item["cat"] = cat
            for attempt in range(2):
                post, srcs = write_post(item)
                if post and post.get("skip"): bad = ["skip: sensitive vishay"]; break
                bad = quality_ok(post, srcs, item)
                if not bad: break
                log("quality fail:", bad, "-", item["title"][:60])
            if bad: continue
            post["labels"] = [cat] + [l for l in (post.get("labels") or []) if l not in ("...", cat)][:2]
            slug = re.sub(r"\W+", "-", post["title"])[:40] or "post"
            bpath = os.path.join(OUT, f"{time.strftime('%Y%m%d')}-{abs(hash(post['title'])) % 10**6}.jpg")
            banner_url = None
            ai_used = False
            try:
                if os.environ.get("DRY_RUN") != "1" and make_ai_image(post, bpath):
                    banner_url = host_image(bpath); ai_used = bool(banner_url)
            except Exception as e:
                log("AI tasveer nahi bani:", e)
            try:
                if not banner_url:
                    make_banner(post, bpath); banner_url = host_image(bpath)
            except Exception as e:
                log("banner nahi bana:", e)
            img = None if banner_url else find_image(post.get("image_query") or "news")
            content = build_html(post, srcs, item, img, banner_url, ai_used)
            open(os.path.join(OUT, f"{time.strftime('%Y%m%d')}-{slug}.html"), "w", encoding="utf-8").write(content)
            url = publish(post["title"], content, post["labels"])
            st["posted"].append({"title": item["title"], "blog_title": post["title"], "cat": cat, "date": time.strftime("%Y-%m-%d"), "url": url, "mode": MODE})
            done_titles.append(item["title"]); save_state(st); made += 1
            log("POST:", post["title"], "->", url, "(", MODE, ")")
            break
    log(f"aaj {made} post bani")
    return 0


if __name__ == "__main__":
    sys.exit(main())
