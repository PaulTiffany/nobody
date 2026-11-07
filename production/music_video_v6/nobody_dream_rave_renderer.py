#!/usr/bin/env python3
"""Nobody Owns Tomorrow: $0 cinematic STORYBOARD animatic.

Uses original Suno word-alignment JSON (model output; not ear-verified),
licensed locally supplied WAV, Pillow, and FFmpeg. No model inference or paid
services. Every frame is a pure function of audio time (apart from display
randomness deterministically seeded). This is a prototype, not photorealism.
"""
import argparse, bisect, colorsys, json, math, os, random, re, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(os.environ.get('NOBODY_MEDIA_ROOT', '/mnt/data'))
ALIGN=ROOT/'nobody_suno_word_alignment.json'
W,H=960,540
DURATION=263.24
FPS=12
RNG=random.Random(1204)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONTM='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
PALETTE=[(79,228,234),(255,112,178),(255,201,93),(158,139,255),(129,236,168)]

FONTS={}
def ff(sz,bold=False,mono=False):
    k=(sz,bold,mono)
    if k not in FONTS:FONTS[k]=ImageFont.truetype(FONTM if mono else BOLD if bold else FONT,sz)
    return FONTS[k]

def blend(a,b,x):
    return int(a*(1-x)+b*x)
def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def lerp(a,b,x):return a+(b-a)*x

def backdrop(top,bottom):
    im=Image.new('RGB',(W,H));d=ImageDraw.Draw(im)
    for y in range(H):
        z=y/(H-1)
        d.line((0,y,W,y),fill=tuple(blend(a,b,z) for a,b in zip(top,bottom)))
    return im

def light_gradient(im,x,y,r,color,strength=0.5):
    # Local warm glow; precomputed on static plates only.
    arr=np.array(im,dtype=np.float32)
    Y,X=np.ogrid[:H,:W]
    dist=((X-x)**2+(Y-y)**2)/(r*r)
    al=np.exp(-dist*2)*strength
    arr[:]=arr*(1-al[:,:,None])+np.array(color,dtype=np.float32)[None,None,:]*al[:,:,None]
    return Image.fromarray(np.clip(arr,0,255).astype('uint8'))

def sparkle(d,x,y,r,col):
    d.line((x-r,y,x+r,y),fill=col,width=1)
    d.line((x,y-r,x,y+r),fill=col,width=1)
    d.ellipse((x-1.3,y-1.3,x+1.3,y+1.3),fill=col)

def lamp_toy(d, t=0,scale=1):
    # Tiny but still the SAME night-brite as the close view (navy body, pink thumb dial).
    box=(720,283,874,380)
    d.rounded_rectangle(box,radius=17,fill=(25,31,64),outline=(135,153,185),width=3)
    d.rounded_rectangle((730,294,864,369),radius=9,fill=(5,14,30),outline=(69,90,127),width=2)
    for iy in range(7):
        for ix in range(13):
            x=741+ix*9.4;y=305+iy*9.4
            phase=(ix*7+iy*11)%13
            bright=abs(math.sin(t*.4+phase))>.2 and (iy > 3+2*math.sin(ix*.3))
            d.ellipse((x-2,y-2,x+2,y+2),fill=(38,70,93) if not bright else PALETTE[(ix+iy)%5])
    d.ellipse((846,369,860,383),fill=(213,116,161),outline=(255,206,213),width=2)

STARS=[(RNG.randrange(60,940),RNG.randrange(28,235),RNG.choice([1,1,1,2]),RNG.random()*6.28) for _ in range(37)]


