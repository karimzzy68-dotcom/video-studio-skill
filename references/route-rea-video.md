# Route: rea-video (copy a whole video: clips + edit style)

Use when the user wants to **completely copy a video**: same kind of clips in the same order, the same cuts, pacing, zooms, captions, transitions, effects and sound, rebuilt with *their* footage/content. Examples: "edit my clips like this reel", "make my ad cut like this one", "copy this video's style".

Not for: copying a single animation or motion graphic (use `route-reanimate.md`). If the reference contains motion graphics, copy the edit with rea-video and each graphic with reanimate.

## Installed
- Real tool: github.com/JuneYaooo/rea-video, cloned at `D:ideo eidting with claudeea-video`, CLI installed editable (`rea-video`), skill at `~/.claude/skills/rea-video` (also `bundled/rea-video`).
- **Windows: always run with `PYTHONUTF8=1`** (PowerShell: `$env:PYTHONUTF8=1`), or the CLI crashes printing its Chinese help text.
- Commands: `decompose`, `stems`, `probe`, `survey`, `moments`, `frames`, `tiles`, `review`, `compare`, `summary`, `remake-plan`, `remake-run`, `code-remake`, `assemble`, `videomd`. Needs ffmpeg + Python 3.10+; a VLM is optional (this agent can look at images itself).
- **Use it for Phase 1 below** (it labels each shot as live / AI / 3D / 2D / code-render / screen-recording, finds captions, stickers, SFX, BGM, lighting, grade, and writes `out/ref/VIDEO.md`). Read `bundled/rea-video/SKILL.md` and its `references/` (remake.md, hyperframes.md, remake-tools.md). Its remake step can write code shots as Remotion/HyperFrames projects.
- The phases below are the fallback / glue: use them to map the user's clips and build with video-studio's engines.

## Reference sources
A local mp4/mov, a downloaded reel the user owns or may use, or a screen recording. If the user gives only a link to a login-walled or DRM site, ask for the file. Never redistribute the reference's footage; copy the *edit style*, not the clips.

## Phase 1: Analyze the reference (output: `work/ref/analysis.json` + `analysis.md`)
1. **Probe**: size, fps, duration, audio layout (`ffprobe`).
2. **Shots**: scene detection (`ffmpeg select='gt(scene,0.3)',showinfo` or PySceneDetect); also detect hard cuts inside moving shots by lowering the threshold. Output a table: shot #, start, end, length.
3. **Frames**: grab the first, middle and last frame of every shot plus 2 fps contact sheets (`tile`). Look at them.
4. **Per shot, record**: shot type (talking head, b-roll, screen recording, product, text card, graphic), framing (wide/medium/close), camera move (static, push-in, handheld, whip), punch-in / zoom value, speed (slow-mo, speed ramp), color look.
5. **Transitions**: at each cut, classify: hard cut, jump cut, dissolve, whip/slide, flash/light leak, glitch, match cut, zoom-through, masked reveal. Measure its length in frames.
6. **Captions**: transcribe with Whisper (word timestamps). Record style: font category, case, size relative to frame, position (inside Reels safe zone?), highlight rule (which words get color/emphasis), animation (pop, slide, typewriter), words per caption.
7. **Pacing**: average shot length, shortest/longest, cut rhythm vs. speech (cut on breath? on beat?). If music: BPM and whether cuts land on beats (librosa).
8. **Audio**: voice vs. music levels (LUFS), music genre and where it enters/ducks, SFX at cuts/text (whoosh, hit, riser, click) with timestamps. Use **earshot** (`timeline`, `describe`, `measure`) instead of guessing.
9. **Overlays/graphics**: stickers, progress bars, lower thirds, UI mockups, grain, vignette, light leaks, logos; time in/out of each. For any non-trivial motion graphic, hand it to **reanimate** (video-file mode, time range).
10. **Structure**: label the beats (hook 0-3 s, setup, proof, payoff, CTA) with timestamps. The hook usually carries the style.

## Phase 2: Map the user's material onto the structure
1. Ingest the user's clips; transcribe; list usable takes per line (pick the cleanest take, see `bundled/video-edit/SKILL.md`).
2. For each reference shot, assign a user clip/segment that plays the same *role* (hook line, proof, b-roll, CTA). Where the user lacks a shot type, say so and propose: reuse with a punch-in, generate b-roll (Higgsfield), screen-record, or a designed text card.
3. Write the **EDL** (`edl.json`): per segment source, in, out, speed, scale/punch-in keyframes, transition-in (type + frames), caption words, sfx cues. Keep the reference's shot lengths scaled to the user's content, not stretched artificially.

## Phase 3: Build
- Cuts, punch-ins, speed, audio: FFmpeg or HyperFrames/Remotion timeline from the EDL.
- Captions in the same style as the reference (HyperFrames/Remotion, never plain `drawtext`).
- Transitions as measured in Phase 1 (xfade types, whip blur, flash frames, light-leak overlays, glitch via `rgbashift`).
- Overlays/graphics rebuilt via reanimate; color look matched with `eq`/`curves`/LUT.
- Music: same genre and energy (real-sound for licensed tracks); cut on beats if the reference does; duck under voice (`sidechaincompress`); SFX at the measured cue times.

## Phase 4: Verify against the reference
1. Side-by-side contact sheet: reference shot N vs. output shot N for every shot.
2. Numbers: shot count and average shot length within ~10%; each cut within +-3 frames of the mapped rhythm; caption positions/size match; loudness within 1 LU; ffprobe the output specs.
3. Earshot timeline of the output vs. the reference (cue placement, mix balance).
4. Report differences that are intentional (user's content) vs. gaps (missing shot types). Iterate once or twice; show a phone-size preview.

## Deliverables
`output/<name>.mp4`, `edl.json`, `analysis.md` (the reference's edit recipe, reusable as a template for the next video), and the build script. Save the recipe in `references/my-style.md` if the user wants this look as a default.
