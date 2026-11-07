#!/usr/bin/env python3
"""Nobody Owns Tomorrow — director revision V3, zero paid video inference.

Director-locked music event cues (v3): remove all editorial scene markers;
no karaoke gap cutaways; special second-half post-chorus camera orbits;
dream->bedroom->toy loop; half-bridge pictograms and half-bridge child;
first deliberate hard cut on final chorus downbeat; kid joins final rave;
final exit to dancing sprites in bedroom, lit city windows, other dreamers.
Timing aligns to user direction and model-derived Suno data, not ear-certified.
"""
import argparse, json, math, sys, random, subprocess
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
import nobody_dream_rave_v2_renderer as v2
base=v2.base
W,H=base.W,base.H
DURATION=base.DURATION
ROOT=Path(__import__('os').environ.get('NOBODY_MEDIA_ROOT', '/mnt/data'))
OUT=ROOT/'nobody_v3_work'
OUT.mkdir(exist_ok=True)

# A visual tone, not an annotation: no overlays or editorial scene titles.
def crop_camera(im,cx,cy,zoom=1.0):
    zoom=max(1.,min(4.7,zoom))
    cw=max(48,round(W/zoom));ch=max(32,round(H/zoom))
    l=max(0,min(W-cw,round(cx-cw/2)));top=max(0,min(H-ch,round(cy-ch/2)))
    return im.crop((l,top,l+cw,top+ch)).resize((W,H),Image.Resampling.BICUBIC)

def mix(a,b,u):return a*(1-u)+b*u

def window_ease(t,a,b):return base.smooth((t-a)/max(.01,b-a))

@lru_cache(maxsize=100)
def chorus_ambient():
    # An abstract constellation NOT the city pictogram; the same physical
    # holes gently breathe in lyric rests rather than switching scenes.
    im=Image.new('RGBA',(W,H),(0,0,0,0))
    d=ImageDraw.Draw(im,'RGBA')
    r=random.Random(301)
    for k in range(46):
        x,y=r.randrange(56),r.randrange(13)
        if 15<x<41 and 2<y<11:continue
        px=148+x*12;py=125+y*20
        col=base.PALETTE[k%len(base.PALETTE)]
        d.ellipse((px-3,py-3,px+3,py+3),fill=(*col,62))
    return im


def draw_peg(d,x,y,color,r=3.2,alpha=225):
    px=148+x*12;py=125+y*20
    if not(140<=px<=825 and 118<=py<=376):return
    d.ellipse((px-r*2,py-r*2,px+r*2,py+r*2),fill=(*color,int(alpha*.18)))
    d.ellipse((px-r,py-r,px+r,py+r),fill=(*color,alpha))


def chorus_front(t):
    """Words are physical pegs; a musical rest is a held lighting state.

    No condition ever substitutes 'pictogram(city)' between chorus words.
    """
    im=base.CLOSE.copy()
    w=base.live_word(t)
    if w:
        im=base.faded_word(im,t,'front')
        token=w['text'].lower().strip(' ,!.')
    else:
        token=''
        # Dark rest is intentional, no city-flash substitute.
        glow=chorus_ambient()
        a=.34+.17*math.sin(t*1.9)**2
        im=Image.alpha_composite(im.convert('RGBA'),Image.blend(Image.new('RGBA',(W,H)),glow,a)).convert('RGB')
    d=ImageDraw.Draw(im,'RGBA')
    beat=base.energy(t)
    # Small diegetic accents. Show lyric-specific symbols BESIDE text, never
    # overprint it; animation is synchronized by the sung word's interval.
    if token:
        pulse=1.0
        u=window_ease(t,w['start'],max(w['start']+.12,w['end']))
        if token in {'tomorrow','morning'}:
            for j in range(15):
                y=11-round(6*u*math.sin(j*math.pi/14))
                draw_peg(d,2+j,y,base.PALETTE[2],2.4,170)
        elif token in {'sky','world'}:
            for j in range(10):
                x=2+round(u*34)-j;y=1+round((j*.18)%3)
                draw_peg(d,x,y,base.PALETTE[0],2.8,200-j*11)
        elif token in {'lights','light','alive'}:
            for j in range(12):
                x=3+(j*17)%50;y=1+(j*11)%12
                if j/12<=u:draw_peg(d,x,y,base.PALETTE[j%5],3,210)
        elif token in {'reason','everyone'}:
            for j in range(7):
                y=3+j;draw_peg(d,4,y,base.PALETTE[4],2.6,100+int(70*u))
        elif token in {'other','side'}:
            for j in range(8):
                draw_peg(d,48+j%7,2+j,base.PALETTE[1],2.8,190)
    # Light-sensitive dial reacts but never becomes a floating overlay.
    d.ellipse((834,389,849,403),fill=(min(255,int(110+90*beat)),100,158,235))
    return im

