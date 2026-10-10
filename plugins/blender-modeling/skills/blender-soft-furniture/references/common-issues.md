# Common issues: symptom → cause → fix

Versions: [T] reproduced headless on Blender 5.2.2 and 4.5.14 (bpy module); [S] from source; [W] web report;
(verify) not reproduced. Add solved bugs from the owner here with the exact symptom and version.

## Simulation

| Symptom | Cause | Fix | Ver. |
|---|---|---|---|
| Cloth falls straight through the mattress/sofa, collider ignored the whole bake | Collider was never evaluated before the cloth object was created (scripted scenes) | `bpy.context.view_layer.update(); bpy.context.evaluated_depsgraph_get()` after creating colliders, before creating the cloth object (`SF.register_colliders`); evaluating just before adding the Cloth modifier was not enough | [T] 5.2.2 |
| Cloth falls through in the UI | No Collision physics on the collider, or Collision modifier above a modifier that creates the shape; collider faces too large vs cloth speed | Add Collision (it uses the mesh at its stack position — keep it last); raise cloth Collision Quality 4–6 | [S] |
| Blanket floats 2–3 cm above the bed | Cloth Distance 0.015 + collider Thickness Outer 0.02 (defaults) | 0.003 + 0.002 → 5 mm gap | [T] |
| Blanket clips into the mattress | Distance/Outer too small for edge length or speed; Quality low; Solidify grows inward | Quality 8, Collision Quality 4; drop from 2–3 cm; Solidify offset +1 | [T] |
| Blanket slides off the bed | Collider Cloth Friction 5 vs heavy overhang | Friction 40; shorter foot overhang; pin a strip under pillows | [T] |
| Overhang keeps swinging / never settles | Air Viscosity 1 | 10 (RNA max); 60 frames; check `max_step` < 2 mm | [T] |
| Result differs every time, looks half-done | Evaluated an unbaked cloth at the last frame | Bake or `frame_set` every frame from the start | [T] |
| Cloth explodes / NaN / huge jitter | Overlapping or n-gon faces at frame 1, pressure way too high, scale not applied, tiny edges next to big ones | All-quad even mesh; apply scale; pressure ∝ edge length; Quality 8+; start with a gap | [T] |
| Pillow tumbles away / drifts | Gravity 0 with asymmetric forces (n-gons, flipped normals) | Fix base mesh (recalc normals, all quads); recentre after apply | [T] |
| Cloth is "rubbery", stretches under weight | Tension 15 (default) on long drops | Tension 40–60 (curtain: 12 → 5.5 mm stretch at 2.4 m) | [T] |
| Sim takes minutes | Subdivision above Cloth; self-collision on everything; 1 cm grid on 2 m blankets; default collision distance | Sim low-res, subdivide after; 3–4 cm grid; distance 0.003 (46 s → 30 s measured); self-collision group | [T] |
| Wrong scale behaviour (sim of a 50 m "pillow") | Object scale not applied / cm scene | Apply scale, metres, unit scale 1 (`blender-python-pitfalls`) | [S] |

## Pillows and cushions

| Symptom | Cause | Fix | Ver. |
|---|---|---|---|
| Balloon pillow (thickness/width > 0.45) | Pressure too high for the edge length (1 cm edges need half the pressure of 2 cm) | Presets in `PILLOW_PRESETS`; tune shrink first | [T] |
| Box cushion balloons | Bending 0.5–1 | Bending 2, pressure 0.3 @ 2 cm | [T] |
| Round pillow stays flat | Shrink 0, or pole/fan mesh | Shrink 0.02–0.06 with self-collision; disc-mapped quad grid | [T] |
| Pinch folds through itself | Self-collision off at the seam pinch | Self-collision 0.003 (ROUND preset) | [T] |
| Twisted, folded pillow | N-gons from partial `subdivide_edges` | All-quad shell (`pillow_base`) | [T] |
| Hard, razor seam | Subdivision of a creased loop only | Piping cord (`add_piping`, 3–5 mm) or crease + slight inward scale | |
| Pinch artifacts at corners after Subdivision | Triangles/poles at corners; extreme shrink | Lower shrink; Smooth brush; keep quads | |
| Every pillow identical | Copies of one sim | Vary size/rotation ±5 %, different dents | |

