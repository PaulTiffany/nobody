#!/usr/bin/env python3
"""Nobody Owns Tomorrow — V4, director-feedback revision.

Real 3-D perspective/projection of 2-D sprite puppets during electronic-trill
flythroughs, plus room dream continuity, organic many-sprite ending, independent
window light colors, earlier peg karaoke onset. Pillow + numpy + ffmpeg; no
paid video inference. Word onset provenance: Suno alignment; not ear-certified.
"""
import argparse, json, math, random, sys
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import nobody_dream_rave_v3_renderer as v3

base=v3.base; v2=v3.v2; W,H=base.W,base.H
ROOT=Path(__import__('os').environ.get('NOBODY_MEDIA_ROOT', '/mnt/data'))
OUT=ROOT/'nobody_v4_work'; OUT.mkdir(exist_ok=True)
PAL=base.PALETTE

# Visual pre-roll, not audio retiming: keep actual Sung boundaries intact.
LYRIC_ANTICIPATION_S=.32
for word in base.words: word['start'] = max(0.0,word['start']-LYRIC_ANTICIPATION_S)
base.starts=[w['start'] for w in base.words]

# Add restrained physical peg animations to chorus, never subtitle overlays.
_v3_chorus=v3.chorus_front
def chorus_front(t):
    im=_v3_chorus(t)
    word=base.live_word(t)
    if not word:return im
    token=word['text'].lower().strip(' ,.!?')
    d=ImageDraw.Draw(im,'RGBA')
    beat=base.energy(t)
    u=v3.window_ease(t,word['start'],max(word['start']+.2,word['end']))
    # Corner miniatures that do not obscure karaoke letters.
    if token in {'tomorrow','sky','world','alive','reason'}:
        for i in range(7):
            aa=(i/7)*math.tau+t*.7
            x=6+int(3.4*math.cos(aa)); y=2+int(2*math.sin(aa))
            v3.draw_peg(d,x,y,PAL[(i+2)%5],r=2.0+u,alpha=int(145+70*beat))
    elif token in {'everyone','side','other'}:
        for i in range(7):
            x=45+i; y=9-int(3*u+2*math.sin(t*2.2+i*.6))
            v3.draw_peg(d,x,y,PAL[i%5],r=2.1,alpha=170)
    return im
v3.chorus_front=chorus_front

# Actual perspective camera used to project a volumetric stage and cutout people.
# Up = y; viewer looks from +z toward the Night-Brite rear circuit plane (z=-2.2).
VUP=np.array([0.,1.,0.],dtype=float)

def cam_state(t,a,b):
    u=max(0.,min(1.,(t-a)/(b-a)))
    s=v3.window_ease(t,a,b)
    # Three phases: approach, orbit, leave. Not a crop-pan: true changing
    # viewpoint rotates all objects, foreshortens dancer limbs and exposes sides.
    theta=-.81 + 1.70*v3.window_ease(t,a+.35,b-.25)
    theta += .05*math.sin(math.pi*2*u)
    radius=6.8-3.10*(math.sin(math.pi*u)**1.25)
    eye=np.array([radius*math.sin(theta), 1.45+.48*math.sin(math.pi*u), radius*math.cos(theta)])
    look=np.array([.26*math.sin(2*math.pi*u),-.11,-.45])
    forward=look-eye;forward/=np.linalg.norm(forward)
    right=np.cross(forward,VUP);right/=np.linalg.norm(right)
    up=np.cross(right,forward);up/=np.linalg.norm(up)
    focal=730.0
    return eye,forward,right,up,focal

def project(C,p):
    eye,fwd,rgt,up,f=C
    v=np.asarray(p,dtype=float)-eye
    z=np.dot(v,fwd)
    if z<.21:return None
    return (W/2+f*np.dot(v,rgt)/z,H/2-f*np.dot(v,up)/z,z)

def pp(C,pts):
    q=[project(C,p) for p in pts]
    if any(x is None for x in q):return None
    return [(x[0],x[1]) for x in q]

