---
name: fivem-mlo-doors-windows
description: Builds working doors, garage doors and see-through glass windows for FiveM MLOs made with Blender + Sollumz (Legacy and Enhanced) - door archetypes (Normal/Garage/Sliding Door special attribute, Dynamic + Enable Door Physics, hinge origin, door extension), portal-attached door/glass entities, door system natives (AddDoorToSystem, DoorSystemSetDoorState/OpenRatio/AutomaticRate/HoldOpen), ox_doorlock/qb-doorlock, server-side state sync, glass shaders, room-to-limbo window portals. Use for MLO door, garage door, door system, ox_doorlock, glass shader, window portal, Sollumz door or fragment, or German "Tür", "Garagentor", "Fenster", "Glas", "Tür geht nicht auf", "durchs Fenster schauen", "Türschloss".
---

# MLO doors, garage doors and windows (state 2026-10)

Scope: functional doors and glass inside a custom MLO built with Blender + Sollumz (+ CodeWalker), on FiveM Legacy
and FiveM for GTAV Enhanced. Related skills (link by name): `fivem-mlo-creation` covers the shell, rooms/portals in
general, collision and export. `gta-texture-editing` covers painting out doors and windows that are baked into textures.
`fivem-security` covers server event validation, and `fivem-frameworks` covers job checks and ox_lib.

## Non-negotiables

1. **A door that moves is its own archetype, never part of the shell.** Give it its own `.ydr` (embedded collision and
   a one-bone skeleton copied from a vanilla template) and a ytyp archetype with a door **special attribute** plus the
   flags **Dynamic** and **Enable Door Physics**. "Enable Door Physics" does nothing without the special attribute.
2. **The origin is the pivot.** Swing door: hinge (side center). Sliding door/gate: bottom corner. Vertical garage
   door: bottom center. Align the mesh to the vanilla template so the local axes match.
3. **Cut the opening.** Remove the door/window opening from both the shell mesh and the shell collision. Put a
   **portal** (`room -> limbo` for outside openings) over it, and **attach the door/glass entity to that portal**, as
   vanilla does (verified in `v_int_66`, the 24/7 shop).
4. **Map and MLO doors are not networked.** Every client has its own copy, and swinging is simulated locally. Keep
   lock/open state on the server (a GlobalState key or an ox_doorlock DB row) and apply it on every client with
   `AddDoorToSystem(hash, model, x, y, z, false, false, false)` plus the door system setters. Door natives are
   client-only.
5. **A window is three parts:** a hole in shell and collision, a separate glass entity with a `glass*` shader
   (alpha bucket) and texture alpha below 255, and a `room -> limbo` portal covering the glass. Without the portal you
   cannot see out from inside, and from outside the interior is not drawn.
6. Door coordinates for scripts are **world** coords of the door **object** in its closed pose. Read them in game
   (ox_doorlock `/doorlock`, `GetEntityCoords`), not from Blender (MLO-local).

## 1. What to build

| Need | Asset (official Cfx template) | ytyp Special Attribute | Origin | Driven by |
|---|---|---|---|---|
| Swinging door | `.ydr` (`v_ilev_bl_door_l`) | Normal Door (7) | hinge, side center | lock state 0/1 |
| Double door | two entities (separate L/R models, or one model rotated 180°) | 7 each | each hinge | two door hashes, same state |
| Sliding door / gate | `.ydr` (`prop_facgate_07b`) | Sliding Door (8) | bottom corner | automatic distance/rate, lock |
| Vertical garage door | `.ydr` (`lr_prop_supermod_door_01`) | Garage Door (5) | bottom center | open ratio + lock, or automatic |
| Vertical slider, barrier arm, rail barrier | `.ydr` | Sliding Vertical Door (10), Barrier Door (9), Rail Crossing (12) (verify) | copy a vanilla prop | as above |
| Fixed window | glass `.ydr` entity on the portal | none (0) | any | nothing |
| Breakable window | `.yft` fragment, bone "Breakable Glass" | none, archetype Dynamic | any | physics |

The fastest option is a vanilla door prop. In CodeWalker, open the RPF Explorer, search `door`/`gate`, open the
prop's `.ytyp` and check the Special Attribute. Look-alikes that are not doors exist: `prop_sec_barier_02a` is not a
door, `prop_sec_barrier_ld_02a` is. Details and a model list: [references/doors.md](references/doors.md).

