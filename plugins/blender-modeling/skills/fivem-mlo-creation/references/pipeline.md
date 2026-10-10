# Pipeline detail: setup, find, export, import, exterior swap, placement

Steps 1–4 and 10 of the pipeline table in `SKILL.md`. Versions: Sollumz 2.9.0, CodeWalker 30 Dev48+,
Blender 4.5 LTS / 5.2 LTS.

## 0. One-time setup

| Item | Setting | Why |
|---|---|---|
| CodeWalker | Download only from the CodeWalker Discord `#releases` (Dev48+; the Cfx guide uses Dev48). Options → **Start in Edit Mode**. | GitHub `master` stops at 2025-04-11; Gen9 converter and fixes are Discord builds. |
| Nametables | Drop the "updated nametables" `.rpf` (Discord `#tips-documentation`) into the game root via RPF Explorer in edit mode. | Otherwise many names show as `hash_XXXXXXXX`. |
| World view | DLC Level = bottom-most entry, **Enable DLC** on, Options → Save Settings. | Without DLC level you look at the base-game ymap, not the `hei_`/patchday version that actually loads. |
| Game folder | CodeWalker reads Legacy (`GTA5.exe`) and Enhanced (`gta5_enhanced.exe`) installs. | Keys come from the exe (`GTAKeys.cs`). |
| Blender | 4.5 LTS or 5.2 LTS. | Sollumz minimum 4.2 (extension); CI covers 4.0–5.2. |
| Sollumz | Preferences → Get Extensions → Repositories → `+` → `https://repo.sollumz.org/` → install "Sollumz" (stable) or "Sollumz (Development)". Or release `Sollumz.zip` → Install from Disk. | Updates in-app. Only one Sollumz version may be enabled. |
| PyMateria | Accept the install prompt (Windows only). | Native binary import/export of `.ydr .ydd .yft .ytd .ybn .ytyp .ymap`, Gen8 and Gen9. Without it: CW XML only. |
| Asset library (optional, 2.9+) | Preferences → Sollumz → Shared Assets directory; Sollumz Tools → Asset Library → **Build Asset Library** on the game folder (no custom RPFs in it; 25–60 min; `Pattern` is a case-sensitive regex, e.g. `^dt1_05`). Also register the folder under Preferences → File Paths → Asset Libraries. | Importing a ymap then instances every referenced archetype; no manual hunting for neighbours. |

## 1. Find the building (CodeWalker world view)

1. Selection mode **Entity**, right-click the building. In the selection panel note: **archetype name**,
   **YMap** (and its `RpfFileEntry` path), **lodLevel**, **lodDist**, and on the **LOD Hierarchy** tab
   `ParentIndex` / `NumChildren`. `ParentIndex -1` + `NumChildren 0` = `ORPHANHD` (safe to delete);
   anything else is in a LOD chain (use the archetype swap).
2. Find the chain: the HD ymap header names its `parent` ymap (typical: `X_strm_N` (HD) → `X` (LOD/SLOD1) →
   `X_lod` (SLOD2)). The name pattern is not reliable; read the `parent` field. (muto-atlas, measured)
3. **`hei_` twins:** search RPF Explorer for `hei_<ymapname>`. With mpheist content active, the `hei_` copy is the
   one that loads. Patch both or you get "fixed up close, still there from afar". (muto-atlas, measured)
4. The same ymap name exists in several RPFs (base + patchday). Take the file from the RPF path CodeWalker
   reports for the selected entity.
5. Selection mode **Collision**: click walls and floor around the door. Note the `.ybn` names; most areas have
   `name.ybn` and `hi@name.ybn` (`hi@` = high-detail set; the Sollumz tutorial says bullets use `hi@`, players
   the normal one). Edit both where you cut a doorway. `ma@` = procedural grass/litter, usually untouched.
6. Selection mode **Occlusion**: list box and model occluders inside the footprint and the ymap holding them.
7. Everything else in the footprint: decals (`*_decal*`, `*_ov`), overlays (`*_ovly*`), signs, ground,
   fences. Match by position/bounding box, not by name (overlay numbers do not match the building number;
   muto-atlas, measured).