def line3(d,C,one,two,col,width=2):
    a=project(C,one);b=project(C,two)
    if a is None or b is None:return
    d.line((a[0],a[1],b[0],b[1]),fill=col,width=width)

def quad3(d,C,pts,fill,outline=None,width=2):
    pts=pp(C,pts)
    if pts is None:return
    d.polygon(pts,fill=fill)
    if outline:d.line(pts+[pts[0]],fill=outline,width=width)

def box3(d,C,x,y,z,sx,sy,sz,col,edge):
    # Faces kept separate; side faces change apparent size through orbit.
    front=[(x-sx/2,y,z+sz/2),(x+sx/2,y,z+sz/2),(x+sx/2,y+sy,z+sz/2),(x-sx/2,y+sy,z+sz/2)]
    back=[(x-sx/2,y,z-sz/2),(x+sx/2,y,z-sz/2),(x+sx/2,y+sy,z-sz/2),(x-sx/2,y+sy,z-sz/2)]
    side_l=[front[0],back[0],back[3],front[3]]
    side_r=[front[1],back[1],back[2],front[2]]
    top=[front[3],front[2],back[2],back[3]]
    # Draw furthest faces first based on camera position, but all are plausible.
    eye=C[0]; side=side_l if eye[0]<x else side_r
    quad3(d,C,top,tuple(min(255,int(q*1.18)) for q in col),edge,1)
    quad3(d,C,side,tuple(int(q*.55) for q in col),edge,2)
    quad3(d,C,front,col,edge,2)

RND=random.Random(55072)
ACTORS=[]
for i in range(58):
    # Stable spatial distribution. Two dance lanes at differing *real* z depths;
    # their silhouettes change size relative to each other as camera travels.
    x=RND.uniform(-2.90,2.90)
    z=RND.uniform(-1.35,1.55)
    if abs(x)<.45 and -.25<z<.85 and i%3==0: x+=.8
    ACTORS.append((x,z,i%5,RND.random()*math.tau,RND.uniform(.31,.51),RND.random()))


def actor3(d,C,x,ground_y,z,height,col,phase,orient=0):
    # Flat paper puppet on a *3-D* plane. Every joint is in world space and
    # projected independently, so orbit changes limb foreshortening correctly.
    right=np.array([math.cos(orient),0,-math.sin(orient)])
    forward=np.array([math.sin(orient),0,math.cos(orient)])
    foot=np.array([x,ground_y,z]);rh=height
    swing=math.sin(phase)
    def point(dx,dy,dz=0):return tuple(foot+right*dx+forward*dz+VUP*dy)
    anchor=project(C,point(0,0))
    head=project(C,point(0,rh*.89))
    if not anchor or not head:return
    scale=max(.3,min(3.5,65/(max(.1,anchor[2]))))
    size=max(2,min(13,int(height*110/anchor[2])))
    # A ground shadow confirms world-space floor contact.
    d.ellipse((anchor[0]-size*.8,anchor[1]-size*.18,anchor[0]+size*.8,anchor[1]+size*.2),fill=(4,18,29,155))
    limbs=[(point(0,rh*.73),point(-rh*.30,rh*(.52+.22*swing),.05)),
           (point(0,rh*.73),point(rh*.33,rh*(.49-.21*swing),-.05)),
           (point(0,rh*.26),point(-rh*.16,.01,.08)),
           (point(0,rh*.26),point(rh*.16,.01,-.04)),
           (point(0,rh*.76),point(0,rh*.23))]
    linew=max(1,min(7,round(size*.28)))
    for a,b in limbs:line3(d,C,a,b,(*col,238),linew)
    hc=project(C,point(0,rh*.92)); hL=project(C,point(-rh*.12,rh*.92));hR=project(C,point(rh*.12,rh*.92))
    if hc and hL and hR:
        wr=max(2,math.dist(hL[:2],hR[:2])*.52)
        hh=max(2,wr*.85)
        d.ellipse((hc[0]-wr,hc[1]-hh,hc[0]+wr,hc[1]+hh),fill=(*col,250))
        # face pin: dark eye never becomes tiny illegible text
        if wr>3.5:d.ellipse((hc[0]+wr*.17,hc[1]-hh*.1,hc[0]+wr*.3,hc[1]+hh*.10),fill=(21,30,51,225))


