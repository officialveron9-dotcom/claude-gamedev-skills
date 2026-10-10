# Garage doors, sliding gates, barriers

Read for vehicle doors in an MLO: vertical garage doors, sliding gates, barrier arms, and keypad or remote control.
Modelling basics are in [doors.md](doors.md). The full Lua resource is in [door-scripting.md](door-scripting.md).

## Types

| Special Attribute | Motion | Template / vanilla example | Origin |
|---|---|---|---|
| Garage Door (5) | panel moves up (up-and-over / roller look) | `lr_prop_supermod_door_01` (official template), `prop_com_gar_door_01` | bottom center |
| Sliding Door (8) | slides sideways | `prop_facgate_07b` (official template), `prop_gate_prison_01`, `prop_autodoor` (double) | bottom corner |
| Sliding Vertical Door (10) | slides vertically (verify) | copy a vanilla prop that uses it | verify |
| Barrier Door (9) | barrier arm (verify value) | `prop_sec_barrier_ld_01a` / `_02a` | copy vanilla |
| Rail Crossing Barrier (12) | rail barrier | vanilla rail crossings | copy vanilla |

- Values 5/7/8 and their origins come from the official Cfx door guide. 9/10/12 come from the Sollumz enum and are
  untested here. The vanilla examples besides the official templates come from doorlock configs; their special
  attribute was not checked, so open their `.ytyp` in CodeWalker before relying on the type.
- `prop_sc1_21_g_door_01` appears in community lists as a garage door (verify the name and attribute in CodeWalker).
- A true rolling shutter (segments wrapping onto a drum) is not something the door system does: the Garage Door type
  moves the whole panel. Fake the look with geometry/texture. Real segment animation needs an animated (YCD) object,
  outside the door system (verify).

## How the door system moves automatic doors

- Garage, sliding and barrier types are automatic doors. When **unlocked** with an automatic distance > 0, the game
  opens them when a ped or vehicle comes within that distance and closes them when nobody is in range. When
  **locked** (state 1), they close and stay shut. Semantics inferred from qb-doorlock and cfx-anes-gates code (verify).
- `DoorSystemSetAutomaticRate(h, rate, false, true)` sets the speed. `DoorSystemSetAutomaticDistance(h, dist, false, true)`
  sets the trigger range.
- qb-doorlock `doorType = 'garage'|'sliding'`: unlocked = state 0, rate `doorRate or 1.0`, distance **30.0**. Locked =
  state 1, distance **0.0**.
- cfx-anes-gates (barriers): default distance 1.5 and rate 1.5. Its comment: "rate should be minimum 1.5 or sometimes
  game doesn't recognize the automatic distance", and "some gates lose their automatic distance on first set", so it
  re-applies distance and rate every 100 ms while the gate is in range.
- ox_doorlock: `auto = true` leaves the rate at the game default unless `doorRate` is set (non-auto doors get rate
  10.0). `holdOpen = true` calls `DoorSystemSetHoldOpen(h, state == 0)`.
- **Enhanced** (patch 2026-08-04): door opening speed is now frame-rate independent. Legacy speed varies with FPS, so
  check the rate on both platforms.

## Control patterns

| Pattern | Behaviour | How |
|---|---|---|
| A. Access-controlled automatic | Authorised players unlock it; then it opens for **anyone** who drives up until it is locked again | qb style: state 0 + distance > 0 / state 1 + distance 0; or ox_doorlock `auto = true` |
| B. Toggle (keypad, remote, button) | Opens and stays open until closed | Hold open: `DoorSystemSetOpenRatio(h, 1.0, false, true)` + `DoorSystemSetDoorState(h, 1, false, true)`. Hold closed: ratio 0.0 + state 1 (verify per model) |
| C. Hold open while unlocked | Opens when approached, stays open | ox_doorlock `auto = true, holdOpen = true` |

- A forum report says `DoorSystemSetOpenRatio(h, -1.0, true, true)` on an **unlocked** door makes it open and close
  endlessly. Never set a ratio on an unlocked automatic door.
- If a model ignores pattern B, fall back to pattern A with a short server `autolock` (ox_doorlock `autolock` seconds).

## MLO geometry for garages

- Make the clear opening larger than the largest vehicle that must pass. At ratio 1.0 the panel must fully clear it.
  Check it in game with the biggest vehicle.
