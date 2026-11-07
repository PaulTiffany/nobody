# Nobody Owns Tomorrow — V4 Dream/Disco Director's Cut (private animatic)

## Quick viewing

Open `Nobody_V4_FINAL_WITH_AUDIO.mp4`. It contains both video and the creator-supplied song. The full score runs 4:23.22. This is a low-budget 640×360 procedural animated **animatic** at 10 fps, not a photorealistic 3-D rendering.

## Director feedback implemented (November 7, 2026)

- Electronic trills (1:23–1:32.8; 2:41–2:50.99; 3:39–3:45.8): now a **true 3-D perspective projection** of a Night-Brite circuit-board miniature. The camera changes yaw, elevation and distance while projected sprites and circuitry change relative apparent size and occlude one another. Sprite people remain 2-D paper-cutout characters with independently projected limbs. This is an orbit/dolly, NOT screen-space shake or a crop-pan. Brief blends connect these sequences to the original static miniature.
- Boy's eyes: brief eye-opening dream shock at 3:09.5 before the hard cut; on his return to the bedroom he has his eyes shut again.
- Bedroom outro: 86 deterministic animated light-sprite placements, spread over bed, room, shelf, floor, toy and stars. Glow is physically layered on the room art.
- Windows from 3:59 onward: per-window independent randomized activation, unequal flashing phases and varying colors; no ordered building sweep. The final outside-world windows also vary independently.
- Night-Brite karaoke: word onset appears **0.32 s earlier** visually; audio is not moved. Subtle in-world peg accents augment selected chorus words. No flashy city cutaways.

## Scope / limitations

The audio and film are aligned to Suno's word-level annotation with director adjustments. The lyrics have **not been independently ear-verified**. The camera is 3-D software projection of simple flat art primitives, not Blender meshes or generated video. The style stays intentionally illustrative. This is a private review, not a published music video; check music rights before public upload.

Production is based entirely on the existing Python/Pillow/numpy and FFmpeg pipeline. No paid image or video generation. The scripts retain traceable scene timing and can be re-rendered at different settings.

## Reproduction

Place the source Python modules in one folder with Pillow and numpy installed. `nobody_dream_rave_v4_renderer.py` imports V3 → V2 → base. All scripts currently reference `/mnt/data` for the supplied `Nobody Owns Tomorrow(1).wav` and `nobody_suno_word_alignment.json`. Change ROOT/paths for another machine.

Run:

```
python nobody_dream_rave_v4_renderer.py --lite --fps 10 --crf 38
```

The code generates `nobody_v4_work/Nobody_V4_COMPLETE_LITE.mp4` and the V4 director manifest; the review build was encoded as two contiguous MP4 segments because a sandbox export was interrupted, then concatenated losslessly. The combined MP4 was decoded end-to-end with FFmpeg and checked for embedded audio.
