# Capabilities: what each tool can do

Pick by need, not habit. All run on Windows; render outputs go to D:.

## FFmpeg / ffprobe (the base layer)
Installed via winget (Gyan full build, 9.x: libx264/x265, libass, libvmaf, scene filters).
- **Inspect**: `ffprobe -v error -show_entries stream=... -of json f.mp4`; `-show_frames -select_streams v -show_entries frame=pts_time,pict_type` for keyframes.
- **Cut**: fast `-ss A -to B -c copy` (keyframe-snapped); exact: re-encode `-ss A -i f -t D -c:v libx264 -crf 16 -c:a aac`. Put `-ss` before `-i` for speed.
- **Join**: concat demuxer (`-f concat -safe 0 -i list.txt -c copy`) for same-codec; `concat` filter or `xfade`/`acrossfade` for transitions (`fade, wipeleft, slideleft, circleopen, dissolve, pixelize, radial` ...).
- **Reframe**: `scale`, `crop`, `pad`, `zoompan`, `crop=w:h:x:y` with expressions for punch-ins; 16:9 -> 9:16 with blurred background (`split, boxblur, overlay`); `rotate`, `transpose`, `hflip`.
- **Speed**: `setpts=PTS/2` + `atempo=2` (atempo 0.5..2 per stage, chain for more); `minterpolate` for slow-mo; `fps=30`.
- **Silence / dead air**: `silencedetect=n=-30dB:d=0.1` -> cut list (see `pipeline-examples/make_edl.py`); `silenceremove`.
- **Scene / shot detection** (rea-video): `select='gt(scene,0.3)',showinfo`; or PySceneDetect.
- **Color**: `eq`, `colorbalance`, `curves`, `lut3d` (.cube), `hue`, `colorchannelmixer`, `vignette`, `noise` (grain), `unsharp`, `gblur`, `tonemap` (HDR->SDR).
- **Overlay / compose**: `overlay` (alpha webm/png sequence, `enable='between(t,a,b)'`), `blend`, `chromakey/colorkey/despill`, `alphamerge`, `drawbox`, `drawtext` (fine for debug/timecode, not for designed type), `subtitles=` (libass .ass/.srt burned captions), `fade`, `tblend`, `rgbashift` (glitch).
- **Stabilize**: `vidstabdetect` + `vidstabtransform`; `deshake`.
- **Audio**: `volume`, `loudnorm` (two-pass to -14 LUFS), `alimiter`, `acompressor`, `sidechaincompress` (duck music under voice), `afade`, `amix`, `adelay`, `apad`, `highpass/lowpass`, `equalizer`, `afftdn` (denoise), `arnndn`, `atrim`, `pan`.
- **Analyze**: `ebur128` (LUFS), `volumedetect`, `astats`, `signalstats`, `psnr/ssim/libvmaf` (compare two videos), `blackdetect`, `freezedetect`, `cropdetect`.
- **Frames / thumbs**: `-vf fps=2,scale=320:-1 f_%04d.jpg`, `tile=6x4` contact sheets, `-frames:v 1` stills, gif via `palettegen/paletteuse`.
- **Export**: `-c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart`; HEVC `libx265`; ProRes `prores_ks`; VP9 alpha `libvpx-vp9 -pix_fmt yuva420p`; hardware `h264_nvenc/qsv/amf` if the GPU has it. Instagram: 1080x1920, 30 fps, <= 90 s, AAC 48 kHz, -14 LUFS.
- **Windows**: use forward slashes; in filtergraphs escape the drive colon (`C\\:/...`) or run from the file's folder.

## HyperFrames (HTML + GSAP -> video)
Compositions are plain HTML. Clips are placed with data attributes (`data-start`, `data-duration`, `data-media-start`, `data-track-index`) on `<video>`, `<audio>`, `<img>` and divs; animation is a GSAP timeline that can be seeked deterministically. Anything the web can draw works: CSS, SVG, canvas, web fonts, backdrop-filter, mix-blend-mode, clip-path, masks.
- Commands (pinned 0.8.34): `hf lint` (must be 0 errors), `hf snapshot --at t1,t2,... --no-end --describe false` (frames to look at), `hf render -o renders/name.mp4 --quality high`. `hf --help` for the rest.
- Strengths: kinetic typography, caption styles, lower thirds, UI mockup inserts, glow / fog / ember overlays, behind-the-subject text (text layer between background plate and cutout subject video), blur-dissolve transitions, light leaks.
- Launcher: `bundled/video-edit/scripts/hf.py` (same on every OS). Windows: set `HYPERFRAMES_BROWSER_PATH` to system Chrome.
- Template and three proven looks: `bundled/video-edit/assets/template/build.py`, `bundled/video-edit/references/looks.md`, `overlays.md`.

