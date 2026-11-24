"""Kaunsi cheez jud chuki hai aur kaunsi jodni baaki hai. `python tools/tool_check.py` -> text; report mein bhi aata hai.
Har kaam ke liye: kya chahiye, abhi hai ya nahi, aur kaise jodna hai. Koi secret print nahi hota."""
import os, urllib.request

# (kaam, secret naam (koi ek kaafi), kaise jodein, bina iske kya hota hai)
NEEDS = [
    ("Free AI (Gemini)", ["GEMINI_API_KEY"], "aistudio.google.com/apikey -> key -> repo Settings > Secrets > GEMINI_API_KEY", "episode/review/video dekhna band"),
    ("Free AI sahare", ["OPENROUTER_API_KEY", "GROQ_API_KEY", "CEREBRAS_API_KEY", "MISTRAL_API_KEY", "SAMBANOVA_API_KEY", "NVIDIA_API_KEY", "COHERE_API_KEY", "HF_TOKEN"], "kam se kam 2-3 jodo (sab free)", "Gemini fail hone par sirf dheema local AI"),
    ("ElevenLabs awaaz (famous voice)", ["ELEVENLABS_API_KEY"], "elevenlabs.io -> API key -> secret ELEVENLABS_API_KEY", "free Madhur awaaz par girta hai"),
    ("YouTube asli views/analytics", ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"], "Google Cloud -> YouTube Data+Analytics API -> OAuth -> 3 secret", "STATS.md bina asli views ke, radar andaza"),
    ("Tyohar tarikh (Google Calendar India)", ["GCAL_API_KEY"], "Google Cloud -> Calendar API key -> secret GCAL_API_KEY (calendar: en.indian#holiday@group.v.calendar.google.com)", "tarikh sirf FESTIVAL.md se, haath se milani padti"),
    ("Instagram par post", ["IG_ACCESS_TOKEN", "IG_USER_ID"], "Meta Business -> Graph API token + IG user id", "Reel haath se daalni padti"),
    ("YouTube par apne aap upload", ["YT_CLIENT_ID", "YT_REFRESH_TOKEN"], "upar wale YouTube secret (upload scope ke saath)", "upload haath se / Claude se"),
]
# Free jagah jahan runner ko seedha pahunchna chahiye (secret nahi chahiye)
SITES = [("YouTube autocomplete", "https://suggestqueries.clients6.google.com/complete/search?client=youtube&ds=yt&q=ram"),
         ("Drik Panchang", "https://www.drikpanchang.com/festivals/month/festivals-december.html"),
         ("Openverse sounds", "https://api.openverse.org/v1/"),
         ("Microsoft TTS (Madhur)", "https://speech.platform.bing.com/")]

def check():
    rows, miss = [], []
    for name, keys, how, lose in NEEDS:
        ok = all(os.environ.get(k) for k in keys) if name.startswith("YouTube asli") else any(os.environ.get(k) for k in keys)
        rows.append((name, ok))
        if not ok:
            miss.append(f"- **{name}**: jodna hai ({how}). Bina iske: {lose}.")
    web = []
    for n, u in SITES:
        try:
            urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=10).read(200)
            web.append((n, True))
        except Exception as e:
            web.append((n, False))
    return rows, miss, web

def text():
    rows, miss, web = check()
    out = ["**Kaun sa app/tool juda hai:**"] + [f"- {'✅' if ok else '❌'} {n}" for n, ok in rows]
    out += ["", "**Free sites jahan runner pahunch sakta hai:**"] + [f"- {'✅' if ok else '❌'} {n}" for n, ok in web]
    if miss:
        out += ["", "**Ye jodna baaki hai:**"] + miss
    return "\n".join(out)

if __name__ == "__main__":
    print(text())
