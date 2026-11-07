#!/usr/bin/env python3
"""Nobody V5 — camera-continuity and room-locked sprite revision.

No paid video inference. Reuses V4, V3, V2 and original Suno-aligned
model-derived timeline. Every physical scene uses a stable camera/object frame:
- Lens push is carried across the 25.09s boundary with fade-in pictograms.
- The toy interior persists in 3D between wide / trill / exit; no arbitrary
  re-initialization of perspective at electronic trills.
- A stationary camera gently cross-dissolves the 2D cartoon stage into its
  dimensional twin at the beginning of each interior sequence.
- Camera orbit has zero angular/radial velocity at both flythrough boundaries.
- Bedroom sprites exist in ROOM coordinates; camera crops the combined scene,
  rather than placing new sprites into screen coordinates after camera movement.
- Final outdoor transition starts with the prior room camera's exact image.
"""
import math, sys, json, argparse, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import nobody_dream_rave_v4_renderer as v4

v3=v4.v3; v2=v4.v2; base=v4.base
W,H=base.W,base.H
HERE=Path(__import__('os').environ.get('NOBODY_MEDIA_ROOT', '/mnt/data'))/'nobody_v5'; HERE.mkdir(parents=True,exist_ok=True)
VUP=v4.VUP

# A 3D scene with a single physically consistent camera pose at the START AND
# END of every musical orbit. Unlike V4, the full wide shot also uses the SAME
# world/camera, so entering the orbit cannot jump to a new composition.
FLY_WINDOWS=[(83.195,92.785),(160.968,170.991),(219.0,225.8)]
INTERIOR_WINDOWS=[(73.274,92.785),(151.094,170.991),(209.797,225.8)]


def smooth(x):
    x=max(0.,min(1.,float(x)))
    return x*x*(3-2*x)


def continuous_cam_state(t, a=None,b=None):
    theta=0.0; radius=6.35; elev=1.46
    # Film: continuous dolly/orbit/return, NOT a hard reframe at bar boundary.
    # The variable "u" is smoothly eased and sin(2πu) vanishes at BOTH ends.
    for lo,hi in FLY_WINDOWS:
        if lo<=t<=hi:
            u=smooth((t-lo)/(hi-lo))
            theta= .91*math.sin(2*math.pi*u)
            radius=6.35-2.00*(math.sin(math.pi*u)**2)
            elev=1.46+.46*(math.sin(math.pi*u)**2)
            break
    eye=np.array([radius*math.sin(theta),elev,radius*math.cos(theta)],float)
    look=np.array([0.,-.11,-.45],float)
    forward=look-eye; forward/=np.linalg.norm(forward)
    right=np.cross(forward,VUP);right/=np.linalg.norm(right)
    up=np.cross(right,forward);up/=np.linalg.norm(up)
    # Keep scale constant at fly edges; perspective does all the motion.
    return eye,forward,right,up,930.0

v4.cam_state=continuous_cam_state


def unified_inside_world(t,include_kid=False):
    """Stable world coordinates across each entire rave sequence."""
    for lo,hi in INTERIOR_WINDOWS:
        if lo <= t <= hi+1e-6:
            rendered=v4.perspective_stage(t,lo,hi,include_kid=include_kid)
            # Portal ends on V2's precise inside_frame, so start with that
            # EXACT geometry rather than suddenly revealing V3 or perspective.
            # Resolve V2 -> V3 illustration -> SAME 3D environment while camera
            # is stationary; after that, an actual 3D camera orbit can begin.
            if t < lo+2.15:
                legacy=v4._v3_inside(t,include_kid=include_kid)
                if t < lo+.45:
                    return Image.blend(v2.inside_frame(t), legacy, smooth((t-lo)/.45))
                return Image.blend(legacy, rendered, smooth((t-(lo+.45))/1.70))
            return rendered
    # Scene requests at exit boundary use the same last 3D shot, not a 2D reset.
    for lo,hi in INTERIOR_WINDOWS:
        if hi < t <= hi+1.75:
            return v4.perspective_stage(hi-.001,lo,hi,include_kid=include_kid)
    return v4._v3_inside(t,include_kid=include_kid)

v3.inside_world=unified_inside_world

