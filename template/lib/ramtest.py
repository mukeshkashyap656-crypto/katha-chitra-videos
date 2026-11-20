import sys, math; sys.argv=['x']; sys.path.insert(0,'/home/claude/lak')
import cairo
from chars import person, hexc, fill_stroke, ellipse, poly, OL
import scenes as S
import render as R
from PIL import Image
W,H=1080,1920
SX,SY,SW,SH=40,230,1000,1220

def bunting(c,y):
    c.rectangle(0,0,SW,y); c.set_source_rgb(*hexc("#7a1424")); c.fill()
    for k in range(17):
        poly(c,[(k*62,y),(k*62+62,y),(k*62+31,y+50)]); fill_stroke(c,"#2f8a4a" if k%2==0 else "#f08a24",3)
def garland(c,x0,x1,y,sag):
    n=int((x1-x0)/30)
    for k in range(n+1):
        t=k/n; xx=x0+(x1-x0)*t; yy=y+sag*4*t*(1-t)
        c.arc(xx,yy,13,0,6.3); fill_stroke(c,"#f7c53f" if k%2 else "#f2a23a",2.5)
    for t in (0.0,1.0):
        xx=x0+(x1-x0)*t
        for j in range(4):
            c.arc(xx,y+18+j*24,10,0,6.3); fill_stroke(c,"#f2a23a" if j%2 else "#d9342b",2.5)
