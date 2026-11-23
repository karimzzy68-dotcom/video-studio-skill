#!/usr/bin/env python3
"""Halloween builds for the six ads (adapted from the /video-edit template's looks).

Usage, from anywhere:  PY halloween_build.py <slug> [--safe]
Reads <project>/segments.json, words.json, work/headpos.txt and writes <project>/index.html.

Two looks:
  NOX47 ads (n*)      cool girl: warm faded grade, calm lowercase Inter captions, butter-yellow Instrument Serif italic
                      punch words; ember glow, drifting fog, candle flicker, rim-lit bats; blur dissolve + warm light
                      leak at every cut.
  Rockettes ads (r*)  midnight moonlight: cool navy/violet grade, tracked Montserrat caps + moonlight-blue DM Serif
                      italic punch words (cool dude type); full moon with passing clouds behind her, falling silver
                      glitter, silver cobwebs drawn in the top corners, a spider dropping in on the CTA; lightning flash
                      + zoom punch at every cut.
Both: the hook's punch word sits BEHIND her head (cutout on top). The cutout (assets/subject.webm) only covers the
opening (SUBJ_END), so nothing is placed behind her after that.
"""
import html as H
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys

ROOT = r"D:\video eidting with claude\reel-edits"
TEMPLATE = r"C:\Users\Lenovo\.claude\skills\video-edit\assets\template"

ADS = {
    'n1': dict(behind=('s0', 'wicked'), punch={'s1': 'not a blue pill', 's2': 'warm tingle', 's3': 'find me',
                                                's4': 'halloween offer', 's5': 'trick or treat'}),
    'n2': dict(behind=('s1', 'naughty'), punch={'s2': 'restaurant', 's3': 'warm tingle', 's4': 'get freaky',
                                                 's5': 'halloween offer', 's6': 'wickedly'}),
    'n4': dict(behind=('s0', 'halloween'), punch={'s3': 'still on', 's4': 'warm rush', 's5': 'about us',
                                                   's6': 'halloween offer'}),
    'r1': dict(behind=('s0', 'naughty'), punch={'s1': 'for you', 's2': 'single use wipes', 's3': 'done',
                                                 's4': 'no blue pill', 's5': 'all yours', 's6': 'before halloween'}),
    'r3': dict(behind=('s0', 'halloween'), punch={'s1': 'tiny packet', 's2': 'no planning', 's3': 'wicked',
                                                   's4': 'link below', 's5': '$1.46 a night'}),
    'r4': dict(behind=('s0', 'adults'), punch={'s1': 'naughty', 's2': 'discreet', 's3': 'no blue pill',
                                                's4': 'tonight'}),
}

slug = sys.argv[1]
SAFE = '--safe' in sys.argv
P = os.path.join(ROOT, slug)
CFG = ADS[slug]
ROCK = slug.startswith('r')
random.seed(sum(map(ord, slug)))

if ROCK:
    ACC, INK = '#BFD4FF', '#F2F5FF'
    GRADE = 'contrast(1.08) saturate(.88) brightness(.97) hue-rotate(-6deg)'
    SPARK_C = '#E6EEFF'
else:
    ACC, INK = '#FAE67A', '#FFF8EF'
    GRADE = 'sepia(.18) saturate(.92) contrast(.95) brightness(1.04) hue-rotate(-5deg)'
    SPARK_C = '#FAE67A'

for sub in ('fonts', 'sfx'):
    dst = os.path.join(P, 'assets', sub)
    if not os.path.isdir(dst):
        shutil.copytree(os.path.join(TEMPLATE, 'assets', sub), dst)
for f in ('hyperframes.json', 'package.json'):
    if not os.path.exists(os.path.join(P, f)):
        shutil.copy(os.path.join(TEMPLATE, f), P)


def vdur(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                       capture_output=True, text=True).stdout.strip()
    return float(r) if r else 0.0


DUR = vdur(os.path.join(P, 'assets', 'aroll.mp4'))
SUBJ_END = vdur(os.path.join(P, 'assets', 'subject.webm')) - .05   # cutout covers 0..SUBJ_END only
SEGS = json.load(open(os.path.join(P, 'segments.json'), encoding='utf-8'))
for s in SEGS:
    s['t0'] = s['frame'] / 30 - .002 if s['frame'] else 0.0
    s['t1'] = (s['frame'] + s['frames']) / 30
CUTS = [s['t0'] for s in SEGS[1:]]
CTA_T = SEGS[-1]['t0']
LAST_WORD_END = 0.0

