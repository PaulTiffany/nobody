# Nobody — active V6 Artilect production recipe

**Creator: Paul Carver Tiffany III · Creative/technical collaborator: ChatGPT 6 (OpenAI).**

This is the current recipe for the finished V6 film; the older ELYSY/MV Studio proposal is preserved in [LEGACY_PRE_V6_WORKFLOW.md](LEGACY_PRE_V6_WORKFLOW.md), **not** credited as executed technology.

## Actual inputs and technology

1. **Song:** [Suno recording](https://suno.com/song/cf3d6b12-d528-4193-a8f0-7f4e9b997ea3); supplied creator-controlled WAV `Nobody Owns Tomorrow(1).wav`. The original WAV is not committed.
2. **Suno MCP:** retrieve clip metadata, beat/section map and best-effort word alignment; the data used for the V6 cut is [preserved in Git](music_video_v6/nobody_suno_word_alignment.json). No assumption of perfectly verified sync.
3. **ChatGPT 6 + OpenAI image generation:** separate original cover/thumbnail/social image, as documented by [asset provenance](music_video_v6/ART_ASSET_PROVENANCE.json). In-film animation is **not** generated from this cover.
4. **Pillow + NumPy + FFmpeg:** actually rendered all V6 film frames, on-toy karaoke, projected flat-sprite cameras, pixel lights, and encoded the final H.264/AAC. Pillow and FFmpeg are the **two active Artilect upstream Git submodules**, separately installed for actual runtime. Font dependency: DejaVu Sans.

## Render

Install Python, Pillow, NumPy, FFmpeg with H.264/AAC support, and DejaVu fonts. Put the creator-owned WAV at `<work>/Nobody Owns Tomorrow(1).wav`. Stage alignment with:

```bash
python production/music_video_v6/PREPARE_WORKSPACE.py /path/to/work
```

Then from `production/music_video_v6`:

```bash
NOBODY_MEDIA_ROOT=/path/to/work python nobody_dream_rave_v6_renderer.py --stills-only
NOBODY_MEDIA_ROOT=/path/to/work python nobody_dream_rave_v6_renderer.py --fps 12 --crf 33
```

The six layered renderer modules are required. The latest cut has already been rendered and byte-checked; clean-machine source-to-video equivalence and cross-platform font paths are not yet qualified. [Full V6 instructions](music_video_v6/README.md).

## Watch, source, publication

`python output/v6-media/reassemble.py` (from repo root) reconstructs the complete soundtrack-backed film from verified chunks. [Original discussion](https://www.youtube.com/watch?v=NXITvkHIV9o) and [interpretive timestamp map](music_video_v6/Nobody_V6_Music_To_Source_Provenance.json). [Full credits](music_video_v6/CREATIVE_CREDITS.md).

`python scripts/validate.py` checks the Artilect repository structure, **not** legal commercial-use rights. YouTube has not been published. The interim `artilect.json.media_url` points to the V6 repository media location, not a public streaming player; replace with the eventual public YouTube watch URL before submitting Artilect's gallery.