- Put a `room -> limbo` portal over the **whole** opening and attach the garage door entity to it. For an opaque door,
  flag 64 "Hide when door closed" may save rendering (verify). Window portals elsewhere stay unflagged.
- Shell collision: leave the opening free. The space the panel moves into (lintel/ceiling for vertical doors, wall
  pocket for sliding ones) must not intersect the door's bound, or the door sticks or jitters.
- The floor collision in the garage needs the correct Room ID, or vehicles and peds inside are treated as exterior and
  flicker or vanish (see `fivem-mlo-creation`).
- Room flags: leave `1` Freeze Vehicles, `16` Force Freeze and `32` Reduce Cars off unless you want them.
- Collision material: `METAL_GARAGE_DOOR` exists in the Sollumz material list.

## ox_doorlock garage door (row as the UI or export stores it)

```lua
-- server, run once (createDoor INSERTs a new row on every call - guard with getDoorFromName)
if not exports.ox_doorlock:getDoorFromName('bennys garage') then
    exports.ox_doorlock:createDoor({
        name = 'bennys garage',
        model = `my_mlo_garage_01`,
        coords = vec3(-205.68, -1310.68, 30.29),   -- world coords of the door object (closed)
        heading = 0,
        state = 1,              -- 1 locked, 0 unlocked
        auto = true,            -- garage/sliding/barrier
        doorRate = 1.0,         -- optional speed
        holdOpen = true,        -- stay open while unlocked
        maxDistance = 8.0,      -- REQUIRED via export (UI defaults to 2)
        groups = { mechanic = 0 },
        lockSound = 'button_remote',   -- native audio names: door_bolt, button_remote, metal_locker, metallic_creak
    })
end
```

Vanilla row for comparison (ox_doorlock `community_mrpd.sql`):
`{"auto":true,"lockSound":"button-remote","groups":{"police":0},"maxDistance":5,"state":1,"model":-190780785,...}`.
The dashed sound names belong to NUI audio (`Config.NativeAudio = false`).

## qb-doorlock garage entry

```lua
Config.DoorList['bennys-garage'] = {
    objName = 'my_mlo_garage_01', objCoords = vec3(-205.68, -1310.68, 30.29),
    textCoords = vec3(-205.68, -1310.68, 31.8),
    doorType = 'garage', doorRate = 1.0,
    authorizedJobs = { ['mechanic'] = 0 },
    locked = true, distance = 10.0,
}
```

## Garage-specific bugs

| Symptom | Cause | Fix |
|---|---|---|
| Opens for one player only | Ratio/state set only on the triggering client | Server state (GlobalState / ox_doorlock); every client applies it |
| Late joiner sees it closed while others see it open | State not applied on registration | Read the state when registering, e.g. `GlobalState['mlodoor:x']` |
| Snaps back shut | Unlocked automatic door with nobody in range; or the automatic distance was lost | Pattern B (lock at ratio) or holdOpen; re-apply the distance (anes-gates trick) |
| Opens and closes endlessly | Open ratio set on an unlocked door | Lock it (state 1) after setting the ratio |
| Opens for anyone who drives up | Pattern A left unlocked | Autolock, or pattern B |
| Panel visually open but the car hits an invisible wall | Shell collision still spans the opening, or a second static copy of the door sits in the shell/ymap | Cut the collision; delete the duplicate |
| Door does not move at all | Archetype lacks attribute 5/8 + Dynamic + Enable Door Physics; model not streamed (`IsModelValid` false); coords off | Fix the archetype; check `IsModelInCdimage`; re-read coords |
| Moves on the wrong axis / sinks into the floor | Wrong special attribute, or origin not where the template has it | 5 = bottom center, 8 = bottom corner; align to the template |
| Door clips through the vehicle or launches it | Door closing on a vehicle; the bound collides with the ceiling | Keep the lintel clear; close only when the opening is empty (check server-side before closing) |
| Can't trigger it from inside the car | `maxDistance` too small for the driver seat; ox_doorlock E key (control 38) in vehicles (verify) | `maxDistance` 5-15, or a remote command via `RegisterKeyMapping` |
| Door visible from outside but missing from inside | Not attached to the portal, single-sided mesh | Attach to the portal; closed mesh |