HEAD = {}
hp = os.path.join(P, 'work', 'headpos.txt')
if os.path.exists(hp):
    for line in open(hp, encoding='utf-8-sig'):
        tops = [int(x) for x in re.findall(r'head top\s+(\d+)', line)]
        if tops:
            HEAD[line.split()[0]] = sorted(tops)[len(tops) // 2]


# ------------------------------------------------------------------ words -> clean caption tokens
def tokens():
    raw = json.load(open(os.path.join(P, 'words.json'), encoding='utf-8'))
    out = []
    for w in raw:
        t = w['text']
        if re.match(r'(?i)^thanks', t) and w['start'] > DUR - 1.5:
            break   # Whisper's phantom "Thanks for watching!" at the very end
        if out and (t.startswith('-') or t.startswith('.') and t[1:2].isdigit()):
            out[-1]['text'] += t
            continue
        if out and out[-1]['text'].lower().rstrip(',.') in ('knox', 'nox') and t.rstrip(',.') == '47':
            out[-1]['text'] = 'NOX47' + t[2:]
            continue
        if out and out[-1]['text'].lower() == 'rock' and t.lower().startswith('edits'):
            out[-1]['text'] = 'Rockettes' + t[5:]
            continue
        out.append(dict(text=t, start=w['start'], end=w['end']))
    clean = []
    for w in out:
        t = re.sub(r'(?i)^knox$', 'NOX47', w['text'])
        keep_case = re.match(r'(?i)^(nox47|rockettes)', t)
        t = t if keep_case else t.lower()
        if keep_case:
            t = 'NOX47' + t[5:] if t.lower().startswith('nox47') else 'Rockettes' + t[9:]
        brk = bool(re.search(r'[,.!?]$', t))
        t = re.sub(r'[,.!?]+$', '', t) if not re.match(r'^\$?\d', t) else t.rstrip(',!?')
        t = t.rstrip('.') if not re.search(r'\d\.\d', t) else t
        if t:
            clean.append(dict(text=t, start=w['start'], end=w['end'], brk=brk))
    return clean


WORDS = tokens()
LAST_WORD_END = WORDS[-1]['end'] if WORDS else DUR


def seg_words(s):
    return [w for w in WORDS if s['t0'] - .08 <= w['start'] < s['t1'] - .05]


def find_phrase(ws, phrase):
    p = phrase.lower().split()
    for i in range(len(ws) - len(p) + 1):
        if [w['text'].lower() for w in ws[i:i + len(p)]] == p:
            return i, i + len(p)
    return None


BLOCKS = []   # (id, start, end, before, punch, after, behind)
for k, s in enumerate(SEGS):
    ws = seg_words(s)
    if not ws:
        continue
    end = SEGS[k + 1]['t0'] if k + 1 < len(SEGS) else DUR
    behind = CFG['behind'][0] == s['id']
    phrase = CFG['behind'][1] if behind else CFG['punch'].get(s['id'])
    span = find_phrase(ws, phrase) if phrase else None
    parts = [(ws, span)]
    if len(ws) > 10:   # long line: two blocks, split at the speaker's comma / before "and" / longest pause
        mid = len(ws) // 2
        cut = min(range(2, len(ws) - 2), key=lambda i: (-ws[i - 1]['brk'] - .6 * (ws[i]['text'] in ('and', 'then', 'but', 'just'))
                                                      - (ws[i]['start'] - ws[i - 1]['end']) + abs(i - mid) * .05))
        if span and span[0] < cut < span[1]:
            cut = span[0]
        a, b = ws[:cut], ws[cut:]
        sa = (span[0], span[1]) if span and span[1] <= cut else None
        sb = (span[0] - cut, span[1] - cut) if span and span[0] >= cut else None
        parts = [(a, sa), (b, sb)]
    for j, (pw, sp) in enumerate(parts):
        a = s['t0'] if j == 0 else pw[0]['start'] - .06
        b = parts[j + 1][0][0]['start'] - .06 if j + 1 < len(parts) else end
        if sp:
            BLOCKS.append((f'b{k}{j}', a, b, pw[:sp[0]], pw[sp[0]:sp[1]], pw[sp[1]:], behind))
        else:
            BLOCKS.append((f'b{k}{j}', a, b, pw, [], [], False))


# ------------------------------------------------------------------ captions
def small_in(gid, t):
    if ROCK:   # cool-dude "track in": scaleX + blur (letterSpacing tweens are rejected by lint)
        return (f"tl.fromTo('#{gid}',{{autoAlpha:0,scaleX:1.45,filter:'blur(8px)'}},{{autoAlpha:1,scaleX:1,filter:'blur(0px)',"
                f"duration:.42,ease:'power3.out',immediateRender:false}},{t:.3f});")
    return (f"tl.fromTo('#{gid}',{{autoAlpha:0,y:16,filter:'blur(6px)'}},{{autoAlpha:1,y:0,filter:'blur(0px)',"
            f"duration:.32,ease:'power2.out',immediateRender:false}},{t:.3f});")


def punch_in(gid, t):
    if ROCK:   # serif letters rise from a mask
        return [f"tl.fromTo('#{gid} .ch',{{yPercent:115}},{{yPercent:0,duration:.6,ease:'expo.out',stagger:.03,immediateRender:false}},{t:.3f});",
                f"tl.fromTo('#{gid}',{{autoAlpha:0,filter:'blur(8px)'}},{{autoAlpha:1,filter:'blur(0px)',duration:.35,ease:'power2.out',immediateRender:false}},{t:.3f});"]
    return [f"tl.fromTo('#{gid}',{{autoAlpha:0,y:26,scale:.9,filter:'blur(12px)'}},{{autoAlpha:1,y:0,scale:1,filter:'blur(0px)',"
            f"duration:.5,ease:'power3.out',immediateRender:false}},{t:.3f});"]


def masked(text):
    return ''.join(f'<span class="mk"><span class="ch">{"&nbsp;" if c == " " else H.escape(c)}</span></span>' for c in text)


def captions():
    html, tw, sparks = [], [], []
    for bid, a, b, before, punch, after, behind in BLOCKS:
        lines = []
        rows = (('s', before + after), ('e', []), ('s', [])) if behind else (('s', before), ('e', punch), ('s', after))
        for li, (kind, ws) in enumerate(rows):
            if not ws:
                continue
            spans = []
            # punch line must fit 900px: shrink long phrases (average glyph width ~.52em DM Serif, ~.42em Instrument)
            fit = '' if kind != 'e' else f' style="font-size:{min(140 if ROCK else 150, 900 / ((.52 if ROCK else .42) * len(" ".join(w["text"] for w in ws)))):.0f}px"'
            if kind == 'e' and ROCK:
                gid = f'{bid}-{li}'
                spans.append(f'<span id="{gid}" class="gw">{masked(" ".join(w["text"] for w in ws))}</span>')
                tw += punch_in(gid, max(a, ws[0]['start'] - .05))
            else:
                for n, w in enumerate(ws):
                    gid = f'{bid}-{li}-{n}'
                    txt = w['text'].upper() if ROCK and kind == 's' and not w['text'].startswith('$') else w['text']
                    spans.append(f'<span id="{gid}" class="gw">{H.escape(txt)}</span>')
                    t = max(a, w['start'] - .05)
                    tw += [small_in(gid, t)] if kind == 's' else punch_in(gid, t)
            lines.append(f'<div class="{kind}"{fit}>{" ".join(spans)}</div>')
        html.append(f'<div id="{bid}" class="gcap">{"".join(lines)}</div>')
        tw.append(f"gsap.set('#{bid} .gw',{{autoAlpha:0}});")
        if b < DUR - .05:
            tw.append(f"tl.to('#{bid}',{{autoAlpha:0,filter:'blur(8px)',duration:.18}},{b - .18:.3f});")
            tw.append(f"tl.set('#{bid}',{{autoAlpha:0}},{b:.3f});")
        if punch and not behind and min(b, DUR - .1) - punch[0]['start'] > .8:
            sparks.append((punch[0]['start'], min(b, DUR - .1)))
    return html, tw, sparks


def behind_word():
    """the hook's punch word, big serif italic BEHIND her head (layout.md formula)"""
    for bid, a, b, before, punch, after, behind in BLOCKS:
        if not behind or not punch:
            continue
        seg = CFG['behind'][0]
        S = 220 if len(' '.join(w['text'] for w in punch)) <= 8 else 180
        head = HEAD.get(seg, 420)
        top = max(228, round(head + .15 * S - .72 * S))
        text = ' '.join(w['text'] for w in punch)
        t = punch[0]['start'] - .06
        b = min(max(b, t + 2.2), SUBJ_END)   # a word spoken at the end of a short line still gets ~2s on screen
        html = [f'<div id="bw" class="bword" style="top:{top}px;font-size:{S}px">{masked(text)}</div>']
        tw = ["gsap.set('#bw',{autoAlpha:0});", f"tl.set('#bw',{{autoAlpha:1}},{t:.3f});",
              f"tl.fromTo('#bw .ch',{{yPercent:110,autoAlpha:0}},{{yPercent:0,autoAlpha:1,duration:.7,ease:'expo.out',stagger:.035,immediateRender:false}},{t:.3f});",
              f"tl.fromTo('#bw',{{scale:1.08,filter:'blur(10px)'}},{{scale:1,filter:'blur(0px)',duration:.6,ease:'power3.out',immediateRender:false}},{t:.3f});",
              f"tl.to('#bw',{{autoAlpha:0,filter:'blur(12px)',duration:.25}},{b - .25:.3f});",
              f"tl.set('#bw',{{autoAlpha:0}},{b:.3f});"]
        return html, tw, (t, b, top, S)
    return [], [], None


def sparkles(spots, bw):
    html, tw = [], []
    n = 0
    glyph = '&#10023;' if ROCK else '&#10022;'
    plan = [(t, b, [(170, 1180, 46), (900, 1240, 34), (860, 1110, 24)]) for t, b in spots]
    if bw:
        t, b, top, S = bw
        plan.insert(0, (t + .2, b, [(120, top + 40, 56), (940, top + 10, 40), (900, top + S * .75, 28)]))
    for t, b, pts in plan:
        for x, y, sz in pts:
            sid = f'sp{n}'; n += 1
            html.append(f'<div id="{sid}" class="spark" style="left:{x}px;top:{y:.0f}px;font-size:{sz}px">{glyph}</div>')
            t_in = t + .1 * (n % 3)
            tw += [f"gsap.set('#{sid}',{{autoAlpha:0,scale:0,rotation:-30}});",
                   f"tl.to('#{sid}',{{autoAlpha:1,scale:1,rotation:0,duration:.35,ease:'back.out(2.5)'}},{t_in:.3f});"]
            reps = int((b - .25 - (t_in + .4)) / .45) - 1
            if reps >= 1:
                reps = reps if reps % 2 else reps - 1
                if reps >= 1:
                    tw.append(f"tl.to('#{sid}',{{scale:.6,duration:.45,yoyo:true,repeat:{reps},ease:'sine.inOut'}},{t_in + .4:.3f});")
            if b < DUR - .05:
                tw.append(f"tl.to('#{sid}',{{autoAlpha:0,scale:0,duration:.2}},{b - .2:.3f});")
    return html, tw


# ------------------------------------------------------------------ NOX47 halloween layer
BAT_SVG = ('<svg viewBox="0 0 200 90" width="{w}" height="{h}"><g fill="#120a14">'
           '<path class="wl" d="M100 45 C 88 30, 70 22, 52 26 C 46 16, 34 12, 22 16 C 26 24, 20 30, 6 34 '
           'C 22 38, 34 46, 40 60 C 52 50, 70 50, 86 58 C 90 52, 96 48, 100 45 Z" style="transform-origin:100px 45px"/>'
           '<path class="wr" d="M100 45 C 112 30, 130 22, 148 26 C 154 16, 166 12, 178 16 C 174 24, 180 30, 194 34 '
           'C 178 38, 166 46, 160 60 C 148 50, 130 50, 114 58 C 110 52, 104 48, 100 45 Z" style="transform-origin:100px 45px"/>'
           '<ellipse cx="100" cy="47" rx="7" ry="11"/><path d="M94 38 L95 29 L99 36 Z M106 38 L105 29 L101 36 Z"/></g></svg>')


def bats():
    html, tw = [], []
    end = min(3.4, SUBJ_END - .05)   # they fly behind her, so only while the cutout exists
    flock = [(1180, 330, -760, 250, 92), (1300, 420, -600, 300, 64), (1250, 260, -500, 200, 48)]
    a = 0.35
    for n, (x0, y0, x1, y1, w) in enumerate(flock):
        bid = f'bat{n}'
        html.append(f'<div id="{bid}" class="bat">{BAT_SVG.format(w=w, h=round(w * .45))}</div>')
        d = end - a
        tw += [f"gsap.set('#{bid}',{{x:{x0},y:{y0},autoAlpha:0,scaleX:-1}});",
               f"tl.set('#{bid}',{{autoAlpha:.95}},{a:.3f});",
               f"tl.to('#{bid}',{{keyframes:[{{x:{(x0 + x1) / 2:.0f},y:{(y0 + y1) / 2 - 60:.0f},duration:{d / 2:.2f},ease:'sine.inOut'}},"
               f"{{x:{x1},y:{y1},duration:{d / 2:.2f},ease:'sine.in'}}]}},{a:.3f});",
               f"tl.fromTo('#{bid} .wl,#{bid} .wr',{{scaleY:1}},{{scaleY:-.35,duration:.11,yoyo:true,repeat:{int(d / .11) | 1},ease:'sine.inOut',immediateRender:false}},{a:.3f});",
               f"tl.set('#{bid}',{{autoAlpha:0}},{end:.3f});"]
    return html, tw


def embers():
    html, tw = [], []
    n, t = 0, 0.2
    while t < DUR - 1:
        for _ in range(3):
            x = random.choice((random.uniform(50, 270), random.uniform(810, 1010)))
            sz = random.uniform(6, 13)
            life = random.uniform(3.5, 5.5)
            eid = f'em{n}'; n += 1
            html.append(f'<div id="{eid}" class="ember" style="left:{x:.0f}px;width:{sz:.1f}px;height:{sz:.1f}px"></div>')
            y0, y1, sway = random.uniform(1500, 1750), random.uniform(500, 900), random.uniform(-70, 70)
            end = min(t + life, DUR)
            tw += [f"gsap.set('#{eid}',{{y:{y0:.0f},opacity:0}});",
                   f"tl.to('#{eid}',{{keyframes:[{{y:{(y0 + y1) / 2:.0f},x:{sway:.0f},opacity:.85,duration:{(end - t) / 2:.2f},ease:'sine.out'}},"
                   f"{{y:{y1:.0f},x:{-sway / 2:.0f},opacity:0,duration:{(end - t) / 2:.2f},ease:'sine.in'}}]}},{t:.3f});"]
        t += random.uniform(.6, 1.0)
    return html, tw


def flicker():
    kf, t = [], 0.0
    while t < DUR:
        d = random.uniform(.12, .3)
        kf.append(f"{{opacity:{random.uniform(.55, 1):.2f},duration:{d:.2f},ease:'sine.inOut'}}")
        t += d
    return [f"tl.to('#flick',{{keyframes:[{','.join(kf)}]}},0);"]


def fog():
    return [f"tl.fromTo('#fog1',{{x:-160}},{{x:120,duration:{DUR:.2f},ease:'none',immediateRender:false}},0);",
            f"tl.fromTo('#fog2',{{x:140}},{{x:-150,duration:{DUR:.2f},ease:'none',immediateRender:false}},0);"]


def nox_transitions():
    # opening: sharp from frame 0 (Instagram can use it as the cover), a slow push-out plus a warm light leak sweep
    tw = [f"tl.fromTo('#stage',{{scale:1.07}},{{scale:1,duration:1.1,ease:'power2.out',immediateRender:false}},0);",
          "tl.fromTo('#leak',{opacity:0,xPercent:-40},{opacity:.6,xPercent:0,duration:.35,ease:'power1.out',immediateRender:false},.12);",
          "tl.to('#leak',{opacity:0,xPercent:40,duration:.7,ease:'power2.out'},.47);"]
    for i, t in enumerate(CUTS):
        side = -40 if i % 2 else 40
        tw += [f"tl.fromTo('#stage',{{filter:'blur(14px) brightness(1.22)',scale:1.045}},{{filter:'blur(0px) brightness(1)',scale:1,duration:.42,ease:'power2.out',immediateRender:false}},{t:.3f});",
               f"tl.set('#stage',{{filter:'none'}},{t + .43:.3f});",
               f"tl.fromTo('#leak',{{opacity:0,xPercent:{-side}}},{{opacity:.75,xPercent:0,duration:.16,ease:'power1.out',immediateRender:false}},{t - .1:.3f});",
               f"tl.to('#leak',{{opacity:0,xPercent:{side},duration:.5,ease:'power2.out'}},{t + .06:.3f});"]
    return tw


# ------------------------------------------------------------------ Rockettes midnight layer
def moon():
    """full moon behind her (top right) with two clouds drifting across; only while the cutout exists"""
    end = SUBJ_END
    html = ['<div id="moonw"><div id="moon"></div><div id="cl1" class="cloud"></div><div id="cl2" class="cloud"></div></div>']
    tw = ["gsap.set('#moonw',{autoAlpha:0});",
          f"tl.fromTo('#moonw',{{autoAlpha:0,y:40}},{{autoAlpha:1,y:0,duration:1.2,ease:'power2.out',immediateRender:false}},.15);",
          f"tl.fromTo('#moon',{{scale:.96}},{{scale:1.03,duration:{end:.2f},ease:'none',immediateRender:false}},0);",
          f"tl.fromTo('#cl1',{{x:-260}},{{x:200,duration:{end:.2f},ease:'none',immediateRender:false}},0);",
          f"tl.fromTo('#cl2',{{x:220}},{{x:-180,duration:{end:.2f},ease:'none',immediateRender:false}},0);",
          f"tl.to('#moonw',{{autoAlpha:0,duration:.3}},{end - .3:.3f});", f"tl.set('#moonw',{{autoAlpha:0}},{end:.3f});"]
    return html, tw


def web_path(size):
    """spoke-and-thread corner web, origin top-left corner"""
    spokes = [math.radians(a) for a in (0, 18, 38, 58, 76, 90)]
    d = []
    for a in spokes:
        d.append(f'M0 0 L{size * math.cos(a):.1f} {size * math.sin(a):.1f}')
    for r in (.22, .4, .58, .76, .92):
        pts = [(size * r * math.cos(a), size * r * math.sin(a)) for a in spokes]
        seg = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            seg += f' Q{mx * .9:.1f} {my * .9:.1f} {x1:.1f} {y1:.1f}'   # threads sag toward the corner
        d.append(seg)
    return ' '.join(d)


def webs():
    size = 250
    path = web_path(size)
    html = [f'<svg id="webL" class="web" width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="left:36px;top:222px">'
            f'<path d="{path}" pathLength="1"/></svg>',
            f'<svg id="webR" class="web" width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="right:36px;top:222px;transform:scaleX(-1)">'
            f'<path d="{path}" pathLength="1"/></svg>']
    tw = ["gsap.set('.web path',{strokeDasharray:1,strokeDashoffset:1});",
          "tl.to('#webL path',{strokeDashoffset:0,duration:1.6,ease:'power2.inOut'},.2);",
          "tl.to('#webR path',{strokeDashoffset:0,duration:1.6,ease:'power2.inOut'},.45);",
          f"tl.fromTo('#webL',{{rotation:0}},{{rotation:1.5,duration:2.2,yoyo:true,repeat:{max(1, int(DUR / 2.2) - 1) | 1},ease:'sine.inOut',transformOrigin:'0% 0%',immediateRender:false}},1.8);"]
    return html, tw


SPIDER = ('<svg width="54" height="60" viewBox="0 0 54 60"><g stroke="#0d0d14" stroke-width="2.6" fill="none" stroke-linecap="round">'
          '<path d="M27 30 L10 18 L4 8 M27 32 L8 30 L1 26 M27 34 L9 42 L4 52 M27 36 L14 50 L12 58 '
          'M27 30 L44 18 L50 8 M27 32 L46 30 L53 26 M27 34 L45 42 L50 52 M27 36 L40 50 L42 58"/></g>'
          '<ellipse cx="27" cy="36" rx="9" ry="11" fill="#0d0d14"/><circle cx="27" cy="23" r="6.5" fill="#0d0d14"/>'
          '<circle cx="25" cy="22" r="1.4" fill="#BFD4FF"/><circle cx="29" cy="22" r="1.4" fill="#BFD4FF"/></svg>')


def spider():
    a = CTA_T + .2
    html = [f'<div id="spw"><div id="thread"></div><div id="spider">{SPIDER}</div></div>']
    tw = ["gsap.set('#spw',{autoAlpha:0});", "gsap.set('#thread',{scaleY:0});", "gsap.set('#spider',{y:-60});",
          f"tl.set('#spw',{{autoAlpha:1}},{a:.3f});",
          f"tl.to('#thread',{{scaleY:1,duration:1.1,ease:'bounce.out'}},{a:.3f});",
          f"tl.to('#spider',{{y:300,duration:1.1,ease:'bounce.out'}},{a:.3f});",
          f"tl.to('#spw',{{rotation:4,duration:1.3,yoyo:true,repeat:5,ease:'sine.inOut',transformOrigin:'50% 0%'}},{a + 1.1:.3f});"]
    return html, tw


def glitter():
    html, tw = [], []
    n, t = 0, 0.3
    while t < DUR - .8:
        for _ in range(2):
            x = random.choice((random.uniform(60, 280), random.uniform(800, 1000)))
            sz = random.uniform(14, 30)
            life = random.uniform(3.2, 5)
            gid = f'gl{n}'; n += 1
            html.append(f'<div id="{gid}" class="glit" style="left:{x:.0f}px;font-size:{sz:.0f}px">&#10022;</div>')
            y0, y1 = random.uniform(230, 500), random.uniform(1100, 1450)
            end = min(t + life, DUR)
            d = end - t
            tw += [f"gsap.set('#{gid}',{{y:{y0:.0f},opacity:0,rotation:0}});",
                   f"tl.to('#{gid}',{{keyframes:[{{opacity:.95,duration:{d * .2:.2f}}},{{opacity:.5,duration:{d * .3:.2f}}},"
                   f"{{opacity:.9,duration:{d * .3:.2f}}},{{opacity:0,duration:{d * .2:.2f}}}]}},{t:.3f});",
                   f"tl.to('#{gid}',{{y:{y1:.0f},x:{random.uniform(-50, 50):.0f},rotation:{random.choice((-1, 1)) * random.uniform(90, 240):.0f},duration:{d:.2f},ease:'none'}},{t:.3f});"]
        t += random.uniform(.45, .8)
    return html, tw


def rock_transitions():
    def flash(t, big=False):
        p = .85 if big else .6
        return (f"tl.fromTo('#flash',{{opacity:0}},{{keyframes:[{{opacity:{p},duration:.04}},{{opacity:.08,duration:.06}},"
                f"{{opacity:{p * .7:.2f},duration:.04}},{{opacity:0,duration:.3,ease:'power2.out'}}],immediateRender:false}},{t:.3f});")
    tw = [flash(0.3),   # not on frame 0: Instagram can use the first frame as the cover
          f"tl.fromTo('#stage',{{filter:'blur(16px) brightness(.25) saturate(.5)',scale:1.1}},{{filter:'blur(0px) brightness(1) saturate(1)',scale:1,duration:.85,ease:'expo.out',immediateRender:false}},.1);",
          "tl.set('#stage',{filter:'none'},.97);"]
    for t in CUTS:
        tw += [flash(t - .06),
               f"tl.fromTo('#stage',{{scale:1.1,filter:'blur(7px) saturate(.6)'}},{{scale:1,filter:'blur(0px) saturate(1)',duration:.38,ease:'expo.out',immediateRender:false}},{t:.3f});",
               f"tl.set('#stage',{{filter:'none'}},{t + .39:.3f});"]
    return tw


# ------------------------------------------------------------------ audio
SFX_GAIN = 0.75


def audio(bw):
    sfx = [('whoosh-short', max(0, t - .12), .2) for t in CUTS]
    if bw:
        sfx.append(('sparkle', bw[0] + .15, .2))
    if ROCK:
        sfx.append(('impact-bass-1', 0.04, .28))
    LEN = {'whoosh-short': .57, 'sparkle': 1.8, 'impact-bass-1': 1.5}
    out, lanes = [], []
    for k, (name, t, vol) in enumerate(sorted(sfx, key=lambda x: x[1])):
        d = min(LEN[name], DUR - t)
        lane = next((i for i, e in enumerate(lanes) if e <= t), None)
        if lane is None:
            lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = t + d
        out.append(f'<audio id="sfx{k}" src="assets/sfx/{name}.mp3" data-start="{t:.3f}" data-duration="{d:.3f}" '
                   f'data-track-index="{10 + lane}" data-volume="{vol * SFX_GAIN:.3f}"></audio>')
    return out


# ------------------------------------------------------------------ css
BASE_CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
#stage{{position:absolute;inset:0;transform-origin:50% 42%}}
.full{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#bgv{{z-index:0}}
#cutwrap{{position:absolute;inset:0;z-index:4}}
.fx{{position:absolute;inset:0;pointer-events:none}}
.bword{{position:absolute;left:0;right:0;z-index:3;text-align:center;color:{ACC};font-style:italic;font-weight:400;line-height:1;
  letter-spacing:-.01em;white-space:nowrap}}
.mk{{display:inline-block;overflow:hidden;padding:0 .04em .16em;margin-bottom:-.16em;vertical-align:bottom}}
.ch{{display:inline-block}}
.gcap{{position:absolute;left:60px;right:60px;bottom:478px;z-index:9;text-align:center;color:{INK}}}
.gw{{display:inline-block}}
.spark{{position:absolute;z-index:9;color:{SPARK_C};line-height:1}}
'''

NOX_CSS = f'''
.bword{{font-family:'Instrument Serif';text-shadow:0 10px 50px rgba(70,30,10,.45)}}
.bat{{position:absolute;left:0;top:0;z-index:2;filter:drop-shadow(0 0 3px rgba(255,190,110,.95)) drop-shadow(0 0 14px rgba(255,130,50,.6))}}
#gwarm{{z-index:7;background:linear-gradient(180deg,rgba(255,226,200,.10),rgba(255,196,170,.16));mix-blend-mode:soft-light}}
#htone{{z-index:7;background:linear-gradient(180deg,rgba(95,45,150,.20) 0%,rgba(95,45,150,0) 38%,rgba(255,120,30,0) 62%,rgba(255,120,30,.20) 100%);mix-blend-mode:soft-light}}
#gvig{{z-index:7;background:radial-gradient(120% 70% at 50% 42%,rgba(255,255,255,0) 50%,rgba(40,18,30,.42) 100%)}}
#ggrad{{z-index:7;background:linear-gradient(180deg,rgba(40,20,35,.34) 0%,rgba(40,20,35,0) 26%,rgba(40,24,18,0) 56%,rgba(30,16,12,.55) 100%)}}
#flick{{z-index:7;background:radial-gradient(90% 60% at 50% 30%,rgba(255,170,90,.16),rgba(255,140,60,0) 70%);mix-blend-mode:screen;opacity:.8}}
.fog{{position:absolute;left:-200px;width:1480px;height:760px;bottom:-120px;z-index:7;mix-blend-mode:screen;opacity:.55;
  background:radial-gradient(40% 32% at 22% 70%,rgba(235,225,245,.16),rgba(235,225,245,0) 70%),
             radial-gradient(36% 28% at 60% 80%,rgba(255,235,225,.14),rgba(255,235,225,0) 70%),
             radial-gradient(30% 26% at 88% 66%,rgba(230,220,250,.12),rgba(230,220,250,0) 70%)}}
#fog2{{bottom:-240px;opacity:.4}}
.ember{{position:absolute;top:0;z-index:7;border-radius:50%;background:#ffd98a;
  box-shadow:0 0 6px 2px rgba(255,170,70,.9),0 0 18px 6px rgba(255,120,30,.45)}}
#leak{{z-index:8;mix-blend-mode:screen;opacity:0;
  background:radial-gradient(55% 40% at 30% 35%,rgba(255,190,120,.85),rgba(255,120,60,0) 70%),
             radial-gradient(45% 35% at 75% 70%,rgba(255,150,200,.55),rgba(255,120,160,0) 70%)}}
