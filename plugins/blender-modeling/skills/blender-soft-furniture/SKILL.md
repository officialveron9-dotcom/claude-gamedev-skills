---
name: blender-soft-furniture
description: "Builds photorealistic soft furniture and textiles in Blender without the usual artefacts and makes them game-ready for GTA V/FiveM MLOs (Sollumz) and Unreal Engine 5.8: pillows and cushions (cloth pressure, shrink, seams, piping), mattress, duvet/blanket drape and turn-down, sofa and headboard upholstery, Chesterfield tufting with Geometry Nodes, throws, curtains, fabric materials, LODs, collision, with tested bpy scripts. Use for pillow, cushion, blanket, duvet, bed sheet, mattress, sofa, armchair, tufting, Chesterfield, curtain, cloth simulation, pressure, upholstery, soft furniture, or German \"Kissen\", \"Decke\", \"Bett\", \"Sofa\", \"Möbel\", \"Polster\", \"Vorhang\", \"realistische Möbel\"."
---

# Blender soft furniture (pillows, beds, upholstery, curtains) → GTA MLO / UE 5.8

Reader: Claude. Checked 2026-10-10. Every number tagged **[T]** was measured headless by
[scripts/sf_selftest.py](scripts/sf_selftest.py) on Blender **5.2.2 LTS** and **4.5.14 LTS** (bpy module);
**[S]** = read in Blender/Sollumz/CodeWalker source; **[W]** = web/search snippet only; **(verify)** = unconfirmed.

Scope: soft goods only. Frames, legs, carcasses, bed frames and all real-world **dimensions** →
`blender-furniture-modeling` (its `make_bed_frame` stores `obj["mattress"]`, consumed by `SF.mattress_from_frame`).
Related: `blender-python-pitfalls` (bpy API), `scenario-blender-retopology` / `scenario-blender-uv-baking`
(low poly, bakes), `fivem-mlo-creation` (entities, rooms, collision, export), `gta-texture-editing` (YTD/DDS),
`clothing-creation-pipeline` (Marvelous Designer, fabric texturing), `ue5-performance-optimization` (Nanite).

## Pick the method

| Item | Method | Why |
|---|---|---|
| Throw pillow, round pillow, bolster | Closed mesh + Cloth **Pressure**, gravity 0, Shrink → apply (`SF.make_pillow`) | Only a sim gives corner pinches and tension wrinkles |
| Seat/back cushion (foam) | BOX shell + low pressure + bending 2 → apply → `add_dent` for sag | Foam keeps the gusset; pure pressure balloons |
| Mattress | Box + Bevel (0.03–0.05 m, 4–6 seg) + piping on welt loops; no sim | Rigid; realism comes from the welt and slight crown |
| Duvet, blanket, bedspread, throw | Thin grid → drape on Collision object → apply → Solidify +1 | Thickness during the sim breaks collision |
| Turn-down / folded edge | Pre-shape the fold in the mesh, then sim (`fold_back=`) | Cloth does not fold itself reliably |
| Chesterfield / diamond tufting | GN displacement + buttons (`add_tufting`, `place_buttons`) | Parametric, exact, no sim; sim-tufting with pins is slow and noisy |
| Channel tufting, quilting stitches | Model the loops + crease, or sculpt; cloth only for puff | Lines must stay straight |
| Curtain | Pleats shaped as a sine first, top pinned, short sim (`make_curtain`) | The sim only relaxes the pleats |
| Hero bedding/sofa for close-ups | Marvelous Designer (pattern + pressure) → retopo in Blender | Real sewing seams; see `clothing-creation-pipeline` |

## Top traps (each one was hit while testing)

1. **No colliders registered → cloth falls through.** Colliders that are first evaluated together with a new cloth
   object are ignored for the whole bake. Evaluate the depsgraph after creating colliders and **before creating the
   cloth object** (`SF.register_colliders()`); doing it right before adding the Cloth modifier was not enough **[T]**.
2. **Jumping to the last frame.** An unbaked cloth evaluated at frame N without stepping gives a wrong shape
   (0.4 m pillow at frame 15: 4.3 cm instead of 7.4–7.7 cm thick) **[T]**. Bake (`ptcache.bake` with `point_cache` override) or
   `frame_set` every frame; both give identical results **[T]**.
