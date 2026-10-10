# MLO structure: rooms, portals, entities, flags, timecycles, instance, occlusion

Sources: Sollumz 2.9 source (`ytyp/properties/*.py`, `ytyp/operators/*.py`), CodeWalker source (`MetaTypes.cs`,
`YmapFile.cs`, `Space.cs`), CFX native docs (`citizenfx/fivem` `ext/native-decls`), muto-atlas measurements.

## Data model

`.ytyp` → `CMloArchetypeDef` (Sollumz archetype type **MLO**, asset = the Bound Composite, asset type Assetless):

| Field | Holds | Notes |
|---|---|---|
| `name` | MLO archetype name | = composite name = `.ybn` name = `Interiors/Name` in `_manifest.ymf` |
| `mloFlags` | MLO flags | see flag tables |
| `entities` | `CEntityDef` list | position/rotation in MLO space, `lodDist -1` (Sollumz default since 2.9) |
| `rooms` | `CMloRoomDef`: `name`, `bbMin/bbMax`, `blend`, `timecycleName`, `secondaryTimecycleName`, `flags`, `portalCount`, `floorId`, `exteriorVisibiltyDepth`, `attachedObjects` (entity indices) | index 0 = limbo |
| `portals` | `CMloPortalDef`: `roomFrom`, `roomTo`, `flags`, `mirrorPriority`, `opacity`, `audioOcclusion`, `corners[4]`, `attachedObjects` | room indices, not names |
| `entitySets` | named entity lists, each entity with its room | toggled by script |
| `timeCycleModifiers` | spheres: name, percentage, range, start/end hour | local mood zones |

`.ymap` → `CMloInstanceDef` = normal `CEntityDef` (archetype = MLO name, world position, rotation, `lodDist`) plus
`groupId`, `floorId`, `defaultEntitySets`, `numExitPortals`, `MLOInstflags`.

## Coordinate frame

- MLO space origin = the Bound Composite's origin. Sollumz exports entity positions, room bounds and portal corners
  relative to it (`asset.location` is subtracted; "Set Bounds From Selection" ignores rotation, so keep the
  composite unrotated).
- Put drawable roots and the composite at the same point (floor centre of the ground storey) while modelling.
- Interior `.ybn` vertices are in this MLO space (CodeWalker: "it's an interior... the vectors are in local space").
- ymap rotation: an **MLO instance quaternion is stored as is**, normal entities store the **inverse**
  (CodeWalker `YmapFile.cs`, Sollumz `ymapexport.py`). Hand-written XML that inverts the MLO rotation shows the
  interior turned the wrong way while the exterior is right.

## Rooms

