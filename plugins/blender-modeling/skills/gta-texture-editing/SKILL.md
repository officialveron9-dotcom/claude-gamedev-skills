---
name: gta-texture-editing
description: Edits GTA V building textures for custom FiveM MLOs on FiveM Legacy and FiveM for GTAV Enhanced (Gen9). Covers finding and extracting YTD/embedded textures with CodeWalker and Sollumz, painting out painted-on doors and windows on diffuse, normal (_n), specular (_s), night and LOD maps, copying shared vanilla textures under new names, recoloring, texconv DDS conversion (BC1/BC3/BC7, mipmaps, sRGB) and re-packing for stream/ and stream_enhanced/. Use for YTD, texture dictionary, DDS, texconv, mipmaps, paint out, retouch, inpaint, normal map, specular map, CodeWalker texture, Sollumz texture, "Textur bearbeiten", "Tür wegmalen", "Fenster wegretuschieren", "Textur ändern", "Farbe ändern".
---

# GTA V texture editing for FiveM MLOs

Reader: Claude. Tags: **[Src]** = read in tool source code (CodeWalker, Sollumz/szio, DirectXTex,
GIMP, Paint.NET plugin), **[Doc]** = official docs, **[Reported]** = community, **(verify)** =
unconfirmed. Tell the user when something is (verify).
Related skills (link, do not repeat): `fivem-mlo-creation` (Blender/Sollumz pipeline, ymap/ytyp, hiding
vanilla buildings), `fivem-mlo-doors-windows` (functional doors, garages, windows), `fivem-gta5-enhanced`
(Alchemist, `stream_enhanced/`, Gen9 crashes), `fivem-server-setup` (streaming rules, oversized assets).

## Ground rules

1. **Textures resolve by name.** A material stores sampler names, not files. The game looks in the embedded
   dictionary first, then the archetype's `textureDictionary` (ytyp), then its parent chain (`gtxd`). [Src]
   So a `.ytd` streamed with a **vanilla file name** replaces it for every building, and an edit
   in a shared/parent txd changes every user.
2. **Never edit vanilla in place.** Copy, give the YTD **and every texture** a new name (`mymlo_facade_d/_n/_s`),
   repoint **every** sampler (`DiffuseSampler`, `BumpSampler`, `SpecSampler`, …), and link the YTD in your ytyp.
3. **One mask, all maps.** The door exists in the diffuse, `_n`, `_s`, the night/emissive material, the LOD/SLOD
   models and possibly an HD (`+hi`) dictionary. Edit or remap all of them, or it shows in one of them.
4. **Edit lossless, convert once.** Work at the original resolution in PNG/PSD/XCF. Convert to DDS only at the end.
5. **DDS = `*_UNORM`, power of two, mips to 4x4.** Never `_SRGB` or typeless (CodeWalker silently stores them as
   format 0). [Src]
6. **Two builds.** Gen8 files go in `stream/` and Gen9 files in `stream_enhanced/`. Rebuild both after every change.
7. Prefer **UV remap** or a **patch plane** when they solve it. Edit textures only when they do not.

## Choose the method

| Situation | Method |
|---|---|
| Door has its own faces, and a plain wall area exists in the same texture | UV remap the door faces onto the wall (knife-cut first if needed) |
| Vanilla building must stay untouched | Patch plane 1–2 cm in front, textured with a wall crop in your YTD |
| Unique facade atlas with baked AO/dirt and no clean region | Texture edit (clone along the grid, all maps) |
| Window glows at night | Delete the `emissivenight*` faces in your copy, or black out the night texture |
| Door visible only far away | Edit/remap the LOD/SLOD copy |

Steps for each method: [references/paint-out-workflow.md](references/paint-out-workflow.md).

## Texture roles (what to retouch)

| Sampler | Game reads | Retouch | Default format |
|---|---|---|---|
| `DiffuseSampler` | RGB colour; A = cutout/decal alpha on those shaders | Clone/heal the door away | BC1 opaque; BC3 or BC7 with alpha |
| `BumpSampler` (`_n`) | **R,G only**, Z rebuilt, B ignored [Src] | Same clone offset as diffuse; smooth wall = `128,128` | Match original (BC1/BC3); BC7 on Gen9 |
| `SpecSampler` (`_s`) | Intensity = dot(RGB, `specMapIntMask`) (default R); A × `specularFalloffMult` = gloss [Src] | Paint **R and A** to the wall's values | BC3 if the original has alpha |
| `emissivenight*`, `glass_emissivenight`, `decal_emissivenight_only` material | Glows at night [Src: shader list] | Delete faces or black out the texture (verify) | Match original |
| `DetailSampler` | Global tiling detail (`mapdetail`) | Never edit | — |
| `TintPaletteSampler` (`*_tnt` shaders) | Column = vertex colour0 **blue** (colour1 on `trees_*_tnt`), row = entity `tintValue` [Src] | Recolour here, not in the diffuse | Match original |

Do not guess roles from suffixes. Read the sampler slots in CodeWalker **Material Editor** or the Sollumz
material panel.

