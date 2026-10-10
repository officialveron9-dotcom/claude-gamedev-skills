# Sources (all accessed 2026-10-10)

Method: GitHub repositories were cloned (`GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1`) and read directly.
forum.cfx.re, blender.org, projects.blender.org and most community sites were blocked or returned nothing
useful; items seen only in search-engine summaries are marked **(search snippet)**. Tests: `bpy` 4.5.14 LTS and
5.2.2 LTS wheels with Sollumz `main` loaded headless (scripts kept in the session scratchpad, results in
[blender-automation.md](blender-automation.md)).

## Read directly (source code / docs)

| Source | Commit / version | Backs up |
|---|---|---|
| https://github.com/Sollumz/Sollumz | `main` 07d6a49 (2026-10-10, 2.9.0-dev); tag `v2.9.0` = 389bd9b (2026-08-04); history back ~600 commits | version, Blender min 4.2 (`blender_manifest.toml`), CI matrix 4.0–5.2 (`.github/workflows/ci.yml`), export settings (Native/CWXML, Gen8/Gen9, gen8/ gen9/ subfolders, `use_custom_settings`), PyMateria dependency (Windows, Cfx wheel index), operator ids (443 registered), room/portal/MLO/entity/archetype flag names (`ytyp/properties/flags.py`), room/portal/entity properties and defaults (`ytyp/properties/mlo.py`, `ytyp.py`), limbo 12-entity limit (#1202, #1248), exit-portal calc, portal corner sorting and arrow formula, Set Bounds From Selection subtracting asset location, MLO instance rotation asymmetry (`ymap_next/ymapexport.py`), collision materials/indices, flag presets incl. Stair plane/mesh, default flag preset auto-applied since 2.9.0 (commit 90c5c70), room ID 0–31, light flags/time flags/intensity×500, light presets, entity lodDist -1 default (995d88d), ynv import-only, no `_manifest.ymf` support |
| https://github.com/Sollumz/wiki | ab7338c (2026-09-25) | Creating Interiors tutorial (picking, importing from CodeWalker, modelling, texturing incl. vertex colour channels, collisions incl. `hi@`, ytyp rooms/portals, export, ymap), FAQ (manifest, flag preset, vertex paint green/red, rain inside, first-person disappearing, invisible in CodeWalker, Import To Asset Library), features, installation (repo.sollumz.org), collisions, archetype flags, maps/entities/LOD hierarchy/occluders/TCM/partitioning, asset libraries, light flags, Gen9 conversion (CodeWalker Dev48 Asset Converter, `ERR_GFX_STATE`, 128 limit) |
| https://pypi.org/project/szio/ (wheels 1.3.0.dev9, 1.4.0.dev1) | — | Native providers: Gen9 writers for ydr/ydd/yft/ytd/ytyp, shared writer for ybn/ymap; CWXML Gen9 shader defaults; MIT licence |
| https://github.com/dexyfex/CodeWalker | 485d56b (2025-04-11) | Manifest Generator output (`INTERIOR_DATA`, `Interiors` → bounds = MLO name), interior ybn "in local space" (`Space.cs`), MLO instance vs entity quaternion inversion (`YmapFile.cs`), `CMloInstanceDef`/`CMloRoomDef`/`CMloPortalDef` fields, `numExitPortals` typed by hand, selection modes (Collision, Occlusion, Mlo Instance), Gen9 game folder (`gta5_enhanced.exe`), MIT-style `Notice.txt` |
| https://github.com/citizenfx/fivem-docs | c2b2125 (2026-10-01) | Assets guide parts 1–9 (CodeWalker Dev48, Blender 4.5.4, Sollumz install + PyMateria prompt, export/import, ytyp, ymap + Calculate Extents/Flags + Manifest Generator + fxmanifest `this_is_a_map`, collision editing, LOD parenting, doors, Sollumz 2.9 asset library); `this_is_a_map` semantics; `DLC_ITYP_REQUEST` = PERMANENT_ITYP_FILE; `TIMECYCLEMOD_FILE`; `increase_pool_size` limits |
| https://github.com/citizenfx/fivem `ext/native-decls` | 0105063 (2026-10-09) | CFX interior natives (`SetInteriorRoomFlag`, `GetInteriorRoomIndexByHash`, `SetInteriorRoomTimecycle`, `SetInteriorPortalFlag`, `SetInteriorProbeLength` 4-unit probe text, getters), declared `game: gta5` |
| https://github.com/B7Kompirine/muto-atlas | 51d9296 (2026-09-13) | community-measured: LOD chain stats and "delete breaks chain", `hei_` twins, do-not-touch extents, `z -= 600`, ymap props culled inside MLOs, MLO entity flags 18350080, vanilla room flags 111/99/107/96, interior vertex colour R = 0, hidden-light export bug, `use_custom_settings`, `trees_normal` black inside; tool notes (VichoTools, Arbolito, ht_mlotool) |
| https://github.com/VIRUXE/rage-cli | bcefaa3 (2026-10-02) | navmesh cells/interiors have no own navmesh, `navmesh build`, XML manifests accepted by FiveM (claim) |
| https://github.com/escobarv110/Rage-Tools | 3988ab8 (2026-10-09) | MLO Creator/MCP features, licence, own limitations |
| https://github.com/escobarv110/RAGE-Evo | de469b6 (2026-09-29) | 3ds Max suite features, no licence file |
| https://github.com/kkMihai/fivem_conflicttool | b75bd5a (2026-10-06) | conflict scanner features, GPL-3.0 |
| https://github.com/byfredQC/mlo-light-manager | 074eb54 (2026-10-06) | live light tuning add-on, GPL-3.0 |
| https://github.com/EnesiEsen/blender-toolkit | 3569ce4 (2026-10-08) | FiveM Toolkit MLO builder, UE5 Bridge direction, GPL-3.0 |
| https://github.com/ahujasid/mcp-for-blender (cloned as blender-mcp) | 7a0373e (2026-10-06) | version 2.1.9, port 9876, tool list, MIT, telemetry opt-in |
| https://github.com/leminhhuy113/fivem-pro, https://github.com/bworthy89/fivem-server-development, https://github.com/digitARTI/Sollumz-MCP | ae642cb / c76c1e9 / e662600 | existing skills/MCP verdicts |
| GitHub repository search (API) "sollumz", "sollumz mcp", "codewalker mcp", "fivem mlo claude skill", "unreal gta5 ydr" | — | tool inventory; no Unreal → GTA exporter |
| Repo skills `fivem-gta5-enhanced` (`references/assets-and-streaming.md`), `fivem-server-setup` (`references/streaming-assets.md`), `fivem-mlo-doors-windows` (blender-modeling plugin), `blender-modeling/EXTERNAL.md` | 2026-10-06/10 | `stream_enhanced` rules, Alchemist, Gen9 pitfalls, streaming rules, portal arrow outward / CCW from outside (vanilla `v_int_66`), Blender MCP setup |
| Local tests with `bpy` 4.5.14 / 5.2.2 | 2026-10-10 | all snippets in `blender-automation.md`; Boolean solver enums and error text; `mesh.separate` headless failure; stale `matrix_world`; export selection behaviour; identical gen8/gen9 CW XML for `normal.sps` |

## Search snippets only

| Source | Backs up |
|---|---|
| https://www.blender.org/lab/mcp-server/, https://projects.blender.org/lab/blender_mcp via strayspark.studio and a2a-mcp.org summaries **(search snippet)** | official Blender Lab MCP: v1.0.0 2026-04-27, Blender 5.1+, TCP bridge |
| https://gamedev.net/news/2955-blender-lab-activity-report-q1-2026/ **(search snippet)** | Blender Lab MCP exists |
| https://xgamingserver.com/blog/how-to-install-mlos-in-fivem/ **(search snippet)** | common MLO stream layout, `DLC_ITYP_REQUEST` usage in packs |
| https://fivemx.com/blog/how-to-create-fivem-mlos **(search snippet, vendor)** | general MLO workflow; nothing beyond the Sollumz wiki |
| https://fivemx.com/gta-news/codewalker-update-gtav-enhanced-assets-support **(search snippet)** | CodeWalker Gen9 asset converter |
| Web searches for "CodeWalker dev49/dev50", "mloFlags 1024", "FiveM navmesh ynv MLO", "Unreal to GTA V ydr exporter" | no usable results (CodeWalker newer than Dev48 not confirmed; "Allow Run" behaviour unconfirmed) |