def boy(d,close=False,awake=False,t=0):
    # Canonical kid: dark wavy hair with a left-curl tuft, teal pajamas, two freckles.
    if not close:
        # Pillow, pajama collar, blanket and resting child in the established same room.
        d.rounded_rectangle((294,310,488,381),radius=31,fill=(179,170,193),outline=(211,190,203),width=3)
        d.ellipse((354,291,453,391),fill=(220,159,125),outline=(151,105,107),width=2)
        d.ellipse((346,325,361,349),fill=(204,134,112))
        d.pieslice((344,276,470,363),180,345,fill=(34,31,49))
        d.ellipse((364,289,404,323),fill=(35,31,47))
        d.polygon([(367,300),(348,293),(361,282),(385,285)],fill=(35,31,47))
        if awake:
            # Conspicuous wake-up expression for the final-chorus drum hit.
            for x,y in ((411,332),(432,332)):
                d.ellipse((x-5,y-6,x+5,y+5),fill=(238,229,208),outline=(95,69,72),width=1)
                d.ellipse((x-2,y-4,x+3,y+3),fill=(30,36,57))
                d.ellipse((x-1,y-3,x,y-2),fill=(255,252,242))
        else:
            d.arc((406,328,430,344),8,150,fill=(66,45,57),width=2)
        for a,b in [(423,352),(433,351)]:d.ellipse((a,b,a+2,b+2),fill=(144,87,81))
        d.arc((422,355,442,366),-5,120,fill=(143,77,83),width=2)
        d.polygon([(322,374),(340,365),(485,365),(514,391),(513,457),(308,457)],fill=(30,143,162))
        d.rounded_rectangle((272,381,646,461),radius=24,fill=(94,112,157),outline=(136,143,180),width=3)
        d.line((298,404,621,404),fill=(145,155,194),width=2)
        d.line((312,432,625,432),fill=(98,132,169),width=4)
    else:
        # Dream close-up, consistent hair/face colors/eyes/freckles.
        d.ellipse((163,104,778,514),fill=(181,166,187),outline=(227,199,194),width=5)
        d.ellipse((265,123,722,517),fill=(224,157,126),outline=(156,109,103),width=4)
        d.ellipse((258,303,303,368),fill=(198,122,110))
        d.pieslice((244,100,743,405),180,335,fill=(33,30,46))
        d.ellipse((278,133,506,226),fill=(31,30,45))
        d.polygon([(285,191),(232,154),(244,118),(335,139)],fill=(31,30,45))
        # eyes shut
        d.arc((469,296,545,339),10,165,fill=(69,47,59),width=5)
        d.arc((617,291,688,331),10,165,fill=(69,47,59),width=5)
        for x,y in [(543,379),(553,373),(568,379),(584,373)]:d.ellipse((x-3,y-3,x+3,y+3),fill=(148,90,80))
        d.arc((548,405,632,447),0,125,fill=(148,89,91),width=4)
        d.polygon([(222,478),(306,438),(735,430),(805,540),(0,540)],fill=(94,113,159))


