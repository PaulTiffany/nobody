# Nobody — producer's recipe

This is an **Artilect production**, not a new karaoke application. Make a film using other people's original open-source projects, give them credit, and keep the source/version trail. Here is the workflow, in order.

## Inputs

- Your own properly licensed copy of **Nobody Owns Tomorrow.wav**. It is intentionally **not** in Git.
- `production/lyrics/Nobody-Owns-Tomorrow.txt`: the *written* song lyrics, not yet checked against the sung take. Correct every repeat, ad lib and changed word by listening.
- `output/silent-other-side.mp4`: a short, **actual** silent visual prototype generated with Pillow and FFmpeg; `output/front.png` and `output/back.png` are still art references.
- `output/nobody-front-back-silent.mp4`: current **full-length (4:23) silent animated backdrop**, front during verses/bridge and reverse-side rave during instrumental/refrain passages. Locally rendered, excluded from Git because it is a large deliverable.
- `output/scene-flips-preview.mp4`: small **public** silent excerpt showing the front → rave → front cycle.
- `production/scene_cues.storyboard.json`: **obsolete guesses for reference only**. The real `production/scene_cues.json` is deliberately absent until vocal alignment is available.

## 1. Sync the real vocals with ELYSY (upstream)

Source: `technologies/ELYSY` → https://github.com/gabrielxcom/elysy . It uses Demucs + WhisperX, is MIT licensed, and has a web-based correction editor. First install the upstream project's prerequisites **using its README** (recommended Python 3.11/3.12, model downloads and FFmpeg; CPU also works). Running installers downloads code/models and must be your own informed choice. No API keys required by the advertised local workflow.

Open ELYSY on `http://127.0.0.1:8765`, load the WAV and the lyrics, run Auto-Align, and **listen to every line**. Correct the text and word timing. Export **Enhanced LRC (word-level)** to a local `nobody.enhanced.lrc`. DO NOT use the old estimated `lyrics_draft.json` for karaoke. ELYSY uses a nontrivial external model download; this step has **not yet been run** in the current sandbox.

## 2. Design and export in UseSuno MV Studio (upstream)

Source: `technologies/UseSunoMVStudio` → https://github.com/UseSuno/UseSunoMVStudio . AGPL-3.0-only. Its parser accepts word-level Enhanced LRC, and its studio supports custom video backgrounds, separate lyrics and audio, and a local 1080p MP4/WebM export.

```bash
cd technologies/UseSunoMVStudio
npm ci
npm run dev
```

In your browser: import the WAV, import `nobody.enhanced.lrc`, choose **Custom media → video background**, and select the full-length **silent** backdrop or a shorter test clip. Preview a chorus and the pass-through-to-rave transition. Tune text contrast, positioning and timing in its editor. Export a 15–30 second range **first**; inspect audio sync and readability. Export the full song only after that succeeds. Browser codec support and permissions vary; the upstream provides a real-time recording fallback. **No exported MV Studio video has been verified in this sandbox yet.**

### Compatibility status

ELYSY's documented Enhanced LRC is `[mm:ss.xx]<mm:ss.xxx>Word ...`; MV Studio's `src/import/lyrics.ts` recognizes `<mm:ss.xxx>word` tags. Their formats are **source-inspected, not end-to-end tested**; timing quality remains unknown until the test import, audition and export actually happen.

## 3. Make an animated backdrop (already working)

A small bespoke visual **artwork generator**, NOT a karaoke renderer: Pillow draws the front of the glowing pegboard, its reverse-side rave, and parallax effects; FFmpeg encodes the frames. Both are credited and pinned as their own direct upstream submodules. The old `film.py` contains optional legacy karaoke modes; **use `--karaoke off`** for this Artilect workflow. Actual media was rendered using separately installed Pillow and FFmpeg binaries, not compiled directly from the pinned source Gitlinks.

```bash
# Dependencies for our procedural artwork (not automatic from gitlinks):
python -m pip install 'Pillow==12.3.0'
# Provide FFmpeg with H.264 and AAC (or change the encoder settings).
python scripts/check_timeline.py
bash production/render_storyboard.sh '/path/to/Nobody Owns Tomorrow.wav' \
  output/nobody-front-back-cut.mp4 12
# Strip audio before importing as Custom media in the lyric studio:
ffmpeg -y -i output/nobody-front-back-cut.mp4 -map 0:v:0 \
  -c:v copy -an output/nobody-front-back-silent.mp4
```

**The previously published cuts were guesses and must not be used for the final video.** After ELYSY exports the word-timed LRC and the producer reviews it by ear, use `scripts/derive_scene_cues.py --lrc /path/to/nobody.enhanced.lrc --wav /path/to/Nobody.wav`. It produces an **unverified candidate** in `production/scene_cues.candidate.json`, with the actual sung phrase timestamps and source-file hashes. Listen against the recording and correct timing in ELYSY, then promote the reviewed candidate to `production/scene_cues.json` and change `timing_status` to `aligned_and_creator_reviewed`. `film.py` refuses ordinary video renders while that reviewed file is absent. `render_storyboard.sh` is explicitly a demonstration of old draft choreography and cannot establish vocal sync.

## Rights / publication / checks

The song is a creator-supplied Suno recording; verify the applicable distribution rights before posting the sound or finished music video publicly. Neither the WAV nor unreleased full render is committed by default. No paid video-generation service or model API was used to create the current visual preview. Check the model licenses if redistributing models, and AGPL compliance if distributing/modifying the MV Studio source. Distinct software licenses remain in the upstream repos.

```bash
python scripts/validate.py
python scripts/check_timeline.py
```

Run `python scripts/test_derive_scene_cues.py` for semantic cue mapping tests; they use synthetic fixtures and **do not certify any real-song timing**. The structure validator checks Git submodule provenance and metadata. It cannot claim that ELYSY finished alignment, that MV Studio exported a video, or that Suno rights are cleared. Submission to Artilect must wait for an actual, reviewed finished film and creator permission for publication.
