# Upstream

Vendored on **2026-10-10**. Only the skills listed here come from upstream; every other file in
this plugin (`blender-python-pitfalls`, `EXTERNAL.md`, `.claude-plugin/plugin.json`) is the owner's own.
Each vendored skill folder contains the upstream `LICENSE` (MIT). Licenses and commits were read
from `git clone --depth 1` of each repository.

## Sources

| Source | License (read) | Commit | Commit date |
|---|---|---|---|
| [luckyfried/code-tools](https://github.com/luckyfried/code-tools) | MIT, Copyright (c) 2026 luckyfried | `c46388134a16bc8de6a8b29636dc18db0846be23` | 2026-09-30 |
| [scenario-labs/skills](https://github.com/scenario-labs/skills) | MIT, Copyright (c) 2026 Scenario | `f6f8ab71aa1f1e8322624869a173c1024aa875b8` | 2026-10-10 |

## Skills

| Skill | Upstream path | Blender version (upstream claim) | Files |
|---|---|---|---|
| `blender-current-api` | code-tools `skills/blender-current-api` | 5.2 LTS, old→new table keyed to release notes | SKILL.md, references/removed-apis.md |
| `blender-game-export` | code-tools `skills/blender-game-export` | 5.x exporters (FBX, glTF) for Unreal/Unity/Godot/three.js | SKILL.md |
| `blender-verify` | code-tools `skills/blender-verify` | official Blender Lab MCP (Blender 5.1+) or `blender -b` | SKILL.md |
| `scenario-blender-expert` | skills `skills/dcc/blender/scenario-blender-expert` | 5.2.1 LTS, tested headless | SKILL.md, references/blender-5.2-deltas.md, references/bpy-reliability.md, scripts/bx_audit.py, bx_gui.py, bx_review.py |
| `scenario-blender-hard-surface` | skills `skills/dcc/blender/scenario-blender-hard-surface` | 5.2.1 | SKILL.md, references/{critique,expert-notes,procedures,sources}.md, scripts/bx_hardsurface.py |
| `scenario-blender-retopology` | skills `skills/dcc/blender/scenario-blender-retopology` | 5.2.1 | SKILL.md, references/{critique,expert-notes,procedures,sources}.md, scripts/bx_retopo.py |
| `scenario-blender-uv-baking` | skills `skills/dcc/blender/scenario-blender-uv-baking` | 5.2.1 | SKILL.md, references/{critique,expert-notes,procedures,sources}.md, scripts/bx_uvbake.py |
| `scenario-blender-rigging` | skills `skills/dcc/blender/scenario-blender-rigging` | 5.2.1 | SKILL.md, references/{critique,expert-notes,procedures,sources}.md, scripts/bx_rig.py |

Folder names are unchanged on purpose: the `scenario-blender-*` scripts find each other through
sibling paths (`../scenario-blender-expert/scripts`), and the skills route to each other by name.

## Changes against upstream

All eight skills:
- Frontmatter: added `license: MIT (see LICENSE; upstream <repo>)` (the code-tools skills had no
  `license` key; the scenario skills had `license: MIT`, replaced by the longer form) and `metadata`
  (`upstream`, `upstream-license`, `blender`, `modified`). No upstream frontmatter key had to be
  stripped; all used only `name`, `description` (and `license`).
- Added one HTML comment after the frontmatter naming the source, commit and the modification.
- Copied the repository `LICENSE` into each skill folder.

Per skill:
- `blender-current-api`: the `description` was wrapped in single quotes, because the upstream plain
  YAML scalar contains `": "` (`"AttributeError: ... has no attribute"`) and does not parse as YAML
  (would break a claude.ai ZIP upload). Text unchanged.
- All other bodies, references and scripts: unchanged.

Known dangling references (left as upstream wrote them):
- `blender-game-export` mentions the `threejs-visual-check` and `gltf-transform` skills (not vendored;
  only relevant for web export).
- The `scenario-blender-*` skills route to siblings that were not vendored (`scenario-blender-sculpting`,
  `-texturing-shading`, `-hair`, `-animation`, `-previs-storyboard`, `-geometry-nodes`,
  `-lighting-rendering`, `-grease-pencil`); each skill already says to ask the user to install a
  missing sibling with `npx skills add scenario-labs/skills --skill <name>`.
- `bx_rig.mannequin()` (test-character builder) imports `scenario-blender-sculpting/scripts/bx_sculpt.py`
  and fails without it; the rest of `bx_rig` does not need it.
- Upstream mentions test suites (`tests/code/...`, `archive/tests/...`) that live outside the skill
  folders; they were not copied.

Not copied: code-tools `blender-animation-rigging`, `blender-compositing-nodes` and the non-Blender
skills; the other eight `scenario-blender-*` skills and the scenario family `README.md`.

## Updating

Clone both repositories, diff the paths above against the pinned commits, copy changed files, and
re-apply the frontmatter changes listed here. Then run `python3 scripts/validate-skills.py` and check
that every `SKILL.md` frontmatter still parses as YAML.
