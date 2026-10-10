# External tools, MCP servers and agent skills for MLO work (checked 2026-10-10)

Method: repositories cloned with `git clone --depth 1` and read (LICENSE, README, source); dates = last commit.
"Not inspected" = only seen in another project's notes or a search result. General Blender skills and Blender MCP
servers (with setup steps) are ranked in the `blender-modeling` plugin's `EXTERNAL.md`; this file covers the
GTA/FiveM side.

## Core toolchain

| Tool | URL | License | Status | Verdict |
|---|---|---|---|---|
| Sollumz | https://github.com/Sollumz/Sollumz | GPL-3.0-or-later | 2.9.0 released 2026-08-04; `main` 2.9.0-dev, commit 2026-10-10; Blender ≥ 4.2 (CI 4.0–5.2); install from `https://repo.sollumz.org/` | **Required.** Drawables, collisions, ytyp/MLO (rooms, portals, entity sets, TCMs), ymap (2.9 rework, MLO instancing), lights, Gen8/Gen9 |
| szio | https://github.com/Sollumz/szio (PyPI `szio`) | MIT | 1.3.0.dev9 in Sollumz 2.9.0, 1.4.0.dev1 on `main` | Sollumz's I/O library; usable headless for scripted conversions |
| PyMateria | https://static.cfx.re/whl/ (licence PDF: static.cfx.re/PyMateria-License-Agreement.pdf) | Cfx licence agreement | 0.2.0, Windows only (Python 3.10–3.14 wheels) | Install it: enables Native binary import/export incl. Gen9 |
| CodeWalker | https://github.com/dexyfex/CodeWalker; builds: CodeWalker Discord `#releases` | MIT-style (`Notice.txt`) | GitHub `master` 2025-04-11; Discord Dev48+ (Cfx guide uses Dev48) | **Required** for finding assets, ymap editing, occluders, `_manifest.ymf`, XML↔binary, Gen9 Asset Converter |
| Alchemist | https://docs.fivem.net/docs/alchemist/ (Cfx Portal download) | Cfx, free | released 2025-11-20; Windows 11 | Gen8 → Gen9 for YDR/YTD/YFT/YPT/YDD; see skill `fivem-gta5-enhanced` |
| OpenIV | — | proprietary | — | Not recommended with Sollumz output (Sollumz wiki); use CodeWalker |

## GTA/FiveM helpers

| Tool | URL | License | Status | What it does | Verdict |
|---|---|---|---|---|---|
| fivem_conflicttool | https://github.com/kkMihai/fivem_conflicttool | GPL-3.0 | 2026-10-06, 56★ | In-game scan of all resources for conflicting ymap/ytyp/ybn/ydr/ytd/yft, double placements, overlapping box occluders; merge YMAP/YBN, shrink occluders | **Use** before shipping a vanilla-ymap/ybn override |
| rage-cli | https://github.com/VIRUXE/rage-cli | Unlicense (public domain) | 2026-10-02, Rust | RPF/RSC7 tools, top-down `plot` of interiors (rooms, portals, collision, navmesh), **`navmesh build`** for MLOs from `.ybn`/`.ymap`/`.ytyp` | **Use** for NPC navmesh and visual QA (navmesh streaming in FiveM: verify) |
| RAGE Tools | https://github.com/escobarv110/Rage-Tools | custom "RAGE Tools License" (use/modify, no rebranding/resale) | 2026-10-09, C#/.NET 8, 29★ | World viewer, light/material editor, **MLO Creator** (exports `.ytyp` + `.ymap` + `_manifest.ymf`), navmesh editor, MCP server `RageTools.Mcp` (TCP 27017) | Promising, unproven. Its own docs: MLO import ignores room/portal data. Repo ships an obfuscation config and an antivirus warning → test in a VM |
| RAGE Evo | https://github.com/escobarv110/RAGE-Evo | no LICENSE file | 2026-09-29 | 3ds Max suite (GIMS EVO successor): ydr/ydd/yft/ybn/ymap/ytyp/ycd/ytd, MLO, lights, occluders, Legacy or Enhanced | Only for 3ds Max users; no licence → read only |
| mlo-light-manager | https://github.com/byfredQC/mlo-light-manager | GPL-3.0 | 2026-10-06 | Blender (Sollumz) add-on + FiveM resource: edit existing MLO lights in Sollumz, see them live in FiveM | Useful for light tuning; does not create lights |
| FiveM Toolkit (in blender-toolkit) | https://github.com/EnesiEsen/blender-toolkit | GPL-3.0 | 2026-10-08 | On top of Sollumz: builds rooms/portals/collision from an outliner layout (`room.<name>`, `portal.<a>.<b>`), exports ydr/ybn/ytyp | New, 0★, by its own README not tested in a live server; no ymap |
| muto-atlas | https://github.com/B7Kompirine/muto-atlas | MIT (code) | 2026-09-13 | Claude Code plugin: skills `fivem-assets`/`fivem-natives`, read-only MCP, offline data layers built from your own game (archetypes, LOD chains, MLO placements, timecycles, lights), measured rules | **Recommended companion.** Several measured facts here come from it (marked "muto-atlas"). Some notes contradict each other (e.g. Sollumz binary ytyp/ymap) — trust the source code |
| VIRUXE/fivem-mcp | https://github.com/VIRUXE/fivem-mcp | not inspected | — | Drives a running FiveM client from an agent (per rage-cli README) | Not inspected |
| Arbolito, VichoTools, ht_mlotool, Audio Occlusion Tool | e.g. https://github.com/Hancapo/Arbolito | not inspected | — | ymap split/merge; MLO transform export; MLO audio occlusion | Not inspected (muto-atlas community notes) |
| Five Toolkit | https://tools.scarfacemlo.com | closed, Discord login | "Shell Creator" in development (2026-09) | Browser pipeline "no Blender" | Not recommended: closed; muto-atlas refuted parts of its data |