8. Selection mode **Mlo Instance**: if a vanilla interior already exists there, pick another building or
   disable it client-side (`DisableInterior(id, true)`, `UnpinInterior(id)`; verify on your build).

## 2. Export from CodeWalker

- RPF Explorer → search the name → right-click → **Export XML** → `name.ydr.xml`.
- Double-click the model → Textures/Materials → **Save All Textures** into a folder named exactly like the
  asset (`dt1_05_build1/`) next to the XML. Sollumz loads textures from that folder automatically.
- Textures that live in a parent/shared dictionary (gtxd parent chain) are not in the model's `.ytd`; find them
  by name in RPF Explorer. Texture painting/re-packing: skill `gta-texture-editing`.
- With PyMateria you may instead **Extract** the binaries and import them directly.
- Export the `.ybn`(s) and the vanilla ymap too. Keep an untouched copy of every vanilla file.

## 3. Import into Blender

- Sollumz Tools → General → Import, or drag and drop (file handler accepts
  `.ybn .ydr .ydd .yft .ytyp .ytd .ymap .xml`).
- "Import To Asset Library" is a separate button since 2.9; if nothing appears, you hit that button.
- Import `.ydr` and `.ybn` first, then the `.ymap` (Sollumz tutorial). The drawable sits at the origin in
  drawable space; the ymap entity shows where it sits in the world.
- Units: 1 GTA unit = 1 m. Keep scene unit scale 1.0. Never scale the imported hierarchy.
- What you get: Drawable empty (`sollumz_drawable`) → Drawable Model meshes (`name.model`) with LOD meshes in
  Mesh Properties → Sollumz LODs (High/Medium/Low/Very Low) → embedded bounds and lights as children.
  `.ybn`: Bound Composite → GeometryBVH/Geometry → poly meshes and primitives.
- Missing textures: V → **Find Missing Files**, choose the texture folder.
- Wrong names on UV/colour layers make the model invisible in CodeWalker: UV = `UVMap 0`, `UVMap 1`; colour =
  `Color 1`, `Color 2` (Face Corner, Byte Color). Sollumz warns.

## 4. New exterior archetype (option A)

1. Duplicate the imported drawable (or import again) and rename the **Drawable root** to `abc_bldg_ext`.
   The exported file is named after the root object; a `.001` suffix is dropped on export but still breaks name
   lookups in scripts, so rename explicitly.
2. **Do not move the drawable root or its models.** The vanilla ymap entity transform must still fit.
3. Cut door/window openings in every LOD that is visible up close (High, usually Medium). Low/Very Low can stay
   closed. Methods:

   | Method | Do | Avoid |
   |---|---|---|
   | Manual (preferred) | Knife (`K`) or loop cut, delete faces, fill the reveal with Bridge Edge Loops | changing UVs of faces you keep |
   | Boolean | cutter box, modifier solver **`EXACT`** (`FAST` was renamed `FLOAT` in 5.x; `MANIFOLD` needs closed input), apply, then clean ngons | Boolean on the whole facade: vanilla meshes are non-manifold with split normals |

4. New reveal faces: UV from neighbours (Follow Active Quads / project), vertex colour copied from neighbouring
   exterior faces (red-dominant). Keep the exterior shader set.