def room_plate(awake=False,outro=False):
    im=backdrop((14,23,49),(43,40,75));d=ImageDraw.Draw(im)
    # Night wall, slightly lived-in, bookcase, framed star chart.
    d.rectangle((0,436,W,H),fill=(39,32,48))
    d.polygon([(0,436),(960,421),(960,450),(0,480)],fill=(62,46,66))
    # Window, bright moon and quiet city outside
    d.rounded_rectangle((89,70,316,282),radius=16,fill=(49,58,89),outline=(138,132,147),width=7)
    d.rectangle((104,84,300,271),fill=(17,35,71) if not outro else (50,64,102))
    d.ellipse((237,105,280,148),fill=(238,232,197))
    d.ellipse((220,97,270,137),fill=(24,40,75) if not outro else (51,65,100))
    for i in range(7):
        xx=105+i*31;hh=RNG.choice([32,47,68,82,40])
        d.rectangle((xx,271-hh,xx+25,270),fill=(17,27,51))
        for yy in range(271-hh+10,267,15):
            d.line((xx+6,yy,xx+9,yy),fill=(138,145,110),width=3)
    d.line((202,84,202,270),fill=(114,121,147),width=6)
    d.line((104,177,300,177),fill=(114,121,147),width=6)
    d.rounded_rectangle((57,67,102,301),radius=14,fill=(79,75,109))
    d.rounded_rectangle((302,67,338,301),radius=14,fill=(85,81,108))
    d.rounded_rectangle((399,92,605,239),radius=8,fill=(44,48,74),outline=(140,130,159),width=4)
    d.ellipse((461,124,529,196),outline=(117,206,213),width=3)
    for cx,cy,rad,col in [(460,153,4,(250,196,138)),(529,153,3,(244,123,170)),(495,183,4,(131,224,226))]:sparkle(d,cx,cy,rad,col)
    # Constellation mobile
    for i,x in enumerate((390,451,509,576,647)):
        d.line((x,30,x,60+i%3*11),fill=(131,129,158),width=2)
        sparkle(d,x,64+i%3*10,7,(199,200,220))
    # Bed headboard, mattress and small rug
    d.rounded_rectangle((222,286,666,470),radius=25,fill=(50,50,78),outline=(108,92,124),width=7)
    d.rounded_rectangle((243,323,656,472),radius=23,fill=(205,186,172))
    d.ellipse((253,453,675,515),fill=(53,44,66))
    boy(d,awake=awake)
    # Nightstand and night-brite
    d.rounded_rectangle((685,372,902,472),radius=9,fill=(112,76,81),outline=(174,123,110),width=4)
    d.rectangle((687,459,709,540),fill=(101,68,72))
    d.rectangle((870,459,887,540),fill=(101,68,72))
    lamp_toy(d,1 if awake else 3)
    im=light_gradient(im,810,344,240,(112,165,234),.23)
    if not awake and not outro:
        d=ImageDraw.Draw(im)
        pass  # cinematic frames carry no editorial headings
    if outro:
        # One luminous peg survives the closing image.
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((730,294,864,369),radius=9,fill=(5,14,30))
        d.ellipse((795,321,815,341),fill=(124,231,238))
        sparkle(d,804,331,20,(202,246,253))
    return im

def dream_plate():
    im=backdrop((31,25,66),(79,52,98));d=ImageDraw.Draw(im)
    for x,y,r,phase in STARS:
        if y<260:sparkle(d,x,y,2+(r%3),(83,91,150))
    # No non-diegetic dream title over the character
    boy(d,close=True)
    im=light_gradient(im,760,218,460,(136,77,194),.17)
    return im

def close_plate():
    im=backdrop((15,19,49),(40,30,59));d=ImageDraw.Draw(im)
    # Deliberately a close cinematic view of the EXACT same wooden nightstand/toy.
    d.polygon([(0,443),(960,423),(960,540),(0,540)],fill=(72,46,56))
    d.polygon([(0,454),(960,436),(960,457),(0,481)],fill=(105,69,76))
    d.rounded_rectangle((69,63,890,421),radius=40,fill=(38,50,84),outline=(173,181,208),width=6)
    d.rounded_rectangle((89,80,870,401),radius=31,fill=(7,14,36),outline=(70,88,132),width=5)
    d.rounded_rectangle((106,99,855,384),radius=19,fill=(5,11,27),outline=(27,48,83),width=3)
    d.ellipse((830,385,851,408),fill=(215,108,172),outline=(253,202,214),width=3)
    for px,py in [(92,75),(866,73),(93,405),(866,407)]:
        d.ellipse((px-3,py-3,px+3,py+3),fill=(219,218,221))
    # pegboard holes, but no karaoke word yet
    for y in range(13):
        for x in range(56):
            px=148+x*12;py=125+y*20
            d.ellipse((px-3,py-3,px+3,py+3),fill=(23,36,66))
    # No non-diegetic scene marker across the toy
    im=light_gradient(im,474,235,500,(57,99,171),.14)
    return im

