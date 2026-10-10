# MLO common issues: symptom → cause → fix

Versions: Sollumz 2.9.0, CodeWalker 30 Dev48+, FiveM Legacy and FiveM for GTAV Enhanced (early access since
2026-07-21). Add new rows here when the owner reports a solved bug (exact symptom, cause, fix, version).
Door, garage door and glass specifics: skill `fivem-mlo-doors-windows` (its `common-issues.md`).

## Loading / visibility

| Symptom | Cause | Fix |
|---|---|---|
| MLO shows in CodeWalker, nothing in game | no `_manifest.ymf`, or generated without the ytyp/ymap in the CodeWalker project | add ytyp + ymaps to the project, Tools → Manifest Generator, save into `stream/` |
| Nothing in game, manifest present | `this_is_a_map 'yes'` missing; resource not ensured; files in a second copy of the resource (FiveM ignores one) | fix manifest; check server log for "Started resource" and duplicates |
| Whole resource seems dead, no errors | a broken stream asset can drop the resource silently (muto-atlas) | test with a copy without `stream/`; bisect the files |
| Interior invisible from outside, visible once inside | no exit portal, portal flipped or smaller than the opening, glass/door not attached to the portal | fix portal (corners CCW from outside, arrow outward), attach entities |
| Interior invisible from some angles only, flickers through the door | vanilla box/model occluder in the footprint | delete/shrink occluders in your copy of that vanilla ymap |
| Exterior (world) disappears when you step in | no exit portal to `limbo`, portal one-way, room flag 256 Dont Render Exterior | add/fix exit portal, clear 256 and flag 1 |
| MLO disappears in first person but not third | wrong Room ID on floor collision, or portals assigned to wrong rooms (Sollumz FAQ) | name rooms clearly, fix Room IDs |
| Interior culls on stairs, mezzanine, tall furniture, or when jumping | 4-unit downward probe finds room-ID-0 or non-interior collision | Room IDs on every walkable surface; `SetInteriorProbeLength(x)` for tall rooms |
| Neighbour room invisible through an inner doorway | missing room↔room portal | add internal portal |
| Some props invisible inside | entity not attached to a room/portal; prop placed via a normal ymap inside the MLO (culled) | attach in the MLO entity list |
| More than 12 entities in limbo | game limit (Sollumz 2.9.0 refuses; 2.9.0-dev warns on export) | move them into rooms |
| Interior rotated wrong, exterior right | MLO instance quaternion inverted in hand-written ymap | MLO instance rotation is stored un-inverted |
| Interior offset from the building | MLO origin ≠ composite origin, or room bounds typed in world space | keep drawables + composite at one origin; bounds relative to the composite |
| MLO pops in late / vanishes at distance with the exterior | exterior in limbo (option B) streams with the interior | archetype swap (option A) or larger instance `lodDist` + LOD entity |
| `numExitPortals` wrong | CodeWalker does not compute it | set it to the number of portals touching limbo |

## Vanilla building / LOD

| Symptom | Cause | Fix |
|---|---|---|
| Facade flickers / z-fights, double geometry | vanilla HD entity still drawn under your exterior | archetype swap in the vanilla HD ymap copy |
| Fixed up close, old building from afar | `hei_` twin ymap not patched, or LOD/SLOD model still closed | patch `hei_` copy; edit LOD model only if the silhouette changed |
| Several neighbouring buildings vanish/flicker after the edit | vanilla entity deleted → LOD chain indices shifted | restore; swap archetype or move `z -= 600` instead of deleting |
| Collision missing across the map | ymap `streamingExtents`/`entitiesExtents` enlarged (muto-atlas measured) | never enlarge vanilla extents |
| Decals/graffiti float in the new opening | overlay/decal entities in the footprint | hide them as well (match by position, not name) |
| Other map resource breaks yours (or vice versa) | both stream the same vanilla ymap/ybn | merge into one file (`fivem_conflicttool` merge) |
| Old interior/props of a vanilla MLO at the spot | vanilla interior still active | `DisableInterior` + `UnpinInterior` client-side, or choose another building |

## Collision

