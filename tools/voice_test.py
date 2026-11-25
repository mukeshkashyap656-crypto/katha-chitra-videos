"""Free awaazon ke namoone: ek hi Hindi line har awaaz mein. Sirf sunne ke liye; kisi video ki awaaz nahi badalta."""
import asyncio
import os
import subprocess
import sys

LINE = "भैया, ज़रा रुकिए! जंगल में कोई हमें देख रहा है। क्या आप भी वो आवाज़ सुन रहे हैं?"
EDGE = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural",
        "en-US-AvaMultilingualNeural", "en-US-EmmaMultilingualNeural", "en-AU-WilliamMultilingualNeural",
        "fr-FR-RemyMultilingualNeural", "fr-FR-VivienneMultilingualNeural", "de-DE-FlorianMultilingualNeural",
        "de-DE-SeraphinaMultilingualNeural", "it-IT-GiuseppeMultilingualNeural", "ko-KR-HyunsuMultilingualNeural",
        "pt-BR-ThalitaMultilingualNeural"]
KOKORO = ["hf_alpha", "hf_beta", "hm_omega", "hm_psi"]
OUT = "voice_out"


async def edge(voice, path):
    import edge_tts
    await edge_tts.Communicate(LINE, voice).save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    done = []
    for v in EDGE:
        p = f"{OUT}/edge_{v}.mp3"
        try:
            asyncio.run(edge(v, p))
            assert os.path.getsize(p) > 5000
            done.append((v, p))
        except Exception as e:
            print("BAND:", v, str(e)[:150])
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
        pipe = KPipeline(lang_code="h")
        for v in KOKORO:
            try:
                audio = np.concatenate([a for _, _, a in pipe(LINE, voice=v)])
                p = f"{OUT}/kokoro_{v}.wav"
                sf.write(p, audio, 24000)
                done.append(("kokoro " + v, p))
            except Exception as e:
                print("BAND: kokoro", v, str(e)[:150])
    except Exception as e:
        print("BAND: kokoro", str(e)[:200])
    for name, p in done:
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                           capture_output=True, text=True).stdout.strip()
        print("CHALU:", name, d, "sec")
    if not done:
        sys.exit(1)


if __name__ == "__main__":
    main()