## 2. Flag values (CodeWalker = Sollumz names)

| Archetype flag | Value | Use |
|---|---|---|
| Dynamic | 131072 | required on doors (official Cfx doc) |
| Enable Door Physics | 67108864 | required on doors; needs a special attribute |
| Static | 32 | never on a door (freezes it) |
| Draw Last | 4 | glass: drawn after opaque geometry, so it blends over what is behind it |
| Disable alpha sorting | 64 | try it together with Draw Last on overlapping glass |
| Double-sided rendering | 65536 | renders back faces; an alternative to modelling both glass faces |

Portal flags: `1` One-Way, `2` Link Interiors, `4` Mirror, `8` Disable Timecycle Modifier (set on vanilla window
portals), `64` Hide when door closed, `8192` Use Light Bleed (set on the vanilla shop door portal). Room flags: `256`
Dont Render Exterior (must be off in rooms with windows), `8` No Exterior Lights, `4` No Directional Light.
Full tables: [references/windows-glass-portals.md](references/windows-glass-portals.md).

## 3. Door into the MLO (Sollumz)

1. Import the vanilla template `.ydr`. Snap the cursor to your door mesh and set the origin to the hinge
   (`Object > Set Origin > Origin to 3D Cursor`). Align it to the template and apply transforms.
2. Convert to Drawable. Delete the template mesh, then parent your mesh to the template armature/drawable and add a
   **Copy Transforms** constraint (target: armature, bone: the template door bone). If you changed the collision,
   make a new Bound Composite and parent the collision to it, or the in-game collision breaks.
3. ytyp: Base archetype, Asset Type Drawable, name = file name, Special Attribute 7, flags Dynamic + Enable Door Physics.
4. MLO archetype: add the door as an **entity**, set **Attached Portal** to the doorway portal, and add a **Door
   extension** (`enableLimitAngle`, `limitAngle` in radians; vanilla uses 1.117 = 64°).
5. Export `.ydr`/`.ytd` (Gen8 to `stream/`, Gen9 to `stream_enhanced/`). Put the same `.ytyp`/`.ymap` in **both**
   folders, because Enhanced ignores `stream/` once `stream_enhanced/` exists. Leave a few mm between the leaf and
   the frame collision.

More (frames, double doors, separate ymap, wrong vs right): [references/doors.md](references/doors.md).

## 4. Door system natives (client; verified in citizenfx/natives)

| Native (Lua name) | Signature / notes |
|---|---|
| `AddDoorToSystem` | `(doorHash, modelHash, x, y, z, p5, scriptDoor, isLocal)`. Use `false, false, false` (local system; sync it yourself). `scriptDoor=true` has a hard cap |
| `DoorSystemSetDoorState` | `(doorHash, state, requestDoor, forceUpdate)`. 0 unlocked, 1 locked, 2 locked until out of area, 3 force unlocked this frame, 4 force locked this frame, 5 force open this frame, 6 force closed this frame |
| `DoorSystemSetOpenRatio` | `(doorHash, ratio -1.0..1.0, requestDoor, forceUpdate)`. 0 = closed; the sign is the direction |
| `DoorSystemSetAutomaticRate` | `(doorHash, rate, requestDoor, forceUpdate)`: speed of automatic (garage/sliding) doors |
| `DoorSystemSetAutomaticDistance` | `(doorHash, distance, requestDoor, forceUpdate)`: trigger distance for automatic doors |
| `DoorSystemSetHoldOpen` | `(doorHash, toggle)`: keeps the door open while unlocked |
| `IsDoorRegisteredWithSystem`, `DoorSystemFindExistingDoor(x,y,z,model)` | Avoid double registration (FindExisting uses a 0.5 m radius) |
| `DoorSystemGetDoorState`, `DoorSystemGetOpenRatio`, `IsDoorClosed`, `DoorSystemGetIsPhysicsLoaded` | Lock state applies only once physics has loaded. The state set earlier is kept until the door streams in |
| `GetClosestObjectOfType(x,y,z,r,model,false,false,false)` | Finds the door object (ox_doorlock uses r = 1.0) |
| `DoorControl`, `SetStateOfClosestDoorOfType` | Hardcoded not to work in multiplayer. Do not use |

Cfx extras: `DoorSystemGetActive()` returns `{ {hash, handle}, ... }`, and `DoorSystemGetSystemSize()`.

