# Changelog

## 0.3 — 28 September 2026 (evening)

- **Gable roof for the tavern** — a passport choice (`krysha='valma'` hip, default; `'dvuskat'` gable): ridge along the
  facade, roof past the gables, plaster gable ends with a dark king post and struts, verge boards, purlin ends. The AI
  eyes choose it from a picture. Existing seeds are unchanged (seed 13 is byte-identical).
- **Volumetric stone** — larger corner stones protruding 4–7 cm, an uneven top course, outer-stair parapets with cap
  stones and uneven tops, half-buried boulders at the foot of stairs and free corners; the same live stone on the plinth
  of houses with a yard.
- **Yard trades by place** — `osoboe`: a stable under the canopy (hay, trough, saddle, harness, hitching rail, a wide
  gateway), beehives deep in the garden, a poultry coop on legs with a ramp.
- **Red-stone look** — irregular rubble stone and dry dusty ground in the viewer.

## 0.2 — 28 September 2026 (afternoon)

- **A house from your picture** — `generator_domov/obraz.py`: an AI that sees images (any chat by hand, Claude Code, a
  local Ollama model or the Anthropic API) reads a picture into a passport; the generator builds the nearest house it
  knows, clamped to safe ranges, rolling numbers back to the seed until every check passes; picture colours go into the
  palette. Two examples from our concept art.
- **Textured browser demo** — the glTF carries UVs laid along each face; the viewer dresses houses in CC0 Poly Haven
  textures by style, tinted to the house colours, lit by a CC0 sky with filmic tone mapping; drop your own `.glb`.
- README: why we built it, what we tried, when it helps, engines and formats, who does what from a picture to a house.

## 0.1 — 28 September 2026 (midday)

- The rule-based generator: passport → floor plan → engine-free details by group → gameplay checks; two families
  (tavern with forge in four compositions, house with a yard), two styles; export to glTF; a three.js viewer with group
  toggles and a cut-height slider; seven example houses; a 43-second trailer.
