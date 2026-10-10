# Tools, versions, licenses and "buy vs build" (checked 2026-10-09)

Contents: tool matrix · Marvelous Designer / CLO · Blender · Substance 3D · ZBrush · retopo tools · buy vs build (Fab, MetaHuman outfits, CC5, Daz, Mixamo-free) · license summary.

Prices are list prices seen in news coverage or vendor pages; re-check before buying. "(verify)" = not confirmed from a primary source.

---

## Tool matrix

| Tool | Version (2026-10) | Price | Use it for | Trade-off |
|---|---|---|---|---|
| **Marvelous Designer** | 2026.1 (Aug 2026); 2026.0 Apr 2026 | Personal 39 USD/mo or 280 USD/yr; Enterprise 199 USD/mo or 2 000 USD/yr (floating; 2 300 incl. Linux); Indie (apply: ≥2 employees, <500 k USD revenue); Student 99 USD one-off (verify) | Pattern-based garments, drape/sim, fold detail, USD to MetaHuman, LiveSync to UE | Sim mesh needs retopo; retopology deletes sewing; Python API reportedly Enterprise-tier |
| **CLO** | same engine, fashion-oriented | similar | Same as MD plus DXF-AAMA/ASTM patterns, tech packs | Only worth it if the garment must also be manufactured. For games pick MD |
| **Blender** | 5.2 LTS (14 Jul 2026, supported to Jul 2028); 5.1 (17 Mar 2026) | free (GPL) | Cleanup, retopo, Shrinkwrap/Surface Deform fitting, cloth sim, weight transfer, LODs, FBX/USD export, scripting | Cloth sim is drape-only (no patterns/ease); FBX exporter is still the Python add-on (`io_scene_fbx` 5.15.0 in the 5.2 branch); 5.2 node-based cloth is experimental |
| **Substance 3D Painter** | 12.0.2 (Mar 2026; 12.1 beta adds OpenPBR) | Texturing plan 24.99 USD/mo or 249.88 USD/yr (Painter + Designer + Sampler + Assets) | Wear, dirt, seams, stitch stamps, baking, export presets, Python export API | No Substrate/fuzz export preset found; build a custom output template |
| **Substance 3D Designer** | 16 (May 2026) | in the plan | Procedural weaves, tileable fabric normals/roughness | Learning curve; use the Assets library fabrics first |
| **Substance 3D Sampler** | 6 (May 2026) | in the plan | Photo/scan → tileable fabric material (Image to Material) | Needs flat, evenly lit fabric photos |
| **ZBrush** | 2026.2 (Apr 2026); rental only | 49 USD/mo or 399 USD/yr | Fold sculpting, seam/stitch detail, high-poly for bakes | Optional; Blender sculpt covers 80 % for clothing |
| **Character Creator 5** | 5.x (Aug 2025) + Auto Setup All-in-One 2.0 (Dec 2025: UE 5.5–5.7) | paid + content | Transfer Skin Weights templates, Conform, Hide Body Mesh, UE export | UE 5.8 support unconfirmed; CC content licenses |
| **Quad Remesher** (Exoside) | 1.4.1 download; 1.3 docs | Pro 109.90 USD perpetual, Indie non-commercial 59.90, 3-month 15.99 (page undated) | Auto quad retopo of MD/sculpt meshes | Blender 5.2 compatibility unconfirmed (forum question unanswered) |
| **Instant Meshes** | wjakob, BSD-3 | free | Auto retopo for NPC garments | No edge-flow control; bundled in the QuadMend add-on |
| **Blender Remesh / QuadriFlow** | built in | free | Quick quad remesh for background garments | Worse flow than Quad Remesher |

