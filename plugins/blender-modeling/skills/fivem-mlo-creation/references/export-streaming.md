# Export, CodeWalker import, resource layout, Gen9/Enhanced, in-game testing

Sources: Sollumz 2.9 source (`sollumz_preferences.py`, `sollumz_operators.py`, `dependencies.py`), szio 1.3/1.4
providers, Sollumz wiki, fivem-docs (resource manifest, data files, server commands, assets guide), skill
`fivem-gta5-enhanced` (Alchemist, `stream_enhanced`).

## Sollumz export

Sollumz Tools → General → **Export** (or V → Export RAGE Assets). Settings live in the add-on preferences:

| Setting | Values | Use for an MLO |
|---|---|---|
| Target Formats | **Native** (binary, needs PyMateria, Windows only) / **CW XML** — multi-select | Native when available; CW XML for diffing or without PyMateria |
| Target Game Versions | **Gen8** (Legacy) / **Gen9** (Enhanced) — multi-select | both → output goes into `gen8/` and `gen9/` subfolders |
| Limit to Selected | on (default) | only selected **and visible** objects export |
| Apply Parent Transforms | off (default) | leave off for MLO pieces |
| Mesh Domain | Face Corner (default) | Vertex only for MP freemode heads |
| Export YTYPs / Maps / Texture Dictionaries | off in the generic export; YTYP export defaults to "selected" | tick YTYPs (All) when the ytyp should come along |

What Native writes (szio 1.4): `.ydr .ydd .yft .ytd .ybn .ytyp .ymap` (+ `.yld`). The Gen9 provider has its own
writers for `.ydr/.ydd/.yft/.ytd/.ytyp`; `.ybn` and `.ymap` are written by the same code for Gen8 and Gen9
(consistent with reports that bounds need no conversion). `.ycd` always comes out as XML.

CW XML: `name.ydr.xml`, `name.ybn.xml`, `name.ytyp.xml`; embedded textures are copied next to the XML. Gen9 XML only
differs by Gen9-specific shader parameter defaults (identical for a `normal.sps` test model).

Scripted export: [blender-automation.md](blender-automation.md) (`use_custom_settings=True`, real selection).

### Textures

- Embedded: material → Sollumz → Texture Parameters → "Embedded" (or "Set all Textures Embedded") → the archetype
  `textureDictionary` becomes the drawable name automatically.
- Shared `.ytd`: 2.9 scene texture dictionaries (`export_ytds`), archetype `textureDictionary` = ytd name. Better
  for several drawables sharing wall textures.
- DDS, power of two, mipmaps, ≤ 2048; Sollumz embeds the DDS from disk. Format, painting, re-packing:
  skill `gta-texture-editing`.

## No PyMateria: CW XML → binary with CodeWalker

1. CodeWalker RPF Explorer in edit mode → open the folder or RPF you want the binaries in → drag the `.xml` files in
   (Sollumz tutorial), or right-click → Import XML. CodeWalker writes Gen8 binaries.
2. Gen9: CodeWalker RPF Explorer → Tools → **Asset Converter** (Dev48+; untick "Include subfolders") converts
   YTD/YDR/YDD/YFT/YPT, **or** Cfx **Alchemist** (`AlchemistCli.exe <in> <out> [--relaxed] [-jN] [-f]`,
   Windows 11). Neither converts `.ytyp/.ymap/.ybn` — copy those unchanged.
3. Restart CodeWalker after adding files to an RPF so the world view picks them up.

## Resource layout

