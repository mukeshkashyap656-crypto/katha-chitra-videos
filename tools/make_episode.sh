#!/bin/bash
# One episode, start to finish: voice -> drawings -> HyperFrames video -> cover as first 0.1 s -> out/<NAME>.mp4 + out/<NAME_cover>.jpg
# Usage: bash tools/make_episode.sh episodes/<name>
# The episode folder has episode.json (NAME, COVER_NAME, LINES) and may have its own draw_assets.py / build_episode.py
# (otherwise the template examples are used).
set -e
R=$(cd "$(dirname "$0")/.." && pwd); E=$(cd "$1" && pwd); EP=${EP:-/tmp/ep}; OUT=$R/out
NAME=$(python3 -c "import json;print(json.load(open('$E/episode.json'))['NAME'])")
COVER=$(python3 -c "import json;print(json.load(open('$E/episode.json')).get('COVER_NAME','${NAME}_Cover'))")
mkdir -p "$OUT"
bash "$R/template/setup.sh" "$EP"
python3 "$R/tools/make_voice.py" "$E/episode.json" "$EP/voice.zip"
unzip -p "$EP/voice.zip" engine.txt > "$OUT/voice_engine.txt" 2>/dev/null || echo madhur > "$OUT/voice_engine.txt"
DRAW=$E/draw_assets.py; BUILD=$E/build_episode.py
if [ ! -f "$DRAW" ] && grep -q '"SHOTS"' "$E/episode.json"; then
  # data-only episode (scene list): the scene engine draws and builds it, no episode code needed
  python3 "$R/tools/engine/spec.py" "$E/episode.json"
  DRAW=$R/tools/engine/draw.py; BUILD=$R/tools/engine/build.py
fi
[ -f "$DRAW" ] || DRAW=$R/template/draw_assets.py
[ -f "$BUILD" ] || BUILD=$R/template/build_episode.py
export EPDIR=$E
# episode scripts import from template/lib
export PYTHONPATH=$R/template/lib:$PYTHONPATH
EP=$EP VOICE_ZIP=$EP/voice.zip python3 "$DRAW"
EP=$EP python3 "$BUILD"
cd "$EP/proj"
# the cover is its own small project: copy every picture it uses from proj/assets
for f in $(grep -o -E 'assets/[A-Za-z0-9_./-]+' cover/index.html | sort -u); do [ -f "$f" ] && cp "$f" "cover/$f"; done
npx hyperframes lint . | tee "$OUT/lint.txt"
grep -q -E '\b[1-9][0-9]* error' "$OUT/lint.txt" && { echo "lint errors"; exit 1; } || true
npx hyperframes render . -q delivery -o raw.mp4
# cover: render the cover composition itself (snapshot adds labels/guide lines), take the frame at 0.5 s
(cd cover && npx hyperframes render . -q delivery -o ../cover.mp4)
ffmpeg -v error -y -ss 0.5 -i cover.mp4 -frames:v 1 -vf "scale=1080:1920" -q:v 2 "$OUT/$COVER.jpg"
# cover as the very first 0.1 s (phone gallery thumbnail / YouTube thumbnail pick)
ffmpeg -v error -y -loop 1 -t 0.1 -i "$OUT/$COVER.jpg" -f lavfi -t 0.1 -i anullsrc=r=48000:cl=stereo \
  -vf "scale=1080:1920,fps=30,format=yuv420p" -c:v libx264 -c:a aac -shortest /tmp/c.mp4
ffmpeg -v error -y -i raw.mp4 -vf "fps=30,format=yuv420p" -c:v libx264 -crf 18 -c:a aac -ar 48000 -ac 2 /tmp/r.mp4
printf "file /tmp/c.mp4\nfile /tmp/r.mp4\n" > /tmp/l.txt
ffmpeg -v error -y -f concat -safe 0 -i /tmp/l.txt -c copy -movflags +faststart "$OUT/$NAME.mp4"
# director-check sheet: a frame every 0.25 s
# sound check (like "earshot"): the video must really have voice at a normal level, never silent
ffmpeg -nostats -i "$OUT/$NAME.mp4" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | tee "$OUT/sound_check.txt"
LUFS=$(grep -oE -- "-?[0-9]+\.[0-9]+" "$OUT/sound_check.txt" | head -1)
python3 -c "import sys; l=float('${LUFS:--99}'); print('awaaz level', l, 'LUFS'); sys.exit(0 if l > -40 else 'AWAAZ NAHI HAI / bahut dheemi: video mein awaaz check karo')"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$NAME.mp4")
# poori video ki sheet: 100 frame poore video par failte hue (chhota video ho toh har 0.25 s)
FPS=$(python3 -c "print(round(min(4.0, 100.0/float('$DUR')), 4))")
ffmpeg -v error -y -i "$OUT/$NAME.mp4" -vf "fps=$FPS,scale=180:-1,tile=10x10" -frames:v 1 "$OUT/check_sheet.jpg"
# aakhri 5 second (subscribe widget yahin dikhta hai): har 0.25 s
ffmpeg -v error -y -ss "$(python3 -c "print(max(0.0, float('$DUR')-5.0))")" -i "$OUT/$NAME.mp4" -vf "fps=4,scale=180:-1,tile=10x2" -frames:v 1 "$OUT/ending_sheet.jpg"
# machine jaanch: cover sach mein pehla frame hai? (AI se nahi, ginti se)
ffmpeg -v error -y -i "$OUT/$NAME.mp4" -frames:v 1 -vf "scale=540:960" /tmp/first.png
ffmpeg -v error -y -i "$OUT/$COVER.jpg" -vf "scale=540:960" /tmp/cov.png
PSNR=$(ffmpeg -i /tmp/first.png -i /tmp/cov.png -lavfi psnr -f null - 2>&1 | grep -oE "average:[0-9.]+|average:inf" | head -1 | cut -d: -f2)
python3 -c "p='${PSNR:-0}'; v=99.0 if p=='inf' else float(p); open('$OUT/first_frame_check.txt','w').write(('ok ' if v>25 else 'FAIL ')+str(v))"
cat "$OUT/first_frame_check.txt"
# sachchi ginti wali machine jaanch (kaali screen, ruka video, khamoshi, awaaz ka zor); fail hone par bhi video rukta nahi, review use padhta hai
python3 "$R/tools/machine_checks.py" "$OUT/$NAME.mp4" "$OUT/machine_report.json" | tee "$OUT/machine_report.txt" || true
ls -la "$OUT"
