# Sources (accessed 2026-10-10)

Legend: **D** = read directly (source code, cloned repo, bpy introspection, own headless test);
**S** = search-result snippet only (docs.blender.org, blender.org, daz3d.com, imeshh.com and most tutorial sites were
blocked from the sandbox, HTTP 403/DNS); **T** = own measurement with `scripts/sf_selftest.py` or probe scripts.

## Measurements (T)

| What | Backs up |
|---|---|
| `scripts/sf_selftest.py` on bpy 5.2.2 LTS (Python 3.13, `uv pip install bpy==5.2.*`) and bpy 4.5.14 LTS (Python 3.11) | every [T] number: pillow ratios, drape gap/friction/air damping/time, curtain stretch, tufting depth, LOD tris, GN input API, bake vs step vs jump |
| Probe sweeps (pressure × shrink × bending × resolution, BOX/ROUND tuning, collision distance, friction, air damping, Solidify even/clamp, fold lift) | presets and tables in pillows-cushions.md, beds-blankets.md |
| bpy introspection of `ClothSettings`, `ClothCollisionSettings`, `CollisionSettings`, `PointCache` defaults; Principled BSDF inputs on 4.5.14 and 5.2.2 | default values quoted (mass 0.3, quality 5, distance 0.015, outer 0.02, friction 5, Subsurface Scale 0.05 → 0.005, Thin Wall 5.2 only) |
| Cycles renders of pillows, bed, tufting, materials (review only, not shipped) | visual checks of the presets |

## Source code (D)

| Source | Backs up |
|---|---|
| github.com/blender/blender, branch `blender-v5.2-release` @ d13f752: `makesrna/intern/rna_cloth.cc` | Quality = steps per frame, UI 1–80; shrink range and `shrink_min` setter raising `shrink_max`; pressure, target volume, pressure scale (kPa), pressure vertex group, internal springs descriptions |
| same: `editors/physics/physics_pointcache.cc` | `PTCACHE_OT_bake` poll needs a `point_cache` context member; exec path bakes synchronously (`BKE_ptcache_bake`), invoke starts a job |
| same: `modifiers/intern/MOD_collision.cc` | collision modifier stores world positions per frame, resets when time goes backwards |
| same: `intern/cycles/kernel/svm/wave.h` | Wave BANDS `n = p.x * 20` → period 2π/(20·Scale) |
| github.com/Sollumz/Sollumz `main` @ 07d6a49 (2026-10-10): `ydr/operators/materials.py`, `ydr/cloth_env.py`, `ydr/operators/lod_tools.py`, `ybn/collision_materials.py` | auto shader choice normal_spec/normal/spec/default; env cloth one per fragment, `CLOTH_ENV_MAX_VERTICES = 1000`; Auto LOD methods/defaults; collision material indices |
| szio 1.4.0.dev1 wheel (PyPI), `gta5/Shaders.xml` | `normal_spec`, `normal_spec_detail`, `*_tnt`, `cloth_*` (`IS_CLOTH`) parameters and defaults |
| github.com/dexyfex/CodeWalker `CodeWalker.Shaders/BasicPS.hlsl` | detail normal: UV × `detailSettings.zw` (and × 3.17), × `detailSettings.y`, masked by spec alpha |
| github.com/B7Kompirine/muto-atlas @ 51d9296 (MIT code) `skills/fivem-assets/trunk/tool-pitfalls.md`, `sources/external-tools.md`, `data/collision_materials.tsv` | UV-less mesh → 3 verts per triangle (~4× file) in Sollumz 2.9; auto split at 65 535 verts; rottweiler 11 303 tris; 150 k-tri collision note |

## Skills and repositories (D)

