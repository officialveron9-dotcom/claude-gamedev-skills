# Existing furniture add-ons, generators and agent skills (checked 2026-10-10)

Read when the user asks for an add-on or another skill, or before reusing outside code. Method: GitHub code and repo
search (`SKILL.md` + furniture/archviz, "blender furniture generator", archipack), `git clone --depth 1` and the
LICENSE file read where possible [D]; otherwise search snippets [S]. Vendor only MIT, Apache-2.0 or CC0; repos
without a LICENSE are read-only. blender.org and extensions.blender.org were unreachable.

## Add-ons and generators

| Project | Licence | Last activity | What it does | Verdict |
|---|---|---|---|---|
| Archimesh (extensions.blender.org) | GPL-2.0-or-later (per a third-party mirror) [S] | bundled until Blender 4.1, extension v1.2.5 for 4.2+ [S] | rooms, doors, windows, kitchen cabinets, shelves, books, lamps, columns, stairs | Optional for quick archviz blocking. Check its output against [dimensions.md](dimensions.md), then run `finalize()` (bevel, origin, normals). Not tested here |
| Archipack, https://github.com/s-leger/archipack | GPL-3.0 [D] | repo last commit 2019-02-18 (Blender 2.79) [D]; 2.x sold on Gumroad (€49, Blender 3.x–5.x per listing); free community 1.2.85 is Blender 3.0 only [S] | walls, doors, windows, stairs, roofs; kitchen generator in the paid version [S] | Skip for this pipeline (free version does not run on 4.x/5.x; paid version untested) |
| LayoutLab, https://github.com/Furche/LayoutLab | none ("Not yet specified") [D] | 2026-07-27 [D] | v0.9 semantic room planning, parametric `bed_basic`, `wardrobe_basic`, `desk_basic` generators, JSON regenerate, clearance analysis, Blender 4.0+ | Good idea (objects that know their parts and clearances); read only, do not copy |
| cupboard-generator, https://github.com/karelvrabeckv/cupboard-generator | none [D] | archived, 2020-08-08 [D] | single cupboard add-on | Skip (old, no licence) |
| mesh-stuff, https://github.com/pyrokitty64/mesh-stuff | "CC0" in the repo description only [S] | 2026-10-07 [S] | "procedural game-ready house and furniture assets built with Blender Python scripts" | Not inspected (repo too large to clone here); check licence file and code before use |

## Agent skills

| Skill (repo) | Licence | Last commit | Content | Verdict |
|---|---|---|---|---|
| `blender-furniture`, https://github.com/luneszleg/Blender-MCP-Modelling-Skills | none [D] | 2026-08-06 [D] | 879 lines on modifiers over the BlenderMCP socket (Shrinkwrap screens, Displace crumpled paper, plush, booleans); no dimension tables, stylised sizes | Skip (no licence, not dimension-driven) |
| `furniture-design`, https://github.com/adauzat90/Woodworking_AI | none [D] | 2026-07-03 [D] | 137 lines of cabinetmaker rules: heights, depths, clearances, reveals, joinery, wood movement, sag | Useful cross-check; its numbers agree with this skill (900 mm counters, 740 mm tables, 3 mm reveals, legs ~1/12 height). Read only |
| `archviz`, https://github.com/arjun988/blender-skills | MIT [D] | 2026-07-10 [D] | 71-line generic archviz checklist (scale, camera, PBR) | Nothing beyond this skill |
| `blender-roomkit`, https://github.com/KevinXu02/aha-3d | Apache-2.0 [D] | 2026-09-29 [D] | reconstructs rooms from images/video with an asset index, placement checks, cabinet animation | Different job (photo → room); not for game props |
| `blender-room-generation`, https://github.com/hugozap/cozy-room-3d | MIT [D] | 2026-05-22 [D] | low-poly rooms for three.js via MCP, glTF export | Stylised low-poly; skip |
| `furniture-design-sketchup`, https://github.com/dasfink/sketchup-mcp | MIT (README) [D] | 2026-04-07 [D] | SketchUp MCP woodworking: cut lists, dados, shop drawings | SketchUp, not Blender |
| `blender-procedural`, https://github.com/muhammadusamahoyrr/fyp | MIT [D] | 2026-10-10 [D] | courtroom assets for a react-three-fiber app | Project-specific |
| `ak-furniture`, https://github.com/FIRaci/A-ch-n | none [D] | 2026-08-17 [D] | Arknights dormitory furniture data | Unrelated |
| `blender-image-to-3d`, majidmanzarpour/blender-game-skills (see the plugin's EXTERNAL.md) | MIT | 2026-09-23 | game asset from reference photos with silhouette checks | Complementary when the user has photos of a specific piece |

Result: 14 items found, none covers real-world furniture dimensions + game-ready cleanup + tested generators for GTA
and UE; nothing was vendored. This skill's generators are original code.