```lua
-- client: register once, snap closed, then apply the server state
local hash = `mlodoor_office_1`
if not IsDoorRegisteredWithSystem(hash) then
    AddDoorToSystem(hash, `my_mlo_door_01`, -551.32, -191.88, 38.22, false, false, false)
end
DoorSystemSetDoorState(hash, 4, false, false)                 -- force-close once (ox/qb doorlock do this)
DoorSystemSetDoorState(hash, GlobalState['mlodoor:office'] or 1, false, false)
```

Full resource (shared config, server authority via GlobalState, keypad, remote, double doors):
[references/door-scripting.md](references/door-scripting.md).

## 5. Locking with ox_doorlock (1.22.1)

Doors live in the MySQL table `ox_doorlock` (JSON `data`), not in a config file. Create them in game with
`/doorlock` (ACE `Config.CommandPrincipal`, default `group.admin`), or on the server with
`exports.ox_doorlock:createDoor{...}`. Fields: `name, model, coords, heading, doors` (double), `state` (1 = locked,
the default), `maxDistance` (must be set when using the export), `auto` (garage/sliding/barrier), `doorRate`, `holdOpen`,
`autolock` (seconds), `groups` (`{ job = minGrade }`), `items`, `characters`, `passcode`, `lockpick`, `hideUi`,
`lockSound`/`unlockSound`. Traps:
- The server checks groups/items/passcode/ACE `doorlock.<name>` but **not the player's distance**. In 1.22.1 a
  `doorAuthorization` hook can grant access but cannot revoke it.
- Server-side `TriggerEvent('ox_doorlock:setState', id, state)` skips authorization. Validate before calling it.
qb-doorlock uses `Config.DoorList` with `doorType = 'door'|'double'|'sliding'|'doublesliding'|'garage'`. Its
server event trusts the client arguments `unlockAnyway` and `sentSource` and has no distance check (commit `4a8e911`),
so patch it before protecting valuables.
Snippets: [references/door-scripting.md](references/door-scripting.md).

## 6. Garage doors (summary)

- The door system animates garage, sliding and barrier types itself. **Unlocked** with an automatic distance > 0, it
  opens when a ped or vehicle comes near and closes when nobody is in range. **Locked**, it closes and stays shut.
  qb-doorlock uses distance 30.0 when unlocked and 0.0 when locked, with rate `doorRate or 1.0`.
- For a keypad or button that opens and closes it, set `DoorSystemSetOpenRatio(h, 1.0)` + state 1 to hold it open and
  ratio 0.0 + state 1 to hold it closed (verify per model). Unlocked + open ratio oscillates (forum report).
  Alternatively use ox_doorlock `auto = true, holdOpen = true`.
- Make the opening vehicle-sized. Put a `room -> limbo` portal over the full opening and attach the garage door to it.
  Remove the shell collision from the opening; the door's own bound blocks it when closed. Set `maxDistance` 5-15 so
  a driver can trigger it.
Details, bug list: [references/garage-doors.md](references/garage-doors.md).

## 7. Windows (summary)

- Glass: a separate entity with **two faces** (each pointing out) a few mm apart, or the Double-sided flag. Never put
  two coplanar faces at the same position. Do not merge glass into the shell drawable, because sorting breaks.
- Shaders (verified in Sollumz/szio `Shaders.xml`, alpha bucket 1): `glass`, `glass_pv`, `glass_pv_env`,
  `glass_env`, `glass_spec`, `glass_reflect`, `glass_normal_spec_reflect`, `glass_breakable`, `glass_emissive`
  (it also has an opaque variant), `glass_emissivenight`, and `glass_displacement` (bucket 7, refraction).
  `decal_glass` **does not exist**. Transparency comes from
  the DiffuseSampler alpha. A BC1/DXT1 texture with no alpha gives opaque glass.
- Portal: `Room From` = the room, `Room To` = limbo (0). The Sollumz arrow points from the room toward limbo, i.e.
  outward. In the vanilla 24/7 shop the corners run counter-clockwise when seen from outside. The portal sits in the
  opening a few cm outside the glass plane (vanilla: 7-9 cm) and covers the whole opening. Do not set One-Way (1) or "Hide when door
  closed" (64) on glass. The same portal serves both directions.
- Night: interior lights are drawn only while the room renders, i.e. through the portal and within streaming range.
  For far views add `glass_emissivenight`/Time-archetype emissive windows and baked LOD lights. To let light reach the
  outside, use the light flag "Both Interior and Exterior".