.gcap{{text-shadow:0 2px 26px rgba(40,18,10,.7),0 1px 4px rgba(0,0,0,.35)}}
.gcap .s{{font:500 60px Inter;letter-spacing:-1.2px;line-height:1.14;text-wrap:balance}}
.gcap .e{{font:italic 400 150px 'Instrument Serif';line-height:.95;color:{ACC};margin:2px 0 6px;white-space:nowrap}}
.spark{{text-shadow:0 0 18px rgba(250,230,122,.65)}}
'''

ROCK_CSS = f'''
.bword{{font-family:'DM Serif Display';text-shadow:0 0 40px rgba(110,150,255,.45),0 10px 40px rgba(0,0,20,.5)}}
#moonw{{position:absolute;left:600px;top:236px;width:440px;height:440px;z-index:2}}
#moon{{position:absolute;left:110px;top:60px;width:240px;height:240px;border-radius:50%;
  background:radial-gradient(circle at 42% 40%,#fbfcff 0%,#e3e9f7 45%,#c4cde3 70%,#aab4cf 100%);
  box-shadow:0 0 50px 14px rgba(200,215,255,.55),0 0 140px 50px rgba(120,150,255,.28)}}
.cloud{{position:absolute;width:460px;height:150px;border-radius:50%;
  background:radial-gradient(50% 50% at 50% 50%,rgba(40,48,80,.85),rgba(40,48,80,0) 75%)}}