## Remotion (React -> video)
Use for React components, typed props, data-driven batches, a scrubbable Studio.
- Start: `npx create-video@latest`; preview `npx remotion studio`; render `npx remotion render <CompId> out/name.mp4` (`--props='{"title":"..."}'`, `--codec h264|h265|vp8|vp9|prores|gif`, `--scale`, `--concurrency`, `--crf`); stills `npx remotion still`.
- Core API: `useCurrentFrame`, `useVideoConfig`, `interpolate`, `spring`, `Easing`, `<Sequence>`, `<Series>`, `<AbsoluteFill>`, `<Freeze>`, `<Loop>`, `<OffthreadVideo>` (frame-accurate video), `<Audio>`, `<Img>`, `staticFile`, `delayRender`, `calculateMetadata` (dynamic duration), `<Composition>` / `<Folder>`.
- Packages: `@remotion/transitions` (slide, fade, wipe, flip), `@remotion/captions` + `@remotion/install-whisper-cpp` (word captions), `@remotion/media-utils` (audio visualization, durations), `@remotion/media-parser`, `@remotion/three`, `@remotion/lottie`, `@remotion/gif`, `@remotion/shapes`, `@remotion/paths` (SVG draw-on), `@remotion/noise`, `@remotion/motion-blur`, `@remotion/layout-utils` (fit text), `@remotion/google-fonts`, `@remotion/rive`, `@remotion/skia`, `@remotion/player` (embed in a web app), `@remotion/renderer` + `@remotion/bundler` (render from Node), `@remotion/lambda` / `cloudrun` (cloud render).
- Rules: every frame is a pure function of the frame number (no CSS transitions, no `setTimeout`, no `Math.random` without `random(seed)`); use `<OffthreadVideo>`, not `<video>`.
- Licence: free for individuals and small teams; larger companies need a Remotion company licence. Check before client delivery.

## Page-contract renderer (lemo-opuscar `core/render`)
Any page that sets `window.READY=true` and implements `window.render(t)` renders deterministically: `node core/render/video.mjs <dir> --fps 24 --workers 3`; `still.mjs` review frames; `events.mjs` sound cues; `readcheck.mjs` reading-time check; `mux.sh` loudnorm -14 LUFS + limiter + grain. Best for three.js, shaders, canvas, p5, d3, generative scenes. See `route-lemo.md`.

## Playwright (+ Chrome)
Record or screenshot a live site at fixed viewport and fps, drive hover/scroll/click, read computed styles and Web Animations. Used by reanimate (`capture.ts`) and by the HTML renderers.

## Animation libraries inside HTML / React scenes
GSAP (timelines, staggers, easing `expo.out`, `back.out`, `elastic`), anime.js, Framer Motion / Motion (springs), Lottie (`lottie-web`, `@remotion/lottie`), three.js / react-three-fiber (3D, glTF, HDRI, bloom, DOF), GLSL shaders, Rive, D3 (data viz), p5.js, Matter.js (physics), canvas-confetti, tsParticles, MapLibre (maps), Lucide / Tabler icons, Google Fonts / Fontsource.

## AI / ML helpers
- **Whisper / faster-whisper**: word timestamps for captions and cut points (`base.en` fast, `small` multilingual).
- **rembg / U2Net / SAM**: subject cutout and mattes (CPU is slow, about 1.4 s/frame: run in background, opening only).
- **Real-ESRGAN**: upscaling. **RIFE / `minterpolate`**: frame interpolation. **Demucs**: stem separation. **PySceneDetect**: shot boundaries. **OpenCV / MediaPipe**: face and pose tracking, head position (`headpos.py`). **CLIP / CLAP (earshot)**: semantic search of frames and sounds.
- **Generation (connected MCPs)**: Higgsfield (images, Kling clips, audio, upscaling, motion control), see the `ugc-video-factory` skill.
- **TTS**: Kokoro (offline), edge-tts (online, many voices), ElevenLabs if the user has a key.

## Python media stack
Pillow (RGBA overlays, contact sheets), numpy, OpenCV, PyAV, librosa (beats and tempo for cut-to-music), pydub, scenedetect, pysubs2/srt (caption files), yt-dlp (only for footage the user owns or may use).

## Output targets
Reels / TikTok / Shorts 1080x1920 · YouTube 1920x1080 or 3840x2160 · Square 1080x1080 · Ads: render 16:9, 1:1, 9:16 variants from one data file · GIF / WebP previews · ProRes or alpha WebM for overlays · SRT / VTT sidecars.
