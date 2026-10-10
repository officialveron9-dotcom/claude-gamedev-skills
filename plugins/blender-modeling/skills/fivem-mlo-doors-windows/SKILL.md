---
name: fivem-mlo-doors-windows
description: Builds working doors, double/garage doors and see-through windows for FiveM MLOs from scratch in Blender + Sollumz (Legacy and Enhanced) - tested bpy generators (hinge pivot, frame, wall opening with reveal, glass, bounds, LODs), door archetypes (Normal/Garage/Sliding Door attribute, Dynamic + Enable Door Physics), portal-attached entities, door system natives (AddDoorToSystem, DoorSystemSetDoorState/OpenRatio/AutomaticRate), ox_doorlock, server-side state sync, glass shaders, room-to-limbo portals. Use for MLO door, garage door, ox_doorlock, glass shader, window portal, Sollumz door, or German "Tür", "Garagentor", "Fenster", "Glas", "Tür geht nicht auf", "durchs Fenster schauen", "Türschloss".
---

# MLO doors, garage doors and windows (state 2026-10)

Scope: functional doors and glass inside a custom MLO built with Blender + Sollumz (+ CodeWalker), on FiveM Legacy
and FiveM for GTAV Enhanced. **Default: Claude builds every door, double door, garage door and window from scratch**
with the tested generators in [references/procedural-modeling.md](references/procedural-modeling.md). Vanilla props
are **reference only**, for dimensions, flags, special attribute and behaviour. Only GTA's systems are reused: archetype
attributes/flags, door physics, the door system/ox_doorlock, glass shaders and portals.
Related skills (link by name): `fivem-mlo-creation` covers the shell, rooms/portals in general, collision and export. `gta-texture-editing` covers painting out doors and windows that are baked into textures.
`fivem-security` covers server event validation, and `fivem-frameworks` covers job checks and ox_lib.

## Non-negotiables