BRIDGE_ICONS={42:'fall',43:'fly',44:'question',45:'question',46:'call'}

def bridge_illustration(t):
    idx,line=v2.active_line(t)
    if idx not in BRIDGE_ICONS:return v2.pictogram(t)
    name=BRIDGE_ICONS[idx]
    im=base.CLOSE.copy();d=ImageDraw.Draw(im,'RGBA')
    u=window_ease(t,line['start'],line['end'])
    if name=='fall':
        # A constellation descending rather than full-screen lyric text.
        for i in range(19):
            x=7+i*2.25;y=3+u*8+2*math.sin(i*.5+t*.6)
            draw_peg(d,x,y,base.PALETTE[0 if i%3 else 2],3.2,200)
    elif name=='fly':
        for k in range(3):
            x=9+k*17;y=10-7*u
            draw_peg(d,x,y,base.PALETTE[(k+3)%5],4,233)
            for j in range(5):draw_peg(d,x-3+j,y+1+abs(2-j),base.PALETTE[3],2.6,160)
    elif name=='question':
        for j in range(14):
            x=27+round(10*math.sin((j/13)*math.pi)); y=round(1+j*.55)
            draw_peg(d,x,y,base.PALETTE[2],3,250)
        draw_peg(d,27,11,base.PALETTE[2],4,250)
        for k in range(14):
            x=(5+k*5)%56;y=2+int(4*(.5+.5*math.sin(t*1.7+k)))
            draw_peg(d,x,y,base.PALETTE[4],2.2,180)
    else:
        for j in range(21):
            x=7+j*2;y=6+4*math.sin(j*.55-t*2.0)
            draw_peg(d,x,y,base.PALETTE[j%5],3.1,230)
    return im

# Improve the PCB micro-world with spatial motion. The rear peg lattice stays
# rooted to the physical toy; the translucent foreground sprites move at a
# different apparent depth during the electronic-trill post-choruses.
DANCERS=[]
rnd=random.Random(20261107)
for i in range(34):
    x=rnd.uniform(242,724);y=rnd.uniform(377,455)
    DANCERS.append((x,y,i%5,rnd.random()*math.tau,rnd.randint(13,26),rnd.uniform(.65,1.4)))


def tiny_person(d,x,y,color,phase,height=22,scale=1.0):
    # Small recognizable dance poses; two independent arms + legs.
    r=height*.26*scale; torso=height*.85*scale
    x,y=float(x),float(y)
    ya=y-torso
    limb=math.sin(phase)
    d.ellipse((x-r,ya-r*2,x+r,ya),fill=(*color,245))
    d.line((x,ya+1,x,y),fill=(*color,240),width=max(2,round(3.0*scale)))
    d.line((x,ya+torso*.25,x-9*scale,y-torso*.7+8*limb*scale),fill=(*color,235),width=max(2,round(2.8*scale)))
    d.line((x,ya+torso*.25,x+10*scale,y-torso*.7-7*limb*scale),fill=(*color,235),width=max(2,round(2.8*scale)))
    d.line((x,y,x-7*scale,y+9*scale+3*limb*scale),fill=(*color,235),width=max(2,round(2.6*scale)))
    d.line((x,y,x+7*scale,y+10*scale-3*limb*scale),fill=(*color,235),width=max(2,round(2.6*scale)))


