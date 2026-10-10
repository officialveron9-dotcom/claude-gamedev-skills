# External skills, tools and assets (checked 2026-10-10)

## 1. Existing agent skills for soft furniture

How checked: 42 Blender/agent-skill repositories cloned (`git clone --depth 1`; the list in
`plugins/blender-modeling/EXTERNAL.md` plus a5c-ai/babysitter), every `SKILL.md` grepped for pillow, cushion,
blanket, duvet, sofa, couch, tufting, Chesterfield, upholstery, curtain, cloth, fabric; plus web searches on
skills.sh / openskillindex / GitHub. GitHub code search was not available from this session.

**Result: 0 skills dedicated to soft furniture. 11 distinct skills/scripts touch the topic; 0 are good enough to
vendor; 1 is worth installing optionally.**

| # | Skill / file | License | Last commit | Content | Verdict |
|---|---|---|---|---|---|
| 1 | arjun988/blender-skills `cloth-sim` — https://github.com/arjun988/blender-skills | MIT | 2026-07-10 | 85-line garment/flag cloth workflow, 4-row preset table (quality, bending, mass); no pressure, pillows or collision numbers | Not vendored: generic, no measured values |
| 2 | arjun988/blender-skills `prop-artist` | MIT | 2026-07-10 | Prop checklists, lists furniture as a category | Not soft goods |
| 3 | a5c-ai/babysitter `library/specializations/game-development/skills/cloth-simulation` — https://github.com/a5c-ai/babysitter | MIT | 2026-08-31 | 21-line stub (capability list only) | Reject |
| 4 | Gaius114/blender-claude-mcp `blender-arch` (also copied in MAX-786/claude-3d-harness `library/gaius`) — https://github.com/Gaius114/blender-claude-mcp | MIT | 2026-05-19 | 1 466-line archviz skill (Italian comments) with a `mat_fabric()` sheen helper | Not vendored; its comment "Sheen = 4.x name" is wrong (`Sheen Weight` since 4.0) |
| 5 | TMHSDigital/Blender-Developer-Tools `showcase/wingback-armchair` — https://github.com/TMHSDigital/Blender-Developer-Tools | **CC BY-NC-ND 4.0** | 2026-10-08 | Procedural deep-button tufted wingback (13 buttons on a diamond lattice, piped welts, nailheads) | Read-only reference; license forbids derivatives/commercial use |
| 6 | scenario-labs/skills `scenario-blender-geometry-nodes` — https://github.com/scenario-labs/skills | MIT | 2026-10-10 | Tested 5.2 GN physics: "Cloth Dynamics (Experimental)" XPBD asset + Collider + Custom Force (procedure H) | **Optional install** for GN cloth experiments: `npx skills add scenario-labs/skills --skill scenario-blender-geometry-nodes` |
| 7 | dcc-mcp/dcc-mcp-blender `blender-physics` scripts (`add_cloth_modifier.py`, `set_cloth_settings.py`) — https://github.com/dcc-mcp/dcc-mcp-blender | MIT | 2026-10-09 | Thin wrappers to add/set cloth over MCP | Not needed (plain bpy) |
| 8 | PoBruno/mcp-blender-agent `aaa-modeling` — https://github.com/PoBruno/mcp-blender-agent | MIT | 2026-07-20 | Spec-sheet workflow; parametric library = beach chair, bar stool, dining table | Hard furniture only |
| 9 | majidmanzarpour/blender-game-skills `blender-image-to-3d` | MIT | 2026-09-23 | Photo → game prop with silhouette checks | Useful for hard props from photos (already in EXTERNAL.md) |
| 10 | clawic/skills `interior-design` — https://github.com/clawic/skills | MIT | 2026-07-27 | Room planning advice (fit a sofa through a door) | No 3D content |
| 11 | LevyBytes/AI-SKILL-blender `material-nodes/references/clothsettings-bpy-struct.md` | **AGPL-3.0** | 2026-06-22 | ClothSettings API dump | Reject (license; bpy itself is the better reference) |

Hard furniture (frames, legs, dimensions): this repo's own `blender-furniture-modeling`.

## 2. Tools and add-ons

| Tool | License / price | What it does for soft goods | Verdict |
|---|---|---|---|
| Blender Cloth (built-in) | GPL | Pressure (2.82+), internal springs, shrink, pin groups, self-collision | Default; settings in this skill |
| Blender 5.2 GN "Cloth Dynamics (Experimental)" | GPL | XPBD cloth as node groups | Experimental; stay on the Cloth modifier for production |
| Marvelous Designer | subscription (see `clothing-creation-pipeline`) | Pattern pillows/duvets/sofa covers; Pressure property (a 2016 tutorial used ~20, normals outward, gravity off), Shrinkage Weft/Warp, pin + sew for tufting [W] | Hero bedding/sofas; retopo after |
| Pillow Maker (shift4cube, Gumroad) | listed free [W] | Plane + cloth pressure setup, collision distance 0.001 [W] | Not tested; our presets replace it |
| ClothMaster (Superhive) | paid [W] | One-click cloth incl. "turn any object into a pillow" [W] | Not tested |
| Sollumz | GPL-3.0 | GTA export, Auto LOD, collision materials, env-cloth fragments | Required for GTA (`fivem-mlo-creation`) |

## 3. Asset sources

| Source | License | Notes |
|---|---|---|
| Poly Haven | CC0 [W] | fabric/leather textures, some sofa/pillow models; use as reference or texture source |
| ambientCG | CC0 [W] | Fabric and Leather categories |
| Fab | Standard License (commercial use/modification, no standalone redistribution; Personal < 100 k USD) or CC-BY [W] | check each listing; log licenses |
| RenderHub / Superhive / Gumroad pillow packs | per product (often restrictive "extended" licenses) [W] | read before shipping in a FiveM resource |
