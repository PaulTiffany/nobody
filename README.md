# Nobody Owns Tomorrow — The Other Side 🎬🎶

**Created and directed by Paul Carver Tiffany III, in collaboration with ChatGPT 6 (OpenAI).**

A dreaming child, a glowing lightboard, and a tiny dance party behind the lights: our complete **4:23 V6 animated pop music video** responding artistically to a substantive conversation about AI and the future.

![V6 film storyboard](production/music_video_v6/storyboard_v6_web.jpg)

## Watch / reproduce

The **finished sound-on V6** master and compact encodes are preserved as verified chunks in [output/v6-media](output/v6-media/README.md). Clone and run `python output/v6-media/reassemble.py` to recover the real MP4s; the old [silent study](output/scene-flips-preview.mp4) is **not** the finished movie. YouTube publication is still pending.

[Source and reproduction](production/music_video_v6/README.md) · [Director's cues](production/music_video_v6/Nobody_V6_Directors_Cues.json) · [Timestamped interview-to-song map](production/music_video_v6/Nobody_V6_Music_To_Source_Provenance.json)

## Real creative technology and credits

**Paul Carver Tiffany III** — creator, musician and lead artistic director.
**ChatGPT 6 (OpenAI)** — creative/technical collaborator and animated-art direction.

- **Original song:** [Nobody Owns Tomorrow on Suno](https://suno.com/song/cf3d6b12-d528-4193-a8f0-7f4e9b997ea3), clip `cf3d6b12-d528-4193-a8f0-7f4e9b997ea3`.
- **Suno MCP integration:** fetched clip metadata, beat/section analysis and machine-derived word alignment for karaoke and directorial timing (not independently listening-certified).
- **OpenAI image generation with ChatGPT 6:** created the original cover / YouTube thumbnail illustration and social-preview artwork. This is **separate from the video renderer**.
- **Pillow and FFmpeg:** the **two actually used, pinned direct Git submodules** satisfying Artilect's original-upstream technology requirement. **NumPy** and **DejaVu fonts** are independently credited installed dependencies.
- **In-video sprites, karaoke and camera:** custom time-indexed Pillow/NumPy rendering, including 2.5D projection and physical room-space anchoring; FFmpeg audio/video encoding.
- **Earlier proposed ELYSY and UseSuno MV Studio:** NOT used for V6; retained only as historical documentation and in prior Git history. They are no longer active `technologies/` submodules.

[Full creator/technology credits](production/music_video_v6/CREATIVE_CREDITS.md) · [Release provenance](production/music_video_v6/RELEASE_PROVENANCE.md) · [Suno MCP/toolchain receipt](production/music_video_v6/TOOLCHAIN_EXECUTION.json) · [Original artwork provenance](production/music_video_v6/ART_ASSET_PROVENANCE.json)

## Substantive source / artistic interpretation

Independent pop-music response to [The Beyond Tomorrow Podcast](https://www.youtube.com/watch?v=NXITvkHIV9o). Source passages and our timestamped creative interpretations are [explicitly mapped](production/music_video_v6/Nobody_V6_Music_To_Source_Provenance.json). Neither the podcast nor its guests created or endorsed this video. No interview footage is embedded.

## Artilect status

This is a **creator-owned production recipe, not a new platform**. Artilect structure CI has passed. The `artilect.json` media URL is temporarily the **GitHub source location for the V6 sound-on film**, not a directly playable YouTube video; replace it with the public watch URL upon release. Before commercial posting, verify the applicable Suno download/distribution rights and review promotional artwork for third-party marks.

**Nobody owns tomorrow. Nobody owns the sky.**