## Workflow (texture edit)

1. **Locate:** in the CodeWalker World view, select the building and note the archetype, `.ydr`, `.ytyp`
   `textureDictionary` and LOD parent. In the model viewer, open Material Editor (sampler names; "(embedded)"
   marks embedded ones), Texture Editor (embedded dictionary) and the "HD textures" checkbox. Check the night
   materials and the LOD/SLOD models too.
2. **Extract:** "Save all textures…" (DDS), then convert to PNG:
   `texconv -nologo -y -ft png -m 1 -o png *.dds`.
3. **Copy and rename** every map of the set (`mymlo_<part>_d/_n/_s/_night`), lower case and ASCII. Keep the
   originals in `vanilla/`.
4. **Paint out** with the same mask on all maps:
   - Tiling: clone by whole pattern periods.
   - Atlas: clone, then fix the low-frequency light (frequency separation).
   - `_n`: same offset as the diffuse, or flat `128,128`.
   - `_s`: R and A set to the wall's values.
   - Night: black.
   - Grow the mask 2–4 px, and pad fills 4–8 px past UV island borders (mip bleeding).

   `paint_out.py` does the first pass for all maps.
5. **Check tiling and seams** (offset filter), and check at 25% zoom (mip level).
6. **Convert** (exact flags below), then run `dds_check.py`.
7. **Pack:** new YTD (CodeWalker New → YTD File…, or XML import, or the Sollumz Texture Dictionaries panel), or
   embed. Repoint the materials. Set `textureDictionary` in your ytyp.
8. **Build both generations.** CodeWalker writes Gen8 or Gen9 depending on the **game folder it is set to**: an
   Enhanced folder means Gen9 (YTD v5), "(GTAV Enhanced)" in the title. [Src] Alternatives: Alchemist, or a Sollumz
   Gen9 export. Run `rsc_gen.py`.
9. **Stream** into `stream/` and `stream_enhanced/`. Restart the server. Test day, night, rain, close up
   (HD) and from 300 m+ (LOD), on **both** clients.

Repack, embedding, naming, `gtxd.meta` parents, `+hi`, Gen9 specifics:
[references/repack-and-stream.md](references/repack-and-stream.md).

## Formats: Legacy vs Enhanced

| | FiveM Legacy (Gen8) | FiveM for GTAV Enhanced (Gen9) |
|---|---|---|
| Safe colour formats | DXT1 (BC1), DXT5 (BC3) | BC1, BC3, BC7 (`*_UNORM` from tools) |
| BC7 | Format exists in Gen8 tooling (`D3DFMT_BC7`) [Src]; in-game (verify), so prefer BC1/BC3 | Yes [Src: Gen9 format enum] |
| sRGB formats | None (gamma lives in UNORM data) | Gen9 has `_SRGB` formats; CodeWalker TODOs hint that some vanilla textures use them. Tools write UNORM, and visual parity is (verify) |
| `script_rt_*` | Any | Uncompressed A8R8G8B8, no mips, or `ERR_GFX_STATE` (`fivem-gta5-enhanced`) |
| Resource version (YTD) | 13 | 5 |
| Folder | `stream/` | `stream_enhanced/` (then `stream/` is ignored) |
| Convert | — | Alchemist (official), CodeWalker Asset Converter, Sollumz Gen9 export |

Size: power of two, ≤2048 px for facades. A 2048² set (BC1 + BC1 + BC3) is about 10.7 MiB. Keep each YTD/drawable
well under 16 MiB. Memory table and editor settings:
[references/formats-and-tools.md](references/formats-and-tools.md).

## texconv: exact commands (Windows; mips = log2(short side) − 1)

```bat
:: colour map (diffuse/night), 2048x2048 -> -m 10 ; 2048x1024 -> -m 9 ; 1024 -> -m 9 ; 512 -> -m 8
texconv -nologo -y -l -srgb -f BC1_UNORM -m 10 -o dds mymlo_facade_d.png
:: colour map with alpha (cutout/decal)
texconv -nologo -y -l -srgb -f BC3_UNORM -m 10 -o dds mymlo_sign_d.png
:: data maps: never gamma-convert (texconv 2025-03-24+ for --ignore-srgb)
texconv -nologo -y -l --ignore-srgb -f BC1_UNORM -m 10 -o dds mymlo_facade_n.png
texconv -nologo -y -l --ignore-srgb -f BC3_UNORM -m 10 -o dds mymlo_facade_s.png
```

| Wrong | Right | Why |
|---|---|---|
| `texconv -f BC1_UNORM x.png` on a PNG with an sRGB/gAMA chunk | add `-srgb` | Otherwise sRGB→linear runs and the texture gets darker [Src] |
| `-f BC7_UNORM_SRGB`, Paint.NET "BC7 (sRGB, DX 11+)" | `BC7_UNORM`, "BC7 (Linear, DX 11+)" | CodeWalker maps `_SRGB` to format 0 [Src] |
| `-m 0` (down to 1x1) for Sollumz | `-m log2(min)-1` | Sollumz clamps/retries; stopping at 4x4 is safe [Src] |
| `-pow2` on a 1000x512 facade | Fix the canvas/UVs | Stretching shifts every UV detail |
| `-nmap …` on a normal map | Plain conversion | `-nmap` turns a height map into a normal map |

