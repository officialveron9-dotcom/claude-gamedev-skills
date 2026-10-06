# Sources (accessed 2026-10-06)

**How these were verified:** this session's egress proxy blocked direct fetches of dev.epicgames.com, forums.unrealengine.com, fab.com, manual.reallusion.com, support.marvelousdesigner.com and every other site tried. **No page was read directly.** Every fact below comes from **search-engine extracts (snippets)** of the listed pages. Items marked *(secondary)* come from non-Epic sites. Items marked *(forum)* are user reports, not official statements. Re-check anything load-bearing in the editor.

## Version and release state
- https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes: Chaos cloth production-ready in 5.8, USD round-trip with CLO/Marvelous, ClothAsset SKM clothing support, Skeletal-Mesh Dataflow nodes, Mutable "reaches production readiness" and dataless COs, MetaHuman Crowd experimental, groom attributes via Interchange USD.
- https://forums.unrealengine.com/t/tutorial-chaos-cloth-updates-5-8/2729420: Dataflow cloth editor production-ready and the default. Tapered capsule update, weight-map painting, new vertex/texture map import nodes.
- https://unrealdirective.com/resources/engine-plugins/chaosclothasset/ *(secondary)*: Chaos Cloth Asset Beta in 5.7 → Production in 5.8.
- https://unrealdirective.com/resources/engine-plugins/mutable/ *(secondary)*: lists Mutable v1.8.0 as Beta (conflicts with the release notes, so treated as unresolved).
- https://www.pcgameshardware.de/Unreal-Engine-Software-239301/News/Version-5-9-angekuendigt-KI-Features-im-Fokus-1551788/ *(secondary)*: 5.9 announced informally, no release. 5.8 confirmed as current. Sibling skill `ue5-animation-characters` independently records 5.8 released 2026-06-17.
- https://www.awn.com/news/unreal-engine-57-now-available, https://gamefromscratch.com/unreal-engine-5-7-released/ *(secondary)*: Substrate production-ready in 5.7.

## Modular characters
- https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-modular-characters-in-unreal-engine: Leader Pose / Copy Pose / Merge comparison table (setup, GT, RT, physics, morphs).
- https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/Components/SkinnedMesh/SetLeaderPoseComponent: Force Update and follower tick-pose parameters.
- https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/USkinnedMeshComponent, https://forums.unrealengine.com/t/leaderposecomponent/2649952 *(forum)*: `bUseBoundsFromLeaderPoseComponent` and bounds workarounds.
- https://issues.unrealengine.com/issue/UE-217626: crash with a PoseableMesh leader (curves/morphs), fixed for 5.5. https://issues.unrealengine.com/issue/UE-22271: Leader Pose overriding SetMorphTarget on followers.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimNode_CopyPoseFromMesh, https://dev.epicgames.com/documentation/unreal-engine/copy-a-pose-in-unreal-engine: Copy Pose From Mesh options (Use Attached Parent, Copy Curves) and tick-order lag.
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/SkeletalMerging/FSkeletalMeshMergeParams, https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/SkeletalMerging/USkeletalMergingLibrary: SkeletalMerging plugin, `MergeMeshes`, params (MeshesToMerge, Skeleton, MeshSectionMappings, StripTopLODS, UVTransformsPerMesh).
- https://answers.unrealengine.com/questions/851111/view.html *(forum)*: bounds from the Physics Asset, Bounds Scale.

