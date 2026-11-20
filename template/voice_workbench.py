# Paste into the Composio remote workbench (the sandbox cannot reach the voice server).
# Free Microsoft Madhur voice with exact word timings -> zip -> Google Drive (account googledrive_titan-wiper).
# Then download the printed Drive file id with the Google Drive download tool and pass it as VOICE_ZIP.
import subprocess, sys, json, zipfile
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "edge-tts"], capture_output=True)
import edge_tts
LINES = {   # id: (text in everyday spoken Hindi, rate, pitch)  — Ram ~ "+2%","+10Hz"; Vishwamitra ~ "-12%","-16Hz"
    "ram": ("गुरुदेव... ये इतना डरावना जंगल किसका है?", "+2%", "+10Hz"),
    "vm": ("ये ताड़का का वन है, राम। उसमें हज़ार हाथियों जितनी ताक़त है!", "-12%", "-16Hz"),
}
EPNAME = "bhag4"
async def gen(k, t, r, p):
    c = edge_tts.Communicate(t, "hi-IN-MadhurNeural", rate=r, pitch=p, boundary="WordBoundary"); words = []
    with open(f"/home/user/{k}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": words.append([ch["text"], ch["offset"] / 1e7, ch["duration"] / 1e7])
    return words
res = {k: await gen(k, *v) for k, v in LINES.items()}
json.dump(res, open("/home/user/words.json", "w"), ensure_ascii=False)
with zipfile.ZipFile(f"/home/user/{EPNAME}_voice.zip", "w") as z:
    for n in [f"{k}.mp3" for k in LINES] + ["words.json"]: z.write("/home/user/" + n, n)
u, e = upload_local_file(f"/home/user/{EPNAME}_voice.zip")
r, e2 = run_composio_tool("GOOGLEDRIVE_UPLOAD_FILE", {"file_to_upload": {"name": f"{EPNAME}_voice.zip", "mimetype": "application/zip", "s3key": u["s3key"]}}, account="googledrive_titan-wiper")
print(e, e2, "DRIVE_ID:", r.get("data", {}).get("id"))
