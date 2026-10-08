# Upstream

Vendored on **2026-10-08**. Every skill folder contains the original `LICENSE` (and `NOTICE` for
Apache-2.0 skills). Only MIT and Apache-2.0 sources were used. Frontmatter was reduced to the
portable keys (`name`, `description`, `license`, `metadata`); none of the sources used other keys.

## Sources

| Source | License | Commit | Commit date |
|---|---|---|---|
| [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) | Apache-2.0 (Copyright 2026 Abhishek Barali and contributors), `NOTICE` copied | `d4b0e35550c55ae70bdfcab4ef5a0e94610438a9` | 2026-09-27 |
| [mattpocock/skills](https://github.com/mattpocock/skills) | MIT (Copyright (c) 2026 Matt Pocock) | `b0618bc436ad893b3c5e84e55fba86586d34a404` | 2026-10-08 |
| [fvadicamo/dev-agent-skills](https://github.com/fvadicamo/dev-agent-skills) | MIT (Copyright (c) 2025 Francesco Vadicamo) | `8e710c57b4aa34fec63752ccf04a47adb4a8be65` | 2026-09-11 |

## Skills

| Skill | Upstream path | Engine / version label | Files |
|---|---|---|---|
| `performance-optimization` | awesome-gamedev `skills/disciplines/performance-optimization` | engine-neutral method; examples Godot 4.7, Unity 6.3 LTS, Unreal 5 (`stat unit`, Unreal Insights) | SKILL.md, references/profiling-and-budgets.md |
| `shader-programming` | awesome-gamedev `skills/disciplines/shader-programming` | engine-neutral GLSL + HLSL mapping; engine notes Godot 4 / Unity / Unreal | SKILL.md, references/effects.md |
| `physics-tuning` | awesome-gamedev `skills/disciplines/physics-tuning` | engine-neutral; examples Godot 4.7, Unity 6.3 | SKILL.md, references/timestep-and-ccd.md |
| `save-systems` | awesome-gamedev `skills/disciplines/save-systems` | engine-neutral; examples Godot 4.7 (`FileAccess`), Python | SKILL.md, references/versioning-and-migration.md |
| `game-feel` | awesome-gamedev `skills/disciplines/game-feel` | engine-neutral; examples Godot 4.7, Unity 6.3 | SKILL.md, references/feedback-recipes.md |
| `steam-publish` | awesome-gamedev `skills/workflows/steam-publish` | engine-neutral (Steamworks, SteamPipe, steamcmd) | SKILL.md, references/steampipe-build-scripts.md |
| `writing-for-agents` | mattpocock `skills/productivity/writing-for-agents` | language-agnostic (CLAUDE.md, AGENTS.md, skills) | SKILL.md, SKILL-MECHANICS.md, agents/openai.yaml |
| `codebase-design` | mattpocock `skills/engineering/codebase-design` | language-agnostic | SKILL.md, DEEPENING.md, DESIGN-IT-TWICE.md, agents/openai.yaml |
| `tdd` | mattpocock `skills/engineering/tdd` | language-agnostic rules; TypeScript examples in tests.md / mocking.md | SKILL.md, tests.md, mocking.md, agents/openai.yaml |
| `code-review` | mattpocock `skills/engineering/code-review` | language-agnostic; uses git and parallel sub-agents | SKILL.md, agents/openai.yaml |
| `grilling` | mattpocock `skills/productivity/grilling` | language-agnostic | SKILL.md, agents/openai.yaml |
| `git-commit` | fvadicamo `plugins/github-workflow/skills/git-commit` | language-agnostic (Conventional Commits) | SKILL.md, references/commit_examples.md |

**No Godot 4 and no Unity engine skills were vendored on purpose.** This plugin is meant to be
installed next to `brotato` (Godot 3); `scripts/install-skills.*` copy whole plugins, so a Godot 4
skill here would end up in the Brotato project and make Claude write Godot 4 code. The six game
skills above are engine-neutral methods, but their *code samples* are Godot 4.7 / Unity 6.3; each
affected `SKILL.md` carries an "Engine note" right after the frontmatter saying how to translate
to Godot 3 or Unreal. Godot 4 and Unity collections are listed, with install commands, in
`docs/beste-skills-games-allgemein.md`.

## Changes against upstream

All skills:
- Added `license` and `metadata` (`upstream`, `upstream-license`, `engine`, `modified`) to the frontmatter.
- Added an HTML comment after the frontmatter naming the modification (Apache-2.0 §4(b) notice; done for the MIT skills too).
- Copied the repo-level `LICENSE` (and `NOTICE` for Apache-2.0) into each skill folder.

Per skill:
- `performance-optimization`, `physics-tuning`, `save-systems`, `game-feel`, `shader-programming`: added an "Engine note" blockquote (Godot 4 vs Godot 3, Unreal equivalents). Body otherwise unchanged. `references/` unchanged.
- `steam-publish`, `writing-for-agents`, `codebase-design`, `tdd`, `grilling`, `git-commit`: body unchanged.
- `code-review`: replaced the sentence that tells the user to run `/setup-matt-pocock-skills` (the upstream issue-tracker setup) with a note to take the spec from a file or ask. The two-axis review and the Fowler smell baseline are unchanged.
- `grilling` is the skill that `grill-me` (upstream's user-invoked alias with `disable-model-invocation: true`) delegates to; the alias was not copied because that key is not portable.
- mattpocock's `agents/openai.yaml` files (Codex display metadata) were kept; they are inert in Claude Code and claude.ai.
- `tdd` refers to the `codebase-design` and `code-review` skills by name; both are in this plugin.

Not copied from upstream: the awesome-gamedev `router` skill (routes between all 74 skills, useless
with six), its `scripts/validate-skills.py` and `tests/`; mattpocock `grill-me`, `grill-with-docs`
and the other 33 skills; fvadicamo's PR skills.

## Updating

Clone the upstream repo, diff the paths above against the pinned commit, and re-apply the changes
listed here. Run `python3 scripts/validate-skills.py` afterwards.
