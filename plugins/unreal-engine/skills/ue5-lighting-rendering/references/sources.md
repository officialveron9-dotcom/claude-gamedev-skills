# Sources (accessed 2026-10-06)

Access note: direct fetching of dev.epicgames.com, unrealengine.com, forums and most blogs was blocked by the research environment's network policy. Epic pages marked *(excerpt)* were read through search-engine excerpts of the live (5.8-era) pages. Files marked *(downloaded)* were read in full from GitHub.

## Version and feature status
- https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes *(excerpt)*: Lumen Lite (irradiance field + probe occlusion, Medium quality); MegaLights Production-Ready with lighting channels, IES for volumetrics/translucency, transmission, froxel translucency, light finder/ray visualizer; `r.Shadow.Virtual.DeferredInvalidationBudget`, `r.Shadow.Virtual.PrefilteredDistant.ProjectEnable`, `r.Nanite.VSMInvalidateOnLODDelta` throttling; TSR fixes; dynamic resolution on PC DX12/Vulkan.
- https://www.unrealengine.com/news/unreal-engine-5-8-is-now-available and https://forums.unrealengine.com/t/unreal-engine-5-8-released/2729274 *(excerpt)*: 5.8 release (State of Unreal, June 2026), MegaLights/Movie Render Graph production-ready.
- https://forums.unrealengine.com/t/5-8-1-hotfix-released/2738864, https://forums.unrealengine.com/t/5-8-2-hotfix-released/2746335, https://forums.unrealengine.com/t/5-8-3-hotfix-released/2833315 *(excerpt)*: hotfix line; 5.8.3 is the latest found.
- https://www.pcgameshardware.de/Unreal-Engine-Software-239301/News/Version-5-9-angekuendigt-KI-Features-im-Fokus-1551788/ *(excerpt)*: 5.9 announced, no release date.
- https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-7-release-notes *(excerpt)*: Substrate Production-Ready, MegaLights Beta, Nanite Foliage experimental (5.7).
- https://x.com/EpicShaders/status/2070573554135953556 *(excerpt)*: Daniel Wright (Epic): Lumen Lite = irradiance fields with probe occlusion and automatic probe placement, used at Medium GI and Reflection quality.
- https://tomlooman.com/unreal-engine-5-8-performance-highlights/ *(excerpt)*: Lumen Medium = irradiance field gather (`r.Lumen.FinalGatherMethod 0`), faster reflections falling back to SSR, `sg.GlobalIlluminationQuality 1` + `sg.ReflectionQuality 1`.

## Lumen, ray tracing, MegaLights
- https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine *(excerpt)*: HWRT vs SWRT; SWRT needs mesh distance fields; mesh SDF for first ~2 m then global SDF.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine *(excerpt)*: PPV settings (Final Gather Quality, Lumen Scene Lighting Quality/Detail/View Distance 200 m, Max Roughness To Trace 0.4, Ray Lighting Mode / Hit Lighting, refraction bounces); emissive noise limits.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-performance-guide-for-unreal-engine *(excerpt)*: Epic = 30 fps / High = 60 fps console targets, 8 ms / 4 ms Lumen budgets at 1080p; `sg.GlobalIlluminationQuality`, `sg.ReflectionQuality`.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-ray-tracing-in-unreal-engine *(excerpt)*: HWRT traces skinned meshes.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/megalights-in-unreal-engine *(excerpt)*: enabling in Project Settings > Direct Lighting, HWRT prompt, per-light MegaLights Shadow Method, `r.MegaLights.NumSamplesPerPixel`, directional + cloud limitation.
- https://advances.realtimerendering.com/s2025/content/MegaLights_Stochastic_Direct_Lighting_2025.pdf *(title/excerpt)*: MegaLights stochastic direct lighting design.
- https://github.com/trumank/patternsleuth (engine_version.rs) *(downloaded)*: `r.Lumen.IrradianceFieldGather` last present in 5.7 (renamed path in 5.8).