## Agent skills / MCPs found for Sollumz, CodeWalker, FiveM mapping

| Item | URL | License | Verdict |
|---|---|---|---|
| muto-atlas (skills + MCP) | see above | MIT | Best match; complements this skill (data lookups, measured vanilla values) |
| bworthy89/fivem-server-development | https://github.com/bworthy89/fivem-server-development | MIT | Qbox server skill incl. MLO streaming; nothing on building MLOs |
| leminhhuy113/fivem-pro | https://github.com/leminhhuy113/fivem-pro | MIT | All-in-one FiveM skill; `maps-sollumz.md` is a 55-line overview (manifest, portals) — too shallow |
| digitARTI/Sollumz-MCP | https://github.com/digitARTI/Sollumz-MCP | GPL-3.0 | Despite the name, a plain copy of Sollumz (last commit 2026-03-29) with no MCP code. Ignore |
| jhammant/codewalker | https://github.com/jhammant/codewalker | — | Unrelated (codebase-analysis MCP named "codewalker") |
| Blender Lab MCP (official) | https://projects.blender.org/lab/blender_mcp | GPL (per `EXTERNAL.md`) | Blender 5.1+, `execute_blender_code`; Sollumz operators callable through it (search snippets; site blocked here) |
| MCP for Blender | https://github.com/ahujasid/mcp-for-blender | MIT | 2.1.9 (2026-10-06), `uvx mcp-for-blender`, port 9876, works on Blender 4.x |

## Unreal Engine → GTA V

Result (2026-10-10): **no maintained Unreal → GTA V (`.ydr/.ybn/.ytyp`) exporter exists.** GitHub search
"unreal gta5 ydr" returned 0 repositories; web searches found only Unreal → Unity/Godot exporters and GTA-themed
UEFN maps. RAGE Evo is 3ds Max ↔ GTA; EnesiEsen's "UE5 Bridge" goes Blender → Unreal (the other way).

Working route:
1. Unreal: export the static mesh as FBX (or glTF); for a level piece, Export Selected. Bake materials to textures
   (diffuse, normal, specular) at power-of-two sizes.
2. Blender: import, apply transforms, metres, Z-up; split into ≤ 128 material/geometry chunks for Gen9.
3. Sollumz: Create Shader Material (`normal_spec.sps` etc.), `UVMap 0`, `Color 1` (interior: R 0, G > 0), DDS
   textures, Convert to Drawable, collision as usual.
4. Licences: check the source asset's licence before using it outside Unreal (Fab/Marketplace terms differ per
   listing; verify).