```
abc_mlo_bldg/
  fxmanifest.lua
  stream/                         # FiveM Legacy (Gen8)
    abc_bldg_ext.ydr              # new exterior (option A)
    abc_bldg_int_0.ydr  abc_bldg_int_1.ydr   # interior shell per storey/room
    abc_bldg.ytd                  # if textures are not embedded
    abc_bldg_mlo.ybn              # interior collision, MLO-local, name = MLO archetype
    abc_bldg.ytyp                 # base archetypes + MLO archetype
    abc_bldg_milo_.ymap           # MLO instance
    dt1_05_strm_2.ymap  hei_dt1_05_strm_2.ymap      # patched vanilla copies (archetype swap, occluders)
    dt1_05_0.ybn  hi@dt1_05_0.ybn                   # patched vanilla exterior collision (world space)
    _manifest.ymf
  stream_enhanced/                # FiveM for GTAV Enhanced (Gen9): COMPLETE set
    Gen9 .ydr/.ytd + copies of every .ybn/.ytyp/.ymap/_manifest.ymf above
```

```lua
fx_version 'cerulean'
games { 'gta5', 'gta5enhanced' }   -- Cfx's own cross-platform maps use this; Legacy-only: game 'gta5'
this_is_a_map 'yes'                -- reloads map storage when the resource loads (fivem-docs)

-- Optional. Loads the ytyp permanently (= PERMANENT_ITYP_FILE); needed for archetypes used without a ymap
-- reference, e.g. props/doors spawned by script. Path on Enhanced with stream_enhanced/: verify.
-- data_file 'DLC_ITYP_REQUEST' 'stream/abc_bldg.ytyp'

-- Optional custom timecycle:
-- files { 'data/timecycle_mods_abc.xml' }
-- data_file 'TIMECYCLEMOD_FILE' 'data/timecycle_mods_abc.xml'
```

Rules:
- File names unique across all running resources and lowercase. Two resources streaming the same vanilla ymap
  or ybn → undefined winner (flicker, double buildings, missing collision). Scan with `fivem_conflicttool`.
- Every map resource ships its own `_manifest.ymf` (common practice; verify behaviour with many resources).
- Enhanced loads only `stream_enhanced/` when it exists (wildcard fix 2026-09-24): a missing ytyp/ymap/ybn copy there
  means no MLO on Enhanced although Legacy works.
- Server warns per asset above 16/32/64 MiB; keep `.ytd` small.
- Big map packs: `increase_pool_size "InteriorProxy" <n>` etc. (max increases in
  [mlo-rooms-portals.md](mlo-rooms-portals.md)); check F8 → Tools → Streaming → Pool Monitor.

## Gen9 / Enhanced summary

| Question | Answer (2026-10-10) |
|---|---|
| Does Sollumz export Gen9 directly? | Yes: Native + Gen9 with PyMateria (Windows). CW XML Gen9 also exists but still needs CodeWalker. |
| Do I need Alchemist? | Only if you have Gen8 binaries (e.g. CodeWalker XML import, older exports, bought props). |
| Converted file types | YDR, YDD, YFT, YTD, YPT (Alchemist and CodeWalker converter) |
| Unconverted types | `.ytyp .ymap .ybn .ymf` are copied as is. Sollumz writes a Gen9-flavoured `.ytyp` with Native+Gen9; whether Enhanced requires it is unverified |
| Known Gen9 crash causes | >128 materials/geometries in one drawable; `script_rt_*` textures not A8R8G8B8 (`ERR_GFX_STATE`) — reported |
| CFX interior natives on Enhanced | declared for `gta5`; not verified on Enhanced |

## In-game testing

1. Full disconnect/reconnect after every asset change (the stream is cached; a resource restart is not enough and
   restarting a stream resource with players online can crash clients).
2. Walk the test matrix: approach from far (LOD switch), look through every door and window from outside, enter,
   every room, first person, stairs up/down, jump on furniture, exit, day (12:00) and night (00:00), rain on,
   vehicle through garage doors, second client.
3. `/mloinfo` command from `SKILL.md` in each room: interior id ≠ 0, correct room name, expected flags/timecycle.
4. Tune live with `SetInteriorRoomFlag`, `SetInteriorRoomTimecycle`, `SetInteriorPortalFlag`,
   `SetInteriorRoomExtents` + `RefreshInterior`, then write the values back into Blender and re-export.
5. Check the client log (`CitizenFX.log`) and server console for streaming errors and oversized-asset warnings.
