# Sources (accessed 2026-10-06)

Access note: direct fetching of dev.epicgames.com, unrealengine.com, forums and most blogs was blocked by the research environment's network policy. Pages marked *(excerpt)* were read through search-engine excerpts of the live pages. Files marked *(downloaded)* were read in full from GitHub.

## Version / 5.8 changes
- https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes *(excerpt)*:
  - Lumen Lite (Medium), MegaLights Production-Ready
  - VSM `r.Shadow.Virtual.DeferredInvalidationBudget`, `r.Shadow.Virtual.PrefilteredDistant.ProjectEnable`
  - Nanite handheld raster/culling optimizations
  - Dynamic resolution enabled for PC DX12/Vulkan
  - TSR memory-spike fix
- https://tomlooman.com/unreal-engine-5-8-performance-highlights/ *(excerpt)*: 5.8 focus on stabilisation; shader-permutation reductions (VSM, Substrate, MegaLights, Lumen, volumetric fog); Lumen Lite = `sg.GlobalIlluminationQuality 1` + `sg.ReflectionQuality 1`, `r.Lumen.FinalGatherMethod 0`.
- https://windowsforum.com/news/unreal-engine-5-8-shader-stutter-fixes-what-pc-gamers-need-to-know.446696/ *(excerpt, secondary)*: 5.8 shader de-duplication; Epic-reported Fortnite shader-count reduction; refined PSO precaching.
- https://forums.unrealengine.com/t/5-8-3-hotfix-released/2833315 *(excerpt)*: 5.8.3 is the current hotfix found.

## Profiling
- https://dev.epicgames.com/documentation/en-us/unreal-engine/stat-commands-in-unreal-engine *(excerpt)*: stat unit/unitgraph/RHI/game/engine/foliage/levels semantics.
- https://zenn.dev/kta552/articles/ue-profile-2-0-how-to-use?locale=en *(excerpt)*: 5.6+ ProfileGPU table output and stat gpu split into Graphics/Compute; Insights dependency arrows.
- https://github.com/GameDevGrzesiek/OptimizationBible/blob/main/UnrealEngineTools.md *(downloaded, secondary)*:
  - 5.6 unified GPU profiler (stat gpu / ProfileGPU / Insights)
  - GPU pass → problem table (adapted)
  - Profile in Test builds, not the editor
- https://dev.epicgames.com/documentation/en-us/unreal-engine/trace-in-unreal-engine-5 and https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-reference-in-unreal-engine-5 *(excerpt)*: `-trace=` channels, `-statnamedevents`, `trace.start`/`trace.stop`.
- https://www.intel.com/content/www/us/en/developer/articles/technical/unreal-engine-optimization-profiling-fundamentals.html *(excerpt)*: Frame/Game/Draw/GPU meaning; determine CPU vs GPU bound first.

## Lumen / VSM / MegaLights / Nanite costs
- https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-performance-guide-for-unreal-engine *(excerpt)*: Epic = 30 fps, High = 60 fps console targets; 8 ms / 4 ms Lumen budgets at 1080p; `sg.GlobalIlluminationQuality`, `sg.ReflectionQuality`.
- https://x.com/EpicShaders/status/2070573554135953556 *(excerpt)*: Lumen Lite at Medium GI/Reflections, ~2x faster than High.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine *(excerpt)*: caching default on; `r.Shadow.Virtual.Cache 0`; WPO/PDO invalidation; Shadow Cache Invalidation Behavior.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/megalights-in-unreal-engine *(excerpt)*: fixed rays per pixel, `r.MegaLights.NumSamplesPerPixel`, HWRT recommendation, shadow method.
- https://dev.epicgames.com/documentation/unreal-engine/nanite-virtualized-geometry-in-unreal-engine *(excerpt)* and https://forums.unrealengine.com/t/nanite-displacement-bugged-in-exact-same-landscape-in-ue-5-8-but-not-in-ue-5-7/2739815 *(excerpt)*: Nanite tessellation experimental; 5.8 displacement regressions.
- https://portal.productboard.com/epicgames/1-unreal-engine-public-roadmap/c/2219-nanite-foliage-skinning-experimental- *(excerpt)*: Nanite foliage/skinning experimental.

## PSO / shader stutter
- https://dev.epicgames.com/documentation/en-us/unreal-engine/pso-precaching-for-unreal-engine *(excerpt)*: precaching default since 5.3; `r.PSOPrecaching`; delayed proxy creation while PSOs compile.
- https://dev.epicgames.com/documentation/unreal-engine/manually-creating-bundled-pso-caches-in-unreal-engine *(excerpt)*: bundled cache workflow, `r.ShaderPipelineCache.Enabled`.
- https://tomlooman.com/unreal-engine-psocaching/ *(excerpt)*: hybrid precache + bundled cache recommendation.
- https://www.unrealengine.com/tech-blog/game-engines-and-shader-stuttering-unreal-engines-solution-to-the-problem *(title/excerpt)*: Epic's PSO stutter background.

## CVar evidence (downloaded)
- Epic engine `BaseScalability.ini` (5.8-era, as shipped with Fortnite): https://raw.githubusercontent.com/iFireMonkey/FortniteTracker/master/ini%20Files/BaseScalability.ini. Source of all tier tables, cross-checked against 5.8 logs.
- UE 5.8.0-5.8.3 logs in public GitHub repos ("LogConfig: Set CVar [[…]]", console echoes, and the "SetByScalability was ignored … lower priority" warnings):
  - SalFell/Lean-and-Loot, Ozzon/That-Body-Game, zombico/lounge-handoff
  - iiishop/Vam2UE5, CaulyKan/UnrealMmdPlayerVR
  - Schreezer/Cinderline (`t.MaxFPS` echo, 5.8.2)
  - Tabatskyi/MultiplayerGame, mnoles1911/voxelsim, danger10043/Unreal10thTeamProject-ProjectWither
  - talal-jpg/OBS_GameplayAbilitySystemRpg, JamesIV4/sim-copter-remake