def kid3(d,C,t):
    # Teal-PJ child on the same 3-D floor as sprites; dimensions stay fixed
    # as the camera circles around him, unlike scale-in-place 2-D overlay.
    x=.20+0.12*math.sin(t*.75);z=.22;h=1.38; y=-1.18
    ori=.12*math.sin(t*.5)
    right=np.array([math.cos(ori),0,-math.sin(ori)])
    def pt(xx,yy,zz=0):return tuple(np.array([x,y,z])+right*xx+np.array([0,yy,zz]))
    teal=(39,160,175);skin=(228,165,136);hair=(36,33,51)
    for a,b,cc,wid in [
       (pt(-.13,.46),pt(-.24,.03),teal,7),(pt(.13,.46),pt(.24,.03),teal,7),
       (pt(-.20,.89),pt(-.48,1.13+.13*math.sin(t*4.5)),teal,8),
       (pt(.20,.89),pt(.5,1.03-.18*math.sin(t*4.5)),teal,8),
       (pt(0,.45),pt(0,1.02),teal,16)]:line3(d,C,a,b,(*cc,255),wid)
    head=project(C,pt(0,1.22));hl=project(C,pt(-.16,1.22));hr=project(C,pt(.16,1.22))
    if head and hl and hr:
        r=max(6,math.dist(hl[:2],hr[:2])*.49)
        d.ellipse((head[0]-r,head[1]-r*1.2,head[0]+r,head[1]+r*1.25),fill=(*skin,255))
        d.pieslice((head[0]-r-2,head[1]-r*1.32,head[0]+r+2,head[1]+r*.3),170,355,fill=(*hair,255))
        if r>7:
            for dx in (-.33,.33):d.ellipse((head[0]+dx*r-1,head[1]+r*.14,head[0]+dx*r+1,head[1]+r*.21),fill=(45,37,52,255))


