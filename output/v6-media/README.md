# Nobody V6 — synchronized H.264/AAC music video

Both **complete 4:23.24 sound-on music videos** are preserved in this public repository as numbered **byte-exact binary chunks**. Keeping each Git object under 750 KB permits reliable upload and integrity checking. **These are NOT independent clips:** concatenate them, don't play a single `.part` file.

To reconstruct both final MP4s after cloning:

```bash
python output/v6-media/reassemble.py
```

This writes `output/v6-media/rendered/Nobody_V6_COMPLETE_WITH_AUDIO.mp4` (960×540 master) and `Nobody_V6_SMALL_WITH_AUDIO.mp4` (download-friendly derivative). Python standard library only. The script verifies each complete file against its original SHA-256 and byte length, and refuses missing/modified chunks. CI also runs this reconstruction. The binaries are proper MP4 files containing synchronized **H.264 video and AAC music**, not silent drafts.

| Version | Size | SHA-256 |
|---|---:|---|
| V6 master | 10,875,633 bytes | `bd899cc80fefcdac0a222f3ffab3f87e41f405a83185a846330ed50e5ced007d` |
| V6 compact | 4,250,328 bytes | `0625d6a97126575c9fd4f147bd3136694d3795e63b5c4031a0520ed254037c47` |

Source and reproducibility: [production/music_video_v6](../../production/music_video_v6/README.md).

**Release status:** repository push **does not publish to YouTube**. Video is an independent, artist-directed response to the [Beyond Tomorrow discussion](https://www.youtube.com/watch?v=NXITvkHIV9o). The original panel's media is not sampled in the film, and its guests do not endorse our interpretation. **Before commercial distribution**, the creator should check the Suno commercial-use entitlement and use YouTube's AI-generated media disclosure where appropriate. The artist's 49 MB original WAV is intentionally not separately redistributed in Git.