# All world-to-screen transformations are applied to the complete physical
# scene (room + pegs + dance sprites) as one view transform. No screen-space
# dancing sprites attached to the camera after a crop.
def room_with_world_sprites(t,brightness=1.0):
    return v4.room_sprites(base.ROOM_B.copy(),t,brightness=brightness)


def last_exit_to_room(t):
    a=unified_inside_world(t,include_kid=True)
    u=v3.window_ease(t,225.8,229.0)
    z=v3.mix(3.7,1.0,u)
    # Start at sleeping boy, widen naturally onto whole physical room.
    image=room_with_world_sprites(t,brightness=v3.window_ease(t,226.7,228.9))
    b=v3.crop_camera(image,422,334,z)
    # Image b and room_sprite_party at 229 share source plate, sprite positions.
    blend=v3.window_ease(t,225.8,227.8)
    return Image.blend(a,b,blend) if blend<1 else b

v3.last_exit_to_room=last_exit_to_room

# Use the same room at all times throughout the finale; no awake-room to
# sleeping-room switch at 229. Camera movement affects all room objects equally.
def city_window_room(t):
    im=base.ROOM_B.copy().convert('RGBA')
    lights=Image.new('RGBA',(W,H),(0,0,0,0))
    d=ImageDraw.Draw(lights,'RGBA')
    for xx,yy,when,phase,ci,speed in v4.WINDOWS:
        amt=v3.window_ease(t,when,when+.38)
        if amt<=0:continue
        pulse=v4.flash(t,phase,speed)
        col=base.PALETTE[(ci+int((t+phase*3)*(.6+speed*.45)))%5]
        a=amt*(.65+.35*pulse)
        d.ellipse((xx-3,yy-5,xx+18,yy+13),fill=(*col,int(30*a)))
        d.rectangle((xx,yy-2,xx+10,yy+8),fill=(*col,int(245*a)))
        d.line((xx+1,yy,xx+8,yy),fill=(240,245,252,int(176*a)),width=2)
    im=Image.alpha_composite(im,lights)
    return v4.room_sprites(im.convert('RGB'),t,brightness=1.0)

v3.city_window_room=city_window_room


def window_to_city(t):
    # This crop is evaluated on the fully composed room, never separate motes.
    room=city_window_room(t)
    u=v3.window_ease(t,248,252.2)
    cx=v3.mix(480,203,u); cy=v3.mix(270,172,u); z=v3.mix(1,3.0,u)
    return v3.crop_camera(room,cx,cy,z)

v3.window_to_city=window_to_city


def other_dreamers(t):
    # At exactly 252.2s this is PIXEL-IDENTICAL to window_to_city(252.2)
    # before gradually resolving to the other-city plate.
    q=v3.window_ease(t,252.2,255.6)
    near=window_to_city(t)
    city=v4.outside_plate(t)
    z=v3.mix(1.0,2.38,v3.window_ease(t,255.6,263.24))
    cx=v3.mix(480,532,v3.window_ease(t,255.6,263.24))
    cy=v3.mix(270,265,v3.window_ease(t,255.6,263.24))
    city=v3.crop_camera(city,cx,cy,z)
    return Image.blend(near,city,q) if q<1 else city

v3.other_dreamers=other_dreamers

# Preserve V4's choir, lyric anticipation, new hand-drawn sprites etc. Camera
# at the opening has forward momentum through the shot's semantic boundary.
def continuous_intro(t):
    return 1.0 + .05*(v3.window_ease(t,24.15,27.4)-v3.window_ease(t,29.0,32.0))


def frame(t):
    kind=v3.scene_at(t)[3]
    if kind=='kid_to_room':
        im=last_exit_to_room(t)
    elif kind=='room_sprite_party':
        im=room_with_world_sprites(t)
    elif kind=='windows':
        im=city_window_room(t)
    elif kind=='window_push':
        im=window_to_city(t)
    elif kind=='other_dreamers':
        im=other_dreamers(t)
    elif kind=='verse_icons' and 25.09<=t<25.96:
        # At entry the exact CLOSE plate already fills the lens. Bring the
        # icon up gradually; do not abruptly replace the still at 25.09.
        fresh=v4.frame(t)
        im=Image.blend(base.CLOSE.copy(),fresh,v3.window_ease(t,25.09,25.90))
    else:
        im=v4.frame(t)
    if 24.15<=t<32.0:
        im=v3.crop_camera(im,480,270,continuous_intro(t))
    # The original film letterboxes every frame. Preserve the same static
    # matte in custom V5 scenes; do not let it jump at a scene boundary.
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,9),fill=(5,7,18))
    d.rectangle((0,H-10,W,H),fill=(5,7,18))
    return im

