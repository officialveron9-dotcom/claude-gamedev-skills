# Common issues: symptom → cause → fix

Read when a door, garage door or window misbehaves in game. Tags: "(verify)" = inferred or community-reported, not
confirmed in a primary source. Versions are given where they matter. Add new solved bugs as rows (repo rule).

## Doors

| Symptom | Cause | Fix |
|---|---|---|
| Door does not move at all, not even when pushed | Leaf is part of the shell drawable, archetype flag Static (32), or no door special attribute | Separate `.ydr` + archetype with Special Attribute 7 + Dynamic + Enable Door Physics ([doors.md](doors.md)) |
| Door falls over, rolls away or flies off when touched | Dynamic without Enable Door Physics or without a special attribute: a loose physics prop | Set both. Sollumz wiki: Enable Door Physics does nothing without a special attribute |
| Door rotates around its middle or the wrong edge | Origin not at the hinge | Origin to the hinge (Cfx Part 8 steps), re-export, re-read coords in game |
| Door swings up/sideways, or on the wrong axis | Mesh not aligned to the template's local axes | Align to the vanilla template before Convert to Drawable; apply transforms |
| Door swings into the wall / 180° | No limit on the swing | MLO entity Door extension: `enableLimitAngle` + `limitAngle` (radians; vanilla 1.117) |
| Door jitters, sticks or launches on spawn | Leaf bound intersects the frame/floor collision in the closed pose | Leave a gap of mm to 1-2 cm; shrink the leaf box bound (verify per model) |
| Door invisible from one side | Single-sided mesh or flipped normals | Closed mesh with outward normals, or the Double-sided rendering flag (65536) |
| Door visible but no collision | No embedded bound in the `.ydr`, or collision edited without a new Bound Composite | Keep or rebuild the Bound Composite (Cfx docs step 8) |
| Can't walk through the open doorway | Shell collision still spans the opening, or a static copy of the door remains in the shell | Cut the collision; delete the duplicate |
| Door dark or black inside the MLO | No vertex colours | Paint `Color 1` green for interior (Cfx Part 3, Sollumz FAQ) |
| Door vanishes or flickers when seen from inside | Door placed in a ymap (exterior entity) inside the MLO doorway; or not attached to the portal | Make it an MLO entity attached to the doorway portal (vanilla v_int_66) (verify the ymap case) |
| Lock does nothing / `/doorlock` can't select the door | Not an object (type 3) or not a door archetype; model not streamed (`IsModelValid` false) | Fix the archetype; check `IsModelInCdimage(model)`; check the `stream/` path |
| Lock works on a vanilla door but not the custom one | Coords in the script are Blender-local, or more than 0.5-1.0 m off; wrong model hash | Read coords in game (`GetEntityCoords`, ox `/doorlock`); hash the archetype name |
| Door stays ajar after locking | Something (a ped, a prop, or the frame collision) blocks it. The engine closes a door first and only then locks it (Cfx forum guide) | Clear the swing path and the frame gap; register with state 4 first (ox/qb pattern); ox_doorlock waits for `IsDoorClosed` |
| Door randomly flips between locked and unlocked | Two resources register the same door under different hashes | One owner per door; check `DoorSystemFindExistingDoor` |
| `attempt to call a nil value (global 'AddDoorToSystem')` | Door native called in a server script | Door natives are client-only; the server only stores the state |
| Double door: one leaf stays locked | Only one hash set, or a leaf has wrong coords | Two hashes, same state; check each leaf's coords |
| Left leaf mirrored with negative scale looks broken or has no collision | Negative entity scale | Separate L/R models, or a 180° rotation (vanilla `v_ilev_247door`/`_r`) |

## Sync and scripting

