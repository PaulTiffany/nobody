#!/usr/bin/env python3
"""Derive front/reverse scene transitions from *aligned lyrics*, not guessed minutes.

Input is Enhanced LRC from ELYSY or another upstream lyric aligner. This script
only interprets timing already present; it performs NO speech recognition and
cannot verify singing acoustically. Creator must audition and review the LRC.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

LINE_RE = re.compile(r'^\[(\d{2}):(\d{2})(?:\.(\d{2,3}))?\](.*)$')
WORD_RE = re.compile(r'<(\d{2}):(\d{2})(?:\.(\d{2,3}))?>([^<]*)')


def seconds(mm, ss, ms):
    return int(mm) * 60 + int(ss) + (int(ms or '0') / (10 ** len(ms or '0')) if ms else 0)


def normalize(value):
    return ' '.join(re.findall(r"[a-z]+(?:'[a-z]+)?", value.casefold()))


def parse_enhanced_lrc(contents):
    """Do NOT infer missing word timestamps or distribute text over a line."""
    lines = []
    for number, line in enumerate(contents.splitlines(), 1):
        line = line.strip().lstrip('\ufeff')
        if not line or line.startswith('[ti:') or line.startswith('[ar:'):
            continue
        match = LINE_RE.match(line)
        if not match:
            if line.startswith('['):  # ignore ordinary metadata
                continue
            raise ValueError(f'LRC line {number}: expected [mm:ss.xx] prefix')
        start = seconds(*match.groups()[:3]); rest = match.group(4)
        markers = list(WORD_RE.finditer(rest))
        if not markers:
            raise ValueError(f'LRC line {number}: word-level Enhanced LRC required; no word timestamps')
        words=[]
        for m in markers:
            word=normalize(m.group(4))
            if not word:  # trailing time marker terminates last note; no new word
                continue
            if len(word.split()) != 1:
                raise ValueError(f'LRC line {number}: one token per timestamp required, got {word!r}')
            words.append({'text':word, 'start':round(seconds(*m.groups()[:3]), 3)})
        if not words: raise ValueError(f'LRC line {number}: no sung words')
        if abs(start - words[0]['start']) > 2:
            raise ValueError(f'LRC line {number}: inconsistent line and first word timestamps')
        if any(a['start'] > b['start'] for a,b in zip(words,words[1:])):
            raise ValueError(f'LRC line {number}: nonmonotonic word timestamps')
        lines.append({'text':' '.join(w['text'] for w in words), 'words':words,
                      'start':words[0]['start'], 'line_number':number})
    if not lines: raise ValueError('No aligned lyric lines')
    if any(a['start'] > b['start'] for a,b in zip(lines, lines[1:])):
        raise ValueError('LRC lines must be chronologically sorted')
    return lines


def find_scenes(lines):
    """Song-specific semantic rule: enter rave at refrain, exit for next verse.

    Cut duration is taken from first 'on' to the onset of 'side'. Returns
    finish on the first sung word of the next section; start 0.6s before it.
    The latter is a director-selected *relative* transition duration, not an
    invented absolute time or word alignment.
    """
    events=[]; side='front'; rave_count=0; exit_count=0
    exits=['another promise on a screen', 'maybe were afraid of falling', 'nobody owns tomorrow']
    # Song chorus contains the last exit string too; only use it after third rave
    for line in lines:
        phrase=normalize(line['text']).replace("'", '')
        words=line['words']
        if phrase == 'on the other side' and side == 'front':
            if len(words) != 4:
                raise ValueError('Refusing transition: "on the other side" has ambiguous tokenization')
            begin=words[0]['start']; arrive=words[-1]['start']
            if arrive - begin < .25 or arrive - begin > 6:
                raise ValueError(f'Implausible on-the-other-side phrase timing {begin}-{arrive}')
            events.append({'start':begin, 'end':arrive, 'direction':'front_to_back',
                           'cue':'on the other side', 'source_line':line['line_number']})
            side='back'; rave_count+=1
        elif side == 'back':
            next_expected = {1: exits[0], 2: exits[1], 3: exits[2]}.get(rave_count)
            if phrase == next_expected:
                arrive=words[0]['start']; begin=round(arrive-.60,3)
                if begin <= events[-1]['end']:
                    raise ValueError('Return cue overlaps the ingress; review LRC')
                events.append({'start':begin,'end':arrive,'direction':'back_to_front',
                               'cue':next_expected, 'source_line':line['line_number']})
                side='front'; exit_count+=1
    if rave_count != 3 or exit_count != 3 or len(events) != 6:
        raise ValueError(f'Expected 3 refrain entrances / 3 returns, found {rave_count}/{exit_count}; '
                         'correct sung transcription or update human-directed choreography')
    if any(a['end'] > b['start'] for a,b in zip(events,events[1:])):
        raise ValueError('Overlapping scene events')
    return events


def make_cues(lrc_text, lrc_path, wav_path):
    lines=parse_enhanced_lrc(lrc_text)
    events=find_scenes(lines)
    audio_hash=hashlib.sha256(wav_path.read_bytes()).hexdigest()
    lrc_hash=hashlib.sha256(lrc_text.encode('utf-8')).hexdigest()
    return {
        'schema':1,
        'timing_status':'aligned_source_requires_creator_audition',
        'aligned_lyrics_source':lrc_path.name,
        'aligned_lyrics_sha256':lrc_hash,
        'audio_sha256':audio_hash,
        'note':'Timings copied from word-level Enhanced LRC, not acoustically verified by this script. Await listening review.',
        'transitions':events,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lrc',type=Path,required=True)
    ap.add_argument('--wav',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=Path('production/scene_cues.candidate.json'))
    args=ap.parse_args()
    if not args.lrc.is_file(): ap.error('Missing aligned Enhanced LRC; FIRST align WAV with ELYSY')
    if not args.wav.is_file(): ap.error('Missing exact source WAV')
    result=make_cues(args.lrc.read_text(encoding='utf-8'),args.lrc,args.wav)
    # Never replace production/scene_cues.json through automatic import. Only
    # an explicit, creator-auditioned promotion should make it live.
    if args.output.name == 'scene_cues.json': ap.error('Refusing to overwrite live cues with unreviewed data')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for x in result['transitions']:
        print(f"{x['direction']:>13} | {x['start']:7.3f}–{x['end']:7.3f} | {x['cue']}")
    print(f'Candidate only: {args.output}. Audition against WAV; do not render as verified until reviewed.')

if __name__=='__main__':
    main()
