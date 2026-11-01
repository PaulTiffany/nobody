#!/usr/bin/env python3
"""No audio model or large assets required. Deterministic format/choreography tests."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from derive_scene_cues import parse_enhanced_lrc, find_scenes

def lrc_line(t, words, interval=.45):
    def stamp(t,word=False):
        mm, ss = divmod(t,60)
        return f'{int(mm):02d}:{ss:06.3f}' if word else f'{int(mm):02d}:{ss:05.2f}'
    return '['+stamp(t)+']' + ''.join(f'<{stamp(t+i*interval,True)}>{w} ' for i,w in enumerate(words.split()))

SAMPLE='\n'.join([
    lrc_line(80,'On the other side'),lrc_line(84,'On the other side'),
    lrc_line(100,'Another promise on a screen'),
    lrc_line(180,'On the other side'),lrc_line(184,'On the other side'),
    lrc_line(190,"Maybe we're afraid of falling"),
    lrc_line(237,'On the other side'),lrc_line(241,'On the other side'),
    lrc_line(260,'Nobody owns tomorrow'),
])

class TestTiming(unittest.TestCase):
    def test_exact_timing_from_lrc(self):
        scenes=find_scenes(parse_enhanced_lrc(SAMPLE))
        self.assertEqual([s['direction'] for s in scenes], ['front_to_back','back_to_front']*3)
        self.assertEqual([(s['start'],s['end']) for s in scenes], [(80,81.35),(99.4,100),(180,181.35),(189.4,190),(237,238.35),(259.4,260)])
    def test_missing_words_do_not_get_fabricated_timestamps(self):
        with self.assertRaisesRegex(ValueError,'word-level'):
            parse_enhanced_lrc('[01:20.00]On the other side')
    def test_missing_verses_rejected(self):
        with self.assertRaisesRegex(ValueError,'Expected 3'):
            find_scenes(parse_enhanced_lrc(lrc_line(80,'On the other side')))
    def test_nonchronological_rejected(self):
        with self.assertRaisesRegex(ValueError,'chronologically'):
            parse_enhanced_lrc(lrc_line(20,'hello')+'\n'+lrc_line(10,'world'))
    def test_bad_interval_rejected(self):
        with self.assertRaisesRegex(ValueError,'Implausible'):
            find_scenes(parse_enhanced_lrc(lrc_line(80,'On the other side',.01)))

if __name__=='__main__':unittest.main()
