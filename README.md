# video-studio

One Claude Code skill for all video work: edit raw clips into reels/ads, build motion graphics and films in code, copy an animation, copy a whole video's edit style, and handle the sound.

## 1. Requirements
- [Claude Code](https://claude.com/claude-code)
- ffmpeg + ffprobe, Node 20+, Python 3.10+ (Windows: `winget install Gyan.FFmpeg OpenJS.NodeJS Python.Python.3.12`)
- Bun 1.1+ (only for `reanimate`), Chrome (for HyperFrames/Playwright rendering)
- Windows or macOS or Linux. Written and tested on Windows 11 (CPU only).

## 2. Install the skills
Copy this repo's contents into your Claude skills folder:

```sh
git clone https://github.com/karimzzy68-dotcom/video-studio-skill
# main skill
cp -r video-studio-skill ~/.claude/skills/video-studio
# each sub-skill so it also works on its own
for n in reanimate rea-video lemo-opuscar earshot real-sound video-edit; do
  cp -r video-studio-skill/bundled/$n ~/.claude/skills/$n
done
```
(Windows PowerShell: use `Copy-Item -Recurse`; target `$HOME\.claude\skills\`.) Restart Claude Code.

## 3. Install the tools the sub-skills drive (one time each)
| Sub-skill | Install | Windows note |
|---|---|---|
| rea-video | `git clone https://github.com/JuneYaooo/rea-video` then `pip install -e rea-video` | run with `PYTHONUTF8=1` or the CLI crashes on its Chinese help text |
| reanimate | `git clone https://github.com/NiazMorshed2007/reanimate`, then run `bash skills/reanimate/scripts/setup.sh` (Bun, Playwright, ffmpeg, ~250 MB) | upstream untested on Windows; use Git Bash |
| lemo-opuscar | `git clone https://github.com/lemomo-ai/lemo-opuscar`, then `sh plugin/skills/lemo-opuscar/scripts/setup.sh deps` | use Git Bash |
| earshot | `pip install -e "<earshot repo>[mcp,llm]"`, `earshot doctor` | see `bundled/earshot/SKILL.md` |
| video-edit | first run does its own setup (asks name, handle, default look) | set `HYPERFRAMES_BROWSER_PATH` to system Chrome |

## 4. Use it
Just describe the job; the skill routes it. Examples:

```text
/video-studio edit these clips into a 25s reel, bold captions, music under the voice
/video-studio copy the hero entrance animation on https://example.com into components/Hero.tsx      -> reanimate
/video-studio copy this video's clips and edit style: ref.mp4, use my footage in ./clips             -> rea-video
/video-studio make a 45s film in the Neon Tubes style about my coffee farm                          -> lemo-opuscar
/video-studio check the audio of output/ad.mp4: loudness, sync, does it sound real                  -> earshot
```

| Request | Route |
|---|---|
| Copy an animation / motion graphic | `reanimate` |
| Copy a whole video (clips + edit style) | `rea-video` |
| Raw clips -> finished 9:16 reel | `video-edit` |
| Film in code, 99 named styles | `lemo-opuscar` |
| Judge/choose/verify sound | `earshot`, `real-sound` |

## 5. Make it yours
Copy `references/my-style.template.md` to `references/my-style.md` and fill in fonts, colors, caption rules, music folder and output folders. Add new looks to `bundled/video-edit/references/looks.md`. Add a new route by adding a row to the table in `SKILL.md` and a `references/route-<name>.md`.

## 6. What's inside
- `SKILL.md`: router + universal workflow + engine picker
- `references/capabilities.md`: what FFmpeg, HyperFrames, Remotion, Playwright, GSAP/three.js/Lottie, Whisper, rembg can do
- `references/route-*.md`, `audio.md`, `windows-gotchas.md`
- `pipeline-examples/`: real scripts (silence-aware cuts, opening-only cutout, designed looks, music mix)
- `bundled/`: third-party skills, each with its own licence:
  reanimate (NiazMorshed2007, MIT) · rea-video (JuneYaooo) · lemo-opuscar (lemomo-ai / LemoLab; library cloned separately) · earshot · real-sound · video-edit

## Troubleshooting
See `references/windows-gotchas.md`.
