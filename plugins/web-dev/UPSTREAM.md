# Upstream

Vendored on **2026-10-08** from the repositories below (each cloned with `git clone --depth 1`, commit pinned).
Every skill folder contains the original license text (`LICENSE`, or `LICENSE.txt` for Anthropic).
Skill content is unchanged except for the edits listed under "Changes against upstream".

| Skill (folder) | Upstream (path @ commit, date) | License | Upstream `name` |
|---|---|---|---|
| `vercel-react-best-practices` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) `skills/react-best-practices` @ `063bee94c3f4df8453406c830b0a7df0f2860278` (2026-08-28) | MIT (declared in README and SKILL.md frontmatter; repo has no LICENSE file, see note) | `vercel-react-best-practices` |
| `react-19-best-practices` | [pproenca/dot-skills](https://github.com/pproenca/dot-skills) `skills/.curated/react` @ `cf93c57cac89d6fc3e4194686000411567f5caf3` (2026-08-15) | MIT (© 2025 pproenca) | `react` |
| `nextjs-16-app-router` | pproenca/dot-skills `skills/.curated/nextjs` @ same commit | MIT | `nextjs` |
| `tailwind-v4-best-practices` | pproenca/dot-skills `skills/.curated/tailwind` @ same commit | MIT | `tailwind` |
| `wcag-accessibility` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills) `skills/accessibility` @ `afa8da942115f2961fdbfa80807ea0b232ff6c00` (2026-08-24) | MIT (© 2026 Addy Osmani) | `accessibility` |
| `core-web-vitals` | addyosmani/web-quality-skills `skills/core-web-vitals` @ same commit | MIT | `core-web-vitals` |
| `security-and-hardening` | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) `skills/security-and-hardening` @ `1401c8b8030e023baeebb31781a6653fe8e93026` (2026-10-03) | MIT (© 2025 Addy Osmani) | `security-and-hardening` |
| `webapp-testing` | [anthropics/skills](https://github.com/anthropics/skills) `skills/webapp-testing` @ `683bc88e56f3e09ba94f7055977f3d3aa499f202` (2026-10-05) | Apache-2.0 (`LICENSE.txt` in the skill folder) | `webapp-testing` |
| `playwright-core` | [testdino-hq/playwright-skill](https://github.com/testdino-hq/playwright-skill) `core/` @ `400e4256cd22669ad69c18d31d3e5541e4e1c2a3` (2026-09-06) | MIT (© 2026 TestDino) | `playwright-core` (folder was `core`) |
| `dependency-verification` | [athola/claude-night-market](https://github.com/athola/claude-night-market) `plugins/imbue/skills/dependency-verification` @ `9f3eb003bedbd1d84389c5dd68711ea56c8c69b4` (2026-10-01) | MIT (© 2025 athola) | `dependency-verification` |
| `supabase-postgres-best-practices` | [supabase/agent-skills](https://github.com/supabase/agent-skills) `skills/supabase-postgres-best-practices` @ `c9be0e931b7930f7d02126d04774d904c381e7d7` (2026-10-02) | MIT (© 2026 Supabase) | `supabase-postgres-best-practices` |
| `nodejs-best-practices` | [mcollina/skills](https://github.com/mcollina/skills) `skills/node` @ `72b72751477157ebda36203eaffac701ac5df5ae` (2026-10-03) | MIT (© 2026 Matteo Collina) | `node` |

## Changes against upstream

General rule applied to all skills: frontmatter keeps only `name`, `description`, `license`, `metadata`
(other keys break claude.ai ZIP uploads); `name` equals the folder name; relative links must resolve
inside the skill folder (checked by `scripts/validate-skills.py`).

- **`vercel-react-best-practices`**: content unchanged (SKILL.md, `rules/`, `AGENTS.md`, `README.md`,
  `metadata.json`). Added `LICENSE` with the standard MIT text because the upstream repo only declares
  "MIT" in its README and frontmatter and ships no license file. In `AGENTS.md` (the compiled copy of
  the rules) the links `./<rule>.md` were rewritten to `rules/<rule>.md` so they resolve from the folder.
- **`react-19-best-practices`, `nextjs-16-app-router`, `tailwind-v4-best-practices`**: renamed from the
  generic upstream names `react`, `nextjs`, `tailwind` (`name:` in the frontmatter changed accordingly) to
  avoid clashes with other installed skills. In `nextjs-16-app-router/SKILL.md` the related-skill hint
  "see `react` skill" now says `react-19-best-practices`. Upstream mentions of the `react-hook-form`,
  `tanstack-query` and `zod` skills refer to pproenca/dot-skills skills that are **not** vendored.
  `assets/templates/`, `references/`, `AGENTS.md` and `metadata.json` copied unchanged.
- **`wcag-accessibility`**: renamed from `accessibility`. The link to the sibling skill
  `../web-quality-audit/SKILL.md` now points to that file on GitHub.
- **`core-web-vitals`**: copied `references/MEASUREMENT.md` and `references/RUM.md` from the upstream
  `performance` skill into this skill's `references/` and pointed the two links there; the link to
  `../performance/SKILL.md` now points to GitHub.
- **`security-and-hardening`**: copied the repo-level `references/security-checklist.md` into the
  skill's `references/` and changed the inline paths `../../references/security-checklist.md`
  (SKILL.md) and `../../../references/security-checklist.md` (`references/hardening-patterns.md`)
  accordingly. The text still names sibling skills of the upstream collection
  (`deprecation-and-migration`, `observability-and-instrumentation`, `debugging-and-error-recovery`),
  which are not vendored.
- **`webapp-testing`**: unchanged (Apache-2.0; no file modified, so no modification notice is required).
  Needs Python with `playwright` installed (`pip install playwright && playwright install chromium`).
- **`playwright-core`**: folder renamed from `core` to match `name: playwright-core`. 38 links to the
  sibling folders `../ci/`, `../pom/`, `../migration/`, `../playwright-cli/` were rewritten to GitHub
  URLs (`https://github.com/testdino-hq/playwright-skill/blob/main/...`). In `test-organization.md`
  five links still used an older upstream layout (`foundations/`, `decisions/`, `infrastructure/`) and
  were already broken upstream; they now point to the existing files or to GitHub.
- **`dependency-verification`**: frontmatter reduced to `name`, `description`, `license` (removed
  `alwaysApply`, `category`, `tags`, `dependencies`, `tools`, `usage_patterns`, `complexity`,
  `model_hint`, `estimated_tokens`, `modules`, `role`). Added a short note at the top: the upstream
  PreToolUse hook `guard_package_hallucination.py` (depends on the plugin's `hooks/shared/` modules) is
  not included; the manual registry check in `modules/registry-checks.md` works without it. Mentions of
  `sanctum:…`, `leyline:…`, `imbue:…` refer to other upstream plugins.
- **`supabase-postgres-best-practices`**: unchanged (includes upstream `CHANGELOG.md`).
- **`nodejs-best-practices`**: renamed from `node` (`name:` changed). `rules/`, `rules/assets/` and
  `tile.json` (upstream registry metadata) copied unchanged.

## Not vendored on purpose

Skills that need tooling we did not copy (Chrome DevTools MCP, `playwright-cli` binary, Vercel API,
gstack browser), skills that fetch their rules at runtime (`web-design-guidelines`), and collections
under CC BY-SA / CC BY-NC / no license. Details and install commands: `docs/beste-skills-web.md`.

To update: diff each skill against the newest upstream commit, copy the changed files again and
re-apply the changes above, then run `python3 scripts/validate-skills.py`.
