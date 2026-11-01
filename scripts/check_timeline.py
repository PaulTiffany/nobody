#!/usr/bin/env python3
"""Check estimated karaoke timeline (not a replacement for manual vocal QA)."""
from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]/'production/lyrics_draft.json'
x=json.loads(p.read_text(encoding='utf-8'))
sections=x['sections']; cues=x['cues']; dur=x['audio_duration_seconds']
assert x['status'].startswith('PROVISIONAL')
assert sections[0]['start']==0
assert sections[-1]['end']==dur
assert all(abs(a['end']-b['start'])<1e-7 for a,b in zip(sections,sections[1:])), 'Sections must be contiguous'
assert all(a['end']>a['start']>=0 for a in sections)
assert all(a['end']<=b['start'] for a,b in zip(cues,cues[1:])), 'Lyric overlap'
assert all(0 <= c['start'] < c['end'] <=dur for c in cues)
assert all(c['text'].strip() for c in cues)
assert len(cues)>=40
assert any(c['text']=='On the other side' for c in cues)
print(f'✓ Timeline structurally valid: {len(cues)} phrases, {len(sections)} musical sections, {dur:.2f}s; timing UNVERIFIED')
