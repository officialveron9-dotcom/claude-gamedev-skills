# Windows: glass, shaders, portals, lights

Read when an MLO needs real windows: see out from inside, see in from outside, glass that looks right, optional
breakage, and lit windows at night. General rooms/portals/collision are covered in `fivem-mlo-creation`. Removing
windows painted into textures is covered in `gta-texture-editing`.

## Anatomy of a working window

1. **Hole** in the shell mesh and in the shell collision (or a glass collision, see below).
2. **Frame**: opaque, part of the shell or a static prop.
3. **Glass**: its own drawable/archetype, placed as an MLO entity **attached to the window portal** (vanilla 24/7:
   `v_ret_247_win1/2/3` are the `attachedObjects` of the window portals).
4. **Portal** `room -> limbo` over the opening (or `roomA -> roomB` for interior windows).

## Glass geometry

- Use two faces, one facing out and one facing in, offset by the pane thickness (a few mm), or one face plus the
  archetype flag **Double-sided rendering (65536)**. Two faces at the same position z-fight (flicker).
- Back faces are culled. A single outward face is invisible from inside, and vice versa.
- Keep glass out of the shell drawable. Alpha geometry inside a large opaque drawable sorts against its own faces
  and other glass badly. Enhanced also caps a drawable at 128 materials/geometries.
- UVs: `UVMap 0`. Vertex colours: `Color 1` green for interior assets (Cfx docs). Missing vertex paint makes MLO
  props look dark or black (Sollumz FAQ).

## Glass shaders (Sollumz/szio `Shaders.xml`, verified 2026-10; same names on Gen9)

| Shader | Bucket | Samplers | Notable params (defaults) | Use |
|---|---|---|---|---|
| `glass` | 1 alpha | Diffuse, Bump, Environment | reflectivePower 0.45, bumpiness 1 | general window glass with env reflection |
| `glass_pv` | 1 | Diffuse | DecalTint, Crack*, Broken* colours | simple pane with crack params (breakable-style; verify use) |
| `glass_pv_env` | 1 | Diffuse | as `glass_pv` + env | as above with reflection |
| `glass_env` | 1 | Diffuse, Bump, Spec | bumpiness 0.1, specularFalloffMult 400 | spec-mapped glass |
| `glass_spec` | 1 | Diffuse, Spec | specularFalloffMult 100 | cheap spec glass |
| `glass_reflect` | 1 | Diffuse, Environment | reflectivePower 25 | strongly reflective (shopfront) |
| `glass_normal_spec_reflect` | 1 | Diffuse, Bump, Spec, Environment | reflectivePower 1 | full-featured |
| `glass_breakable` | 1 (+3 screendoor variant) | Diffuse, Bump, Spec | Crack*, Broken* | breakable fragment glass |
| `glass_emissive` | 0 or 1 | Diffuse, Bump, Environment | emissiveMultiplier 2 | glowing glass (always on) |
| `glass_emissivenight` | 1 | Diffuse, Bump, Environment | emissiveMultiplier 6 | lit windows at night (by name; verify timing) |
| `glass_displacement` | 7 displacement alpha | Diffuse, Bump, Spec, Environment | displParams 16,16,6 | refracting glass, rendered last |
| `mirror_default` / `mirror_decal` / `mirror_crack` | 1 | ... | gMirrorBounds | mirrors (need a mirror portal, flag 4) |

`decal_glass` **does not exist**. For dirt or stickers on glass use a separate `decal`/`decal_dirt` layer, or bake
them into the glass diffuse alpha.

### Transparency and sorting

- Opacity comes from the **DiffuseSampler alpha**. Use BC3/DXT5 (or uncompressed) with alpha of about 20-90 out of
  255. A BC1/DXT1 texture with no alpha channel renders fully opaque, and alpha 0 makes the glass invisible.
- Sollumz sets the render bucket from the shader. The Alpha bucket means "alpha without shadows, commonly used on glass".
- Sorting fixes in order: (1) a separate glass entity per window; (2) archetype flag **Draw Last (4)**; (3) also
  **Disable alpha sorting (64)**; (4) avoid glass directly behind glass inside the same drawable.
- Vanilla glass archetypes (`v_66_glass1..3`) use flags `536879104` = Use Ambient Scale (536870912) + Dont Cast
  Shadows (8192).

## Glass collision

- Materials: `GLASS_SHOOT_THROUGH` (bullets pass), `GLASS_BULLETPROOF`, `GLASS_OPAQUE`. Material flags include
  `SEE THROUGH`, `SHOOT THROUGH`, `SHOOT THROUGH FX` (Sollumz). The collision polys need the Room ID of the room.
- Put a thin box bound in the opening. If the shell collision has a hole and no glass bound, peds walk through.

## Breakable glass (fragment `.yft`)

Exported by the current Sollumz source (2.9-dev, 2026-10). The Sollumz wiki still says non-vehicle `GlassWindows` are
unsupported, so check that your build has **Bone > Fragment > Physics > Breakable Glass**.

1. Fragment armature with a single root bone. The glass bone has **Use Physics** and **Breakable Glass** enabled, plus
   a Glass Type: `Pane`, `Security` or `Pane Weak`.
2. The mesh skinned to that bone has exactly **2 separate, parallel planes of 2 triangles each** (front and back; their
   distance = glass thickness) and a material. Sollumz warns: "requires 2 separate planes", "planes need to be made
   up of 2 triangles each", "planes are not parallel", "missing the mesh and/or collision", "missing a material".
3. Link a collision object to the same bone (Child Of constraint) and give it a mass.
4. ytyp archetype: **Dynamic** flag (Sollumz prop-setup: physics needs Dynamic), Asset Type Fragment.
5. Shader: use the crack-capable family (`glass_breakable`, `glass_pv*`). Import a vanilla breakable window to copy
   its settings (verify).