def perspective_stage(t,a,b,include_kid=False):
    C=cam_state(t,a,b)
    bg=base.backdrop((5,12,29),(22,22,53)).convert('RGBA')
    d=ImageDraw.Draw(bg,'RGBA')
    e=base.energy(t)
    # A casing, its *same* perforation lattice, and a copper circuit floor
    # occupy known 3-D planes. Camera can actually pass side-to-side.
    quad3(d,C,[(-3.35,-1.23,-2.15),(3.35,-1.23,-2.15),(3.35,1.63,-2.15),(-3.35,1.63,-2.15)],(10,34,48,255),(100,149,177,255),5)
    for gy in range(13):
        for gx in range(56):
            xx=-3.05+gx*(6.10/55);yy=-.94+gy*(2.12/12)
            a2=project(C,(xx,yy,-2.10))
            if not a2 or a2[0]<-8 or a2[0]>W+8 or a2[1]<-8 or a2[1]>H+8:continue
            rad=max(.7,3.3/a2[2])
            hot=(gx*7+gy*19)%13<5
            col=PAL[(gx*3+gy*5)%5] if hot else (25,63,84)
            alpha=185 if hot else 132
            d.ellipse((a2[0]-rad,a2[1]-rad,a2[0]+rad,a2[1]+rad),fill=(*col,alpha))
    quad3(d,C,[(-3.4,-1.22,2.6),(3.4,-1.22,2.6),(3.4,-1.22,-2.1),(-3.4,-1.22,-2.1)],(13,48,57,255),(98,126,135,255),2)
    # Copper paths and etched circuit tracks carry true perspective.
    for xx in np.linspace(-3.0,3.0,17):line3(d,C,(xx,-1.19,-2.05),(xx+.12,-1.19,2.60),(196,122,75,190),2)
    for zz in np.linspace(-1.95,2.50,12):line3(d,C,(-3.4,-1.18,zz),(3.4,-1.18,zz),(111,106,77,160),1)
    # Surface-mounted components have true projected side faces.
    for x,z in [(-2.9,-1.2),(2.85,-1.15),(-2.8,.45),(2.9,.50)]:
        box3(d,C,x,-1.18,z,.43,.88,.48,(30,74,104),(166,137,96))
        for k in range(4):line3(d,C,(x-.17,-.93+k*.19,z+.245),(x+.17,-.93+k*.19,z+.245),(*PAL[k%5],220),2)
    # DJ station behind dancers, and disco ball hovering in actual depth.
    box3(d,C,0,-1.20,-.98,1.10,.43,.45,(44,38,94),(124,223,226))
    b=project(C,(0,1.15,-.85))
    if b:
        r=max(4,min(21,70/b[2]));d.ellipse((b[0]-r,b[1]-r,b[0]+r,b[1]+r),fill=(129,147,178,250),outline=(235,222,242,255),width=2)
        for k in range(12):
            xx=b[0]+r*.76*math.cos(k*math.tau/12+t*.9)
            yy=b[1]+r*.76*math.sin(k*math.tau/12+t*.9)
            d.ellipse((xx-1.3,yy-1.3,xx+1.3,yy+1.3),fill=(*PAL[k%5],255))
    # Far characters to near characters. Density and occlusion now really vary.
    people=[]
    for i,(xx,zz,ci,phase,h,accent) in enumerate(ACTORS):
        x=xx+.09*math.sin(t*(.7+.03*(i%6))+phase)
        z=zz+.07*math.cos(t*.66+phase)
        q=project(C,(x,-1.18,z))
        if q:people.append((q[2],x,z,ci,phase,h,i))
    people.sort(reverse=True)
    for depth,x,z,ci,phase,h,i in people:
        actor3(d,C,x,-1.18,z,h,PAL[ci],t*(3.9+.03*(i%6))+phase,orient=(i%5-2)*.30)
    if include_kid:kid3(d,C,t)
    # Nearest light pegs provide unmistakable foreground parallax and occlusion.
    for i in range(15):
        x=-3.1+i*.45;z=1.7+(i%4)*.11
        y=.8+(i%3)*.20
        pt=project(C,(x,y,z))
        if not pt:continue
        r=max(2,min(11,38/pt[2]));col=PAL[i%5]
        d.ellipse((pt[0]-r*2,pt[1]-r*2,pt[0]+r*2,pt[1]+r*2),fill=(*col,22))
        d.ellipse((pt[0]-r*.5,pt[1]-r*.5,pt[0]+r*.5,pt[1]+r*.5),fill=(*col,220))
    return bg.convert('RGB')


_v3_inside=v3.inside_world
# Legacy wide shot remains unchanged: perspective orbit is an explicit deliberate
# new cinematic move during the three electronic trills.
def inside_world(t,include_kid=False):
    moves=[(83.195,92.785),(160.968,170.991),(219.0,225.8)]
    for a,b in moves:
        if a<=t<b:
            new=perspective_stage(t,a,b,include_kid=include_kid)
            # Short frame-exact transition, intentionally preserving old world
            # composition at musical cut but changing to physical orbit view.
            fade_in=v3.window_ease(t,a,a+.72)
            fade_out=1-v3.window_ease(t,b-.72,b)
            k=min(fade_in,fade_out)
            if k<.999:
                old=_v3_inside(t,include_kid=include_kid)
                return Image.blend(old,new,k)
            return new
    return _v3_inside(t,include_kid=include_kid)
v3.inside_world=inside_world

