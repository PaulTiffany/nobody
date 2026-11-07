#!/usr/bin/env python3
"""Nobody Owns Tomorrow — continuity + semantic pegs revision (2026-11-07).

Local zero-video-inference, deterministic revision of the existing animatic.
Based on nobody_dream_rave_renderer.py; uses same user-owned WAV and Suno
alignment. Word-level *lyrics* appear only in choruses; verses use pictograms.
The first-camera move and the final return resolve to the same physical plate.
This remains an illustrated animatic: timing is model-aligned, not ear-certified.
"""
import argparse, json, math, random, re, sys
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
import nobody_dream_rave_renderer as base

ROOT=Path(__import__('os').environ.get('NOBODY_MEDIA_ROOT', '/mnt/data')); W,H=base.W,base.H
DURATION=base.DURATION

# Make identical toy geometry the source of BOTH room miniature and macro.
# The original miniature had a different aspect ratio and camera trajectory.
base.CLOSE=base.close_plate()
toy=base.CLOSE.crop((69,63,890,421)).convert('RGBA')
mask=Image.new('L',toy.size,0)
ImageDraw.Draw(mask).rounded_rectangle((0,0,toy.width-1,toy.height-1),radius=40,fill=255)
toy.putalpha(mask)
SMALL_TOY=toy.resize((165,72),Image.Resampling.LANCZOS)
# A faint miniature skyline makes the actual bedtime prop visibly alive. It
# is the same toy as the macro, not a second object with different geometry.
_small=ImageDraw.Draw(SMALL_TOY,'RGBA')
for col,hh in enumerate([4,6,3,7,5,8,4,6,3,8,5,4,7,6,4,9,5,4,6,7,3]):
    xx=17+col*6
    for rr in range(hh):
        if (col*13+rr*7)%4!=0:
            yy=61-rr*5
            color=base.PALETTE[(col+rr)%5]
            _small.ellipse((xx-1,yy-1,xx+1.5,yy+1.5),fill=(*color,150))

def same_toy(d,t=0,scale=1):
    d._image.paste(SMALL_TOY,(720,291),SMALL_TOY)

base.lamp_toy=same_toy
base.ROOM_A=base.room_plate(awake=True)
base.ROOM_B=base.room_plate(awake=False)
base.ROOM_OUT=base.room_plate(awake=False,outro=True)
# Remove the original non-diegetic dream title; this is a cinematic insert,
# not a slideshow. Restore the scene's smooth background in its place.
_dream=base.DREAM.copy();_draw=ImageDraw.Draw(_dream)
for _y in range(22,80):
    f=_y/max(1,H-1)
    col=tuple(base.blend(a,b,f) for a,b in zip((31,25,66),(79,52,98)))
    _draw.line((16,_y,615,_y),fill=col,width=1)
base.DREAM=_dream

# Improve physical width-fitting; don't truncate 9-letter words. The original
# dotmap silently discarded trailing letters at 51 columns.
def fit_dotmap(text,maxcols=53):
    text=re.sub('[^A-Z0-9]','',text.upper())
    if not text:return [],0
    # Compact tracking for long words, never remove letters.
    spacing=1 if 6*len(text)-1<=55 else 0
    glyphwidth=5
    full=len(text)*(glyphwidth+spacing)-spacing
    if full>55:
        # Extremely long word: use a four-column condensed face.
        glyphwidth=4;spacing=0;full=len(text)*glyphwidth
    pts=[]
    for i,ch in enumerate(text):
        g=base.GLYPHS.get(ch,base.GLYPHS['O'])
        for y,row in enumerate(g):
            for x in range(glyphwidth):
                source_x=round(x*4/max(1,glyphwidth-1))
                if row[source_x]=='1':pts.append((i*(glyphwidth+spacing)+x,y))
    return pts,full
base.dotmap=fit_dotmap

# Universal camera path from established physical miniature to full-res
# macro. Its final high-res plate is EXACTLY the scene used at the cut.
ROOM_TO_CLOSE=(706.13,278.34,193.0,108.54) # source-space crop