## MetaHuman
- https://dev.epicgames.com/documentation/unreal-engine/getting-started-with-parametric-clothing: parametric vs fixed, Outfit Asset, source/target body, multiple sizes.
- https://dev.epicgames.com/documentation/metahuman/creating-parametric-clothing-for-metahuman, https://dev.epicgames.com/documentation/metahuman/getting-started-for-creating-parametric-clothing-in-metahuman: steps (Combined Skel Mesh → Cloth Asset → Outfit + Wardrobe Item → test with a retargeted Manny anim).
- https://dev.epicgames.com/documentation/metahuman/testing-and-configuring-your-parametric-outfit-asset, https://dev.epicgames.com/documentation/unreal-engine/testing-and-setup-in-metahuman-creator: Hair & Clothing → Outfit Clothing → Wear, testing sizes, Body Hidden Face Map location and purpose.
- https://dev.epicgames.com/documentation/metahuman/tailoring-your-own-wardrobe-items, https://dev.epicgames.com/documentation/metahuman/asset-format-and-structure-requirements-for-metahumans-on-fab: skeletal vs Chaos Outfit clothing, optional `WI_*` wardrobe item.
- https://dev.epicgames.com/documentation/unreal-engine/creating-your-metahuman-in-unreal-engine: *Show Compatibility Mode Bodies*, 18 fixed bodies, recommended 6 or 4 source bodies, Export Combined Skel Mesh.
- https://dev.epicgames.com/documentation/metahuman/metahuman-known-issues-5-8-in-unreal-engine: Long Messy Hair on Medium, UEFN fix-up stretching clothing, `.mhpkg` missing parent materials.
- https://dev.epicgames.com/documentation/metahuman/lodsync-component-for-unreal-engine: Components to Sync, Drive default for Body/Face, Num LODs / Forced LOD / Min LOD.
- https://forums.unrealengine.com/t/metahuman-parametric-wardrobe-asset-missing-cloth-simulation-5-8/2736828 *(forum, with official reply cited in snippet)*: sim stripped by the wardrobe/assembly path.
- https://forums.unrealengine.com/t/intended-workflow-for-resizing-a-chaos-outfit-asset-while-preserving-cloth-simulation/2762838 *(forum)*: `ApplyResizing` corrupting sim-to-render deformation.
- https://forums.unrealengine.com/t/fully-hidden-metahuman-body-becomes-visible-after-assembly/2833124 *(forum)*: all-black mask bug.
- https://forums.unrealengine.com/t/simpra-org-clothes-pack-a1-mhpkg-colorable-parametric-metahuman-wardrobe-clothes/2833932 *(vendor post)*: mask menu path, one mask at a time in 5.6, white/black convention.
- https://forums.unrealengine.com/t/certain-metahuman-clothing-assets-stretching/2737381 *(forum)*: wrist stretching to the origin in 5.6, unresolved.
- https://forums.unrealengine.com/t/groom-binding-moves-my-hair-up-by-2-units/507699 *(forum)*: 2-unit Z offset after a Maya round-trip.
- https://www.metahuman.com/news/metahuman-leaves-early-access-with-a-feature-packed-new-release, https://medium.com/@Jamesroha/a-beginners-guide-to-metahumans-in-unreal-engine-5-6-and-5-7-e9b14fadbf3d *(secondary)*: in-editor Creator, parametric body, extended Manny skeleton.
- https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/, https://digitalproduction.com/2025/06/05/metahumans-graduate-ready-for-unity-godot-and-the-fab-cash-register/ *(secondary)*, https://www.unrealengine.com/eula/mhc: MetaHuman licensing under the UE EULA from 5.6, use in other engines, no AI training.

## Chaos Cloth
- https://dev.epicgames.com/documentation/unreal-engine/panel-cloth-editor-overview: Cloth Asset and Dataflow workflow, skin weight transfer, Chaos Cloth Component.
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ChaosClothAssetDataflowNodes (and node pages): MaxDistance semantics, TransferSkinWeights, CollisionConfig (thickness, complex/simple colliders, skinned triangle mesh, CCD), SelfCollisionConfig (thickness per side), BackstopConfig, VelocityScaleConfig fields, AerodynamicsConfig.
- https://dev.epicgames.com/documentation/unreal-engine/node-reference/Dataflow (SetPhysicsAsset, ClothAssetTerminal, SimulationSolverConfig, SimulationMaxDistanceConfig, SimulationDefaultConfig, StaticMeshImport, WeightMap, SimulationLongRangeAttachmentConfig, SimulationVelocityScaleConfig, TransferSkinWeights, TransferLinearSkinWeights, Remesh): node names.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ChaosClothComponent: component based on SkinnedMeshComponent, accepts cloth or outfit assets, set_enable_simulation, suspend_simulation.
- https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/ClothComponent/ForceNextUpdateTeleport, https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/USkeletalMeshComponent/ForceClothNextUpdateTeleportAndR-: teleport/reset API.
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ChaosClothAssetEditor/UE__Chaos__ClothAsset__UE_EXPERI- (search extract): `DF_LegacyClothingAssetTemplate` legacy conversion.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ChaosClothingInteractor: SetAerodynamics deprecated → SetWind.
- https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/ClothingSystemRuntimeInterface/FClothCollisionData: collision primitive types (spheres, capsules, tapered capsules, convex, boxes).
- https://forums.unrealengine.com/t/does-chaos-cloths-kinematic-collider-node-work-with-simulated-bodies-that-have-soft-constraints/2572339 *(forum)*, https://www.michellemolina3d.com/blog/chaos-cloth-kinematic-collider-in-unreal-engine-55-for-metahuman *(secondary)*: kinematic collider, soft-constraint clipping.
- https://forums.unrealengine.com/t/cloth-sim-jitters/1327753 *(forum)*, https://issues.unrealengine.com/issue/UE-172069: `p.ChaosCloth.UseTimeStepSmoothing 0`.
- https://forums.unrealengine.com/t/tutorial-cloth-troubleshooting-and-debugging-tips/576633: debug CVars (`p.ClothPhysics`, `p.ChaosCloth.Reset`, `p.ChaosCloth.DebugStep`, `r.Mobile.EnableCloth`).
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ChaosCloth/UChaosClothSharedSimConfig (search extract): iteration/subdivision counts, local-space simulation against far-from-origin jitter.
- https://bugnet.io/blog/fix-unreal-chaos-cloth-sim-blows-up-on-teleport, https://bugnet.io/blog/fix-unreal-skeletal-mesh-cloth-popping-on-lod-change *(secondary)*: teleport explanation, per-LOD disable, rough ms cost.
- https://www.intel.com/content/www/us/en/developer/articles/technical/unreal-engine-blueprint-cpu-optimizations-for-cloth-simulations.html *(secondary)*: `bDisableClothSimulation` is construction-only.