def dotted_wall(c,y0,y1):
    c.rectangle(0,y0,SW,y1-y0); c.set_source(S.grad(c,y0,y1,"#fbe3a8","#f5c873")); c.fill()
    c.set_source_rgba(*hexc("#e0a040"),0.6)
    for yy in range(int(y0)+20,int(y1),40):
        for xx in range(10+(yy//40%2)*20,SW,40):
            c.arc(xx,yy,3,0,6.3); c.fill()
def river(c,y0,y1):
    c.rectangle(0,y0,SW,y1-y0); c.set_source_rgb(*hexc("#4aa3d8")); c.fill()
    c.set_source_rgb(1,1,1); c.set_line_width(3)
    for r_,yy in enumerate(range(int(y0)+18,int(y1),26)):
        for xx in range(-20+(r_%2)*22,SW,44):
            c.arc(xx,yy,20,math.pi,2*math.pi); c.stroke()
    for xx in range(0,SW,90):
        ellipse(c,xx+40,y0,60,34); fill_stroke(c,"#3f8a3a",3)
def diamond_pillar(c,x,y0,y1,w=56):
    c.rectangle(x-w/2,y0,w,y1-y0); fill_stroke(c,"#8e1b2b",4)
    c.set_source_rgb(*hexc("#f7c53f"))
    for yy in range(int(y0)+30,int(y1)-20,44):
        poly(c,[(x,yy-14),(x+11,yy),(x,yy+14),(x-11,yy)]); c.fill()
    for yy in (y0-14,y1-6):
        c.rectangle(x-w/2-10,yy,w+20,22); fill_stroke(c,"#f2c230",4)
def round_arch(c,x,ytop,w,ybot):
    c.move_to(x-w/2,ybot); c.line_to(x-w/2,ytop+w/2); c.arc(x,ytop+w/2,w/2,math.pi,0); c.line_to(x+w/2,ybot)
    c.set_source_rgb(*hexc("#8e1b2b")); c.set_line_width(14); c.stroke()
def throne(c,x,y):
    c.move_to(x-170,y-60); c.line_to(x-170,y-470); c.curve_to(x-170,y-620,x-40,y-700,x,y-760); c.curve_to(x+40,y-700,x+170,y-620,x+170,y-470); c.line_to(x+170,y-60); c.close_path()
    fill_stroke(c,"#8e1b2b",6)
    c.move_to(x-125,y-60); c.line_to(x-125,y-450); c.curve_to(x-125,y-570,x-30,y-640,x,y-690); c.curve_to(x+30,y-640,x+125,y-570,x+125,y-450); c.line_to(x+125,y-60); c.close_path()
    fill_stroke(c,"#f2c230",4)
    c.set_source_rgb(*hexc("#e0902a"))
    for yy in range(int(y-640),int(y-80),36):
        for xx in range(int(x-110),int(x+115),36):
            c.arc(xx+(yy//36%2)*18,yy,3.5,0,6.3); c.fill()
    c.rectangle(x-195,y-150,390,90); fill_stroke(c,"#d9342b",5)
    c.set_source_rgb(*hexc("#f7c53f"))
    for k in range(8): c.arc(x-175+k*50,y-105,8,0,6.3); c.fill()
def flag_sun(c,x,y):
    c.move_to(x,y); c.line_to(x,y-760); c.set_source_rgb(*OL); c.set_line_width(14); c.stroke()
    c.move_to(x,y); c.line_to(x,y-760); c.set_source_rgb(*hexc("#c98a4a")); c.set_line_width(8); c.stroke()
    poly(c,[(x,y-820),(x-22,y-760),(x+22,y-760)]); fill_stroke(c,"#d9dde2",4)
    c.rectangle(x+4,y-700,150,190); fill_stroke(c,"#f2c230",4)
    c.arc(x+79,y-605,34,0,6.3); fill_stroke(c,"#d9342b",3)
    c.set_source_rgb(*OL); c.set_line_width(3)
    for k in range(12):
        a=k*math.pi/6; c.move_to(x+79+math.cos(a)*44,y-605+math.sin(a)*44); c.line_to(x+79+math.cos(a)*58,y-605+math.sin(a)*58); c.stroke()
def sleepy_sun(c,x,y,r):
    S.folk_sun(c,x,y,r,0)
def chhatra(c,x,y,w=200):
    c.move_to(x,y); c.line_to(x,y+150); c.set_source_rgb(*OL); c.set_line_width(9); c.stroke()
    c.move_to(x,y); c.line_to(x,y+150); c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(5); c.stroke()
    c.move_to(x-w/2,y+40); c.curve_to(x-w/2,y-30,x+w/2,y-30,x+w/2,y+40); c.close_path(); fill_stroke(c,"#d9342b",5)
    for k in range(9):
        xx=x-w/2+k*w/8; poly(c,[(xx-11,y+40),(xx+11,y+40),(xx,y+62)]); fill_stroke(c,"#f2c230",3)
    c.arc(x,y-22,12,0,6.3); fill_stroke(c,"#f2c230",3)
def rangoli(c,x,y):
    ellipse(c,x,y,190,55); fill_stroke(c,"#fbf0dc",4)
    for k in range(12):
        a=k*math.pi/6
        ellipse(c,x+math.cos(a)*120,y+math.sin(a)*34,26,9); fill_stroke(c,"#d9342b" if k%2 else "#2f8a4a",2)
    ellipse(c,x,y,70,22); fill_stroke(c,"#f2a23a",3); ellipse(c,x,y,30,10); fill_stroke(c,"#d9342b",2)

def scene(c):
    dotted_wall(c,0,SH)
    river(c,640,900)
    for ax in (190,520,850): round_arch(c,ax,190,300,900)
    bunting(c,60)
    garland(c,60,390,150,110); garland(c,400,700,150,110); garland(c,700,990,150,110)
    for px in (355,690): diamond_pillar(c,px,230,900)
    sleepy_sun(c,850,300,52)
    c.rectangle(0,900,SW,SH-900); c.set_source(S.grad(c,900,SH,"#e07a3a","#c8582a")); c.fill()
    c.set_source_rgba(*hexc("#f2c230"),0.5); c.set_line_width(3)
    for k in range(-8,14):
        c.move_to(k*90,900); c.line_to(k*90-220,SH); c.stroke()
    # back dais for the rear row of courtiers (raised, red carpet)
    c.rectangle(0,850,SW,40); fill_stroke(c,"#d9342b",4)
    c.rectangle(0,890,SW,26); fill_stroke(c,"#8e1b2b",4)
    c.set_source_rgb(*hexc("#f2c230"))
    for k in range(25): c.arc(20+k*40,870,5,0,6.3); c.fill()
    # raised throne with steps and royal umbrella
    for k,(w_,y_) in enumerate(((330,880),(280,850))):
        c.rectangle(500-w_/2,y_,w_,32); fill_stroke(c,"#f2c230" if k else "#8e1b2b",4)
    c.save(); c.translate(500,862); c.scale(0.62,0.62); throne(c,0,0); c.restore()
    chhatra(c,500,330,190)
    HS=440   # same size for everyone
    sitters=[(85,"darbari",870),(245,"mantri2",870),(755,"mantri",870),(915,"darbari2",870),(90,"darbari2",1190),(910,"mantri2",1190)]
    for cx_,who,fy in sitters:
        ellipse(c,cx_,fy,80,17); fill_stroke(c,"#f2a23a",3)
        person(c,who,cx_,fy-4,HS,pose="sit",arms=(-0.15,2.1,0.15,-2.1),emo="sad",look=0.8 if cx_<500 else -0.8)
    # main: Dasharatha (speaking, pleading) and the rishi, centre stage, facing each other
    person(c,"dasharatha",395,1190,HS,arms=(-0.15,2.1,0.15,-2.1),mouth="B",emo="sad",look=0.7)
    person(c,"rishi",605,1185,HS,arms=(-0.15,2.1,0.15,-2.1),emo="stern",look=-0.7)
    S.diya(c,500,1200,1.0)

def frame():
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s)
    c.set_source_rgb(*hexc("#7a1424")); c.paint()
    c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(4); c.rectangle(10,10,W-20,H-20); c.stroke()
    for k in range(0,H,40):
        for x in (22,W-22):
            poly(c,[(x,k),(x+9,k+20),(x,k+40),(x-9,k+20)]); fill_stroke(c,"#f2c230",2)
    for k in range(0,W,40):
        for y in (22,H-22):
            poly(c,[(k,y),(k+20,y-9),(k+40,y),(k+20,y+9)]); fill_stroke(c,"#f2c230",2)
    c.save(); c.translate(SX,SY); c.rectangle(0,0,SW,SH); c.clip(); scene(c); c.restore()
    c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(8); c.rectangle(SX-4,SY-4,SW+8,SH+8); c.stroke()
    # title cartouche
    c.rectangle(250,48,580,150); c.set_source_rgb(*hexc("#5a0c18")); c.fill_preserve(); c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(5); c.stroke()
    c.rectangle(262,60,556,126); c.set_line_width(2); c.stroke()
    t1=R.text_surface("रामायण",70,(255,214,90),maxw=520); t2=R.text_surface("भाग 3 · विश्वामित्र के साथ राम",34,(255,244,220),maxw=540)
    c.set_source_surface(t1,W/2-t1.get_width()/2,46); c.paint(); c.set_source_surface(t2,W/2-t2.get_width()/2,138); c.paint()
    # logo
    Image.open('/home/claude/cmp/logo_crop.png').save('/tmp/logo.png')
    lg=cairo.ImageSurface.create_from_png('/tmp/logo.png')
    c.save(); c.translate(905,250); c.scale(0.62,0.62); c.arc(100,100,98,0,6.3); c.clip(); c.set_source_surface(lg,0,0); c.paint(); c.restore()
    # dialogue panel
    py=SY+SH+30
    c.rectangle(50,py,W-100,H-80-py); c.set_source_rgb(*hexc("#3a0a10")); c.fill_preserve(); c.set_source_rgb(*hexc("#f2c230")); c.set_line_width(5); c.stroke()
    c.rectangle(64,py+14,W-128,H-80-py-28); c.set_line_width(2); c.stroke()
    nm=R.text_surface("महाराज दशरथ",42,(240,190,60),maxw=900)
    tx=R.text_surface("मेरा राम तो अभी सोलह वर्ष का भी नहीं...",50,(255,244,220),maxw=900,lh=1.45)
    c.set_source_surface(nm,W/2-nm.get_width()/2,py+34); c.paint()
    c.set_source_surface(tx,W/2-tx.get_width()/2,py+100); c.paint()
    s.write_to_png('/home/claude/cmp/naya_style_test.png')
if __name__ == "__main__":
    frame()