# 82 persistent 2-D sprites, spatially distributed on the bed, shelf, floor,
# toy and around the room. Some are LARGE enough to read as tiny dancers.
R=random.Random(761901)
ROOM_ACTORS=[]
for i in range(86):
    band=i%5
    if band==0: x=R.uniform(60,282); y=R.uniform(410,505)     # window/left wall + floor
    elif band==1: x=R.uniform(255,662); y=R.uniform(448,517)   # bedspread
    elif band==2: x=R.uniform(680,918); y=R.uniform(420,526)   # nightstand
    elif band==3: x=R.uniform(340,652); y=R.uniform(255,305)   # floating over pillow
    else: x=R.uniform(70,922); y=R.uniform(105,248)            # sprite constellations
    ROOM_ACTORS.append((x,y,R.choice([12,14,16,19,22]),i%5,R.random()*math.tau,R.random()))

@lru_cache(maxsize=1)
def soft_dot():
    return Image.new('RGBA',(1,1),(0,0,0,0))

def room_sprites(im,t,brightness=1):
    # Use the same sleeping room plate for the entirety of the outro; the eye
    # opening was an ambiguous one-beat dream shock, NOT sustained wakefulness.
    im=im.convert('RGBA')
    halos=Image.new('RGBA',(W,H),(0,0,0,0));hd=ImageDraw.Draw(halos,'RGBA')
    silhouettes=[]
    for i,(bx,by,sz,ci,phase,depth) in enumerate(ROOM_ACTORS):
        col=PAL[ci]
        x=bx+7*math.sin(t*(.58+.05*(i%8))+phase)
        y=by+5*math.sin(t*2.1+phase)
        a=max(0,min(255,int(235*brightness)))
        if a<8:continue
        glow_r=sz*(1.0+.22*math.sin(t*2+phase))
        hd.ellipse((x-glow_r,y-sz*1.6-glow_r,x+glow_r,y-sz*1.6+glow_r),fill=(*col,int(85*brightness)))
        silhouettes.append((x,y,sz,ci,phase,a))
    im=Image.alpha_composite(im,halos.filter(ImageFilter.GaussianBlur(14)))
    d=ImageDraw.Draw(im,'RGBA')
    for x,y,sz,ci,phase,a in silhouettes:
        color=PAL[ci]
        # lively silhouettes; larger than V3 and clearly visible
        v3.tiny_person(d,x,y,color,t*5.0+phase,height=sz,scale=.75)
    return im.convert('RGB')
v3.room_sprites=room_sprites


def last_exit_to_room(t):
    a=inside_world(t,include_kid=True)
    u=v3.window_ease(t,225.8,227.55)
    b=v3.portrait_view(t,plate=base.ROOM_B,zoom=v3.mix(3.7,1.0,v3.window_ease(t,225.8,229)),center=(422,334))
    if u<.999:return Image.blend(a,b,u)
    return room_sprites(b,t,brightness=v3.window_ease(t,227.2,229))
v3.last_exit_to_room=last_exit_to_room

WINDOWS=[]
RR=random.Random(82215)
for bi in range(7):
 for row in range(4):
    WINDOWS.append((105+bi*31+5,204+row*16,239+RR.uniform(.0,6.7),RR.uniform(0,6.28),RR.randrange(5),RR.uniform(.4,1.0)))


def flash(t,phase,speed=1.0):
    # Irregular, deterministic, independent blinking. Smooth color changes,
    # non-sequential onsets: a slow glow overlaid with syncopated dance flicker.
    return max(.20,min(1.,.55+.29*math.sin(t*(1.6+speed*.8)+phase)+.18*math.sin(t*(3.0+speed*.6)+phase*1.37)))

