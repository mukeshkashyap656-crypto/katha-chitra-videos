import datetime, glob, json, os, shutil

ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
today = ist.date()
ej = json.load(open("stage/episode.json", encoding="utf-8"))
bhag = str(ej.get("BHAG") or os.environ["BHAG"])
try:
    q = json.load(open("stage/queue.json", encoding="utf-8"))
    item = next((x for x in q["episodes"] if str(x["bhag"]) == bhag), None)
except OSError:
    item = None
date = item["date"] if item else str(today)
if date < str(today):
    date = str(today)
mp4 = sorted(glob.glob("stage/*.mp4"))[0]
jpgs = [p for p in glob.glob("stage/*.jpg") if not p.endswith(("check_sheet.jpg", "ending_sheet.jpg"))]
jpgs.sort(key=lambda p: (0 if "cover" in os.path.basename(p).lower() else 1, p))   # asli cover pehle, sheet kabhi nahi
os.makedirs("videos", exist_ok=True)
vname = os.path.basename(mp4)
shutil.copy(mp4, "videos/" + vname)
cover = ""
if jpgs:
    cover = "videos/" + os.path.basename(jpgs[0])
    shutil.copy(jpgs[0], cover)
size = os.path.getsize("videos/" + vname)
question = (ej.get("QUESTION") or "").strip()
lines = ej.get("LINES", {})
first = ""
if lines:
    v = list(lines.values())[0]
    first = (v[0] if isinstance(v, list) else str(v)).strip()
suffix = " 😱 #shorts"   # niyam: title seedha sawaal; "भाग X" description + tags mein
title = question + suffix
if len(title) > 100:
    title = question[: max(10, 100 - len(suffix) - 1)] + "…" + suffix
caption = (f"🎬 रामायण भाग {bhag} (वाल्मीकि रामायण)\n{question} 😱\n\n{first}\n\n📖 वाल्मीकि रामायण (बालकाण्ड) | भाग {bhag}\n"
           "👉 कमेंट करें: जय श्री राम 🚩\n🔔 Follow करें — रोज़ शाम 7 बजे रामायण का नया भाग!\n\n"
           "#ramayan #valmikiramayan #jaishriram #ramayanshorts #kathachitra")
tags = ["valmiki ramayan", "ramayana facts", "ramayan story", "ramayan in hindi", "jai shri ram", "katha chitra", "ramayan shorts", f"ramayan bhag {bhag}"]
eps = json.load(open("episodes.json", encoding="utf-8"))
old = eps.get(bhag, {})
if old.get("status") == "posted" or old.get("youtube_id") or old.get("instagram_id"):
    print(f"Bhag {bhag} pehle se post ho chuka hai, kuch nahi badla")
else:
    eps[bhag] = {"file": "videos/" + vname, "size": size, "cover": cover, "title": title, "caption": caption,
                 "tags": tags, "date": date, "auto": True, "status": "ready"}
    json.dump(eps, open("episodes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Bhag {bhag} tayyar: {vname}, post tithi {date} (shaam 7 baje IST)")
