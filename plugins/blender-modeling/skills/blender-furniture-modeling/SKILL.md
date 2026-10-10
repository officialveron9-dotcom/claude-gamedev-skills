---
name: blender-furniture-modeling
description: "Builds realistic, bug-free hard furniture in Blender at real-world size for GTA V/FiveM MLOs (Sollumz) and Unreal Engine 5.8: tables, desks, chairs, bar stools, shelves, wardrobes, cabinets, kitchen units, dressers, nightstands, bed frames, billiard tables. Dimension tables (EU/US), proportions, part-based construction, bevel + weighted normals, materials, cleanup, collision, LODs, budgets and tested bpy generators. Use for furniture, prop, archviz, proportions, dimensions, bevel, weighted normals, or German \"Möbel\", \"Tisch\", \"Stuhl\", \"Schrank\", \"Regal\", \"Küche\", \"Maße\", \"Proportionen\", \"realistische Möbel\"."
---

# Hard furniture in Blender (state 2026-10)

Scope: rigid furniture and carcasses as game props. Soft goods (mattresses, cushions, upholstery, pillows, blankets,
curtains, leather) → `blender-soft-furniture`; for beds and sofas this skill builds only frames, legs and carcasses.
Related skills (link by name): `blender-python-pitfalls` (bpy versions), `scenario-blender-hard-surface` (booleans,
bevel theory), `scenario-blender-uv-baking` (bakes, wear masks), `blender-game-export` (FBX/glTF, UCX),
`fivem-mlo-creation` (MLO entities, collision, budgets, export), `fivem-mlo-doors-windows` (`sz_*` Sollumz conversion,
glass shaders, room doors), `gta-texture-editing` (YTD/DDS), `billiards-game-dev` (pocket jaws, ball physics).
Tags: **[V]** verified headless on bpy 5.2.2 and 4.5.14, **[D]** read in source, **[S]** search snippet,
**(verify)** = practice/unconfirmed; tell the user.

## Non-negotiables

1. **Real size, in metres.** Scene unit scale 1.0. Take every size from [dimensions.md](references/dimensions.md),
   never from a scaled default cube. Put a 0.45 × 0.25 × 1.75 m box next to the piece before calling it done.
2. **Build from real parts**: top, legs, aprons, panels, back, plinth, doors, drawer fronts, handles. Each part is a
   closed shell; parts touch but never share vertices and never have coplanar same-facing overlapping faces.
3. **Bevel every edge 1–3 mm** with Harden Normals + Weighted Normal on smooth shading. The Bevel modifier default
   width is **0.1 m** [V]: always set it.
4. **Reveals 2–3 mm** between doors/drawer fronts (gap/2 at outer edges). Zero gap reads as a block.
5. **Origin at the bottom centre of the footprint**, rotation/scale applied, front faces −Y, Z up.
6. **Merge by distance per part only.** A global merge welds touching boards into non-manifold edges [V].
7. **Thin parts clamp the whole bevel**: Clamp Overlap is object-wide, a 3 mm back panel shrank a 2 mm bevel to
   1.5 mm everywhere [V]. Use a weight-limited bevel with thin parts weighted down (`finalize` does it).
8. **Game-ready**: LOD0 bevelled, LOD1 unbevelled, collision = a few boxes, glass separate, no hidden interiors
   unless fronts open.

## Workflow

| # | Step | Gate |
|---|---|---|
| 1 | Pick dimensions (table below, full set in [dimensions.md](references/dimensions.md)) | every size has a source or "(verify)" |
| 2 | Generate with `furniture_gen.py` ([generators.md](references/generators.md)) or model by parts ([construction.md](references/construction.md)) | parts count, bbox = parameters |
| 3 | `finalize(obj)`: transforms, per-part merge, normals, origin, Bevel + WN | 0 non-manifold, origin at floor |
| 4 | Materials + UVs (grain per part) ([materials.md](references/materials.md)) | texel density consistent |
| 5 | Collision + LODs (`make_collision`, `make_lods`) | tris within budget |
| 6 | Export: Sollumz (GTA) or FBX (UE) ([topology-cleanup.md](references/topology-cleanup.md) §6) | size checked in the target |
| 7 | Look: render/screenshot next to the 1.75 m box (`blender-verify`) | reads as real, no flicker |

## Key dimensions (metres; details, EU/US and tags in dimensions.md)

