# Nobody Owns Tomorrow — V6 release provenance and Artilect evidence

**Audit date:** 2026-11-07. This documents the cut already rendered; it does not certify rights or represent a new video render.

## Creative source graph

| Layer | Source | Relationship / status |
|---|---|---|
| Original song | [Suno clip `cf3d6b12-d528-4193-a8f0-7f4e9b997ea3`](https://suno.com/song/cf3d6b12-d528-4193-a8f0-7f4e9b997ea3) | `Nobody Owns Tomorrow`, created 2026-11-01, 263.24 seconds. Creator-supplied WAV used for the music-video soundtrack. No separate WAV stored in Git. |
| Music-driven timing | [Stored Suno word alignment](nobody_suno_word_alignment.json) | Model-generated word spans, best effort; some directorial adjustments (approximately 0.32 s anticipation) are distinct from sung onsets. Independent full ear verification not claimed. |
| Artistic direction | [27-shot directed V6 cues](Nobody_V6_Directors_Cues.json) | Music-section/phrase/shot choreography, iterative user corrections V1–V6, miniature sprite world and dream scenes. |
| Rendered film | [Checksummed V6 master and compact files](../../output/v6-media/README.md) | Sound-on H.264/AAC videos retained as public, byte-exact chunks. Reassembler and GitHub Actions verify assembled SHA-256; this does *not* establish a fresh source-to-video deterministic rebuild. |
| Discussion interpreted | [Beyond Tomorrow original episode](https://www.youtube.com/watch?v=NXITvkHIV9o) | Independent musical response, not clips, quotes, paraphrased speaker lyrics, or guest endorsement. |
| Interpretive source map | [Timestamped thematic associations](Nobody_V6_Music_To_Source_Provenance.json) | 11 pairs linking original interview moments to artistic themes; source timestamps are the panel's clock and our_video timestamps are the song's clock. |
| Upload copy | [Description](YOUTUBE_PASTE_DESCRIPTION.txt) and [pinned comment](YOUTUBE_PINNED_COMMENT.txt) | Drafts; not yet a posted YouTube release. |

## Actual V6 technology used, as distinct from pinned historical candidates

| Component | Upstream | Provenance |
|---|---|---|
| Pillow | https://github.com/python-pillow/Pillow | **Used** to draw, composite, and transform the images. Direct Git submodule is pinned; Python runtime package was separately installed. |
| FFmpeg | https://github.com/FFmpeg/FFmpeg | **Used** for H.264/AAC encoding and validation. Direct Git submodule pinned; actual runtime was an installed FFmpeg binary, not built from the pinned source. Binary redistribution/codec licenses are build-dependent. |
| NumPy | https://github.com/numpy/numpy | **Used** for raster masks, spatial compositing and numerical operations. Installed package; **not one of the four direct Git submodules**. License: BSD-3-Clause. |
| Suno service | https://suno.com/song/cf3d6b12-d528-4193-a8f0-7f4e9b997ea3 | **Used** for original song creation and its retained word timing. Service, not open-source Git technology; do not present it as a Git submodule or open-source dependency. |
| ELYSY | https://github.com/gabrielxcom/elysy | **Not executed in V6.** Pinned, historically proposed alignment engine. Its presence is not an execution receipt. |
| UseSuno MV Studio | https://github.com/UseSuno/UseSunoMVStudio | **Not executed in V6.** Pinned, historically proposed karaoke renderer. Its AGPL-3.0-only license remains its own. |
| DejaVu fonts | https://dejavu-fonts.github.io/ | Used for visual text in the rendering environment. Font licensing and machine availability are separate from source Gitlinks. |

The pinned submodule commits have independently resolved in their original GitHub repositories; their Gitlink commit SHAs remain recorded in the repository. See [toolchain snapshot](TOOLCHAIN_EXECUTION.json) for the specific runtime versions visible at the latest audit. Those versions must **not** be retroactively claimed as independently proven original-render versions.

## Known limits and release gates

- The public repository contains the V6 **video plus soundtrack**, split into binary parts. Avoid claiming the audio is unpublished or secret simply because the source WAV is not separately tracked.
- The `artilect.json.media_path` currently selects the early silent clip, solely to satisfy the gallery's committed-file constraint. **Do not submit it as the finished V6 film.** Replace it with the real public YouTube video URL in `media_url` after the video is uploaded.
- Reproduce new video frames with the creator's WAV, supplied aligner JSON, Python/Pillow/NumPy, FFmpeg/libx264 and the DejaVu font family. The original renderer still has Linux font paths and old absolute-path auxiliary tooling. No clean-machine full audiovisual rebuild is certified.
- Verify what Suno commercial terms applied when this clip was created, that this specific audio file was obtained under permitted download conditions, and its intended public/monetized usage. Current account plan is **not** proof of past creation or download rights.
- YouTube upload, generated-content disclosure, and Artilect showcase submission remain creator-controlled. The original interview is credited, timestamp-linked, and not sampled.
- Avoid implying endorsement by the podcast, individual speakers, the Night-Brite/Lite-Brite trademark owners, or Suno.
