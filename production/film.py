#!/usr/bin/env python3
"""Full-length, timeline-driven Artilect video renderer.

No speech-recognition/forced alignment is implied: lyrics_draft.json contains
inferred phrase regions, which require creator listening before publication.
The video is deterministic at an absolute audio time (even across chunked runs).
"""
import argparse
from bisect import bisect_right
import json
import math
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import render as core

ROOT=Path(__file__).resolve().parents[1]
W,H=core.W,core.H
FPS=16
DURATION=263.24
PALETTE=core.PALETTE
FRONT_TO_BACK=95.0
BACK_TO_FRONT=240.2


def load_timeline(path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    cues=data['cues']
    if not cues: raise ValueError('Empty lyric timeline')
    if any(c['start']>=c['end'] for c in cues): raise ValueError('Bad start/end cue')
    if any(c['end']>data['audio_duration_seconds']+.01 for c in cues):raise ValueError('Lyric cue extends past audio')
    if any(a['end']>b['start'] for a,b in zip(cues,cues[1:])):raise ValueError('Overlapping lyric cues')
    sections=data['sections']
    if abs(sections[0]['start'])>.001 or abs(sections[-1]['end']-data['audio_duration_seconds'])>.001:
        raise ValueError('Storyboard does not cover full track')
    if any(abs(a['end']-b['start'])>.001 for a,b in zip(sections,sections[1:])):
        raise ValueError('Storyboard has gaps')
    return data


def get_active(t,cues):
    starts=[c['start'] for c in cues]
    i=bisect_right(starts,t)-1
    if i>=0 and t<cues[i]['end']: return cues[i]
    return None


def chapter(t,sections):
    for s in sections:
        if s['start']<=t<s['end']: return s['name']
    return sections[-1]['name']


def draw_refracted_overlay(img,t,energy,origin=(480,255),vivid=False):
    im=img.convert('RGBA')
    overlay=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(overlay,'RGBA')
    phase=t*1.7
    cx,cy=origin
    for n in range(9):
        r=22+n*36+16*math.sin(phase*.35+n*.36)
        col=PALETTE[(n+2)%5]
        d.ellipse((cx-r*1.32,cy-r*.68,cx+r*1.32,cy+r*.68),outline=(*col,int(32+energy*44 if vivid else 22+energy*18)),width=4 if n%3==0 else 2)
    for n in range(25):
        ang=n*2.39996+t*.05
        radius=17+(n*31)%355
        x=cx+radius*math.cos(ang)
        y=cy+radius*.64*math.sin(ang)
        r=1.5+1.8*energy
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*PALETTE[n%5],180))
    return Image.alpha_composite(im,overlay).convert('RGB')


def scene(t,energy):
    if t < FRONT_TO_BACK:
        im=core.draw_front(t,energy,FRONT_TO_BACK,show_tag=False)
        if t>FRONT_TO_BACK-1.2:
            f=core.smooth((t-(FRONT_TO_BACK-1.2))/1.2)
            # The forward rush becomes a rainbow diffraction before the cut.
            im=draw_refracted_overlay(im,t,energy,vivid=True)
            im=Image.blend(im,Image.new('RGB',(W,H),(240,232,255)),min(.81,f*.74))
        return im,'front'
    if t < 184:
        im=core.draw_back(t-FRONT_TO_BACK,energy,show_tag=False)
        if t<FRONT_TO_BACK+.5:
            f=core.smooth((t-FRONT_TO_BACK)/.5)
            im=Image.blend(Image.new('RGB',(W,H),(238,236,255)),im,f)
        return im,'back'
    if t < 210:
        # Quiet bridge: the lights remain alive but the rave recedes into
        # an introspective, slowly rotating tunnel.
        im=core.draw_back(t-FRONT_TO_BACK,energy*.52,show_tag=False)
        im=Image.blend(im,core.BG,.25)
        im=draw_refracted_overlay(im,t,energy,vivid=True)
        return im,'bridge'
    if t < BACK_TO_FRONT:
        im=core.draw_back(t-FRONT_TO_BACK,energy,show_tag=False)
        # Brief apertures reveal the FRONT and REVERSE are the same system.
        # Blend only near major musical turns, keeping the rest legible.
        if (211<t<216) or (231<t<236):
            f= .31+.27*math.sin(t*.63)
            im=Image.blend(im,core.draw_front(t,energy,10000,show_tag=False),f)
        return im,'together'
    im=core.draw_front(t,energy,10000,show_tag=False)
    if t<BACK_TO_FRONT+.6:
        f=core.smooth((t-BACK_TO_FRONT)/.6)
        im=Image.blend(Image.new('RGB',(W,H),(236,233,255)),im,f)
    if t>259:
        # The deliberately isolated last peg switches on as the music dies.
        k=core.smooth((t-260.0)/1.9)
        d=ImageDraw.Draw(im,'RGBA')
        cx,cy=482,151
        for r,alpha in [(43,int(18*k)),(24,int(65*k)),(10,int(140*k)),(4,int(240*k))]:
            d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,222,118,alpha))
    return im,'outro'


