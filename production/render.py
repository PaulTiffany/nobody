#!/usr/bin/env python3
"""Deterministic, zero-API, Pillow/FFmpeg Lite-Brite karaoke concept renderer.

All pixels derive from the audio time t and a fixed procedural seed. No remote
services, models, generated assets, or scene state are required.
"""
import argparse
from array import array
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
W, H = 960, 540
FPS = 20
PALETTE = [(67, 233, 249), (255, 95, 164), (255, 205, 105), (148, 115, 255), (109, 249, 167)]
RNG = random.Random(2407)
STARS = [(RNG.randrange(W), RNG.randrange(H-100), RNG.uniform(.25, 1.9), RNG.random()*6.28) for _ in range(90)]
PEGS = []
for gy in range(13):
    for gx in range(29):
        # City towers plus atmosphere; all geometry is generated from this fixed seed.
        tower = [3, 7, 6, 11, 8, 5, 10, 7, 4, 12, 7, 9, 6, 8, 4, 10, 7, 5, 11, 6, 8, 5, 10, 7, 12, 6, 9, 5, 3][gx]
        lit = (gy >= 13 - tower and RNG.random() > .19) or (gy < 6 and RNG.random() < .045)
        PEGS.append((gx, gy, lit, RNG.randrange(len(PALETTE)), RNG.uniform(.8, 1.2)))
DANCERS = [(RNG.uniform(.09, .91), RNG.uniform(.61, .82), RNG.randrange(len(PALETTE)), RNG.uniform(0, 6.28)) for _ in range(32)]

def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def mix(a, b, f): return a + (b-a)*clamp(f)
def smooth(f):
    f=clamp(f)
    return f*f*(3-2*f)

def font(size, bold=False):
    candidates = (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"])
    for path in candidates:
        if Path(path).is_file(): return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def centered(draw, text, y, fnt, fill, stroke_width=0, stroke_fill=None):
    box = draw.textbbox((0,0), text, font=fnt, stroke_width=stroke_width)
    x = (W - (box[2]-box[0]))//2
    draw.text((x,y), text, font=fnt, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill, anchor="la")

def audio_envelope(path, start, duration):
    """Analyze just the selected PCM16 WAV excerpt; no model inference."""
    with wave.open(str(path), "rb") as wav:
        if wav.getsampwidth() != 2 or wav.getcomptype() != "NONE":
            raise ValueError("Input must be uncompressed PCM16 WAV (convert with FFmpeg first)")
        rate, ch = wav.getframerate(), wav.getnchannels()
        wav.setpos(min(int(start*rate), wav.getnframes()))
        out=[]
        window=max(1,int(.05*rate))
        for _ in range(math.ceil(duration/.05)+5):
            payload = wav.readframes(window)
            if not payload:
                out.append(0.0)
                continue
            samps=array('h')
            samps.frombytes(payload)
            subs=samps[::max(1,ch*12)]  # Subsample for fast deterministic envelope.
            rms=math.sqrt(sum(v*v for v in subs)/max(1,len(subs)))/32768.0
            out.append(clamp(rms*3.2))
        return out

def signal(env,t): return env[min(len(env)-1,max(0,int(t/.05)))] if env else .25

def gradient():
    im=Image.new('RGB',(W,H))
    d=ImageDraw.Draw(im)
    for y in range(H):
        k=y/H
        d.line((0,y,W,y), fill=(int(mix(7,18,k)),int(mix(12,9,k)),int(mix(36,54,k))))
    return im
BG = gradient()

def glowdots(canvas, points, blur=8):
    layer=Image.new('RGBA',(W,H),(0,0,0,0))
    d=ImageDraw.Draw(layer,'RGBA')
    for x,y,r,color,alpha in points:
        if x < -25 or y < -25 or x > W+25 or y > H+25: continue
        d.ellipse((x-r*2.5,y-r*2.5,x+r*2.5,y+r*2.5),fill=(*color,int(alpha*50)))
    canvas.paste(Image.alpha_composite(canvas.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(blur))).convert('RGB'))
    return canvas

