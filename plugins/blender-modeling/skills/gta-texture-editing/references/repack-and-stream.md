# Re-packing textures and streaming them (Legacy + Enhanced)

Read when creating or editing a `.ytd`, embedding textures, repointing materials to new texture
names, or when an edited texture does not show in game. Tags as in SKILL.md.

## Embedded vs separate YTD

| | Embedded (inside `.ydr/.yft/.ydd`) | Separate `.ytd` |
|---|---|---|
| Lookup | The drawable's own texture dictionary, resolved first [Src] | By name via the archetype's `textureDictionary` (ytyp), then the parent chain |
| Sharing | One drawable only | Many drawables and LODs can use one YTD |
| Size counts toward | The drawable's memory (oversize warning on the `.ydr`) | The `.ytd` |
| Typical use | Unique small props, patch planes | Building copies, sets of MLO parts, LOD models |
| Edit in CodeWalker | Model viewer → **Texture Editor** ("Couldn't find embedded texture dict." if none) | Open the `.ytd` directly |

Rule: a texture used by more than one drawable goes into one shared YTD; do not embed it in each.

## CodeWalker workflow (Gen8 or Gen9 depends on its mode)

- CodeWalker saves resources in the format of the **game folder it is set to**. With a GTA V Enhanced folder
  (contains `gta5_enhanced.exe`), window titles end in "(GTAV Enhanced)" and `Save` writes **Gen9** (YTD
  resource version 5). With a Legacy folder it writes **Gen8** (version 13). [Src: GTAFolder, YtdFile.GetVersion]
  Never save the Legacy deliverable from an Enhanced-mode CodeWalker. `rsc_gen.py` (automation.md)
  checks the result.
