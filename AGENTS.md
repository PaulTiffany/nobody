# Nobody — Artilect production instructions (V6)

**Creator and lead director: Paul Carver Tiffany III. Collaborative AI creative/technical director: ChatGPT 6 (OpenAI).**

Read `production/README.md` (active V6 recipe), `production/music_video_v6/CREATIVE_CREDITS.md`, and `production/music_video_v6/RELEASE_PROVENANCE.md` first.

This is a finished artistic production, not a new platform. Source song: https://suno.com/song/cf3d6b12-d528-4193-a8f0-7f4e9b997ea3. Intellectual inspiration: https://www.youtube.com/watch?v=NXITvkHIV9o. Preserve the distinction between source statement, our interpretation, lyric/scene timing, and generated visuals. Do not imply the panelists endorsed us.

**Correct V6 creative stack:** Suno created the original song; Suno MCP retrieved song metadata, 432 beats / 15 acoustic sections and 362 lyric-word alignment entries. ChatGPT 6 and OpenAI image generation created **separate cover/thumbnail artwork**, not the film's procedurally animated frames. The V6 video itself is custom Pillow + NumPy animation and FFmpeg H.264/AAC encoding, using DejaVu fonts. Word alignment is best effort; visual anticipations of about 0.32 seconds are directorial choices.

**Artilect direct source Git submodules actually used in V6:** Pillow and FFmpeg; preserve these pinned original upstream Gitlinks. NumPy is installed as a Python dependency. Suno MCP and OpenAI image generation are hosted services, *not* Git submodules. ELYSY and UseSuno MV Studio were **not executed** and are now archived as historical candidates, not active technologies. Do not miscredit them.

Creative direction: original pegboard karaoke, sleeping boy, 2.5D miniature rave with smooth spatial camera, physically anchored sprites, and city-of-other-dreamers outro; the brief eye opening near 3:09.5 is the intended shock cut. User-supplied shot corrections govern quality.

Media provenance: original song WAV is not tracked; the **complete video including soundtrack is publicly stored** as checksum-verified chunks under `output/v6-media/`. Cover and social-preview art provenance is documented in `production/music_video_v6/ART_ASSET_PROVENANCE.json`; those session assets are **not represented as binary files committed to Git**.

Before YouTube / Artilect showcase publication, verify the recording's commercial-use and permitted-download rights, artwork-brand usage, and required AI-use disclosure. Update `artilect.json.media_url` with the real YouTube watch link; current source/reconstruction link is not a video player. The creator approves publication. Run `python scripts/validate.py`.
