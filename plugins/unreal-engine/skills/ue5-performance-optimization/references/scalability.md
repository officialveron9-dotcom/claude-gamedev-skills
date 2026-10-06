# Scalability, presets and device profiles (UE 5.8)

Contents: groups and levels · config layering and the CVar-priority trap · what Epic's tiers contain · a tier plan for this game · device profiles · auto-detect and user settings.

## Groups and levels

Levels: 0 Low, 1 Medium, 2 High, 3 Epic, 4 Cinematic (`@Cine` sections).

| Group CVar | Controls (5.8 BaseScalability) |
|---|---|
| `sg.ResolutionQuality` | Internal screen % (presets: Performance 50, Balanced 58.3, Quality 66.7, Native 100) |
| `sg.ViewDistanceQuality` | `r.ViewDistanceScale` (0.4/0.6/0.8/1.0/10), `r.SkeletalMeshLODBias` (2/1/0/0/0) |
| `sg.AntiAliasingQuality` | TSR history %, update quality, flicker rejection |
| `sg.ShadowQuality` | VSM pages/LOD bias/SMRT rays, MegaLights samples, volumetric fog grid |
| `sg.GlobalIlluminationQuality` | Lumen GI (off/Lite/High/Epic/Cine), RT skeletal meshes, DFAO |
| `sg.ReflectionQuality` | Lumen reflections (off at Low and **Medium**), SSR quality |
| `sg.PostProcessQuality` | DOF, bloom, motion blur, eye adaptation, tonemapper, LUT size |
| `sg.TextureQuality` | Streaming pool, mip bias, anisotropy |
| `sg.EffectsQuality` | `r.MaterialQualityLevel`, SSS quality, translucency lighting volume, refraction quality, Niagara quality level |
| `sg.FoliageQuality` | Foliage/grass density |
| `sg.ShadingQuality` | Anisotropic materials, hair shading quality |
| `sg.LandscapeQuality` | Landscape (unused here) |

Console: `scalability 3` sets all groups; then override single groups (`sg.ShadowQuality 2`).

## Config layering and the priority trap

- Engine `BaseScalability.ini` → project `Config/DefaultScalability.ini` → platform `Config/<Platform>/<Platform>Scalability.ini`.
- Override only the keys you change, in the **same section names** (`[GlobalIlluminationQuality@2]`). Never edit engine Base files: upgrades overwrite them, and launcher builds can't be shipped modified.
- **CVar priority trap (seen in 5.8 logs).** A CVar set by Project Settings/DefaultEngine.ini, the console or the command line outranks scalability. The engine then logs `Setting the console variable 'X' with 'SetByScalability' was ignored as it is lower priority than the previous 'SetByProjectSetting'`.
  - Consequence: the in-game quality menu silently stops affecting that CVar.
  - Rule: tier-dependent CVars go **only** in DefaultScalability.ini or device profiles, never in `[SystemSettings]` or `[/Script/Engine.RendererSettings]`.
- Saved user settings (`Saved/Config/<Platform>/GameUserSettings.ini`, `[ScalabilityGroups]`) persist between runs. Delete them when testing new defaults.

## What the 5.8 tiers contain (excerpts)

| | Low | Medium | High | Epic | Cine |
|---|---|---|---|---|---|
| Lumen GI | off | Lite (irradiance field) | screen probes /32 | /16 + mesh SDF | /8 |
| Lumen reflections | off | **off (SSR)** | half-res | full, translucency front layer allowed | + front layer on |
| HW hit lighting | – | no | no | allowed | allowed |
| TSR history | 100 % | 100 % | 100 % | 200 % | 200 % |
| Streaming pool (MB) | 400 | 600 | 800 | 1000 | 3000 |
| Limit pool to VRAM | yes | yes | yes | no | no |
| Max anisotropy | 1 | 2 | 4 | 8 | 8 |
| Skeletal LOD bias | 2 | 1 | 0 | 0 | 0 |
| VSM pages / SMRT local rays | 512 / 0 | 512 / 4 | 2048 / 4 | 4096 / 8 | 8192 / 16 |
| MegaLights samples/pixel | 2 | 2 | 4 | 4 | 4 |
| `r.DepthOfFieldQuality` | 0 | 1 | 2 | 2 (gather divisor 2) | 4 (full-res) |

## Recommended tier plan for the pool-hall game

| Preset | GI / Reflections | Resolution | Notes |
|---|---|---|---|
| Ultra (Epic) | Lumen HWRT, hit lighting reflections | TSR ~75-100 %, history 200 % | Hero look; RTX 3080/RX 6800-class and above (assumption, profile it) |
| High | Lumen HWRT, surface-cache reflections | TSR 67-75 % | Default for most RT GPUs |
| Medium | Lumen Lite + **reflection captures placed** | TSR 58-67 % | Check ball reflections; captures are mandatory |
| Low | No Lumen: Sky Light + captures + a few extra fill lights | TSR 50-58 % | Needs a manually authored fallback look |

- Keep exposure, light intensities and materials identical across tiers. Only lighting technique and resolution change.
- Build fallback fill lights as a "LowQualityLights" set toggled by the menu or tier. Without them, Low looks flat and dark.
- Recheck VSM SMRT and MegaLights samples at Medium. Noisy soft shadows read worse than slightly harder ones.

Example `Config/DefaultScalability.ini` overrides:
```ini
[ReflectionQuality@2]
r.Lumen.Reflections.DownsampleFactor=1       ; full-res reflections at High for glossy balls

[GlobalIlluminationQuality@2]
r.Lumen.HardwareRayTracing.HitLighting.Allowed=0

[TextureQuality@2]
r.Streaming.PoolSize=1200                    ; hero 2K-4K textures at High
```

## Device profiles (per platform/hardware class)

```ini
; Config/DefaultDeviceProfiles.ini
[Windows DeviceProfile]
DeviceType=Windows
BaseProfileName=
+CVars=r.Streaming.PoolSize=1500
+CVars=sg.ResolutionQuality=75
```
- Device-profile CVars also outrank scalability. Use them for platform caps (pool size, max anisotropy), not for values the user menu should change.
- Steam Deck or other handhelds: separate profile with Medium (Lumen Lite) as the 5.8 target and lower resolution.

## Auto-detect and user settings

- `[ScalabilitySettings]` `PerfIndexThresholds_*` in BaseScalability map a CPU/GPU benchmark to levels.
- Call `UGameUserSettings::RunHardwareBenchmark` then `ApplyHardwareBenchmarkResults` (Blueprint: *Run Hardware Benchmark*) on first launch only.
- Expose per-group settings (shadows, GI, reflections, post, textures, resolution/upscaler) rather than one master preset. Lumen and resolution are the two that matter most to players.
- Changing `sg.GlobalIlluminationQuality` or `sg.ReflectionQuality` at runtime switches Lumen paths (Lite ↔ High). Expect a few frames of GI re-convergence. Apply settings in a menu, not mid-shot.
