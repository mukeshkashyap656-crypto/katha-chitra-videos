import sys, math; sys.argv=['x']; sys.path.insert(0,'/home/claude/lak')
import cairo
import render as R, scenes as S
from chars import person, hexc, fill_stroke, ellipse
W,H=1080,1920
s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s)
# background: night fort sky full canvas
c.save(); c.scale(W/S.SW, H/S.SH*0.82); S.bg_fort(c, 1.0, night=False); c.restore()
c.rectangle(0,0,W,H); c.set_source_rgba(0.35,0.04,0.06,0.45); c.fill()
# Rani big, centered, inside 3:4 safe zone (y 240..1680)
c.save(); c.rectangle(0,0,W,H); c.clip()
person(c,"rani_w",540,3190,2700,arms=(0.12,0.05,-0.12,-0.05),mouth="B",emo="angry")
c.restore()
# border
c.set_source_rgb(*hexc("#e8b730")); c.set_line_width(10); c.rectangle(18,18,W-36,H-36); c.stroke()
c.set_line_width(4); c.rectangle(34,34,W-68,H-68); c.stroke()
# top band text (inside safe zone)
def band(y,h,alpha=0.9):
    c.rectangle(60,y,W-120,h); c.set_source_rgba(*hexc("#3a0a10"),alpha); c.fill_preserve()
    c.set_source_rgb(*hexc("#e8b730")); c.set_line_width(5); c.stroke()
t1=R.text_surface("झाँसी की रानी",92,(255,214,90),maxw=900,shadow=(40,8,5))
t2=R.text_surface("भाग 1",48,(255,244,220),maxw=400)
band(270,230)
c.set_source_surface(t1,W/2-t1.get_width()/2,280); c.paint()
c.set_source_surface(t2,W/2-t2.get_width()/2,420); c.paint()
q=R.text_surface("“मैं अपनी झाँसी नहीं दूँगी!”",76,(255,244,220),maxw=920,shadow=(20,4,2))
band(1390,270)
c.set_source_surface(q,W/2-q.get_width()/2,1410); c.paint()
y2=R.text_surface("1854 • सच्ची कहानी",44,(255,214,90),maxw=700)
c.set_source_surface(y2,W/2-y2.get_width()/2,1555); c.paint()
s.write_to_png('/home/claude/lak/cover_lakshmibai_bhag1.png')
