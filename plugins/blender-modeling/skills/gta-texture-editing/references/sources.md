# Sources (all accessed 2026-10-10)

Method: docs.sollumz.org, docs.gimp.org and gitlab.gnome.org could not be fetched from the
research environment. Tool behaviour was read from source code (shallow `git clone` of public repos)
and is tagged **[Src]** in the skill. Search-engine summaries are marked "snippet" and back only items
tagged [Reported] or (verify).

## Read directly (source code / official docs repos)

| Source | Backs up |
|---|---|
| https://github.com/dexyfex/CodeWalker (HEAD `485d56b`, 2025-04-11): `CodeWalker.Core/GameFiles/Resources/Texture.cs` | Gen8 `TextureFormat` enum (DXT1/3/5, ATI1/2, `BC7 ` FourCC, A8R8G8B8 …), Gen9 `TextureFormatG9`, legacy↔Gen9 mapping (UNORM only, sRGB TODOs), `EnsureGen9` G9_Flags `0x00260208`/`0x00260228` for `script_rt_`, `TextureUsage`/`UsageFlags` enums, YTD XML fields and import from DDS |
| CodeWalker `CodeWalker.Core/GameFiles/Utils/DDSIO.cs` | DDS import maps only `*_UNORM` DXGI formats; `_SRGB`/typeless → format 0; unsupported-format exceptions |
| CodeWalker `CodeWalker/Forms/YtdForm.cs` | Add (name = file name, unique names message), Replace keeps Name/Usage/UsageFlags, Rename, "Unable to load … valid .dds" message, save-outside-mods warning |
| CodeWalker `CodeWalker/ExploreForm.cs` | New → YTD File…, Import XML path convention (DDS folder named like the YTD) |
| CodeWalker `CodeWalker/Forms/ModelForm.cs`, `ModelMatForm.cs` | Texture Editor for embedded textures ("Couldn't find embedded texture dict."), Material Editor renames non-embedded texture refs, embedded read-only, Save all/shared textures |
| CodeWalker `GameFileCache.cs`, `Rendering/Renderer.cs`, `FileTypes/GtxdFile.cs` | Texture lookup order, `gtxd.ymt`/`gtxd.meta` `CMapParentTxds` parent chain, `_manifest.ymf` `HDTxdAssetBindings`, resident `mapdetail`/`vehshare` |
| CodeWalker `FileTypes/YtdFile.cs` (+ Ydr/Ydd/Yft/Ypt `GetVersion`), `Resources/ResourceBuilder.cs`, `CodeWalker/Utils/GTAFolder.cs` | Saves Gen9 when set to an Enhanced folder (`gta5_enhanced.exe`, "(GTAV Enhanced)" title); RSC7 header layout; versions ytd 13/5, ydr/ydd 165/159, yft 162/171, ypt 68/71 |
| CodeWalker `CodeWalker.Shaders/Common.hlsli`, `BasicPS.hlsl` (decompiled R* shader comments) | Normal map uses R,G only, Z rebuilt; spec intensity = dot(spec.rgb, specMapIntMask), alpha × specularFalloffMult; vertex colour0 R/G × ambient scalars; decal alpha × colour0 alpha |
| https://github.com/Sollumz/Sollumz (HEAD `07d6a49`, 2026-10-10): `ytd/ytdexport.py`, `ytd/properties.py`, `ydr/ydrexport.py` | TXD panel/sources, texture name = file name, DDS-only export, HD → `+hi` with first mip dropped, embedded textures |
| Sollumz `ydr/shader_materials.py`, `tools/meshhelper.py`, `dependencies.py` | Tint palette preview (column = colour0 blue, colour1 for trees; row = tint value), V flip on import, PyMateria optional (Windows) for binary I/O, szio 1.4.0.dev1 |
| szio 1.4.0.dev1 wheel (PyPI): `gta5/native/adapters/texture.py`, `texture_gen9.py`, `_utils.py`, `dds.py`, `gta5/Shaders.xml`, `gta5/shader.py` | Checkerboard fallback + warning texts, mip clamp to 4x4, Gen8 formats incl. BC6/BC7, shader names (emissivenight*, *_tnt, decal*), sampler lists, `normal_spec` defaults (`specMapIntMask` 1,0,0) |
| https://github.com/Sollumz/Sollumz/releases (WebFetch) | 2.9.0 TXD support and HD `+hi`; 2.8.3 DDS bad mip count fix; 2.8.1 packed textures; 2.8.0 Gen8/Gen9 export |
| https://github.com/Sollumz/Sollumz/wiki (HEAD `2027ce6`, 2025-05-25) | Older guidance: DDS only, power-of-two sizes, embedded vs YTD + ytyp link |
| https://github.com/microsoft/DirectXTex (HEAD `1acf4eb`, 2026-10-06): `Texconv/texconv.cpp`, `CHANGELOG.md`, `skills/texture-converter` | texconv options (`-f -m -l -o -y -srgb -srgbi -srgbo --ignore-srgb -bc -nogpu -dx9 -pow2 --bad-tails`), format aliases, `--ignore-srgb` added 2025-03-24, Windows-only build |
| DirectXTex `DirectXTexWIC.cpp`, `DirectXTexConvert.cpp`, `DirectXTexCompress.cpp`, `DirectXTexMipmaps.cpp` | PNG `sRGB`/`gAMA` chunk → `_SRGB` load; implicit sRGB→linear when the target is UNORM; IN+OUT cancel |
| https://github.com/GNOME/gimp (mirror, HEAD `d3e807f`, 2026-10-10) `plug-ins/file-dds/dds.c`, `ddswrite.c` | GIMP DDS export labels (BC1–BC5, BC7, mipmap options, sRGB/gamma options), UNORM DXGI output |
| https://github.com/0xC0000054/pdn-ddsfiletype-plus (`f3b4354`, 2026-02-04) `src/DdsWriter.cs`, `Resources.resx` | Paint.NET labels; "Linear" = UNORM without conversion, "sRGB" = `_SRGB` |
| https://github.com/citizenfx/fivem-docs (HEAD `c2b2125`, 2026-10-01): `alchemist/_index.md`, `developers/legacy-vs-enhanced.md` | Alchemist (Win 11; YDR/YTD/YFT/YPT/YDD), `stream`/`stream_enhanced` rules |
| fivem-docs `game-references/data-files.md` | `GTXD_PARENTING_DATA` = `CMapParentTxds` |
| fivem-docs `assets-manual/beginner-series/part-2.md`, `part-3.md` | Save All Textures / Find Missing Textures; DDS + NVTT recommendation; Embedded toggle |
| https://github.com/advimman/lama, https://github.com/Sanster/IOPaint (`61a759f`), https://github.com/enesmsahin/simple-lama-inpainting | Apache-2.0 code licences, Places365 training data, IOPaint CLI, SimpleLama API (RGB + mask 255) |
| This repo: `fivem-server-setup/references/streaming-assets.md`, `fivem-gta5-enhanced/references/assets-and-streaming.md` | 16 MiB oversize thresholds, unique file names, `script_rt_` and 128-material Gen9 pitfalls |

