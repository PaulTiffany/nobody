# Nobody Owns Tomorrow — V3 Director's Revision

A complete 4:23 music-synced illustrated animatic produced using the creator's original WAV, Pillow, FFmpeg, and previously retrieved Suno model-derived word alignment. No paid video/image inference. The output is a **10/12-fps 2.5D illustrated animatic**, not physically modeled Blender footage or photorealistic generative video.

## V3 acceptance / review beats

- **0:25**: No visible chapter marker (including the former “NIGHT-BRITE / THE WORLD INSIDE”). The bedroom-to-toy push uses the same model of the toy.
- **0:54–1:11**, **2:12–2:29**, **3:10–3:27**: Pegboard karaoke remains. No city-image substitutions in lyric rests; occasional lyric-specific peg light effects.
- **1:11–1:13**: Portal zoom resolves on the final word “side.”
- **1:23–1:33**: Movable 2.5D camera through dancing toy circuitry, with closer and farther light points. Not 3D meshes.
- **1:33–1:38**: Emerge from the dream and pull out from the child; **1:38–1:43**: smoothly zoom back toward Night-Brite.
- **2:41–2:51**: Repeat the dynamic miniature dance camera, then emerge onto the **front of the Night-Brite** rather than the child.
- **2:53–3:00**: Animated Night-Brite icons for the first half of the bridge; **3:00–3:09.5**: return to the boy.
- **3:09.5**: Eyes open. **3:10.147**: the first *intentionally dramatic* hard cut to final karaoke, on the nearby detected downbeat.
- **3:29–3:39**: Child joins little people in the circuit-board rave.
- **3:39–3:46**: Traveling camera for final electronic passage; **3:46–3:49**: exit into boy's bedroom, with the little sprites. No anomalous text over the toy.
- **3:49–3:59**: Sprites dance around bedroom; **3:59–4:08**: neighboring apartment lights gain the Night-Brite palette; **4:08–end**: zoom toward window and reveal additional sleeping children and their illuminated toys.

## Timing and limitations

Song: *Nobody Owns Tomorrow*, 263.24 seconds. The creative edit uses Suno's model-derived word alignment as a guide, alongside director-adjusted event cues and previously retrieved musical analysis. The user-specified electronic passage entrances (approximately 1:23, 2:41, and 3:39) guide camera changes. The exact alignment has not been independently verified against every sung syllable. Model-derived labels are not intrinsic semantic truth. A scene's intention is a directorial choice, not automatically extracted from the recording.

## Reproduction

Place these scripts together in a folder with Pillow and numpy installed, and FFmpeg on PATH. The current scripts reference `/mnt/data/nobody_suno_word_alignment.json` and `/mnt/data/Nobody Owns Tomorrow(1).wav`, both of which are creator-provided/creator-connected data. Put those files at the referenced paths or change `ROOT`, `ALIGN`, and `AUDIO` in `nobody_dream_rave_renderer.py` before rerunning. Audio is omitted from the source archive because the full creator WAV is large; the finished VIDEO has AAC audio embedded.

Run `python nobody_dream_rave_v3_renderer.py --lite --crf 36 --fps 12`. The rendered file is `Nobody_V3_LITE_Full_Song.mp4`.

No source changes have been pushed to GitHub. No public release has been made.