## Recolour quickly

- `_tnt` shader: change the entity `tintValue` (palette row) or edit the palette texture. Editing the diffuse is
  pointless because the palette multiplies it.
- Non-tint shader: Hue/Saturation/Curves on a **16-bit sRGB** copy of the diffuse only. Use dithering (`-bc d`)
  or BC7 against banding. Never recolour `_n`/`_s`.
- Vertex colour0 R/G scale ambient (baked AO). Use them to darken, not to change hue. [Src: decompiled shader]

## Automation (Claude can run these on the user's machine)

| Script | Does |
|---|---|
| `paint_out.py` | Mask from `--rect` (px) or `--uv-rect` (Blender UVs). Same clone (`--offset`) or OpenCV/LaMa inpaint on diffuse, `_n` (renormalised), `_s` (R+A) and night (black). Writes a mask PNG |
| `png2dds.py` | Batch texconv by suffix: UNORM only, BC1/BC3 by real alpha (or `--bc7`), mips to 4x4, refuses non-power-of-two |
| `dds_check.py` | Header check: power of two, ÷4, mips, `_SRGB`/typeless, >2048, >16 MiB, total size |
| `make_ytd_xml.py` | CodeWalker `.ytd.xml` for a DDS folder (Usage by suffix) for Import XML |
| `rsc_gen.py` | Gen8 vs Gen9 per file from the RSC7 version; flags wrong `stream*/` folder |

Code, test results and the LaMa snippet: [references/automation.md](references/automation.md).

## Top symptoms

| Symptom | Cause | Fix |
|---|---|---|
| Magenta/black checkerboard | Sollumz got a non-DDS/missing image (16x16 fallback) [Src] | Convert to DDS, re-export |
| Change appears on other buildings | Vanilla file/texture name streamed, or shared parent txd | New names, repoint materials |
| Door still visible far away / up close | LOD/SLOD textures / HD `+hi` copy | Edit or remap those too |
| Window still glows at night | `emissivenight*` geometry or night texture | Delete faces or black out |
| Bumps or shine where the door was | `_n`/`_s` not edited or not repointed | Same mask on all maps; rename + repoint all samplers |
| Darker / washed out | Implicit sRGB conversion / `_SRGB` export | `-srgb` / `--ignore-srgb`, UNORM only |
| Works on Legacy, not Enhanced | Stale/unconverted file in `stream_enhanced/` | Rebuild both; `rsc_gen.py` |

Full table (CodeWalker messages, crashes, blur, seams, oversize):
[references/common-issues.md](references/common-issues.md).

## Checklist per edited texture

- [ ] Vanilla original kept unchanged; copy has a new lower-case name with a project prefix
- [ ] Shared/parent txd checked; nothing streamed under a vanilla file name
- [ ] Diffuse, `_n`, `_s`, night/emissive, LOD/SLOD and HD (`+hi`) copies handled (edited, remapped or deliberately skipped)
- [ ] Same mask/offset on all maps; `_n` has no door bevels; `_s` R/A match the wall
- [ ] Seams checked (offset filter, island padding, 25% zoom)
- [ ] Original resolution kept; power of two; ≤2048 px
- [ ] DDS: `*_UNORM` (BC1/BC3; BC7 tested on Legacy), mips to 4x4, colour with `-srgb`, data with `--ignore-srgb`
- [ ] `dds_check.py` passes; YTD/drawable well under 16 MiB
- [ ] Every sampler repointed; ytyp `textureDictionary` set; HD toggle only if `+hi.ytd` ships
- [ ] Gen8 file in `stream/`, Gen9 file in `stream_enhanced/` (`rsc_gen.py` clean)
- [ ] Tested on both clients: day, night, rain, close up, 300 m+

## References

- [references/paint-out-workflow.md](references/paint-out-workflow.md): finding every copy of the door,
  method choice, retouch per map, UV remap and patch plane steps, recolouring. Read before any edit.
- [references/formats-and-tools.md](references/formats-and-tools.md): format table, memory, sRGB rule, texconv
  flags, GIMP/Paint.NET/Photoshop/OpenIV settings, inpainting licences. Read when exporting or a tool misbehaves.
- [references/repack-and-stream.md](references/repack-and-stream.md): embedded vs YTD, CodeWalker/Sollumz
  steps, YTD XML, `gtxd.meta`, naming, Gen8/Gen9 streaming. Read when packing or linking.
- [references/automation.md](references/automation.md): the five scripts with test notes. Read before running
  batch work for the user.
- [references/common-issues.md](references/common-issues.md): symptom → cause → fix. Read when debugging.
- [references/sources.md](references/sources.md): what each source backs up (2026-10-10).