| Rule | Detail |
|---|---|
| limbo first | name exactly `limbo`, empty timecycle, flags 96 in vanilla (muto-atlas), bounds = whole MLO (`Create Limbo Room` uses the asset extents). Sollumz counts exit portals by the name `limbo`. |
| limbo ≤ 12 entities | game limit; Sollumz 2.9.0 blocks the 13th assignment, 2.9.0-dev (#1248) warns on export instead. Shell parts belong in real rooms. |
| room bounds | axis-aligned box in MLO space around the room's geometry, a few cm larger. Sollumz: select the room's collision verts in Edit Mode → **Set Bounds From Selection**. |
| room membership | decided by the **Room ID of the collision under the entity**, found by a downward probe of 4 units (16 in some cases); `SetInteriorProbeLength(0–150)` (CFX native) extends it for tall rooms/atriums. |
| room IDs | collision material `room_id` = index in the room list (0 = limbo). Sollumz caps it at 31 (5-bit field) → max 32 rooms incl. limbo. |
| timecycle | per room; hashed name. Copy one from a vanilla MLO of similar mood (CodeWalker: open its `.ytyp` → rooms). Sollumz default for new rooms: `int_gasstation`. Live test: `SetInteriorRoomTimecycle` + `RefreshInterior`. |
| floorId | storey index (0 = ground) (verify effect) |
| exteriorVisibiltyDepth | Sollumz default -1 (vanilla common); limits how deep through portals the exterior is drawn (verify) |
| blend | 1.0 default |

### Room flags (Sollumz `RoomFlags`, value = bit)

| Value | Name | Use |
|---|---|---|
| 1 | Freeze Vehicles | |
| 2 | Freeze Peds | |
| 4 | **No Directional Light** | blocks sun/moon light leaking in (it is not blocked by geometry) |
| 8 | **No Exterior Lights** | |
| 16 | Force Freeze | |
| 32 / 64 | Reduce Cars / Reduce Peds | vanilla limbo = 96 |
| 128 | Force Directional Light On | |
| 256 | Dont Render Exterior | **off** in any room with windows or a view outside |
| 512 | Mirror Potentially Visible | rooms with mirrors |

Measured vanilla (muto-atlas): dark/underground rooms 111 (= 1+2+4+8+32+64), above-ground rooms 99/107/0, limbo 96.
Change only `|= 4|8` to darken; leave population bits alone.

## Portals

| Rule | Detail |
|---|---|
| one per opening | every door, garage door and **window** between a room and limbo; one per internal doorway between rooms |
| corners | 4 coplanar points, slightly larger than the opening, on the shell's opening plane. Exit portal: corners counter-clockwise seen from outside, Sollumz arrow pointing out of the room (vanilla `v_int_66`, per `fivem-mlo-doors-windows`). Sollumz arrow = −(c3−c1)×(c2−c1). `Flip Direction` reverses the order. |
| from/to | exit: `room_from` = room, `room_to` = limbo. Internal: either order, but keep it consistent |
| attached objects | doors, garage doors and glass sit **on the portal** (entity → Attached Portal); built per `fivem-mlo-doors-windows` |
| exit portal count | portals touching limbo without flag 2 → set `numExitPortals` on the ymap instance (Sollumz Maps has a calc button; CodeWalker needs it typed) |
| `opacity`, `mirrorPriority`, `audioOcclusion` | 0 for normal openings |

### Portal flags (Sollumz `PortalFlags`)

| Value | Name | Use |
|---|---|---|
| 1 | One Way | rarely; breaks two-way visibility |
| 2 | Link Interiors Together | portal into another MLO; not counted as exit |
| 4 | Mirror | mirror surfaces (+16 expensive shaders, +128 can see directional, +256 portal traversal, +512 floor, +1024 can see exterior) |
| 8 | Disable Timecycle Modifier | set on vanilla window portals |
| 32 | Low LOD Only | |
| 64 | Hide when door closed | door portals: culls what is behind a closed door |
| 2048 / 4096 | Water Surface / Extend To Horizon | |
| 8192 | Use Light Bleed | vanilla shop door portal |

### MLO flags (Sollumz `MloFlags`)

| Value | Name |
|---|---|
| 256 | Subway |
| 512 | Office |
| 1024 | Allow Run (verify in-game effect) |
| 2048 | Cutscene Only |
| 4096 | LOD When Locked |
| 8192 | No Water Reflection |
| 32768 | Has Low LOD Portals |

## Entities

- Every entity is attached to exactly one room or one portal. Unattached = invisible.
- Split the interior shell **per room** (one drawable per room or per storey) so hidden rooms are culled. One giant
  shell attached to one room is drawn whenever that room is visible.
- Props inside the footprint go into the MLO entity list, not into a ymap (ymap props inside an MLO are culled;
  muto-atlas).
- `lodDist -1` = archetype `lodDist` (Sollumz archetype default 200, HD texture distance 100).
- Entity flags: Sollumz default 0. Vanilla MLO entities measured 18350080 (includes Cast Static Shadows 524288 +
  Cast Dynamic Shadows 1048576; muto-atlas). Copy flags from a comparable vanilla MLO (verify impact).
- Do not put the same entity in a room and an entity set; set entities still need a room.

## Entity sets

- Sollumz: MLO → Entity Sets tab → `+`, then set each entity's **EntitySet** (and room). Visibility toggle in
  Blender since 2.8.1.
- Default-on sets: list them in the ymap instance `defaultEntitySets`.
- Script (client; names per docs.fivem.net/natives, verify): `ActivateInteriorEntitySet(id, 'set_name')`,
  `DeactivateInteriorEntitySet(id, 'set_name')`, `IsInteriorEntitySetActive`, then `RefreshInterior(id)`.
  `id = GetInteriorAtCoords(x, y, z)`; wait for `IsValidInterior(id)` / `IsInteriorReady(id)`.

## Timecycle modifiers

- Room `timecycleName` sets the base look. MLO `timeCycleModifiers` (spheres) add local zones (Sollumz: Timecycle
  Modifiers tab, gizmo). Map-level boxes live in the ymap (Sollumz Maps → Timecycle Modifiers).
- Custom timecycle definitions: `files { 'timecycle_mods_abc.xml' }` +
  `data_file 'TIMECYCLEMOD_FILE' 'timecycle_mods_abc.xml'`.

## Visibility and occlusion: how it decides what to draw

| You stand | What renders | Breaks when |
|---|---|---|
| outside | exterior; interior rooms only through **exit portals in view** | no exit portal, portal flipped/too small, vanilla occluder in front, MLO instance not streamed (`lodDist`) |
| inside room A | room A, rooms reachable through visible portals, exterior through exit portals | missing internal portal (neighbour room invisible), room flag 256, One Way portal |
| on a prop/mezzanine/stairs | depends on the Room ID found 4 units below | that collision has room ID 0 or is not interior collision → you are "outside" and the interior culls |

- Vanilla ymaps contain **box and model occluders**. They do not know about your interior; any occluder inside or
  in front of the building hides the interior seen through the door. Remove/shrink them in your copy of that
  ymap (CodeWalker selection mode Occlusion; `fivem_conflicttool` can shrink boxes).
- Live debugging (CFX natives, client, Legacy; verify on Enhanced): `GetInteriorRoomCount`, `GetInteriorRoomName`,
  `GetInteriorRoomFlag/SetInteriorRoomFlag`, `GetInteriorRoomExtents/SetInteriorRoomExtents`,
  `GetInteriorPortalCount`, `GetInteriorPortalFlag/SetInteriorPortalFlag`, `GetInteriorPortalCornerPosition/
  SetInteriorPortalCornerPosition`, `GetInteriorPortalRoomFrom/To`, `SetInteriorProbeLength`; always
  `RefreshInterior(id)` after a setter. Tune live, then copy the values back into Blender.

## Limits and pools

| Limit | Value | Source |
|---|---|---|
| limbo entities | 12 | Sollumz commit #1202 ("mirrors the game's internal limit") |
| rooms per MLO | 32 incl. limbo | collision room ID field 0–31 (Sollumz property) |
| Gen9 materials/geometries per drawable | 128 | Sollumz wiki (reported) |
| FiveM `increase_pool_size` max increase | InteriorProxy 450, PortalInst 225, OcclusionPortalEntity/Info 750, OcclusionPathNode 5000, OcclusionInteriorInfo 20, StaticBounds 5000 | fivem-docs `server-commands.md` |