def dreaming_boy_at_rave(d,t):
    """Same identifying silhouette as the bedroom child; dream-scale puppet."""
    u=window_ease(t,209.8,211.2)
    if u<=0:return
    x=474+50*math.sin((t-209.8)*.39)
    y=429+7*math.sin(t*5.1)
    s=.7+.3*u
    h=96*s
    # Teal PJs; dark tousled hair, left curl, warm face, freckles.
    d.ellipse((x-33*s,y-h*.62,x+34*s,y-h*.15),fill=(28,143,166,int(255*u)))
    d.polygon([(x-20*s,y-27*s),(x+20*s,y-27*s),(x+29*s,y+16*s),(x-28*s,y+16*s)],fill=(29,151,170,int(255*u)))
    d.line((x-12*s,y+7*s,x-21*s,y+30*s),fill=(31,139,162,int(255*u)),width=max(4,int(10*s)))
    d.line((x+12*s,y+7*s,x+21*s,y+30*s),fill=(31,139,162,int(255*u)),width=max(4,int(10*s)))
    dance=math.sin(t*5.0)
    d.line((x-27*s,y-45*s,x-49*s,y-69*s+21*dance*s),fill=(42,169,180,int(255*u)),width=max(4,int(10*s)))
    d.line((x+27*s,y-44*s,x+51*s,y-71*s-16*dance*s),fill=(42,169,180,int(255*u)),width=max(4,int(10*s)))
    d.ellipse((x-37*s,y-h-25*s,x+36*s,y-h+42*s),fill=(225,157,126,int(255*u)))
    d.pieslice((x-40*s,y-h-28*s,x+36*s,y-h+28*s),175,350,fill=(37,31,47,int(255*u)))
    d.polygon([(x-38*s,y-h+5*s),(x-58*s,y-h-17*s),(x-43*s,y-h-30*s),(x-16*s,y-h-24*s)],fill=(37,31,47,int(255*u)))
    for dx in (-13,14):d.ellipse((x+dx*s-2,y-h+17*s,x+dx*s+2,y-h+20*s),fill=(42,35,53,int(255*u)))
    d.arc((x-10*s,y-h+23*s,x+11*s,y-h+34*s),0,160,fill=(134,64,76,int(255*u)),width=2)
    for dx in (16,22):d.ellipse((x+dx*s,y-h+25*s,x+dx*s+2,y-h+27*s),fill=(147,83,79,int(255*u)))


def camera_move_for_rave(t):
    # Three second-half electronic trills are the flying-camera passages.
    segments=[(83.195,92.785),(160.968,170.991),(219.0,225.8)]
    for a,b in segments:
        if a<=t<b:
            u=(t-a)/(b-a)
            # Dolly forward; sail to the left DJ then around right-side dancers.
            z=1.03+.55*math.sin(math.pi*u)**.75
            cx=480+170*math.sin(math.tau*(u-.18))
            cy=290+46*math.sin(math.tau*(u+.15))
            return z,cx,cy,1.0
    return 1.01+0.02*math.sin(t*.39),480+18*math.sin(t*.31),270+11*math.sin(t*.22),0.