| Symptom | Cause | Fix |
|---|---|---|
| Fall through the floor inside | `.ybn` name ≠ MLO name, or not under `Interiors` in the manifest | rename to MLO name, regenerate manifest |
| Collision exists but far away / at the wrong spot | interior ybn exported in world coords (composite not at MLO origin) | keep composite at MLO origin, re-export |
| Collision does nothing at all | no flag preset on the GeometryBVH (pre-2.9 or hand-made BVH) | apply "General (Default)" |
| Cannot walk through the doorway | vanilla exterior `.ybn`/`hi@.ybn` still closed | cut both, stream copies |
| Stuck on stairs, camera shakes | stepped collision only | add a ramp ("Stair plane") or replace steps by a ramp |
| Wrong footstep sound / bullet decals | collision material DEFAULT or wrong type | assign CONCRETE/WOOD/... per surface |
| Rain falls inside | standing on Room ID 0, or vanilla ytyp particle extensions (Sollumz FAQ: edit the vanilla exterior ytyp extensions) | fix Room IDs; remove particle extensions |
| Export error "empty collision geometry" | composite with no polys (Sollumz 2.9-dev reports it, #1244) | add geometry or delete the bound |
| NPCs walk into walls / can't enter | no navmesh for the interior | accept for players; or `rage-cli navmesh build` (verify) |

## Lighting / look

| Symptom | Cause | Fix |
|---|---|---|
| Pitch black inside | no `Color 1` / G = 0; all entities in limbo; no room timecycle | paint G; attach to rooms; set timecycle |
| Dark at night only | lights: time flags 0 or night-off, intensity ~0.02 (Sollumz "Default" preset) | time flags 16777215, intensity 0.5–8 |
| All lights in one spot | lights were hidden at export (muto-atlas) | unhide; disable with intensity 0 |
| Intensity tiny after scripting | wrote `energy` instead of `intensity` (energy = intensity × 500) | set `light_properties.intensity` |
| Glows pink/red at night | unpainted vertex colours (Sollumz FAQ) | paint vertex colours |
| Sun/shadow dots inside | room flag 4 missing | add 4 (and 8) |
| Looks wet / reflective / too bright | R ≠ 0 on interior faces (sky ambient), wrong timecycle | R = 0; vanilla-like timecycle |
| Black patches | inverted normals; `trees_normal` shader inside (muto-atlas) | recalc normals; `normal.sps` family |
| Purple/pink textures in game | texture not embedded and no `.ytd`/wrong `textureDictionary`; PNG instead of DDS | embed or ship the ytd, set archetype txd; DDS power of two |
| Model invisible in CodeWalker | UV/colour layer names not `UVMap 0` / `Color 1` | rename (Sollumz warns) |
| Low-res/blurry textures | missing mipmaps, or HD txd distance | DDS with mips; `hdTextureDist` |

## Export / Sollumz / Blender

| Symptom | Cause | Fix |
|---|---|---|
| `No Sollumz objects selected for export!` | Limit to Selected on and nothing selected/visible; object has no Sollumz type | select roots, unhide; Convert to Drawable/Composite |
| `model name has no Sollumz materials! Aborting...` | Principled BSDF material left, or no shader/texture on the model | Create Shader Material; or `sz_lods.high.mesh` unset on script-made meshes |
| Script export writes only the `.ytyp` | export reads the real view-layer selection, not `temp_override` | `obj.select_set(True)` |
| Script export ignores your format/version | `use_custom_settings` not set → user prefs used | `use_custom_settings=True` |
| "Native" missing in the export dialog | PyMateria not installed (Windows only) | install from Sollumz prefs, or export CW XML + CodeWalker |
| Import of XML does nothing | "Import To Asset Library" used (separate button since 2.9) | normal Import |
| Import error | outdated Sollumz (9/10 cases, Sollumz FAQ) | update |
| `RuntimeError: ... Selection not supported in object mode` (`mesh.separate` in a script) | operator needs a real Edit Mode context | bmesh split ([blender-automation.md](blender-automation.md)) |
| `TypeError: bpy_struct: item.attr = val: enum "FAST" not found in ('FLOAT', 'EXACT', 'MANIFOLD')` (Blender 5.2) | Boolean solver `FAST` renamed `FLOAT` in 5.x (4.5 still has `FAST`) | use `EXACT` (valid in both) |
| Vertex count doubled/tripled after export | face corners vs vertices (Sollumz FAQ) | normal; judge by faces |

## Enhanced (Gen9)

| Symptom | Cause | Fix |
|---|---|---|
| Works on Legacy, nothing on Enhanced | Gen8 drawables in `stream_enhanced/`, or ytyp/ymap/ybn/manifest not copied there | convert (Sollumz Gen9 / Alchemist / CodeWalker), copy everything |
| Crash on approach (`ERR_GFX_*`) | >128 materials/geometries per drawable (reported) | split the shell per room |
| `ERR_GFX_STATE` | `script_rt_*` texture compressed (reported) | A8R8G8B8, no mips |
| Interior OK, door/glass missing on Enhanced | door/glass `.ydr` not converted | see `fivem-mlo-doors-windows` |
| Client freezes at 100 % with `data_file` mounts | server b157 regression (rfc #567) | b156 (see `fivem-gta5-enhanced`) |
