#!/usr/bin/env python3
"""Byte-exact reassembler for the V6 music videos tracked as Git blobs.

No internet, inference, transcoding, or third-party Python dependencies.
The checked-in parts are segments of the original H.264/AAC MP4s, never
lossily recompressed segments. Reassembly is simple byte concatenation.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
VARIANTS = {
    'master': ('Nobody_V6_COMPLETE_WITH_AUDIO.mp4', 10875633,
               'bd899cc80fefcdac0a222f3ffab3f87e41f405a83185a846330ed50e5ced007d', 15),
    'compact': ('Nobody_V6_SMALL_WITH_AUDIO.mp4', 4250328,
                '0625d6a97126575c9fd4f147bd3136694d3795e63b5c4031a0520ed254037c47', 6),
}

def assemble(kind: str, out_dir: Path) -> Path:
    name, size, digest, count = VARIANTS[kind]
    pieces = sorted((HERE/'parts').glob(name+'.part*'))
    if len(pieces) != count:
        raise SystemExit(f'{kind}: expected {count} parts, found {len(pieces)}')
    for i,p in enumerate(pieces):
        if p.name != f'{name}.part{i:03d}':
            raise SystemExit(f'{kind}: missing or out-of-order part {i:03d}: {p}')
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir/name
    h = hashlib.sha256()
    n = 0
    with target.open('wb') as out:
        for p in pieces:
            with p.open('rb') as inp:
                while data := inp.read(1024*1024):
                    n += len(data); h.update(data); out.write(data)
    if n != size or h.hexdigest() != digest:
        target.unlink(missing_ok=True)
        raise SystemExit(f'{kind}: INVALID size/hash: {n} bytes, {h.hexdigest()}')
    print(f'OK {kind}: {target}, {n:,} bytes, SHA256 {digest}')
    return target

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--variant', choices=['master','compact','both'], default='both')
    ap.add_argument('--out', type=Path, default=HERE/'rendered')
    args = ap.parse_args()
    for kind in (('master','compact') if args.variant == 'both' else (args.variant,)):
        assemble(kind, args.out)
