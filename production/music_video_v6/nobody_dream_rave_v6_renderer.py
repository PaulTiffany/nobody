#!/usr/bin/env python3
"""Nobody V6 -- continuous miniature camera, fully 3D-projected party, provenance.

V6 corrections:
* Remove both legacy flat inner rave renders entirely; in every interior shot,
  use the same world, camera, characters and stage geometry.
* Portal goes directly from the actual front board to that perspective stage.
* Room-to-board lenses at 0:15..0:25.09 and 1:38..1:42.90 now sample a single
  spatially coherent HIGH-RES parent plate, instead of cross-dissolving two
  mismatched toy outlines. (The source miniature does not have geometry to
  yield literal photorealism; high-resolution close plate provides detail.)
* Distribute sprite color independently of their physical placement.
* Preserve all user's music edits and the intentional drumbeat hard cut.
* The film itself has no external-source overlay; see provenance publication kit.
"""
import os, sys, json, math, random, argparse, subprocess
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nobody_dream_rave_v5_renderer as v5
v4=v5.v4; v3=v5.v3; v2=v5.v2; base=v5.base
W,H=base.W,base.H
HERE=Path(os.environ.get('NOBODY_MEDIA_ROOT', '/mnt/data'))/'nobody_v6';HERE.mkdir(parents=True,exist_ok=True)

# Spatially decouple color from predefined room zones. The five spatial bands
# were previously exactly the same modulus as the five-color palette, yielding
# unnatural single-color neighborhoods; we preserve the actual x/y footprints.
rng=random.Random(20261107)
old=v4.ROOM_ACTORS[:]
colors=[i%5 for i in range(len(old))]
rng.shuffle(colors)
v4.ROOM_ACTORS[:]=[(x,y,sz,colors[i],phase,depth) for i,(x,y,sz,ci,phase,depth) in enumerate(old)]

# A SINGLE texture-bearing miniature in a single room. Use a static high-res
# plate and spatial camera crop -- NO image blend / duplicate casing geometry.
S=5
REGION=(706.13,278.34,193.0,108.54)

@lru_cache(maxsize=1)
def master_room():
    room=base.ROOM_B.resize((W*S,H*S),Image.Resampling.BICUBIC)
    x,y,w,h=REGION
    X,Y=int(round(x*S)),int(round(y*S)); A=int(round(w*S));B=int(round(h*S))
    tex=base.CLOSE.resize((A,B),Image.Resampling.LANCZOS)
    # Soft-edged spatial seam surrounds the *same* canonical prop. Never blend
    # in screen space: only a single physical object is sampled by the camera.
    mask=Image.new('L',(A,B),255)
    m=np.full((B,A),255,dtype=np.uint8)
    edge=4
    vx=np.minimum(np.arange(A),A-1-np.arange(A))
    vy=np.minimum(np.arange(B),B-1-np.arange(B))
    mix=np.minimum(vy[:,None],vx[None,:]).astype(np.float32)
    m=(np.minimum(1.0,mix/edge)**0.67*255).astype(np.uint8)
    mask=Image.fromarray(m,'L')
    room.paste(tex,(X,Y),mask)
    return room

# Hold the spatially matched room plate throughout the film: it replaces the
# miniature in the original source frame, rather than fading layers over it.
MASTER5=master_room()
base.ROOM_B=MASTER5.resize((W,H),Image.Resampling.BICUBIC)

def single_plate_push(t,begin,end):
    z=base.smooth((t-begin)/max(.001,end-begin))
    x,y,w,h=REGION
    l=base.lerp(0.0,x,z); top=base.lerp(0.0,y,z)
    cw=base.lerp(float(W),w,z); ch=base.lerp(float(H),h,z)
    crop=master_room().crop((round(l*S),round(top*S),round((l+cw)*S),round((top+ch)*S)))
    return crop.resize((W,H),Image.Resampling.BICUBIC)

_original_push=v2.exact_room_push
def shared_push(t,begin,end,ending=None):
    if ending=='outro':return _original_push(t,begin,end,ending)
    return single_plate_push(t,begin,end)
v2.exact_room_push=shared_push

# Direct same-geometry interior, no old v2.INSIDE and no illustrated overlay.
def true_inside(t,include_kid=False):
    for lo,hi in v5.INTERIOR_WINDOWS:
        if lo<=t<=hi+1e-6:
            return v4.perspective_stage(t,lo,hi,include_kid=include_kid)
        if hi<t<=hi+1.80:
            return v4.perspective_stage(hi-.001,lo,hi,include_kid=include_kid)
    # For any fallback, keep in 3D; never call the old flat interior.
    return v4.perspective_stage(t,73.274,92.785,include_kid=include_kid)
v5.unified_inside_world=true_inside
v3.inside_world=true_inside

# Portal destination is now the same perspective scene at the next timestamp.
# Magnification on the physical pegboard continues until a soft radial
# aperture reveals the world behind the single glowing peg.
PORTALS=[(71.614,73.274),(149.374,151.094),(207.788,209.797)]