| Item | Numbers |
|---|---|
| Dining chair | seat 0.43–0.47, seat 0.40–0.50 wide × 0.40–0.45 deep, back top 0.80–0.95, tilt 5–10° (verify) |
| Office chair EN 1335-1:2020 | seat height range A 0.40–0.52, B 0.42–0.51, C 0.43–0.48 [S] |
| Dining table / desk | 0.73–0.76 / 0.72–0.75 (verify vs EN 527-1); 0.60 width per diner [S]; knee clearance ≥ 0.60 |
| Coffee / side table | 0.40–0.46 / 0.50–0.65 |
| Counter / bar | top 0.90–0.92 + stool 0.65 / top 1.05–1.10 + stool 0.75; seat → underside of top 0.25–0.30 [S] |
| Kitchen EU | worktop 0.90 (0.85–0.95), 0.038 thick, 0.60 deep; carcass 0.72 + plinth 0.10–0.15 (EN 1116 ≥ 0.08); wall units ≥ 0.45 above the worktop, 0.30–0.35 deep [S] |
| Kitchen US | counter 36 in (0.914), base 34.5 in, 24 in deep, toe kick ~4 × 3 in, wall cabinets 18 in above, 12 in deep [S] |
| Bookcase | 0.25–0.30 deep (BILLY 0.80 × 0.28 × 2.02 [S]); 18 mm shelves span ≤ 0.80 (verify) |
| Wardrobe | 0.58–0.60 deep, 2.01 / 2.36 high (PAX [S]); long hanging 1.6–1.8 clear |
| Dresser / nightstand | 0.75–1.00 × 0.45–0.50 deep / top level with the mattress top ±0.05 [S] |
| Beds | EU 0.90/1.40/1.60/1.80 × 2.00; UK double 1.35 × 1.90; US queen 60 × 80 in, king 76 × 80, Cal king 72 × 84 [S]; frame inner = mattress + 0.01–0.02 per side; mattress top 0.45–0.60 |
| Room door handle | 1.05 (DE practice [S]); cabinet handles: base units near the top edge, wall units near the bottom edge |
| Pendant lamp | 0.75–0.90 above the dining table top [S] |
| Pool table (WPA) | 9 ft 2.540 × 1.270 between cushion noses, bed 0.743–0.787, nose 63.5 % of the ball = 36.3 mm, mouths corner 4.5–4.625 in / side 5–5.125 in, 18 sights [S] |
| Snooker | 3.569 × 1.778, floor → top of cushion rail 0.864 ±0.013 (WPBSA 2022) [S] |

## Proportion rules that read as real

- Leg section ≈ height/12–height/15 for solid wood (0.05–0.07 on a 0.75 table), chairs 0.03–0.04, steel 0.02–0.04.
- Boards: carcass 16–19 mm, tops 25–40 mm, doors 18–22 mm, back 3 mm (8 mm grooved), drawer sides 12–16 mm.
- Top overhang 0.03–0.08 past the legs; aprons 0.07–0.12 high, set back 0.01–0.02; recessed plinths 0.06–0.15.
- Split doors wider than ~0.55–0.60; graduate drawer fronts (smallest on top).
- "Toy-like" = thick boards, fat legs, no bevels, no reveals, one material. Fix those first.

## Construction rules (details and wrong-vs-right: [construction.md](references/construction.md))

- Contact faces facing each other are hidden and fine. **Same plane + same facing + overlap = z-fighting.**
  Offset 1–8 mm: seat overhang, rail setback, back panel 2 mm inside the outline, staggered stretchers [V].
- Tilt a backrest about its front-bottom edge so it sinks into the seat; the back edge leaves a wedge gap [V].
- Splayed legs = sheared boxes with level top and bottom faces, not rotated boxes [V].
- Concealed cup hinges are invisible: do not model them. Handles: separate small parts, 25 mm proud.
- Grain (texture U) along the long axis: tops/shelves lengthwise, legs/sides/doors vertical, rails/drawer fronts
  horizontal. World-scale box UVs keep density constant and stop identical boards repeating [V].
- Imperfection goes into textures (roughness variation, edge wear, dust), not displacement.

## Bevel + normals (verified defaults and settings)

```python
bev = obj.modifiers.new("Bevel", "BEVEL")       # defaults: width 0.1 m (!), 1 segment, Harden off, Miter Sharp
bev.width, bev.segments, bev.profile = 0.002, 2, 0.5   # games 1-2 segments, renders 3
bev.limit_method = "ANGLE"                       # or "WEIGHT" + bevel_weight_edge (thin parts weighted down)
bev.harden_normals = True                        # creates custom normals itself (4.1+: no Auto Smooth needed)
bev.miter_outer = "MITER_ARC"
wn = obj.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
wn.keep_sharp = True                             # Face Area, weight 50 (defaults)
obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
```

