# Community skills and MCP servers for this pipeline (checked 2026-10-09)

Method: GitHub code search for `SKILL.md` mentioning Marvelous Designer, Substance Painter, Blender cloth/weights; repositories cloned and LICENSE + last commit read directly unless noted. "Verdict" is for a solo dev shipping a commercial UE game: only permissively licensed, specific, maintained items are recommended.

## MCP servers

| Project | URL | License | Last activity | Notes | Verdict |
|---|---|---|---|---|---|
| Blender Lab official MCP (`blender_mcp`) | https://projects.blender.org/lab/blender_mcp · https://www.blender.org/lab/mcp-server/ | not fetched (host blocked); Blender extension (verify GPL) | v1.0.3 2026-09-11 (per third-party notes) | Blender 5.1+ extension `lab_blender_org/mcp`, bridge `127.0.0.1:9876`, needs *Allow Online Access*; code execution, scene summary, screenshots | **Use** on Blender 5.1+ |
| mcp-for-blender (ahujasid, ex `blender-mcp`) | https://github.com/ahujasid/mcp-for-blender | MIT (read) | 2026-10-06 (read) | pyproject 2.1.9, add-on 1.8, Blender ≥3.0; `execute_blender_code`, `look`, asset/generation tools; anonymous usage telemetry on by default, content telemetry opt-in (`DISABLE_TELEMETRY=true`, `BLENDER_MCP_SAFE_MODE=1`); third-party | **Use** on Blender 4.x or when the official one is unavailable |
| MarvelousDesigner-MCP (Laboon2501) | https://github.com/Laboon2501/MarvelousDesigner-MCP | MIT (read) | 2026-09-19 (read) | Windows, MD 2026.0.315 with Python plug-ins; `md-mcp install-plugin`, in-app `md_start_listener`; tools for topology, sewing, sim steps, import/export, API doc search; ships a 24-line `skill/marvelous-designer/SKILL.md` | **Use with care** if your MD license exposes the Python API; verify on your build |
| dcc-mcp-marvelous-designer (dcc-mcp) | https://github.com/dcc-mcp/dcc-mcp-marvelous-designer | MIT (read) | 2026-09-26 (read) | Typed adapter on the 2025 MD Python API; README states no live host acceptance | Watch; not production-tested |
| hermes-plugin-blender (NousResearch) | https://github.com/NousResearch/hermes-plugin-blender | MIT (read) | 2026-10-04 (read) | Wraps the official Blender Lab server for the Hermes agent; verified headless with Blender 5.2.2 LTS | Read its setup notes; Hermes-specific |
| blender_mcp-setup-guide (psiQAQ) | https://github.com/psiQAQ/blender_mcp-setup-guide | GPL (read) | 2026-10-09 (read) | Packages the official MCP as a bundled extension for Blender 5.1 stable / 5.2 preview; notes Blender 5.0 incompatible with its bundle | Setup reference only |

## Skills

| Project | URL | License | Last activity | Content | Verdict |
|---|---|---|---|---|---|
| cc-blender-skill (RobLe3) | https://github.com/RobLe3/cc-blender-skill | MIT (read) | 2026-05-01 (read) | v1.3.0, 30 chainable skills (modeling, materials, UV, export, lighting, render) validated on Blender 5.1.1; `blender-export` has an FBX recipe (`FBX_SCALE_ALL`); prop-oriented, no clothing/skinning | Reuse the export recipe; otherwise generic |
| blender-skills (arjun988) | https://github.com/arjun988/blender-skills | MIT (read) | 2026-07-10 (read) | 188 `SKILL.md` under `.cursor/skills/` incl. `cloth-sim` (85 lines: pin groups, settings starters, bake), `retopology` (Quad Remesh/Instant Meshes table), `character-artist`, `rigging`, `uv-workflow`, `texture-workflow`, `export-pipeline`; marketplace listing "under review" | Usable starters; generic, verify bpy on 5.x |
| claudedesignskills › substance-3d-texturing (freshtechbro) | https://github.com/freshtechbro/claudedesignskills | MIT (read) | 2025-11-19 (read) | PBR channel overview, web/glTF export, Painter Python batch export | Partial (web-oriented, no UE/fuzz) |
| CLI-Anything (HKUDS) | https://github.com/HKUDS/CLI-Anything | Apache-2.0 (read) | 2026-09-22 (read) | Agent-harness generator; has a Blender CLI harness/skill | Generic; not clothing-specific |
| blender-mcp-skill (AndreiFlau) | https://github.com/AndreiFlau/blender-mcp-skill | **no LICENSE file** | 2026-10-03 | Talks to the official extension bridge directly from a Claude Code skill | **Do not copy** (all rights reserved); read for the bridge protocol idea only |
| design-skills › marvelous-designer-* (reason-machines) | https://github.com/reason-machines/design-skills | MIT (read) | 2026-08-04 | Skills describe an MD13 "unlock/activation" tool (software cracking) | **Reject** |
| OS › skills/tools/clo3d (antonyfmunoz) | https://github.com/antonyfmunoz/OS | no LICENSE | 2026-08-10 | Brand-specific CLO 3D tool note; useful fact: CLO plug-in API runs in-app, not headless | Reject (license); fact noted |
| Various "game-art"/"texture-art" skills (sickn33/agentic-awesome-skills, davila7/claude-code-templates, omer-metin/skills-for-antigravity, a5c-ai/babysitter `substance`, scenario-labs/skills `scenario-maya-lookdev`) | GitHub code search hits | not inspected | – | Generic game-art checklists mentioning Substance | Not evaluated; nothing specific to garment fitting |

No skill found that covers body-specific garment fitting, weight transfer or MetaHuman Outfit Assets; this skill fills that gap.
