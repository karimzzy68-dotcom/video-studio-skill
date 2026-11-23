---
name: video-studio
description: "Master video-making skill: edits reels/ads from raw clips, builds motion graphics and films in code, clones animations or whole video edits, and does the sound. Use for ANY video task: 'edit these clips', 'make an ad / reel / explainer / film', 'copy this animation / motion graphic / hero' (-> reanimate), 'copy this video's clips and edit style' (-> rea-video), 'make a film in a named style' (-> lemo-opuscar), captions, cutouts, kinetic text, color grade, music, sound design, audio checks (-> earshot), Remotion, HyperFrames, FFmpeg, Playwright, three.js, GSAP, Lottie, Whisper, rembg. Start here; it routes to the right tool and sub-skill."
---

# video-studio

One entry point for everything video. Read this file, pick the route, then open only the reference you need.

## 1. Route the request (do this first)

| The user wants... | Route | Read |
|---|---|---|
| **Copy an animation / motion graphic / UI motion / hero / loader / hover / scroll effect** (from a URL, gif, mp4, Lottie, screen recording) | **reanimate** | `references/route-reanimate.md`, `bundled/reanimate/SKILL.md` |
| **Copy a whole video**: its clips, cuts, pacing, captions, transitions, sound = "edit my footage like this video" | **rea-video** | `references/route-rea-video.md`, `bundled/rea-video/SKILL.md` |
| Raw talking-head clips -> finished 9:16 reel (cuts, punch-ins, captions, looks, cutout, inserts) | **video-edit** | `bundled/video-edit/SKILL.md` |
| A film / explainer / promo made entirely in code, in a named style (99 styles) | **lemo-opuscar** | `references/route-lemo.md`, `bundled/lemo-opuscar/SKILL.md` |
| Short AI ad: UGC or sitcom style, Higgsfield images + Kling clips | **ugc-video-factory** (global skill) | its SKILL.md |
| Any sound decision: pick SFX/music, check sync, loudness, "does this sound real" | **earshot** | `bundled/earshot/SKILL.md`, `references/audio.md` |
| Build a real soundtrack from licensed recordings | **real-sound** | `bundled/real-sound/SKILL.md` |
| Pick a render engine / library / "what can X do" | capabilities | `references/capabilities.md` |
| Windows problems, paths, crashes | gotchas | `references/windows-gotchas.md` |

Disambiguation rule (the user's own): **copying a motion = reanimate. Copying a whole edited video (clips + edit style) = rea-video.** If a request is both ("make mine move like that intro AND cut like that video"), run rea-video for the edit and reanimate for each motion graphic inside it.

If the route is unclear, ask one question; otherwise state the route in one line and go.

## 2. Universal workflow (every route)

1. **Brief**: goal, platform + aspect (9:16 / 16:9 / 1:1), length, source files, brand, voice/music. Infer; ask only what changes the work.
2. **Probe sources**: `ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,duration -of json <file>`. Note rotation and VFR phone footage (normalize to CFR before editing).
3. **Transcribe** speech with Whisper (word timestamps) when there is talking; this drives cuts and captions.
4. **Plan the edit** as data (EDL/JSON: segments, in/out, punch-ins, captions, inserts, sfx cues). Edit the data, not the render.
5. **Build** with the right engine (section 3).
6. **Check**: contact sheets of frames at every cut and every insert; `ffprobe` the output; **earshot** for audio (sync, loudness -14 LUFS, true peak <= -1 dBTP).
7. **Deliver** to `D:\video eidting with claude\output\` with a clear name. Keep intermediates in `work/`. Show the user a short phone-sized preview and take notes; each revision is a re-render of data, not a restart.

## 3. Engine picker (details in `references/capabilities.md`)

| Need | Use |
|---|---|
| Cut, concat, scale, crop, speed, audio, format, burn subs, any file conversion | **FFmpeg** |
| Kinetic text, UI inserts, overlays, designed looks, web-tech motion with a timeline | **HyperFrames** (HTML + GSAP -> mp4) |
| Programmatic/React videos, data-driven templates, many variants of one design | **Remotion** |
| Frame-exact generative / 3D / shader scenes, full control | **Page contract** (`window.render(t)`) via lemo-opuscar `core/render` (Playwright) |
| Subject cutout (behind-head text), background removal | **rembg / cutout.py** (CPU is slow: ~1.4 s/frame; cut out only the opening) |
| Word-level captions | **Whisper / faster-whisper** |
| Voiceover | Kokoro (offline), edge-tts (online), or user's recording |
| Stock/licensed sound | **real-sound** + **earshot** to choose |
| Measure motion in a reference | **reanimate** scripts (Bun + Playwright) |

## 4. This project's proven pipeline (Windows, CPU-only)

Reference scripts in `pipeline-examples/` (from the Halloween ads job):
`make_edl.py` silence-aware cuts that keep a breath · `hook_cutout.py` cutout of the opening only · `halloween_build.py` two designed looks → HyperFrames `index.html` · `make_overlay.py` RGBA particle overlay piped to ffmpeg · `mix_music.py` held tail + ducked music bed.

Lessons already paid for:
- Never hand-roll ffmpeg `drawtext` overlays and call it designed; the user called it cheap. Use HyperFrames/Remotion.
- Always show captions. Endings must finish the last word (hold the last frame ~1.1 s, fade out). First frame must be sharp.
- Set `HYPERFRAMES_BROWSER_PATH` to system Chrome on Windows (bundled headless shell crashes).
- Do not pipe a long Python step into `Select-Object -First` in PowerShell (kills it).
- Everything (outputs, caches, installs) goes on **D:**; C: paths are junctions.

## 5. How people customize this skill

This skill is meant to be edited. Put your changes in these places and nothing else breaks:

| Change | Edit |
|---|---|
| Your brand fonts, colors, handle, default look | `references/my-style.md` (create from `references/my-style.template.md`) |
| A new designed look | add a section to `bundled/video-edit/references/looks.md`, then a builder in `pipeline-examples/` |
| New route (another cloning or editing skill) | add a row to the table in section 1 and a `references/route-<name>.md` |
| Default output folder / render quality | section 2 step 7 and `references/capabilities.md` (FFmpeg + HyperFrames flags) |
| Add your own sound bank | `references/audio.md` |

Install for yourself: copy the `video-studio/` folder to `~/.claude/skills/video-studio/` (and `bundled/reanimate`, `bundled/lemo-opuscar`, `bundled/earshot`, `bundled/real-sound`, `bundled/video-edit` to `~/.claude/skills/<name>/` so each also works on its own). Share it by zipping the folder; remove `bundled/video-edit/config.json` first, it holds personal info.
