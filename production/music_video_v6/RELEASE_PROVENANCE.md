# V6 release and Artilect provenance (2026-11-07)

**Created and directed by Paul Carver Tiffany III, collaborating with ChatGPT 6 (OpenAI).** [Full credits](CREATIVE_CREDITS.md).

## Actual creative source graph

| Layer | Verified source | Status |
|---|---|---|
| Original music | [Nobody Owns Tomorrow on Suno](https://suno.com/song/cf3d6b12-d528-4193-a8f0-7f4e9b997ea3) | Suno-created song, Nov 1 2026; 263.24s; clip `cf3d6b12-d528-4193-a8f0-7f4e9b997ea3`. |
| Timing | Suno MCP song analysis and [committed alignment JSON](nobody_suno_word_alignment.json) | Connector readback confirms 432 beats, 15 sections, 362 machine-aligned entries. Best-effort word boundaries; not ear-certified. |
| Creator direction | [27-shot V6 direction](Nobody_V6_Directors_Cues.json) | Human-supervised music-sensitive visual cuts and corrections. |
| Video imagery | [Six-layer procedural Pillow/NumPy renderer](README.md) | In-video graphics and 2.5D dancing light-sprites computed in Python, **not from the cover-image generator**. |
| Final video encoding | FFmpeg | H.264 video / AAC original song; [checksummed full and compact encodes](../../output/v6-media/README.md) reconstructed from public chunks. |
| Cover / thumbnail | ChatGPT 6 with OpenAI image generation | Original generated cover illustration, optimized GitHub social preview. [Hashes, dimensions and caveats](ART_ASSET_PROVENANCE.json); session media files not recorded as Git binaries. |
| Intellectual source | [The Beyond Tomorrow Podcast](https://www.youtube.com/watch?v=NXITvkHIV9o) | [11 timestamped, explicitly interpretive connections](Nobody_V6_Music_To_Source_Provenance.json), no podcast footage or direct guest endorsement. |
| Publication copy | [YouTube description](YOUTUBE_PASTE_DESCRIPTION.txt) · [comment](YOUTUBE_PINNED_COMMENT.txt) | Drafts; video not uploaded to YouTube. |

## Actual tools versus historical candidates

**Suno MCP** is an actively used connected service for clip metadata, audio timing and word alignment. **OpenAI image generation** is an actively used service for promotional art; **ChatGPT 6** is credited for creative/code collaboration. Neither is an open-source Git submodule. **Pillow** ([original upstream](https://github.com/python-pillow/Pillow), MIT-CMU) and **FFmpeg** ([original upstream](https://github.com/FFmpeg/FFmpeg), license depends on build) are the two executed, independently developed **direct/pinned upstream Git submodules** required by Artilect. NumPy ([upstream](https://github.com/numpy/numpy), BSD-3-Clause) is an installed numerical code dependency; DejaVu fonts are a separate resource.

**Do not cite ELYSY, WhisperX or UseSuno MV Studio as executed V6 technologies.** Earlier exploration is archived in [the legacy recipe](../LEGACY_PRE_V6_WORKFLOW.md) and Git history, not current `technologies/` Gitlinks.

## Evidence limitations

- V6 source assets, Cues, timings and audio-backed film are preserved; GitHub CI reassembly hash verification has passed. This is **not** a clean-machine full-render replication.
- The original WAV is **not** separately tracked, but it is audible inside the public assembled MP4s.
- Cover/thumbnail was created here but its binary is not tracked; whether the social-preview JPEG was uploaded to GitHub Settings is not confirmed.
- Commercial use and original Suno download entitlement remain creator-review items; do not infer solely from current plan. Image contains third-party branding references that should be reviewed before independent-IP publication.
- `artilect.json.media_url` temporarily links to the **current GitHub V6 media-reconstruction directory**, not an immediately playable video. Replace it with the YouTube watch URL when published; do not mistake structural pass for final gallery readiness.
