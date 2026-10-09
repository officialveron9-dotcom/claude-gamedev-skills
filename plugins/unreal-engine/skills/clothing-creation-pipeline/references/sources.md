# Sources (accessed 2026-10-09)

Legend: **D** = read directly (cloned repo/source file or fetched page); **S** = search-result snippet only (page itself unreachable from this environment: `support.marvelousdesigner.com`, `developer.marvelousdesigner.com`, `dev.epicgames.com`, `docs.blender.org`, `blender.org`, `projects.blender.org`, `cgchannel.com` were blocked); **N** = not verified / practice.

## Marvelous Designer / CLO
- S https://www.marvelousdesigner.com/support/news/view/448aa11bc06d4b91a63668ca1d12a96e, https://www.cgchannel.com/2026/08/clo-virtual-fashion-releases-marvelous-designer-2026-1/, https://80.lv/articles/new-marvelous-designer-update-lets-artists-rip-pinch-shape-fabric-like-never-before/, https://digitalproduction.com/2026/04/15/marvelous-designer-2026-0-adds-3d-pencil-and-lacing/: MD 2026.0 (Apr 2026: 3D Pencil, Lacing, EveryWear rigging beta, glTF) and 2026.1 (Aug 2026: Seamline Rip beta, Brush Pinching, sim override, blend-shape animation).
- S https://developer.marvelousdesigner.com/ , https://developer.marvelousdesigner.com/register.html, https://www.cgchannel.com/2025/10/marvelous-designer-is-now-available-for-linux/, https://en.prnasia.com/releases/apac/clo-launches-marvelous-designer-for-linux-expanding-support-for-professional-pipelines-505079.shtml: Python API (in-app, plug-in manager, batch import/export, sim params), Linux edition, API reported as Enterprise-tier.
- S https://support.marvelousdesigner.com/hc/en-us/articles/47358269350041 (license tiers), https://support.marvelousdesigner.com/hc/en-us/articles/47358297616153-What-is-the-difference-between-Personal-and-Enterprise-License (freelancers Personal, companies Enterprise, corporate-card reclassification), https://www.cgchannel.com/?p=171883 (Nov 2025 prices: Personal 39/280, Enterprise 199/2 000/2 300, Indie criteria). Current EULA text on output distribution: **N**.
- S https://support.marvelousdesigner.com/hc/en-us/articles/52699135975705-Marvelous-Designer-to-MetaHuman-USD-Garment-Integration-Workflow (+ja/zh versions), https://support.clo3d.com/hc/en-us/articles/53322960594969 : MD 2025.2 ↔ UE 5.6+, 2025.0 ↔ 5.4, 5.5 unsupported; Core Data; `/Game/Outfits/`; Dataflow nodes USD Import → Transfer Skin Weights → Remesh → Terminal; Outfit Asset sized source steps.
- S https://support.clo3d.com/hc/en-us/articles/32152615561369-Open-MetaHuman-Body-Types : `Apose`, `Default_Pose` (arms bent) required for UE USD import; "No matching avatar" below 2024.0.173.
- S https://support.marvelousdesigner.com/hc/en-us/articles/47358232885017 , https://www.versluis.com/2015/03/how-to-export-a-garment-from-marvelous-designer/ : FBX export options Thin/Thick, Weld/Unweld, Single/Multiple, Unified UV, mm default trap.
- S https://support.marvelousdesigner.com/hc/en-us/articles/47358258770073-Remeshing-to-Retopology-Selected-ver-5-1-4 , https://support.marvelousdesigner.com/hc/en-us/articles/47358257345305-Does-Marvelous-Designer-support-the-quad-mesh , community posts 48283124609305 / 48272815935641: retopology removes sewing, Remesh All (Replace).
- S https://support-connect.clo-set.com/hc/en-us/articles/45304300058137-What-is-LiveSync , https://www.fab.com/listings/e1ecc882-d6c4-4928-b880-5f66d1590bba , https://www.marvelousdesigner.com/ko/support/news/view/c68de71f63fa47bb9464917bc07a9e95 : LiveSync 2.x, parametric body support in progress, USD + Chaos Cloth recommended for engine sim.
- S https://support.clo3d.com/hc/en-us/articles/115012666547 , https://www.unrealengine.com/news/tailoring-for-metahumans-clo-and-marvelous-designer-to-unreal-engine-demo : CLO vs MD, Epic April 2026 webinar.

