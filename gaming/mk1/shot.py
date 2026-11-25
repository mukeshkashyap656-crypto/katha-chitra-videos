import sys, json, subprocess
from playwright.sync_api import sync_playwright
meta=json.load(open('/tmp/mk/meta.json'))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///tmp/mk/page.html'); pg.evaluate('document.fonts.ready'); pg.evaluate('frame(0)'); pg.wait_for_timeout(500)
    if sys.argv[1]=='stills':
        for k,(i,s,d) in enumerate(meta['scenes']):
            pg.evaluate(f'frame({s+d*float(sys.argv[2])})'); pg.screenshot(path=f'/tmp/mk/st_{k+1:02d}.png')
    else:
        a,z,out=int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
        f=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate','30','-i','-','-c:v','libx264','-crf','19','-preset','veryfast','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        for i in range(a,z):
            pg.evaluate(f'frame({i/30})'); f.stdin.write(pg.screenshot(type='jpeg',quality=92))
        f.stdin.close(); assert f.wait()==0
    print('galti:',errs[:3]); b.close()
