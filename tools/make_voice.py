"""Madhur (free Microsoft voice) with exact word timings -> voice.zip (each id.mp3 + words.json).
Runs on GitHub's computer, which can reach the voice server (no Composio / Drive needed).
Usage: python3 tools/make_voice.py episodes/<name>/voice.json out/voice.zip
voice.json: {"LINES": {"ram": ["text", "+2%", "+10Hz"], "vm": ["text", "-12%", "-16Hz"]}}
"""
import asyncio, json, sys, zipfile, os, tempfile
import edge_tts

VOICE = "hi-IN-MadhurNeural"


async def gen(path, text, rate, pitch, tries=8):
    # Microsoft's voice server sometimes sends no audio or drops the connection;
    # wait a little longer each time and try the same line again.
    for i in range(tries):
        try:
            words = await gen_once(path, text, rate, pitch)
            if words and os.path.getsize(path) > 1000:
                return words
            raise edge_tts.exceptions.NoAudioReceived("empty audio")
        except Exception as e:
            if i == tries - 1:
                raise
            print(f"  {type(e).__name__}, retry {i + 1}")
            await asyncio.sleep(4 * (i + 1))


async def gen_once(path, text, rate, pitch):
    c = edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["text"], ch["offset"] / 1e7, ch["duration"] / 1e7])
    return words


async def main(cfg_path, out_zip):
    lines = json.load(open(cfg_path, encoding="utf-8"))["LINES"]
    tmp = tempfile.mkdtemp()
    res = {}
    for k, (text, rate, pitch) in lines.items():
        res[k] = await gen(f"{tmp}/{k}.mp3", text, rate, pitch)
        print(k, len(res[k]), "words")
        await asyncio.sleep(1.5)
    json.dump(res, open(f"{tmp}/words.json", "w", encoding="utf-8"), ensure_ascii=False)
    os.makedirs(os.path.dirname(os.path.abspath(out_zip)), exist_ok=True)
    with zipfile.ZipFile(out_zip, "w") as z:
        for n in [f"{k}.mp3" for k in lines] + ["words.json"]:
            z.write(f"{tmp}/{n}", n)
    print("voice zip:", out_zip)


asyncio.run(main(sys.argv[1], sys.argv[2]))
