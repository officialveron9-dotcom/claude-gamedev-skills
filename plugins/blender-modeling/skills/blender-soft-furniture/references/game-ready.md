# Game-ready soft furniture (GTA V/FiveM via Sollumz, Unreal Engine 5.8)

Contents: pipeline · budgets · reduce (decimate/retopo) · UVs and bakes · LODs · collision · GTA: props vs merged,
shaders, limits · UE: Nanite, collision, export.
Base rules live in `fivem-mlo-creation` (rooms, entities, entity sets, export, streaming) and
`blender-game-export` / `blender-python-pitfalls` §9 (FBX for UE). This file adds what is specific to soft goods.

## 1. Pipeline

| Step | Tool | Gate |
|---|---|---|
| 1 High | sim result + Subdivision + tufting + piping (keep in a `HIGH` collection) | looks right in a render |
| 2 LOD0 | `SF.game_ready(high, target_tris=...)` (Decimate Collapse, triangulated) or retopo (`scenario-blender-retopology`) for hero pieces | tris ≤ budget, silhouette kept |
| 3 UVs | `SF.ensure_uv` (Smart UV 66°, margin 0.02) or proper seams (`scenario-blender-uv-baking`) | no overlaps, texel density per project |
| 4 Bake | `scenario-blender-uv-baking` `bake_high_to_low`: normal, AO (+ curvature for wear) | inverted texels < 2 % |
| 5 LOD1/2 | `SF.game_ready(..., lod_ratios=(1, 0.5, 0.25))` or Sollumz Auto LOD | no popping at switch distance |
| 6 Collision | `UCX_` boxes (UE) / Sollumz Bound Box (GTA) | convex, simple |
| 7 Material | Sollumz shader material / UE material with baked maps | |
| 8 Export | Sollumz Export / FBX | test in engine |

Measured: a subdivided 0.5 m KNIFE pillow is 11.6 k tris; `game_ready(target_tris=1500)` → LOD0 1 500, LOD1 750,
LOD2 374, `UCX_Pillow_00` 8 verts/12 tris containing the mesh, UVs on every LOD, 1.5 s [T, 4.5.14 + 5.2.2].

## 2. Budgets (LOD0; practice starting points — Rockstar and Epic publish none)

| Item | GTA prop / MLO | UE (non-Nanite) | UE Nanite |
|---|---|---|---|
| Throw pillow | 300–800 | 500–1 500 | 2–10 k |
| Seat/back cushion | 300–1 000 | 800–2 000 | 5–20 k |
| Mattress | 300–800 | 500–1 500 | 2–10 k |
| Duvet/blanket | 1.5–4 k | 3–8 k | 20–60 k |
| Sofa soft parts (all cushions) | 3–8 k | 6–15 k | 50–150 k |
| Curtain panel | 0.8–3 k | 2–6 k | 10–40 k |
| Tufted panel | bake tufting into normal/AO, 500–2 k | 2–6 k + normal | 30–100 k geometry |

Reference points: muto-atlas measured a vanilla `a_c_rottweiler_02.ydd` at 11 303 tris and notes that a
150 k-tri model slows collision calculation [S, muto-atlas]. Keep every MLO drawable well under the streaming
warnings (16/32/64 MiB, `fivem-mlo-creation`).

## 3. Reduce

- Decimate **Collapse** handles smooth cloth well (organic, no hard edges); keep `use_collapse_triangulate`;
  protect seams/piping with a vertex group + Invert/Factor if they collapse.
- Sim meshes are regular grids: Sollumz Auto LOD's **Un-Subdivide** method suits meshes made by subdivision
  (not executed on these meshes).
- Piping/buttons/stitches: real geometry on LOD0 only for hero props; otherwise bake into normal + AO.
- Never ship the cloth mesh with a Subdivision modifier unapplied — Sollumz/FBX export evaluates modifiers
  depending on settings; apply or use the evaluated copy (`game_ready` does).

## 4. UVs and bakes

- Generated meshes have **no UV map**. A UV-less mesh exported through Sollumz shares no vertices
  (vertices = 3 × triangles, file ~4×) [S, muto-atlas measured on Sollumz 2.9]. Unwrap before export.