def rave_plate():
    im=backdrop((19,7,44),(67,22,90));d=ImageDraw.Draw(im)
    d.polygon([(0,428),(960,422),(960,540),(0,540)],fill=(19,11,48))
    # Toy interior miniature circuitry: three layers of copper tracks + neon depth.
    for i in range(16):
        x=40+i*58
        d.line((480,95,x,451),fill=(43+i%4*5,32,100+i%3*15),width=3)
    for yy in [253,298,346,386,430,474,512]:
        d.line((0,yy,960,yy),fill=(52,56,126),width=2)
    for i in range(12):
        xx=80+i*75
        d.line((xx,70,xx,140+i%4*11),fill=(88,46,136),width=2)
        sparkle(d,xx,140+i%4*11,4,PALETTE[i%5])
    # Toy-speakers like little cathedral pillars
    for x in [114,843]:
        d.rounded_rectangle((x-57,228,x+57,437),radius=17,fill=(26,21,65),outline=(199,88,181),width=4)
        for cy,r in [(284,34),(378,24)]:
            d.ellipse((x-r,cy-r,x+r,cy+r),outline=(108,228,229),width=4)
            d.ellipse((x-r*.43,cy-r*.43,x+r*.43,cy+r*.43),fill=(68,48,116))
    # Tiny elevated DJ stage and mini disco ball
    d.rounded_rectangle((369,351,594,436),radius=12,fill=(23,37,77),outline=(125,234,234),width=4)
    d.line((363,382,604,382),fill=(114,227,244),width=3)
    d.line((480,59,480,133),fill=(104,95,141),width=3)
    d.ellipse((453,119,507,173),fill=(123,130,177),outline=(199,217,244),width=2)
    for ang in range(0,360,45):
        x=480+22*math.cos(math.radians(ang));y=146+22*math.sin(math.radians(ang))
        d.ellipse((x-3,y-3,x+3,y+3),fill=(236,200,243))
    # LED sign physical fascia for animated word (not a subtitle bar!)
    d.rounded_rectangle((178,173,787,258),radius=18,fill=(17,17,45),outline=(216,123,193),width=4)
    d.text((230,88),'THE OTHER SIDE',font=ff(24,True),fill=(232,176,220))
    return im

ROOM_A=room_plate(awake=True);ROOM_B=room_plate(awake=False);ROOM_OUT=room_plate(awake=False,outro=True)
DREAM=dream_plate();CLOSE=close_plate();RAVE=rave_plate()

# 5x7 dot-matrix glyphs, one illuminated peg per pixel, legible on a physical board.
GLYPHS={
'A':["01110","10001","10001","11111","10001","10001","10001"],
'B':["11110","10001","10001","11110","10001","10001","11110"],
'C':["01111","10000","10000","10000","10000","10000","01111"],
'D':["11110","10001","10001","10001","10001","10001","11110"],
'E':["11111","10000","10000","11110","10000","10000","11111"],
'F':["11111","10000","10000","11110","10000","10000","10000"],
'G':["01111","10000","10000","10111","10001","10001","01110"],
'H':["10001","10001","10001","11111","10001","10001","10001"],
'I':["11111","00100","00100","00100","00100","00100","11111"],
'J':["00111","00010","00010","00010","10010","10010","01100"],
'K':["10001","10010","10100","11000","10100","10010","10001"],
'L':["10000","10000","10000","10000","10000","10000","11111"],
'M':["10001","11011","10101","10101","10001","10001","10001"],
'N':["10001","11001","10101","10011","10001","10001","10001"],
'O':["01110","10001","10001","10001","10001","10001","01110"],
'P':["11110","10001","10001","11110","10000","10000","10000"],
'Q':["01110","10001","10001","10001","10101","10010","01101"],
'R':["11110","10001","10001","11110","10100","10010","10001"],
'S':["01111","10000","10000","01110","00001","00001","11110"],
'T':["11111","00100","00100","00100","00100","00100","00100"],
'U':["10001","10001","10001","10001","10001","10001","01110"],
'V':["10001","10001","10001","10001","10001","01010","00100"],
'W':["10001","10001","10001","10101","10101","10101","01010"],
'X':["10001","10001","01010","00100","01010","10001","10001"],
'Y':["10001","10001","01010","00100","00100","00100","00100"],
'Z':["11111","00001","00010","00100","01000","10000","11111"],
'0':["01110","10011","10101","10101","11001","10001","01110"],
'1':["00100","01100","00100","00100","00100","00100","01110"],
'2':["01110","10001","00001","00010","00100","01000","11111"],
'3':["11110","00001","00001","01110","00001","00001","11110"],
'4':["00010","00110","01010","10010","11111","00010","00010"],
'5':["11111","10000","10000","11110","00001","00001","11110"],
'6':["00111","01000","10000","11110","10001","10001","01110"],
'7':["11111","00001","00010","00100","01000","01000","01000"],
'8':["01110","10001","10001","01110","10001","10001","01110"],
'9':["01110","10001","10001","01111","00001","00010","11100"],
}