| Symptom | Cause | Fix |
|---|---|---|
| Door locked/open for one player only | State applied only on the triggering client (local `DoorSystemSetDoorState`) | Server state → GlobalState / `TriggerClientEvent(-1)` → every client applies it |
| Late joiner or player arriving from far away sees the wrong state | Doors are not networked (citizenfx/fivem #2563); no state sent on registration | Read `GlobalState` on register; ox_doorlock sends all doors via callback on start |
| Shot-open/pushed door looks closed to others | Swing physics is per client, not synced (#2563) | Expected. Script only lock/open targets |
| Client writes `GlobalState` / `LocalPlayer.state` and nothing happens | `sv_stateBagStrictMode true` | Write state on the server (that is the point) |
| Cheater opens police doors from across the map | ox_doorlock 1.22.1 `setState` has no distance check; qb-doorlock trusts `unlockAnyway`/`sentSource` (4a8e911) | Own server checks (distance, job, cooldown); patch qb-doorlock ([door-scripting.md](door-scripting.md)) |
| ox_doorlock hook returning `false` does not block | Hook can only grant in 1.22.1 (`authorised or hookResult == nil or hookResult`) | Restrict through groups/items, or wrap the event |
| ox_doorlock `createDoor` creates duplicates on every restart | Export INSERTs every call | Guard with `getDoorFromName` |
| ox_doorlock: `attempt to compare number with nil` near door | `maxDistance` missing (created via export) | Always pass `maxDistance` |
| ox_doorlock lock sound silent | Native audio (`Config.NativeAudio = true`) expects `door_bolt`, `button_remote`, `metal_locker`, `metallic_creak`; dashed names are NUI files | Match the names to the audio mode |

## Garage doors

| Symptom | Cause | Fix |
|---|---|---|
| Opens only for the player who pressed the button | Ratio/state set locally | Server state; apply on all clients ([garage-doors.md](garage-doors.md)) |
| Snaps back shut after opening | Unlocked automatic door closes when nobody is in range; automatic distance lost | Lock at ratio 1.0 (verify) or `holdOpen`; re-apply the distance every ~100 ms in range (cfx-anes-gates) |
| Opens and closes endlessly | `DoorSystemSetOpenRatio` on an **unlocked** door (forum report) | Set the ratio, then state 1 |
| Opens for any car that drives up | Unlocked automatic door with distance > 0 (qb `garage` type uses 30.0) | Autolock, or the toggle pattern |
| Visually open, but the car hits an invisible wall | Shell collision across the opening, or a static duplicate | Cut the collision; remove the duplicate |
| Panel sticks halfway / jitters at the top | Door bound hits lintel/ceiling collision while moving | Clear the space the panel moves into |
| Moves on the wrong axis | Wrong special attribute or origin | 5 = vertical, bottom center; 8 = sliding, bottom corner |
| Speed differs between Legacy and Enhanced | Enhanced 2026-08-04: door speed frame-rate independent; Legacy depends on FPS | Tune `doorRate`/rate on both |
| Barrier/gate ignores the automatic distance | Rate below 1.5, or the distance is lost on first set (cfx-anes-gates notes) | Rate ≥ 1.5; refresh distance and rate |
| Driver can't toggle from the car | `maxDistance` too small; E key in vehicles (verify) | `maxDistance` 5-15, or a remote key mapping |

## Windows, glass, portals

| Symptom | Cause | Fix |
|---|---|---|
| Glass opaque (solid colour) | Non-glass shader (opaque bucket), or texture without alpha (BC1/DXT1) | `glass*` shader; BC3/DXT5 with alpha < 255 |
| Glass invisible | Alpha 0 everywhere; single face seen from the back; entity lodDist too small; glass outside the portal area | Alpha 20-90; two faces or Double-sided; raise lodDist; enlarge the portal |
| Glass black or very dark | No vertex colours, or the room is too dark through the portal | Paint vertex colours; check room timecycle and lights |
| Glass flickers | Two coplanar faces (z-fight), or glass coplanar with the portal or shell | Offset faces by a few mm; glass about 7 cm from the portal plane (vanilla) |
| Glass sorts wrongly (objects behind it vanish or pop in front) | Glass inside the shell drawable; glass behind glass | Separate glass entity; Draw Last (4); Disable alpha sorting (64) |
| Can't see outside from inside (sky or black behind the glass) | No `room -> limbo` portal over the window; room flag Dont Render Exterior (256) | Add the portal; clear flag 256 |
| Exterior disappears when looking through a window from a back room | Exterior only through chained portals; depth limited | Keep `exteriorVisibiltyDepth = -1`; add portals between rooms (verify) |
| From outside the window shows void / the street behind the building | Portal missing or facing inward; One-Way set; MLO not loaded at that distance | Portal room → limbo with the arrow outward; no One-Way; check the MLO ymap/entity lodDist |
| Interior visible from outside but glass missing | Glass attached to the room, not the portal; single face | Attach it to the window portal (vanilla); two faces |
| Exterior tinted by the interior timecycle when looking out | Room timecycle applies through the portal | Portal flag 8 Disable Timecycle Modifier (vanilla windows) (verify effect) |
| MLO disappears in first person but not in third | Wrong Room ID in the floor collision, or portals assigned wrongly (Sollumz FAQ) | Fix collision Room IDs; name rooms clearly |
| Interior lights not visible from outside at night | Room not rendered (out of range, or no portal in view); light flag Interior Only | Portal over the windows; `Both Interior and Exterior` light flag; `glass_emissivenight` / Time-archetype emissives + baked LOD lights for distance |
| Peds/bullets pass through the window | No glass collision in the opening | Thin box bound with `GLASS_BULLETPROOF` (or `GLASS_SHOOT_THROUGH` if intended) |
| Breakable glass does not export or break | Mesh not 2 parallel planes × 2 triangles, no collision on the bone, Breakable Glass off, archetype not Dynamic, or the Sollumz build lacks the feature | Follow the Sollumz export warnings ([windows-glass-portals.md](windows-glass-portals.md)) |
| Crash or pool error with many window portals | Interior/portal pools full (verify which) | `increase_pool_size` PortalInst/OcclusionPortalInfo/Entity within Cfx limits; merge window portals |

## Enhanced (Gen9)

| Symptom | Cause | Fix |
|---|---|---|
| Door/glass model invisible on Enhanced only | Gen8 `.ydr/.yft` streamed | Alchemist or Sollumz target Gen9 → `stream_enhanced/` |
| Crash near the MLO when a script searches for door objects | `GetClosestObjectOfType`/`GetGamePool('CObject')` near MLOs crashed before 2026-08-04 | Update the client/server; the fix shipped in the 2026-08-04 patch |
| Shell with many glass materials crashes | More than 128 materials/geometries per drawable (Gen9) | Split the shell; keep glass as separate entities |