- Bake from the high (sim + subsurf + tufting + piping) to LOD0: normal + AO. UE: DirectX normal (green down).
  GTA normal maps: only R/G are read, Z rebuilt (`gta-texture-editing`); match the green direction of a vanilla `_n`
  map in CodeWalker (verify).
- Texel density: 512 px/m baseline, 1 024 px/m for props seen up close (beds/sofas in first person)
  (`blender-furniture-modeling`, `scenario-blender-uv-baking`). Tiled weave goes to a detail map, not the unique map.

## 5. LODs

| Engine | How |
|---|---|
| GTA (Sollumz) | Mesh → Sollumz LODs High/Medium/Low/Very Low; *Auto LOD* (methods Collapse / Un-Subdivide / Planar, decimate step 0.6, optional per-LOD ratios default 0.90/0.70/0.50/0.30/0.15 or target tris per LOD, optional auto LOD distances) [S, Sollumz `ydr/operators/lod_tools.py`] |
| UE non-Nanite | LOD0–2 from `game_ready` (FBX with `_LOD1`… or auto LOD in UE) |
| UE Nanite | one high mesh; LODs not needed (fallback mesh is generated) |

## 6. Collision

| Item | GTA (Sollumz Bound) | UE |
|---|---|---|
| Pillow | none (small decor), or Bound Box FEATHER_PILLOW | none or `UCX_` box, no collision for scattered decor |
| Seat cushion / sofa | Bound Box per seat + one for back/arms, material FOAM or CLOTH (fabric) / LEATHER | `UCX_` per part |
| Bed | Bound Box at mattress top (FOAM), frame boxes from the sibling skill | `UCX_` mattress + frame |
| Curtain | none | none |

Collision material indices in Sollumz: CARPET_SOLID 97, CLOTH 100, FOAM 106, FEATHER_PILLOW 107, LEATHER 109
[S, Sollumz `ybn/collision_materials.py`]. Never use a poly copy of a sim mesh as collision.

## 7. GTA MLO: separate props vs merged into the room drawable

| Choose | When | Cost / limit |
|---|---|---|
| **Separate archetype** (own `.ydr`, MLO entity in a room) | big/hero items (bed, sofa), reused across rooms/MLOs, variants via **entity sets** (made/unmade bed, cushions on/off), item must have its own collision and `lodDist` | one entity + draw call(s) each; entity must be attached to a room; ≤ 12 entities in `limbo` |
| **Merged into the room/decor drawable** | small static clutter of one room (scatter pillows, folded throws) | no reuse or toggling; drawable ≤ 128 materials/geometries on Gen9 (reported) |
| Middle way | one `abc_room_decor` drawable per room with one atlas material | best for many small pieces |

- Entity sets: toggle with `ActivateInteriorEntitySet` + `RefreshInterior` (`fivem-mlo-creation` → mlo-rooms-portals).
- Interior lighting: GTA reads vertex colour 0 R/G as ambient multipliers [S, CodeWalker shader notes in
  `gta-texture-editing`]; props inside an MLO should carry the same vertex colour logic as the shell
  (R≈0, G 0.4–0.8) or they light differently (verify per shader).
- Sollumz splits geometries at 65 535 vertices automatically [S, muto-atlas measured]; budgets above stay far below.
- Gen9/Enhanced: same files, `stream_enhanced/` (`fivem-mlo-creation`).

## 8. Unreal Engine 5.8

- Nanite: enable on opaque static soft props (pillows, mattress, duvet, sofa cushions); masked/translucent sheers →
  programmable raster or not Nanite; WPO sway → raster + VSM invalidation (`ue5-performance-optimization`).
- Fallback mesh is used for collision, HWRT and non-Nanite paths; check *Fallback Relative Error* on hero pieces.
- Collision: `UCX_<mesh>_00` boxes exported with the mesh (FBX), or simple collision in the editor.
- Export: FBX settings in `blender-python-pitfalls` §9; apply transforms; 1 m test cube.
- Sitting/sleeping interactions need no soft collision: use boxes; animate the dent with a morph target only for hero
  shots.