## Epic / MetaHuman
- S https://dev.epicgames.com/documentation/metahuman/creating-parametric-clothing-for-metahuman , https://dev.epicgames.com/documentation/metahuman/building-an-outfit-asset-in-unreal-engine , https://dev.epicgames.com/documentation/metahuman/testing-and-configuring-your-parametric-outfit-asset , https://dev.epicgames.com/documentation/unreal-engine/creating-parametric-clothing-for-fab , https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ChaosSizedOutfitSource : three input workflows, ≥2 source bodies, merged body+head source mesh, same garment representation per size, interpolation points, Wear/Source Size Override/Refresh Preview, `WI_` wardrobe item.
- S https://www.metahuman.com/news/metahuman-5-8-is-now-available : 5.8 (Collections, Mesh to MetaHuman arbitrary topology, MIT core libraries).
- S https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UMaterialExpressionSubstrateSlab- : FuzzAmount / FuzzColor / FuzzRoughness.
- Everything else Epic-side (import options, Hidden Face Map, LODSync, Fab/MetaHuman EULA): see `ue5-character-creation-clothing/references/sources.md`.

## Blender
- D `github.com/blender/blender` branch `blender-v5.2-release` (sparse clone): `scripts/addons_core/io_scene_fbx/__init__.py` (add-on 5.15.0; export option names, defaults, `bake_space_transform` warning), `source/blender/editors/object/object_data_transfer.cc` (operator properties), `source/blender/editors/object/object_vgroup.cc` (smooth/clean/limit_total properties), `source/blender/makesrna/intern/rna_modifier.cc` (Shrinkwrap/SurfaceDeform/Solidify/Decimate/DataTransfer identifiers and enums), `rna_cloth.cc` (collision/pressure property names and ranges), `source/blender/editors/io/io_usd.cc` (USD export options).
- S https://www.blender.org/download/releases/ , https://www.blender.org/releases/5-2/ , https://www.blendernation.com/blender-5-1-released , https://gamefromscratch.com/blender-5-2-lts-released/ : 5.1 (17 Mar 2026), 5.2 LTS (14 Jul 2026, node-based physics experimental).
- S https://docs.blender.org/manual/en/5.2/files/import_export/fbx.html : FBX export via add-on; https://www.beamng.com/posts/1961656/ : Collada removed in 5.x.
- S https://docs.blender.org/manual/en/dev/modeling/modifiers/modify/data_transfer.html : Nearest Face Interpolated definition.
- S https://booth.pm/en/items/8930466 (Dress Fit), https://80.lv/articles/fix-body-clothing-clipping-in-blender-with-this-tool/ (ShellFit), https://superhivemarket.com/products/quadmend/docs (QuadMend bundles Instant Meshes BSD-3): add-ons, not evaluated.

## MCP servers and skills (all D unless noted)
- D https://github.com/ahujasid/mcp-for-blender (LICENSE MIT, README, TERMS_AND_CONDITIONS.md Aug 2026, pyproject 2.1.9, addon.py bl_info 1.8 / Blender 3.0+, server.py tool list).
- D https://github.com/Laboon2501/MarvelousDesigner-MCP (MIT; README, INSTALLATION_REPORT.md: MD 2026.0.315 Windows verified; skill file).
- D https://github.com/dcc-mcp/dcc-mcp-marvelous-designer (MIT; README + docs/acceptance.md: no live host acceptance).
- D https://github.com/NousResearch/hermes-plugin-blender (MIT; official server pinned from projects.blender.org, Blender 5.1+, port 9876, verified with 5.2.2 LTS).
- D https://github.com/psiQAQ/blender_mcp-setup-guide (GPL; official v1.0.3 for 5.1, main snapshot for 5.2).
- D https://github.com/AndreiFlau/blender-mcp-skill (no LICENSE; official extension `lab_blender_org/mcp`, Allow Online Access, port 9876).
- D https://github.com/RobLe3/cc-blender-skill (MIT, v1.3.0, Blender 5.1.1 validation, export recipe).
- D https://github.com/arjun988/blender-skills (MIT, `.cursor/skills/cloth-sim`, `retopology`).
- D https://github.com/freshtechbro/claudedesignskills (MIT, substance-3d-texturing).
- D https://github.com/HKUDS/CLI-Anything (Apache-2.0).
- D https://github.com/reason-machines/design-skills (MIT; MD "unlock" content → rejected), https://github.com/antonyfmunoz/OS (no license).
- S https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026 (official Blender Lab MCP release dates v0.1.0 24 Mar, v1.0.0 27 Apr, v1.0.2 8 Sep, v1.0.3 11 Sep 2026; Anthropic creative connectors 28 Apr 2026) — competitor blog, treat as secondary.
- S GitHub code search `"Marvelous Designer" filename:SKILL.md`, `"Substance Painter" filename:SKILL.md` for the long-tail list.