## Exposure, light units, real-world references
- https://dev.epicgames.com/documentation/en-us/unreal-engine/using-physical-lighting-units-in-unreal-engine *(excerpt)*: lux for directional, cd/m² for sky/emissive, candela/lumen/unitless for local lights with inverse-square falloff; EV100 auto exposure.
- https://dev.epicgames.com/documentation/en-us/unreal-engine/auto-exposure-in-unreal-engine *(excerpt)*: Extend default luminance range (default on, Min/Max EV100); physical camera EV100 formula; Manual metering; histogram percentages.
- https://photographylife.com/exposure-value *(excerpt)*: EV100 table (home interiors 5-7, offices 7-8, galleries 8-11).
- https://www.cuesportsindia.com/equipments/3/pool-table *(excerpt; reproduces WPA equipment spec)*: ≥ 520 lux on bed and rails; fixture heights 40 in / 65 in; even illumination.

## Shadows
- https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine *(excerpt)*: caching on by default, `r.Shadow.Virtual.Cache 0` for debugging, WPO/PDO invalidation.
- https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/EShadowCacheInvalidationBehavior *(excerpt)*: Auto/Always/Rigid/Static.

## Materials
- https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-substrate-materials-in-unreal-engine *(excerpt)*: Slab/Fuzz, Convert to Substrate, project opt-in for upgraded projects.
- https://dev.epicgames.com/documentation/unreal-engine/programming-with-substrate-gbuffer-formats *(excerpt)*: Blendable vs Adaptive GBuffer, ~15 % cook increase.
- https://x.com/Sprintermax/status/1988647594902671809 *(excerpt)*: Substrate enabled by default for new 5.7 projects (corroborated by the Substrate overview).
- https://www.cgchannel.com/2026/06/see-5-key-features-for-cg-artists-in-unreal-engine-5-8/ and https://www.strayspark.studio/blog/substrate-toon-shader-ue5-8-tutorial *(excerpt)*: Substrate status history; 5.8 Toon (experimental), AxF import.
- Engine header `MaterialExpressionSubstrate.h`, located through GitHub code search: existence of the *Substrate Simple Clear Coat* expression.

## Path tracer, Nanite notes
- https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine *(title/excerpt)*: Path Tracer reference page.
- https://forums.unrealengine.com/t/nanite-displacement-bugged-in-exact-same-landscape-in-ue-5-8-but-not-in-ue-5-7/2739815 *(excerpt)*: Nanite tessellation/displacement regressions in 5.8.

## CVar evidence (downloaded)
- Epic engine `BaseScalability.ini` (5.8-era, as shipped with Fortnite) via https://raw.githubusercontent.com/iFireMonkey/FortniteTracker/master/ini%20Files/BaseScalability.ini: all tier values quoted in `cvars.md`/`lumen-megalights.md`. Spot-checked identical in 5.8 logs (e.g. `r.Lumen.FinalGatherMethod=1`, `r.TSR.History.ScreenPercentage=200`, `r.Streaming.PoolSize=1000` at Epic).
- UE 5.8 logs (LogConfig "Set CVar" lines and console echoes), public GitHub repos:
  - SalFell/Lean-and-Loot (`LeanLoot/Saved/Logs/LeanLoot.log`, 5.8.1)
  - Ozzon/That-Body-Game (`Docs/*.log`, 5.8.0)
  - zombico/lounge-handoff (`gates/*.log`, 5.8.2)
  - iiishop/Vam2UE5 (`Evidence/*/cook.log`, 5.8.2/5.8.3)
  - CaulyKan/UnrealMmdPlayerVR (`.perflogs/*.log`, 5.8.2)
  - Schreezer/Cinderline (`artifacts/**`, 5.8.2)
  - Tabatskyi/MultiplayerGame (5.8.0)
  - mnoles1911/voxelsim (5.8.0)
  - danger10043/Unreal10thTeamProject-ProjectWither (5.8.2)
  - talal-jpg/OBS_GameplayAbilitySystemRpg (5.8.0)
  - JamesIV4/sim-copter-remake (5.8.0)