#cl1{{left:-40px;top:190px}}
#cl2{{left:30px;top:20px;width:380px;height:120px;opacity:.75}}
#rtone{{z-index:7;background:linear-gradient(180deg,rgba(40,70,170,.24),rgba(100,50,170,.18));mix-blend-mode:soft-light}}
#rvig{{z-index:7;background:radial-gradient(110% 66% at 50% 42%,rgba(0,0,0,0) 48%,rgba(6,10,30,.55) 100%)}}
#rgrad{{z-index:7;background:linear-gradient(180deg,rgba(8,12,35,.38) 0%,rgba(8,12,35,0) 24%,rgba(8,12,35,0) 58%,rgba(6,8,25,.58) 100%)}}
.web{{position:absolute;z-index:8;overflow:visible}}
.web path{{fill:none;stroke:rgba(225,232,255,.62);stroke-width:1.6;stroke-linecap:round}}
#spw{{position:absolute;left:900px;top:222px;width:54px;z-index:8}}
#thread{{position:absolute;left:26px;top:0;width:1.6px;height:330px;background:rgba(225,232,255,.7);transform-origin:50% 0%}}
#spider{{position:absolute;left:0;top:0;filter:drop-shadow(0 0 6px rgba(190,210,255,.7))}}
.glit{{position:absolute;top:0;z-index:8;color:#EEF3FF;line-height:1;text-shadow:0 0 10px rgba(170,195,255,.9),0 0 22px rgba(110,140,255,.5)}}
#flash{{z-index:12;background:radial-gradient(120% 80% at 60% 20%,rgba(235,240,255,1),rgba(170,190,255,.85));mix-blend-mode:screen;opacity:0}}
.gcap{{text-shadow:0 2px 22px rgba(0,5,30,.85),0 1px 4px rgba(0,0,0,.4)}}
.gcap .s{{font:600 38px Montserrat;line-height:1.5;text-wrap:balance}}
.gcap .s .gw{{letter-spacing:.2em;margin:0 .06em;transform-origin:50% 50%}}
.gcap .e{{font:italic 400 140px 'DM Serif Display';line-height:1.12;color:{ACC};margin:0 0 4px;white-space:nowrap;
  text-shadow:0 0 34px rgba(110,150,255,.55),0 8px 30px rgba(0,5,30,.6)}}
.spark{{text-shadow:0 0 16px rgba(170,195,255,.9)}}
'''

SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')


def build():
    c_html, c_tw, spots = captions()
    b_html, b_tw, bw = behind_word()
    s_html, s_tw = sparkles(spots, bw)
    tweens = [f"gsap.set('.g',{{filter:'{GRADE}'}});"]
    if ROCK:
        m_html, m_tw = moon()
        w_html, w_tw = webs()
        sp_html, sp_tw = spider()
        g_html, g_tw = glitter()
        tweens += rock_transitions() + m_tw + w_tw + sp_tw + g_tw
        behind_layer = m_html
        looks = '<div id="rtone" class="fx"></div><div id="rvig" class="fx"></div><div id="rgrad" class="fx"></div>'
        front = g_html + w_html + sp_html
        after_caps = ['<div id="flash" class="fx"></div>']
        css = BASE_CSS + ROCK_CSS
    else:
        bat_html, bat_tw = bats()
        e_html, e_tw = embers()
        tweens += nox_transitions() + fog() + flicker() + bat_tw + e_tw
        behind_layer = bat_html
        looks = ('<div id="gwarm" class="fx"></div><div id="htone" class="fx"></div><div id="gvig" class="fx"></div>'
                 '<div id="ggrad" class="fx"></div><div id="flick" class="fx"></div>'
                 '<div id="fog1" class="fog"></div><div id="fog2" class="fog"></div>')
        front = e_html + ['<div id="leak" class="fx"></div>']
        after_caps = []
        css = BASE_CSS + NOX_CSS
    tweens += b_tw + c_tw + s_tw
    nl = '\n'
    return f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="assets/fonts/fonts.css" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
  <audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="2" data-volume="1"></audio>
{nl.join(audio(bw))}
  <div id="stage">
    <video id="bgv" class="full g" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="0"></video>
{nl.join(behind_layer)}
{nl.join(b_html)}
    <div id="cutwrap"><video id="cut" class="full g" src="assets/subject.webm" muted playsinline data-start="0" data-media-start="0" data-duration="{SUBJ_END:.3f}" data-track-index="1"></video></div>
  </div>
  {looks}
{nl.join(front)}
{nl.join(c_html)}
{nl.join(s_html)}
{nl.join(after_caps)}
{SAFE_GUIDE if SAFE else ''}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{nl.join(tweens)}
tl.set({{}}, {{}}, {DUR:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''


with open(os.path.join(P, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(build())
json.dump({'last_word_end': LAST_WORD_END}, open(os.path.join(P, 'work', 'tail.json'), 'w'))
print(f'{slug} [{"rockettes" if ROCK else "nox47"}]: index.html {DUR:.2f}s, cutout to {SUBJ_END:.2f}s, {len(BLOCKS)} blocks, '
      f'cuts {[round(c, 2) for c in CUTS]}, head {HEAD}')
for bid, a, b, before, punch, after, behind in BLOCKS:
    print(f"  {bid} {a:5.2f}-{b:5.2f}  {' '.join(w['text'] for w in before)} [{' '.join(w['text'] for w in punch)}{' (behind)' if behind else ''}] {' '.join(w['text'] for w in after)}")
