# Formats, memory and tools

Read when choosing a DDS format, mip count or editor export setting, or when a tool's output does
not load. Tags: **[Src]** read in the tool's source code, **[Doc]** official docs, **[Reported]**
community, **(verify)** unconfirmed.

## GTA texture formats

| Format (CodeWalker name) | DXGI on import/export | Gen8 (Legacy) | Gen9 (Enhanced) | Use for |
|---|---|---|---|---|
| `D3DFMT_DXT1` | `BC1_UNORM` | yes [Src] | `BC1_UNORM` [Src] | Opaque diffuse, normal, spec without alpha |
| `D3DFMT_DXT3` | `BC2_UNORM` | yes | `BC2_UNORM` | Rare; do not choose for new work |
| `D3DFMT_DXT5` | `BC3_UNORM` | yes | `BC3_UNORM` | Diffuse with alpha, spec with gloss in alpha |
| `D3DFMT_ATI1` | `BC4_UNORM` | yes | `BC4_UNORM` | Single channel (rare in maps) |
| `D3DFMT_ATI2` | `BC5_UNORM` | yes | `BC5_UNORM` | Two channels; the game reads normal R,G only, but only use it for `_n` if the original was ATI2 (verify) |
| `D3DFMT_BC7` (FourCC `BC7 `) | `BC7_UNORM` | format exists in Gen8 tools (CodeWalker, PyMateria) [Src]; in-game on FiveM Legacy (verify) | `BC7_UNORM` | Highest quality RGB(A); smooth gradients |
| `D3DFMT_A8R8G8B8` | `B8G8R8A8_UNORM` | yes | `B8G8R8A8_UNORM` | `script_rt_*` render targets only (Gen9: must be uncompressed, no mips) |
| `D3DFMT_A8B8G8R8`, `X8R8G8B8`, `A1R5G5B5`, `A8`, `L8` | `R8G8B8A8`, `B8G8R8X8`, `B5G5R5A1`, `A8`, `R8` | yes | yes | Special cases, palettes (verify per shader) |

- CodeWalker imports **only `*_UNORM`** DXGI formats. `BC1_UNORM_SRGB`, `BC3_UNORM_SRGB`, `BC7_UNORM_SRGB`
  and `*_TYPELESS` map to format 0 (unknown) without an error message, so the texture is
  broken in the saved YTD. [Src: `DDSIO.GetTextureFormat`]
- CodeWalker's Gen9 conversion maps 1:1 to non-sRGB Gen9 formats (`DXT1` to `BC1_UNORM`, …). Its code
  has TODOs for `BC7_UNORM_SRGB`/`BC3_UNORM_SRGB`, so some vanilla Gen9 textures use sRGB formats. [Src]
  Whether a UNORM diffuse looks identical on Enhanced is unverified. Compare in game (verify).
- Match the format of the vanilla texture you are replacing (CodeWalker YTD view shows it) unless you
  have a reason to change it. Decide spec format by whether the original has alpha.
- Size rules: width and height are each a power of two (they may differ, e.g. 2048x1024) [Doc: Sollumz docs].
  BC needs multiples of 4. Use ≤2048 px for facades. 4096 is technically possible, but it is 21 MiB as BC3 and trips
  FiveM's 16 MiB oversize warning by itself.
- Mipmaps: generate a chain that ends at **4 px on the short side**, so `mips = log2(min(w,h)) - 1`
  (1024² is 9, 2048x1024 is 9, 512² is 8). Sollumz/szio clamps BC textures to that count when the DDS fails to
  load with a longer chain (2.8.3 fix "bad mip-map counts"). [Src] A full chain down to 1x1 (texconv `-m 0`)
  is accepted by CodeWalker. Vanilla convention (verify).

## Memory per texture (full mip chain = ×4/3)

| Size | BC1 / BC4 | BC3 / BC5 / BC7 | A8R8G8B8 |
|---|---|---|---|
| 512² | 0.17 MiB | 0.33 MiB | 1.33 MiB |
| 1024² | 0.67 MiB | 1.33 MiB | 5.33 MiB |
| 2048² | 2.67 MiB | 5.33 MiB | 21.3 MiB |
| 4096² | 10.7 MiB | 21.3 MiB | 85.3 MiB |

A facade set (diffuse BC1 + `_n` BC1 + `_s` BC3) at 2048² is about 10.7 MiB. Embedded textures count toward the
drawable's size and separate textures toward the YTD's size. FiveM thresholds and the "Oversized assets" warning
are covered in `fivem-server-setup` (streaming-assets reference).

## sRGB: the one rule

GTA stores gamma-encoded colour in **UNORM** formats. Every tool must write the 8-bit values
unchanged, with no gamma conversion and no `_SRGB` flag.

- **texconv** loads a PNG that has an `sRGB` or `gAMA` (1/2.2) chunk as `R8G8B8A8_UNORM_SRGB`. Converting that to
  `BC1_UNORM` then applies an implicit sRGB-to-linear conversion, so the result is **darker and more
  contrasty** in game. [Src: DirectXTex `ConvertScanline`, WIC/PNG loader] Prevent it:
  - Colour maps: add `-srgb` (marks input and output as sRGB, cancels the conversion, and works in every
    version).
  - Data maps (`_n`, `_s`): add `--ignore-srgb` (texconv 2025-03-24 or newer). With an older texconv, re-save the PNG with Pillow first, which writes no colour chunk.
  - Never use `-srgbo` or `-srgbi` alone, and never use `-f *_SRGB`.
- A file that comes out brighter or washed out had linear-to-sRGB applied (`-srgbo`, an "sRGB" export
  option, or a viewer that treats `_SRGB` data as linear).
