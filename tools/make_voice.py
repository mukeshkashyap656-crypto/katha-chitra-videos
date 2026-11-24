"""Voices with exact word timings -> voice.zip (each id.mp3 + words.json + engine.txt).
Main voice: Madhur (free Microsoft voice, edge-tts, exact word times).
Sahara (backup): Piper, free open-source Hindi voice that runs on GitHub's own computer (rohan / pratham),
used automatically if Madhur does not work (or VOICE_ENGINE=piper). Word times are then estimated from the text.
Usage: python3 tools/make_voice.py episodes/<name>/episode.json out/voice.zip
"""
import asyncio, json, sys, zipfile, os, tempfile, subprocess, wave, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine"))
try:
    import spec as SP
except Exception:
    SP = None

VOICE = "hi-IN-MadhurNeural"
# Har kirdaar ki apni awaaz (user ka hukm 24 Nov 2026). Sahare ki list: pehli na chale to agli, aakhir mein Madhur (hamesha chalti hai).
# episode.json mein "VOICES": {"narrator": "<edge voice>", "vayu": "<edge voice>"} se badal sakte hain.
FALLBACK = "hi-IN-MadhurNeural"
VOICE_DEFAULT = {
    "narrator": ["en-US-AdamMultilingualNeural", "en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", FALLBACK],   # kathavachak: Adam
    "female": ["hi-IN-SwaraNeural", FALLBACK],
    "male": [FALLBACK],
}
PIPER_VOICES = ["rohan", "pratham"]   # Hindi male voices in rhasspy/piper-voices
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/{v}/medium/hi_IN-{v}-medium.onnx"


def _estimate_words(path, text):
    """Kuch awaazon se shabd-samay nahi aata: mp3 ki lambai ko shabdon ki lambai ke hisaab se baant do."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                               capture_output=True, text=True, check=True).stdout.strip())
    toks = text.split(); lens = [max(1, len(t.strip("।,!?.…"))) for t in toks]
    speech = max(0.3, dur - 0.3); t, words = 0.12, []
    for tok, n in zip(toks, lens):
        d = speech * n / sum(lens); words.append([tok.strip("।,!?…"), t, d * 0.9]); t += d
    return words


async def gen_edge(path, text, rate, pitch, voice=VOICE):
    import edge_tts
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["text"], ch["offset"] / 1e7, ch["duration"] / 1e7])
    if os.path.getsize(path) < 2000:
        raise RuntimeError(f"{voice} se awaaz nahi aayi")
    if not words:
        words = _estimate_words(path, text)
    return words


def voices_for(k, epi):
    """Line k ke liye awaazon ki list (pehli pasandida, phir sahare)."""
    who = SP.speaker(k, epi) if SP else None
    over = epi.get("VOICES", {})
    if who is None: role = "narrator"
    elif over.get(who): role = who
    else:
        nc = epi.get("NEW_CHARS", {}).get(who, {})
        role = "female" if (nc.get("kind") == "f" or who.startswith("kanya") or who in ("sita", "urmila")) else "male"
    lst = over.get(role) or VOICE_DEFAULT.get(role) or VOICE_DEFAULT["male"]
    lst = [lst] if isinstance(lst, str) else list(lst)
    if FALLBACK not in lst: lst.append(FALLBACK)
    return role, lst


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
    epi = json.load(open(cfg_path, encoding="utf-8")); lines = epi["LINES"]
    tmp = tempfile.mkdtemp(); res = {}; engine = "madhur"; used = {}
    if os.environ.get("VOICE_ENGINE", "madhur") != "piper":
        try:
            for k, (text, rate, pitch) in lines.items():
                role, vlist = voices_for(k, epi); done = False
                for vi, vname in enumerate(vlist):
                    tries = 8 if vname == FALLBACK else 3          # pasandida awaaz par 3 koshish, phir agli; Madhur par 8
                    for attempt in range(tries):
                        try:
                            res[k] = await gen_edge(f"{tmp}/{k}.mp3", text, rate, pitch, vname); used[k] = f"{role}: {vname}"; done = True; break
                        except Exception as e:
                            print(k, vname, "koshish", attempt + 1, "nahi chali:", e)
                            if attempt == tries - 1 and vname == FALLBACK: raise
                            await asyncio.sleep(min(30, 4 * (attempt + 1)) if vname == FALLBACK else 2)
                    if done: break
                print(k, len(res[k]), "words |", used[k])
                await asyncio.sleep(1.5)   # lines ke beech thoda ruk ke, server pe zor kam
            json.dump(used, open(f"{tmp}/voices.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("KAUN SI AWAAZ KISKI:", json.dumps(used, ensure_ascii=False))
        except Exception as e:
            if os.environ.get("MADHUR_ONLY") == "1":
                # pehle poora kaam dobara try hoga (workflow), Piper sirf aakhri sahara
                raise SystemExit(f"Madhur abhi nahi chali ({e}); thodi der baad poora episode dobara banega")
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
        if os.path.exists(f"{tmp}/voices.json"): z.write(f"{tmp}/voices.json", "voices.json")
    print("voice zip:", out_zip, "| awaaz:", engine)


asyncio.run(main(sys.argv[1], sys.argv[2]))
