# Sources (accessed 2026-10-06)

Method note: direct fetches of dev.epicgames.com, unrealengine.com and forums.unrealengine.com were blocked by the session's egress policy. Facts were checked against search-engine extracts of these pages. Items marked *(secondary)* come from non-Epic sites and should be confirmed in-engine.

## Version / release state
- https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes: 5.8 Character & Animation (IK Retargeter foot definition, Retarget Override Sets, Direct Mesh Controls), Mover updates (NavWalking for Detour Crowd, root motion/montage handling), Mass changes.
- https://www.unrealengine.com/news/unreal-engine-5-8-is-now-available: 5.8 availability.
- https://forums.unrealengine.com/t/5-8-1-hotfix-released/2738864, https://forums.unrealengine.com/t/5-8-2-hotfix-released/2746335, https://forums.unrealengine.com/t/5-8-3-hotfix-released/2833315: hotfix line, the 5.8.3 MetaHuman Nanite LOD fix, and the state machine state-stack fix.
- https://wnhub.io/news/engines/item-51157, https://www.pcgameshardware.de/Unreal-Engine-Software-239301/News/State-of-Unreal-2026-UE6-UE-5-8-MegaLights-1545629/ *(secondary)*: 5.8 released 2026-06-17, called the last UE5 feature release, and UE6 early access planned for late 2027.
- https://tomlooman.com/unreal-engine-5-8-performance-highlights/ *(secondary, reputable)*: new Animation Budget Allocator CVars in 5.8.

## Animation Blueprint, threading, layers
- https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-optimization-in-unreal-engine: multithreaded update setting, thread-safe functions, VisibilityBasedAnimTickOption values, URO.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-in-lyra-sample-game-in-unreal-engine: BlueprintThreadSafeUpdateAnimation, Property Access, ALI_ItemAnimLayers / ABP_ItemAnimLayersBase.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-blueprint-linking-in-unreal-engine: Animation Layer Interface, Link Anim Class Layers grouping semantics, notify propagation options.
- https://forums.unrealengine.com/t/animation-blueprints-property-access-out-of-sync/2644738: the Property Access timing issue (used for the one-frame-latency warning).

## Motion Matching, Choosers, GASP, warping
- https://www.unrealengine.com/en-US/blog/unreal-engine-5-4-is-now-available: Motion Matching production-ready in 5.4.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-in-unreal-engine: Pose Search Schema and Database, the Motion Matching node, Pose History.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-debugging-in-unreal-engine: Rewind Debugger integration and required plugins.
- https://forums.unrealengine.com/t/how-close-is-the-chooser-plugin-to-production-readiness/2709573, https://portal.productboard.com/epicgames/1-unreal-engine-public-roadmap/c/1462-choosers-and-proxy-tables-beta: Choosers Beta in 5.4, later called production by Epic staff.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/game-animation-sample-project-in-unreal-engine: GASP features (Offset Root Bone experimental, database LOD, traversal).
- https://www.unrealengine.com/tech-blog/explore-the-updates-to-the-game-animation-sample-project-in-ue-5-7: Mover character (Experimental), 400 animations, new Mover modes, Pose Search column in Choosers.
- https://www.unrealengine.com/tech-blog/download-the-latest-game-animation-sample-project-now-updated-for-ue-5-8: Physics Control Component/Asset, Pose Search Interaction Assets, Motion Match Multi, Chooser internal databases, experimental Look-At POI Control Rig.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/adding-a-metahuman-to-the-game-animation-sample-project-in-unreal-engine: the GASP MetaHuman character.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/distance-matching-in-unreal-engine and the UAnimDistanceMatchingLibrary API: DistanceMatchToTarget and AdvanceTimeByDistanceMatching.
- https://dev.epicgames.com/documentation/unreal-engine/pose-warping-in-unreal-engine: Stride, Orientation and Slope warping.
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/AnimationWarpingRuntime/FAnimNode_OffsetRootBone and https://issues.unrealengine.com/issue/UE-305539: Offset Root Bone purpose and the moving-base limitation.
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/AnimationWarpingRuntime/FAnimNode_FootPlacement: Foot Placement node (experimental struct).
- https://dev.epicgames.com/documentation/en-us/unreal-engine/mover-in-unreal-engine: Mover is Experimental.
- https://unrealdirective.com/resources/engine-plugins/uaf/, https://dev.epicgames.com/documentation/en-us/unreal-engine/API/PluginIndex/UAF *(the first is secondary)*: UAF is Experimental. The GASP UAF character report is *(secondary, unverified)*.

