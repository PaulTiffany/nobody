#!/usr/bin/env python3
"""Validate alternating *visual* storyboard gates (NOT lyric synchronization)."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'production/scene_cues.storyboard.json').read_text())
transitions=data['transitions']
assert data['schema']==1
assert data['timing_status']=='storyboard_estimate_not_vocal_aligned'
assert len(transitions)==6
assert transitions[0]['direction']=='front_to_back'
assert all(0 <= a['start'] < a['end'] <= 263.24 for a in transitions)
assert all(a['end'] < b['start'] for a,b in zip(transitions,transitions[1:]))
assert all(a['direction'] != b['direction'] for a,b in zip(transitions,transitions[1:]))
assert [e['direction'] for e in transitions].count('front_to_back')==3
assert [e['direction'] for e in transitions].count('back_to_front')==3
print('✓ Front/back scene cue ordering; NOT acoustic timing verification')