- New YTD: RPF Explorer → Edit mode → right-click in a folder → **New → YTD File…** → name it. [Src]
- YTD window buttons: **Add…**, **Replace…**, **Remove**, the "Name:" field (rename), File → **Save All
  Textures…**, plus a **Details** tab (Usage, flags, G9 fields). With Add…, **texture name = DDS file name
  without extension**; a name that already exists is rejected ("All textures must have unique names in a
  YTD"). [Src: YtdForm]
- Replace a texture: keeps the original's **Name, Usage, UsageFlags**. Add does not set Usage, so it stays
  `UNKNOWN`. Clean copy workflow: duplicate the vanilla YTD file, rename the file, Replace the edited textures,
  delete the textures you do not use, then rename the textures to your names (rename keeps Usage). Whether
  `Usage UNKNOWN` matters in game is unverified (verify). [Src: YtdForm]
- Repoint a material: Model viewer → **Material Editor** → select the geometry → type the new name into
  `DiffuseSampler`/`BumpSampler`/`SpecSampler` → Save. Embedded entries are read-only there
  ("(embedded)"); rename them in the Texture Editor instead. [Src: ModelMatForm]
- Archetype link: set `textureDictionary` of the archetype in your `.ytyp` to your YTD name (without
  `.ytd`). Building with Sollumz instead: `fivem-mlo-creation`.

### YTD via XML (scriptable)

CodeWalker "Export XML" writes `<name>.ytd.xml` plus a folder `<name>/` of DDS files. "Import XML" on
`<name>.ytd.xml` reads the DDS files from the folder `<name>/` **next to it** and writes `<name>.ytd` in
CodeWalker's current game mode (Gen8/Gen9). [Src: ExploreForm.ImportXml] On import, **size, mips and
format come from the DDS file**; Name, Usage and UsageFlags come from the XML. Errors:
`Texture file not found:` / `Texture file format not supported:`. [Src: Texture.ReadXml]
`make_ytd_xml.py` (automation.md) generates the XML.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TextureDictionary>
  <Item>
    <Name>mymlo_facade_d</Name>
    <Unk32 value="0" />
    <Usage>DIFFUSE</Usage>
    <UsageFlags>UNK24</UsageFlags>
    <ExtraFlags value="0" />
    <Width value="2048" />
    <Height value="2048" />
    <MipLevels value="10" />
    <Format>D3DFMT_DXT1</Format>
    <FileName>mymlo_facade_d.dds</FileName>
  </Item>
</TextureDictionary>
```

Usage values: `DIFFUSE`, `NORMAL`, `SPECULAR`, `EMISSIVE`, `DETAIL`, `TINTPALETTE`, `DEFAULT`, …
`UsageFlags` is a flag enum (`UNK24` is "used by almost everything" per CodeWalker's comment). Copy the
values from an exported vanilla XML instead of guessing. [Src]

## Sollumz workflow (2.9.0+, Aug 2026)

- **Texture Dictionaries** panel: create a TXD and add textures by hand, or add **Sources** (object or
  collection). Sources collect every image their Sollumz shaders use; embedded images are off by default. [Src + Doc]
- Texture name = image file name (basename, lower case). To rename, rename the file and reload. [Src]
- Only DDS images are exported. PNG/JPG or a missing file logs a warning and becomes a 16x16
  magenta/black checkerboard. Packed images must contain DDS bytes. [Src: szio]
- "HD" toggle per texture: the full resolution goes to `<txd>+hi.ytd` and the base YTD gets half resolution
  (first mip dropped, so the DDS needs mips). This works for embedded textures too (`+hidr/+hifr/+hidd`). [Src]
  If you ship only the base YTD, players see half resolution.
- Embedded: tick **Embedded** on the image node (material → Sollumz panel).
- Gen8/Gen9: chosen in the export settings (2.8.0+). Binary export needs the optional **PyMateria**
  dependency (Windows); otherwise export CodeWalker XML and import it in CodeWalker. [Src: dependencies.py]

## Parent texture dictionaries (optional)

For several YTDs that share base textures, declare a parent so children look up missing names in it:

```xml
<!-- data/gtxd.meta -->
<CMapParentTxds>
  <txdRelationships>
    <Item>
      <parent>mymlo_shared</parent>
      <child>mymlo_facade</child>
    </Item>
  </txdRelationships>
</CMapParentTxds>
```
```lua
files { 'data/gtxd.meta' }
data_file 'GTXD_PARENTING_DATA' 'data/gtxd.meta'
```
[Doc: data-files `GTXD_PARENTING_DATA` / `CMapParentTxds`; XML shape from CodeWalker GtxdFile parser]
Never make a vanilla txd the child or parent.

## Naming

- Lower case, ASCII, no spaces, project prefix: `mymlo_facade_d`, `mymlo_facade_n`, `mymlo_facade_s`,
  `mymlo_facade_night`; YTD `mymlo_facade.ytd`.
- Rename **every** map of the set and repoint **every** sampler. Renaming only the diffuse is a
  common mistake: the game still loads the vanilla `_n` (door bumps) and `_s`.
- A streamed file with a vanilla file name **replaces** that file globally, and file names must be unique
  across running resources (see `fivem-server-setup`). Use vanilla names only for an intentional global
  override, which conflicts with any other resource doing the same.

## Streaming

```
my_mlo/
  fxmanifest.lua          -- this_is_a_map 'yes', ytyp data_file: see fivem-mlo-creation
  stream/                 -- Gen8 (Legacy): mymlo_facade.ytd, mymlo_ext.ydr, ...
  stream_enhanced/        -- Gen9 (Enhanced): the same names, converted
```

- Legacy ignores `stream_enhanced/`. Enhanced loads **only** `stream_enhanced/` when that folder exists, and falls back
  to `stream/` (deprecated) when it does not. So after every texture change, **rebuild both copies**. A stale Gen8 file
  in `stream_enhanced/`, or a stale Gen9 file there, is the most common reason for "works on one, not the other". [Doc]
- Gen8 to Gen9: Alchemist (official, Windows 11, converts YDR/YTD/YFT/YPT/YDD) [Doc], CodeWalker Tools → Asset
  Converter, or a direct Gen9 export from Sollumz. Details and CLI: `fivem-gta5-enhanced`.
- Gen9 texture specifics [Src: CodeWalker `EnsureGen9`]: `G9_Flags` default `0x00260208` (2490888) and
  `0x00260228` (2490920) for `script_rt_*`. `script_rt_*` must be uncompressed without mips (ERR_GFX_STATE
  otherwise, see `fivem-gta5-enhanced`). Building textures need no manual flags.
- Size: keep each YTD and each drawable with embedded textures well under 16 MiB (FiveM oversize
  warning; details in `fivem-server-setup` streaming-assets).
- Test: restart the whole server for map assets (restarting a stream resource with players online can crash
  clients). Client cache problems: clear the FiveM cache folder if an old texture persists (verify path per
  platform).
