# Route: reanimate (copy an animation / motion graphic)

Use when the user says copy / clone / recreate / "make it move like this" / "same hero as" / "match this exactly", and the thing is a **motion**: a website section, widget, loader, marquee, hover, scroll effect, page transition, canvas / WebGL / three.js scene, or a gif / mp4 / Lottie of one.

Not for: copying a whole edited video. That is `route-rea-video.md`.

## Installed at
- Skill: `C:\Users\Lenovo\.claude\skills\reanimate` (also in `bundled/reanimate`)
- Source clone: `D:\video eidting with claude\reanimate` (github.com/NiazMorshed2007/reanimate)
- Full instructions: `bundled/reanimate/SKILL.md` and `references/{capture,analysis,implementation,verify,webgl}.md`

## Flow (summary; the skill has the detail)
1. **Scope**: target, destination (code location + stack), fidelity: motion-faithful (default), pixel-faithful, mixed.
2. **Setup once**: `bash <skill>/scripts/setup.sh` (Bun 1.1+, Playwright Chromium, static ffmpeg, about 250 MB). Windows is untested upstream: run it from Git Bash; if Chromium fails, point Playwright at system Chrome.
3. **Capture the reference**: `bun scripts/capture.ts --url ... --selector ... --trigger load|scroll|hover|click --duration ... --track "<els>"` gives video, frames, `inspect.json` (declared CSS/WAAPI animations, keyframes, easings) and `track.json`.
4. **Spec table**: one row per element per property (start, duration, from -> to, easing, stagger).
5. **Build** in the user's stack (CSS, Framer Motion, GSAP, three.js). If the deliverable is a video, build it as a HyperFrames or Remotion composition instead.
6. **Verify**: capture the clone identically, `compare.ts`, side-by-side `sheet.ts`; fix the largest difference; repeat 2-5 rounds. Report what still differs and why.

## Inside a video
To put the copied motion in a video: build it as an HTML/GSAP scene (HyperFrames) or React (Remotion) using the spec's timings and easings, render, then verify against the reference frames the same way.