- In Photoshop/GIMP/Krita, keep the document in 8-bit or 16-bit sRGB. Do not "Convert to linear" or assign a
  linear profile.

## texconv (DirectXTex, Windows only) [Src: Texconv/texconv.cpp, CHANGELOG]

Install: `winget install Microsoft.DirectXTex.Texconv` or download from github.com/microsoft/DirectXTex/releases.

```bat
:: opaque diffuse, 2048x2048 -> 10 mips (ends at 4x4)
texconv -nologo -y -l -srgb -f BC1_UNORM -m 10 -o dds facade_d.png
:: diffuse with alpha (cutout/decal) or high quality
texconv -nologo -y -l -srgb -f BC3_UNORM -m 10 -o dds facade_d.png
texconv -nologo -y -l -srgb -f BC7_UNORM -m 10 -o dds facade_d.png
:: normal / specular (data, no gamma)
texconv -nologo -y -l --ignore-srgb -f BC1_UNORM -m 10 -o dds facade_n.png
texconv -nologo -y -l --ignore-srgb -f BC3_UNORM -m 10 -o dds facade_s.png
:: extract an existing DDS (from CodeWalker) to PNG for editing, top mip only
texconv -nologo -y -ft png -m 1 -o png facade_d.dds
```

| Flag | Meaning |
|---|---|
| `-f <fmt>` | Output DXGI format (`BC1_UNORM`, `BC3_UNORM`, `BC7_UNORM`, `B8G8R8A8_UNORM`); aliases `DXT1`, `DXT5`, `BPTC` map to UNORM |
| `-m <n>` | Mip levels (`0` = full chain, `1` = none) |
| `-l` | Lower-case output file name (texture name in CodeWalker = file name) |
| `-o <dir>` / `-y` | Output folder / overwrite |
| `-pow2` | Resize to the nearest power of two. Do not use it on facades, because it stretches the texture; fix the canvas instead |
| `-bc d` | Dithering for BC1–BC3, which reduces banding after recolouring; `-bc u` uses uniform weighting |
| `-nogpu` | Force the CPU BC7 encoder, for example when DirectCompute fails |
| `-dx9` | Legacy header; fails for BC7 and strips sRGB. CodeWalker reads both DX9 and DX10 headers, so do not use it |
| `--bad-tails` | Read old DXTn files with broken mips smaller than 4x4 |

## Editors and plugins

| Tool | DDS export setting for GTA | Notes |
|---|---|---|
| **GIMP 3.x** built-in DDS [Src] | Compression `BC1 / DXT1`, `BC3 / DXT5` or `BC7` (BC7 in 3.2+ (verify)); Mipmaps **Generate mipmaps**; Format Default. Colour maps: "Apply gamma correction" + "Use sRGB colorspace" on. `_n`/`_s`: both off | Always writes UNORM; the two gamma options only change mip filtering, not the top level. The BC3nm/RXGB/YCoCg/AEXP variants are wrong for GTA |
| **Paint.NET 5.x** (DDS FileType Plus) [Src] | `BC1 (Linear, DXT1)`, `BC3 (Linear, DXT5)`, `BC7 (Linear, DX 11+)`, Generate mipmaps | The "Linear" labels write UNORM with the pixels unchanged, which is correct. `(sRGB, DX 10+)` writes `_SRGB`, which CodeWalker does not read |
| **Photoshop** | NVIDIA Texture Tools Exporter: BC1/BC3/BC7, generate mips, do **not** pick sRGB variants | Intel Texture Works is abandoned; reports say it breaks on newer Photoshop [Reported]. FiveM's docs recommend NVTT [Doc] |
| **Krita** | Export PNG, convert with texconv | Its DDS export is limited (verify) |
| **CodeWalker** (YTD viewer) | Imports DDS only, exports DDS ("Save Texture As…", "Save all textures") | Does no conversion. See repack-and-stream.md |
| **Sollumz** (Blender) | Accepts **DDS only** for export. Other formats log "Embedded texture '<img>' is not in DDS format" and become a 16x16 magenta/black checkerboard [Src: szio] | Texture name = image file name, lower-cased [Src] |
| **OpenIV** | Texture editor for Legacy YTDs (2.6.3, 2023) [Reported] | Not built for Enhanced. Third-party "Enhanced fixes" exist; do not rely on them for Gen9 YTDs [Reported] |
| **Texture Toolkit** (Neodymium, 2016) | Edits textures embedded in YDR/YFT/YDD/YPT | Legacy only and outdated [Reported]; use CodeWalker's Texture Editor instead |

## Inpainting tools and licences

| Tool | Licence (code) | Notes |
|---|---|---|
| OpenCV `cv2.inpaint` (Telea/NS) | Apache-2.0 | Good for small areas and noise; blurs brick/tile patterns. Tested in automation.md |
| LaMa (`advimman/lama`), `simple-lama-inpainting`, IOPaint | Apache-2.0 | Big-LaMa weights are trained on Places365. Check the dataset terms before selling the MLO (verify). Handles RGB only; restore alpha afterwards |
| Stable Diffusion inpainting (SD 1.5/2 inpaint, SDXL inpaint) | CreativeML OpenRAIL-M / ++-M (verify) | Hallucinates perspective and lighting; run at native tile size and check that the result tiles |
| Photoshop Generative Fill (Firefly) | Adobe terms (verify) | Fast on unique facades; output size is limited, so upscale artefacts appear on 2K textures (verify) |
| FLUX.1 Fill [dev] | Non-commercial licence (verify) | Avoid it for paid or Tebex MLOs |
| GIMP Resynthesizer "Heal selection", Krita Smart Patch | GPL | Good free alternative to content-aware fill (verify GIMP 3 port) |
