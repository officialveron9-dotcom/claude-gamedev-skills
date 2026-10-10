# Doors: archetype, model, placement

Read when building or placing a swinging, double or sliding door in an MLO. Garage/roller/barrier specifics are in
[garage-doors.md](garage-doors.md). Lua and doorlock configs are in [door-scripting.md](door-scripting.md).

## How vanilla doors work

- A door is an **object archetype** with a door **special attribute** (Normal 7, Garage 5, Sliding 8, Barrier 9,
  Sliding Vertical 10, Rail Crossing 12) and the archetype flags **Dynamic (131072)** + **Enable Door Physics
  (67108864)**. The Sollumz wiki says Enable Door Physics does nothing unless the special attribute is set too.
- Unlocked swing doors are pushed open by peds and vehicles and swing back. A locked door is held by the door system
  at its target (closed unless an open ratio is set). If you lock a door while it is ajar, it closes first and then
  locks (Cfx forum guide).
- **Not networked.** A door's swing and break state are simulated per client. A door shot open on one client stays
  closed for a player who arrives later (citizenfx/fivem #2563, contributor replies). Every multiplayer lock script
  therefore registers doors locally (`AddDoorToSystem(..., false, false, false)`) and broadcasts the state itself.
- The door system maps a **door hash** you choose to a model and position. It acts on the object of that model at
  that position: `DoorSystemFindExistingDoor` searches 0.5 m, and ox_doorlock's `GetClosestObjectOfType` uses 1.0 m.

### Vanilla reference: 24/7 shop (`v_int_66.ytyp`, archetype `v_shop_247`)

| Item | Value |
|---|---|
| Front door portal | `roomFrom 1 (V_66_ShopRm) -> roomTo 0 (limbo)`, flags `8192` (Use Light Bleed), `attachedObjects` = both door entities |
| Door entities | `v_ilev_247door` (rotation quaternion `0,0,1,0` = 180° about Z) + `v_ilev_247door_r`: two models, not mirrored by scale |
| Door entity flags / lodDist | `555220992` / `100` |
| Door extension | `CExtensionDefDoor`: `enableLimitAngle true`, `startsLocked false`, `canBreak false`, `limitAngle 1.117011` (radians, 64°), `doorTargetRatio 0`, `audioHash` per door |
| Door leaf vs portal | portal plane at y = -5.578, door entities at y = -5.490 (about 9 cm inside) |

## Option A: reuse a vanilla door (fastest)

1. Find a model. In CodeWalker, use RPF Explorer > search `door`, `gate`, `gar_door`, `shutter`. Open the `.ytyp` that
   holds the archetype and check `specialAttribute` and `flags`. Alternatively click a door in the world view and read
   the archetype panel. Common families: `v_ilev_*` (interior doors), `prop_*door*`, `prop_*gate*`, `hei_*`, `apa_*`.
2. Models that public doorlock configs drive with the door system (so they are known door archetypes):

| Model | Kind | Seen in |
|---|---|---|
| `v_ilev_bl_door_l` | swing (official template) | Cfx docs Part 8 |
| `v_ilev_247door` / `v_ilev_247door_r` | glass double swing | vanilla v_int_66 |
| `v_ilev_ph_cellgate`, `v_ilev_ph_cellgate1` | cell gate | qb-doorlock |
| `prop_doorluxyry`, `prop_doorluxyry2`, `apa_prop_apa_cutscene_doorb` | swing | qb-doorlock |
| `prop_facgate_07b` | sliding gate (official template) | Cfx docs, qb-doorlock |
| `prop_gate_prison_01`, `hei_prop_station_gate`, `prop_fnclink_03gate5` | gates | qb-doorlock |
| `prop_autodoor` | automatic sliding double door | qb-doorlock (luxury dealer) |
| `prop_com_gar_door_01` | garage door | qb-doorlock example |
| `lr_prop_supermod_door_01` | vertical garage (official template) | Cfx docs |
| `prop_sec_barrier_ld_01a`, `prop_sec_barrier_ld_02a` | barrier arm | cfx-anes-gates (`prop_sec_barier_02a` is **not** a door) |

3. Add it to the MLO as an entity by archetype name. Vanilla archetypes need no streaming. Build the opening to fit
   the door: get the size with `GetModelDimensions(model)` in game or from the bounding box in CodeWalker. Do not
   scale door entities (`scaleXY`/`scaleZ` ≠ 1); whether the bounds of dynamic objects follow entity scale is unverified.

## Option B: custom door from your own geometry (Sollumz, official Cfx workflow)

1. Model the leaf as a **closed** mesh (front, back, edges) with normals pointing out. A single plane disappears from
   one side. Paint vertex colours (`Color 1`, face corner, byte color): green for interior assets, red for exterior
   (Cfx docs Part 3). Unpainted props look dark or black in MLOs (Sollumz FAQ).
2. Import the template: `v_ilev_bl_door_l.ydr` (swing), `prop_facgate_07b.ydr` (sliding), `lr_prop_supermod_door_01.ydr`
   (vertical garage). Use CodeWalker to export and Sollumz to import.
3. Origin: select the hinge edge, use `Mesh > Snap > Cursor to Selected`, then in Object Mode `Object > Set Origin >
   Origin to 3D Cursor`. Hinge = side center (swing), bottom corner (sliding), bottom center (vertical garage).
4. Align your mesh with the template mesh (same facing and same closed pose) and apply all transforms.
5. Convert to Drawable. Delete the template mesh, then unparent your mesh and parent it to the template armature/drawable.
   Add a **Copy Transforms** constraint with Target = armature and Bone = the template's door bone.
6. Collision: keep the template's Bound Composite and resize its box (a box bound is better than a mesh). If you
   changed the collision's scale or transforms, create a **new Bound Composite** and parent the collision to it, or
   the in-game collision breaks (Cfx docs). Keep the template's composite flags and use a fitting material
   (`WOOD_*`, `METAL_*`, `GLASS_*` for glass doors).
7. Textures: embed them or use a `.ytd` named in the archetype's Texture Dictionary. Painting out a door baked into
   the shell texture belongs to `gta-texture-editing`.
8. Export the `.ydr` (Native or CW XML; Gen8 and/or Gen9). File name = archetype name.

### ytyp archetype (Sollumz: Archetype Definition > YTYPs > Auto-Create From Selected)

| Field | Value |
|---|---|
| Type | Base |
| Name / Asset Name | `my_mlo_door_01` (= file name) |
| Asset Type | Drawable |
| Special Attribute | Normal Door (7) / Sliding Door (8) / Garage Door (5) |
| Flags | Dynamic + Enable Door Physics (at least `67239936`); never Static (32) |
| Physics Dictionary | empty (collision embedded in the `.ydr`) |
| LOD Distance | about 100 (vanilla door entities use 100) |

```xml
<Item type="CBaseArchetypeDef">
  <lodDist value="100" />
  <flags value="67239936" />          <!-- 131072 Dynamic + 67108864 Enable Door Physics -->
  <specialAttribute value="7" />      <!-- Normal Door -->
  <!-- bbMin/bbMax/bsCentre/bsRadius: let Sollumz/CodeWalker compute -->
  <name>my_mlo_door_01</name>
  <textureDictionary>my_mlo_door_01</textureDictionary>
  <physicsDictionary />
  <assetType>ASSET_TYPE_DRAWABLE</assetType>
  <assetName>my_mlo_door_01</assetName>
</Item>
```

## Placing the door

**In the MLO (recommended, vanilla practice).** In the Sollumz MLO archetype, open Entities > Add Object(s) as Entity,
then set **Attached Portal** to the doorway portal instead of a room. The door then renders together with the portal
from both rooms.

Door extension (entity extension `CExtensionDefDoor`; it is the default extension type for MLO entities in Sollumz):

| Field | Meaning |
|---|---|
| `enableLimitAngle` / `limitAngle` | Clamp the swing; radians (vanilla 1.117011 = 64°) |
| `startsLocked` | Door begins locked (scripts override it) |
| `canBreak` | Door can break off (vanilla shop doors: false) |
| `doorTargetRatio` | Default target ratio, 0 = closed (verify effect) |
| `audioHash` | Door sound set. Copy one from a similar vanilla door |

**In a separate `.ymap` (exterior entity).** This is fine for doors in an exterior wall that is not an MLO doorway. A
door that sits in an MLO portal but lives in a ymap is an exterior entity. It is lit as exterior and can vanish or
flicker from inside (verify), so keep MLO doorway doors in the MLO.

**In an entity set.** This makes doors optional (`ActivateInteriorEntitySet` / `DeactivateInteriorEntitySet` +
`RefreshInterior`). The door object is recreated, so re-apply the door state after the refresh (verify).

Portal flag **64 "Hide when door closed"**: by its name it culls the far side while the attached door is closed (verify).
Use it only for opaque doors, never for glass doors (vanilla 24/7 glass doors: flags 8192 only).

## Double doors

- Two entities, one per hinge. Vanilla uses separate L/R models (`v_ilev_247door` / `_r`), and one entity is rotated
  180° about Z. **Never mirror with negative scale.**
- Two door hashes, and the same state is always applied to both (ox_doorlock `doors = { {...}, {...} }`,
  qb-doorlock `doors = {...}`).
- Leave a gap of a few mm between the leaves, and make sure the leaf bounds do not overlap when closed, or they push
  each other.

## Frames and the opening

- Cut the opening in the shell mesh **and** in the shell collision. Room/portal/collision workflow: `fivem-mlo-creation`.
- The frame is static: either shell geometry or a separate static prop. Static is fine on the frame but never on the leaf.
- In the closed pose the leaf bound must not touch the frame or floor collision. Leave a few mm to 1-2 cm, or the
  door jitters, sticks or gets launched (practice; verify per model).
- The portal covers the inner frame opening. The leaf lies within about 10 cm of the portal plane (vanilla: 9 cm).

## Sliding doors

Use the template `prop_facgate_07b`, Special Attribute 8, origin at the bottom corner. They are "automatic" doors: when
unlocked they open as someone approaches within the automatic distance. See [garage-doors.md](garage-doors.md) for rate
and distance.

## Wrong vs right

| Wrong | Right |
|---|---|
| Door leaf modelled inside the shell `.ydr` | Separate `.ydr` + archetype + MLO entity |
| Origin at the mesh center | Origin at the pivot for the door type |
| Flags `Dynamic` only (door falls over or rolls away) | `Dynamic` + `Enable Door Physics` + special attribute |
| `Static` on the leaf "so it does not move" | Lock it with the door system instead |
| Leaf with front faces only | Closed mesh, both sides visible |
| Script coords taken from Blender | World coords of the door object read in game |
| Shell collision across the doorway | Opening cut; the door bound blocks when closed |
| Left door made with `scaleXY -1` | L/R models, or a 180° rotation |