Order: Booleans (EXACT, `scenario-blender-hard-surface`) → Bevel → Weighted Normal → Triangulate (Keep Normals on;
custom normals survive [V]). Mirror with merge: delete each half
part's face on the mirror plane first, or the merge leaves doubled inner faces (8 non-manifold edges) [V].

## Generators (tested: 276/276 checks on bpy 5.2.2 and 4.5.14)

| Function | Builds |
|---|---|
| `make_table` | top + 4 legs + aprons (dining, desk, coffee, bar table presets) |
| `make_chair` | seat, legs, seat rails, tilted back posts, slats, stretchers |
| `make_bar_stool` | round seat, 4 splayed legs with level feet, staggered footrests (0.65 / 0.75) |
| `make_shelf` | bookcase: sides, top, bottom, plinth, shelves, nailed-on back |
| `make_cabinet` | wardrobe, kitchen base/wall unit, sideboard, TV unit: carcass, PLINTH/KICK/LEGS/NONE base, overlay doors with gaps, bar/knob handles, worktop, optional separate doors with hinge pivots |
| `make_drawer_unit` | dresser, nightstand: graduated fronts, handles, optional drawer boxes |
| `make_bed_frame` | rails, ledgers, slats, legs, headboard from a mattress key (EU/UK/US); stores the mattress box for `blender-soft-furniture` |
| `make_billiard_table` | WPA/snooker playing surface, bed height, profiled cushions at nose height, pocket mouths, rails, sights (pocket jaws are placeholders) |
| `finalize`, `make_collision` (UE UCX / Sollumz bounds), `make_lods` | cleanup + Bevel/WN, collision, LOD1/LOD2 |

Asserted per object: bbox = parameters (±0.1 mm, bevelled ±1 mm), origin on the floor at the footprint centre,
closed parts with outward normals, 0 non-manifold, no z-fighting faces, custom normals, door/drawer gaps, hinge
pivots, chair tilt, cushion nose height, pocket mouths, FBX round trip. Code and conventions:
[generators.md](references/generators.md); harness: [generator-tests.md](references/generator-tests.md).
Not executed: Blender 4.2, Sollumz conversion, UE import, in-game checks.

## Materials (details: [materials.md](references/materials.md))

| Surface | Principled (4.0+ names) | GTA shader [D] |
|---|---|---|
| Wood oiled / lacquered | Roughness 0.45–0.65 / 0.35–0.5 + Coat Weight 0.3–1 | `normal_spec` (`normal_spec_detail` for tiling grain) |
| Painted MDF, laminate | Roughness 0.2–0.55, Metallic 0 | `normal_spec` (`normal_spec_tnt` for colour variants) |
| Brushed steel / chrome | Metallic 1, Roughness 0.25–0.4 / 0.02–0.1 | `normal_spec_reflect` / `spec_reflect` |
| Powder-coated metal | **Metallic 0**, Roughness 0.4–0.6 | `normal_spec` |
| Glass | Transmission Weight 1, IOR 1.52, real thickness | `glass*`, separate entity (doors skill) |
| Polished stone | Roughness 0.05–0.2 | `normal_spec_reflect` |

CC0 textures: Poly Haven, ambientCG [S]. Texel density 512 px/m baseline, 1024 px/m for close first-person props;
`meters_per_uv = texture_px / px_per_m`. GTA spec maps: R = intensity, A = gloss (not roughness).

## Game targets

- **GTA V / FiveM**: Sollumz exports the evaluated mesh (modifiers applied) and face-corner normals, so Bevel/WN
  survive with Mesh Domain "Face Corner" [D]. Hierarchy Drawable > `.model` + `.col` > box bounds
  (`make_collision(obj, "SOLLUMZ")`, then `sz_convert` from `fivem-mlo-doors-windows`). 1–4 materials per prop
  (Gen9 drawable limit 128). Set drawable LOD distances (Sollumz default 9998) and archetype lodDist (default 200)
  [D]. Place props as MLO entities in a room. Textures ≤ 2048, YTD < 16 MiB.
- **Unreal 5.8**: `finalize(triangulate=True)`, `UCX_<name>_NN` boxes, FBX with the settings in
  `blender-python-pitfalls` §9 (round trip kept 1.6 × 0.9 × 0.75 m [V]). Nanite for opaque furniture; glass in a
  separate non-Nanite mesh [S]. Import normals.
