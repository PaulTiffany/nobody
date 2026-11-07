# Nobody V6 — source-aware release candidate

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
