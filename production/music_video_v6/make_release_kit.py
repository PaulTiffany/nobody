from pathlib import Path
import json, csv, textwrap, zipfile, shutil, math, os, subprocess
from PIL import Image,ImageDraw,ImageFont
import qrcode
OUT=Path('/mnt/data/nobody_v6')
video='NXITvkHIV9o'
url=lambda s:f'https://www.youtube.com/watch?v={video}&t={s}s'
link=f'https://www.youtube.com/watch?v={video}'

# Observed panel topics in user's 1h29m transcript; associations are interpretive
# editorial annotations, not assertions that the speaker said the song's lyrics.
bridges=[
  {'our_music_video_s':25.09,'our_scene':'First night-brite pictograms / warnings and city','interview_s':969,'source_time':'16:09','source_theme':'People feeling disconnected from AI development and its consequences','relationship':'Visual interpretation of anxious city'} ,
  {'our_music_video_s':44.32,'our_scene':'Who holds the switch / who holds the key?','interview_s':694,'source_time':'11:34','source_theme':'Discussion reframes pause AI as whether and how AI can be controlled','relationship':'Question echoed in our pre-chorus, not quotation'},
  {'our_music_video_s':54.25,'our_scene':'Nobody owns tomorrow: first chorus','interview_s':1140,'source_time':'19:00','source_theme':'Ethics as negotiation of interests and shared purposes','relationship':'Our pluralistic artistic response'},
  {'our_music_video_s':72.94,'our_scene':'Other Side doorway / first 3D party','interview_s':1956,'source_time':'32:36','source_theme':'Imagining a beneficial superintelligence and wider abundance','relationship':'A hopeful, playful visual metaphor'},
  {'our_music_video_s':103.0,'our_scene':'Another promise on a screen','interview_s':1641,'source_time':'27:21','source_theme':'Unequal access to the benefits of technology','relationship':'Our human-centered critique of automation'},
  {'our_music_video_s':149.37,'our_scene':'Second Other Side','interview_s':2602,'source_time':'43:22','source_theme':'Disagreement over whether the transition will look like familiar disaster scenarios','relationship':'Alternative possibilities represented as dreams'},
  {'our_music_video_s':171.0,'our_scene':'Maybe we are afraid of falling (bridge)','interview_s':624,'source_time':'10:24','source_theme':'Acknowledging uncertainty rather than treating catastrophe as certain','relationship':'Lyrical emphasis on questions and humility'},
  {'our_music_video_s':190.147,'our_scene':'Eye-opening surprise / final chorus','interview_s':2642,'source_time':'44:02','source_theme':'Human flourishing and retaining agency','relationship':'The sudden eye-opening plays with control and dreaming'},
  {'our_music_video_s':239,'our_scene':'City windows glow','interview_s':874,'source_time':'14:34','source_theme':'AI in ordinary lives and the breadth of people affected','relationship':'Extend a single toy to a community'},
  {'our_music_video_s':248,'our_scene':'Other children, other dreams','interview_s':5252,'source_time':'1:27:32','source_theme':'Humanity deciding together what sort of AGI is created','relationship':'Our dream-world ending returns to collective agency'},
  {'our_music_video_s':251,'our_scene':'Outro provenance / world of other dreamers','interview_s':5232,'source_time':'1:27:12','source_theme':'The future is not predetermined; which systems we create matters','relationship':'Title motif: nobody owns tomorrow (original creative lyric)'}
]
for b in bridges:b['source_deep_link']=url(b['interview_s'])
(OUT/'Nobody_V6_Music_To_Source_Provenance.json').write_text(json.dumps({'source_episode_title':"AI EXPERTS REVEAL: It’s Too Late! We Can't Stop What's Coming",'source_channel':'The Beyond Tomorrow Podcast with Julian Issa','source_link':link,'source_published':'2026-10-30','annotations':'Creator interpretation, not endorsements or quotations. Times in the song are synchronized to Suno; source interview times refer to the original panel episode.','links':bridges},indent=2),encoding='utf-8')
with (OUT/'Nobody_V6_Deep_Links.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(bridges[0].keys()));w.writeheader();w.writerows(bridges)

# Ready-to-paste video description. Chapter times are rounded as viewing aids,
# source links are separate (YouTube's own video-creator chapters are not back-links).
desc='''Nobody Owns Tomorrow (The Other Side) — animated music video

A little boy falls asleep. His glowing Night-Brite has another life inside it: a microscopic dance floor, a hundred colorful characters, and a whole city of other dreamers. ✨

An original musical response to an October 2026 AI discussion on humanity's agency, shared purposes, and the unknown future. Not a summary, quotation, or endorsement by the panelists.

🎙️ ORIGINAL DISCUSSION
The Beyond Tomorrow Podcast with Julian Issa — “AI EXPERTS REVEAL: It’s Too Late! We Can't Stop What's Coming” (October 30, 2026)
'''+link+'''

The interview moments our song plays with:
• 11:34 — Can humans control AI?  '''+url(694)+'''
• 19:00 — Ethics and shared purposes  '''+url(1140)+'''
• 20:46 — Top-level goals and self-modification  '''+url(1246)+'''
• 25:42 — What does it mean for humanity to have common goals?  '''+url(1542)+'''
• 32:36 — Imagining beneficial superintelligence  '''+url(1956)+'''
• 44:02 — Why human agency matters  '''+url(2642)+'''
• 1:27:12 — The future isn't predetermined  '''+url(5232)+'''
• 1:27:56 — Humanity's role in guiding what comes next  '''+url(5276)+'''

These are thematic connections selected by the music-video creators, not claims about any speaker's agreement with the song.

🎬 MUSIC VIDEO CHAPTERS
00:00 The bedroom
00:25 The Night-Brite comes alive
00:54 Nobody owns tomorrow
01:12 On the other side
01:23 Inside the toy — dance-floor orbit
01:33 Out of the dream
01:43 Another promise on a screen
02:12 Chorus II
02:30 Another world inside the pegs
02:41 The second electronic trill
02:51 The bridge
03:10 One dramatic eye-opening
03:29 Dancing with the dream
03:39 Final little rave
03:49 Sprites fill the bedroom
03:59 The city lights up

🎵 MUSIC + PRODUCTION
Original song: “Nobody Owns Tomorrow” (Suno-assisted production)
Music, visual direction, and animated artwork were developed as a collaborative creative production. The illustrated scenes use a deterministic renderer and a Suno-aligned lyric/beat timeline, not generated live-action footage. Original interview clips and speakers' likenesses are not used in this video.

#NobodyOwnsTomorrow #AIMusicVideo #Transhumanism #AI #NightBrite
'''
(OUT/'YOUTUBE_PASTE_DESCRIPTION.txt').write_text(desc,encoding='utf-8')
comment='''This song is our artistic response to a conversation about humanity's future, not an attempt to speak on behalf of the panelists. ❤️

Original discussion: '''+link+'''

The closing thoughts that especially stuck with us: 1:27:12 (the future isn't predetermined) '''+url(5232)+''' and 1:27:56 (we still have agency in shaping it) '''+url(5276)+'''

What idea from the conversation would *you* turn into a song?'''
(OUT/'YOUTUBE_PINNED_COMMENT.txt').write_text(comment,encoding='utf-8')

# Clean diegetic music video intentionally keeps all source credits OFF the art.
# Optional end-card lets creator append a visual provenance cue on their own.
W,H=1280,720
im=Image.new('RGB',(W,H),(8,15,32)); d=ImageDraw.Draw(im)
for y in range(H):d.line((0,y,W,y),fill=(int(7+y*.012),int(13+y*.013),int(34+y*.025)))
for j in range(85):
    x=70+(j*179)%850;y=100+(j*67)%470
    c=[(79,228,234),(255,112,178),(255,201,93),(158,139,255),(129,236,168)][j%5]
    d.ellipse((x-2,y-2,x+2,y+2),fill=c)
freg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f1=ImageFont.truetype(fb,44);f2=ImageFont.truetype(freg,27);f3=ImageFont.truetype(freg,23)
d.text((66,95),'INSPIRED BY A CONVERSATION',font=f2,fill=(132,220,221))
d.text((66,152),'Nobody Owns Tomorrow',font=f1,fill=(247,248,254))
d.text((66,229),'An independent musical response to',font=f2,fill=(226,231,239))
d.text((66,272),'The Beyond Tomorrow Podcast',font=ImageFont.truetype(fb,31),fill=(248,214,164))
d.text((66,316),'"AI EXPERTS REVEAL: It\'s Too Late!"',font=f2,fill=(218,223,236))
d.text((66,480),'Watch the original discussion',font=ImageFont.truetype(fb,25),fill=(241,247,248))
d.text((66,518),'The conversation and the song are distinct works.',font=f3,fill=(180,192,208))
qr=qrcode.QRCode(box_size=8,border=2,error_correction=qrcode.constants.ERROR_CORRECT_M);qr.add_data(url(5232));qr.make(fit=True)
qim=qr.make_image(fill_color='black',back_color='white').convert('RGB').resize((233,233))
im.paste(qim,(943,270));d.text((956,517),'SOURCE @ 1:27:12',font=ImageFont.truetype(fb,17),fill=(255,224,181))
d.rounded_rectangle((42,42,1238,674),radius=34,outline=(75,104,137),width=3)
im.save(OUT/'OPTIONAL_YouTube_Source_End_Card.png',optimize=True)

# Retain V5 direction and incorporate the new verifiable changes.
v5=json.loads(Path('/mnt/data/nobody_v5/Nobody_V5_Scene_Cues.json').read_text())
v5.update(direction_version='v6-music-video-with-interview-provenance',interview_source=link,release_status='rendered for review, NOT uploaded or published')
v5['v6_corrections']={
  'inside_rave':'Only one projected 3D rave world and 3D camera for wide, fly and exit; no flat inside_frame() rendering',
  'portal':'Physical Night-Brite word magnification and radial iris to same 3D world; no legacy flat inside',
  'lens_pushes':'Single 5x room texture with toy master mapped to physical location; single-camera crop, no double casing image blend',
  'room_sprites':'Keep fixed room coordinates but shuffle sprite palette separately from five placement bands',
  'source':'Provenance links in upload description, pinned comment, and OPTIONAL card; no editorial titles burnt into video',
  'song':'Unchanged: Suno alignments, original user-supplied sound, narrative cuts, bridge etc.'}
(OUT/'Nobody_V6_Directors_Cues.json').write_text(json.dumps(v5,indent=2),encoding='utf-8')
readme='''# Nobody V6 — source-aware release candidate

## The film
- Soundtrack from the artist-supplied WAV, synchronized to Suno's best-effort alignment.
- 4:23.24, 12 fps. Two encodes: 960×540 master and 640×360 download-friendly.
- No paid video inference, no borrowed footage from the source interview.

## Directorial fixes implemented
- The 0:23 and 1:41 toy zooms use one 5× spatially textured bedroom master.
  The old 2D layering/casing dissolve during the push was removed.
- All three toy interiors now draw the same 3D stage directly, even in the first
  moments before the electronic trill. No old flat inside-stage frames in V6.
- A peg-centered radial aperture opens from the zoomed chorus text to the 3D world.
- Room dancers remain spatially anchored. Their colors are independently
  shuffled so the old per-location color segregation disappears.
- Original chorus word sync, kid reveal, room sprites, window color behavior,
  and ending remain as in V5.

## Provenance to source interview
- Original episode: The Beyond Tomorrow Podcast with Julian Issa, 2026-10-30.
- YouTube original: https://www.youtube.com/watch?v=NXITvkHIV9o
- See YOUTUBE_PASTE_DESCRIPTION.txt and Nobody_V6_Music_To_Source_Provenance.json
  for explicit episode timestamps. These links are interpretations, not literal
  claims or endorsement by the speakers. The original footage is NOT included.
- The MP4 intentionally contains no source titles overlaid on the story.
  OPTIONALLY use OPTIONAL_YouTube_Source_End_Card.png as a separate credit slate,
  or link the source using YouTube Studio's video info-card / end-screen tools.
  Cards link to the video, while description links can jump to explicit moments.

## Caveats before publishing
- Shot-to-shot continuity was checked with render previews and frame tests; this
  is still a hand-drawn/procedural 2.5D animatic, not photo-real video.
- Audio/lyrics timing is model-derived (Suno), not independent ear-certified.
- Verify the original Suno song was made/downloaded under a commercial-use
  eligible subscription; user controls rights and public release.
- In YouTube Studio: disclose AI-generated music using the AI-use selector.
- The director has not uploaded or published anything to YouTube or GitHub.

## Reproducing
- Python >=3.10, Pillow and numpy, FFmpeg + libx264.
- Sources are layered V2/V3/V4/V5/V6 and require the same relative or absolute
  paths referenced in scripts, plus the creator's audio and Suno alignment.
- Avoid publishing third-party model weights or user-owned audio separately.
'''
(OUT/'README_V6.md').write_text(readme,encoding='utf-8')

# Package compact first (best reliability per user's previously failing >10MB files).
with zipfile.ZipFile('/mnt/data/Nobody_V6_WATCH_AND_PROVENANCE_SMALL.zip','w') as z:
 for p in [OUT/'Nobody_V6_SMALL_WITH_AUDIO.mp4',OUT/'YOUTUBE_PASTE_DESCRIPTION.txt',OUT/'YOUTUBE_PINNED_COMMENT.txt',OUT/'Nobody_V6_Deep_Links.csv',OUT/'README_V6.md']:
  z.write(p,p.name,compress_type=zipfile.ZIP_STORED if p.suffix=='.mp4' else zipfile.ZIP_DEFLATED)
with zipfile.ZipFile('/mnt/data/Nobody_V6_RELEASE_QUALITY.zip','w') as z:
 for p in [OUT/'Nobody_V6_COMPLETE_WITH_AUDIO.mp4',OUT/'YOUTUBE_PASTE_DESCRIPTION.txt',OUT/'YOUTUBE_PINNED_COMMENT.txt',OUT/'Nobody_V6_Music_To_Source_Provenance.json',OUT/'README_V6.md']:
  z.write(p,p.name,compress_type=zipfile.ZIP_STORED if p.suffix=='.mp4' else zipfile.ZIP_DEFLATED)
# Source package: no audio required for code/asset provenance; storyboard optional card.
with zipfile.ZipFile('/mnt/data/Nobody_V6_SOURCE_STORYBOARD_AND_LINKS.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in [OUT/'Nobody_V6_Storyboard.jpg',OUT/'OPTIONAL_YouTube_Source_End_Card.png',OUT/'Nobody_V6_Music_To_Source_Provenance.json',OUT/'Nobody_V6_Deep_Links.csv',OUT/'Nobody_V6_Directors_Cues.json',OUT/'YOUTUBE_PASTE_DESCRIPTION.txt',OUT/'YOUTUBE_PINNED_COMMENT.txt',OUT/'README_V6.md']:
  z.write(p,p.name)
 for n in ['nobody_dream_rave_renderer.py','nobody_dream_rave_v2_renderer.py','nobody_dream_rave_v3_renderer.py','nobody_dream_rave_v4_renderer.py','nobody_dream_rave_v5_renderer.py','nobody_dream_rave_v6_renderer.py','nobody_suno_word_alignment.json']:
  p=Path('/mnt/data/nobody_v5')/n
  z.write(p,'source/'+n)
print('created packages',[(p.name,p.stat().st_size) for p in Path('/mnt/data').glob('Nobody_V6_*.zip')])
