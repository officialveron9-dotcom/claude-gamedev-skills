# Working in this repo

This repo is a Claude Code plugin marketplace (`gamedev-skills`) of skills for Unreal Engine 5,
FiveM, FiveM for GTAV Enhanced, Blender modeling (GTA MLOs, textures, clothing), Brotato mods (Godot 3) and web development. The owner writes in German; reply in German. Skill content is English.

## Layout

- `plugins/<plugin>/skills/<skill>/SKILL.md` plus `references/*.md`. Plugins are listed in
  `.claude-plugin/marketplace.json`; each has `.claude-plugin/plugin.json`.
- `unreal-engine-reference`, `general-dev`, `gamedev-general`, `web-dev` and the skills listed in `plugins/blender-modeling/UPSTREAM.md` are copied from upstream (see each `UPSTREAM.md`).
  Don't edit them by hand except to re-sync with upstream; keep each skill's `LICENSE`.

## Rules for skills

- Frontmatter keys only: `name`, `description` (plus `license`, `compatibility`, `metadata`,
  `allowed-tools` if needed). Other keys break claude.ai ZIP uploads. `name` = folder name.
- Content = what Claude gets wrong: pitfalls, wrong-vs-right code, error message → cause → fix
  tables, checklists. No beginner background.
- Keep `SKILL.md` under ~300 lines; move detail into `references/` and link it with a relative path.
- Tag version-specific facts (e.g. "UE 5.8", "artifact 12913+"); add new sources to `references/sources.md`.

## When the owner reports a solved bug

Add a row to the matching skill's troubleshooting table (`common-errors.md`, `common-issues.md`,
`troubleshooting.md` or `known-issues.md`): exact message or symptom → cause → fix, with version.

## Before committing

Run `python3 scripts/validate-skills.py`. Update the skill tables in `README.md` when adding or renaming a skill.