## Bed, blanket, curtains

| Symptom | Cause | Fix | Ver. |
|---|---|---|---|
| Spike/huge bulge after Solidify | Even Thickness at a sharp fold | Even off (Clamp did not help) | [T] |
| Turn-down layers intersect after Solidify | Folded flap normals point down/inward | `lift_group(ob, "fold", 2 × thickness)` along −normal before Solidify | [T] |
| Duvet too smooth (uniform tension) | High bending, coarse grid | Bending 0.5–1, 2–3 cm grid near folds, sculpt compression | |
| Fitted sheet slides/wrinkles wrong in a sim | Sims cannot hold tight elastic fits | Shell + Displace (`fitted_sheet`), sculpt corner gathers | [T] |
| Curtain top sags | Pin group missing or `vertex_group_mass` not set | Pin top row, pin stiffness 1 | [T] |
| Curtain bottom too long after sim | Stretch under gravity | Tension 60 or shorten drop by the measured stretch | [T] |

## Tufting

| Symptom | Cause | Fix | Ver. |
|---|---|---|---|
| `TypeError: bpy_struct[key] = val: id properties not supported for this type` setting a GN input | 5.2 moved modifier inputs | `getattr(mod.properties.inputs, sock.identifier).value = v` (≤ 5.1: `mod[identifier]`) | [T] 5.2.2 |
| No tufting visible | Vertex group `tuft` missing/zero (Named Attribute returns 0) | `tuft_mask(ob)`; panel must face +Z local while building | [T] |
| Faceted dimples | Base too coarse | Edges ≤ radius/1.5 + Subdivision 1–2 below GN | |
| Buttons hidden | Seated at the dimple bottom | Seat on the ring at the button radius (`place_buttons`) | [T] |
| Tufting on the sides | Mask threshold too low | `min_normal_z` 0.7+, margin 0.04–0.08 | |

## Shading

| Symptom | Cause | Fix |
|---|---|---|
| Sofa looks like plastic | Roughness 0.5 default, no sheen, uniform colour | Fabric roughness 0.8–0.95 + Sheen; leather 0.35–0.5 + grain; variation |
| `KeyError: ... key "Sheen" not found` | 3.x name | `Sheen Weight` (4.0+) |
| Velvet reads as felt | Sheen Weight 0 / Sheen Roughness too high | Sheen 1.0, Sheen Roughness 0.3, darker base |
| Weave moiré in the distance | Bump frequency above pixel size | Fade weave with distance (UE) / detail map mip; lower strength |
| Faceted shading on the game mesh | Flat shading after decimate; custom normals lost | Shade smooth; weighted normals not needed on soft goods; bake normal from the high |
| Stretched textures | Smart UV on a sim mesh with stretched islands; Object coords with unapplied scale | Re-unwrap with seams (`scenario-blender-uv-baking`); apply scale |

## Game export

| Symptom | Cause | Fix |
|---|---|---|
| Poly count far too high | Exported the sim/subdivided mesh (11.6 k tris for one pillow) | `game_ready` / retopo to the budget, bake detail |
| Sollumz file ~4× larger than expected | Mesh without UVs: no shared vertices [S, muto-atlas] | Unwrap (`ensure_uv`) before export |
| Normal bake artifacts (inverted patches, seams) | Cage/extrusion, overlapping UVs, low too far from high | `scenario-blender-uv-baking` measure_projection; unique UVs; triangulate before bake |
| Normal map green inverted in UE | OpenGL vs DirectX | Bake DirectX (green down) for UE |
| Prop invisible in the MLO | Entity not attached to a room / limbo count > 12 | `fivem-mlo-creation` |
| `model ... has no Sollumz materials! Aborting...` | Principled material left on the mesh | Convert to Sollumz shader material (`normal_spec`) |