3. **Bad base mesh.** `bmesh.ops.subdivide_edges` on only the X/Y edges of a cube leaves **28-gons**; the pillow then
   twists and folds through itself **[T]**. Build all-quad shells (`SF.pillow_base`). No poles/fans on round panels:
   a revolved disc barely inflated (ratio 0.11) **[T]**.
4. **Pressure is resolution-dependent.** Same settings, 2 cm edges → thickness/width 0.26; 1 cm → 0.50 (balloon)
   **[T]**. Scale pressure with edge length (presets: 60 × edge for KNIFE).
5. **Floating blanket = default collision distances.** Cloth `distance_min` 0.015 + collider `thickness_outer` 0.02 →
   3.1 cm gap; 0.003 + 0.002 → 5 mm with zero clipping **[T]**. Rest gap ≈ sum of both.
6. **Blanket slides off.** Collider friction 5 (default) let a 0.55 m foot overhang pull the duvet off the bed;
   friction 40 held it **[T]**. Hanging parts still swung 26–110 mm/frame at frame 60 with air damping 1; 10 (RNA max)
   settled to 1.2 mm **[T]**.
7. **Solidify Even Thickness spikes** at the turn-down fold (+0.48 m, 20 self-intersections); Clamp did not help;
   Even off fixed it **[T]**. The folded flap's normals point down/inward: push it out by 2 × thickness along −normal
   before Solidify or both shells clip the mattress (117 tri pairs) **[T]**.
8. **Shrink is what lets a flat panel dome.** Round pillow, shrink 0 → ratio 0.11; with self-collision on, shrink
   0.06 → 0.53 (balloon) **[T]**. Tune shrink first, pressure second.
9. **Self-collision changes inflation.** ROUND pillow: off → 0.28 ratio but 26 intersecting tri pairs at the pinch;
   on → needs lower pressure/shrink (preset 0.6 @ 2 cm, shrink 0.02) **[T]**.
10. **5.2 GN modifier inputs**: `mod["Socket_0"] = x` raises `TypeError: bpy_struct[key] = val: id properties not supported
    for this type`; use `mod.properties.inputs.Socket_0.value` (≤5.1: the idprop way) **[T]**.
11. **Procedural fabric does not export.** Sollumz needs Sollumz shader materials, UE needs textures: bake first.

## Settings (start here; all [T] unless tagged)

| Setup | Values |
|---|---|
| Pillow cloth (all shapes) | gravity (Field Weights) 0, Pressure on, `pressure_factor` 1, Quality 8, mass 0.3, air 1, tension/compression 15, shear 5, 45 frames (settles to < 1–4 mm/frame) |
| KNIFE 0.5 × 0.5, 2 cm edges | Pressure 1.2, Shrink 0.10, Bending 0.5, self-coll off → 0.44 × 0.13 m, ratio 0.29 |
| BOX 0.6 × 0.6 × 0.10 | Pressure 0.3, Shrink 0.05, **Bending 2** → 0.15 m thick, crown 2.2 cm (bending 0.5–1 → 0.21–0.27 m, balloon) |
| ROUND Ø 0.45 | Pressure 0.6, Shrink 0.02, Bending 0.5, **self-coll on** (0.003) → ratio 0.32–0.36 |
| BOLSTER 0.5 × Ø 0.2 | Pressure 1.0, Shrink 0.05 → keeps Ø 0.19, caps bulge |
| Drape (duvet) | grid 3–4 cm, Quality 8, collision quality 4, `distance_min` 0.003, self-coll 0.003, mass 0.4, bending 2, air damping 10; collider outer 0.002, inner 0.05, cloth friction 40; 60 frames; 3.2 k verts: 12 s |
| Curtain 1.4 × 2.4, fullness 2 | top row pinned (`vertex_group_mass`), tension 60 (stretch 5.5 mm; tension 15: 12 mm), bending 1, self-coll 0.004, 40 frames |
| Tufting (GN) | diamond spacing 0.12, button depth 0.025, radius 0.015, pleat depth 0.010, width 0.006, base edges ≤ 1 cm + Subdivision 1 |

Real-world sizes (pillows 40–65 cm, mattress thickness 0.18–0.30 m, top 0.45–0.60 m): `blender-furniture-modeling`.

## Workflows (detail in references)

- **Pillow**: `pillow_base` → `add_pillow_cloth` → `simulate` → `apply_cloth` → `add_piping` (seam group) →
  Subdivision 1 → `add_dent`/sculpt for use marks → material. [references/pillows-cushions.md](references/pillows-cushions.md)