def exact_room_push(t,begin,end,ending=None):
    progress=base.smooth((t-begin)/(end-begin))
    if ending=='outro':
        # Reverse: same camera path, same proportions and screen location.
        z=1-progress
        room=base.ROOM_OUT
    else:
        z=progress
        room=base.ROOM_B
    final_x,final_y,final_w,final_h=ROOM_TO_CLOSE
    l=base.lerp(0,final_x,z);top=base.lerp(0,final_y,z)
    cw=base.lerp(960,final_w,z);ch=base.lerp(540,final_h,z)
    view=room.crop((round(l),round(top),round(l+cw),round(top+ch))).resize((W,H),Image.Resampling.BICUBIC)
    # Resolve the soft upscaled toy to the same high-resolution canonical
    # drawing as the macro. No jump between distinct representations.
    if ending=='outro':
        a=1-base.smooth((progress)/.22)
    else:
        a=base.smooth((z-.77)/.23)
    if a>0:
        view=Image.blend(view,base.CLOSE,min(1,max(0,a)))
    return view

# 56 by 13 real dot locations. Verse illustrations illuminate these same
# physically modeled holes; NO overlay lyric captions in verses or inside rave.
GRID_X,GRID_Y=148,125
STYLE={
 'city':1,'phone':1,'stop':1,'comet':0,'two_people':4,'rain':0,
 'book':2,'heart':4,'switch':1,'key':2,'circuit':0,'door':4,
 'promise':1,'robot':2,'voice':0,'fork':1,'noise':3,'choir':4,
 'music':2,'star':4
}
# Each phrase has a scene image or action. The assignments use the ACTUAL
# line ordering of the aligned recording, not guessed textual conditions.
VERSE_SCENES={
 0:'city',1:'phone',2:'stop',3:'comet',4:'two_people',5:'rain',6:'book',7:'heart',
 8:'switch',9:'key',10:'circuit',11:'door',
 21:'promise',22:'robot',23:'voice',24:'fork',25:'noise',26:'choir',
 27:'music',28:'star',29:'switch',30:'key',31:'circuit',32:'door'
}
LINE_BY_START=sorted([(l['start'],i,l) for i,l in enumerate(base.align['lines'])])

def active_line(t):
    from bisect import bisect_right
    starts=[x[0] for x in LINE_BY_START]
    k=bisect_right(starts,t)-1
    if k<0:return -1,None
    _,i,line=LINE_BY_START[k]
    if t>line['end']+.6:return -1,None
    return i,line

