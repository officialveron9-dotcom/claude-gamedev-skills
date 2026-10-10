# Collision (.ybn), navmesh, lighting, vertex colours, timecycles

Sources: Sollumz 2.9 source (`ybn/`, `ydr/lights.py`, `ydr/properties.py`, presets JSON), Sollumz wiki (collisions,
interiors tutorial, FAQ, light flags), Cfx assets guide part 5, CFX native docs, muto-atlas measurements.

## Collision

### Hierarchy

```
Bound Composite        abc_bldg_mlo        <- name = MLO archetype = .ybn file; MLO origin
└─ Bound GeometryBVH   abc_bldg_mlo.bvh    <- composite flags (what it is / what collides with it)
   ├─ Bound Poly Mesh  abc_bldg_mlo.poly_mesh   <- triangles; one collision material per surface+room
   ├─ Bound Poly Box / Sphere / Capsule / Cylinder   <- cheap furniture, pillars
```

### Build steps (Sollumz 2.9)

1. Copy the interior shell, floors, slabs, stairs and walls into one mesh. Drop small details (skirting, frames,
   decals); collision needs no UVs. Keep the doorway/window holes open — the custom door/glass objects bring their own
   collision (`fivem-mlo-doors-windows`).
2. Materials: one collision material per **surface type × room**, because the Room ID lives on the material.
   Sollumz Tools → Collisions → material list → Create Collision Material; then Material Properties → Collision
   Properties → **Room ID** (dropdown lists the MLO's rooms once the composite is the MLO asset).
3. Select the mesh → V → **Convert to Composite** (Child Type: GeometryBVH). Since 2.9.0 the default flag preset
   "General (Default)" is applied automatically; on older versions apply it by hand
   (Object → Flag Presets → Apply) or the collision does nothing (Sollumz FAQ).
4. Keep the composite at the MLO origin, unrotated, scale 1. Interior collision is MLO-local. (The Sollumz FAQ line
   "apply world coordinates to the poly_mesh" is for **map** ybns, e.g. the vanilla exterior collision you cut.)
5. Furniture: Sollumz Tools → Collisions → Create Bound (Box/Cylinder/...), parent to the BVH, give it a material.

| Material (Sollumz index) | Use |
|---|---|
| CONCRETE (1) | floors, walls, slabs |
| BRICK (13), STONE (11), MARBLE (14), CERAMIC (81) | masonry, tiles |
| WOOD_SOLID_MEDIUM (70), WOOD_SOLID_POLISHED (72), WOOD_FLOOR_DUSTY (73), LAMINATE (96) | wooden floors, stairs |
| LINOLEUM (95), CARPET_SOLID (97), CARPET_FLOORBOARD (99) | office/flat floors |
| PLASTER_SOLID (101) | drywall |
| METAL_SOLID_MEDIUM (56) | steel stairs, railings |
| GLASS_SHOOT_THROUGH (112), GLASS_BULLETPROOF (113) | glass (normally on the glass object itself) |
| DEFAULT (0) | avoid; wrong footstep/bullet effects |

Script lookup by name instead of index: `collisionmats` in `ybn.collision_materials` (see
[blender-automation.md](blender-automation.md)).

### Flag presets (Sollumz `flag_presets.json`)

| Preset | Type flags (CompositeFlags1) | Include flags (CompositeFlags2) | Use |
|---|---|---|---|
| General (Default) | MAP_WEAPON, MAP_DYNAMIC, MAP_ANIMAL, MAP_COVER, MAP_VEHICLE | vehicles, PED, RAGDOLL, animals, OBJECT, PLANT, PROJECTILE, EXPLOSION, FORKLIFT_FORKS, TEST_* , GLASS | walls, floors |
| General 2 | same without MAP_WEAPON | same | geometry bullets should ignore |
| Stair plane | MAP_STAIRS | PED, TEST_* | invisible smooth ramp for walking |
| Stair mesh | General + MAP_STAIRS | General | the actual steps |

### Stairs

- Vanilla pattern: a smooth ramp polygon with "Stair plane" (peds walk on it) plus the stepped mesh with
  "Stair mesh" (everything else). Simplest working variant: one ramp with General preset and the STAIRS poly flag.
- Steps-only collision → jittery walking and camera bob; give the ramp the same Room ID as the floor it leads to
  (or split it at the landing) so the 4-unit probe never sees room 0 on the stairs.
- Per-polygon flags on the collision material: STAIRS, NOT_CLIMBABLE, SEE_THROUGH, SHOOT_THROUGH,
  NOT_COVER, WALKABLE_PATH, NO_CAM_COLLISION, NO_NAVMESH, TOO_STEEP_FOR_PLAYER, NO_NETWORK_SPAWN, ...

### Exterior (vanilla) collision

- The doorway must also be open in the vanilla **world-space** `name.ybn` and `hi@name.ybn` around the building
  (Sollumz tutorial). Edit copies, stream them under the same names. Collision selection mode in CodeWalker shows
  which files cover the door.

### Why players fall through or get stuck

| Cause | Check |
|---|---|
| `.ybn` name ≠ MLO archetype name, or not listed under `Interiors` in `_manifest.ymf` | manifest XML |
| interior ybn exported in world space (composite not at MLO origin) | collision appears offset by the building's world position |
| no flag preset on the BVH (pre-2.9 or manually created BVH) | BVH Object Properties → flags all off |
| empty collision geometry | Sollumz 2.9 reports it as an export error (#1244) |
| vanilla exterior ybn still closed at the door | stuck in the doorway |
| door/glass object collision overlapping the frame | leave a few mm gap |
| stream cache | reconnect fully after replacing a `.ybn` |

## Navmesh (NPCs)

- Peds path on `.ynv` cells (`navmesh[X][Y].ynv`, 150 m grid); interiors have no navmesh of their own, their
  polygons live in the cell flagged interior. A custom MLO ships none, so NPCs walk on whatever was there before
  (rage-cli README). Players are unaffected.
- Sollumz imports `.ynv` only (no export). CodeWalker has a WIP navmesh editor. `rage-cli navmesh build`
  (VIRUXE/rage-cli, public domain) generates interior polygons from your `.ybn` + `_milo_.ymap` + `.ytyp` and
  appends them to the vanilla cell; stream the resulting `navmesh[X][Y].ynv` (verify on your server, and only one
  resource may override a cell).
- If NPC jobs (shop clerks, scenarios) do not need to walk, skip navmesh work.

## Lighting

### What makes an interior bright or dark

| Layer | Set where | Typical |
|---|---|---|
| Room timecycle | ytyp room `timecycleName` | copy from a vanilla room with the same mood |
| Vertex colour `Color 1` | Blender colour attribute (Face Corner, Byte Color) | interior faces R = 0, G 0.4–0.8; exterior faces red-dominant |
| Embedded lights | Sollumz lights inside the room's drawable | real light, cost per light |
| Emissive shaders | `emissive*.sps` on lamp meshes | glow only, cast no light; pair with a light |
| Room flags | 4 No Directional Light, 8 No Exterior Lights | stops sun/moon and street lights leaking in |

Vertex colour channels: R = natural/sky ambient (vanilla interior surfaces measured R = 0 exactly; a Blender round
trip can break it → interior picks up sky light and looks wet/over-reflective; muto-atlas), G = artificial
ambient (G = 0 → pitch black inside), B = described as moonlight/extra term in the Sollumz wiki (verify).
Community scheme (R* interiors): lower walls green → dark green, upper walls blue → dark blue, red/yellow only where
sun enters (muto-atlas community notes). Unpainted (white) props glow pink-red at night (Sollumz FAQ).

### Lights in Sollumz

- Select the room's drawable → Sollumz Tools → Drawable → **Light Tools** → **Create Light** (Point / Spot / Capsule); the
  light is parented to the drawable and exported inside its `.ydr`. The light renders only while its room renders.
- Properties: color, **intensity** (`light_properties.intensity`; Blender `energy` = intensity × 500 — set
  intensity, not energy), falloff (cutoff distance), falloff exponent, flashiness, extent (capsule), cone angles
  in **radians** (2.9.0-dev clamps them on export since 2026-09-06), corona, volume, culling plane.
- **Time flags** = 24 hour bits (hour 0 = bit 0). Interior lights: all 24 hours = `16777215`. Sollumz wall-light
  presets use `15728767` (night only: 00–07 and 20–24) — wrong for an interior that must be lit at noon.
  The "Default" preset has time flags 0 and intensity 0.02 (energy 10): set both.
- Preset intensities for orientation (Sollumz presets): point wall light 0.5–1.0 with falloff 2; spot wall light 3–8
  with falloff 5–8.
- Do not hide a light to disable it (exports at a broken position); set intensity 0.

| Light flag | Value | Use |
|---|---|---|
| Interior Only | 1 | default for MLO lights |
| Exterior Only | 2 | |
| Cast Static Shadows | 128 | static geometry shadows |
| Cast Dynamic Shadows | 256 | player/ped shadows; expensive, few per room |
| Calculate From Sun | 512 | intensity follows time of day |
| Enable Buzzing | 1024 | neon/tube hum |
| No Specular | 8192 | |
| Both Interior and Exterior | 16384 | lamps over the entrance |
| Corona Only | 32768 | |
| Enable Culling Plane | 262144 | stop a light bleeding through a wall |
| Only Low Res Shadows | 2097152 | cheaper shadows |

Light count: keep shadow-casting lights to a handful per room and prefer static shadows; exact engine limits per
room were not found (verify in game with FPS and Pool Monitor). Live tuning without re-export:
`byfredQC/mlo-light-manager` (Blender ↔ FiveM live link, GPL-3; see [external-tools.md](external-tools.md)).

### Pitch black / too bright

| Symptom | Cause | Fix |
|---|---|---|
| everything black inside, day and night | `Color 1` missing or G = 0; entities in limbo; no timecycle | paint G; attach to rooms; set room timecycle |
| black only at night | lights' time flags = night-off or 0, intensity ≈ 0 | time flags 16777215, intensity > 0 |
| black faces/patches | inverted normals on the inner shell; `trees_normal` shader inside an interior (muto-atlas) | recalc normals inward; use `normal.sps` family |
| interior glows at night | white vertex colours / unpainted props, emissive everywhere | paint vertex colours, limit emissive |
| sunlight/shadow acne inside | room flag 4 missing | add 4 (and 8) |
| washed out, "wet", over-reflective | R channel ≠ 0 on interior faces | set R = 0 on interior faces |
| exterior timecycle (fog, rain light) inside | standing on room-ID-0 collision | fix room IDs |
