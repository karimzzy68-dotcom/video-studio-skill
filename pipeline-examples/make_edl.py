"""Writes edl.json for each ad project: one segment per spoken phrase, dead air removed but a natural breath kept
on both sides (so the next line never starts instantly). Alternate segments get a gentle punch-in for variety."""
import json, os, re, subprocess, sys

ROOT = r"D:\video eidting with claude\reel-edits"
PRE, POST, GAP = 0.12, 0.22, 0.35   # breath before / after each phrase; pauses longer than GAP get trimmed
FIX = {'Knox': 'NOX47', 'NOX': 'NOX47', 'Rock edits': 'Rockettes'}

def silence_starts(src):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-af', 'silencedetect=n=-30dB:d=0.1', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]


for slug in sys.argv[1:] or sorted(os.listdir(ROOT)):
    proj = os.path.join(ROOT, slug)
    words = json.load(open(os.path.join(proj, 'words_c1.json'), encoding='utf-8'))
    src = json.load(open(os.path.join(proj, 'sources.json'), encoding='utf-8'))['c1']
    dur = float(os.popen(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{src}"').read())
    sil = silence_starts(src)
    groups, cur = [], [words[0]]
    for w in words[1:]:
        if w['start'] - cur[-1]['end'] > GAP:
            groups.append(cur); cur = [w]
        else:
            cur.append(w)
    groups.append(cur)
    edl = []
    for k, g in enumerate(groups):
        a = max(0.0, g[0]['start'] - PRE)
        # Whisper's word ends run early: end on the real silence after the last word (+ a breath), never mid-word
        real_end = next((s for s in sil if s > g[-1]['end'] - 0.25), dur)
        b = max(g[-1]['end'] + POST, real_end + 0.12)
        if k + 1 < len(groups):
            b = min(b, groups[k + 1][0]['start'] - PRE)
        else:
            b = dur - 0.01   # last line: keep everything to the end of the source, the tail is held in mix_music.py
        if edl and a < edl[-1]['out']:
            a = edl[-1]['out']
        edl.append({'id': f's{k}', 'clip': 'c1', 'in': round(a, 3), 'out': round(b, 3),
                    'zoom': 1.0 if k % 2 == 0 else 1.12, 'cx': 0.5, 'cy': 0.4,
                    'line': ' '.join(w['text'] for w in g)})
    json.dump(edl, open(os.path.join(proj, 'edl.json'), 'w', encoding='utf-8'), indent=1)
    print(slug, f"{dur:.1f}s ->", round(sum(s['out'] - s['in'] for s in edl), 2), 's,', len(edl), 'segments')