- **Bed**: frame from `blender-furniture-modeling` → `mattress_from_frame` → fitted sheet (Shrinkwrap shell) →
  `drape_blanket(fold_back=0.35)` → pillows settled with gravity → wrinkle pass. [references/beds-blankets.md](references/beds-blankets.md)
- **Sofa/armchair**: frame + legs from the sibling skill; every cushion a separate BOX object; welts = piping; seat
  sag = dent or settle sim; tufted back = `add_tufting` + `place_buttons`; throw = drape on the arm.
  [references/sofas-tufting.md](references/sofas-tufting.md)
- **Curtain**: `make_curtain` (fullness 2–2.5, pinned heading) → Solidify 2 mm → hem. [references/curtains.md](references/curtains.md)

## What makes soft furniture look fake

| Fake | Real |
|---|---|
| Balloon pillow (ratio > 0.45, no corner pinch) | Ratio 0.25–0.35, dog-eared corners, tension wrinkles toward corners |
| Uniform tension, perfectly smooth duvet | Lower bending/finer grid where it folds; sculpted compression around pillows |
| Floating or clipping blanket | 3–5 mm rest gap, contact shadow (AO) under every fold |
| Perfect symmetry, identical pillows | Rotate/scale each ±3–5 %, one dent, one pillow leaning |
| Razor seam edges | Piping cord 3–5 mm radius, or creased seam loop + Subdivision |
| Plastic sofa | Roughness 0.8–0.95 + Sheen for fabric; leather 0.35–0.5 with grain bump and creases |
| Flat colour | ±3–6 % value variation, wear on arms/seat front, dust in creases |
| Normal-map-only folds | Large folds in geometry, medium in baked normal, weave in tiled detail |

Fabric values, CC0 sources, GTA/UE shader mapping: [references/materials.md](references/materials.md).

## Game-ready (summary)

- Pipeline: sim/high mesh → **LOD0** (decimate or retopo) → UV → bake normal + AO from the high
  (`scenario-blender-uv-baking`) → LOD1/LOD2 → collision → export. `SF.game_ready()` does LODs, Smart UV and a box
  (`UCX_`) hull. Never export the sim mesh: 11.6 k tris for one subdivided pillow **[T]**.
- Budgets (LOD0, practice, not Rockstar/Epic figures): throw pillow 300–800 tris, seat cushion 300–1 000,
  duvet 1.5–4 k, mattress 300–800, sofa soft parts 3–8 k, curtain panel 0.8–3 k. UE + Nanite: keep more geometry
  (opaque soft goods are fine Nanite candidates), still decimate sims to clean meshes.
- GTA: static props use `normal_spec` (Sollumz auto-picks it when a Principled material has normal + specular image
  nodes) or `normal_spec_detail` for a tiled weave **[S]**. The `cloth_*` shaders carry `IS_CLOTH` and are for
  simulated env-cloth fragments (YFT, ≤ 1 000 verts in Sollumz), not static furniture **[S]**.
- GTA collision: Bound Box/primitives per item, materials FEATHER_PILLOW (107), FOAM (106), CLOTH (100),
  LEATHER (109), CARPET_SOLID (97) **[S]** (Sollumz index); never a poly copy of a sim mesh.
- Separate props (own archetype, MLO entity, entity sets for variants) vs merged into the room drawable: decision
  table in [references/game-ready.md](references/game-ready.md).

## Automation

```python
import sys; sys.path.append(r"<skills>/blender-soft-furniture/scripts"); import sf_soft as SF
p = SF.make_pillow("Pillow_A", "KNIFE", (0.5, 0.5)); SF.add_piping(p)
bed = SF.make_mattress("Mattress", (1.6, 2.0, 0.24), top_z=0.6)        # or SF.mattress_from_frame(frame)
duvet = SF.drape_blanket(bed, size=(2.2, 2.3), fold_back=0.35)          # fold lifted, Solidify, Subdiv
SF.add_tufting(cushion); SF.place_buttons(cushion)
lods, ucx = SF.game_ready(p, lod_ratios=(1.0, 0.5, 0.25), target_tris=600)
```

Run the self-test before trusting a new Blender version:
`blender -b --factory-startup --python-exit-code 1 -P scripts/sf_selftest.py` (or `python sf_selftest.py` with the
`bpy` module); full API, measured results, how baking works headless: [references/scripts.md](references/scripts.md).

