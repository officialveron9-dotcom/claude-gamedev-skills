# Content, memory, streaming, PSOs, package size (UE 5.8)

Contents: texture streaming and compression · VRAM consumers · skeletal LODs/animation cost · HLOD · draw calls · PSO and shader stutter · package size.

## Texture streaming

- Symptom: on-screen *"TEXTURE STREAMING POOL OVER … BUDGET"*, blurry hero textures, mips popping in late.
- Diagnose:
  - `stat streaming` (pool, over-budget, wanted vs resident).
  - `ListTextures` (biggest offenders).
  - *Optimization Viewmodes > Required Texture Resolution / Mesh UV Densities*.
- Pool per TextureQuality tier (5.8 BaseScalability): 400 / 600 / 800 / 1000 / 3000 MB. `r.Streaming.LimitPoolSizeToVRAM=1` at Low-High.
- Fix order:
  1. **Right-size at the source.** No 4K-8K on small props. Hero felt, ball atlas and rails get the budget (see the texel table in the lighting skill's materials reference).
  2. Per-texture *Maximum Texture Size* / *LOD Bias*, or texture-group LOD bias in device profiles for whole classes.
  3. Run *Build > Build Texture Streaming* so streaming has accurate texel factors.
  4. Only then raise `r.Streaming.PoolSize` per tier/device profile, if VRAM allows.
  5. Streaming Virtual Textures for many large unique textures (`r.VirtualTextures=1`).
- `r.Streaming.MipBias` (Low tier 16!) and `r.Streaming.Boost` are tier-controlled. Don't set them in DefaultEngine.ini (the priority trap; see scalability.md).
- *Never Stream*: only for UI/critical small textures. Every never-streamed 4K texture is permanent VRAM.

Compression settings (per texture):

| Content | Setting | Note |
|---|---|---|
| Albedo (no alpha) | Default (BC1) or BC7 for hero | BC7 for felt/ball albedo avoids banding; double size |
| Normal maps | Normalmap (BC5) | Never sRGB |
| Packed masks (ORM) | Masks (no sRGB) | Wrong sRGB breaks roughness |
| Single channel | Grayscale/Alpha (BC4) | |
| HDR / emissive maps | HDR Compressed (BC6H) | |
| UI | UserInterface2D | No mips, no streaming |
| Disk size | *Lossy Compression Amount* (Oodle Texture RDO) | Smaller packages; check artifacts on felt gradients |

## VRAM consumers to check on 8 GB GPUs

- Texture pool (above).
- VSM physical pages: Epic 4096, Cine 8192 (`r.Shadow.Virtual.MaxPhysicalPages`).
- Lumen surface cache atlas (`r.LumenScene.SurfaceCache.AtlasSize`: 2048-4096).
- HWRT acceleration structures: skeletal and dynamic meshes, plus the RT geometry of every visible-in-RT actor.
- Nanite streaming pool.
- Render targets: resolution × GBuffer (Substrate bytes per pixel) × TSR history (200 % at Epic).
- Diagnose with `memreport -full` per tier. Look at RHI memory and texture lists.

## Characters: LODs and animation cost

- Close shots need LOD0, but players across the room don't.
  - Generate LODs (Skeletal Mesh LOD Settings / reduction) and set LOD screen sizes.
  - Tier bias is automatic: `r.SkeletalMeshLODBias` 2/1/0/0/0 across Low-Cine.
- Trap: *Forced LOD* left on from a cinematic keeps LOD0 everywhere.
- Animation cost (game thread / worker threads):
  - *Visibility Based Anim Tick Option*: don't tick pose when not rendered.
  - Update Rate Optimizations for distant characters.
  - The Animation Budget Allocator plugin caps total animation cost when many NPCs are present.
- Hair: strand grooms on every bar NPC are expensive. Use groom LODs or cards for non-hero characters, and strands only for close-up players. `r.HairStrands.*` quality is ShadingQuality-tiered.
- Skin cache must stay enabled if characters appear in HWRT reflections (`r.SkinCache.CompileShaders`).

## HLOD

- Single pool-hall room: not needed (Nanite plus a small level).
- Multi-room venue in World Partition: build HLOD layers for rooms not visible, and use data layers to unload back rooms. Non-Nanite distant geometry is where HLOD pays off.

## Draw calls (render/RHI thread)

- Diagnose: `stat rhi` (draw calls/primitives), `stat scenerendering`, Insights render-thread track.
- Fixes, biggest first:
  1. Nanite for static opaque meshes. Nanite draws are batched by material/raster bin, not per mesh.
  2. Repeated props (chairs, bottles, glasses, lamps) as ISM/HISM, or as Packed Level Actors.
  3. Merge Actors for small static clusters that must stay non-Nanite.
  4. Fewer material slots per mesh. Each section is a draw in every pass (depth, base, each shadow page/light).
  5. Fewer shadow-casting lights touching non-Nanite meshes.
- Rule of thumb, not an Epic limit: past a few thousand draw calls on PC, the render thread usually starts to dominate.

## PSO and shader stutter

- Precaching has been on by default since 5.3. PSOs are compiled when components load.
  - If a PSO isn't ready, the default strategy delays proxy creation and skips the draw. Symptom: objects **appear a few frames late** on first sight, instead of a hitch.
  - Strategy CVar: `r.PSOPrecache.ProxyCreationStrategy` (see `help` for values).
  - Global shaders: `r.PSOPrecache.GlobalShaders`.
- Precaching doesn't cover everything (some global/compute/edge-case PSOs). Epic and community guidance is a **hybrid**:
  1. Record a bundled PSO cache in a packaged build launched with `-logPSO`, playing through all content (break, every camera mode, menus, effects).
  2. Merge the recorded `.rec.upipelinecache` files with the ShaderPipelineCacheTools commandlet and ship them.
  3. `r.ShaderPipelineCache.Enabled=1`.
- Test like a player: packaged build, **deleted driver shader cache** (e.g. NVIDIA DXCache / AMD DxCache folders under `%LOCALAPPDATA%`), first run. Watch Insights for PSO creation scopes during the first break shot.
- 5.8 reduced shader permutations engine-wide. Disabling unused rendering features cuts permutations further:
  - Static lighting (`r.AllowStaticLighting=0`)
  - Sky atmosphere (`r.SupportSkyAtmosphere`)
  - Volumetric clouds (`r.VolumetricCloud.Support`)
  - Local fog volumes (`r.SupportLocalFogVolumes`)
  - Unused Targeted RHIs
- Shader compiles in the editor ("Compiling Shaders N") are DDC work, not runtime stutter. Use a shared DDC on multiple machines.

## Package size and cook

1. Disable unused plugins. This is the biggest win for content, shaders and startup.
2. *Project Settings > Packaging*: *List of maps to include*; *Exclude editor content when cooking*; *Use Io Store*; *Create compressed cooked packages*; *Share Material Shader Code* + *Shared Material Native Libraries*; Shipping config without debug files.
3. Compression: Oodle (Kraken for size/speed balance); higher compression level for distribution builds.
4. Textures: right-size, *Lossy Compression Amount* (Oodle RDO), no oversized never-streamed textures.
5. Nanite: *Keep Triangle Percent* / *Trim Relative Error* on over-dense scans.
6. Audit:
   - Size Map and Reference Viewer (who pulls what).
   - Asset Audit window.
   - Fix Up Redirectors.
   - Delete Starter Content and unused marketplace packs. Hard references from a single Blueprint can drag whole packs in.
7. Rendering features/RHIs off (see PSO section): smaller shader libraries.
