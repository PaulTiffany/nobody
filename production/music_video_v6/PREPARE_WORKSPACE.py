#!/usr/bin/env python3
"""Stage a reproducible V6 workspace WITHOUT copying/committing song audio.

Usage: python PREPARE_WORKSPACE.py /path/to/work  [--wav /path/to/song.wav]
Then set NOBODY_MEDIA_ROOT to the chosen work path and run V6 renderer.
"""
import argparse, shutil
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('work'); ap.add_argument('--wav',type=Path);a=ap.parse_args()
w=Path(a.work).resolve();w.mkdir(parents=True,exist_ok=True)
shutil.copy2(Path(__file__).with_name('nobody_suno_word_alignment.json'), w/'nobody_suno_word_alignment.json')
if a.wav:shutil.copy2(a.wav,w/'Nobody Owns Tomorrow(1).wav')
print(f'Ready: {w}. Set NOBODY_MEDIA_ROOT={w} and run the V6 renderer.')