## Montages, notifies, root motion, Motion Warping
- https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine: montages and root motion modes for networked games.
- https://docs.unrealengine.com/4.27/en-US/API/Runtime/Engine/Animation/EMontageNotifyTickType__Type/index.html: Queued vs Branching Point semantics.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-warping-in-unreal-engine and the UMotionWarpingComponent API: warp targets, Skew Warp, AddOrUpdateWarpTargetFromLocationAndRotation.

## Control Rig / IK
- https://dev.epicgames.com/documentation/en-us/unreal-engine/control-rig-full-body-ik-in-unreal-engine: FBIK as a position-based solver, bone settings.
- https://dev.epicgames.com/documentation/unreal-engine/control-rig-in-animation-blueprints-in-unreal-engine and the AnimNode_ControlRig Python API: the Control Rig node and its alpha inputs.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/ik-rig-in-animation-blueprints-in-unreal-engine: the IK Rig node and exposed goals.

## Retargeting
- https://dev.epicgames.com/documentation/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine-5-8, https://dev.epicgames.com/documentation/unreal-engine/retargeting-operation-stack-in-unreal-engine-5-8: op stack, 5.8 retargeting changes.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/IKRetargeterController: default op order (add_default_ops).
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/IKRig/ERootMotionSource: Copy From Source Root / Generate From Target Pelvis.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/retargeting-bipeds-with-ik-rig-in-unreal-engine, https://dev.epicgames.com/documentation/en-us/unreal-engine/auto-retargeting-in-unreal-engine: Auto Retarget Chains, Auto Align, auto-generate for known skeletons.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/fix-foot-sliding-with-ik-retargeter-in-unreal-engine: the speed-planting/FBIK foot goal setup.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/runtime-ik-retargeting-in-unreal-engine: runtime retarget cost, FBIK expense, disabling IK at distance.
- https://www.unamedia.com/ue5-mixamo/docs/mixamo-root-motion-animations *(secondary)*: Mixamo lacks a root bone.

## MetaHuman
- https://www.metahuman.com/news/metahuman-5-8-is-now-available, https://dev.epicgames.com/documentation/metahuman/metahuman-5-8-release-notes-in-unreal-engine: 5.8 features (Collections Experimental, Mesh to MetaHuman bodies, open-source libraries).
- https://dev.epicgames.com/documentation/en-us/metahuman/assembly: UE Cine vs UE Optimized (High/Medium/Low), texture limits.
- https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/, https://digitalproduction.com/2025/06/05/metahumans-graduate-ready-for-unity-godot-and-the-fab-cash-register/ *(secondary)*: in-editor Creator in 5.6, cloud autorig and texture synthesis, the EULA change.
- https://dev.epicgames.com/documentation/metahuman/controlling-metahuman-levels-of-detail-lods-in-unreal-engine, https://dev.epicgames.com/documentation/en-us/metahuman/lodsync-component-for-unreal-engine: LODSync, Num LODs, Forced LOD, groom LOD.
- https://dev.epicgames.com/documentation/en-us/metahuman/the-metahuman-component-for-unreal-engine: per-LOD body and neck correctives, facial LOD threshold, rigid body LOD threshold.
- https://dev.epicgames.com/documentation/en-us/metahuman/requirements-and-configuration-settings-for-metahumans-in-unreal-engine: Support Compute Skin Cache, Groom and RigLogic plugins.
- https://dev.epicgames.com/documentation/en-us/metahuman/audio-driven-animation, https://dev.epicgames.com/documentation/en-us/metahuman/metahuman-animator-in-unreal-engine: audio, video and webcam animation, the 5.6+ requirement.
- https://forums.unrealengine.com/t/status-of-skinned-meshes-and-metahuman-and-nanite-support/2835575: limitations of Nanite skinned meshes.

## Performance
- https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-budget-allocator-in-unreal-engine: plugin, SkeletalMeshComponentBudgeted, a.Budget.* CVars and defaults.
- https://unrealdirective.com/resources/console-variables/a-uro-enable/, https://ue5consolecommands.com/command/a-uro-forceanimrate/ *(secondary CVar indexes)*: a.URO.* and a.Parallel* descriptions.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-shortcuts-and-tips-unreal-engine: ShowDebug ANIMATION, a.VisualizeLODs.
- https://forums.unrealengine.com/t/when-update-rate-optimization-is-enabled-in-skeletal-mesh-component-anim-curve-results-are-not-as-expected/1191889: URO vs curve values.
- https://forums.unrealengine.com/t/animationbudgetallocator-doesnt-utilize-interpolation-on-registered-components-and-it-feels-like-framerate-drop-what-is-a-proper-way-to-address-it/2663219: the allocator interpolation complaint.

## Not verified (treat as assumptions)
- Exact names of the new 5.8 `a.Budget.*` CVars. Use console autocomplete.
- That the 5.8 GASP ships a UAF character (secondary source only).
- The performance budget numbers in performance.md (author's starting points, not Epic figures).