| Source | Backs up |
|---|---|
| This repo: `blender-python-pitfalls`, `clothing-creation-pipeline`, `fivem-mlo-creation`, `gta-texture-editing`, `scenario-blender-*`, `blender-furniture-modeling` (sibling, `make_bed_frame` → `obj["mattress"]`), `ue5-performance-optimization` | links instead of duplication; Nanite do/don't; MLO limits; texture formats; FBX settings |
| scenario-labs/skills @ f6f8ab7 `scenario-blender-geometry-nodes` (procedure H), `scenario-blender-texturing-shading` (expert-notes: bump distance ~0.001, strength 0.1–0.2 for fabric) | GN cloth option; bump values |
| Repos in external.md §1 (licenses read from LICENSE files, dates from `git log`) | skill survey and verdicts |

## Web (S = snippet only)

| URL | Backs up |
|---|---|
| https://hpcl.daz3d.com/blog/back-to-basics-modeling-a-blanket-and-pillow-using-cloth-simulations-in-blender (and mirrors) | common tutorial pillow recipe: pressure 1, quality 5, gravity 0, self-collision distance 0.001, billow by frame 15–20; blanket: quality 5, collision quality 5–10 |
| https://blender.stackexchange.com/q/234022 (via mirror backiee.wasmer.app) | user report: raising quality steps and resetting collider Outer Thickness to 0.02 fixed a penetrating blanket |
| https://blenderartists.org/t/how-to-make-a-top-cover-quilt-on-a-bed/681978 | usual method: simulate thin, add thickness with Solidify after |
| https://docs.blender.org/manual/en/2.92/physics/cloth/settings/collisions.html | quality reduces tears/penetration; collision distance trade-off; self-collision normally on |
| https://projects.blender.org/archive/blender-archive/commit/541d0fdba61a9c99612f7532207d5ce704f10b43 | pressure vertex group added; shrink range unlocked to negative values |
| https://wiki.blender.org/release_notes/2.82/ , cgchannel / foxrenderfarm 2.82 coverage | cloth internal air pressure and internal springs added in 2.82 |
| https://wiki.blender.org/release_notes/4.0/shading/ | Sheen = new microfiber model, top layer above emission and coat |
| https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/principled.html | Sheen Weight/Roughness/Tint meanings (no numeric fabric values) |
| https://www.blenderguru.com/posts/couch-william | couch series; cushion made with cloth pressure |
| https://www.blendernation.com/2020/06/25/creating-a-tiled-chesterfield-cushion-with-the-new-cloth-filter-in-blender-2-9/ , https://www.blendernation.com/2017/04/05/model-quiltedtufted-leather/ , https://imeshh.com/blog/blender-28-pro-sofa-modeling-guide-part-1-square-chesterfiel | tufting by modeling/cloth filter; no GN tufting tutorial found |
| https://versluis.com/2016/05/how-to-create-a-pillow-in-marvelous-designer , https://cgworld.jp/regular/202605-cgw330-tr09.html , https://www.ronenbekerman.com/?p=22060 | MD pillow pressure ~20, normals outward, gravity off; Shrinkage Weft/Warp; rhomboid tufting by sewing + pins |
| https://shift4cube.gumroad.com/l/PillowMaker , https://superhivemarket.com/products/clothmaster | pillow add-ons (not tested) |
| https://forum.cfx.re/t/virtual-physical-memory-for-assets/1689728 , https://forum.cfx.re/t/free-eng-oversized-assets-logger/5224938 | FiveM oversized-asset tiers (< 16 MiB none … > 64 MiB red), textures as main cause |
| https://dev.epicgames.com/documentation/unreal-engine/nanite-technical-details | Nanite fallback mesh used for collision, HWRT, non-Nanite paths; transparent not supported, masked costs more |
| https://dev.epicgames.com/documentation/fab/licenses-and-pricing-in-fab | Fab Standard vs CC-BY, Personal tier < 100 k USD, NoAI only on Standard |
| https://licenseorg.com/guide/3d-assets/ambientcg , https://app.cinevva.com/guides/free-textures-hdris-materials , https://www.cryengine.com/asset-db/product/janbostl/sofa-03 | ambientCG and Poly Haven CC0 (Poly Haven statement quoted on a mirror) |
| https://skills.sh/arjun988/blender-skills/cloth-sim , https://openskillindex.com/skills/a5c-ai-babysitter-cloth-simulation | located the two cloth skills, then read from the cloned repos |
