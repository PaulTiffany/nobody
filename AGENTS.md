# Nobody — Artilect producer instructions

This repository follows the canonical instructions of https://github.com/PaulTiffany/artilect/tree/submission-template (the `AGENTS.md` and `SKILL.md` contract). **This is a creative production, not a new platform.**

Read `production/README.md` first. Use existing credited upstream technology. The four original projects are direct pinned submodules: ELYSY, UseSunoMVStudio, Pillow and FFmpeg. Preserve each original upstream Gitlink and `.gitmodules` URL. Do not vendor them, silently swap them, or claim source was installed simply because it's present as a Git submodule.

Creative goal: the front of a luminous pegboard shows a melancholy city. Each time the chorus sings “on the other side,” push through a light peg to a jubilant parallax miniature rave. Return to the front for verses and the quiet bridge. The end returns to a single illuminated peg. The lyrics should be gracefully synchronized in front of the art, not baked into an incorrectly timed programmatic sweep.

Workflow:
1. Use creator's properly licensed WAV privately; use `production/lyrics/Nobody-Owns-Tomorrow.txt` as source words, **correct them against what the song actually sings**.
2. Use upstream ELYSY for alignment, inspect results by listening and export **Enhanced LRC**. Never invent timing or claim alignment merely because a JSON or .lrc file parses.
3. Use upstream UseSuno MV Studio to import the audio, enhanced LRC, and our **silent** background film; produce a genuine rendered karaoke video and check the output. Don't build a competing timing UI or karaoke renderer.
4. Pillow/FFmpeg are the actual tools for the visual artwork. Run `production/render_storyboard.sh` and review the six scene switches in `production/scene_cues.json`. Existing legacy karaoke modes are deprecated for this project.
5. Document actual commands, pinned source versions, licenses, rights, external model/binary dependencies, failures and real media receipts. Keep videos/music out of Git unless explicitly approved. Run `python scripts/validate.py`.
6. Do not falsely declare completed production. A human controls artistic decisions, licensing and Artilect showcase submission; get approval for publishing the finished audio/movie.

Do not execute unreviewed upstream installer scripts without informed consent. Keep any secret tokens or model weights out of Git. MIT licenses do not cancel the AGPL terms of MV Studio, and model/media rights remain independent of software licenses.