5. Select the facade's window faces by material or shader (`glass`, `emissive`) and separate/delete them:
   [blender-automation.md](blender-automation.md). Every opening (door, garage door, window) is then filled with a
   **custom object built from scratch** (own archetype, door special attribute or glass shader, attached to the
   opening's portal) per skill `fivem-mlo-doors-windows`. Size openings to those objects: a few mm gap between
   leaf and frame collision; vehicle-sized for garage doors. Doors/windows only painted into the texture:
   `gta-texture-editing`.
6. Exterior collision: open the doorway in the vanilla world-space `.ybn` and `hi@.ybn` (cut polys or move
   them). These are vanilla overrides (same file name) and conflict with other maps editing the same file;
   check with `fivem_conflicttool` ([external-tools.md](external-tools.md)).
7. Decals/overlays on the cut facade: hide them the same way (archetype swap to an empty/edited model, or
   `z -= 600`), or they float in the opening.

### Option B: exterior inside the MLO (limbo)

- Only for `ORPHANHD` buildings. Remove the vanilla entity from your ymap copy, add `abc_bldg_ext` to the MLO as
  a limbo entity (counts toward the 12-entity limbo limit).
- The exterior now streams with the MLO instance (`lodDist` of the instance) and has no LOD → visible popping at
  distance. Give the MLO instance a large `lodDist` or keep a separate LOD entity in a normal ymap.

### LOD handling summary

| Situation | Do |
|---|---|
| HD entity has a LOD parent | archetype swap on the HD entity only; vanilla LOD/SLOD stay (they show the closed building far away, which is fine) |
| Your exterior is bigger than vanilla (added annex) | keep the swapped archetype inside the vanilla bounding box (entities outside a ymap's extents do not stream; muto-atlas) and put the annex in your own ymap/LOD entity; Sollumz Auto LOD (Decimate) for drawable LODs |
| You must hide a chained entity | `z -= 600` or archetype swap; never delete; never enlarge `entitiesExtents`/`streamingExtents` (muto-atlas measured map-wide collision loss) |
| SLOD2 merges many blocks | cannot be hidden per building; model surgery or accept it |
| `lodDist` | archetype `lodDist` for your exterior ≈ vanilla value; entity `lodDist -1` = use archetype value. Interior entities: `lodDist -1` (Sollumz default since 2.9) |

## 10. Placement, vanilla patch and manifest (CodeWalker project)

1. Project window → File → Open Folder (your resource `stream` folder) so your `.ytyp/.ydr/.ybn` load.
   Restart CodeWalker after dropping new files into an RPF.
2. **MLO placement ymap:** File → New → Ymap File; Ymap → New Entity; set Archetype = `abc_bldg_mlo`.
   Paste position/rotation (Sollumz: General → Object Location & Rotation Tools → copy). The MLO origin =
   composite origin, so place the instance where that origin belongs in the world.
3. MLO instance fields: **Num Exit Portals** = number of portals to `limbo` (CodeWalker does not compute it;
   Sollumz Maps has a calc button), Group ID 0, Floor ID 0, default entity sets as needed.
4. Select the ymap → **Calculate Extents** and **Calculate All Flags** → save as e.g. `abc_bldg_milo_.ymap`.
5. **Vanilla patch:** select the building entity with the project open (the ymap is added to the project),
   change only **Archetype** to `abc_bldg_ext`, save under the original file name into your `stream/`.
   Same for the `hei_` twin. Do not touch extents.
6. **Occluders:** in the vanilla ymap(s) holding occluders that overlap the building, delete or shrink them
   (selection mode Occlusion). Occluders hide whatever is behind them, including your interior seen through the door.
7. **Manifest:** add the `.ytyp` and every `.ymap` (yours + patched vanilla) to the project → Tools →
   **Manifest Generator** → Generate → save `_manifest.ymf` into `stream/`. Check it contains:

   ```xml
   <imapDependencies_2><Item><imapName>abc_bldg_milo_</imapName>
     <manifestFlags>INTERIOR_DATA</manifestFlags><itypDepArray><Item>abc_bldg</Item></itypDepArray></Item></imapDependencies_2>
   <Interiors itemType="CInteriorBoundsFiles"><Item><Name>abc_bldg_mlo</Name>
     <Bounds><Item>abc_bldg_mlo</Item></Bounds></Item></Interiors>
   ```

   (Shape copied from CodeWalker's generator source.) Files not in the project are not covered.

### Placing in Blender instead (Sollumz 2.9 Maps)

- Archetype Definition → MLO → **Create MLO Instance** (a collection instance pivoted at the MLO origin) →
  Maps panel: add a map group/container → **Add Object(s) as Entity**. Items not assigned to a container are
  skipped on export with a warning. Auto-partitioning puts interiors into a `_milo_` container.
- Sollumz writes the MLO instance rotation un-inverted and normal entity rotations inverted (same as CodeWalker).
  When writing ymap XML by hand, follow that asymmetry.
- Sollumz does not generate `_manifest.ymf`; use CodeWalker or write the XML above. FiveM is reported to accept
  an XML `_manifest.ymf` (rage-cli README; verify).