Details: [references/windows-glass-portals.md](references/windows-glass-portals.md).

## 8. GTA V Enhanced (Gen9)

- `.ydr/.yft/.ytd` (doors, glass, fragments) must be Gen9: run Alchemist or export with the Sollumz target "Gen9"
  (it writes a `gen9/` subfolder), then put them in `stream_enhanced/`. `.ytyp/.ymap` are not converted, so special
  attributes, flags, portals and extensions carry over unchanged. They must still be copied into `stream_enhanced/`.
- The glass shader names are identical on Gen9 (szio `ShadersG9ParamsDefaults.json` lists every `glass_*`).
  Enhanced allows at most 128 materials/geometries per drawable, so keep glass out of huge shells.
- Patch 2026-08-04: door opening speed is now frame-rate independent, so a `doorRate` tuned on Legacy can look
  different. A client crash in `GetClosestObjectOfType`/`GetGamePool('CObject')` near MLOs was fixed in the same patch.
- The door natives and the server-state approach are unchanged. No Enhanced-specific door, portal or glass bug was
  found up to 2026-10-10. RT reflections on glass: unverified.

## 9. Top symptoms

| Symptom | Likely cause | Fix |
|---|---|---|
| Door won't open / is frozen | Door is part of the shell, archetype is Static, or there is no special attribute | Separate entity, attribute 7, Dynamic + Enable Door Physics |
| Door falls over / flies away | Dynamic without a door attribute or Enable Door Physics | Set both; check the bound mass/material |
| Door spins around its middle | Origin not at the hinge | Origin to hinge; re-export; re-read coords |
| Lock script does nothing | Coords are Blender-local or off by more than 0.5-1 m, or wrong model hash | `/doorlock` target or `GetEntityCoords` in game |
| Locked for one player only | State set locally with no broadcast; late joiners get no state | GlobalState / ox_doorlock; apply on join |
| Garage door snaps back / pumps | Unlocked + open ratio, or automatic distance lost | Lock at the ratio, or hold open; re-apply the distance |
| Glass opaque or black | Not a glass shader, texture without alpha, no vertex colour | glass shader, BC3 with alpha, paint vertex colours |
| Can't see outside from inside | No `room -> limbo` portal, or Dont Render Exterior | Add the portal, clear room flag 256 |
| Interior missing from outside | Portal missing or flipped, glass not on the portal, or entity lodDist too low | Fix the portal direction, attach the glass, raise lodDist |

All rows with versions: [references/common-issues.md](references/common-issues.md).

## 10. Checklists

**Per door**
- [ ] Own `.ydr` from the template, origin at the pivot, axes aligned, embedded collision, skeleton bone kept.
- [ ] ytyp: Special Attribute (7/8/5), Dynamic, Enable Door Physics, not Static, name = file name.
- [ ] Opening cut in shell mesh and collision. Portal over the doorway. Door entity attached to that portal.
- [ ] Door extension with a limit angle if needed. Double doors use two entities and two hashes.
- [ ] World coords and model hash checked in game. Server holds the state; every client applies it, including late joiners.

**Per garage door**
- [ ] Attribute 5 (vertical) or 8 (sliding), origin bottom center/corner, vehicle-sized portal and opening.
- [ ] Shell collision removed from the opening. Rate and distance tuned on both platforms.
- [ ] Open/close via server event (job, distance, PIN or item checked server-side), synced to all clients.

**Per window**
- [ ] Hole in shell and collision, separate glass entity, both faces or Double-sided, glass shader, alpha texture, vertex colours.
- [ ] `room -> limbo` portal over the glass, arrow outward, glass attached to it, not One-Way, room flag 256 off.
- [ ] Glass collision material `GLASS_*`. If it must break: a `.yft` with a Breakable Glass bone.
- [ ] Checked from inside and outside, by day and at night.

## References

- [references/doors.md](references/doors.md): read when building or placing a swinging/double/sliding door.
- [references/garage-doors.md](references/garage-doors.md): read for garage, roller, sliding gate or barrier doors.
- [references/windows-glass-portals.md](references/windows-glass-portals.md): read for glass, shaders, portals, lights.
- [references/door-scripting.md](references/door-scripting.md): read when writing Lua or configuring ox/qb doorlock.
- [references/common-issues.md](references/common-issues.md): read when something is broken in game.
- [references/sources.md](references/sources.md): read to check where a fact comes from.
