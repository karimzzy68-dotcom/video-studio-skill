"""Cut the speaker out of the OPENING only (where the behind-head word, bats and moon sit), instead of the whole ad:
about 4s of frames instead of 16s on a CPU-only PC. Builds a mini project in <project>/work/hook/, runs the skill's
cutout.py + headpos.py there, and copies the result to <project>/assets/subject.webm and work/headpos.txt.
Usage: PY hook_cutout.py <slug>"""
import json, os, shutil, subprocess, sys

ROOT = r"D:\video eidting with claude\reel-edits"
SK = r"C:\Users\Lenovo\.claude\skills\video-edit"
PY = sys.executable
BEHIND_SEG = {'n1': 's0', 'n2': 's1', 'n4': 's1', 'r1': 's0', 'r3': 's0', 'r4': 's0'}

slug = sys.argv[1]
proj = os.path.join(ROOT, slug)
hook = os.path.join(proj, 'work', 'hook')
os.makedirs(os.path.join(hook, 'assets'), exist_ok=True)
segs = json.load(open(os.path.join(proj, 'segments.json'), encoding='utf-8'))
seg = next(s for s in segs if s['id'] == BEHIND_SEG[slug])
end_frame = max(seg['frame'] + seg['frames'] + 3, 108)           # through the hook line, at least 3.6s
end_frame = min(end_frame, sum(s['frames'] for s in segs))
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', os.path.join(proj, 'assets', 'aroll.mp4'),
                '-vf', f'trim=end_frame={end_frame},setpts=N/30/TB', '-an', '-r', '30', '-fps_mode', 'cfr',
                '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                os.path.join(hook, 'assets', 'aroll.mp4')], check=True)
json.dump([s for s in segs if s['frame'] < end_frame - 10], open(os.path.join(hook, 'segments.json'), 'w', encoding='utf-8'), indent=1)
r = subprocess.run([PY, os.path.join(SK, 'scripts', 'cutout.py'), hook])
if r.returncode:
    sys.exit('cutout failed')
shutil.copy(os.path.join(hook, 'assets', 'subject.webm'), os.path.join(proj, 'assets', 'subject.webm'))
hp = subprocess.run([PY, os.path.join(SK, 'scripts', 'headpos.py'), hook], capture_output=True, text=True, encoding='utf-8')
open(os.path.join(proj, 'work', 'headpos.txt'), 'w', encoding='utf-8').write(hp.stdout)
print(slug, f'hook cutout {end_frame} frames ({end_frame / 30:.2f}s)')
print(hp.stdout)
