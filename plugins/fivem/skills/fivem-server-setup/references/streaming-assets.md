# Streaming custom assets - checklists

Read before adding vehicles, maps/MLOs, clothing or other streamed files, or when a streamed asset is invisible/crashes clients.

## General rules

- Files in `stream/` (subfolders allowed) are streamed automatically; no manifest entry needed. Meta/XML data files are **not** in `stream/` - they go in e.g. `data/` and need `files {}` + `data_file`.
- File names must be unique across all running resources (two `police.yft` -> only one is used, depending on start order). Prefix custom models.
- Size: the server warns per asset above 16 MiB physical/virtual memory (yellow), 32 (orange), 64 (red); above 48 MiB it adds "Oversized assets can and WILL lead to streaming issues". Keep `.ytd` well below 16 MiB: 1024-2048 px max, BC/DXT compression, mipmaps, split large dictionaries.
- Every streamed file is downloaded by every client on join; large packs = long joins and `Server->client connection timed out` for slow clients. Remove unused assets.
- Restarting a stream resource while players are online can crash clients - restart the server or test locally.
- XML ymap/ytyp may be streamed raw (file named `x.ymap` containing XML) but are parsed by the game parser - prefer binary from CodeWalker.

## Add-on vehicle

```
my_cars/
  fxmanifest.lua
  stream/  mycar.yft  mycar_hi.yft  mycar.ytd  (+ mycar+hi.ytd if provided)
  data/mycar/  vehicles.meta  carvariations.meta  carcols.meta  handling.meta  [vehiclelayouts.meta]
```
```lua
fx_version 'cerulean'
game 'gta5'
files { 'data/**/*.meta' }
data_file 'HANDLING_FILE'          'data/**/handling.meta'
data_file 'VEHICLE_METADATA_FILE'  'data/**/vehicles.meta'
data_file 'CARCOLS_FILE'           'data/**/carcols.meta'
data_file 'VEHICLE_VARIATION_FILE' 'data/**/carvariations.meta'
data_file 'VEHICLE_LAYOUTS_FILE'   'data/**/vehiclelayouts.meta'
```

Checklist when the car is invisible, "model not found", or spawns as default handling:
- [ ] `modelName` in vehicles.meta = `.yft` file name = spawn name; `txdName` = `.ytd` name.
- [ ] `handlingId` in vehicles.meta = `handlingName` in handling.meta (case-sensitive, unique; reusing a base-game handling name overrides that car's handling).
- [ ] carvariations `modelName` matches; `kits` ids in carcols are unique (modkit ID collisions across packs break tuning/liveries).
- [ ] All meta files listed in `files` **and** `data_file`; paths/globs correct.
- [ ] Vehicle uses DLC parts/layouts -> `sv_enforceGameBuild` high enough.
- [ ] Display name: add a text entry (client `AddTextEntry('MYCAR', 'My Car')` matching `gameName`) or the label shows `NULL`/`CARNOTFOUND`.
- [ ] ``IsModelInCdimage(`mycar`)`` on the client returns true.
- [ ] Server-side spawn: ``CreateVehicleServerSetter(`mycar`, '<type from vehicles.meta>', ...)`` - wrong type (e.g. `automobile` for a bike) misbehaves.

Replacement (not add-on) of a base vehicle: stream files with the original names (`adder.yft`, `adder_hi.yft`, `adder.ytd`); handling via `HANDLING_FILE` with the original `handlingName`.

## Maps / MLOs (ymap, ytyp, ybn, ydr, ytd)

```lua
fx_version 'cerulean'
game 'gta5'
this_is_a_map 'yes'
-- many MLO packs also declare their archetype file:
-- data_file 'DLC_ITYP_REQUEST' 'stream/my_mlo.ytyp'
```
- Include `_manifest.ymf` (CodeWalker: Tools -> Manifest Generator) so props/archetypes load correctly.
- Two maps editing the same area/ymap entities -> flickering, missing collisions, double buildings. Check for overlapping MLOs and for maps that replace the same vanilla ymap.
- Interior proxies / occlusion: missing `ybn` (collision) -> falling through floors; wrong occlusion -> invisible walls/flicker.
- Big packs: `increase_pool_size` (e.g. `InteriorProxy`, `OcclusionPathNode`, `TxdStore`, `Building`) within the allowed limits; check F8 -> Tools -> Streaming -> Pool Monitor.
- Doors in MLOs need door system entries (e.g. ox_doorlock) using the exact door model hash and coords.

## Clothing (MP freemode)

- Add-on clothing pack: `stream/` holds the `.ymt` (e.g. `mp_m_freemode_01_mp_m_mypack.ymt`) and drawables/textures named with `^` as a folder separator (e.g. `mp_m_freemode_01_mp_m_mypack^jbib_000_u.ydd`, `..._diff_000_a_uni.ytd`); this uses the subdir file mapping feature (resources can require it with `dependency '/policy:subdir_file_mapping'`). Generate packs with a clothing tool rather than renaming by hand.
- Shop/apparel metadata (if the pack ships it): `files { 'mp_m_freemode_01_mypack.meta' }` + `data_file 'SHOP_PED_APPAREL_META_FILE' 'mp_m_freemode_01_mypack.meta'`.
- Component/drawable IDs shift when packs are added/removed or reordered - saved outfits in the DB point to different items afterwards. Freeze the pack order (resource names, ensure order) once live.
- Too many drawables per component/texture variations can exceed engine limits; split into several packs.
- Keep each `.ytd` small (clothing textures 512-1024 px); oversized clothing textures are a common cause of texture loss.

## Other data files

Weapons (`WEAPONINFO_FILE`, `WEAPON_ANIMATIONS_FILE`, `WEAPONCOMPONENTSINFO_FILE`, `PED_PERSONALITY_FILE`), audio (`AUDIO_WAVEPACK` folder, `AUDIO_GAMEDATA` / `AUDIO_SOUNDDATA` `.dat151.rel` / `.dat54.rel` files), scenarios (`SCENARIO_POINTS_OVERRIDE_PSO_FILE`), timecycles (`TIMECYCLEMOD_FILE`): always `files` + `data_file`, file types from the official data-files reference. Wrong type -> silently ignored or client crash on join.
