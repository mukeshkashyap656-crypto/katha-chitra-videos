set -e
cd /tmp/mk
N=$(python3 -c "import json;print(round(json.load(open('meta.json'))['total']*30))")
Q=$(( (N+3)/4 )); : > list.txt; pids=()
for k in 0 1 2 3; do a=$((k*Q)); z=$(( (k+1)*Q )); [ $z -gt $N ] && z=$N; python3 src/shot.py video $a $z part$k.mp4 > log$k.txt 2>&1 & pids+=($!); echo "file part$k.mp4" >> list.txt; done
for p in "${pids[@]}"; do wait $p; done
cat log*.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy body.mp4
python3 -I - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto('file:///tmp/mk/page.html'); pg.evaluate('document.fonts.ready'); pg.evaluate('frame(0)'); pg.wait_for_timeout(400)
    pg.evaluate("document.getElementById('s').innerHTML=DEFS+cover();for(const i of ['q','tag','sub','cta'])document.getElementById(i).style.display='none'")
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/mk/cover.jpg',type='jpeg',quality=94)
PY
ffmpeg -v error -y -framerate 30 -loop 1 -t 0.1 -i cover.jpg -vf format=yuv420p -c:v libx264 -crf 19 -preset veryfast -pix_fmt yuv420p c.mp4
printf "file c.mp4\nfile body.mp4\n" > l2.txt
ffmpeg -v error -y -f concat -safe 0 -i l2.txt -c copy v.mp4
ffmpeg -v error -y -i v.mp4 -f f32le -ar 48000 -ac 1 -i a.f32 -map 0:v -map 1:a -af "adelay=100,loudnorm=I=-15:TP=-1.5:LRA=11" -ar 48000 -ac 2 -c:v copy -c:a aac -b:a 192k -movflags +faststart MKGaming_1_Game_Band_Player_Chalu.mp4
cp cover.jpg MKGaming_1_Cover.jpg
ffprobe -v error -show_entries format=duration,size -of csv=p=0 MKGaming_1_Game_Band_Player_Chalu.mp4
ffmpeg -nostats -i MKGaming_1_Game_Band_Player_Chalu.mp4 -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1
ffmpeg -hide_banner -i MKGaming_1_Game_Band_Player_Chalu.mp4 -af silencedetect=n=-45dB:d=0.8 -vf blackdetect=d=0.3 -f null - 2>&1 | grep -E "silence_|black_" || echo "khamoshi/kaali screen nahi mili"
rm -f ck_*; ffmpeg -v error -y -i MKGaming_1_Game_Band_Player_Chalu.mp4 -vf "fps=4,scale=216:384,tile=8x4:padding=6:color=white" ck_%d.jpg; ls ck_*
