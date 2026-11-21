"""
Machine jaanch (AI nahi, ginti): video par ffmpeg se sachchi cheezein naapta hai.
Free hai, har baar ek jaisa jawab deta hai, isliye AI ki aankh/kaan se zyada bharosemand.

Use:  python3 tools/machine_checks.py <video.mp4> [out.json]
Jawab: JSON {"ok": bool, "fails": [...], "warns": [...], "facts": {...}}  (aur ek chhota Hinglish text)

Jo cheezein jaanchi jaati hain:
  - size 1080x1920, fps, lambai (Short: 20-62 sec), awaaz hai ya nahi
  - kaali frame (beech mein khaali screen)            -> FAIL
  - ruki hui (frozen) frame lambe samay tak           -> WARN (bolte waqt zyada ho toh FAIL)
  - lambi khamoshi (awaaz ke beech mein)              -> WARN
  - awaaz ka zor (LUFS) bahut dheema / bahut tez      -> FAIL
  - awaaz ke hisson mein zor ka bahut fark (koi line dheemi) -> WARN
"""
import json
import re
import subprocess
import sys


def _run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    return (r.stdout or "") + (r.stderr or "")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path],
                         capture_output=True, text=True).stdout
    j = json.loads(out or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in j.get("streams", []) if s.get("codec_type") == "audio"), None)
    num, _, den = (v.get("r_frame_rate") or "0/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 0.0
    return {"w": v.get("width"), "h": v.get("height"), "fps": round(fps, 2),
            "dur": float(j.get("format", {}).get("duration") or 0), "has_audio": a is not None}


def black_frames(path):
    txt = _run(["ffmpeg", "-nostats", "-i", path, "-vf", "blackdetect=d=0.2:pix_th=0.10", "-an", "-f", "null", "-"])
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", txt)]


def frozen_segments(path, min_len=2.0):
    txt = _run(["ffmpeg", "-nostats", "-i", path, "-vf", f"freezedetect=n=-60dB:d={min_len}", "-an", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", txt)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", txt)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def silences(path, min_len=0.9):
    txt = _run(["ffmpeg", "-nostats", "-i", path, "-af", f"silencedetect=n=-42dB:d={min_len}", "-vn", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", txt)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", txt)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def loudness(path, ss=None, t=None):
    cmd = ["ffmpeg", "-nostats"]
    if ss is not None:
        cmd += ["-ss", str(ss)]
    if t is not None:
        cmd += ["-t", str(t)]
    cmd += ["-i", path, "-af", "ebur128", "-vn", "-f", "null", "-"]
    txt = _run(cmd)
    m = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", txt, re.M)
    return float(m[-1]) if m else None


def check(path):
    fails, warns, facts = [], [], {}
    p = probe(path)
    facts.update(p)
    if (p["w"], p["h"]) != (1080, 1920):
        fails.append(f"size {p['w']}x{p['h']} hai, Short ke liye 1080x1920 chahiye")
    if p["fps"] and p["fps"] < 24:
        warns.append(f"fps kam hai ({p['fps']})")
    if not (20 <= p["dur"] <= 62):
        (fails if (p["dur"] < 8 or p["dur"] > 180) else warns).append(f"lambai {p['dur']:.1f} sec (Short ke liye 20-62 sec theek)")
    elif p["dur"] > 50:
        warns.append(f"lambai {p['dur']:.1f} sec, VIRAL.md ka target 35-45 sec hai")
    if not p["has_audio"]:
        fails.append("video mein awaaz hai hi nahi")
        return _pack(fails, warns, facts)

    blk = black_frames(path)
    facts["black"] = blk
    # shuru ke 0.1 sec ka cover kaala nahi hota; beech/aakhir mein kaala ruka toh galti
    for a, b in blk:
        if b - a >= 0.3:
            fails.append(f"kaali (khaali) screen {a:.1f}s se {b:.1f}s tak")

    fro = frozen_segments(path, 2.5)
    facts["frozen"] = fro
    for a, b in fro:
        end = b if b is not None else p["dur"]
        if end - a >= 4.0:
            fails.append(f"video {a:.1f}s se {end:.1f}s tak ruka hua (frozen)")
        else:
            warns.append(f"{a:.1f}s se {end:.1f}s tak koi hilchal nahi")

    sil = silences(path, 0.9)
    facts["silence"] = sil
    for a, b in sil:
        end = b if b is not None else p["dur"]
        if a < 0.3 or end >= p["dur"] - 0.2:
            continue        # shuru/aakhir ki khamoshi theek
        if end - a >= 1.5:
            fails.append(f"{a:.1f}s se {end:.1f}s tak lambi khamoshi (khaali second)")
        else:
            warns.append(f"{a:.1f}s par {end - a:.1f}s ki khamoshi")

    lufs = loudness(path)
    facts["lufs"] = lufs
    if lufs is None or lufs < -30:
        fails.append(f"awaaz bahut dheemi ({lufs} LUFS)")
    elif lufs > -8:
        fails.append(f"awaaz bahut tez ({lufs} LUFS), phatne ka darr")
    elif not (-20 <= lufs <= -12):
        warns.append(f"awaaz ka zor {lufs} LUFS (Shorts ke liye -16 ke aaspaas achha)")

    # 4 barabar hisson mein zor ka fark: koi hissa baaki se bahut dheema ho toh line dheemi hai
    parts = []
    n = 4
    seg = p["dur"] / n
    for i in range(n):
        v = loudness(path, ss=round(i * seg, 2), t=round(seg, 2))
        parts.append(v)
    facts["lufs_parts"] = parts
    vals = [v for v in parts if v is not None]
    if len(vals) >= 3 and max(vals) - min(vals) > 7:
        warns.append(f"awaaz ke hisson ka zor bahut alag hai ({', '.join(f'{v:.0f}' for v in vals)} LUFS): koi line dheemi/tez ho sakti hai")
    return _pack(fails, warns, facts)


def _pack(fails, warns, facts):
    lines = ["Machine jaanch: " + ("✅ theek" if not fails else "❌ FAIL")]
    lines += [f"- ❌ {x}" for x in fails] + [f"- ⚠️ {x}" for x in warns]
    f = facts
    lines.append(f"- ℹ️ {f.get('w')}x{f.get('h')}, {f.get('fps')} fps, {f.get('dur', 0):.1f} sec, zor {f.get('lufs')} LUFS")
    return {"ok": not fails, "fails": fails, "warns": warns, "facts": facts, "text": "\n".join(lines)}


if __name__ == "__main__":
    res = check(sys.argv[1])
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=1)
    print(res["text"])
    sys.exit(0 if res["ok"] else 1)
