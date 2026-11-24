---
videomd: 1
part: timeline
shots: 6
tokens: 564
---

# Timeline

One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
`story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).

```videomd-timeline
#01 0.0-3.1 | seen Œufs versés depuis un verre doseur dans la poêle vide, titre… | camera smooth move | overlay subtitle | made~ live action 49% · runner-up AI-generated video 40% | material~ the user's real material: live footage | remake reshoot · S1 | flag low confidence
#02 3.1-5.6 | seen Gros plan : une dizaine d'œufs au plat, une spatule glisse d… | camera smooth move | overlay subtitle | made~ AI-generated video 65% · runner-up 3D render 18% | material~ AI-generated | remake AI generation · G1 | flag to confirm,disputed
#03 5.6-7.2 | seen Les œufs glissent dans la poêle inclinée | camera static (subject moves) | overlay subtitle | made~ live action 54% · runner-up AI-generated video 34% | material~ the user's real material: live footage | remake reshoot · S1 | flag low confidence
#04 7.2-9.6 | seen La poêle est retournée : la galette d'œufs saute et retombe … | camera smooth move | overlay subtitle | made~ live action 50% · runner-up AI-generated video 38% | material~ the user's real material: live footage | remake reshoot · S1 | flag low confidence
#05 9.6-10.2 | seen Plan final sur la galette dorée dans la poêle | camera smooth move | overlay text, subtitle | made~ live action 56% · runner-up AI-generated video 35% | material~ the user's real material: live footage | remake reshoot · S1 | flag low confidence
#06 10.2-11.4 | seen Carte de fin : logo, bouton « Commandez maintenant », adress… | camera static | transition fade through 0.3s | made~ code / template render 82% · runner-up AI-generated video 5% | material~ rendered by the creator | remake code render · Part 1
```