## Mutable
- https://dev.epicgames.com/documentation/unreal-engine/mutable-overview-in-unreal-engine: purpose and runtime generation.
- https://dev.epicgames.com/documentation/unreal-engine/mutable-physics-and-clothing-in-unreal-engine: no Panel Cloth support, legacy cloth recommended, Enable Physics Asset Merging.
- https://forums.unrealengine.com/t/mutable-plugin-5-8-mesh-reshape-works-correctly-with-body-morphs-but-modifiers-clip-mesh-with-mesh-produce-geometry-artifacts-on-the-reshaped-mesh/2836644 *(forum)*: Clip Mesh With Mesh / Remove Mesh Blocks artifacts with reshape.
- https://forums.unrealengine.com/t/mutable-crashes-customizableobjectmeshupdate-leveltick-cpp/2738421 *(forum)*: 5.8 Mutable crash reports.

## Grooms
- https://dev.epicgames.com/documentation/unreal-engine/setting-up-bindings-for-grooms-in-unreal-engine: Target/Source Skeletal Mesh, shared UVs, Num Interpolation Points + RBF, Matching Section.
- https://dev.epicgames.com/documentation/unreal-engine/setting-up-level-of-detail-for-grooms-in-unreal-engine, https://dev.epicgames.com/documentation/unreal-engine/groom-scalability-and-performance-with-unreal-engine: Strands/Cards/Meshes per LOD.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/HairStrandsCore/UGroomComponent: collision components, physics-asset collision radius.
- https://dawnarc.com/2024/03/ue5groom-hair-notes/ *(secondary)*: SetForcedLOD vs binding LOD, Skin Cache requirement, missing-UV error.
- https://dev.epicgames.com/documentation/metahuman/groom-tools: Houdini groom tools (5.8 compatible).
- No source found for the hats/hair approach. That section is marked as practice.

## Skin weights and editing
- https://dev.epicgames.com/documentation/unreal-engine/create-an-action-utility-for-transferring-skin-weights-in-unreal-engine, https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/GeometryScript/MeshQueries/BoneWeights/TransferBoneWeightsfromMesh: static → skeletal weight transfer.
- https://dev.epicgames.com/documentation/unreal-engine/skeleton-editing-in-unreal-engine, https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/MeshModelingToolsEditorOnly/UWeightToolTransferManager: Skeletal Mesh Editing Tools plugin, weight painting and transfer.

## Import
- https://dev.epicgames.com/documentation/en-us/unreal-engine/interchange-import-reference-in-unreal-engine, https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-import-options-reference-in-unreal-engine: Import Morph Targets, Use T0 As Ref Pose, Skeleton, Create Physics Asset, Import Meshes in Bone Hierarchy, Interchange default since 5.5, normal import method.
- https://app.cinevva.com/guides/blender-to-unreal-export-checklist *(secondary)*: Blender units, leaf bones, bone axes.
- https://forums.unrealengine.com/t/fbx-skeletal-front-face-x-axis-mesh-import-issues-with-interchange-fbx-importer/2690232 *(forum)*: Interchange front-axis issues.