def inside_world(t,include_kid=False):
    z,cx,cy,fly=camera_move_for_rave(t)
    im=v2.INSIDE.copy()
    d=ImageDraw.Draw(im,'RGBA')
    energy=base.energy(t)
    # Solder contacts animate in place; their stable 56 x 13 spacing is a
    # constant visual reference while the camera travels through the board.
    for k in range(26):
        x=99+k*29;y=284-(8+29*energy)*(.45+.55*math.sin(t*3.4+k)**2)
        col=base.PALETTE[k%5]
        d.ellipse((x-3,y-3,x+3,y+3),fill=(*col,195))
    for j in range(20):
        x=95+j*38;y=70+20*math.sin(j*.8+t*.6)
        col=base.PALETTE[j%5]
        if (t*1.3+j)%4<2.3:d.ellipse((x,y,x+4,y+4),fill=(*col,185))
    # Back dancers move along dance-floor lanes and weave around components.
    for i,(x,y,ci,phase,h,depth) in enumerate(DANCERS):
        ox=24*math.sin((t-74)*(.33+.018*(i%9))+phase) + 13*math.sin(t*.94+phase)
        oy=9*math.sin((t-74)*(.27+.022*(i%6))+phase*2)
        yy=y+oy
        col=base.PALETTE[ci]
        tiny_person(d,x+ox,yy,col,t*4.2+phase,h,scale=.73+.25*depth)
    if include_kid:dreaming_boy_at_rave(d,t)
    im=crop_camera(im,cx,cy,z)
    # At camera's near depth, hanging light-pegs parallax more strongly than
    # the PCB, suggesting the lens is weaving BETWEEN foreground components.
    d=ImageDraw.Draw(im,'RGBA')
    if fly:
        for i in range(9):
            phase=i*2.6
            xx=(i*137+140+115*math.sin(t*.62+phase))%1000-20
            yy=95+(i*73)%400+27*math.sin(t*.91+phase)
            r=3+3.0*(.5+.5*math.sin(phase+t*.4))
            col=base.PALETTE[i%5]
            d.ellipse((xx-r*3,yy-r*3,xx+r*3,yy+r*3),fill=(*col,42))
            d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=(*col,150))
    return im


def portrait_view(t,plate=None,zoom=1,center=(422,335)):
    if plate is None:plate=base.ROOM_B
    im=crop_camera(plate,center[0],center[1],zoom)
    # Light motes are physically reflected on the boy's bedding, not text.
    d=ImageDraw.Draw(im,'RGBA')
    e=base.energy(t)
    if zoom>=1.3:
        for i in range(13):
            x=(int((i*94+20+26*math.sin(t*.51+i))%W));y=(i*41+90)%H
            if (x-520)**2+(y-300)**2<10000:continue
            c=base.PALETTE[i%5]
            rr=2+3*e
            d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(*c,70))
    return im


def dream_to_room_loop(t):
    if t<93.55:
        a=inside_world(t)
        b=portrait_view(t,zoom=3.9)
        u=window_ease(t,92.785,93.55)
        return Image.blend(a,b,u)
    if t<98.0:
        u=window_ease(t,93.55,98.0)
        return portrait_view(t,zoom=mix(3.9,1.0,u),center=(mix(422,480,u),mix(338,270,u)))
    return v2.exact_room_push(t,98.0,102.903)


def reverse_portal_to_toy(t,start=170.991,end=172.65):
    # Back through a contact aperture and emerge on the physical front.
    u=window_ease(t,start,end)
    target=bridge_illustration(t)
    if u<.42:
        return Image.blend(inside_world(t),crop_camera(target,577,242,3.8),base.smooth(u/.42))
    z=mix(3.8,1.0,base.smooth((u-.42)/.58))
    return crop_camera(target,577,242,z)


def bridge_to_boy(t):
    # First pulls away from toy, then approaches sleeping child. Shared room plate.
    if t<184.0:
        u=window_ease(t,180.0,184.0)
        # Reverse the known room-to-close crop; resolve from high-res macro plate.
        l,topy,cw,ch=v2.ROOM_TO_CLOSE
        z=u
        x=mix(l,0,z);y=mix(topy,0,z);w=mix(cw,960,z);h=mix(ch,540,z)
        room=base.ROOM_B.crop((round(x),round(y),round(x+w),round(y+h))).resize((W,H),Image.Resampling.BICUBIC)
        a=1-base.smooth(u/.18)
        return Image.blend(room,bridge_illustration(t),a) if a>.01 else room
    if t<189.5:
        u=window_ease(t,184.0,189.5)
        return portrait_view(t,zoom=mix(1,1.85,u),center=(mix(480,422,u),mix(270,334,u)))
    # A little boy wakes when the drum arrives; facial eye change is local.
    u=window_ease(t,189.5,190.147)
    asleep=portrait_view(t,zoom=1.85,center=(422,334))
    awake=portrait_view(t,plate=base.ROOM_A,zoom=1.85,center=(422,334))
    return Image.blend(asleep,awake,u)