v3.frame=frame
base.frame=frame


def generate_storyboard():
    picks=[(23.9,'Bedroom -> toy'),(25.11,'Same plate: icons fade'),(26.0,'Word illustration'),
           (73.4,'Toy interior wide'),(76.4,'3D world stabilized'),(82.95,'Camera center'),
           (85.7,'3D dolly / yaw'),(89.1,'Parallax / orbit'),(92.76,'Camera returns center'),
           (160.8,'Second rave wide'),(163.5,'Second orbit'),(170.95,'Back to center'),
           (225.70,'Third orbit ends'),(227.2,'Boy / room pullout'),(229.05,'Sprites in room'),
           (244.0,'Independent city lights'),(250.7,'Room-relative pan'),(254.0,'Outside-world dissolve')]
    cw,ch=256,144;gap=10; label=24
    cols=3; rows=math.ceil(len(picks)/cols)
    board=Image.new('RGB',(cols*(cw+gap)+gap,rows*(ch+label+gap)+gap),(8,12,28));d=ImageDraw.Draw(board)
    for i,(t,note) in enumerate(picks):
        image=frame(t).resize((cw,ch),Image.Resampling.BICUBIC)
        xx=gap+(i%cols)*(cw+gap); yy=gap+(i//cols)*(ch+label+gap)
        board.paste(image,(xx,yy))
        d.text((xx+3,yy+ch+3),f'{int(t//60)}:{t%60:05.2f} {note}',fill=(228,233,245))
    p=HERE/'Nobody_V5_Storyboard.jpg';board.save(p,quality=82,optimize=True)
    return p


def manifest():
    original=json.loads((Path(__import__('os').environ.get('NOBODY_MEDIA_ROOT', '/mnt/data'))/'nobody_v4_work/Nobody_V4_Directors_Cues.json').read_text())
    original.update(direction_version='v5-camera-continuity',camera_principle='World-to-camera transforms, not screen-space overlays',
      v5_corrections={
        'first_push':'Same lens trajectory through 25.09; 0.8s peg icon fade and 0.05 continuing push',
        'rave':'One projected 3D stage all through each rave; yaw+zoom with zero velocity at each start/end; dissolve from 2D portal while camera holds',
        'room':'All 86 sprites world-locked before camera crop, same sleeping-bedroom plate during final exit, room party, window lighting and pan',
        'last_city':'First outside-dreamer frame matches final bedroom-window camera, cross-dissolve instead of discontinuous cut',
        'unchanged':'Suno lyrics, timed beats, narrative, final 190.147 intentional hard cut, user-directed 1:33/2:51/3:09/3:29/3:49/4:08 choreography'
      })
    p=HERE/'Nobody_V5_Scene_Cues.json';p.write_text(json.dumps(original,indent=2));return p

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--start',type=float,default=0.0)
    a.add_argument('--duration',type=float,default=base.DURATION)
    a.add_argument('--fps',type=int,default=10)
    a.add_argument('--crf',type=int,default=38)
    a.add_argument('--lite',action='store_true')
    a.add_argument('--stills-only',action='store_true')
    args=a.parse_args()
    print('scene cues',manifest(),flush=True)
    print('storyboard',generate_storyboard(),flush=True)
    if args.stills_only:sys.exit(0)
    dur=min(args.duration,base.DURATION-args.start)
    out=HERE / (f'Nobody_V5_TEST_{args.start:.2f}_{dur:.2f}.mp4' if args.start else 'Nobody_V5_COMPLETE_WITH_AUDIO.mp4')
    print('rendering',out,flush=True)
    v3.render(out,args.start,dur,fps=args.fps,size='lite' if args.lite else 'full',crf=args.crf)
    print('render complete',out,out.stat().st_size,flush=True)
