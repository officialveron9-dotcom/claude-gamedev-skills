# Texture problems: symptom → cause → fix

Read when an edited texture looks wrong or does not appear in game, in CodeWalker or in Blender.
Tags: [Src] tool source, [Doc] official docs, [Reported] community, (verify) unconfirmed.
Add solved cases from the owner as new rows (exact message or symptom, cause, fix, versions).

| Symptom | Cause | Fix |
|---|---|---|
| Magenta/black checkerboard on the surface | Sollumz could not embed the image: not DDS (PNG/JPG), file missing, packed non-DDS data, or a corrupt DDS. It writes a 16x16 checkerboard instead and logs "Embedded texture '…' is not in DDS format" or "Failed to embed texture '…'. DDS image data may be corrupted." [Src: szio, Sollumz 2.8–2.9] | Convert to DDS (texconv), fix the image path or pack the DDS, re-export |
| Texture white, grey or missing in game, fine in Blender | Non-embedded name not found: YTD not streamed, YTD name ≠ ytyp `textureDictionary`, texture name typo, or only the diffuse renamed | Check the names in CodeWalker Material Editor; check the archetype's `textureDictionary`; stream the YTD (repack-and-stream.md). Exact in-game look of a missing texture (verify) |
| CodeWalker YTD preview empty, or the saved YTD breaks, after adding a DDS | DDS is `BC*_UNORM_SRGB`, `*_TYPELESS` or another format CodeWalker maps to format 0. Import does not warn [Src: DDSIO] | Re-export as `BC1/BC3/BC7_UNORM` (Paint.NET "Linear" variants; texconv `-f BC1_UNORM`). Run `dds_check.py` |
| "Unable to load <file>. Are you sure it's a valid .dds file?" (CodeWalker) | Not a DDS, unsupported DXGI format (P8, AI44, …), or a broken header [Src] | Re-export with texconv |
| "The following texture(s) already exist in this YTD" | Same name (= DDS file name) is already in the YTD [Src] | Use Replace, or rename the file |
| `Texture file not found:` / `Texture file format not supported:` on CodeWalker Import XML | DDS not in the folder named like the YTD next to the `.ytd.xml`, or a bad DDS [Src] | Put DDS files in `<name>/` beside `<name>.ytd.xml`; check with `dds_check.py` |
| Edited texture appears on **other buildings** too | You streamed a YTD with a **vanilla file name** (global replacement), or edited a texture in a shared/parent txd | Copy it under new YTD and texture names, repoint the materials, and remove the vanilla-named file from `stream*/` |
| Old door still visible **far away** | LOD/SLOD drawables use their own textures/UVs | Edit or remap the LOD copy, or hide the LOD entity with your map changes (`fivem-mlo-creation`) |
| Old door visible **only up close** | HD dictionary (`+hi`, `+hidr` …) bound in `_manifest.ymf` still has the original [Src: CodeWalker HD binding] | Edit the HD copy too, or use new names (no binding to an HD txd) |
| Old window **glows at night** | Separate geometry/material with an `emissivenight*` shader, or a night texture not edited | Delete those faces in your copy or black out that region of its texture; test at night |
| Normal map still shows door bevels and edges | `_n` not edited, or edited but the material still points to the vanilla `_n` name | Clone `_n` with the same offset as the diffuse; rename and repoint `BumpSampler` |
| Door area still shiny or reflective | `_s` R (intensity) and A (gloss) still contain the door | Paint R and A to the wall's values; repoint `SpecSampler` |
| Visible seams or lines around the patch, especially at distance | Edit crosses a UV island border without padding; clone offset not a multiple of the pattern period; mip bleeding | Dilate the fill 4–8 px past the island; use period-multiple offsets; check with the offset filter |
| Texture blurry up close | (a) Sollumz "HD" ticked but `+hi.ytd` not shipped (base has half resolution) [Src]; (b) oversized assets make the game keep low mips (texture loss) [Doc]; (c) the source was upscaled from a mip | Ship `+hi.ytd` or untick HD; reduce size (BC1, ≤2048); edit at the original resolution |
| Shimmer/moiré at distance | DDS without mipmaps | Regenerate with `-m <log2(min)-1>`; `dds_check.py` |
| "Oversized assets can and WILL lead to streaming issues" / textures vanish across the city | YTD or drawable (with embedded textures) above about 16 MiB | Split dictionaries, use BC1 where alpha is unused, ≤2048 px; see `fivem-server-setup` streaming-assets |
| Colours darker and more saturated than in Photoshop | sRGB-tagged PNG went through texconv without `-srgb`, so it was converted to linear [Src: DirectXTex] | `-srgb` for colour maps, `--ignore-srgb` for data maps, or re-save the PNG with Pillow |
| Colours washed out or brighter | Linear-to-sRGB applied (`-srgbo`, "sRGB" export variant, profile conversion) | Re-export the UNORM variant with no colour conversion |
| Banding after a hue/brightness change | 8-bit adjustment on a gradient plus BC1 | Adjust in 16-bit, add dithering (`-bc d`), or use BC7 |
| Crash or freeze when the asset loads (Enhanced) | Gen8 file loaded by Enhanced; compressed `script_rt_*` (`ERR_GFX_STATE`); more than 128 materials in a drawable [Reported] | Convert (Alchemist/CodeWalker/Sollumz Gen9); see `fivem-gta5-enhanced` |
| Crash, or asset silently missing, on Legacy (verify which) | Gen9 file in `stream/` (saved by CodeWalker in Enhanced mode) | Re-save in a Legacy-mode CodeWalker or use the Gen8 export; check with `rsc_gen.py` |
| Works on Legacy, missing or old on Enhanced | `stream_enhanced/` exists with a stale or unconverted copy; Enhanced then ignores `stream/` [Doc] | Rebuild both folders after every change; `rsc_gen.py` |
| Works on Enhanced, old texture on Legacy | Only `stream_enhanced/` was updated | Update the Gen8 file in `stream/` |
| Colour differs between Legacy and Enhanced | Different tone mapping and lighting (DX12/RT) on Enhanced; possibly a UNORM vs sRGB format difference (verify) | Compare side by side; adjust per platform only if needed (separate files are already separate) |
| Texture fine in CodeWalker, old one in game | Client cache or another resource streaming the same file name (start order decides) | Search all resources for the file name; restart the server; clear the client cache (verify path) |
| Sollumz import: "Failed to import image" for a DDS | Mip count in the header longer than the data, e.g. a chain below 4x4 | Sollumz 2.8.3+ tries to fix it [Doc: release notes]; re-export with `-m log2(min)-1` |