def room_sprites(im,t,brightness=1):
    d=ImageDraw.Draw(im,'RGBA')
    e=base.energy(t)
    for i in range(20):
        phase=i*2.3
        x=170+(i*67)%660+18*math.sin(t*.73+phase)
        y=305+(i*41)%145+8*math.sin(t*2.2+phase)
        c=base.PALETTE[i%5]
        a=int(235*brightness)
        if a<10:continue
        # Particles have bright halos but remain tiny toy-like characters.
        d.ellipse((x-8,y-21,x+8,y-5),fill=(*c,int(a*.08)))
        tiny_person(d,x,y,c,t*4.2+phase,9,scale=.50)
    return im


def city_window_room(t):
    im=base.ROOM_A.copy()
    d=ImageDraw.Draw(im,'RGBA')
    q=window_ease(t,239,248)
    # Existing 7 buildings outside real bedroom window begin displaying
    # Night-Brite colors, connecting the single child's dream to the city.
    for i in range(7):
        bx=105+i*31
        # Reuse the silhouette layout already visible through the glass.
        for j in range(4):
            y=204+j*16
            col=base.PALETTE[(i+j)%5]
            amt=window_ease(t,239+(i*4+j)*.42,243+(i*4+j)*.42)
            if amt>0:
                r=2.2+1.1*math.sin(t*2+i+j)**2
                # Glow BEHIND a fully bright window; drawing the halo last
                # previously dimmed the colorful windows into near-invisibility.
                d.ellipse((bx+1-r,y-3-r,bx+16+r,y+10+r),fill=(*col,int(50*amt*q)))
                d.rectangle((bx+5,y-2,bx+13,y+7),fill=(*col,int(252*amt*q)))
                d.line((bx+6,y,bx+12,y),fill=(250,251,245,int(205*amt*q)),width=2)
    return room_sprites(im,t,brightness=.9)


def last_exit_to_room(t):
    a=inside_world(t,include_kid=True)
    b=portrait_view(t,plate=base.ROOM_A,zoom=mix(3.7,1.5,window_ease(t,225.8,229)),center=(422,334))
    u=window_ease(t,225.8,227.6)
    if u<.99:return Image.blend(a,b,u)
    # The dream opens into child's room, spirits gradually materialize there.
    return room_sprites(b,t,brightness=window_ease(t,227,229))


def window_to_city(t):
    room=city_window_room(t)
    u=window_ease(t,248,252.2)
    im=crop_camera(room,mix(480,203,u),mix(270,172,u),mix(1,3.0,u))
    return im

