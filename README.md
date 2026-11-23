# video-studio

One Claude Code skill for all video work: edit raw clips into reels/ads, build motion graphics and films in code, copy an animation, copy a whole video's edit style, and handle the sound.

## Install

Copy this folder to `~/.claude/skills/video-studio/`. For each bundled sub-skill to also work on its own, copy `bundled/<name>/` to `~/.claude/skills/<name>/`.

## Routing

| Request | Route |
|---|---|
| Copy an animation / motion graphic | `reanimate` |
| Copy a whole video (clips + edit style) | `rea-video` |
| Raw clips -> finished 9:16 reel | `video-edit` |
| Film in code, 99 named styles | `lemo-opuscar` |
| Judge/choose/verify sound | `earshot`, `real-sound` |

Start at `SKILL.md`. Details: `references/capabilities.md` (FFmpeg, HyperFrames, Remotion, Playwright, AI helpers), `references/windows-gotchas.md`, `references/my-style.template.md` (make it yours).

## Bundled third-party skills (see each folder for its licence)
- `bundled/reanimate`: NiazMorshed2007/reanimate (MIT)
- `bundled/rea-video`: JuneYaooo/rea-video
- `bundled/lemo-opuscar`: lemomo-ai/lemo-opuscar (the skill stub; the library is cloned separately)
- `bundled/earshot`, `bundled/real-sound`, `bundled/video-edit`: skills as installed locally

The upstream tools themselves (rea-video CLI, reanimate scripts' dependencies, lemo-opuscar library) are installed from their own repos; see `references/route-*.md`.
