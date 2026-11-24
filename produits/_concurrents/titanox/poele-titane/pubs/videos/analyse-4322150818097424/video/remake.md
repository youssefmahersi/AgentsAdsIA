---
videomd: 1
part: remake
tokens: 1594
---

## Remake plan

### Step by step

This is a tabletop / unboxing / product. Do the steps in this order; the detail for each is in the matching subsection below.

1. **Write the content**: replace the original's 1 lines with your own (script table under “Sound”); pictures follow the shot list
2. **Shoot**: phone held vertical, mostly medium shot; light: soft frontal light (flat light) — a large source from the camera side, almost no shadow on the subject: facing a window, a ring light, or a big softbox behind the camera, one large soft light straight above the desk / behind the camera (or two, symmetrical at 45°); grade: natural (close to the original colours) (setups under “Shoot”)
3. **Generate**: 1 call (2 s), several shots each. Each shot gets one source frame for composition (subtitles erased, in `remake/refs/`), the swapped-in people, animals and products get reference images, and the prompt lists the shots in order
4. **Adapt the prompts to your model**: the prompts in this report are generic, and every model reads them differently (how shots are split, how references are addressed, how dialogue is written). Before generating, rewrite them following the official prompt guide of the model you actually use, or have the agent refine them with that model's prompting skill; notes for MiniMax H3 / H3 Max at the top of “AI generation”
5. **Voice**: the original is human recording; record it yourself or use TTS; 1 lines with their pace in the script table under “Sound”
6. **Edit**: follow the order and lengths in the shot list; the original has 6 shots at 1.9s each; 1 transitions under “Edit”
7. **Subtitles and styled text**: timing and style under “Packaging layer”
8. **Sound effects**: 1; place similar ones from a library at the times under “Sound”
9. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

**1 AI video shot → 1 generation unit, 1 MiniMax H3 / H3 Max call; live action 4 shots → 1 scene, 3 camera setups; code render / screen capture 1 shot → 1 code project**

### Generation units

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #2 | 3.1–5.6s | generate 4s, trim to 2.5s | reference images |

**Why it is split this way**

- Grouping: consecutive shots share a call where they fit, ≤15s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model takes no reference video: one source frame per shot (subtitles erased) fixes composition, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture; the voice was recorded by a person: record it separately and mix it in rather than having the video model speak, so copy and timing stay editable
- Packaging: the title on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

**G1 · shots #2 · 2.5s**

- reference images: source frames of shots #2 (subtitles erased)

Draft prompt (generic; rewrite it in MiniMax H3 / H3 Max's format into remake/prompts.json before generating):

```text
Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; high key (bright overall, almost no shadows), soft light (almost no lit / shadow edge), warm (about 3000–4000K), background clearly blurred (shallow depth of field / portrait mode). No subtitles, captions or watermarks in the picture.
Gros plan : une dizaine d'œufs au plat, une spatule glisse dessous (composition: @图片1)
```

### Shooting scenes

Shoot every shot of one scene before moving to the next; within a scene, shoot the wider sizes first and the close-ups last so the lighting is set only once. Leave about 1s of handle at both ends of every take.

**S1**: shots #1, #3–#5 (7.77s on screen); Œufs versés depuis un verre doseur dans la poêle vide, titre incrusté
- Lighting: soft frontal light (flat light), key light frontal, cool (daylight / cool-white LED)
- Setup medium shot · moving camera (gimbal / handheld pan) · pull-out/push-in: shots #1, #4, 5.57s on screen, shoot about 9.6s
- Setup medium close-up · fixed camera (tripod / mount / on the desk) · static: shots #3, 1.6s on screen, shoot about 3.6s
- Setup medium close-up · moving camera (gimbal / handheld pan) · pull-out: shots #5, 0.6s on screen, shoot about 2.6s

### Code composition

Rebuild it as one project in an HTML video framework (such as HyperFrames or Remotion): cuts, transitions and each shot's key frames from "Rhythm and key frames", layout, colours and elements from the scenes below. Text and UI are 100% controllable, changing copy is a data change, and an AI coding assistant can write the project.

`rea-video code-remake <breakdown folder>` only makes a quick draft: it renders `code/remake.mp4` from each scene's sampled points / cut-out, motion and background glow and scores it. Particles, point clouds and data visualisations on a dark ground come close; an illustrated character's acting and morph transitions do not.

- Part 1: shots #6 (10.2–11.4s)

How to build the pictures (by the measured picture type):
- vector shapes: SVG shapes + interpolate() / spring() keyframes, positions and timing measured from the frame

| Shot | Time | Build | Picture | Camera | Colours | On-screen text |
|---|---|---|---|---|---|---|
| #6 | 10.2–11.4s | vector shapes | Carte de fin : logo, bouton « Commandez maintenant », adresse du site sur fond dégradé rose | static | white, orange | titanoxfrance.com |

Per-shot motion timeline (measured: positions in % of frame width / height, colours sampled once the element settles; read together with the key-frame strip)

**Motion #6 10.2–11.4s (fade in) · 0 events**

- No element motion measured (still picture or only slight changes)

### Real material in the picture (the original files are needed)

4 shots, 7.77s (68%) contain real material (screen recordings, screenshots, photos, embedded video); a model cannot stand in for them:

- **live footage** (whole frame): shots #1, #3–#5, 7.8s in all
