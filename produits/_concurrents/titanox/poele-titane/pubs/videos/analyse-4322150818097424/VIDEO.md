---
videomd: 1
name: titanox-4322150818097424
description: 'Œufs versés depuis un verre doseur dans la poêle vide, titre incrusté; Gros plan : une dizaine d''œufs au plat, une spatule glisse dessous Made with (inferred): live action 68%, AI-generated video 22%, code / template render 10%'
source:
  file: titanox-4322150818097424.mp4
  sha256: 6ee074eec721b235e820b243c3a83af7d151ab91a4dd3bce725facc9cc7d5ef4
  duration: 11.367
  size: 720x1280
  fps: 30.0
  aspect: '9:16'
shots: 6
tracks:
  transcript: video/transcript.vtt
lang: en
made_mix:
  live_action: 0.6833
  ai_video: 0.2171
  code_render: 0.0997
confidence: 0.572
readers:
- tools
- agent
open_questions: 6
generator:
  name: rea-video
  version: 0.1.0
---

# titanox-4322150818097424.mp4

**Verdict** (inferred): Mixed production: live action 68% + AI-generated video 22% + code / template render 10%; overlays: text labels, subtitles (composited in code / an editor); real material used: live footage (7.8s); audio: voice + 1 sound effects; packaging: title ×2, 1 sound effects land on text / sticker pops
**Made with** (inferred, by duration): live action 68%, AI-generated video 22%, code / template render 10%
**Remake**: 1 AI video shot → 1 generation unit, 1 MiniMax H3 / H3 Max call; live action 4 shots → 1 scene, 3 camera setups; code render / screen capture 1 shot → 1 code project
**Real material to collect**: 4 shots (68% of the duration), list in `video/remake.md`

## Next steps

- Remake: Capsule Cinema does the generation, assembly and checks. `rea-video remake <this dir>` hands over to it, does what can be done automatically and keeps the original elsewhere; `remake/status.md` says per shot what is left. Add incoming clips to `remake/mine.json` and run it again
- Code-rendered shots are best rebuilt in an HTML video framework (such as HyperFrames) from the rhythm and key frames in `video/rhythm.md`; `rea-video code-remake <this dir>` only makes a quick draft for particles / data-visualisation pictures
- AI shots: prompts are in the generation units of `video/remake.md`; for automatic generation use Capsule Cinema: `scripts/remake_reference.py prepare <this dir>`, then `run <jobs.json> --dry-run` (paid: ask the user first)

## Open questions

- Shot #1 (0.0–3.1s): live action at only 49% confidence, runner-up AI-generated video
- Shot #2 (3.1–5.6s): Tools say AI-generated video, the image review says live action; on the AI / live-action axis the fusion follows the tools (eval-calibrated)…
- Shot #3 (5.6–7.2s): live action at only 54% confidence, runner-up AI-generated video
- Shot #4 (7.2–9.6s): live action at only 50% confidence, runner-up AI-generated video
- Shot #5 (9.6–10.2s): live action at only 56% confidence, runner-up AI-generated video
- No AI listened to the soundtrack (the review covered the picture only): real voice versus TTS is inferred from the waveform; the effects were found on the separ…

## Map

Read this page first; for detail, open only the file you need. Each line is `path | ~tokens | what is in it · when to read it`; paths are relative to this directory.

```videomd-map
video/timeline.md | 578 | Timeline: one line per shot · what a stretch says, which shots need review, how a shot was made
video/moments.md | 72 | Special moments · reveals, twists, climaxes, goofs: times, key frames, clips
video/content.md | 111 | Content and structure · what it says, the narrative line, structure, the script
video/cast.md | 49 | Cast, scenes and props · reference images for characters, first-frame prompts
video/sound.md | 264 | Sound · voice, music, sound effects, beats and sources
video/rhythm.md | 248 | Rhythm and key frames · when cuts and transitions happen, shot lengths, the change curve, key frames of each shot
video/look.md | 800 | Camera, lighting and editing · for filmed shots: framing, camera, lighting, kit
video/packaging.md | 167 | Packaging · subtitles, styled text, stickers, picture-in-picture: timing and style
video/remake.md | 1606 | Remake plan · generation units, shoots, code builds, real material to collect, acting and emotion
video/transcript.vtt | 11 | Transcript: who says what, when · quoting speech, subtitles and voice-over
video/shots/*.md | 645 | Per-shot detail, tokens per file on average · checking one shot: what is seen, the inference and its basis, prompts, frames
breakdown.json | 26573 | Full raw data · for programs; a model rarely needs it
shots/ | - | contact sheet, first and last frame of each shot · checking by eye
storyboard.jpg | - | storyboard of the whole video · the whole video at a glance
stems/ | - | voice, music and effects stems · listening, remaking the sound
sfx/ | - | a clip of each sound effect · finding matching effects
packaging/ | - | subtitle files, packaging timeline, sticker frames · remaking subtitles and packaging
frames/ | - | picture scenes: full-size frames, the drawn layer cut out and sampled, measurements · remaking rendered pictures
audio.png | - | waveform and beat chart · seeing the rhythm
```

## How to read

- One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
- `story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
- Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).
- What is “seen” can be checked against the frames; what is “inferred” is the tools' and image readers' judgement, with the basis in each shot file. When they disagree, trust the frames.
