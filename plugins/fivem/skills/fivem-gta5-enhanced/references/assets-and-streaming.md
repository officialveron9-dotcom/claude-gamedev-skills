# Assets and streaming on Enhanced (Gen9)

Tags: [Official], [Reported], [Unknown].

## Folder rules [Official, docs + patch notes 2026-08-31 / 09-22 / 09-24]

- A resource may contain `stream/` and `stream_enhanced/`.
- On Enhanced: if `stream_enhanced/` exists, only it is loaded and `stream/` is skipped (wildcard
  matching fixed 2026-09-24). Without `stream_enhanced/`, `stream/` is used, but the server warns that
  this is deprecated.
- For cross-compatible resources, put Gen8 files in `stream/` and Gen9 files in `stream_enhanced/`.
  Legacy keeps using `stream/`.
- Base-game overrides with the same filename (e.g. `minimap.gfx`) apply again since Hotfix 3.
- Resource names with uppercase letters: client file lookups were fixed on 2026-09-22.
- Pools: `dwdStore` sizes itself from streamed `.ydd` files (09-22), and several pools extend
  automatically (08-31). `increase_pool_size` is still reported broken for `CWeaponComponentInfo`
  (rfc #524).
- Downloads: the 25 MB/s cap was removed (09-22), and failed validations are retried. Files carry
  hashes for cache validation (08-31).

## Do Gen8 assets work unconverted?

- Cfx built Alchemist because Gen8 3D resources need conversion. Several community guides report
  that unconverted Legacy `.yft/.ytd` (vehicles, clothing, MLO drawables) do not load or render on
  Enhanced. [Reported, consistent with the official tooling]
- Hotfix 3 fixed "asset version mismatch errors on streamed files" that stopped default resources
  like Qbox from starting. The server and client do check asset versions. [Official]
- Rule: convert every `.ydr/.ytd/.yft/.ydd/.ypt` before deploying, and test in game.

## Alchemist (official converter) [Official, docs.fivem.net/docs/alchemist]

- Released 2025-11-20. Download from the Cfx Portal (portal.cfx.re/downloads). Requires **Windows 11**.
- Supported types: **YDR, YTD, YFT, YPT, YDD**.
- Modes: Asset Conversion (Gen8 to Gen9) and Asset Refinement (fixes Legacy assets made with old
  tools). Relaxed Mode skips some validation and auto-fixes, so output may differ slightly.
- If you point it at the server `resources/` folder, it produces a drop-in replacement folder.
  Non-asset files (scripts, UI, config) are copied unchanged. [Official + Reported detail]
- CLI: `AlchemistCli.exe <input> <output> [--refine] [--relaxed] [-f] [-jN] [--fail-on-error]`
  (default 10 threads). On first run it asks you to accept the ToS and choose telemetry.
- Known issue: the GUI aborts on escrowed assets. Use the CLI, which skips them and lists them in the
  report, or remove them first.
- It does not handle `.ymap`, `.ytyp`, `.ybn`, `.ycd`, `.ynv`, `.meta`/`.ymt` or audio. Community
  summaries claim the Alchemist announcement said `.ybn`/`.ycd` need no conversion; one blog lists bounds
  as version 43 on both. [Reported, unverified] Test collisions and animations in game.

## Third-party tools [Reported]

- **CodeWalker** (30 dev48+; Discord #releases): RPF Explorer > Tools > Asset Converter converts
  YTD/YDR/YDD/YFT/YPT to Gen9; XML import/export for Gen9.
- **Sollumz** (Blender; 2.9 per a Cfx forum post): exports Legacy or Enhanced binaries directly. YMAP and
  YCD still go through CodeWalker XML.
- **OpenRPF** (gta5-mods) is a single-player Enhanced loader. It is irrelevant for FiveM, so do not
  tell FiveM players to install it.

## Gen9 asset pitfalls [Reported, Sollumz wiki 2026-09]

| Symptom | Cause | Fix |
|---|---|---|
| `ERR_GFX_STATE` crash when entering a vehicle | `script_rt_*` texture in the `.ytd` is compressed (DXT5/BC3) | Re-save as uncompressed RGBA8 (`D3DFMT_A8R8G8B8`) without mipmaps; set G9_Flags to `2490920` in CodeWalker if it was not set |
| Crash on spawn or approach, before entering | More than **128 materials/geometries** in one file | Re-export through Sollumz (CW XML, Blender, XML) to merge, or ask the author for an optimized model |
| Vehicle textures look low-res | Client downscaled them (bug) | Fixed in Hotfix 8 (full 2048 again) [Official] |
| Custom ped models invisible | Open bug on b153 (rfc #543) | None yet [Official report] |
| 3+ add-on vehicles via `VEHICLE_METADATA_FILE` crash in `INIT_SESSION` | Bug | Fixed in Hotfix 8 [Official] |
| Client freezes at 100% loading with `data_file` mounts | Regression in server b157 (rfc #567) | Use server b156 [Official report] |

## DX12 and ray tracing

- GTA V Enhanced is DX12 with optional ray tracing. Press reports say FiveM Enhanced players get RT
  reflections/shadows/AO/GI. [Reported] This is a client graphics setting, not a server option. No
  server convar for RT exists in the docs.
- `3D scaleforms render steadily with TAA enabled` (08-04) and `DUI rendering is no longer flipped`
  (Hotfix 4) are the only render fixes relevant to scripts. [Official]
- Audio: no Enhanced-specific audio streaming notes found. [Unknown] Assume `data_file` audio
  entries work as on Legacy, but test them (see the #567 freeze).
