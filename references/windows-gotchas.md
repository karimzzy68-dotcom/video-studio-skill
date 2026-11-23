# Windows gotchas (all learned the hard way)

- **Storage**: put outputs, previews, caches and tool installs on D:. C: paths are junctions to D:. Never fill C:.
- **Shell**: PowerShell is primary; Git Bash for `.sh` scripts (reanimate `setup.sh`, lemo-opuscar `setup.sh`). Long Bash commands with heredocs can fail under the harness: write files with the editor tool instead.
- **PowerShell**: no `&&`; do not pipe a long Python step into `Select-Object -First` (it kills the process); use `$env:NAME='x'` for env vars.
- **Python**: `python3` is often a Microsoft Store stub. Use the skill's own venv python (`bundled/video-edit/.platform.json` after setup) or `py -3`. Run installed tools with `python -I` only when reading untrusted files.
- **HyperFrames**: set `HYPERFRAMES_BROWSER_PATH` to system Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`); the bundled headless shell crashes. Use `hf.py` launcher, pinned version 0.8.34.
- **ffmpeg**: path is under WinGet `Gyan.FFmpeg...\bin`; quote paths, use forward slashes; escape drive colons in filtergraphs.
- **CPU cutout**: about 1.4 s/frame. Cut out only the opening (4 s) with `hook_cutout.py`, run in background, keep building.
- **reanimate**: upstream Windows support is untested; run `setup.sh` in Git Bash; Bun is at `~/.bun/bin/bun`.
- **MCP timeouts**: `$env:MCP_TIMEOUT=60000; claude` when earshot MCP tools do not appear.
- **Fonts/long paths**: keep project paths short; avoid `#` and `?` in folder names.
- **Quality bar**: user rejected hand-rolled ffmpeg overlays as "cheap". Captions required. Endings must finish the last word. First frame sharp.