## Other tools
- S https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/all-changes , https://www.therookies.co/blog/headlines/adobe-unveils-substance-3d-gdc , https://community.adobe.com/announcements-48/now-available-substance-3d-designer-16-sampler-6-and-zbrush-to-painter-integration-1624336 , https://helpx.adobe.com/no/substance-3d/pricing-change.html : Painter 12.0.x (Mar 2026), 12.1 beta OpenPBR, Designer 16 / Sampler 6 (May 2026), Texturing plan 24.99/249.88 USD.
- S https://worldofleveldesign.com/categories/substance/painter/export-import-textures-ue5.php , https://www.versluis.com/2025/07/how-to-use-packed-orm-maps-in-substance-painter/ , https://helpx.adobe.com/substance-3d-painter-python/api/substance-painter/export.html : UE4 (Packed) preset for UE5, ORM layout, Python export API.
- S https://www.cgchannel.com/2025/12/maxon-releases-zbrush-2026-1-and-zbrush-for-ipad-2026-1/ , https://www.cgchannel.com/?p=175400 : ZBrush 2026.1/2026.2, 49 USD/mo or 399 USD/yr rental-only.
- S https://exoside.com/quadremesher/quadremesher-buy/ , https://www.exoside.com/quadremesherdata/QuadRemesher_1.3_UserDoc.pdf , https://blenderartists.org/t/quad-remesher-add-on-update/1647735 : prices (undated), 1.4.1 latest download, Blender 5.2 compatibility unconfirmed.
- S https://www.reallusion.com/auto-setup/unreal-engine/download.html , https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Creating-Custom-Assets/Creating_Assets_with_Transfer_Skin_Weights.htm , https://manual.reallusion.com/Character-Creator-4/Content/ENU/4.0/08_Cloth/Creating_Custom_Clothes_OBJ.htm , https://manual.reallusion.com/Character-Creator-4/Content/ENU/4.0/08_Creating_Custom_Assets/Arms-Layer-for-Transferring-Skin-Weight.htm : Auto Setup 2.0 (UE 5.5–5.7, Dec 2025), Transfer Skin Weights templates, Lateral Partitioning, Conform.
- S https://github.com/daz3d/DazToUnreal , https://www.daz3d.com/forums/discussion/432206/daz-to-unreal-guide-for-newcomers-the-famous-before-your-buy-or-limitations : no 5.8 build found; dForce outfits export, dForce hair does not.
- S https://www.strayspark.studio/blog/texture-resolution-guide-games-512-1k-2k-4k , https://polycount.com/discussion/comment/2765919 , https://help.maxon.net/c4d/2026/en-us/Content/html/Texel_Density.html : texel density ranges (512–1024 px/m third person, 1024–2048 close-up).

## Not verified (treat as assumptions)
- Whether the MD Python/plug-in API is available on a Personal subscription in 2026, and the current Personal EULA wording on distributing output.
- Official Blender Lab MCP license text and exact tool list (host blocked); release dates come from a competitor's blog.
- Blender USD `convert_scene_units='CENTIMETERS'` vs UE USD import unit handling; FBX `colors_type='LINEAR'` behaviour for UE vertex-color masks.
- UE 5.8 "non-destructive round trip" with CLO/MD beyond the release-note sentence.
- Reallusion Auto Setup support for UE 5.8; Quad Remesher on Blender 5.2.
- Triangle budgets, texel-density targets for this project, per-fabric material values, skin-offset distances, Maya Copy Skin Weights option names: practice, not measured or re-verified.
- MD avatar import defaults (unit, axis, Skin Offset) for 2026.x builds.
