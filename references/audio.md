# Audio: earshot + real-sound + mixing

You cannot hear. Never say a sound "fits", is "clean" or "synchronized" without an earshot reading behind it. Quote numbers ("strong match z +3.9; p_real 0.96; -14.2 LUFS").

## earshot (bundled: `bundled/earshot/SKILL.md`, full command reference)
Local CPU audio understanding. Install once: `pip install -e "<earshot repo>[mcp,llm]"`, then `earshot doctor`. Existing install in this project: `D:\video eidting with claude\tools\earshot`.
Loops:
1. **Choose an asset**: `earshot rank "soft felt mallet hit" downloads/sfx/ --top 5`, then `earshot find file.ogg "single clean hit" --top 3` for the trim.
2. **Verify it is real**: `earshot realness file` (p_real); catches code-synthesized sound.
3. **Review a soundtrack or video**: `timeline`, `describe`, `measure`, `critique`, `sheet`; compare two mixes with `ab`; `compare` against a reference (rea-video).
4. **Make a sound in code and improve it**: `earshot forge`; the shipped sound bank: `sfx_list`, `sfx_render`, `kit_render` (code-made films).
MCP mode keeps models loaded: `claude mcp add earshot --scope user -- <venv>/python -m earshot mcp`; if tools do not appear start Claude with `MCP_TIMEOUT=60000`. Set `EARSHOT_THREADS=2-3` on a shared machine.

## real-sound (bundled: `bundled/real-sound/SKILL.md`)
Premium soundtracks from real licensed recordings: cue list from picture, sourcing (Freesound, Mixkit, composer libraries) with licence checks, music edit at bar lines, JSON sound design rendered by a deterministic mixer, measured QA (clicks, masking, harshness, sync, loudness), mastering, credits, mux. Use it whenever a video's sound is synthesized or "random".

## Mixing rules of thumb (measure with earshot/ffmpeg `ebur128`)
- Final: -14 LUFS integrated, true peak <= -1 dBTP; two-pass `loudnorm` then `alimiter`.
- Voice on top; music bed about -18 to -22 dB under voice, ducked with `sidechaincompress` (see `pipeline-examples/mix_music.py`: VOL 0.24, fade with picture, 1.1 s held tail).
- SFX at every text pop, cut and whoosh, subtle (-24 to -18 dB); riser into the hook payoff; hit on the CTA.
- Hold the last frame ~1.1 s after the final word so the ad never ends mid-sentence.
- Music licence: only use tracks the user may use; record credits.

## User's sound sources
Music: `D:\Capcut automation\assets\Resources\sound effects\` (e.g. Velvet Hour.mp3). SFX bank in `bundled/video-edit/assets/template/assets/sfx`. Add your own banks here and list them below.