def dotmap(text,maxcols=53):
    text=re.sub('[^A-Z0-9]','',text.upper())
    if not text:return []
    # 5x7 standard glyphs + one empty column. For >9 letters, tiny condensed type.
    n=len(text)
    if n*6-1>maxcols:text=text[:max(1,(maxcols+1)//6)]
    points=[]
    for i,ch in enumerate(text):
        glyph=GLYPHS.get(ch,GLYPHS['O'])
        for y,row in enumerate(glyph):
            for x,dot in enumerate(row):
                if dot=='1':points.append((i*6+x,y))
    return points,6*len(text)-1

# Pre-render every unique word into TWO scene-integrated spatial light layers.
# The layer is cached to prevent a blur operation on every video frame.
from functools import lru_cache
@lru_cache(maxsize=200)
def word_layer(word,where):
    text=re.sub('[^A-Z0-9]','',word.upper())
    if not text:return Image.new('RGBA',(W,H))
    pts,cols=dotmap(text,maxcols=51)
    if where=='front':
        step=12;yy=175;xx=480-int((cols-1)*step/2);vx=step;vy=20; radius=4.5
    else:
        step=min(11,max(6,480/max(1,cols)))
        yy=187;xx=480-(cols-1)*step/2;vx=step;vy=9;radius=3
    halo=Image.new('RGBA',(W,H),(0,0,0,0));hg=ImageDraw.Draw(halo,'RGBA')
    sharp=Image.new('RGBA',(W,H),(0,0,0,0));sg=ImageDraw.Draw(sharp,'RGBA')
    colors=[(96,237,242),(250,136,191),(255,206,124)]
    for x,y in pts:
        cx=xx+x*vx;cy=yy+y*vy
        color=colors[(x//6+y//3)%3] if where=='front' else colors[(x+y//2)%3]
        hg.ellipse((cx-radius*2.1,cy-radius*2.1,cx+radius*2.1,cy+radius*2.1),fill=(*color,160))
        sg.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(*color,255))
        sg.ellipse((cx-1,cy-1,cx+1,cy+1),fill=(245,248,251,255))
    halo=halo.filter(ImageFilter.GaussianBlur(6 if where=='front' else 4))
    return Image.alpha_composite(halo,sharp)

align=json.load(open(ALIGN))
words=[]
for line in align['lines']:
    for wd in line['words']:
        if wd['text'].strip():
            words.append({'text':wd['text'],'start':wd['start'],'end':wd['end'],'line':line['text']})
words.sort(key=lambda x:x['start'])
starts=[w['start'] for w in words]

def live_word(t):
    i=bisect.bisect_right(starts,t)-1
    if i<0:return None
    w=words[i]
    if t<=w['end']+.22:return w
    return None

# Storyboards and distinctive scene changes follow lyric timestamps rather
# than old approximate guesses. A portal begins on ON, reveals on SIDE.
SHOTS=[
 ('00 / THE ROOM',0.0,11.0,'bedroom_eyes_open','A sleepy boy settles into bed. The toy is already glowing.'),
 ('01 / THE TOY WAITS',11.0,25.09,'bedroom_asleep','The door closes; the camera notices the toy.'),
 ('02 / THE LIGHTS SING',25.09,71.614,'nightbrite_karaoke','The pegs form each sung word, never a subtitle overlay.'),
 ('03 / FIRST PORTAL',71.614,72.947,'portal_enter','ON → THE → OTHER → SIDE drives the lens push.'),
 ('04 / INSIDE THE LIGHT',72.947,102.903,'miniature_rave','A toy-scale party; words become physical LED signs.'),
 ('05 / SECOND VERSE',102.903,149.374,'nightbrite_karaoke','The camera backs out, and the pegs sing again.'),
 ('06 / SECOND PORTAL',149.374,150.772,'portal_enter','The word SIDE opens the toy again.'),
 ('07 / A BIGGER PARTY',150.772,170.991,'miniature_rave','A celebratory micro-world, still word-synced.'),
 ('08 / THE DREAM',170.991,190.41,'sleeping_boy','Bridge: lights flicker across the sleeping boy; no captions.'),
 ('09 / ONE MORE CHORUS',190.41,207.788,'nightbrite_karaoke','The words return to the front of the toy.'),
 ('10 / LAST PORTAL',207.788,209.17,'portal_enter','The final SIDE leads into the brightest rave.'),
 ('11 / THE OTHER SIDE',209.17,226.315,'miniature_rave','Last miniature dance, LED words and light-play.'),
 ('12 / A SINGLE PEG',226.315,DURATION,'bedroom_outro','The child sleeps; the toy returns to one light.')
]

# Deterministic, low-cost RMS values for dancing/light accents.
AUDIO=ROOT/'Nobody Owns Tomorrow(1).wav'
def get_env(path):
    # Audio-free still renders work too; do not load entire WAV.
    if not path.exists():return [0.15]*int(DURATION*10+5)
    e=[]
    with wave.open(str(path),'rb') as w:
        ch=w.getnchannels();r=w.getframerate();sw=w.getsampwidth()
        n=int(r*.1)
        if sw!=2:return [0.15]*int(DURATION*10+5)
        while True:
            raw=w.readframes(n)
            if not raw:break
            a=np.frombuffer(raw,dtype='<i2').astype(np.float32)[::max(1,ch*5)]
            e.append(float(np.clip(np.sqrt(np.mean(a*a))/11000,0,1)))
    return e or [0.15]
ENV=get_env(AUDIO)
def energy(t):
    return ENV[max(0,min(len(ENV)-1,int(t*10)))]


def faded_word(im,t,where):
    w=live_word(t)
    if not w:return im
    layer=word_layer(w['text'],where)
    alpha=smooth((t-w['start'])/.12)
    if t>w['end']:alpha*=max(0,1-(t-w['end'])/.24)
    if alpha>0.005:
        if alpha<.99:
            faded=layer.copy(); faded.putalpha(faded.getchannel('A').point(lambda v:int(v*alpha)))
            im=Image.alpha_composite(im.convert('RGBA'),faded).convert('RGB')
        else: im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    return im


def front_frame(t,portal=False):
    im=CLOSE.copy()
    d=ImageDraw.Draw(im)
    # Ambient city constellation in physical pegs whenever no word is active.
    if live_word(t) is None:
        for i in range(43):
            x=175+i*15;y=305+int(32*math.sin(i*.19)+5*math.sin(t*.8+i*.3))
            if y>=125:
                col=PALETTE[i%5]
                d.ellipse((x-3,y-3,x+3,y+3),fill=tuple(int(c*.72) for c in col))
    else:
        im=faded_word(im,t,'front')
    d=ImageDraw.Draw(im)
    # Physical toy heartbeat, not separate subtitle.
    amp=energy(t)
    d.ellipse((831,387,847,403),fill=(int(114+110*amp),int(90+80*amp),153))
    if portal:
        # A camera push through a luminous hole, beginning with ON and ending on SIDE.
        if t<72:at=71.614;dur=1.333
        elif t<151:at=149.374;dur=1.398
        else:at=207.788;dur=1.382
        z=smooth((t-at)/dur)
        # Cine-zoom toward the rightmost peg as text resolves.
        cropw=round(960-670*z);croph=round(540-378*z)
        cx=575;cy=242
        l=max(0,min(W-cropw,int(cx-cropw*.5)))
        top=max(0,min(H-croph,int(cy-croph*.5)))
        im=im.crop((l,top,l+cropw,top+croph)).resize((W,H),Image.Resampling.BILINEAR)
        flare=Image.new('RGB',(W,H),(255,236,245))
        im=Image.blend(im,flare,max(0,(z-.72)/.28)*.66)
    return im

DANCERS=[(RNG.randint(245,695),RNG.randint(387,453),i%5,RNG.random()*6.28,RNG.randint(11,20)) for i in range(19)]
def rave_frame(t):
    im=RAVE.copy();d=ImageDraw.Draw(im,'RGBA')
    a=energy(t)
    # Beat-driven light rays, genuinely tied to the source audio envelope.
    for i in range(10):
        x=195+i*65
        ht=int((8+60*a)*(0.5+0.5*abs(math.sin(t*3+i*1.4))))
        col=PALETTE[i%5]
        d.rounded_rectangle((x,326-ht,x+15,326),radius=5,fill=(*col,180))
    for i,(x,y,ci,phase,height) in enumerate(DANCERS):
        col=PALETTE[ci]
        wobble=math.sin(t*3.8+phase)*9
        bounce=math.sin(t*5.1+phase)*4*(.25+a)
        xx=x+wobble;yy=y+bounce
        d.ellipse((xx-6,yy-height-13,xx+6,yy-height-1),fill=(*col,252))
        d.line((xx,yy-height,xx,yy),fill=(*col,245),width=4)
        d.line((xx,yy-height+6,xx-10+wobble*.6,yy-height-4),fill=(*col,235),width=3)
        d.line((xx,yy-height+6,xx+10+wobble*.6,yy-height-5),fill=(*col,235),width=3)
        d.line((xx,yy,xx-8,yy+12),fill=(*col,235),width=3)
        d.line((xx,yy,xx+8,yy+11),fill=(*col,235),width=3)
    return faded_word(im.convert('RGB'),t,'rave')

# Dream scene just one consistent subject with flickering peg reflections.
def dream_frame(t):
    im=DREAM.copy();d=ImageDraw.Draw(im,'RGBA')
    a=energy(t)
    for i in range(33):
        x=65+(i*67)%850;y=75+(i*41)%315
        if (x-430)**2+(y-320)**2<155*155:continue
        phase=t*.7+i*2.8
        r=3+3*abs(math.sin(phase))
        col=PALETTE[i%5]
        alpha=int(60+120*(.45+.5*abs(math.sin(phase)))*(.3+a))
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*col,alpha))
    return im

def room_frame(t,awake=False,outro=False):
    if outro:
        im=ROOM_OUT.copy();d=ImageDraw.Draw(im)
        # A brief afterglow preserves the final word as memory, then one peg.
        if 226.32<=t<246.3:
            w=live_word(t)
            if w:
                col=PALETTE[1]
                d.text((728,479),w['text'].upper(),font=ff(17,True),fill=col)
        return im
    a=ROOM_A if awake else ROOM_B
    im=a.copy()
    # Gradually push toward the toy, reflecting on a consistent room layout.
    if 15<=t<=25.09:
        z=smooth((t-15)/10.09)
        cw=int(960-510*z);ch=int(540-287*z)
        cx=793;cy=338
        l=max(0,min(960-cw,round(cx-cw*.5)))
        top=max(0,min(540-ch,round(cy-ch*.5)))
        im=im.crop((l,top,l+cw,top+ch)).resize((W,H),Image.Resampling.BILINEAR)
    return im

def scene_at(t):
    idx=0
    while idx<len(SHOTS)-1 and t>=SHOTS[idx][2]:idx+=1
    return SHOTS[idx]

def frame(t):
    shot=scene_at(t);kind=shot[3]
    if kind=='bedroom_eyes_open':im=room_frame(t,awake=True)
    elif kind=='bedroom_asleep':im=room_frame(t)
    elif kind=='nightbrite_karaoke':im=front_frame(t)
    elif kind=='portal_enter':im=front_frame(t,portal=True)
    elif kind=='miniature_rave':im=rave_frame(t)
    elif kind=='sleeping_boy':im=dream_frame(t)
    elif kind=='bedroom_outro':im=room_frame(t,outro=True)
    else:raise ValueError(kind)
    # Minimal letterbox makes still-frame animation read like a short film.
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,9),fill=(5,7,18))
    d.rectangle((0,H-10,W,H),fill=(5,7,18))
    return im


