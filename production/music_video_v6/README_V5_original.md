# Nobody Owns Tomorrow — V5 Camera Continuity Cut

**Private, zero-paid-video-inference director's animatic.** Contains the complete 4:23 song, its synchronized word art, the boy's dream, miniature rave, dancing bedroom sprites, and the final city-window pullout. This is software 2.5D/3D perspective with 2D paper sprites, not AI live-action footage.

## Watch

Open `Nobody_V5_COMPLETE_MUSIC_VIDEO.mp4` from the companion `Nobody_V5_WATCH_VIDEO.zip`. 640×360, 10 fps, H.264 video / AAC music; runtime **263.2 s**.

## Why V4 snapped

- **At 0:25.09:** the physical zoom completed and immediately switched to another frame that already had fully illuminated illustrative pegs. In V5 the camera keeps a gentle forward lens motion across the shot boundary; illustration fades in over 0.8 s on the SAME toy plate.
- **At 1:23.195, 2:40.968, and 3:39:** V4 displayed a separate 3D stage and began the orbit from an oblique camera even though the previous wide shot had been centered. V5 renders the entire interior from *one continuous 3D stage* with one camera. The dolly/orbit begins and ends facing forward, with zero first derivative at musical boundaries. A stationary staged conversion from the existing drawn portal into the 3D set occurs earlier (1:13.274–1:15.424, repeated), not at the moment the trill starts.
- **At the end:** V4 rendered some bedroom sprites onto the ALREADY zoomed portrait of the boy, so their coordinates moved relative to his room. V5 positions all the light characters in the fixed bedroom image, then crops/pans the COMPOSED scene. Room and sprites share the same camera transform from 3:45.8 through 4:12.2. The boy stays asleep after the single-frame surprise at 3:09.5.
- **At 4:12.2:** V5 first frames of the outside-dreamers shot match the preceding window-camera image before dissolving to the outside world.

## Preserved

The user-directed cuts and events remain: verses are illustrated, choruses are word-level Night-Brite karaoke, at 1:33 the view emerges into the boy's dream, first-half bridge returns to the front of the toy, at 3:09.5 the boy appears briefly awake, at 3:29 he joins the sprites, and in the last minute the bedroom fills with sprites and colored windows lead us to other dreaming children. The **3:10.147 deliberate drum-hit hard cut** is not smoothed.

## Limitations and verification

Some transitions between entirely different illustrated physical locations still use a stylistic dissolve. V5 explicitly avoids *camera resets* at the electronic-trill boundaries, but this is not mathematically continuous 3D geometry between the bedroom and the abstract toy interior. The song's word-level timings are Suno model output, not manually ear-certified. Original music rights and publication approval remain with the creator.

`verify_v5.py` checks representative adjacent frames across V5's formerly snapping boundaries and reports pixel-motion differences; it is a **regression guard**, not an aesthetic or audio-sync guarantee. The entire MP4 was decoded with FFmpeg and checked for an AAC track and a complete 263.2-second video.

## Reproduction

Install Pillow + NumPy, with FFmpeg on PATH, and put the five `nobody_dream_rave*_renderer.py` files plus `nobody_suno_word_alignment.json` in one directory. The scripts presently refer to `/mnt/data/Nobody Owns Tomorrow(1).wav` and `/mnt/data/nobody_suno_word_alignment.json` for audio and annotation. Replace those with your licensed local paths for portability. Run:

```bash
python nobody_dream_rave_v5_renderer.py --fps 10 --crf 39 --lite
python verify_v5.py
```

Existing `nobody` GitHub repository not altered. The source archive includes the previous stages and this V5 revision for audit and iteration.
