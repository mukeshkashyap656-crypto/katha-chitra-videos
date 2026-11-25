"""Gaming kahani ki free awaaz (har line alag file + har shabd ka samay). Sirf awaaz banata hai, kuch post nahi."""
import asyncio, json, os, sys
import edge_tts

VOICE = {"n": ("hi-IN-MadhurNeural", "+6%", "+0Hz"),      # kahani sunane wala
         "p": ("en-US-BrianMultilingualNeural", "-8%", "+0Hz")}  # player


async def one(lid, text, who, out):
    v, rate, pitch = VOICE[who]
    words = []
    c = edge_tts.Communicate(text, v, rate=rate, pitch=pitch, boundary="WordBoundary")
    with open(f"{out}/{lid}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["text"], ch["offset"] / 1e7, ch["duration"] / 1e7])
    assert os.path.getsize(f"{out}/{lid}.mp3") > 3000, lid
    return {"id": lid, "text": text, "who": who, "voice": v, "words": words}


async def main(src, out):
    os.makedirs(out, exist_ok=True)
    res = []
    for lid, text, who in json.load(open(src, encoding="utf-8")):
        for k in range(4):
            try:
                res.append(await one(lid, text, who, out)); break
            except Exception as e:
                print(lid, "dobara:", str(e)[:150]); await asyncio.sleep(5)
        else:
            sys.exit("awaaz nahi bani: " + lid)
        print(lid, "OK", len(res[-1]["words"]), "shabd")
    json.dump(res, open(f"{out}/voice.json", "w", encoding="utf-8"), ensure_ascii=False)

asyncio.run(main(sys.argv[1], sys.argv[2]))