def draw_front(t, energy, transition, show_tag=True):
    canvas=BG.copy()
    d=ImageDraw.Draw(canvas,'RGB')
    pan=18*math.sin(t*.31)
    for x,y,size,phase in STARS:
        xx=x+pan*size*.25
        alpha=clamp(.3+.45*math.sin(t*.9+phase))
        v=int(85+115*alpha)
        d.ellipse((xx-size,y-size,xx+size,y+size),fill=(int(.5*v),int(.76*v),v))
    # Desk silhouette gives the physically located toy some scale.
    d.polygon([(0,451),(W,433),(W,H),(0,H)],fill=(8,7,22))
    # Independently rendered toy layer, for actual affine parallax and lens-push.
    toy=Image.new('RGBA',(840,426),(0,0,0,0))
    p=ImageDraw.Draw(toy,'RGBA')
    p.rounded_rectangle((65,14,776,400),radius=31,fill=(15,18,38,255),outline=(96,110,151,255),width=5)
    p.rounded_rectangle((84,32,754,379),radius=18,fill=(5,8,25,255),outline=(40,47,87,255),width=4)
    for gx,gy,lit,ci,variation in PEGS:
        x=110+gx*22
        y=67+gy*22
        p.ellipse((x-3,y-3,x+3,y+3),fill=(30,35,64,255))
    bulb=Image.new('RGBA',toy.size,(0,0,0,0)); b=ImageDraw.Draw(bulb,'RGBA')
    for gx,gy,lit,ci,variation in PEGS:
        if not lit: continue
        x=110+gx*22; y=67+gy*22
        color=PALETTE[ci]
        flick= .82+.17*math.sin(t*(1+ci*.15)+gx*.8+gy*.42)
        radius=(3.5+1.7*energy)*variation
        b.ellipse((x-radius*2.6,y-radius*2.6,x+radius*2.6,y+radius*2.6), fill=(*color,int(50*flick)))
        p.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*color,255))
        p.ellipse((x-radius*.42,y-radius*.5,x+radius*.42,y+radius*.2),fill=(245,250,255,200))
    toy=Image.alpha_composite(toy,bulb.filter(ImageFilter.GaussianBlur(9)))
    # Crisp peg faces on top of halation.
    p=ImageDraw.Draw(toy,'RGBA')
    for gx,gy,lit,ci,variation in PEGS:
        if not lit: continue
        x=110+gx*22; y=67+gy*22
        r=3.6*variation
        p.ellipse((x-r,y-r,x+r,y+r),fill=(*PALETTE[ci],250))
        p.ellipse((x-1.3,y-2.1,x+.5,y-.1), fill=(255,255,255,220))
    p.text((421,389),"N O B O D Y   O W N S   T O M O R R O W",anchor="mm",font=font(14,True),fill=(176,180,209,255))
    zoom=1.0 + .019*math.sin(t*.38)
    if t >= transition - 1.0: zoom *= mix(1,5.1,smooth((t-(transition-1.0))/.98))
    # Rotate a little while diving into the board's lit acrylic.
    destw=int(840*zoom); desth=int(426*zoom)
    destw=max(1,destw); desth=max(1,desth)
    toy=toy.resize((destw,desth),Image.Resampling.BILINEAR)
    # Lens aim at 58%-width / 46%-height of the unscaled object.
    anchor=(.58,.46)
    ox=int(W*.5-anchor[0]*destw+pan*.28)
    oy=int(H*.47-anchor[1]*desth+8*math.sin(t*.2))
    canvas.paste(toy,(ox,oy),toy)
    # Small desk reflections and retro title.
    if show_tag and t < transition - .95:
        d=ImageDraw.Draw(canvas,'RGBA')
        d.text((32,24),"01  /  THE PICTURE",font=font(17,True), fill=(151,194,219,230))
        d.line((31,52,233,52),fill=(93,167,181,120),width=2)
    return canvas

