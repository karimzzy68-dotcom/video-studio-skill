# Route: lemo-opuscar (films in code, 99 styles)

Use when the user wants a film, explainer, promo, short or animation made entirely in code, in a named style (Impasto Oil Painting, Watercolor, Ukiyo-e, Neon Tubes, Satellite Briefing, Exploded Teardown, LiDAR Survey, Dark Keynote, Blueprint, Chalkboard ...), or wants help choosing a style.

## Installed at
- Library clone: `D:\video eidting with claude\lemo-opuscar` (github.com/lemomo-ai/lemo-opuscar; 99 styles, 15 categories). This clone is `LIB`.
- Skill: `bundled/lemo-opuscar/` (its setup.sh normally clones to `~/lemo-opuscar`; here use the clone above).
- Read first: `lemo-opuscar/AGENTS.md`, then `DIRECTOR.md` (story, sound, rhythm, delivery), `TECHNIQUE.md` (building), `core/README.md` (commands), `styles/README.md` (index), `MY-STYLES.md` (make your own style).

## Rules that matter
- `STYLE.md` is fixed: keep every invariant. Story, structure, shots and timings are yours, directed from the user's topic. Write `TREATMENT.md` with three structures before opening a style's demo.
- Never build inside `styles/`; build in `D:\video eidting with claude\films\<name>\`.
- Built for Claude Fable / Opus / Sonnet at high effort.
- Styles marked with a star need an image generator the user provides (Codex CLI or another).
- Setup: `sh plugin/skills/lemo-opuscar/scripts/setup.sh deps` (needs Node, ffmpeg, Python; voice and music tiers optional). On Windows run the `sh` scripts from Git Bash.

## Commands (from `$LIB`)
`node core/render/still.mjs <dir> 1.5 3` review stills · `video.mjs <dir> --fps 24 --workers 3` render · `events.mjs` sound cues · `readcheck.mjs` on-screen text reading time · `sh core/render/mux.sh video.mp4 mix.wav out.mp4` master to -14 LUFS · `core/tts/tts.py` Kokoro voice · `asr_check.py` verify narration · `core/audio/sfx.py | sampler.py | pluck.py` procedural and sampled sound.

## Combine
**earshot** to check the mix, **real-sound** for real recordings instead of procedural sound, **ffmpeg** for social cut-downs and variants.