- Budgets (LOD0 tris, verify per project): chair 0.5–2k, table 0.3–1.5k, cabinet 0.5–3k, bed frame 1–3.5k,
  pool table 3–8k. Generator results at 2 / 1 bevel segments: table 972 / 396, wardrobe 1 512 / 616, pool 5 016 /
  2 328 [V].

## Top symptoms (full table: [common-issues.md](references/common-issues.md))

| Symptom | Cause | Fix |
|---|---|---|
| Looks toy-like / too thick | boards 30–50 mm, fat legs, no bevel, no reveals | real thicknesses, 1–3 mm bevel, 2–3 mm gaps |
| Melted edges after adding Bevel | default width 0.1 m | width 0.002 |
| Wrong scale in game | unit scale ≠ 1, scale not applied, FBX scale option | metres, `finalize`, `FBX_SCALE_ALL`, compare to a 1 m cube |
| Black/smeared shading | no custom normals, non-planar faces | Harden Normals + Weighted Normal, flatten faces |
| Z-fighting on a tabletop / joints | coplanar same-facing overlapping faces | offset 1–8 mm; decals ≥ 2 mm or decal shader |
| Bevel smaller than set everywhere | thin part + object-wide Clamp Overlap | weight-limited bevel (`finalize`) |
| Non-manifold after merge or mirror | global merge welds parts; closed half + Mirror merge | merge per part; open halves first |
| Grain runs the wrong way / stretches | one projection for all parts | per-part grain projection, rotate islands |
| Rotates around the wrong point / floats | origin not at the footprint bottom centre | `finalize` (min z = 0, footprint centred) |
| Flickers in GTA at distance | coplanar overlays, missing LODs, wrong lod distances | offsets, LOD1/LOD2, set lod distances |
| Too many polygons | 3+ bevel segments, hidden interiors, 32-segment rounds | 1–2 segments, 16–24 segments, LODs |
| Bevel artifacts on booleans | cut below the bevel, cutter near an edge | EXACT cut above the bevel (`scenario-blender-hard-surface`) |

## Checklists

**Every piece**
- [ ] Sizes from the tables; 1.75 m box comparison done; proportions checked (§ rules).
- [ ] Parts as closed shells; reveals 2–3 mm; no coplanar same-facing overlaps; thin parts identified.
- [ ] `finalize`: rotation/scale applied, origin at the floor (footprint centre), 0 non-manifold, outward normals.
- [ ] Bevel 1–3 mm (Harden Normals, Miter Arc), Weighted Normal last, smooth shading; materials per part, grain per part.
- [ ] Collision boxes, LOD1/LOD2, tris within budget; glass separate.

**Per type**
- Table/desk: knee clearance ≥ 0.60, aprons set back, top overhang 0.03–0.08.
- Chair/stool: seat height for its table/counter/bar, back tilt 5–10°, level feet, stretchers staggered.
- Shelf: span ≤ 0.80 at 18 mm, shelf setback 2–3 mm, back panel inside the outline.
- Cabinet/wardrobe/kitchen: depth incl. doors, plinth/kick, door count (≤ 0.6 m each), handle heights, worktop overhang.
- Drawers: graduated fronts, gaps, boxes inside the carcass if modelled.
- Bed frame: inner = mattress + clearance, slat gaps ≤ 0.07, mattress top 0.45–0.60, nightstand matched.
- Billiard: playing surface between noses, bed height, nose 63.5 % of the ball, mouths, sights, jaws modelled.

**Export**: GTA and UE checklists in [topology-cleanup.md](references/topology-cleanup.md) §6.

## References

- [references/dimensions.md](references/dimensions.md): read when sizing any piece (all tables, EU/US, proportions).
- [references/construction.md](references/construction.md): read when modelling by hand (parts, boards, bevel sizes, doors, grain, wrong vs right).
- [references/materials.md](references/materials.md): read when assigning materials, textures, GTA shaders or UE materials.
- [references/topology-cleanup.md](references/topology-cleanup.md): read before export (rules, modifier defaults, Clamp Overlap, budgets, collision, LODs, export checklists).
- [references/generators.md](references/generators.md): read **first** when scripting furniture (conventions, API, presets, full code).
- [references/generator-tests.md](references/generator-tests.md): read when changing the generators (harness, results, bugs found).
- [references/common-issues.md](references/common-issues.md): read when something looks or behaves wrong.
- [references/external.md](references/external.md): read when the user asks for add-ons or other skills.
- [references/sources.md](references/sources.md): read to check where a number comes from.