## Fast triage (full table: [references/common-issues.md](references/common-issues.md))

| Symptom | First check |
|---|---|
| Cloth falls straight through the bed | Colliders not evaluated before the cloth object was created; Collision modifier missing |
| Blanket floats 2–3 cm | Default `distance_min` 0.015 + `thickness_outer` 0.02 |
| Blanket slides off / keeps swinging | Collider friction 5 → 40; air damping 1 → 10; overhang too long |
| Pillow is a balloon | Pressure too high for the edge length; shrink too high with self-collision; bending too low (BOX) |
| Pillow twists/folds through itself | N-gons/poles in the base mesh; self-collision off on round pillows |
| Shape differs every time / looks unfinished | Jumped to the last frame instead of baking/stepping; not settled (check movement per frame) |
| Spikes or clipping after Solidify | Even Thickness on; folded flap's normals point inward |

## Checklists

**Pillow/cushion**
- [ ] All-quad closed shell, edge length chosen first (2 cm prop, 1 cm hero), scale applied.
- [ ] Pressure/shrink/bending from the preset for that edge length; 45 frames; < 2 mm/frame at the end.
- [ ] Ratio 0.25–0.35 (throw) / crown 1–3 cm (seat); 0 self-intersections; corners pinched.
- [ ] Piping on the seam group; Subdivision 1; dent or lean; each copy varied.

**Bed**
- [ ] Mattress from the frame's stored box; bevelled; welts piped; Collision outer 0.002, friction 40.
- [ ] Duvet: 3–4 cm grid, fold pre-shaped, colliders registered first, 60 frames, settled.
- [ ] Gap 3–6 mm, 0 verts inside, 0 tri overlaps before and after Solidify (Even off, offset +1).
- [ ] Pillows settled on the mattress (gravity on) with a dent where the head lies.

**Sofa/armchair**
- [ ] Frame/legs from `blender-furniture-modeling`; each cushion separate; seat sag; welts on all cushion seams.
- [ ] Tufting mask covers the panel only; buttons seated in the dimples; leather vs fabric preset.
- [ ] Throw draped on the arm, not floating; asymmetry everywhere.

**Curtain**
- [ ] Fullness 2–2.5, pleats ≤ 12 cm, heading pinned, hem 1 cm above floor (or 2–5 cm break) after stretch.
- [ ] Self-collision on; Solidify 2 mm; GTA: static drawable unless it must sway (env cloth YFT).

**Game-ready export**
- [ ] LOD0 within budget, UVs, normal + AO baked from the high (DirectX green for UE).
- [ ] LOD1/LOD2 (or Sollumz Auto LOD), smooth normals, no sim mesh exported.
- [ ] Collision: `UCX_` boxes (UE) / Sollumz Bound Box with soft collision material (GTA).
- [ ] GTA: Sollumz shader material, textures power of two ≤ 1 024 per prop, separate archetype or merged per table.
- [ ] UE: Nanite on for opaque props, fallback checked; scale 1 cm test.

## References

| File | Read when |
|---|---|
| [references/pillows-cushions.md](references/pillows-cushions.md) | making any pillow/cushion: base meshes, measured sweeps, seams, piping, pinch, sag, sculpt |
| [references/beds-blankets.md](references/beds-blankets.md) | mattress, fitted sheet, duvet drape, turn-down, tuck, pillows on the bed, headboard |
| [references/sofas-tufting.md](references/sofas-tufting.md) | sofa/armchair cushions, welts, sag, tufting maths, buttons, leather, throws |
| [references/curtains.md](references/curtains.md) | curtains, pleats, heading, length, GTA env cloth, UE |
| [references/materials.md](references/materials.md) | fabric/leather shading, Principled names per version, CC0 textures, GTA/UE shader mapping |
| [references/game-ready.md](references/game-ready.md) | budgets, LODs, bakes, collision, Sollumz shaders, MLO entity vs merged, Nanite |
| [references/scripts.md](references/scripts.md) | running/extending `sf_soft.py`, headless baking, test results per version |
| [references/common-issues.md](references/common-issues.md) | any bug: symptom → cause → fix with version |
| [references/external.md](references/external.md) | other skills, add-ons, asset sources, licenses |
| [references/sources.md](references/sources.md) | where a fact comes from |