def draw_back(t, energy, show_tag=True):
    canvas=BG.copy()
    d=ImageDraw.Draw(canvas,'RGBA')
    amp=.4+.8*energy
    # Receding circuit-board architecture; two independently moving depth layers.
    for layer in range(3):
        step=80+layer*28
        shift=math.sin(t*(.2+layer*.12))*18*(layer+1)
        for x in range(-step, W+step,step):
            xx=x+shift
            col=(52+layer*13,65,132+layer*20, 95)
            d.line((W//2+shift*.1,63, xx,500),fill=col,width=max(1,3-layer))
    d.ellipse((218,75,742,450),fill=(40,16,85,45),outline=(255,85,166,95),width=4)
    for i in range(10):
        angle=i*math.tau/10+t*.11
        ex=W/2+math.cos(angle)*300
        ey=H*.46+math.sin(angle)*155
        color=PALETTE[i%len(PALETTE)]
        d.line((W//2,170,ex,ey),fill=(*color,int(60+80*energy)),width=7 if i%2==0 else 3)
    # Floor grid in forced perspective.
    horizon=348
    d.rectangle((0,horizon,W,H),fill=(10,6,31,235))
    for i in range(-10,11):
        x=W//2+i*75
        d.line((W//2,horizon,x,H),fill=(43,133,181,135),width=2)
    for row in range(1,9):
        yy=horizon+int((row/9)**1.5*(H-horizon))
        d.line((0,yy,W,yy),fill=(47,105,166,115),width=2)
    # Speakers are clearly the reverse electronics of the front board.
    for x in (77,W-77):
        d.rounded_rectangle((x-57,220,x+57,412),radius=15,fill=(16,22,43,255),outline=(85,164,188,230),width=5)
        for y,rad in ((283,32),(366,20)):
            kick=rad+5*energy
            d.ellipse((x-kick,y-kick,x+kick,y+kick),outline=(*PALETTE[1],255),width=5)
            d.ellipse((x-rad*.47,y-rad*.47,x+rad*.47,y+rad*.47),fill=(44,28,77,255))
    # Glow behind the dancers, distinct from their sharp silhouettes.
    gl=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl,'RGBA')
    for idx,(nx,ny,ci,phase) in enumerate(DANCERS):
        xx=nx*W+9*math.sin(t*(2+ci*.2)+phase)
        yy=ny*H+8*math.sin(t*(2.8+idx*.03)+phase)
        gd.ellipse((xx-14,yy-14,xx+14,yy+14),fill=(*PALETTE[ci],140))
    gl=gl.filter(ImageFilter.GaussianBlur(17))
    canvas=Image.alpha_composite(canvas.convert('RGBA'),gl).convert('RGB')
    d=ImageDraw.Draw(canvas,'RGBA')
    for idx,(nx,ny,ci,phase) in enumerate(DANCERS):
        xx=nx*W+9*math.sin(t*(2+ci*.2)+phase)
        yy=ny*H+8*math.sin(t*(2.8+idx*.03)+phase)
        col=PALETTE[ci]
        wobble=8*math.sin(t*3.3+phase)
        d.line((xx,yy+6,xx+wobble,yy+23),fill=(*col,245),width=5)
        d.line((xx,yy+6,xx-wobble,yy+25),fill=(*col,245),width=5)
        d.line((xx,yy+5,xx-10*math.sin(t*2.7+phase),yy-9),fill=(*col,240),width=4)
        d.line((xx,yy+5,xx+10*math.sin(t*2.7+phase),yy-12),fill=(*col,240),width=4)
        d.ellipse((xx-7,yy-16,xx+7,yy-2),fill=(*col,255))
    # Large audio-reactive central equalizer, behind the karaoke.
    for i in range(28):
        x=247+i*17
        level=(.3+.7*(.5+.5*math.sin(i*.8+t*4.2)))*(20+85*energy)
        d.rounded_rectangle((x,350-level,x+9,350),radius=4,fill=(*PALETTE[i%5],int(130+100*amp/1.2)))
    if show_tag:
        d.text((35,22),"02  /  THE OTHER SIDE",font=font(17,True),fill=(255,205,211,255))
        d.line((35,50,279,50),fill=(244,94,166,180),width=2)
    return canvas

def lyrics(canvas,t,cues,after):
    # A progress indicator, not claimed automatic word-level transcription.
    active=None
    for entry in cues:
        if entry['start'] <= t < entry['end']:
            active=entry
            break
    d=ImageDraw.Draw(canvas,'RGBA')
    d.rounded_rectangle((112,450,848,514),radius=20,fill=(5,10,28,226),outline=(102,133,172,100),width=2)
    if active:
        progress=clamp((t-active['start'])/(active['end']-active['start']))
        text=active['text'].upper()
        fnt=font(32 if len(text)<34 else 27,True)
        width=d.textbbox((0,0),text,font=fnt)[2]
        x=(W-width)//2
        d.text((x,464),text,font=fnt,fill=(214,220,235,255))
        # Fill left-to-right clipping as a karaoke timing study, avoiding word-sync claims.
        overlay=Image.new('RGBA',(W,H),(0,0,0,0))
        od=ImageDraw.Draw(overlay)
        od.text((x,464),text,font=fnt,fill=PALETTE[1 if after else 0]+(255,))
        mask=Image.new('L',(W,H),0)
        md=ImageDraw.Draw(mask)
        md.rectangle((x,456,x+int(width*progress),510),fill=255)
        canvas.paste(overlay,(0,0),mask)
    else:
        centered(d,"( O O H  —  O N   T H E   O T H E R   S I D E )",468,font(19,True),(174,184,224,235))
    d.text((W-293,H-13),"CONCEPT CUT  ·  LYRIC TIMING PROVISIONAL",font=font(11),fill=(145,148,184,220))
    return canvas

def frame(t, transition, env, cues):
    amp=signal(env,t)
    # The transition is a single time-evaluated, deterministic gate.
    if t < transition:
        im=draw_front(t,amp,transition)
    else:
        im=draw_back(t-transition,amp)
    if transition-.15 < t < transition+.22:
        fade=1-abs(t-transition)/.22
        alpha=int(225*clamp(fade))
        im=Image.blend(im,Image.new('RGB',(W,H),(244,245,253)),alpha/255)
    return lyrics(im,t,cues,after=(t>=transition))

def render(args):
    wav=Path(args.wav).resolve()
    if not wav.exists(): raise FileNotFoundError(f"Audio missing: {wav}")
    if args.duration<=0 or args.fps<=0 or args.start<0: raise ValueError("Invalid timing")
    cues=json.loads(Path(args.cues).read_text(encoding='utf-8'))['preview_cues']
    env=audio_envelope(wav,args.start,args.duration)
    out=Path(args.out).resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    # Stream video frames through FFmpeg; no scratch images, no GPU/API calls.
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y',
         '-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}',
         '-framerate',str(args.fps),'-i','pipe:0',
         '-ss',str(args.start),'-t',str(args.duration),'-i',str(wav),
         '-map','0:v:0','-map','1:a:0',
         '-c:v','libx264','-preset','veryfast','-crf',str(args.crf),
         '-pix_fmt','yuv420p','-c:a','aac','-b:a','128k',
         '-movflags','+faststart','-shortest',str(out)]
    try:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for k in range(round(args.duration*args.fps)):
            im=frame(k/args.fps,args.transition,env,cues)
            p.stdin.write(im.tobytes())
        p.stdin.close()
        result=p.wait()
    except BrokenPipeError:
        result=p.wait()
    if result: raise RuntimeError(f'FFmpeg exited with code {result}')
    print(f"Rendered {out} | {args.duration:.2f}s | {args.fps} fps | from {wav.name} at {args.start:.2f}s")

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wav',required=True,help='Your local, licensed, PCM16 WAV file (never committed)')
    ap.add_argument('--start',type=float,default=0)
    ap.add_argument('--duration',type=float,default=14)
    ap.add_argument('--transition',type=float,default=8,help='local clip seconds to board pass-through')
    ap.add_argument('--fps',type=int,default=FPS)
    ap.add_argument('--crf',type=int,default=29)
    ap.add_argument('--cues',default=str(ROOT/'production/cues.json'))
    ap.add_argument('--out',default=str(ROOT/'output/other-side-preview.mp4'))
    render(ap.parse_args())
