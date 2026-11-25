"""Voices with exact word timings -> voice.zip (each id.mp3 + words.json + engine.txt).
Main voice: Madhur (free Microsoft voice, edge-tts, exact word times).
Sahara (backup): Piper, free open-source Hindi voice that runs on GitHub's own computer (rohan / pratham),
used automatically if Madhur does not work (or VOICE_ENGINE=piper). Word times are then estimated from the text.
Usage: python3 tools/make_voice.py episodes/<name>/episode.json out/voice.zip
"""
import asyncio, json, sys, zipfile, os, tempfile, subprocess, wave, urllib.request, hashlib, shutil
# Wahi line (wahi text, awaaz, speed) dobara ho toh purani bani awaaz wapas lo: episode baar baar banta hai, har baar awaaz nahi banani.
CACHE = os.path.expanduser(os.environ.get("VOICE_CACHE", "~/.cache/kc_voice"))
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


# ---- ElevenLabs (mashhoor awaazein): ELEVENLABS_API_KEY (GitHub secret) ho to sabse pehle yahi; na chale to neeche ki free awaazein ----
import base64, urllib.error
ELEVEN = {   # kirdaar -> (naam, voice_id): ElevenLabs ki premade (mashhoor) awaazein
    "narrator": ("Adam", "pNInz6obpgDQGcFmaJgB"),
    "vishwamitra": ("George", "JBFqnCBsd6RMkjVDRZzb"), "ram": ("Liam", "TX3LPaxmHKxFdv7VOQHJ"),
    "lakshman": ("Josh", "TxGEqnHWrfWFTfGW9XjX"), "vasishtha": ("Daniel", "onwK4e9ZLuTAKqWW03F9"),
    "dasharatha": ("Brian", "nPczCjzI2devNBz1zQrb"),
    "_devta": ("Arnold", "VR6AewLTigWG4xSOukaG"), "_rakshas": ("Charlie", "IKne3meq5aSn9XLyUdCD"),
}
ELEVEN_FEMALE = [("Sarah", "EXAVITQu4vr4xnSDxMaL"), ("Matilda", "XrExE9yKIg1WjnnlVkGX"), ("Jessica", "cgSgspJ2msm6clMCkdW9")]
ELEVEN_MALE = [("Antoni", "ErXwobaYiN019PkySvjV"), ("Sam", "yoZ06aMxZJJ28mfd3POQ"), ("Callum", "N2lVS1w4EtoT3dr4eOWO"), ("Eric", "cjVigY5qzO86Huf0OWal")]


def eleven_pick(role, who, epi):
    over = epi.get("ELEVEN_VOICES", {})
    if who and over.get(who): return over[who] if isinstance(over[who], list) else ("custom", over[who])
    if role == "narrator": return ELEVEN["narrator"]
    if who in ELEVEN: return ELEVEN[who]
    nc = epi.get("NEW_CHARS", {}).get(who or "", {})
    if nc.get("rakshas"): return ELEVEN["_rakshas"]
    if nc.get("big"): return ELEVEN["_devta"]
    pool = ELEVEN_FEMALE if role == "female" else ELEVEN_MALE
    return pool[sum(map(ord, who or "x")) % len(pool)]


def gen_eleven(path, text, rate, vid):
    import json as _j
    key = os.environ["ELEVENLABS_API_KEY"]
    spd = max(0.7, min(1.2, 1 + int(rate.rstrip("%")) / 100.0))
    body = {"text": text, "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True, "speed": spd}}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128",
                                 data=_j.dumps(body).encode(), headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r: d = _j.load(r)
    open(path, "wb").write(base64.b64decode(d["audio_base64"]))
    al = d.get("normalized_alignment") or d["alignment"]
    ch, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, t0, t1 = [], "", None, 0
    for c, a, b in zip(ch, st, en):
        if c.isspace():
            if cur: words.append([cur, t0, t1 - t0]); cur = ""; t0 = None
        else:
            if t0 is None: t0 = a
            cur += c; t1 = b
    if cur: words.append([cur, t0, t1 - t0])
    if os.path.getsize(path) < 2000 or not words: raise RuntimeError("ElevenLabs se awaaz nahi aayi")
    return words


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
                _who = SP.speaker(k, epi) if SP else None
                _ck = hashlib.sha1(json.dumps([text, rate, pitch, vlist, role, _who, bool(os.environ.get("ELEVENLABS_API_KEY")),
                                               epi.get("ELEVEN_VOICES", {})], ensure_ascii=False).encode()).hexdigest()[:24]
                try:
                    if os.path.exists(f"{CACHE}/{_ck}.json") and os.path.getsize(f"{CACHE}/{_ck}.mp3") > 2000:
                        _c = json.load(open(f"{CACHE}/{_ck}.json", encoding="utf-8"))
                        shutil.copy(f"{CACHE}/{_ck}.mp3", f"{tmp}/{k}.mp3"); res[k] = _c["words"]; used[k] = _c["used"]
                        print(k, len(res[k]), "words |", used[k], "| purani bani awaaz (cache)"); continue
                except Exception as e:
                    print(k, "cache nahi padha:", e)
                # 25 Nov 2026 (user ka hukm): ElevenLabs sirf kathavachak (Adam) ke liye; baaki sab kirdaar free awaaz.
                # Kisi kirdaar ko ElevenLabs dena ho to episode.json "ELEVEN_VOICES" mein uska naam likho.
                if os.environ.get("ELEVENLABS_API_KEY") and (role == "narrator" or (_who and _who in epi.get("ELEVEN_VOICES", {}))):
                    nm, vid = eleven_pick(role, _who, epi)
                    for attempt in range(3):
                        try:
                            res[k] = gen_eleven(f"{tmp}/{k}.mp3", text, rate, vid); used[k] = f"{role}: ElevenLabs {nm}"; done = True; break
                        except urllib.error.HTTPError as e:
                            print(k, "ElevenLabs", nm, "koshish", attempt + 1, "HTTP", e.code, e.read()[:150])
                            if e.code in (401, 402, 403, 429) and attempt >= 1: break      # key/limit ka masla: free awaaz par jao
                            await asyncio.sleep(3)
                        except Exception as e:
                            print(k, "ElevenLabs", nm, "koshish", attempt + 1, "nahi chali:", e); await asyncio.sleep(3)
                for vi, vname in enumerate([] if done else vlist):
                    tries = 6 if vname == FALLBACK else 2          # pasandida awaaz par 2 koshish, phir agli; Madhur par 6
                    for attempt in range(tries):
                        try:
                            res[k] = await gen_edge(f"{tmp}/{k}.mp3", text, rate, pitch, vname); used[k] = f"{role}: {vname}"; done = True; break
                        except Exception as e:
                            print(k, vname, "koshish", attempt + 1, "nahi chali:", e)
                            if attempt == tries - 1 and vname == FALLBACK: raise
                            await asyncio.sleep(min(10, 2 * (attempt + 1)) if vname == FALLBACK else 1)
                    if done: break
                print(k, len(res[k]), "words |", used[k])
                try:
                    os.makedirs(CACHE, exist_ok=True)
                    shutil.copy(f"{tmp}/{k}.mp3", f"{CACHE}/{_ck}.mp3")
                    json.dump({"words": res[k], "used": used[k]}, open(f"{CACHE}/{_ck}.json", "w", encoding="utf-8"), ensure_ascii=False)
                except Exception as e:
                    print(k, "cache mein nahi rakha:", e)
                await asyncio.sleep(0.5)   # lines ke beech thoda ruk ke, server pe zor kam
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