def lens_portal(t,start,end):
    frac=base.smooth((t-start)/max(.01,end-start))
    front=v3.chorus_front(t)
    cx,cy=577.,242.
    lens=1+5.1*frac
    cropw=W/lens;croph=H/lens
    # Center remains aligned with a real peg on the toy face.
    l=max(0,min(W-cropw,cx-cropw/2)); top=max(0,min(H-croph,cy-croph/2))
    front=front.crop((round(l),round(top),round(l+cropw),round(top+croph))).resize((W,H),Image.Resampling.BICUBIC)
    hi=end+0.001
    b=true_inside(hi, include_kid=(start>200))
    # Reveal becomes radial after the camera starts passing through the peg.
    a=base.smooth((frac-.36)/.64)
    if a<=0:return front
    if a>=.999:return b
    yy,xx=np.ogrid[:H,:W]
    r=np.sqrt(((xx-W*.5)/(W*.5))**2+((yy-H*.5)/(H*.5))**2)
    radius=1.56*(a**1.06)
    soft=.18
    alpha=np.clip((radius-r)/soft,.0,1.0)
    mask=Image.fromarray((255*alpha).astype('uint8'),'L')
    return Image.composite(b,front,mask)

# We do not reroute V2 portal for 'bridge exit' (the user's designed return
# from back to front is a separate scene, not a new rave entry).
_v5_frame=v5.frame

def frame(t):
    key=v3.scene_at(t)[3]
    if key=='push':im=single_plate_push(t,15,25.09)
    elif key=='room_push':im=single_plate_push(t,98,102.903)
    elif key=='portal':
        p=next((s,e) for s,e in PORTALS if s<=t<=e) if any(s<=t<=e for s,e in PORTALS) else min(PORTALS,key=lambda p:abs(t-p[0]))
        im=lens_portal(t,*p)
    elif key=='verse_icons' and 25.09<=t<25.86:
        # The close texture at push completion matches the next still exactly.
        fresh=v4.frame(t)
        im=Image.blend(base.CLOSE.copy(),fresh,base.smooth((t-25.09)/.77))
    else:
        im=_v5_frame(t)
    # The preceding layer already contains consistent letterbox bars for
    # regular shots; normalize custom shots identically.
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,9),fill=(5,7,18));d.rectangle((0,H-10,W,H),fill=(5,7,18))
    return im
v3.frame=frame
base.frame=frame

def save_storyboard():
    picks=[(4,'Boy in bed'),(18,'Single miniature plate'),(23.0,'One casing in zoom'),(25.12,'Same toy, verses'),
           (56,'Chorus karaoke'),(72.0,'Into physical peg'),(73.28,'3D dance floor'),(79,'Same room, still'),
           (85.8,'3D orbit'),(90.5,'3D return'),(93.9,'Dream zoom-out'),(101.4,'Return to night-brite'),
           (149.7,'Second portal'),(154,'Second interior 3D'),(164,'Second fly-around'),
           (190,'Kid eye shock'),(212,'Kid dances inside'),(220.0,'Final orbital move'),
           (231,'Sprites in bedroom'),(245,'Mixed window lights'),(258,'Other dreamers')]
    tw,th=304,171;foot=24;gap=12;cols=3
    rows=math.ceil(len(picks)/cols)
    board=Image.new('RGB',(gap+cols*(tw+gap),gap+rows*(th+foot+gap)),(7,12,28));d=ImageDraw.Draw(board)
    for i,(t,label) in enumerate(picks):
        shot=frame(t).resize((tw,th),Image.Resampling.BILINEAR)
        x=gap+(i%cols)*(tw+gap);y=gap+(i//cols)*(th+foot+gap)
        board.paste(shot,(x,y))
        d.text((x+3,y+th+3),f'{int(t//60)}:{t%60:05.2f}  {label}',fill=(231,232,249))
    output=HERE/'Nobody_V6_Storyboard.jpg';board.save(output,quality=85,optimize=True)
    return output

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--start',type=float,default=0)
    ap.add_argument('--duration',type=float,default=base.DURATION)
    ap.add_argument('--fps',type=int,default=10)
    ap.add_argument('--crf',type=int,default=37)
    ap.add_argument('--lite',action='store_true')
    ap.add_argument('--stills-only',action='store_true')
    args=ap.parse_args()
    print('storyboard',save_storyboard(),flush=True)
    if args.stills_only:exit()
    out=HERE/('Nobody_V6_COMPLETE_WITH_AUDIO.mp4' if args.start==0 and args.duration>=base.DURATION else f'Nobody_V6_TEST_{args.start:.2f}_{args.duration:.2f}.mp4')
    dur=min(args.duration,base.DURATION-args.start)
    print('rendering',str(out),flush=True)
    v3.render(out,args.start,dur,fps=args.fps,size='lite' if args.lite else 'full',crf=args.crf)
    print('ready',str(out),out.stat().st_size,flush=True)
