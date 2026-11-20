import subprocess, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script import LINES

V = "/home/claude/dl/voices/"
OUT = "/home/claude/lak/audio"
os.makedirs(OUT, exist_ok=True)

# speaker -> (model, length_scale, pitch factor, sentence silence)
SPK = {
    "N": ("hi_IN-pratham-medium", 1.05, 1.00),
    "G": ("hi_IN-pratham-medium", 1.25, 0.90),   # old, weak, low
    "E": ("hi_IN-pratham-medium", 1.00, 1.10),   # different, a bit higher
    "R": ("hi_IN-priyamvada-medium", 1.05, 1.00),
}

def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

info = []
for lid, spk, scene, text in LINES:
    model, ls, pitch = SPK[spk]
    raw = f"{OUT}/{lid}_raw.wav"
    subprocess.run([sys.executable, "-I", "-m", "piper", "-m", V + model + ".onnx", "-f", raw,
                    "--length-scale", str(ls), "--sentence-silence", "0.25"],
                   input=text.encode(), check=True, capture_output=True)
    fin = f"{OUT}/{lid}.wav"
    af = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
    if pitch != 1.0:
        af = f"asetrate=22050*{pitch},aresample=22050,atempo={1/pitch:.4f}," + af
    if spk == "R":
        af += ",volume=1.15"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", "44100", "-ac", "1", fin], check=True)
    d = dur(fin)
    info.append({"id": lid, "spk": spk, "scene": scene, "text": text, "dur": round(d, 3)})
    print(lid, spk, scene, round(d, 2))

json.dump(info, open(f"{OUT}/lines.json", "w"), ensure_ascii=False, indent=1)
print("total speech", round(sum(i["dur"] for i in info), 2))