@lru_cache(maxsize=150)
def shape(name):
    im=Image.new('L',(56,13),0);d=ImageDraw.Draw(im)
    if name=='city':
        for x,h in [(1,5),(6,9),(12,6),(17,11),(25,7),(31,9),(38,5),(44,10),(51,6)]:
            d.rectangle((x,13-h,min(55,x+4),12),outline=255,width=1)
            for yy in range(13-h+2,11,3):d.point((x+2,yy),fill=255)
        d.ellipse((43,1,47,5),outline=255)
    elif name in ('phone','promise'):
        d.rounded_rectangle((19,0,36,12),radius=2,outline=255,width=2)
        d.line((23,3,32,3),fill=255)
        d.ellipse((27,10,29,12),fill=255)
        if name=='phone':
            d.polygon([(39,3),(44,11),(34,11)],outline=255)
            d.line((39,6,39,8),fill=255)
        else:
            d.line((22,4,27,8),fill=255);d.line((27,8,34,4),fill=255)
    elif name=='stop':
        d.polygon([(22,1),(33,1),(39,5),(39,8),(33,12),(22,12),(17,8),(17,5)],outline=255,width=2)
        d.line((26,3,26,10),fill=255,width=2);d.line((30,3,30,10),fill=255,width=2)
    elif name=='comet':
        d.ellipse((43,3,51,11),outline=255,width=2)
        for j in range(8):d.line((3+j*5,5+j%3,9+j*5,3+j%4),fill=255)
        d.line((0,9,40,6),fill=255)
    elif name=='two_people':
        for x in (18,37):
            d.ellipse((x-3,2,x+3,6),outline=255)
            d.line((x,6,x,11),fill=255);d.line((x,8,x-5,10),fill=255)
        d.line((18,8,37,8),fill=255)
        d.ellipse((25,1,31,7),outline=255)
    elif name=='rain':
        for x,h in [(2,6),(8,8),(14,4),(20,10),(26,6),(32,8),(38,6),(44,9),(50,4)]:
            d.rectangle((x,13-h,x+3,12),outline=255)
    elif name=='book':
        d.polygon([(9,3),(27,5),(27,12),(9,9)],outline=255,width=2)
        d.polygon([(27,5),(47,3),(47,9),(27,12)],outline=255,width=2)
        d.line((14,5,23,6),fill=255);d.line((31,6,43,5),fill=255)
    elif name=='heart':
        d.polygon([(28,12),(14,4),(14,2),(18,0),(24,1),(28,4),(33,1),(39,0),(43,3),(42,6)],outline=255,width=2)
        d.ellipse((4,4,10,10),outline=255);d.ellipse((46,4,52,10),outline=255)
    elif name=='switch':
        d.rounded_rectangle((10,2,47,11),radius=4,outline=255,width=2)
        d.ellipse((16,3,23,10),fill=255)
        d.line((26,6,41,6),fill=255,width=2)
    elif name=='key':
        d.ellipse((10,2,21,11),outline=255,width=2)
        d.line((21,6,47,6),fill=255,width=2)
        d.line((40,6,40,10),fill=255,width=2);d.line((46,6,46,10),fill=255,width=2)
    elif name=='circuit':
        d.rectangle((22,3,34,10),outline=255,width=2)
        for i in range(2,54,4):
            if i<20 or i>35:d.point((i,2+(i//4)%9),fill=255)
        for y in (2,6,10):d.line((0,y,21,y),fill=255);d.line((34,y,55,y),fill=255)
    elif name=='door':
        d.rectangle((24,0,40,12),outline=255,width=2)
        d.line((27,3,40,0),fill=255);d.line((27,3,27,12),fill=255)
        d.ellipse((13,5,17,9),outline=255);d.line((15,9,15,12),fill=255)
        d.ellipse((47,5,51,9),outline=255);d.line((49,9,49,12),fill=255)
    elif name=='robot':
        d.rounded_rectangle((18,2,38,10),radius=2,outline=255,width=2)
        d.line((28,0,28,2),fill=255);d.point((28,0),fill=255)
        d.ellipse((22,5,25,7),fill=255);d.ellipse((32,5,35,7),fill=255)
        d.line((24,9,32,9),fill=255);d.line((20,11,20,12),fill=255);d.line((36,11,36,12),fill=255)
    elif name=='voice':
        d.ellipse((7,5,14,9),outline=255)
        for i in range(5):
            x=18+i*8;d.arc((x,1+i%3,x+6,12-i%3),-65,65,fill=255,width=2)
    elif name=='fork':
        d.line((27,12,27,6),fill=255,width=2)
        d.line((27,6,7,0),fill=255,width=2)
        d.line((27,6,49,0),fill=255,width=2)
        d.polygon([(3,0),(10,0),(7,4)],fill=255);d.polygon([(46,0),(53,0),(49,4)],fill=255)
    elif name=='noise':
        for i in range(55):
            x=(17*i+7)%56;y=(i*7+i//4)%13
            d.point((x,y),fill=255)
    elif name=='choir':
        for x in range(4,56,9):
            d.ellipse((x-2,2,x+2,6),outline=255)
            d.line((x,6,x,12),fill=255,width=2)
    elif name=='music':
        for x,h in [(3,2),(7,7),(11,3),(15,10),(19,4),(23,7),(27,3),(31,8),(35,5),(39,10),(43,3),(47,6),(51,2)]:
            d.line((x,12-h,x,12),fill=255,width=2)
        d.line((2,7,53,7),fill=255)
    elif name=='star':
        d.polygon([(28,0),(32,4),(43,4),(35,7),(38,12),(28,9),(18,12),(21,7),(13,4),(24,4)],outline=255,width=2)
        for x,y in [(3,2),(7,9),(51,2),(49,10)]:d.point((x,y),fill=255)
    return tuple((x,y) for y in range(13) for x in range(56) if im.getpixel((x,y))>0)

@lru_cache(maxsize=40)
def static_icon(name):return set(shape(name))

def pictogram(t):
    line_idx,line=active_line(t)
    name=VERSE_SCENES.get(line_idx,'city')
    im=base.CLOSE.copy()
    d=ImageDraw.Draw(im,'RGBA')
    pts=static_icon(name)
    a=base.energy(t)
    p=0 if line is None else max(0,min(1,(t-line['start'])/max(.08,line['end']-line['start'])))
    if line:
        ws=line['words']; reached=sum(w['start']<=t for w in ws)
        # Subsequent sung words activate more of the graphic, not textual glyphs.
        fill=max(.28,min(1,(reached+.3)/max(1,len(ws))))
    else:fill=.82
    for x,y in pts:
        # A flickering ripple proceeds through each symbol as singing continues.
        z=(x/55)*.84 + .16*(y/12)
        bright=fill>=z or ((x*7+y*13)%17 <3 and fill>.15)
        if not bright:continue
        flick=.70+.3*abs(math.sin(t*3.3+x*.7+y*.4))
        col=base.PALETTE[(STYLE.get(name,0)+(x//18))%5]
        cx=GRID_X+x*12;cy=GRID_Y+y*20
        rr=3.0+(1.5*a)
        d.ellipse((cx-rr*2,cy-rr*2,cx+rr*2,cy+rr*2),fill=(*col,int(23+45*flick)))
        d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=(*col,int(200+40*flick)))
        d.ellipse((cx-.9,cy-1.8,cx+.9,cy),fill=(245,251,254,190))
    # Dynamic semantic effects that are unmistakably animated.
    if name=='rain':
        for k in range(25):
            x=3+((k*17)%50);y=(k*9+int(t*15))%13
            cx=GRID_X+x*12;cy=GRID_Y+y*20
            d.ellipse((cx-2,cy-3,cx+2,cy+3),fill=(111,187,244,160))
    elif name=='comet':
        x=8+int(41*p);cy=GRID_Y+(3+int(2*math.sin(t*5)))*20
        for j in range(5):
            d.ellipse((GRID_X+(x-j)*12-2,cy-2,GRID_X+(x-j)*12+2,cy+2),fill=(*base.PALETTE[2],int(220-42*j)))
    elif name in ('voice','music'):
        for k in range(10):
            xx=GRID_X+(4+5*k)*12; yy=GRID_Y+(6+int(4*math.sin(t*4+k*.7)))*20
            d.ellipse((xx-2,yy-2,xx+2,yy+2),fill=(249,188,221,200))
    elif name=='noise':
        for k in range(26):
            x=(k*23+int(t*11))%56;y=(k*19+int(t*4))%13
            cx=GRID_X+x*12;cy=GRID_Y+y*20
            d.point((cx,cy),fill=(236,205,254,245))
    return im

# The newly built *inside* looks like the reverse of the same pegboard:
# perforated rear pins, copper PCB traces, component towers, casing and
# microscopic dancers. No inexplicable text strip or billboard.
def actual_inside_plate():
    im=base.backdrop((8,13,37),(29,13,55))
    d=ImageDraw.Draw(im,'RGBA')
    # Thick toy casing and corner screws — deliberately matching the bezel.
    d.rounded_rectangle((13,14,947,529),radius=46,fill=(21,28,59,255),outline=(142,170,194,255),width=8)
    d.rounded_rectangle((34,35,926,510),radius=32,fill=(8,14,39,255),outline=(66,88,134,255),width=5)
    for x,y in [(54,52),(907,52),(54,486),(907,486)]:
        d.ellipse((x-9,y-9,x+9,y+9),fill=(114,125,149,255),outline=(193,210,214,255),width=2)
        d.line((x-4,y+4,x+4,y-4),fill=(45,56,77,255),width=2)
    # Back of the SAME 56 x 13 peg lattice, seen through the rear of the toy.
    d.rounded_rectangle((80,60,881,299),radius=18,fill=(6,25,46,255),outline=(57,111,134,255),width=4)
    for yy in range(13):
        for xx in range(56):
            x=92+xx*14; y=79+yy*16
            palette=base.PALETTE[(xx*5+yy*11)%5]
            if (xx*13+yy*17)%11<4:
                d.ellipse((x-5,y-5,x+5,y+5),fill=(*palette,90),outline=(*palette,160),width=1)
                d.ellipse((x-2,y-2,x+2,y+2),fill=(200,231,243,195))
            else:
                d.ellipse((x-3,y-3,x+3,y+3),fill=(36,67,83,255))
    # Exposed copper tracks converge to miniature DJ booth; a circuit board
    # architectural space, NOT a generic nightclub with a sign.
    d.polygon([(71,306),(885,302),(920,487),(40,487)],fill=(16,54,64,255))
    for i in range(16):
        x=80+i*53
        d.line((x,305,480+(x-480)*1.45,480),fill=(193,126,74,168),width=2)
    for y in (331,357,388,426,465):
        d.line((70,y,891,y),fill=(151,115,66,190),width=2)
    # Resistors, sockets, capacitors create unmistakable toy-scale geometry.
    for x in (142,805):
        d.rounded_rectangle((x-39,309,x+39,421),radius=12,fill=(35,69,88,255),outline=(210,164,98,255),width=4)
        for yy in (327,347,367,387,407):
            d.line((x-31,yy,x+31,yy),fill=(*base.PALETTE[(yy//19)%5],150),width=3)
    for x in (240,720):
        d.rounded_rectangle((x-21,383,x+21,460),radius=7,fill=(46,66,106,255),outline=(126,174,196,255),width=3)
        d.ellipse((x-13,392,x+13,418),outline=(255,177,119,220),width=3)
    # PCB strips rise behind a central miniature DJ booth.
    d.polygon([(368,399),(591,399),(608,468),(348,468)],fill=(28,39,86,255))
    d.line((358,404,599,404),fill=(97,237,236,255),width=4)
    d.rounded_rectangle((409,382,552,429),radius=7,fill=(19,27,59,255),outline=(251,122,175,240),width=3)
    for x in range(421,548,13):
        d.ellipse((x-3,395,x+3,401),fill=(*base.PALETTE[(x//13)%5],230))
    d.line((480,61,480,145),fill=(109,117,153,255),width=4)
    d.ellipse((451,134,509,192),fill=(111,131,165,255),outline=(218,227,242,255),width=3)
    for i in range(15):
        a=i*2*math.pi/15
        d.ellipse((480+24*math.cos(a)-3,163+24*math.sin(a)-3,480+24*math.cos(a)+3,163+24*math.sin(a)+3),fill=(246,210,244,245))
    return im

INSIDE=actual_inside_plate()
DANCERS=[];rnd=random.Random(707)
for i in range(29):
    # A dozen little hand-drawn light people at the back, more at the front.
    x=rnd.randint(250,711);y=rnd.randint(369,443)
    DANCERS.append((x,y,i%5,rnd.random()*6.28,rnd.randint(10,20)))

def inside_frame(t):
    im=INSIDE.copy();d=ImageDraw.Draw(im,'RGBA')
    a=base.energy(t)
    # Music-reactive backlit circuitry and reflected colored light
    for i in range(22):
        x=107+i*34;level=(4+25*a)*(0.65+0.35*math.sin(t*4+i)**2)
        d.rounded_rectangle((x,281-level,x+8,281),radius=3,fill=(*base.PALETTE[i%5],int(130+90*a)))
    # The disco is IN the toy: microscopic dancers between components.
    for x,y,ci,phase,h in DANCERS:
        pulse=math.sin(t*4.5+phase)
        yy=y+4*pulse
        swing=8*math.sin(t*3.6+phase)
        col=base.PALETTE[ci]
        d.ellipse((x-5,yy-h-13,x+5,yy-h-3),fill=(*col,235))
        d.line((x,yy-h,x,yy),fill=(*col,240),width=3)
        d.line((x,yy-h+4,x-8+swing*.4,yy-h-5),fill=(*col,240),width=3)
        d.line((x,yy-h+4,x+8+swing*.4,yy-h-4),fill=(*col,240),width=3)
        d.line((x,yy,x-5,yy+10),fill=(*col,230),width=3)
        d.line((x,yy,x+6,yy+11),fill=(*col,230),width=3)
    # The tiny DJ is a lit circuit component waving behind board contacts.
    x=480;y=390+3*math.sin(t*3)
    d.ellipse((x-9,y-29,x+9,y-11),fill=(251,199,116,255))
    d.line((x,y-10,x,y+12),fill=(239,137,191,255),width=5)
    d.line((x,y-4,x+12,y-17+6*math.sin(t*4)),fill=(239,137,191,255),width=4)
    d.line((x,y-4,x-12,y-16),fill=(239,137,191,255),width=4)
    return im

# The front has actual karaoke only during choruses. Verses perform images.
def front(t,karaoke=True):
    if karaoke:
        im=base.CLOSE.copy()
        if base.live_word(t):im=base.faded_word(im,t,'front')
        else:im=pictogram(t)
        return im
    return pictogram(t)

# No time<72 branch: original first zoom reset at exactly 72.0 to the
# second portal's timing and jumped back to full-screen mid-zoom.
def portal(t,start,end):
    im=front(t,karaoke=True)
    z=base.smooth((t-start)/max(.1,end-start))
    cw=max(82,round(960-850*z));ch=max(48,round(540-480*z))
    cx,cy=577,242
    l=max(0,min(W-cw,round(cx-cw*.5)));top=max(0,min(H-ch,round(cy-ch*.5)))
    im=im.crop((l,top,l+cw,top+ch)).resize((W,H),Image.Resampling.BICUBIC)
    # The portal resolves to the physical reverse pegboard, not a sudden cut.
    reveal=base.smooth((z-.73)/.27)
    if reveal>0:im=Image.blend(im,inside_frame(t),reveal)
    return im

def back_to_child(t,start=92.785,end=94.7):
    u=base.smooth((t-start)/(end-start))
    # Leave rave through a single miniature light and find matching colored
    # pinpoints on the child's pillow. Out of the *dream*, not into text.
    a=inside_frame(t)
    b=base.dream_frame(t)
    if u<.3:
        cw=round(960-150*u/.3);ch=round(540-90*u/.3)
        a=a.crop(((960-cw)//2,(540-ch)//2,(960+cw)//2,(540+ch)//2)).resize((W,H),Image.Resampling.BICUBIC)
    im=Image.blend(a,b,u)
    return im

def dream_pullback(t,start=94.7,end=102.903):
    p=base.smooth((t-start)/(end-start))
    if p<.3:
        z=1.0+.03*(p/.3)
        cw=round(W/z);ch=round(H/z)
        dream=base.dream_frame(t)
        return dream.crop(((W-cw)//2,(H-ch)//2,(W+cw)//2,(H+ch)//2)).resize((W,H),Image.Resampling.BICUBIC)
    # Cross gently from close face to a crop of SAME CANONICAL bedroom child;
    # the crop then pulls out to the established wide on the actual song clock.
    q=base.smooth((p-.3)/.7)
    cw=base.lerp(205,960,q);ch=base.lerp(116,540,q)
    cx=base.lerp(422,480,q);cy=base.lerp(348,270,q)
    l=max(0,min(960-cw,cx-cw*.5));top=max(0,min(540-ch,cy-ch*.5))
    room=base.ROOM_B.crop((round(l),round(top),round(l+cw),round(top+ch))).resize((W,H),Image.Resampling.BICUBIC)
    a=base.smooth((p-.31)/.31)
    return Image.blend(base.dream_frame(t),room,a)

def bridge_dream(t):
    dream=base.dream_frame(t)
    if t<171.65:
        return Image.blend(inside_frame(t),dream,base.smooth((t-170.991)/.659))
    if t>188.75:
        # Back to the same physical toy at final chorus, instead of popping.
        return Image.blend(dream,base.CLOSE,base.smooth((t-188.75)/(190.41-188.75)))
    return dream

def last_exit(t):
    # Reverse the camera path through the toy into its room.
    if t<222.0:
        p=base.smooth((t-219.994)/(222-219.994))
        return Image.blend(inside_frame(t),base.CLOSE,p)
    # The room gradually returns while the blue peg becomes a single light.
    return exact_room_push(t,222.0,226.315,ending='outro')

SHOTS=[
 ('00 / THE ROOM',0,11,'bedroom_eyes_open','One physical bedroom, one child, one toy.'),
 ('01 / A CAMERA FINDS THE TOY',11,25.09,'bedroom_push','Continuous physical push; no mismatched macro cut at 0:25.'),
 ('02 / THE CITY AND THE QUESTION',25.09,54.25,'verse_peg_anim','Verse imagery: city, phone, pause, comet, asking, rain, book, heart and switches.'),
 ('03 / THE TOY SINGS',54.25,71.614,'chorus_peg_karaoke','Physical peg-formed words only in chorus.'),
 ('04 / THE FIRST PEG PORTAL',71.614,72.947,'portal_enter','Continuous shot start, no reset at 72.0 seconds.'),
 ('05 / MICRO-WORLD',72.947,92.785,'inside_toy','PCB toy-scale disco, no lettering on LED marquee.'),
 ('06 / OUT OF THE DREAM',92.785,94.7,'rave_to_dream','Leave the final other-side syllable for the sleeping boy.'),
 ('07 / THE CHILD REAPPEARS',94.7,102.903,'dream_zoom_out','Zoom out from the sleeping boy into his established bedroom.'),
 ('08 / CAMERA FINDS THE BOARD AGAIN',102.903,105.5,'return_to_toy','Continue from full bedroom to matching macro; verse 2 starts.'),
 ('09 / VERSE IN PICTOGRAMS',105.5,132.02,'verse_peg_anim','Promises, machine, voices, choices, noise, choir, music and hope.'),
 ('10 / CHORUS TWO',132.02,149.374,'chorus_peg_karaoke','Every word illuminated; no truncation.'),
 ('11 / THROUGH THE LIGHT AGAIN',149.374,150.772,'portal_enter','Same continuous portal method.'),
 ('12 / THE COMPONENT PARTY',150.772,170.991,'inside_toy','Miniature dancers inside physical electronics.'),
 ('13 / THE BRIDGE, THE CHILD',170.991,190.41,'dream_bridge','Boy dreaming, color reflections; no captions.'),
 ('14 / FINAL CHORUS',190.41,207.788,'chorus_peg_karaoke','The pegboard sings once more.'),
 ('15 / FINAL PORTAL',207.788,209.17,'portal_enter','Same physical portal and camera path.'),
 ('16 / LAST RAVE',209.17,219.994,'inside_toy','Last tiny rave.'),
 ('17 / HOMEWARD',219.994,226.315,'rave_room_return','Reverse out through the toy and back to the room.'),
 ('18 / THE LAST LIGHT',226.315,DURATION,'bedroom_outro','One peg remains; no disconnected text.')
]
base.SHOTS=SHOTS

def scene_at(t):
    for sh in SHOTS:
        if sh[1]<=t<sh[2]:return sh
    return SHOTS[-1]

def frame(t):
    sh=scene_at(t);kind=sh[3]
    if kind=='bedroom_eyes_open':im=base.ROOM_A.copy()
    elif kind=='bedroom_push':im=exact_room_push(t,15,25.09) if t>15 else base.ROOM_B.copy()
    elif kind=='verse_peg_anim':im=front(t,karaoke=False)
    elif kind=='chorus_peg_karaoke':im=front(t,karaoke=True)
    elif kind=='portal_enter':im=portal(t,sh[1],sh[2])
    elif kind=='inside_toy':im=inside_frame(t)
    elif kind=='rave_to_dream':im=back_to_child(t)
    elif kind=='dream_zoom_out':im=dream_pullback(t)
    elif kind=='return_to_toy':im=exact_room_push(t,102.903,105.5)
    elif kind=='dream_bridge':im=bridge_dream(t)
    elif kind=='rave_room_return':im=last_exit(t)
    elif kind=='bedroom_outro':im=base.ROOM_OUT.copy()
    else:raise ValueError(kind)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,9),fill=(5,7,18));d.rectangle((0,H-10,W,H),fill=(5,7,18))
    return im

# Base encoder uses its own frame global. Replace only its dynamic scene hook,
# never the original file on disk.
base.frame=frame


def storyboard():
    milestones=[(14.5,'BEDTIME'),(24.9,'MATCHED CAMERA'),(29.0,'VERSE PICTOGRAM'),(56.2,'CHORUS KARAOKE'),
      (72.35,'FIXED PORTAL'),(81,'RAVE INSIDE TOY'),(93.35,'DREAM RETURN'),(99.5,'ZOOM FROM DREAM'),
      (110,'VERSE TWO'),(159.7,'MINI PEOPLE'),(176,'THE BRIDGE'),(238,'ONE PEG')]
    cw,ch=350,197;gap=16;top=28;bottom=30
    out=Image.new('RGB',(3*(cw+gap)+gap,4*(ch+gap+bottom)+gap),(14,19,35))
    d=ImageDraw.Draw(out)
    for i,(t,name) in enumerate(milestones):
        pic=frame(t).resize((cw,ch),Image.Resampling.LANCZOS)
        x=gap+(i%3)*(cw+gap);y=top+(i//3)*(ch+gap+bottom)
        out.paste(pic,(x,y))
        d.text((x+4,y+ch+6),f'{int(t//60)}:{t%60:05.2f}  {name}',font=base.ff(14,True),fill=(234,232,242))
    p=ROOT/'Nobody_Dream_Rave_v2_Storyboard.png';out.save(p,optimize=True)
    return p


def manifest():
    a={'title':'Nobody Owns Tomorrow — illustrated animatic v2','duration':DURATION,
       'timing_basis':'Suno aligned words; model-derived, not independently ear-checked',
       'narrative_change':'Verse pegboard pictograms, chorus-only karaoke, continuous physical camera moves, 1:33 dream return, toy-circuit micro-rave with no text',
       'shot_timeline': [{'id':s[0],'start_s':s[1],'end_s':s[2],'visual':s[3],'intent':s[4]} for s in SHOTS],
       'semantic_visuals':[{'line_number':i,'lyric':base.align['lines'][i]['text'],'start_s':base.align['lines'][i]['start'],'end_s':base.align['lines'][i]['end'],'peg_animation':name} for i,name in VERSE_SCENES.items()],
       'not_certified':['automatically aligned word onsets','video frame/word alignment precision','lipsync']}
    p=ROOT/'Nobody_Dream_Rave_v2_Manifest.json';p.write_text(json.dumps(a,indent=2));return p

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--start',type=float,default=0.0)
    parser.add_argument('--duration',type=float,default=DURATION)
    parser.add_argument('--fps',type=int,default=12)
    parser.add_argument('--still-only',action='store_true')
    p=parser.parse_args()
    print('Storyboard:',storyboard(),flush=True)
    print('Manifest:',manifest(),flush=True)
    for t in [24.90,25.10,54.4,71.7,72.15,72.8,73.01,91.9,92.9,94.6,99.0,102.9,103.5,105.45,105.6,150.0,176,190.4,190.5,219.8,222.1,225.9,226.4]:
        frame(t).save(ROOT/f'Nobody_v2_QA_{t:.2f}.png')
    if p.still_only:sys.exit(0)
    out=ROOT/('Nobody_Dream_Rave_v2_Cinematic_Animatic.mp4' if p.start==0 and p.duration>=DURATION else 'Nobody_Dream_Rave_v2_Preview.mp4')
    print('Render',out,flush=True)
    base.render_video(out,p.start,min(p.duration,DURATION-p.start),fps=p.fps)
    print('Done',out,flush=True)