## Search snippets only

| URL | Backs up |
|---|---|
| https://docs.sollumz.org/documentation/texture-dictionaries | TXD panel, sources, HD toggle needs mipmaps (snippet) |
| https://docs.sollumz.org/tutorials/creating-interiors/texturing | Power-of-two incl. non-square (32x16, 512x16), DDS only (snippet) |
| https://docs.sollumz.org/tutorials/asset-conversion-for-gtav-enhanced | script_rt RGBA8 without mips, G9_Flags 2490920 (snippet) |
| https://docs.gimp.org/3.2/de/file-dds-export.html | GIMP 3.2 DDS export lists BC7 (snippet) |
| https://www.gta5-mods.com/tools/texture-toolkit | Texture Toolkit by Neodymium, 2016, embedded textures (snippet) |
| https://libertycity.net/files/gta-5/87242-openiv-2.6.3.html, https://vgtimes.ru/games/gta-5/files/91228-openiv-enhanced-fix-2-1.html | OpenIV 2.6.3 YTD editing (2023); third-party Enhanced fixes (snippet) |
| https://forum.cfx.re/t/how-to-optimize-texture-size-fixing-oversized-assets-bring-any-texture-dictionary-under-16-mb-physical-memory/1764640 | Oversized texture dictionaries → texture loss; resize workflow (snippet) |
| https://forums.nexusmods.com/topic/9361293-intel-textureworks-alternative-for-photoshop-2021, https://forums.developer.nvidia.com/t/nvidia-texture-tools-exporter-will-not-install-in-photoshop-cc-2020/123492/1 | Intel Texture Works abandoned; NVTT Exporter as the Photoshop route (snippet) |
| https://forums.getpaint.net/topic/111731-dds-filetype-plus-9-5-2024/page/7 | User report: sRGB export variants look washed out elsewhere (snippet) |
| https://forum.cfx.re/t/lod-and-slod/2550075, https://forum.cfx.re/t/mlo-textures/4789730 | LOD/SLOD show separately; retexture distant versions too (snippet) |

## Tested locally (2026-10-10)

Scripts in automation.md, run on Linux with Python 3.13, OpenCV 5.0.0, Pillow 12.3.0, numpy 2.5.3, against
synthetic textures and DDS/RSC7 headers. texconv commands were checked against the source, not executed.
The LaMa path was not run.