1. **A door that moves is its own archetype, never part of the shell.** Give it its own `.ydr` (custom mesh,
   embedded box bound; the official Cfx path keeps a vanilla template's armature/bone) and a ytyp archetype with a
   door **special attribute** plus the flags **Dynamic** and **Enable Door Physics**. "Enable Door Physics" does
   nothing without the special attribute.
2. **The origin is the pivot.** Swing door: on the hinge axis at mid-height (vanilla door entities sit at half the
   leaf height). Sliding door/gate: bottom corner. Vertical garage door: bottom center. The generators build the
   leaf along local −X with Z up, like the vanilla 24/7 layout. Compare once with the template's bounding box (verify).
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

| Need | Build (generator) | Reference only (Cfx template) | ytyp Special Attribute | Origin | Driven by |
|---|---|---|---|---|---|
| Swinging door | `make_door` | `v_ilev_bl_door_l` | Normal Door (7) | hinge axis, mid-height | lock state 0/1 |
| Double door | `make_double_door` (`_l` Y-mirrored and rotated 180°, `_r`) | `v_ilev_247door`/`_r` | 7 each | each hinge | two door hashes, same state |
| Sliding door / gate | `make_sliding_door` (origin bottom corner) | `prop_facgate_07b` | Sliding Door (8) | bottom corner | automatic distance/rate, lock |
| Vertical garage door | `make_garage_door` (sectional/roller, one rigid mesh) | `lr_prop_supermod_door_01` | Garage Door (5) | bottom center | open ratio + lock, or automatic |
| Barrier arm, vertical slider, rail barrier | custom | vanilla props | 9, 10, 12 (verify) | copy reference | as above |
| Fixed window | `make_window` (frame + separate glass drawable) | - | none (0) | opening centre | nothing |
| Breakable window | `.yft` fragment, bone "Breakable Glass" | - | none, archetype Dynamic | any | physics |
| Wall hole + reveal | `make_wall_with_opening(*part["wall_opening"])` | - | shell | - | - |

Vanilla props are references: in CodeWalker, read their size, `.ytyp` Special Attribute and flags, then build your own.
Look-alikes exist (`prop_sec_barier_02a` is not a door, `prop_sec_barrier_ld_02a` is). Details:
[references/doors.md](references/doors.md), [references/procedural-modeling.md](references/procedural-modeling.md).

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

## 3. Custom door into the MLO (generator + Sollumz)

1. Generate it: `d = make_door("vx_shop_door_01", open_w=0.95, open_h=2.1)` (or `make_double_door`,
   `make_garage_door`, `make_window`). The pivot sits on the hinge axis at mid-height and the leaf points along local
   −X. A hinge barrel and the bound ending at the axis give 3 mm gaps and a full ±90° swing without touching the jamb.
2. Cut the shell to `d["wall_opening"]` (`make_wall_with_opening` or your shell), so the frame lines the reveal.
3. Move the **Drawable empty** into place. With Sollumz loaded, run `sz_convert(d)` (types, LODs, shaders, collision
   material) and `sz_add_archetype(d["drawable"], "IS_NORMAL_DOOR")` (Special Attribute 7, Dynamic, Enable Door
   Physics). Copy the bound flags from the template. Official skeleton path: `attach_to_template_bone`
   (template mesh deleted).
4. MLO archetype: add the door as an **entity**, set **Attached Portal** to the doorway portal, and add a **Door
   extension** (`enableLimitAngle`, `limitAngle` in radians; vanilla uses 1.117 = 64°).
5. Export with **Apply Parent Transforms OFF**, or rotated leaves get their rotation baked. Put `.ydr`/`.ytd` in
   `stream/` (Gen8) and `stream_enhanced/` (Gen9), and the same `.ytyp`/`.ymap` in **both** (Enhanced ignores `stream/`
   once `stream_enhanced/` exists).

Manual (non-scripted) steps, frames, double doors, wrong vs right: [references/doors.md](references/doors.md).

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
| Door spins around its middle | Origin not at the hinge | Generator pivot (hinge axis, mid-height); re-export; re-read coords |
| Door swings into the wall / stops when open | Hinge axis on the jamb plane, or the bound extends past the axis | Inset the axis by `gap + t/2`, hinge barrel, bound ends at the axis (`make_door`) |
| Visible gaps or rubbing between door and frame | Leaf sized to the opening without gaps, or opening ≠ frame | `wall_opening` from the generator; 3 mm gaps, 10 mm floor |
| Glass flickers at the frame | Glass face coplanar with frame or wall faces | Glass 6 mm double face, 1 cm into the frame, never on a frame plane |
| Lock script does nothing | Coords are Blender-local or off by more than 0.5-1 m, or wrong model hash | `/doorlock` target or `GetEntityCoords` in game |
| Locked for one player only | State set locally with no broadcast; late joiners get no state | GlobalState / ox_doorlock; apply on join |
| Garage door snaps back / pumps | Unlocked + open ratio, or automatic distance lost | Lock at the ratio, or hold open; re-apply the distance |
| Glass opaque or black | Not a glass shader, texture without alpha, no vertex colour | glass shader, BC3 with alpha, paint vertex colours |
| Can't see outside from inside | No `room -> limbo` portal, or Dont Render Exterior | Add the portal, clear room flag 256 |
| Interior missing from outside | Portal missing or flipped, glass not on the portal, or entity lodDist too low | Fix the portal direction, attach the glass, raise lodDist |

All rows with versions: [references/common-issues.md](references/common-issues.md).

## 10. Checklists

**Per door**
- [ ] Built with `make_door`/`make_double_door` (vanilla only as reference). Pivot on the hinge axis at mid-height,
      leaf along −X, 3 mm gaps, bound ending at the axis, names `<prefix>_<mlo>_door_<nn>` without `.001`.
- [ ] Sollumz: Drawable > model + composite > box bound, collision material, LOD, shader slots converted; template
      armature + Copy Transforms (official path); Apply Parent Transforms OFF.
- [ ] ytyp: Special Attribute (7/8/5), Dynamic, Enable Door Physics, not Static, name = file name.
- [ ] Opening cut in shell mesh and collision. Portal over the doorway. Door entity attached to that portal.
- [ ] Door extension with a limit angle if needed. Double doors use two entities and two hashes.
- [ ] World coords and model hash checked in game. Server holds the state; every client applies it, including late joiners.

**Per garage door**
- [ ] `make_garage_door` (one rigid mesh, grooves only) or `make_sliding_door`; attribute 5 or 8; origin bottom
      center/corner; mounted on the interior face; clear space where the panel moves; vehicle-sized portal and opening.
- [ ] Shell collision removed from the opening. Rate and distance tuned on both platforms.
- [ ] Open/close via server event (job, distance, PIN or item checked server-side), synced to all clients.

**Per window**
- [ ] `make_window` + `make_wall_with_opening(*win["wall_opening"])`: hole with reveal, frame/mullions static, separate
      glass drawable (2 faces, not coplanar), `sz_glass.*` slot → glass shader, alpha texture, vertex colours.
- [ ] `room -> limbo` portal over the glass, arrow outward, glass attached to it, not One-Way, room flag 256 off.
- [ ] Glass collision material `GLASS_*`. If it must break: a `.yft` with a Breakable Glass bone.
- [ ] Checked from inside and outside, by day and at night.

## References

- [references/procedural-modeling.md](references/procedural-modeling.md): read **first** when building any door,
  garage door, window or wall opening. It has the tested bpy generators, conventions, Sollumz API and test harness.
- [references/doors.md](references/doors.md): read when building or placing a swinging/double/sliding door.
- [references/garage-doors.md](references/garage-doors.md): read for garage, roller, sliding gate or barrier doors.
- [references/windows-glass-portals.md](references/windows-glass-portals.md): read for glass, shaders, portals, lights.
- [references/door-scripting.md](references/door-scripting.md): read when writing Lua or configuring ox/qb doorlock.
- [references/common-issues.md](references/common-issues.md): read when something is broken in game.
- [references/sources.md](references/sources.md): read to check where a fact comes from.