def lyric_overlay(im,t,cues,sections,mode,unverified=True):
    d=ImageDraw.Draw(im,'RGBA')
    active=get_active(t,cues)
    sec=chapter(t,sections)
    # Top UI is quiet and visibly separated from the song typography.
    d.rounded_rectangle((31,21,350,56),radius=11,fill=(5,11,32,190),outline=(96,158,177,85),width=1)
    d.text((44,29), 'NOBODY  /  '+sec, font=core.font(15,True),fill=(176,221,236,240))
    if active:
        phrase=active['text'].upper()
        progress=core.clamp((t-active['start'])/(active['end']-active['start']))
        # Maintain a readable single karaoke line with contrasting text.
        maxw=750
        size=35
        while size>18 and d.textbbox((0,0),phrase,font=core.font(size,True))[2]>maxw:size-=1
        f=core.font(size,True)
        w=d.textbbox((0,0),phrase,font=f)[2]
        x=(W-w)//2
        y=455+max(0,(35-size)//2)
        d.rounded_rectangle((max(35,x-28),439,min(W-35,x+w+28),508),radius=15,fill=(4,9,29,225),outline=(119,152,189,140),width=2)
        d.text((x+2,y+2),phrase,font=f,fill=(21,22,43,245))
        d.text((x,y),phrase,font=f,fill=(194,205,225,250))
        lyr=Image.new('RGBA',(W,H))
        ld=ImageDraw.Draw(lyr,'RGBA')
        ld.text((x,y),phrase,font=f,fill=(*PALETTE[0 if mode=='front' else 1],255))
        mask=Image.new('L',(W,H)); md=ImageDraw.Draw(mask)
        md.rectangle((x,y-3,x+int(w*progress),y+size+15),fill=255)
        im.paste(lyr,(0,0),mask)
    else:
        if t<14: phrase='(  OOH  ·  OOH  ·  OOH  )'
        elif 95<=t<110: phrase='✦   THE OTHER SIDE   ✦'
        elif 183<=t<191: phrase='(  THE LIGHTS KEEP DANCING  )'
        else: phrase='(  OOH  ·  ON THE OTHER SIDE  )'
        w=d.textbbox((0,0),phrase,font=core.font(24,True))[2]
        d.rounded_rectangle(((W-w)//2-27,444,(W+w)//2+27,507),radius=14,fill=(5,10,30,202))
        d.text(((W-w)//2,464),phrase,font=core.font(24,True),fill=(186,204,227,250))
    d=ImageDraw.Draw(im,'RGBA')
    # Track progress and section marks: waveform-following visuals are not
    # represented as automatic lyric recognition.
    d.rounded_rectangle((30,520,930,524),radius=2,fill=(77,90,129,180))
    d.rounded_rectangle((30,520,30+900*core.clamp(t/DURATION),524),radius=2,fill=(99,233,245,255))
    for s in sections[1:]:
        x=30+int(900*s['start']/DURATION)
        d.rectangle((x-1,519,x+1,525),fill=(244,181,207,235))
    if unverified:
        d.text((632,31),'DRAFT • CUE ALIGNMENT UNVERIFIED',font=core.font(11),fill=(219,169,188,220))
    return im



def check_word_alignment(data, require_complete=False):
    """Reject synthetic/proportional 'karaoke' timings masquerading as sung words.

    This is a schema and provenance gate, NOT an acoustic accuracy test.
    """
    if require_complete and data.get('status') != 'VERIFIED_BY_CREATOR':
        raise ValueError('Full karaoke requires status VERIFIED_BY_CREATOR after listening and review')
    for i, cue in enumerate(data['cues']):
        if require_complete and cue.get('verified') is not True:
            raise ValueError(f'Cue {i+1}: line not reviewed against sung audio')
        if cue.get('verified') is not True:
            continue
        words=cue.get('words',[])
        tokens=cue['text'].split()
        if not words: 
            if require_complete: raise ValueError(f'Cue {i+1}: no word timings')
            continue
        if len(words)!=len(tokens) or [w['text'] for w in words]!=tokens:
            raise ValueError(f'Cue {i+1}: timed words do not match the sung-text transcription')
        prev=cue['start']
        for j,word in enumerate(words):
            a,b=word.get('start'),word.get('end')
            if not (isinstance(a,(int,float)) and isinstance(b,(int,float))
                    and cue['start']-.25 <= a < b <= cue['end']+.25 and a>=prev-.01):
                if require_complete:
                    raise ValueError(f'Cue {i+1}, word {j+1}: invalid onset/offset')
                break
            if require_complete and word.get('verified') is not True:
                raise ValueError(f'Cue {i+1}, word {j+1}: word not reviewed')
            prev=a


def aligned_lyric_overlay(im,t,data,mode,full=False):
    """Only display manually checked lines. Do not synthesize cue timings."""
    active=get_active(t,data['cues'])
    if not active or active.get('verified') is not True:
        return im
    phrase=active['text'].upper()
    d=ImageDraw.Draw(im,'RGBA')
    size=35
    while size>17 and d.textbbox((0,0),phrase,font=core.font(size,True))[2]>820:size-=1
    f=core.font(size,True)
    w=d.textbbox((0,0),phrase,font=f)[2]
    x=(W-w)//2
    y=458
    d.rounded_rectangle((max(20,x-27),440,min(W-20,x+w+27),511),radius=15,
                        fill=(5,9,30,230),outline=(116,154,183,180),width=2)
    d.text((x,y),phrase,font=f,fill=(215,222,239,255))
    color=(*PALETTE[0 if mode=='front' else 1],255)
    words=active.get('words',[])
    if words and len(words)==len(phrase.split()):
        # Every word gets its own measured time window. There is no linear sweep
        # across the whole phrase. At onset the word begins to illuminate.
        cursor=x
        for word in words:
            token=word['text'].upper()
            left=cursor
            width=d.textlength(token,font=f)
            cursor+=d.textlength(token+' ',font=f)
            if word.get('verified') and t>=word['start']:
                progress=core.clamp((t-word['start'])/max(.03,word['end']-word['start']))
                highlight=Image.new('RGBA',(W,H))
                ImageDraw.Draw(highlight,'RGBA').text((left,y),token,font=f,fill=color)
                mask=Image.new('L',(W,H))
                ImageDraw.Draw(mask).rectangle((int(left),y-3,int(left+width*progress),y+size+12),fill=255)
                im.paste(highlight,(0,0),mask)
    # Visibility of the QA watermark prevents a partially synced preview
    # from being mistaken for a certified performance.
    if not full:
        d=ImageDraw.Draw(im,'RGBA')
        d.text((560,25),'ALIGNMENT REVIEW / VERIFIED LINES ONLY',font=core.font(13),fill=(255,208,223,255))
    return im

def wav_signal(path,start,duration):
    # Works on arbitrary absolute excerpts; respects local PCM envelope.
    return core.audio_envelope(path,start,duration)


def film_frame(t,env,start,data,karaoke='off'):
    energy=core.signal(env,t-start)
    im,mode=scene(t,energy)
    if karaoke=='off':
        return im
    if karaoke=='draft':
        return lyric_overlay(im,t,data['cues'],data['sections'],mode)
    return aligned_lyric_overlay(im,t,data,mode,full=(karaoke=='verified'))


def main(args):
    wav=Path(args.wav).resolve();out=Path(args.out).resolve()
    timeline=load_timeline(args.cues)
    if args.karaoke=='verified':
        check_word_alignment(timeline,require_complete=True)
    elif args.karaoke=='review':
        check_word_alignment(timeline,require_complete=False)
    if not wav.is_file(): raise FileNotFoundError(wav)
    if not(0<=args.start<DURATION) or args.duration<=0 or args.start+args.duration>DURATION+.03:
        raise ValueError('Invalid audio excerpt timing')
    env=wav_signal(wav,args.start,args.duration)
    out.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo',
         '-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(args.fps),
         '-i','pipe:0','-ss',str(args.start),'-t',str(args.duration),'-i',str(wav),
         '-map','0:v','-map','1:a','-c:v','libx264','-preset',args.preset,
         '-crf',str(args.crf),'-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',
         '-movflags','+faststart','-shortest',str(out)]
    pipe=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for frame in range(round(args.duration*args.fps)):
            t=args.start+frame/args.fps
            if args.progress and frame%args.fps==0: print(f"frame at {t:.1f}s",flush=True)
            rgb=film_frame(t,env,args.start,timeline,args.karaoke)
            pipe.stdin.write(rgb.tobytes())
    except BrokenPipeError:
        raise RuntimeError(f'FFmpeg stopped prematurely: {pipe.poll()}')
    finally:
        try:pipe.stdin.close()
        except BrokenPipeError:pass
    if pipe.wait()!=0:raise RuntimeError(f'FFmpeg failed: {pipe.returncode}')
    print(f'OK: {out}, start {args.start:.2f}, duration {args.duration:.2f} sec, {args.fps} fps')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--wav',required=True)
    p.add_argument('--cues',default=str(ROOT/'production/lyrics_draft.json'))
    p.add_argument('--out',default=str(ROOT/'output/full-draft.mp4'))
    p.add_argument('--start',type=float,default=0)
    p.add_argument('--duration',type=float,default=DURATION)
    p.add_argument('--fps',type=int,default=FPS)
    p.add_argument('--preset',default='veryfast')
    p.add_argument('--crf',type=int,default=29)
    p.add_argument('--karaoke',choices=['off','review','verified','draft'],default='off',
                   help='off=honest visual-only film; review=checked lines; verified=fully checked words; draft=UNVERIFIED legacy')
    p.add_argument('--progress',action='store_true')
    main(p.parse_args())
