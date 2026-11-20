"""Voices with exact word timings -> voice.zip (each id.mp3 + words.json + engine.txt).
Main voice: Madhur (free Microsoft voice, edge-tts, exact word times).
Sahara (backup): Piper, free open-source Hindi voice that runs on GitHub's own computer (rohan / pratham),
used automatically if Madhur does not work (or VOICE_ENGINE=piper). Word times are then estimated from the text.
Usage: python3 tools/make_voice.py episodes/<name>/episode.json out/voice.zip
"""
import asyncio, json, sys, zipfile, os, tempfile, subprocess, wave, urllib.request

VOICE = "hi-IN-MadhurNeural"
PIPER_VOICES = ["rohan", "pratham"]   # Hindi male voices in rhasspy/piper-voices
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/{v}/medium/hi_IN-{v}-medium.onnx"


async def gen_edge(path, text, rate, pitch):
    import edge_tts
    c = edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["text"], ch["offset"] / 1e7, ch["duration"] / 1e7])
    if not words or os.path.getsize(path) < 2000:
        raise RuntimeError("Madhur se awaaz nahi aayi")
    return words


def piper_model(tmp):
    for v in PIPER_VOICES:
        try:
            onnx = f"{tmp}/{v}.onnx"
            urllib.request.urlretrieve(HF.format(v=v), onnx)
            urllib.request.urlretrieve(HF.format(v=v) + ".json", onnx + ".json")
            print("Piper voice:", v)
            return onnx
        except Exception as e:
            print("Piper voice", v, "nahi mili:", e)
    raise RuntimeError("Piper ki koi Hindi awaaz nahi mili")


def gen_piper(voice, path_mp3, text, rate, pitch):
    """Piper wav -> speed/pitch like the Madhur settings -> mp3; word times spread by word length."""
    import piper
    wav = path_mp3[:-4] + "_raw.wav"
    speed = 1 + int(rate.rstrip("%")) / 100.0
    with wave.open(wav, "wb") as w:
        try:
            from piper import SynthesisConfig
            voice.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=1 / max(0.5, speed)))
        except ImportError:   # older piper-tts
            voice.synthesize(text, w, length_scale=1 / max(0.5, speed))
    f = 1 + int(pitch.rstrip("Hz")) / 150.0   # pitch shift like the Madhur pitch setting
    w = wave.open(wav); sr = w.getframerate(); dur = w.getnframes() / sr; w.close()
    flt = f"asetrate={int(sr * f)},aresample={sr},atempo={1 / f:.4f}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", flt, "-ar", "24000", path_mp3], check=True)
    toks = text.split(); lens = [max(1, len(t.strip("।,!?.…"))) for t in toks]
    speech = max(0.3, dur - 0.25); t, words = 0.12, []
    for tok, n in zip(toks, lens):
        d = speech * n / sum(lens)
        words.append([tok.strip("।,!?…"), t, d * 0.9]); t += d
    return words


async def main(cfg_path, out_zip):
    lines = json.load(open(cfg_path, encoding="utf-8"))["LINES"]
    tmp = tempfile.mkdtemp(); res = {}; engine = "madhur"
    if os.environ.get("VOICE_ENGINE", "madhur") != "piper":
        try:
            for k, (text, rate, pitch) in lines.items():
                for attempt in range(8):   # Microsoft kabhi-kabhi awaaz nahi bhejta, isliye 8 koshish
                    try:
                        res[k] = await gen_edge(f"{tmp}/{k}.mp3", text, rate, pitch); break
                    except Exception as e:
                        print(k, "Madhur koshish", attempt + 1, "nahi chali:", e)
                        if attempt == 7: raise
                        await asyncio.sleep(min(30, 5 * (attempt + 1)))
                print(k, len(res[k]), "words (Madhur)")
                await asyncio.sleep(1.5)   # lines ke beech thoda ruk ke, server pe zor kam
        except Exception as e:
            print("Madhur nahi chali, Piper sahara use kar rahe hain:", e); engine = "piper"
    else:
        engine = "piper"
    if engine == "piper":   # whole episode in one voice, never mixed
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "piper-tts"], check=True)
        from piper import PiperVoice
        voice = PiperVoice.load(piper_model(tmp))
        res = {k: gen_piper(voice, f"{tmp}/{k}.mp3", text, rate, pitch) for k, (text, rate, pitch) in lines.items()}
    json.dump(res, open(f"{tmp}/words.json", "w", encoding="utf-8"), ensure_ascii=False)
    open(f"{tmp}/engine.txt", "w").write(engine)
    os.makedirs(os.path.dirname(os.path.abspath(out_zip)), exist_ok=True)
    with zipfile.ZipFile(out_zip, "w") as z:
        for n in [f"{k}.mp3" for k in lines] + ["words.json", "engine.txt"]:
            z.write(f"{tmp}/{n}", n)
    print("voice zip:", out_zip, "| awaaz:", engine)


asyncio.run(main(sys.argv[1], sys.argv[2]))