Free stack that works: Blender 5.2 + Instant Meshes/QuadriFlow + Blender texture paint or Substance trial + Fab/Quixel fabric materials (Quixel is on Fab; check each item's license).

---

## Marvelous Designer / CLO

**What changed recently**
- 2026.0: 3D Pencil (draw outlines on the avatar → patterns), Lacing tool, scale patterns while keeping 3D shape, **EveryWear Template-Based Rigging (Beta)** that auto-adds bones to garments, glTF, toon shader.
- 2026.1: Seamline Ripping (Beta), **Brush Pinching** (paint wrinkles freehand), Pinching Simulation Override (local sim params while pinching), avatar blend-shape animation recording.
- Linux edition + **Python API** since the 2025.1 era (Sept 2025). Plug-ins (`.py`) are registered in *Plugins > Plug-in Manager*. Coverage at launch said the API ships only with the Enterprise plan; a community MCP reports it working on Windows MD 2026.0.315 "with Python plug-ins". Treat the tier as (verify) and ask sales before planning automation on a Personal plan.

**License facts (support articles, as quoted by search results)**
- Freelancers may use **Personal**; studios, game companies and research companies must buy **Enterprise**. A Personal license bought with a company card or company e-mail can be reclassified as corporate and terminated.
- Older Personal terms allowed selling or distributing your original works. The current EULA text could not be fetched (verify). Keep a screenshot of the terms you accepted.
- Export formats are not license-restricted (OBJ/FBX/USD/Alembic/glTF available in Personal).

**Export settings (FBX/OBJ)**
| Option | Pick | Note |
|---|---|---|
| Thin / Thick | **Thin** for the game mesh. Thick only for bakes/preview | Thick duplicates the shell; thickness needs quad mesh |
| Weld / Unweld | **Weld** | Unweld = split seam vertices = shading seams and no clean retopo |
| Single / Multiple Objects | Single for one material; Multiple when panels need separate materials | |
| Unified UV | On for one texture per garment | Lay out UVs in MD's UV editor first; MD supports a UDIM grid layout |
| Unit | **cm** | mm is a classic default trap |
| Mesh | Triangle for sim fidelity; Quad (Remesh) for the game mesh | Remesh last; it deletes sewing. Use *Remesh All (Replace)* and keep the triangle project |

**Retopology in MD**: right-click pattern in the 3D window → *Remeshing to Retopology (Selected)* with a target polygon count. Community reports: remeshed layers can "fall apart" and lose sewing/internal lines. Pipeline: finish fit → save → remesh on the copy → export quads → finish retopo in Blender.

**MD/CLO → MetaHuman USD (Outfit Asset path)**
- Versions: MD 2025.2+ for UE 5.6+; MD 2025.0 only for UE 5.4; UE 5.5 unsupported for Chaos Cloth data (regular meshes still work).
- UE prerequisites: *MetaHuman Creator Core Data* installed via the Launcher; keep the MetaHuman packaging paths setting; create `/Game/Outfits/<OutfitName>/` with the matching subfolder (asset validation checks it).
- Body: export the MetaHuman as **Combined Skeletal Mesh** (MetaHuman Creator menu) and import it into MD/CLO as the avatar. CLO ships `Apose` (for fitting the arms) and `Default_Pose` (arms bent); apply **`Default_Pose` before the USD export** or the UE USD import misaligns. MD builds older than 2024.0.173 give "No matching avatar" when applying these poses.
- Export USD from MD/CLO (geometry, materials, sim metadata, panel structure).
- UE: import USD (defaults) → *Physics > Cloth Asset* from the static mesh → Dataflow graph keeps **USD Import → Transfer Skin Weights (target = render mesh, type = skeletal mesh, source = combined skeletal mesh) → Remesh (→ optional Remesh LOD2) → Cloth Asset Terminal**.
- Outfit Asset: set *Evaluate Dataflow Graph* = Manual, add the Cloth Asset as a **Sized Outfit Source** with a size name, enable *Sized Outfit*, drag the combined skeletal mesh into the source body slot. Each size's source body is one merged body+head skeletal mesh; the garment must be the same representation in every size; raise interpolation points for quality, or add a size if a body still fits badly.
- Test in MetaHuman Creator: *Hair & Clothing > Outfit Clothing* → drag in → **Wear** → change *Head & Body* sliders. *Source Size Override* + *Refresh Preview* to force a size. A `WI_<name>` wardrobe item with the *MetaHuman Outfit Pipeline* exposes material parameters for colour changes.
- 5.8: the UE release notes mention non-destructive round-trip editing with CLO/MD, USD constraints and cloth attributes. The MD/CLO support articles still describe a one-way flow; treat round-trip as (verify).
- The remaining UE steps (sim stripped by assembly, body mask, LODSync) are in `ue5-character-creation-clothing`.

**LiveSync** (Fab plugin, 2.x): MD/CLO ↔ Unreal Editor without file exports; MetaHumans and any skeletal mesh can go to MD for fitting and back. MD states that support for the parametric MetaHuman body is "in progress" (undated). For engine-side simulation MD itself recommends USD + Chaos Cloth rather than LiveSync.

**MD vs CLO**: shared engine and file formats. CLO adds DXF-AAMA/ASTM import/export, grading, BOM/tech packs. MD targets CG/games. Pick MD unless the garment goes to a factory.

---

## Blender 5.2 notes for garments

- FBX **import** is the new native importer; FBX **export** is still the `io_scene_fbx` Python add-on, so the operator options in `blender-automation.md` apply. `bake_space_transform` is marked "experimental, known to be broken with armatures" in the add-on itself; leave it off.
- Collada was removed in 5.x. Use FBX/USD/glTF.
- Modifiers for fitting: Shrinkwrap (`wrap_method`: `NEAREST_SURFACEPOINT`, `PROJECT`, `NEAREST_VERTEX`, `TARGET_PROJECT`; `wrap_mode`: `ON_SURFACE`, `INSIDE`, `OUTSIDE`, `OUTSIDE_SURFACE`, `ABOVE_SURFACE`; `offset`), Surface Deform (`target`, `falloff`, `strength`, bind with `bpy.ops.object.surfacedeform_bind`), Solidify (`thickness`, `offset`, `use_even_offset`, `use_rim`), Data Transfer (vertex groups), Decimate (`decimate_type='COLLAPSE'`, `ratio`, `vertex_group`, `use_collapse_triangulate`, `use_symmetry`).
- Cloth: object collision `distance_min` (range 0.001–1 m; default 0.015 m is far too large for garments), `collision_quality` (UI 1–20), `self_distance_min` (0.001–0.1), `quality` (UI 1–80), `use_pressure` + `uniform_pressure_force`, `vertex_group_shrink` + `shrink_min/max` for cinching.
- Add-ons seen for garment fitting: *Dress Fit* (nearest-surface push-out with a 2 mm gap, weight copy; Blender 4.0+), *ShellFit* (volume-aware fitting + weights; 4.5+), *QuadMend* (Instant Meshes + QuadriFlow), *Fast Remesher*. Not evaluated; paid.

---

## Substance 3D for fabrics

- Painter project: **Normal map format = DirectX** (UE expects green-down). Bake from the high/thick mesh: normal, world-space normal, AO, curvature, position, thickness, ID.
- Export: the built-in *Unreal Engine 4 (Packed)* preset still works for UE5 (Base Color, Normal, ORM = R:AO, G:Roughness, B:Metallic). Add a custom output template with **Fuzz/Sheen** (grayscale) and **Opacity** channels for Substrate cloth; no official Substrate preset was found.
- Fabric sources: Substance 3D Assets (included in the plan), Sampler *Image to Material* from your own photos (shoot flat, diffuse light, include a scale reference), Designer for custom weaves.
- Python: `substance_painter.export.export_project_textures(config)` lets Claude run exports from a JSON config; texture painting itself stays manual.

---

## Buy vs build

| Source | What you get | Fit to a MetaHuman | License gotcha (details: `ue5-character-creation-clothing`) |
|---|---|---|---|
| **Fab: MetaHuman parametric outfit** (Outfit Asset) | Resizable garment, usually several source bodies, often modular | Best. Still test your stroke poses; Source Size Override if a body clips | Fab Standard (Personal/Professional same rights); UE-Only flag irrelevant inside UE; NoAI flag |
| **Fab: fixed MetaHuman clothing** (`WI_*`, "All MH bodies") | Skeletal meshes per compatibility body | Only the 18 compatibility bodies; parametric bodies clip | Same |
| **Fab: "Rigged to Epic skeleton"** | Manny/Quinn-skinned garments | Needs refit + re-skin to the MetaHuman body (this skill's Blender route) | Check UE4 vs UE5 skeleton |
| **ArtStation/Gumroad MD projects** (`.zprj`) | Patterns + sim setup | Re-drape on your body in MD, then full pipeline | Seller license; often "personal, one commercial project" tiers |
| **MetaHuman Creator wardrobe** (built-in outfits) | Parametric outfits that resize with the body | Good, limited catalogue, cloth sim stripped at assembly (5.8 reports) | MetaHuman EULA (in-UE and other engines allowed; no AI training) |
| **Character Creator 5** | Garment import → *Transfer Skin Weights* template (Cloth/Gloves/Shoes/Hair/Cloak), *Lateral Partitioning* for sleeves, *Conform*, *Hide Body Mesh* / *Delete Hidden Mesh* on export | Fits CC bodies; to MetaHuman only via CC5 HD → UE mapping | Export rights; Extended license for mass outputs; Auto Setup version must match UE |
| **Daz dForce outfits** | Simulated at Daz pose, exported as skinned meshes | Fits Genesis only; retarget + refit | Interactive License per product; dForce hair does not transfer; morph export unreliable (forum) |
| **Mixamo-free paths** | Not a clothing source. For rig-free prototypes use Manny + Fab garments | – | – |

Authoring custom MetaHuman outfits yourself: the Outfit Asset path above (three accepted inputs: FBX render mesh only, USD from MD/CLO with sim + render mesh, or render mesh + hand-made sim mesh). Body hiding = *Body Hidden Face Map* texture in the MetaHuman body UV layout (paint it in the DCC from the body UVs; one mask per character; never fully black).

---

## License summary (what matters for a solo dev shipping a game)

| Thing | Rule |
|---|---|
| Marvelous Designer Personal | OK for a freelancer/sole developer; not for a company; output distribution per current EULA (verify text) |
| Marvelous Designer Python API | Enterprise at launch (verify for 2026) |
| Substance 3D Texturing plan | Commercial use allowed; Assets library content under Adobe's terms |
| Blender, Instant Meshes, QuadriFlow | GPL / BSD; your output is yours |
| Quad Remesher Indie | Non-commercial only; buy Pro for a shipped game |
| Fab Standard | Commercial in any engine except UE-Only items; never redistribute sources |
| MetaHuman | UE EULA + MetaHuman addendum: use in UE and elsewhere, sell on Fab, no generative-AI training |
| CC5 content, Daz | Export rights / Interactive License before anyone else gets a build |