def city_window_room(t):
    im=base.ROOM_B.copy().convert('RGBA')
    lights=Image.new('RGBA',(W,H),(0,0,0,0))
    d=ImageDraw.Draw(lights,'RGBA')
    for xx,yy,when,phase,ci,speed in WINDOWS:
        amt=v3.window_ease(t,when,when+.38)
        if amt<=0:continue
        pulse=flash(t,phase,speed)
        # Rotate colors without cycling all windows together.
        col=PAL[(ci+int((t+phase*3)*(.6+speed*.45)))%5]
        a=amt*(.65+.35*pulse)
        d.ellipse((xx-3,yy-5,xx+18,yy+13),fill=(*col,int(30*a)))
        d.rectangle((xx,yy-2,xx+10,yy+8),fill=(*col,int(245*a)))
        d.line((xx+1,yy,xx+8,yy),fill=(240,245,252,int(176*a)),width=2)
    im=Image.alpha_composite(im,lights)
    return room_sprites(im.convert('RGB'),t,brightness=1.)
v3.city_window_room=city_window_room

# The dream network windows have the same independently pulsing color logic.
OUTSIDE_SEEDS={(k,row,col):(RR.uniform(0,7),RR.random()*math.tau,RR.randint(0,4),RR.uniform(.5,1.5)) for k in range(3) for row in range(5) for col in range(4)}

