# Nobody Owns Tomorrow — V6 (November 7, 2026)

This folder is the **actual latest locally rendered production** and supporting source, as distinct from the repository's historical scene-flips experiment. Nothing here is a claim that the V6 performance has been posted to YouTube.

## Contents

- Six cumulative renderer modules (`nobody_dream_rave_renderer.py`, `..._v2...` through `..._v6...`). The V6 script imports the earlier layers; **all six are required**.
- Suno-derived word-timing data, *not* independently verified by listening. The original WAV is artist-provided and **not checked into this source tree**.
- V3–V6 director cues, the revised camera-continuity storyboard, source interview cross-references, and YouTube description/pinned-comment drafts.
- A web-sized V6 storyboard and optional provenance end card. They are **production reference artwork**, not final rendered video.

## Reproducing / previewing

Python ≥3.10 with `Pillow` and `numpy`, plus FFmpeg/libx264 and DejaVu fonts are needed. See the root's pinned upstream Pillow and FFmpeg submodules. Gitlinks are attribution/source pins, **not an installed runtime**. Rendering depends on supplying the creator's rights-cleared WAV separately.

Create a workspace with the WAV at `<work>/Nobody Owns Tomorrow(1).wav`, and copy `nobody_suno_word_alignment.json` there. Then from this directory:

```bash
NOBODY_MEDIA_ROOT=/absolute/path/to/work python nobody_dream_rave_v6_renderer.py --stills-only
NOBODY_MEDIA_ROOT=/absolute/path/to/work python nobody_dream_rave_v6_renderer.py --fps 12 --crf 33
```

The render will land in `<work>/nobody_v6/`. On Windows PowerShell use `$env:NOBODY_MEDIA_ROOT='C:\\path\\to\\work'` before calling Python. The project was created originally under `/mnt/data`, so any absolute-path assumptions in helper scripts should be verified on other platforms; the six production renderers were patched to respect `NOBODY_MEDIA_ROOT`.

## Verification and artistic scope

The 4:23 full V6 encode (H.264 + AAC) and a smaller derivative were generated in the original production environment. No paid video inference was used. FFmpeg decode verification was reported for that source render. This repository stores source, timing, storyboards, and both final MP4s as byte-exact **reassemblable chunks** under `output/v6-media/`; it does **not** store the artist WAV as a separate file. Run `python output/v6-media/reassemble.py` from the repository root to reconstruct both complete sound-on MP4s. YouTube release still belongs to the creator. Provenance is provided through links and timestamps in the YouTube description; the episode footage itself was not copied.

### Musical and narrative notes

- A boy dreams beside a luminous Night-Brite pegboard, which contains an impossible tiny dance floor. The camera travels through illuminated pegs during repeated “on the other side” sections.
- Repeated 3D orbit sections are **perspective projection of flat sprites** (not Blender meshes). Camera and sprite coordinates are consistent across adjacent shots.
- Brief eye-opening near 3:09.5 is intentionally a **single shock cut**, not the boy waking for the rest of the film.
- The final room has independent dancing sprites and randomized illuminated neighboring windows. Karaoke visual onset anticipates Suno alignment by ~0.32 seconds.

## Provenance

Original conversation: [The Beyond Tomorrow Podcast](https://www.youtube.com/watch?v=NXITvkHIV9o). See `Nobody_V6_Music_To_Source_Provenance.json` and `Nobody_V6_Deep_Links.csv` for precise external video timestamps, annotated as **creative interpretations, not speaker endorsements**.

This work is an artist-directed musical response, not a substitute for the source interview. Keep the original source channel credited and do not embed source audio/video without separate rights.

## Rights and publication

The source song was supplied by its creator. Check the Suno subscription/commercial use terms that applied when the song was generated before releasing to YouTube; YouTube AI-use disclosure and source attributions also need final creator review. Previous production docs explicitly kept full media out of Git. This commit updates the readable project source without leaking the unverified master WAV or large encoded film. YouTube is **not published** from this push.
