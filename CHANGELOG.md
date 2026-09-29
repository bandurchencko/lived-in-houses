# Changelog

## 0.3.4 — 29 September 2026

- **Doors are no longer blocked by the sill beam** — the dark timber beam laid over the stone plinth (and the plinth beam
  of the red-stone look) ran across the entrance at knee height, so a character walking in through a door without a
  porch was stopped (found while walking a generated street in the browser). The beam now stops at the door posts; a
  test keeps every sill beam out of door openings. Example houses rebuilt.
- **Shadows in the browser viewer** — the exported meshes carry no normals (glTF clients compute flat ones), and without
  them three.js drew no shadows at all: a house cast none on its ground plate and its gallery none on its walls. The
  viewer now computes normals at load; houses cast and receive shadows.

## 0.3.3 — 28 September 2026 (night)

- **Stairs no longer flicker** — every step was a box from its own nosing to the end of the flight, so the side faces
  of all steps lay in one plane while the materials alternated (board / beam, paving / stone): the side of the stair
  shimmered when the camera moved. Each step is now a block under its own tread; the cheeks of the niche under the
  outer stair are 1 cm narrower than the flight; the chimney of houses with a yard starts inside the ceiling.
- **Coplanar-face check** — `proverki.sovpadayushchie_grani(D)` finds box faces in one plane (same axis, coordinate
  and normal, overlapping); a test keeps floors and stairs free of them and caps small hidden ones per house.

## 0.3.2 — 28 September 2026 (night)

- **Door jambs no longer flicker** — the jambs sat flush with the wall reveal, two faces in one plane, and flickered
  (z-fighting) when the camera walked through a door. They now stand 2 cm into the opening and stop 5 mm below its
  head, in every family; a test keeps jambs off the reveal plane. Example houses rebuilt.

## 0.3.1 — 28 September 2026 (night)

- **Windows console fix** — the command-line tools (`eksport_glb`, `obraz`, `python -m generator_domov`) no longer
  crash with `UnicodeEncodeError` on a default Windows console (cp1252) when printing the summary; output is UTF-8.
- README: an "In one minute" block — who it is for, the problem it solves, how to use it, what's next.

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
  palette. Two examples from the project's concept art.
- **Textured browser demo** — the glTF carries UVs laid along each face; the viewer dresses houses in CC0 Poly Haven
  textures by style, tinted to the house colours, lit by a CC0 sky with filmic tone mapping; drop your own `.glb`.
- README: why I built it, what I tried, when it helps, engines and formats, who does what from a picture to a house.

## 0.1 — 28 September 2026 (midday)

- The rule-based generator: passport → floor plan → engine-free details by group → gameplay checks; two families
  (tavern with forge in four compositions, house with a yard), two styles; export to glTF; a three.js viewer with group
  toggles and a cut-height slider; seven example houses; a 43-second trailer.
