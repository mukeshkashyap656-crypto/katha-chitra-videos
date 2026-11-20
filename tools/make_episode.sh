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
DRAW=$E/draw_assets.py; [ -f "$DRAW" ] || DRAW=$R/template/draw_assets.py
BUILD=$E/build_episode.py; [ -f "$BUILD" ] || BUILD=$R/template/build_episode.py
# episode scripts import from template/lib
export PYTHONPATH=$R/template/lib:$PYTHONPATH
EP=$EP VOICE_ZIP=$EP/voice.zip python3 "$DRAW"
EP=$EP python3 "$BUILD"
cd "$EP/proj"
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
ffmpeg -v error -y -i "$OUT/$NAME.mp4" -vf "fps=4,scale=180:-1,tile=10x8" -frames:v 1 "$OUT/check_sheet.jpg"
ls -la "$OUT"
