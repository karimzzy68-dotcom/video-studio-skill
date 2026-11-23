"""Finish a rendered reel: hold the last frame after her final word so the ad never ends mid-sentence, fade the
picture out over that hold, and mix the music bed underneath (ducked under the voice, fading out with the picture).
Usage: python mix_music.py <slug>   (reads reel-edits/<slug>/renders/<slug>-v2.mp4, writes output/<Ad name>_Halloween.mp4)"""
import json, os, subprocess, sys

ROOT = r"D:\video eidting with claude"
MUSIC = r"D:\Capcut automation\assets\Resources\sound effects\Velvet Hour.mp3"
OFFSET = {'n1': 18, 'n2': 58, 'n4': 88, 'r1': 118, 'r3': 158, 'r4': 188}   # a different part of the song per ad
VOL = 0.24
HOLD = 1.1   # seconds held after the end of the source, picture fades to black across it

slug = sys.argv[1]
proj = os.path.join(ROOT, 'reel-edits', slug)
src = json.load(open(os.path.join(proj, 'sources.json'), encoding='utf-8'))['c1']
render = os.path.join(proj, 'renders', f'{slug}-v2.mp4')
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', render],
                           capture_output=True, text=True).stdout)
total = dur + HOLD
out = os.path.join(ROOT, 'output', os.path.splitext(os.path.basename(src))[0] + '_Halloween.mp4')
fc = (f"[0:v]tpad=stop_mode=clone:stop_duration={HOLD},fade=t=out:st={dur - 0.1:.3f}:d={HOLD + 0.1:.2f}[v];"
      f"[1:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,volume={VOL},afade=t=in:d=0.8,afade=t=out:st={dur - 0.3:.3f}:d={HOLD + 0.3:.2f}[m];"
      f"[0:a]apad=whole_dur={total:.3f},asplit=2[vo][sc];"
      "[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=25:release=450:makeup=1[duck];"
      "[vo][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.94[a]")
r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', render, '-ss', str(OFFSET[slug]), '-i', MUSIC,
                    '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-t', f'{total:.3f}',
                    '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out], capture_output=True, text=True)
print(slug, 'OK ->' if r.returncode == 0 else 'FAILED', out if r.returncode == 0 else r.stderr[-800:])