def outside_plate(t):
    im=base.backdrop((10,20,48),(37,25,68)).convert('RGBA');d=ImageDraw.Draw(im,'RGBA')
    buildings=[(35,155,277,395,(25,34,66)),(345,88,300,463,(27,37,73)),(682,142,259,401,(28,33,59))]
    for k,(bx,by,bw,bh,shade) in enumerate(buildings):
        d.rectangle((bx,by,bx+bw,540),fill=(*shade,255))
        d.rectangle((bx,by,bx+bw,by+9),fill=(80,79,100,255))
        for row in range(5):
            for col in range(4):
                x=bx+18+col*56;y=by+24+row*66
                if x+38>bx+bw or y+46>530:continue
                onset,phase,ci,speed=OUTSIDE_SEEDS[(k,row,col)]
                active=(row+col+k)%5!=3
                d.rounded_rectangle((x,y,x+38,y+46),radius=3,fill=(19,24,51,255),outline=(60,69,96,255),width=2)
                if not active:continue
                a=flash(t+onset,phase,speed)
                c=PAL[(ci+int(t*(.4+.25*speed)+phase))%5]
                d.rounded_rectangle((x+2,y+2,x+36,y+44),radius=2,fill=(*c,int(50+65*a)),outline=(*c,int(125+110*a)),width=2)
                # Dreaming kid and its bedside pegboard; no ordered sweep.
                d.ellipse((x+8,y+18,x+21,y+31),fill=(183,135,113,255))
                d.arc((x+9,y+15,x+23,y+25),170,330,fill=(37,32,55,255),width=3)
                d.line((x+9,y+35,x+29,y+35),fill=(75,89,145,255),width=5)
                for j in range(5):
                    c2=PAL[(ci+j+int(t*(.8+speed)))%5]
                    xx=x+25+(j%2)*4; yy=y+18+(j//2)*6
                    d.ellipse((xx,yy,xx+2.4,yy+2.4),fill=(*c2,244))
    for j in range(26):
        sx=(j*149+37)%960;sy=(j*47+15)%133
        d.ellipse((sx,sy,sx+2,sy+2),fill=(165,173,220,140))
    return im.convert('RGB')
v3.outside_plate=outside_plate

# All ordinary shot staging is preserved, but the scene-specific image sources
# now resolve through functions above. No changes to narrative shot timing.
_old_scene_frame=v3.frame
def frame(t):
    if v3.scene_at(t)[3]=='room_sprite_party':
        im=room_sprites(base.ROOM_B.copy(),t)
        d=ImageDraw.Draw(im)
        d.rectangle((0,0,W,9),fill=(5,7,18))
        d.rectangle((0,H-10,W,H),fill=(5,7,18))
        return im
    return _old_scene_frame(t)
v3.frame=frame
v3.base.frame=frame


def manifest():
    obj=v3.build_manifest()
    d=json.loads(Path(obj).read_text());d['title']='Nobody Owns Tomorrow — music-directed V4'
    d['direction_version']='v4-2026-11-07'
    d['changes']={
      'camera':'Perspective-project real 3-D world geometry and 2-D sprite puppets in three musical trills. Orbit and dolly (not screen shake/pan); world-space foreshortening and depth sorting.',
      'camera_windows_s':[[83.195,92.785],[160.968,170.991],[219,225.8]],
      'boy':'Eyes open only on brief dream shock at 189.5–190.147; eyes shut for room return and finale.',
      'bedroom_sprites':len(ROOM_ACTORS),'chorus_karaoke_advance_s':LYRIC_ANTICIPATION_S,
      'window_lighting':'non-sequential, independently flickering, changing Night-Brite hues',
      'chorus':'subtle physical peg gestures and no city flash cutaways',
      'media_rights':'private local review only; no publication'
    }
    for s in d['shots']:
        if s['scene'] in ['rave_fly','rave_fly_kid']:s['direction']='Projected orbit-dolly through flattened dancing 2-D sprites in a 3-D toy-circuit room; occlusion, foreground parallax, changing perspective.'
        if s['scene']=='room_sprite_party':s['direction']='82+ dancing light sprites illuminate the bedroom while the sleeping boy remains eyes shut.'
        if s['scene']=='windows':s['direction']='Many windows activate non-sequentially with changing colors and independent dance-flashing.'
    p=OUT/'Nobody_V4_Directors_Cues.json';p.write_text(json.dumps(d,indent=2));return p


def storyboard():
    sample=[(25.1,'PEGBOARD'),(56.0,'CHORUS'),(82.0,'CUTOUT SPRITES'),(85.,'ORBIT: APPROACH'),(88.2,'ORBIT: ROTATION'),(91.4,'ORBIT: EXIT'),(162.4,'2ND ORBIT'),(167.5,'REAR LATTICE'),(190.0,'WAKE SHOCK'),(212,'DREAM RAVE'),(222,'FINAL ORBIT'),(229,'SLEEPING BOY'),(234,'ROOM FULL OF SPRITES'),(244,'NONSEQUENTIAL LIGHTS'),(252.0,'ZOOP OUT WINDOW'),(259,'OTHER DREAMERS')]
    cw,ch=320,180; gap=14;label=27
    board=Image.new('RGB',(4*(cw+gap)+gap,4*(ch+label+gap)+gap),(15,18,32));d=ImageDraw.Draw(board)
    for i,(t,label_s) in enumerate(sample):
        im=v3.frame(t).resize((cw,ch),Image.Resampling.LANCZOS)
        x=gap+(i%4)*(cw+gap);y=gap+(i//4)*(ch+label+gap)
        board.paste(im,(x,y));d.text((x+4,y+ch+5),f'{int(t//60):02}:{t%60:05.2f}   {label_s}',font=base.ff(12,True),fill=(220,230,244))
    p=OUT/'Nobody_V4_Storyboard.jpg';board.save(p,quality=86,optimize=True);return p

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--start',type=float,default=0)
    p.add_argument('--duration',type=float,default=base.DURATION)
    p.add_argument('--fps',type=int,default=10)
    p.add_argument('--crf',type=int,default=38)
    p.add_argument('--lite',action='store_true')
    p.add_argument('--stills-only',action='store_true')
    a=p.parse_args()
    if a.start==0:
        print('manifest',manifest(),flush=True)
        print('storyboard',storyboard(),flush=True)
    if a.stills_only:sys.exit(0)
    dur=min(a.duration,base.DURATION-a.start)
    path=OUT/('Nobody_V4_COMPLETE_LITE.mp4' if a.start==0 and a.lite else 'Nobody_V4_FULL_PREVIEW.mp4')
    print('rendering',path,flush=True)
    v3.render(path,a.start,dur,fps=a.fps,size='lite' if a.lite else 'full',crf=a.crf)
    print('done',path,path.stat().st_size,flush=True)