6. Broken glass is per client: it is not synced, and it resets when the object streams out and back in (verify).

## Portals for two-way visibility

Rules (vanilla `v_int_66` + Sollumz source + Sollumz wiki):

1. One portal per opening (or per group of panes in one opening): `Room From` = the interior room, `Room To` =
   `limbo` (index 0). The Sollumz tutorial requires `Room -> Limbo`, not the reverse.
2. **Direction:** Sollumz draws an arrow along `normal = -(c3 - c1) x (c2 - c1)`. In all four room->limbo portals of
   vanilla `v_int_66` this normal points **outward** (toward limbo). A forum answer agrees: "the blue arrow should
   point out, i.e. from room to limbo". In those portals the corners run c1 bottom-right, c2 top-right, c3 top-left,
   c4 bottom-left **as seen from outside**. Use **Flip Direction** if the arrow points in.
3. **The same portal works both ways.** From inside, the exterior is drawn through it. From outside, the room is
   drawn through it. Do not set **One-Way (1)**.
4. Portal shape: a planar quad, slightly larger than the visible glass, inside the frame, a few cm off the glass
   plane (vanilla: portal y = -5.578, glass y = -5.505, about 7 cm; the door portal reaches 0.15 m below the floor).
   It must cover the whole see-through area. Any glass outside the portal shows the void behind. One portal may serve
   several panes: vanilla portals 3 and 4 each carry an upper and a lower pane.
5. Attach the glass entity (and door leaves) to that portal.
6. Rooms with windows must not have room flag **Dont Render Exterior (256)**.
7. Rooms behind rooms see the exterior only through chained portals. Keep `exteriorVisibiltyDepth` at `-1` (vanilla
   default; exact semantics unverified).
8. Interior windows between two rooms: portal `roomA -> roomB` with the glass attached.

Sollumz steps: select the MLO archetype > Portals > set Room From / Room To > in Edit Mode select the 4 opening vertices
> **Create From Verts**. Corners are sorted by angle **in the current viewport**, so the direction depends on the side
you look from: always check the arrow afterwards. Then go to Entities > select the glass entity > Attached Portal.

### Vanilla example (`v_shop_247` storefront)

| Portal | From -> To | Flags | Attached |
|---|---|---|---|
| 0 front door | 1 -> 0 | 8192 Use Light Bleed | `v_ilev_247door`, `v_ilev_247door_r` |
| 1 back-room door | 1 -> 2 | 0 | none |
| 2 floor mirror | 1 -> 0 | 1796 = Mirror 4 + Portal Traversal 256 + Mirror Floor 512 + Can See Exterior 1024 | none |
| 3, 4 lower windows | 1 -> 0 | 8 Disable Timecycle Modifier | `v_ret_247_win3`, `v_ret_247_win2` |
| 5 upper window | 1 -> 0 | 8 | `v_ret_247_win1` |

### Portal flags (CodeWalker = Sollumz)

| Value | Name | Note |
|---|---|---|
| 1 | One-Way | never on normal windows |
| 2 | Link Interiors together | portal between two MLOs |
| 4 | Mirror | with mirror shaders; 16/128/256/512/1024 are mirror options |
| 8 | Disable Timecycle Modifier | vanilla windows use it (by name: the room tc is not applied through it; verify) |
| 32 | Low LOD Only | |
| 64 | Hide when door closed | opaque doors only (verify) |
| 2048 / 4096 | Water Surface / Extend To Horizon | |
| 8192 | Use Light Bleed | vanilla front door portal (verify effect) |

### Room flags

`1` Freeze Vehicles, `2` Freeze Peds, `4` No Directional Light, `8` No Exterior Lights, `16` Force Freeze, `32`
Reduce Cars, `64` Reduce Peds, `128` Force Directional Light On, `256` Dont Render Exterior, `512` Mirror Potentially
Visible. Vanilla 24/7: limbo and shop room `96`, back room `608`.

## Timecycle and reflections

- Each room has a timecycle (the Sollumz default is `int_gasstation`). Pick one that matches the interior. Vanilla
  window portals carry flag 8.
- `glass`/`glass_reflect` reflect the EnvironmentSampler/cubemap and do not mirror the scene. Real mirrors need a
  mirror portal (flag 4) and `mirror_*` shaders.

## Lights and night

- Interior lights (drawable lights) render only while their room renders: from outside that means through a
  room->limbo portal, within streaming range of the MLO.
- Light flags (Sollumz): **Interior Only**, **Exterior Only**, **Both Interior and Exterior** ("interior lights bleed
  out of the MLO and vice versa"). Use the last one for light that should spill through a window onto the street.
- Far views: add exterior emissive window geometry (`glass_emissivenight`, or a Time archetype for night-only
  emissives) and bake LOD lights (Sollumz "Bake LOD Lights" makes `lodlights`/`distlodlights` ymaps).
- Room flag `8` No Exterior Lights keeps exterior lights out of the room (by name).

## Limits and performance

- Each visible portal makes the engine traverse and render the other side. Use one portal per opening. The vanilla
  storefront uses 1 door portal + 3 window portals.
- No documented per-MLO portal maximum was found. Pools that `increase_pool_size` can raise (Cfx docs, FiveM max
  increase): `PortalInst` +225, `OcclusionPortalInfo` +750, `OcclusionPortalEntity` +750, `InteriorProxy` +450,
  `OcclusionInteriorInfo` +20. Which asset fills which pool is unverified. Check F8 > Tools > Streaming > Pool Monitor.
- Ymap occluders (box/model) must not cover windows or doorways, or they hide what is behind them.
