# Sources (accessed 2026-10-06)

Method note: direct fetches of dev.epicgames.com, unrealengine.com and forums.unrealengine.com were blocked by the session's egress policy. Facts were checked against search-engine extracts of these pages. Items marked *(secondary)* come from non-Epic sites. Confirm them in-engine.

## Version / maturity
- https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes: 5.8 Mass changes (FMassNavMeshPathFollowTask OffsetCornersFromBoundaries, FAgentHeightFragment on Mass StateTree tasks), Mover NavWalking for Detour Crowd, ChaosMover.
- https://www.unrealengine.com/blog/unreal-engine-5-1-is-now-available: Smart Objects and StateTree production-ready in 5.1, MassEntity Beta in 5.1.
- https://portal.productboard.com/epicgames/1-unreal-engine-public-roadmap/c/862-massentity-beta, https://portal.productboard.com/epicgames/1-unreal-engine-public-roadmap/c/1928-mass-entity-builder-experimental-: MassEntity Beta, Mass Entity Builder Experimental.
- https://forums.unrealengine.com/t/mass-entity-5-8-preview/2733180: Mass replication with Iris still in progress in 5.8.
- https://tomlooman.com/unreal-engine-5-8-performance-highlights/ *(secondary, reputable)*: 5.8 Mass overhaul (Mass Signals in core, sparse fragments, off-game-thread entity creation).
- https://dev.epicgames.com/documentation/en-us/unreal-engine/mover-in-unreal-engine: Mover is Experimental.
- https://forums.unrealengine.com/t/behavior-tree-state-tree-or-blueprint-state-machine/2740353: forum guidance that BT receives no updates and StateTree is recommended. The speaker's affiliation was not verified, so a formal deprecation is **unconfirmed**.
- https://www.strayspark.studio/blog/state-tree-vs-behavior-tree-ue5-7-migration-2026 *(secondary, low confidence, conflicting benchmarks)*: the StateTree vs BT tick-cost debate. Used only to say "profile, don't assume".

## StateTree / BT
- https://dev.epicgames.com/documentation/unreal-engine/overview-of-state-tree-in-unreal-engine, https://dev.epicgames.com/documentation/en-us/unreal-engine/statetree-quick-start-guide: concepts, evaluators, global tasks, property binding categories.
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GameplayStateTreeModule/UStateTreeAIComponent: StateTreeAIComponent and StateTreeAIComponentSchema (AIControllerClass).
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GameplayStateTreeModule/FStateTreeRunEnvQueryTask, https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GameplayStateTreeModule/FStateTreeMoveToTask: built-in AI tasks.
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/StateTreeModule/FStateTreeScheduledTick, https://forums.unrealengine.com/t/statetreecomponent-tick/2716348: scheduled and custom tick rates.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/statetree-debugger-quick-start-guide: StateTree debugger, live and remote sessions, trace files.
- https://forums.unrealengine.com/t/statetree-tasks-not-ticking-when-executed-via-use-smart-object-with-gameplay-interaction/2706758: the tick issue under Gameplay Interactions.

## Smart Objects
- https://dev.epicgames.com/documentation/en-us/unreal-engine/smart-objects-in-unreal-engine---overview: definitions, slots, behavior definitions, claim to occupied flow.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/smart-objects-in-unreal-engine---quick-start: required plugins (Smart Objects, AI Behaviors / Gameplay Behaviors, Gameplay Behavior Smart Objects), the BT plus montage example.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/BlueprintAPI/AI/Tasks/MovetoandUseSmartObjectwithGamep-: the "Move to and Use Smart Object with Gameplay Behavior" node.
- https://forums.unrealengine.com/t/5-6-mass-ai-smart-object-invalid-claim-handle-id/2561118 and search extracts on Find/Claim separation: the Find/Claim state separation and the `Try Enter` advice *(forum)*.

## Navigation
- https://dev.epicgames.com/documentation/unreal-engine/navigation-mesh-settings-in-the-unreal-engine-project-settings, https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-how-to-modify-the-navigation-mesh-in-unreal-engine: Static / Dynamic Modifiers Only / Dynamic, the ~50% cheaper tile updates, Can Ever Affect Navigation.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/using-navigation-invokers-in-unreal-engine: invokers (not needed here).
- https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partitioned-navigation-mesh: the World Partition nav workflow.
- https://forums.unrealengine.com/t/aimoveto-failing/2658534 and related threads: MoveTo failure causes (Auto Possess AI, `P` visualization, CanBeMainNavData).
- https://forums.unrealengine.com/t/detour-crowds-vs-rvo-avoidance/313908, https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/AIModule/FCrowdAvoidanceConfig: RVO vs Detour, crowd parameters.

## Perception / EQS / debugging
- https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine: senses, stimuli source, detection by affiliation.
- https://zomgmoz.tv/unreal/AI-Perception/Perception-Detection-by-Affiliation, https://apokrif6.github.io/2024/01/20/affiliation-and-team-in-unreal-engine.html *(secondary)*: the C++ team interface requirement, attitude solver.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/environment-query-system-overview-in-unreal-engine, https://dev.epicgames.com/documentation/en-us/unreal-engine/environment-query-testing-pawn-in-unreal-engine, https://dev.epicgames.com/documentation/en-us/unreal-engine/eqs-node-reference-generators-in-unreal-engine: EQS concepts, the testing pawn color legend, generators.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/using-the-gameplay-debugger-in-unreal-engine, https://dev.epicgames.com/documentation/unreal-engine/ai-debugging-in-unreal-engine: the apostrophe key, numpad categories, EnableGDT.

## Crowds / performance
- https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-sharing-plugin-in-unreal-engine, https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimationSharingStateProcessor: Animation Sharing setup, state processor, significance-based scalability.
- https://unrealdirective.com/resources/engine-plugins/animationsharing/ *(secondary)*: the plugin's status listing.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/significance-manager-in-unreal-engine: Significance Manager, register/unregister, Update call.
- https://forums.unrealengine.com/t/community-tutorial-animtotexture-plugin-how-to-use-it-to-make-vertex-animation-textures-for-crowds/746648, https://vrealmatic.com/unreal-engine/city-sample/crowd *(secondary)*: AnimToTexture and the City Sample crowd use (Experimental plugin).
- https://dev.epicgames.com/documentation/metahuman/metahuman-collections-in-unreal-engine, https://80.lv/articles/populate-your-ue5-8-worlds-with-metahuman-crowds: MetaHuman Collections (Experimental, Actors ↔ Instanced Skinned Meshes, Mass orchestration).
- https://github.com/Megafunk/MassSample, https://christiansantori.com/blog/mass-entity-unreal-engine-purposeful-crowds *(secondary)*: MassCrowd and ZoneGraph context.

## Not verified (treat as assumptions)
- Whether Behavior Trees are formally deprecated in 5.8 (no Epic primary statement found).
- The exact Smart Object subsystem method names in 5.8 (they changed across 5.x, so check the headers).
- The Gameplay Interactions plugin maturity label in 5.8.
- The AI performance budget numbers (author's starting points).
