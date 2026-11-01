#!/usr/bin/env python3
"""Guard that the post-refrain stage actually remains on the back side."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'production'))
import film

class TestSceneState(unittest.TestCase):
    def test_stage_changes_follow_runtime_cues(self):
        previous=film.TRANSITIONS
        film.TRANSITIONS=[
          {'start':10,'end':12,'direction':'front_to_back'},
          {'start':20,'end':21,'direction':'back_to_front'},
        ]
        try:
            self.assertEqual([film.side_at(t) for t in [9,11,13,20.5,22]],
                             ['front','crossing','back','crossing','front'])
        finally:
            film.TRANSITIONS=previous

if __name__=='__main__':unittest.main()