def make_storyboard():
    times=[4.5,25.73,72.8,82,175,236]
    names=['01. BEDTIME','02. TOY KARAOKE','03. THE PORTAL','04. INSIDE THE RAVE','05. THE DREAM','06. ONE LAST LIGHT']
    width,height=450,253
    board=Image.new('RGB',(3*(width+22)+22,2*(height+61)+24),(17,20,35))
    d=ImageDraw.Draw(board)
    for i,(t,name) in enumerate(zip(times,names)):
        im=frame(t).resize((width,height),Image.Resampling.LANCZOS)
        x=22+(i%3)*(width+22);y=26+(i//3)*(height+61)
        board.paste(im,(x,y))
        d.text((x,y+height+10),f'{name}   •   {int(t//60):02}:{int(t%60):02}',font=ff(16,True),fill=(221,226,238))
    p=ROOT/'Nobody_Dream_Rave_Storyboard.png';board.save(p,optimize=True)
    return p


def export_manifest():
    manifest={'name':'Nobody Owns Tomorrow — Dream / Night-Brite / Rave animatic','timing_source':'Suno word-level alignment (not independently ear-verified)',
    'visuals':'Procedurally illustrated, deterministic 2.5D storyboard; zero generative-video cost','fps':FPS,'duration_seconds':DURATION,
    'characters':{'child':{'name':'Unnamed child','continuity':'dark tousled hair, left-curl tuft, medium warm skin, two freckles, teal pajamas, lavender blanket'},
                  'toy':{'name':'Night-Brite','continuity':'navy bezel, cyan/pink/gold pegs, coral dial, physical 56x13 peg array'}},
    'shots':[{'id':name.split(' / ')[0],'label':name,'start_s':start,'end_s':end,'scene':kind,'direction':description,
              'words':[{'text':w['text'],'start_s':w['start'],'end_s':w['end']} for w in words if start<=w['start']<end]} for name,start,end,kind,description in SHOTS]}
    p=ROOT/'Nobody_Dream_Rave_Semantic_Shot_Manifest.json';p.write_text(json.dumps(manifest,indent=2));return p

def render_video(out,start=0,duration=DURATION,fps=FPS):
    # Work at native frame clock; encode audio from user-supplied WAV directly.
    frames=math.ceil(duration*fps)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-video_size',f'{W}x{H}','-framerate',str(fps),'-i','pipe:0',
         '-ss',f'{start:.3f}','-i',str(AUDIO),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','ultrafast','-crf','30',
         '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t',f'{duration:.3f}','-shortest','-movflags','+faststart',str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(frames):
        t=start+i/fps
        if t>=DURATION:t=DURATION-.001
        img=frame(t)
        try:proc.stdin.write(img.tobytes())
        except BrokenPipeError:break
        if (i+1)%200==0: print(f'frame {i+1}/{frames} ({(i+1)/fps:.1f}s)',flush=True)
    try:proc.stdin.close()
    except OSError:pass
    code=proc.wait()
    if code!=0:raise RuntimeError(f'ffmpeg returned {code}')
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float,default=DURATION);p.add_argument('--fps',type=int,default=FPS);p.add_argument('--preview',action='store_true');p.add_argument('--still-only',action='store_true');args=p.parse_args()
    print('Storyboard:',make_storyboard(),flush=True)
    print('Manifest:',export_manifest(),flush=True)
    for name,t in [('bedroom',4.5),('front_lyrics',25.73),('portal',72.8),('rave',82),('dreaming',175),('outro',236)]:
        frame(t).save(ROOT/f'Nobody_Still_{name}.png',optimize=True)
    if args.still_only:sys.exit(0)
    start=args.start;dur=min(args.duration,DURATION-start)
    out=ROOT/('Nobody_Dream_Rave_Cinematic_Animatic.mp4' if not args.preview else f'Nobody_Dream_Rave_Preview_{start:.0f}s.mp4')
    print('Rendering:',out,flush=True)
    print('Done:',render_video(out,start,dur,args.fps),flush=True)