## Fab and licensing
- https://www.fab.com/eula, https://forums.unrealengine.com/t/can-i-use-assets-purchased-from-fab-com-under-the-standard-personal-license-to-develop-games-with-unreal-engine-and-then-use-them-commercially/2452918 *(forum)*: Standard License Personal/Professional (USD 100k), same rights, commercial use, any engine.
- https://www.unrealengine.com/eula-change-log/content: UE-Only Content definition, NoAI section.
- Fab listings (e.g. https://www.fab.com/listings/647b0542-66a7-47b5-9a10-7b1eccfb1435): "Rigged to Epic skeleton" / "IK bones included" technical fields.

## Reallusion
- https://manual.reallusion.com/Live_Link_Plugin/ENU/Live_Link_Plugin/1.36/Skeleton-between-HD-and-UE-Characters.htm, https://www.creativebloq.com/3d/character-creator-5-review-unreal-engine-support-and-auto-rigging-make-it-a-joy-to-use *(secondary)*: CC5 HD extra bones, MetaHuman/Manny/UEFN bone counts.
- https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Metahuman-Interoperability/Exporting-Characters-to-UE.htm: FBX export preset, bind pose presets.
- https://discussions.reallusion.com/t/ue-auto-setup-all-in-one-2-0-is-released-now-supporting-ue-5-7/16072, https://forums.unrealengine.com/t/cc5-fbx-import-crashes-ue5-7-4/2734691 *(forum)*, Reallusion FeedBackTracker issues (Auto Setup crashes, morph + T0 crash, RL opacity no shadow).
- https://discussions.reallusion.com/t/cc4-unreal-delete-hidden-faces/12712, https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08_Cloth/Using_Hide_Body_Mesh_Tool.htm: Delete Hidden Mesh / Hide Body Mesh.
- https://www.reallusion.com/license/content.html: export license, Standard vs Extended for games.

## Daz
- https://github.com/daz3d/DazToUnreal/releases, https://www.daz3d.com/forums/discussion/748786/dtu-bridge-for-ue-5-7 *(forum)*: v5.7.0.521, compile issues, Fab version age, forks.
- https://www.daz3d.com/forums/discussion/662176/daz-to-unreal-5-3-gen9-base-character-missing-settings-in-the-plugin-resolved, https://www.daz3d.com/forums/discussion/629676/daz-to-unreal-characters-importing-into-unreal-5-1-rotated-90-degrees-off *(forum)*: Fix Twist Bones, Zero root rotation, 90° root.
- https://www.daz3d.com/interactive-license-info: Interactive License required for games.

## Mixamo
- https://www.unamedia.com/ue5-mixamo/docs/fix-fbx-import-error/ *(secondary)*: root-track import error.
- https://sorceress.games/blog/replace-the-mixamo-auto-rig-browser-no-adobe-id, https://app.cinevva.com/guides/mixamo-to-blender-2026 *(secondary)*: 65-bone skeleton, maintenance mode, outages.

## Marvelous Designer / CLO
- https://support.marvelousdesigner.com/hc/en-us/articles/52699135975705-Marvelous-Designer-to-MetaHuman-USD-Garment-Integration-Workflow, https://support.clo3d.com/hc/en-us/articles/53322960594969-CLO-to-MetaHuman-USD-Garment-Integration-Workflow: the 8-step USD → Cloth Asset → Outfit flow.

## Not verified (treat as assumptions)
- Mutable's exact status flag in 5.8 (the release notes and a plugin index conflict).
- Reallusion Auto Setup support for UE 5.8.
- Exact reset variant name on `UChaosClothComponent` (only `ForceNextUpdateTeleport` was seen).
- Whether Skeletal Mesh Merge keeps clothing data (assumed not).
- The exact `StaticMeshImport` vs USD import node names for your template, and the name of the kinematic collider node.
- Texture budgets (2K hero / 1K NPC) and the cloth ms cost are starting points, not Epic figures.
- The hats/hair approach and the Blender "root" armature naming are community practice.
