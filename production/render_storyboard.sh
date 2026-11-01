#!/usr/bin/env bash
# Render the alternating front / reverse storyboard. No automated lyric timing.
set -euo pipefail
if [[ $# -lt 1 ]]; then echo "Usage: $0 /path/to/Nobody.wav [output.mp4] [fps]" >&2; exit 2; fi
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
AUDIO=$(realpath "$1")
OUT=$(realpath -m "${2:-$ROOT/output/nobody-front-back-cut.mp4}")
FPS=${3:-12}
cd "$ROOT"
python scripts/check_scene_cues.py
# Cache is invalidated when the song, scene schedule, source, or fps changes.
# This prevents edited crossings from silently reusing old frames.
FINGERPRINT=$({ sha256sum production/film.py production/render.py production/scene_cues.json "$AUDIO"; printf 'fps=%s\n' "$FPS"; } | sha256sum | cut -c1-16)
CACHE=".renders/frontback-$FINGERPRINT"
mkdir -p "$CACHE" "$(dirname "$OUT")"
: > "$CACHE/concat.txt"
for i in $(seq 0 10); do
  start=$((i*25))
  if [[ $i -eq 10 ]]; then duration=13.24; else duration=25; fi
  f="chunk_$(printf %02d "$i").mp4"
  cached_duration=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$CACHE/$f" 2>/dev/null || echo 0)
  if ! python - "$cached_duration" "$duration" <<'VALID'
import sys
try: assert float(sys.argv[1])>=float(sys.argv[2])-.12
except (ValueError,AssertionError): raise SystemExit(1)
VALID
  then
    rm -f "$CACHE/$f"
    echo "Rendering $f  t=$start sec"
    python production/film.py --wav "$AUDIO" --fps "$FPS" \
      --start "$start" --duration "$duration" --out "$CACHE/$f" \
      --preset veryfast --crf 28 --karaoke off
  fi
  printf "file '%s'\n" "$f" >> "$CACHE/concat.txt"
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 \
  -i "$CACHE/concat.txt" -i "$AUDIO" \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 160k \
  -t 263.24 -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"