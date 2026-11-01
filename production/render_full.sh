#!/usr/bin/env bash
# Chunked Artilect lyric-film render, because shorter Pillow/FFmpeg pipes are
# friendlier to low-memory environments. Requires Bash, Python, ffprobe, ffmpeg.
set -euo pipefail
if [ "$#" -lt 1 ]; then echo "Usage: $0 '/path/to/Nobody Owns Tomorrow.wav' [output-path] [off|review|verified|draft]" >&2; exit 2; fi
AUDIO=$(realpath "$1")
KARAOKE=${3:-off}
case "$KARAOKE" in off|review|verified|draft) ;; *) echo "Invalid karaoke mode" >&2; exit 2;; esac
OUT=${2:-output/full-draft.mp4}
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
python scripts/check_timeline.py
mkdir -p ".renders/$KARAOKE"
# Deliberate short chunks; source time remains absolute, so visual animations
# and line progress remain stable across independently rendered chunks.
starts=(0 30 60 90 120 150 180 210 230 240)
durations=(30 30 30 30 30 30 30 20 10 23.24)
: >".renders/$KARAOKE/concat.txt"
for i in "${!starts[@]}"; do
  f="chunk_$(printf '%02d' "$i").mp4"
  if [ ! -s ".renders/$KARAOKE/$f" ]; then
    python production/film.py --wav "$AUDIO" --fps 16 \
      --start "${starts[$i]}" --duration "${durations[$i]}" \
      --out ".renders/$KARAOKE/$f" --karaoke "$KARAOKE"
  fi
  printf "file '%s'\n" "$f" >>".renders/$KARAOKE/concat.txt"
done
# Copy the continuous video stream, but re-mux from the original sound file
# once, avoiding segment AAC priming and cumulative audio offset.
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 \
    -i ".renders/$KARAOKE/concat.txt" -i "$AUDIO" -map 0:v:0 -map 1:a:0 \
    -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"
echo "Film render: $OUT. Karaoke mode: $KARAOKE. Acoustic accuracy requires human listening."
