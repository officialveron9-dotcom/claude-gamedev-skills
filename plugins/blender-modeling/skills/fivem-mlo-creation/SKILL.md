---
name: fivem-mlo-creation
description: "Turns an existing GTA V building into a walkable FiveM interior (MLO) with CodeWalker, Blender and Sollumz 2.9. Covers finding and exporting the building, hollowing it, rooms, portals, limbo, collision, lights, timecycles, occlusion, the vanilla LOD/ymap swap, export and streaming for FiveM Legacy and FiveM for GTAV Enhanced (Gen9), bpy automation, and fixes for invisible or black interiors and falling through floors. Use for MLO, interior, Sollumz, CodeWalker, ytyp, ymap, ydr, ybn, rooms, portals, collision, occlusion, walkable building, Blender GTA. German triggers: begehbar, Interieur, Gebäude aushöhlen, MLO erstellen, Innenraum, Kollision, Blender GTA."
---

# FiveM MLO creation: CodeWalker → Blender/Sollumz → FiveM

Reader: Claude. Checked 2026-10-10. Versions: **Sollumz 2.9.0** (released 2026-08-04, `main` = 2.9.0-dev),
Blender **4.2+** (Sollumz CI runs 4.0–5.2; the bpy snippets here were run on 4.5.14 LTS and 5.2.2 LTS),
**CodeWalker 30 Dev48+** (builds only in the CodeWalker Discord #releases; GitHub `master` frozen at 2025-04-11).
"(verify)" = not confirmed by a source; say so to the user.

Sibling skills (link by name): **`fivem-mlo-doors-windows`** (custom doors, garage doors, glass, door system
scripts), **`gta-texture-editing`** (YTD extraction, painting out painted-on doors/windows, DDS) — both in the
`blender-modeling` plugin; **`fivem-gta5-enhanced`** (Gen9, Alchemist, `stream_enhanced/`), **`fivem-server-setup`**
(streaming checklists, pool sizes). Owner workflow: every door, garage door and window is **built from scratch in
Blender** (no vanilla door/window props); this skill cuts the openings and builds the portals, the sibling skill
builds the door/glass objects that sit in them.

## Ground rules

- **Never overwrite vanilla drawables.** Give every new model a new, lowercase, prefixed archetype name
  (`abc_bldg_ext`, `abc_bldg_int`, `abc_bldg_mlo`); file name = archetype name; unique on the whole server.
- **MLO archetype name = collision `.ybn` name = Bound Composite object name in Blender.** CodeWalker's manifest
  generator writes `<Interiors><Item><Name>abc_bldg_mlo</Name><Bounds><Item>abc_bldg_mlo</Item>`; that link is
  how the game finds interior collision. Interior `.ybn` vertices are **MLO-local**; exterior/map `.ybn` are **world**.
- **One origin.** Shell drawable(s) and the collision composite share the MLO origin (floor centre, no rotation).
  Room bounds, portal corners and MLO entity positions are stored **relative to the composite's origin**
  (Sollumz subtracts `asset.location`). World position/rotation lives only in the ymap MLO instance.
- **Always ship `_manifest.ymf`** (CodeWalker Project → Tools → Manifest Generator). Without it an MLO that works
  in CodeWalker loads nothing in game (Sollumz FAQ, Cfx assets guide part 4).
- **Native binary export needs PyMateria** (Cfx library, Windows only, offered on Sollumz install). Without it
  Sollumz writes CW XML only and CodeWalker must import it.
- **Enhanced:** if `stream_enhanced/` exists, `stream/` is ignored. Put *all* streamed files (Gen9 `.ydr/.ytd`
  plus `.ytyp/.ymap/.ybn/_manifest.ymf`) in `stream_enhanced/`.

## Pipeline

| # | Step | Tool | Output | Gate before next step |
|---|---|---|---|---|
| 1 | Find building: archetype, HD ymap (+ `hei_` twin), LOD parent chain, `.ybn` + `hi@.ybn`, occluders | CodeWalker world view, DLC level = latest, "Enable DLC" | name list | every entity in the footprint listed (decals, overlays) |
| 2 | Export building, ground, decals, ybns, ymap | RPF Explorer → Export XML + "Save All Textures" into a folder named like the asset | `.ydr.xml`, `.dds`, `.ybn.xml`, `.ymap.xml` | opens in CodeWalker |
| 3 | Import | Sollumz Import (or 2.9 asset library: import one ymap, props auto-resolve) | scene | no pink textures (V → Find Missing Files) |
| 4 | New exterior archetype, openings cut for the custom doors/windows, original UVs/colours untouched | Blender | `abc_bldg_ext` drawable | pivot identical to vanilla; opening also cut in collision |
| 5 | Interior shell, slabs per storey, walls, stairs | Blender | `abc_bldg_int` drawable(s) | normals face rooms, `Color 1` G>0 R≈0 |
| 6 | Collision | Sollumz Composite → GeometryBVH → poly mesh | `abc_bldg_mlo` composite | flag preset applied, room IDs set |
| 7 | ytyp: base archetypes + MLO archetype, limbo + rooms, portals over every opening, entities, entity sets; custom door/glass entities attached to their portal (`fivem-mlo-doors-windows`) | Sollumz Archetype Definition | `.ytyp` | every entity in a room or on a portal, exit portals to `limbo` |
| 8 | Lights, vertex colours, timecycles | Sollumz | inside `.ydr` / `.ytyp` | no black/glowing faces in preview |
| 9 | Export | Sollumz "Export RAGE Assets" | `.ydr .ybn .ytyp` (gen8/ + gen9/) | file sizes > 0 |
| 10 | Place MLO, patch vanilla ymap, remove occluders, manifest | CodeWalker project (or Sollumz Maps panel) | `.ymap`, `_manifest.ymf` | MLO visible in CodeWalker with interiors on |
| 11 | Resource + test | FiveM | `stream/`, `stream_enhanced/` | checklist below passes after a reconnect |

Step details, CodeWalker clicks and LOD handling: [references/pipeline.md](references/pipeline.md).

## Exterior strategy (decide before modelling)

| Option | How | Use when | Risk |
|---|---|---|---|
| **A. Archetype swap (default)** | New `abc_bldg_ext` (vanilla mesh + openings, same pivot). In a copy of the vanilla HD ymap (and its `hei_` twin) change only that entity's `archetypeName`. MLO holds only the interior. | building has a LOD parent (most city buildings) | ymap conflict with other map resources streaming the same ymap |
| B. Exterior in limbo | Delete/hide the vanilla HD entity, put `abc_bldg_ext` into the MLO as a limbo entity (Sollumz tutorial style) | entity is `ORPHANHD` (no parent, no children) | exterior unloads with the interior → popping; LOD chain breaks if the entity had a parent |
| C. Empty lot | No vanilla edit; place MLO where nothing stands | new building | none |

Never delete a vanilla entity that is part of a LOD chain: indices shift, `parentIndex` points at the wrong entity,
all levels load at once (flicker, ghost copies). To hide one, change its archetype or move it `z -= 600`, and do
not touch the ymap extents (community-measured, muto-atlas). Details: [references/pipeline.md](references/pipeline.md).

## Hollowing essentials

- Keep the exterior mesh: cut openings only, never Solidify the exterior object. Build the inner shell as a
  separate mesh (copy → shrink along normals by wall thickness → flip normals) with its own materials.
- Wall thickness 0.2–0.3 m; storey height = floor-to-floor of the vanilla facade (windows tell you); slab 0.2 m.
- Openings: manual loop cuts/knife are cleaner than Boolean on vanilla meshes (non-manifold, split normals).
  If you use Boolean, use the `EXACT` solver and clean up afterwards.
- Select the facade's window faces by material/shader (`glass`, `emissive`), delete them from the shell and
  collision, and fill the openings with custom glass and door objects built per `fivem-mlo-doors-windows`
  (own archetypes, portal-attached). Painted-on doors/windows in the facade texture: `gta-texture-editing`.
- bpy helpers (verified 4.5/5.2): select faces by material, separate, inner shell, Solidify-apply, floor slabs,
  room boxes, vertex colour fill, batch rename → [references/blender-automation.md](references/blender-automation.md).

## MLO essentials

- Room 0 must be **`limbo`** (exact name; exit-portal count and Sollumz checks key on it), no timecycle,
  max **12 entities** attached to limbo (game limit; Sollumz 2.9.0 blocks the 13th, 2.9.0-dev warns on export).
- Every entity must be attached to a room; unattached entities are invisible. Props placed inside the MLO via a
  normal ymap are culled; put them in the MLO entity list.
- Portals: 4 corners on the opening plane, slightly larger than the opening; one per door **and per window**.
  Exit portal: `room_from` = room, `room_to` = limbo, Sollumz arrow pointing outward (corners counter-clockwise seen
  from outside, as in vanilla `v_int_66`); `Flip Direction` if not. Room↔room portals for internal doors.
- Floor collision materials carry the **Room ID** (index in the room list). The game detects the room by probing
  collision **4 units downward**; wrong/missing IDs = interior culls in first person, on stairs or when jumping.

| Flag set | Typical value | Meaning |
|---|---|---|
| Room flags | 96 (Reduce Cars+Peds, vanilla limbo); 111 dark/underground; 99/107 above ground | 4 = No Directional Light (blocks sun), 8 = No Exterior Lights, 256 = Dont Render Exterior |
| Portal flags | 0 exit door; 1 one-way; 2 link interiors; 64 hide when door closed; 8192 light bleed | |
| MLO flags | 1024 "Allow Run" (bit 10, verify behaviour) | Subway 256, Office 512, others in the reference |

Rooms, portals, entity sets, timecycles, instance fields, occlusion: [references/mlo-rooms-portals.md](references/mlo-rooms-portals.md).

## Collision and lighting essentials

- Composite → GeometryBVH (flag preset "General (Default)"; auto-applied on convert since 2.9.0) → poly mesh
  copy of floors/walls. Primitives (box/cylinder) for furniture. Materials: CONCRETE 1, MARBLE 14, WOOD_SOLID_POLISHED 72,
  LINOLEUM 95, CARPET_SOLID 97, PLASTER_SOLID 101 (Sollumz index).
- Stairs: a ramp plane with preset "Stair plane" for peds + steps with "Stair mesh"; or one smooth ramp.
- Interior faces: vertex colour `Color 1` R=0 (cuts sky/sun ambient), G>0 (artificial ambient); a shell with no
  colour layer or white colour glows at night; G=0 everywhere is pitch black.
- Room timecycle (Sollumz default `int_gasstation`); copy one from a similar vanilla MLO. Lights: Sollumz
  lights parented to the interior drawable, set `intensity` (not `energy`; energy = intensity × 500), never hide a light
  to disable it. Details: [references/collision-lighting.md](references/collision-lighting.md).

## Export and streaming essentials

```lua
-- fxmanifest.lua
fx_version 'cerulean'
games { 'gta5', 'gta5enhanced' }   -- Legacy-only: game 'gta5'
this_is_a_map 'yes'
-- optional; needed when archetypes are used without a ymap reference (e.g. script-spawned props):
-- data_file 'DLC_ITYP_REQUEST' 'stream/abc_bldg.ytyp'
```

Layout: `stream/` = Gen8 `.ydr/.ytd` + `.ybn/.ytyp/.ymap/_manifest.ymf`; `stream_enhanced/` = Gen9 `.ydr/.ytd` +
copies of the rest. Gen9 route: Sollumz Native+Gen9 (PyMateria) **or** Gen8 binaries → Alchemist / CodeWalker
Asset Converter. Settings, CodeWalker import, testing: [references/export-streaming.md](references/export-streaming.md).

Live check in game (CFX natives, client; Legacy-verified, verify on Enhanced):

```lua
RegisterCommand('mloinfo', function()
  local ped = PlayerPedId()
  local int = GetInteriorFromEntity(ped)
  local room = GetInteriorRoomIndexByHash(int, GetRoomKeyFromEntity(ped))
  print(('interior %d room %d %s flags %d tc %d'):format(int, room,
    room >= 0 and GetInteriorRoomName(int, room) or '-', room >= 0 and GetInteriorRoomFlag(int, room) or -1,
    room >= 0 and GetInteriorRoomTimecycle(int, room) or 0))
end)
```

`interior 0` while standing inside = MLO not loaded or floor collision has no room ID.

## Top symptoms (full table: [references/common-issues.md](references/common-issues.md))

| Symptom | Most likely cause | Fix |
|---|---|---|
| MLO visible in CodeWalker, not in game | no `_manifest.ymf`, or ytyp not loaded | generate manifest, `this_is_a_map 'yes'`, reconnect |
| Exterior vanishes when you step inside | no exit portal to `limbo`, portal flipped, or room flag 256 | add/fix exit portal, clear 256 |
| Interior invisible from outside / through door | portal missing/flipped, vanilla occluder in footprint | fix portal; delete occluders from the vanilla ymap copy |
| Disappears in first person, on stairs, when jumping | wrong/missing room ID on walkable collision; > 4 units above interior collision (tall rooms) | set room IDs everywhere; `SetInteriorProbeLength` |
| Fall through floor | ybn name ≠ MLO name, missing from manifest, no flag preset, world-space interior ybn | rename, regenerate manifest, apply preset, keep local |
| Flicker/z-fighting on facade | vanilla building still drawn + your exterior | archetype swap (option A), hide `hei_` twin too |
| Pitch black inside | `Color 1` G=0, missing timecycle, all entities in limbo | paint G, set room timecycle, attach to rooms |
| Rain/sun inside | floor room ID 0 (limbo), room flag 4 missing | room IDs, flag 4 |
| Works on Legacy, not Enhanced | Gen8 drawables in `stream_enhanced/`, or ymap/ytyp/ybn not copied there | convert, copy all |
| `ERR_GFX_*` crash on approach | >128 materials/geometries per drawable (Gen9), bad `script_rt_` texture | split drawable, fix texture |

## Checklist: CodeWalker to tested MLO

- [ ] Footprint inventory done: HD/LOD/SLOD entities, `hei_` ymap twins, decals/overlays, `.ybn` + `hi@.ybn`, occluders.
- [ ] New prefixed names; exterior pivot = vanilla pivot; vanilla drawables untouched.
- [ ] Inner shell normals face inward; `Color 1` (Face Corner, Byte Color) and `UVMap 0` on every mesh.
- [ ] Drawable ≤ 128 materials/geometries (Gen9), textures power of two DDS ≤ 2048.
- [ ] Composite name = MLO archetype name; BVH has flag preset; floor materials have room IDs; ybn MLO-local.
- [ ] `limbo` first, ≤ 12 limbo entities; each room bounds cover its geometry; every entity in a room.
- [ ] Exit portals room→limbo, arrows consistent; MLO instance `numExitPortals` = exit portal count.
- [ ] Room timecycles set; flags chosen (96 / 111); lights have intensity > 0 and time flags.
- [ ] Vanilla HD ymap copy (+ `hei_`) has the archetype swap; occluders in the footprint removed; extents untouched.
- [ ] ymap flags/extents recalculated (CodeWalker), `_manifest.ymf` generated with ymap + ytyp in the project.
- [ ] `stream/` and `stream_enhanced/` complete; no name clashes (`fivem_conflicttool` or server log).
- [ ] In game after a full reconnect: walk in/out, first person, stairs, jump, every room, day + night, rain, `/mloinfo`.

## References

| File | Read when |
|---|---|
| [references/pipeline.md](references/pipeline.md) | doing steps 1–4 and 10: finding, exporting, importing, exterior swap, LOD chain, occluders |
| [references/mlo-rooms-portals.md](references/mlo-rooms-portals.md) | building the ytyp: rooms, portals, flags, entity sets, timecycles, MLO instance fields |
| [references/collision-lighting.md](references/collision-lighting.md) | making the `.ybn`, stairs, room IDs, navmesh; lights, vertex colours, timecycles |
| [references/export-streaming.md](references/export-streaming.md) | exporting from Sollumz, CodeWalker import, resource layout, Gen9/Enhanced, in-game tests |
| [references/blender-automation.md](references/blender-automation.md) | scripting Blender/Sollumz (bpy snippets, operator ids, MCP servers) |
| [references/common-issues.md](references/common-issues.md) | any bug: full symptom → cause → fix table |
| [references/external-tools.md](references/external-tools.md) | choosing tools, MCPs, other skills; Unreal → GTA question |
| [references/sources.md](references/sources.md) | checking where a fact comes from |