# End-city: reverse-side zoom through bedroom glass into other apartments.
# Children are different tiny silhouettes, each with their own peg toy.
def outside_plate(t):
    im=base.backdrop((10,20,48),(37,25,68));d=ImageDraw.Draw(im,'RGBA')
    # Three distinct apartment buildings; silhouettes anchored in one geometry.
    for k,(x,y,w,h,shade) in enumerate([(35,155,277,395,(25,34,66)),(345,88,300,463,(27,37,73)),(682,142,259,401,(28,33,59))]):
        d.rectangle((x,y,x+w,540),fill=(*shade,255))
        d.rectangle((x,y,x+w,y+9),fill=(80,79,100,255))
        dx=56;dy=66
        for row in range(0,5):
            for col in range(0,4):
                wx=x+18+col*dx;wy=y+24+row*dy
                if wx+37>x+w or wy+46>530:continue
                c=base.PALETTE[(k*2+row+col)%5]
                active=(row+2*col+k)%3!=1
                if active:
                    d.rounded_rectangle((wx,wy,wx+38,wy+46),radius=3,fill=(32,35,72,255),outline=(*c,225),width=2)
                    # Tiny sleeping child silhouette, toy has several lit pegs.
                    d.ellipse((wx+9,wy+22,wx+21,wy+34),fill=(177,113,100,230))
                    d.arc((wx+11,wy+19,wx+24,wy+27),155,330,fill=(39,34,55,250),width=3)
                    d.line((wx+9,wy+35,wx+29,wy+35),fill=(85,98,149,255),width=4)
                    for q in range(4):
                        c2=base.PALETTE[(q+row)%5]
                        d.ellipse((wx+27+3*(q%2),wy+22+5*(q//2),wx+29+3*(q%2),wy+24+5*(q//2)),fill=(*c2,240))
                else:
                    d.rectangle((wx,wy,wx+38,wy+46),fill=(11,23,51,255),outline=(54,58,97,255),width=2)
    for j in range(26):
        sx=(j*149+37)%960;sy=(j*47+15)%133
        d.ellipse((sx,sy,sx+2,sy+2),fill=(165,173,220,140))
    return im


def other_dreamers(t):
    u=window_ease(t,252.2,255.0)
    # At the start the physical bedroom's window fills screen and crossfades
    # into the geographically consistent neighboring city vista.
    near=window_to_city(252.2)
    city=outside_plate(t)
    if u<1:city=Image.blend(near,city,u)
    # One smooth push to the apartment across the street; end with another
    # child dreaming beside a glowing board, not a logo or explanatory title.
    z=mix(1,2.38,window_ease(t,255,263.24))
    cx=mix(480,532,window_ease(t,255,263.24))
    cy=mix(270,265,window_ease(t,255,263.24))
    return crop_camera(city,cx,cy,z)

SHOTS=[
 ('00','00:00','0:15','bedtime',0,15,'Child at bedtime; established room, gentle light'),
 ('01','0:15','0:25.09','push',15,25.09,'Physical camera discovers same toy; no discontinuity'),
 ('02','0:25.09','0:54.25','verse_icons',25.09,54.25,'Verse one pictograms on Night-Brite'),
 ('03','0:54.25','1:11.61','chorus',54.25,71.614,'Karaoke words; gaps retain board, never city cutaway'),
 ('04','1:11.61','1:13.27','portal',71.614,73.274,'First ON THE OTHER SIDE becomes doorway'),
 ('05','1:13.27','1:23.20','rave_wide',73.274,83.195,'Tour of actual toy-circuit party'),
 ('06','1:23.20','1:32.78','rave_fly',83.195,92.785,'Electronic trill: dolly/orbit, animated dancers'),
 ('07','1:32.78','1:38','dream_out',92.785,98.0,'Finish reprise; emerge from boy dream, pull back to bedroom'),
 ('08','1:38','1:42.90','room_push',98.0,102.903,'Continue into Night-Brite for verse two'),
 ('09','1:42.90','2:12.02','verse_icons',102.903,132.02,'Verse two illustrated with diegetic lights'),
 ('10','2:12.02','2:29.37','chorus',132.02,149.374,'Chorus karaoke; stable scene through vocal gaps'),
 ('11','2:29.37','2:31.09','portal',149.374,151.094,'Enter second circuit-board party'),
 ('12','2:31.09','2:40.97','rave_wide',151.094,160.968,'Second cute miniature disco'),
 ('13','2:40.97','2:50.99','rave_fly',160.968,170.991,'Second trill: sweeping moving camera'),
 ('14','2:50.99','2:52.65','exit_to_front',170.991,172.65,'Zoop back to front of board, not boy'),
 ('15','2:52.65','3:00','bridge_icons',172.65,180.0,'First half bridge: animatable pictograms'),
 ('16','3:00','3:09.5','bridge_boy',180.0,189.5,'Back away from board into boy dream'),
 ('17','3:09.5','3:10.147','eyes_open',189.5,190.147,'Child opens eyes on drum pickup'),
 ('18','3:10.147','3:27.79','chorus',190.147,207.788,'First intentional hard cut to final karaoke chorus'),
 ('19','3:27.79','3:29.80','portal',207.788,209.797,'Final ON THE OTHER SIDE; child enters dream party'),
 ('20','3:29.80','3:39','rave_kid',209.797,219.0,'Boy dances among the tiny peg sprites'),
 ('21','3:39','3:45.8','rave_fly_kid',219.0,225.8,'Third trill: traveling lens around dancing child'),
 ('22','3:45.8','3:49','kid_to_room',225.8,229.0,'Float out of dreaming boy to his bedroom'),
 ('23','3:49','3:59','room_sprite_party',229.0,239.0,'All the tiny sprites are dancing in his room'),
 ('24','3:59','4:08','windows',239.0,248.0,'City windows start glowing Night-Brite colors'),
 ('25','4:08','4:12.20','window_push',248.0,252.2,'Camera heads toward bedroom window'),
 ('26','4:12.20','4:23.24','other_dreamers',252.2,DURATION,'Other children dreaming with their own lightboards')]


def scene_at(t):
    for rec in SHOTS:
        if rec[4]<=t<rec[5]:return rec
    return SHOTS[-1]


def frame(t):
    key=scene_at(t)[3]
    if key=='bedtime':im=Image.blend(base.ROOM_A,base.ROOM_B,window_ease(t,6.5,7.5))
    elif key=='push':im=v2.exact_room_push(t,15,25.09)
    elif key=='verse_icons':im=v2.pictogram(t)
    elif key=='bridge_icons':im=bridge_illustration(t)
    elif key=='chorus':im=chorus_front(t)
    elif key=='portal':
        if t<100:im=v2.portal(t,71.614,73.274)
        elif t<170:im=v2.portal(t,149.374,151.094)
        else:im=v2.portal(t,207.788,209.797)
    elif key in ('rave_wide','rave_fly'):im=inside_world(t)
    elif key in ('rave_kid','rave_fly_kid'):im=inside_world(t,include_kid=True)
    elif key=='dream_out' or key=='room_push':im=dream_to_room_loop(t)
    elif key=='exit_to_front':im=reverse_portal_to_toy(t)
    elif key in ('bridge_boy','eyes_open'):im=bridge_to_boy(t)
    elif key=='kid_to_room':im=last_exit_to_room(t)
    elif key=='room_sprite_party':im=room_sprites(base.ROOM_A.copy(),t)
    elif key=='windows':im=city_window_room(t)
    elif key=='window_push':im=window_to_city(t)
    elif key=='other_dreamers':im=other_dreamers(t)
    else:raise ValueError(key)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,9),fill=(5,7,18));d.rectangle((0,H-10,W,H),fill=(5,7,18))
    return im

base.frame=frame

def make_contact_sheet():
    picks=[(4,'BEDTIME'),(25.1,'PEGBOARD'),(56.8,'CHORUS KARAOKE'),(82.7,'MINI DISCO'),
       (86.5,'TRILL CAMERA'),(94.0,'DREAM OUT'),(99.6,'ZOOM TO TOY'),(142,'CHORUS 2'),
       (164,'2ND CAMERA MOVE'),(176,'BRIDGE PICTOGRAM'),(186,'BRIDGE / CHILD'),
       (189.7,'EYES OPEN'),(194,'FINAL CHORUS'),(212,'CHILD AT RAVE'),
       (222,'FINAL TRILL'),(232,'SPRITES IN ROOM'),(244,'CITY WINDOWS'),(260,'OTHER DREAMERS')]
    cw,ch=320,180;pad=16;label=34
    board=Image.new('RGB',(3*(cw+pad)+pad,6*(ch+label+pad)+pad),(14,18,34))
    d=ImageDraw.Draw(board)
    for i,(t,label_text) in enumerate(picks):
        pic=frame(t).resize((cw,ch),Image.Resampling.LANCZOS)
        x=pad+(i%3)*(cw+pad);y=pad+(i//3)*(ch+label+pad)
        board.paste(pic,(x,y));d.text((x+2,y+ch+6),f'{int(t//60):02}:{t%60:05.2f}  {label_text}',font=base.ff(13,True),fill=(227,232,246))
    path=OUT/'Nobody_V3_Storyboard.png';board.save(path,optimize=True);return path


def build_manifest():
    v={'title':'Nobody Owns Tomorrow — music-directed V3','duration_s':DURATION,
       'direction_version':'v3-2026-11-07',
       'timing_provenance':'Suno word alignment, musical beats and user-directed cue corrections; word alignment has not been independently checked by ear',
       'first_intentional_hard_cut_at_s':190.147,
       'no_diegetic_editorial_markers':True,
       'vocal_gaps_in_chorus_hold_same_board':True,
       'postchorus_fly_camera_starts_s':[83.195,160.968,219.0],
       'source_audio':'Nobody Owns Tomorrow(1).wav',
       'shots':[dict(id=i,display_start=b,display_end=c,scene=kind,start_s=t0,end_s=t1,direction=idea) for i,b,c,kind,t0,t1,idea in SHOTS]}
    p=OUT/'Nobody_V3_Directors_Cues.json';p.write_text(json.dumps(v,indent=2));return p


def render(out,start,duration,fps=12,size='full',crf=30):
    srcw,srch=(960,540) if size=='full' else (640,360)
    frames=math.ceil(duration*fps)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{srcw}x{srch}','-framerate',str(fps),'-i','pipe:0',
         '-ss',f'{start:.3f}','-i',str(base.AUDIO),'-map','0:v:0','-map','1:a:0',
         '-c:v','libx264','-preset','veryfast','-crf',str(crf),'-pix_fmt','yuv420p','-c:a','aac','-b:a','96k' if size!='full' else '160k',
         '-t',f'{duration:.3f}','-shortest','-movflags','+faststart',str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for j in range(frames):
        t=min(DURATION-.001,start+j/fps)
        img=frame(t)
        if size!='full':img=img.resize((srcw,srch),Image.Resampling.BICUBIC)
        try:proc.stdin.write(img.tobytes())
        except BrokenPipeError:break
        if (j+1)%250==0:print('frames',j+1,'/',frames,'at',round(t,2),flush=True)
    try:proc.stdin.close()
    except OSError:pass
    rv=proc.wait()
    if rv:raise RuntimeError(f'FFmpeg exited {rv}')
    return out

if __name__=='__main__':
    pa=argparse.ArgumentParser()
    pa.add_argument('--start',type=float,default=0)
    pa.add_argument('--duration',type=float,default=DURATION)
    pa.add_argument('--fps',type=int,default=12)
    pa.add_argument('--lite',action='store_true')
    pa.add_argument('--crf',type=int,default=32)
    pa.add_argument('--stills-only',action='store_true')
    args=pa.parse_args()
    if args.start==0:
        print('Storyboard',make_contact_sheet(),flush=True)
        print('Cues',build_manifest(),flush=True)
    if args.stills_only:sys.exit(0)
    duration=min(args.duration,DURATION-args.start)
    outfile=OUT/('Nobody_V3_LITE_Full_Song.mp4' if args.lite and args.start==0 and duration==DURATION else 'Nobody_V3_Cinematic_Animatic.mp4' if args.start==0 and duration==DURATION else f'Nobody_V3_Preview_{args.start:.0f}s_{duration:.0f}s.mp4')
    print('Render',outfile,'frames',math.ceil(duration*args.fps),flush=True)
    render(outfile,args.start,duration,args.fps,size='lite' if args.lite else 'full',crf=args.crf)
    print('Done',outfile,outfile.stat().st_size,flush=True)
