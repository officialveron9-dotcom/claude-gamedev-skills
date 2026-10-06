# Claude Code skill, plugin and marketplace formats (verified 2026-10-06)

Status: verified against primary sources on 2026-10-06. The current Claude Code release
at that date is **v2.1.291** (from `anthropics/claude-code` CHANGELOG.md). Version numbers
below ("v2.1.2xx or later") are quoted from the docs. Treat older blog posts and tutorials
with suspicion: the plugin docs were reorganised under `code.claude.com/docs/en/plugins/...`
and several rules changed in 2026 (see section 8).

Primary sources (all fetched on 2026-10-06 as `.md` from the docs site unless noted):

| Topic | URL |
| :- | :- |
| Skills in Claude Code | https://code.claude.com/docs/en/skills |
| Plugins overview | https://code.claude.com/docs/en/plugins/overview |
| Plugin manifest (`plugin.json`) | https://code.claude.com/docs/en/plugins/manifest-reference |
| Plugin components | https://code.claude.com/docs/en/plugins/components |
| Create a marketplace | https://code.claude.com/docs/en/plugins/create-marketplace |
| Marketplace reference (`marketplace.json`) | https://code.claude.com/docs/en/plugins/marketplace-reference |
| Host a marketplace / private repos | https://code.claude.com/docs/en/plugins/host-marketplace |
| Install plugins (scopes, private, cloud tab) | https://code.claude.com/docs/en/plugins/install |
| Plugin loading reference | https://code.claude.com/docs/en/plugins/loading |
| Plugins for an org / per repository | https://code.claude.com/docs/en/plugins/org |
| Anthropic's marketplaces | https://code.claude.com/docs/en/plugins/anthropic-marketplaces |
| Code intelligence (LSP) plugins | https://code.claude.com/docs/en/plugins/code-intelligence |
| Settings reference (`enabledPlugins`, `extraKnownMarketplaces`) | https://code.claude.com/docs/en/settings-reference |
| Cloud environments ("What carries over") | https://code.claude.com/docs/en/cloud-environments |
| Claude Code on the web | https://code.claude.com/docs/en/claude-code-on-the-web |
| Env vars (`CLAUDE_CODE_PLUGIN_DIRS`, ...) | https://code.claude.com/docs/en/env-vars |
| Agent Skills overview (platform) | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| Skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| Agent Skills open spec | https://agentskills.io/specification (blocked from this sandbox; read from the source repo `github.com/agentskills/agentskills`, file `docs/specification.mdx`) |
| claude.ai: Creating custom skills | https://support.claude.com/en/articles/12512198-creating-custom-skills |
| claude.ai: Using skills in Claude | https://support.claude.com/en/articles/12512180-using-skills-in-claude |
| Real-world marketplace examples | https://github.com/anthropics/skills (`.claude-plugin/marketplace.json`), https://github.com/anthropics/claude-plugins-official |

---

## 1. `SKILL.md`

### 1.1 Where skills live (Claude Code)

| Location | Path | Loads in |
| :- | :- | :- |
| Enterprise | `.claude/skills/<skill-name>/SKILL.md` in the managed settings dir | all users the org deploys to |
| **Personal** | `~/.claude/skills/<skill-name>/SKILL.md` | all your projects on this machine. **Not** in Cowork or cloud sessions |
| **Project** | `.claude/skills/<skill-name>/SKILL.md` | sessions in this repo (commit it). **Does** load in cloud sessions |
| Nested | `<subdir>/.claude/skills/<skill-name>/SKILL.md` | loads once Claude reads/edits files in `<subdir>` |
| `--add-dir` dir | `.claude/skills/...` inside the added dir | that session |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | wherever the plugin is enabled, as `/plugin-name:skill-name` |
| claude.ai account | skills enabled on claude.ai | Cowork, cloud sessions, and terminal sessions signed in with that account (synced to `~/.claude/skills/synced/`, terminal sync needs v2.1.273+) |

Rules worth knowing (source: skills page):
- Same name in several places: enterprise > personal > project. Plugin skills never clash because they are namespaced.
- Project skills are discovered in the start dir and every parent up to the repo root.
- `<skill-name>` folders may be **symlinks** (enterprise/personal/project locations). Plugin skills handle symlinks differently.
- Reserved folder names: `synced` (any case) and `anthropic-skills` / `anthropic-skills:*` (outside a plugin) do not load.
- A skill folder that also contains `.claude-plugin/plugin.json` loads as a plugin named `<name>@skills-dir` (project-scope ones only after workspace trust, only from the primary working dir's `.claude/skills/`).
- Live reload: edits under `~/.claude/skills/`, `.claude/skills/` are picked up without restart. A brand-new top-level skills dir needs `/reload-skills`.
- `.claude/commands/*.md` (old format) still works, but prefer skills.

### 1.2 Frontmatter accepted by Claude Code

YAML between `---` lines; the opening `---` must be line 1. **All fields are optional; only
`description` is recommended.** Unknown fields are silently ignored by Claude Code (but
break claude.ai/API uploads, see 1.3). Booleans also accept `yes/no/on/off/1/0` (v2.1.218+).

| Field | What it does |
| :- | :- |
| `name` | Command name in the `/` menu. Defaults to the directory name. In a plugin it replaces only the last segment (`/my-plugin:<name>`). |
| `description` | What it does and when to use it. If omitted, the first non-empty body line is used. `description` + `when_to_use` together are **truncated at 1,536 characters** in the skill listing. |
| `when_to_use` | Extra trigger phrases or example requests, appended to `description` (counts toward the 1,536 cap). The only field with an underscore. |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]`. |
| `arguments` | Named positional args for `$name` substitution (string or YAML list). |
| `disable-model-invocation` | `true` means only the user can invoke it with `/name`. The description is then **not** in context. Default `false`. |
| `user-invocable` | `false` hides it from the `/` menu, so only Claude invokes it. Default `true`. |
| `allowed-tools` | Tools pre-approved for the turn that invokes the skill (space/comma string or YAML list). Does not restrict other tools. |
| `disallowed-tools` | Tools removed while the skill is active. |
| `model` | Model override for the rest of the turn (or for the forked subagent with `context: fork`). |
| `effort` | `low` / `medium` / `high` / `xhigh` / `max`. |
| `context` | `fork` runs the skill in a forked subagent. |
| `agent` | Subagent type when `context: fork`. |
| `background` | With `context: fork`: `false` waits for the result (v2.1.218+). Default `true`. |
| `hooks` | Hooks registered when the skill is invoked. |
| `paths` | Glob patterns; auto-load only when working on matching files. |
| `shell` | `bash` (default) or `powershell` for `` !`cmd` `` injection blocks. |
| `metadata` | Free-form map for your own tooling; Claude Code ignores it. |
| `license` | Accepted, not acted on (Agent Skills spec field). |
| `compatibility` | Up to 500 chars, accepted, not acted on (Agent Skills spec field). |

Body substitutions: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name`, `${CLAUDE_SESSION_ID}`,
`${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}` (v2.1.196+), and in plugin
skills `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`. `` !`command` `` lines inject live
shell output (Claude Code only, not claude.ai or the API).

### 1.3 Portable subset (claude.ai upload, Skills API, Agent Skills spec)

From the skills page, section "Using skill frontmatter outside Claude Code": claude.ai
uploads, the Skills API and `package_skill.py` accept **only** these six keys:

`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`

Any other key is a **hard error** on upload:
`Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name`

Field constraints (Agent Skills spec `docs/specification.mdx`, plus platform overview):

| Field | Required (spec/API) | Constraints |
| :- | :- | :- |
| `name` | yes | 1-64 chars; lowercase `a-z`, `0-9`, `-` only; no leading/trailing hyphen; no `--`; **must match the parent directory name** (spec). Platform docs add: no XML tags, must not contain the reserved words `anthropic` or `claude`. |
| `description` | yes | 1-1024 chars, non-empty, no XML tags. Say what it does **and** when to use it. Write it in third person (best practices). |
| `license` | no | short license name or a bundled license file name |
| `compatibility` | no | 1-500 chars, only if there are real environment requirements |
| `metadata` | no | map of string keys to string values |
| `allowed-tools` | no | space-separated string, experimental in the spec |

**Recommendation for our repo:** write every `SKILL.md` with only these six keys, `name`
equal to the folder name, kebab-case, no `claude`/`anthropic` in the name, and a description
well under 1024 chars (aim for 200-400; see the claude.ai conflict in section 9). The same
folder then works as a Claude Code personal/project skill, inside a plugin, as a claude.ai
ZIP upload and through the API. Put Claude Code-only behaviour (`disable-model-invocation`,
`paths`, `context: fork`, and so on) only in skills that never need to go to claude.ai.

### 1.4 Supporting files, size, progressive disclosure

```
my-skill/
├── SKILL.md          # required: frontmatter + instructions (overview / navigation)
├── references/       # optional docs, loaded on demand (spec convention)
├── scripts/          # optional executable code, run rather than read
└── assets/           # optional templates, data, images
```

- Progressive disclosure (platform overview and spec):
  1. metadata (`name` + `description`) is always in context, about 100 tokens per skill
  2. the `SKILL.md` body loads when the skill is triggered; keep it **under 5k tokens**
  3. referenced files and scripts load only when needed; scripts run through bash and only their output enters context
- **Keep `SKILL.md` under 500 lines** (Claude Code docs, spec and best practices all say this).
- Link supporting files from `SKILL.md` with relative paths. Keep references **one level deep** (no chains). Give reference files over 100 lines a table of contents. Use forward slashes only.
- In Claude Code, an invoked skill stays in context across turns. After compaction, Claude Code re-attaches the first 5,000 tokens of each invoked skill, within a 25,000-token combined budget.
- With `disable-model-invocation: true` the description is not loaded at all. That is cheap for rarely used manual workflows.
- Validator: `skills-ref validate ./my-skill` (from `agentskills/agentskills`).

---

## 2. Claude Code plugins

### 2.1 `.claude-plugin/plugin.json`

- The manifest is **optional**. Without it, components are auto-discovered from the standard layout and the name comes from the marketplace entry (or the directory name for `--plugin-dir`).
- When present, **`name` is the only required key**. It must be non-empty with no spaces, `@`, `:` or path separators; use kebab-case. Every component is namespaced under it.
- `claude plugin validate` errors on names that start with `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-`, on names equal to `claude`/`anthropic`/`claude-code`/..., and on names that put `official` next to `claude`/`anthropic`. It **warns** if `claude`/`anthropic` appears as a whole word anywhere. Avoid both words.
- Other common fields: `displayName`, `version`, `description`, `author` `{name (required), email, url}`, `homepage` (must parse as a URL), `repository`, `license` (SPDX), `keywords`, `defaultEnabled` (default `true`), `dependencies`, `userConfig`, `metadata`, plus component path keys (`skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`, `workflows`, `experimental.{themes,monitors,evals}`).
- Component paths are relative to the plugin root and **must start with `./`** (`skills` also accepts `"."`, v2.1.221+). `..` and missing paths fail validation.
- `skills` **adds to** the default `skills/` scan. `commands`, `agents`, `outputStyles` and `workflows` **replace** their default folders.
- **`version` pins users.** If `version` is set, users stay on the cached copy until you change the string. If it is left out of both the manifest and the marketplace entry, a relative-path plugin in a git-hosted marketplace is versioned by the commit SHA, so every push becomes an update. For a personal repo, **omit `version`**.
- Unknown top-level keys are stripped with a warning. Unknown keys inside `userConfig`, `channels`, `lspServers` and `monitors` are errors.
- A `CLAUDE.md` at the plugin root is **not** loaded (validate warns). Put instructions in a skill.
- A top-level `bin/` dir puts executables on PATH, but claude.ai/Cowork refuse to install plugins that have one.

Minimal valid `plugin.json`:

```json
{
  "name": "unreal-dev",
  "description": "Unreal Engine 5 skills: C++ conventions, build/cook commands, editor MCP workflow",
  "author": { "name": "Your Name" },
  "license": "MIT"
}
```

(Only `name` is strictly required. `description` and `author` silence validator warnings.
`version` is deliberately omitted, see above.)

### 2.2 Standard layout and where skills go

```
unreal-dev/                      # plugin root
├── .claude-plugin/
│   └── plugin.json              # optional manifest (ONLY this file goes in .claude-plugin/)
├── skills/
│   ├── ue-cpp-conventions/
│   │   ├── SKILL.md
│   │   └── references/...
│   └── ue-build-cook/
│       └── SKILL.md
├── agents/        (optional)  *.md subagents
├── hooks/hooks.json (optional)
├── .mcp.json      (optional)  MCP servers
└── .lsp.json      (optional)  LSP servers
```

Also allowed: a plugin with only `SKILL.md` at its root (no `skills/` dir) loads as a single skill.

### 2.3 Namespacing and invocation

- `my-plugin/skills/review/SKILL.md` becomes `/my-plugin:review`. With `name: fancy` in the frontmatter it becomes `/my-plugin:fancy`.
- The bare `/fancy` also works **unless** another command already uses that name.
- If the frontmatter `name` already carries the prefix (`my-plugin:fancy`), it is not doubled (v2.1.246+).
- Agents are namespaced too (`my-plugin:reviewer`).
- Install id is `<entry-name>@<marketplace-name>`. Components are namespaced by the **manifest** `name`, while `enabledPlugins` uses the **entry** name. Keep the two identical.

### 2.4 Develop and test

```bash
claude plugin validate ./plugins/unreal-dev        # add --strict in CI
claude --plugin-dir ./plugins/unreal-dev           # load for one session, id <name>@inline
/reload-plugins                                    # inside a session after changes
```

`CLAUDE_CODE_PLUGIN_DIRS` (v2.1.280+) does the same as `--plugin-dir` via an env var (absolute paths, `:`-separated).

---

## 3. Plugin marketplaces

### 3.1 `.claude-plugin/marketplace.json`

The file lives at `<repo-root>/.claude-plugin/marketplace.json`. The directory that contains
`.claude-plugin/` is the **marketplace root**. Relative plugin sources resolve from there,
**not** from `.claude-plugin/`.

Top-level fields: **`name`, `owner`, `plugins` are required.**
- `name`: letters, digits, `.`, `_`, `-`; starts with a letter or digit; no `..`. This is what users type after `@`. Many names are reserved: `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-*`, `agent-skills`, `claude-community`, `inline`, `skills-dir`, `synced`, `npm`, `github`, `gh`, `claudeai-*`, any non-ASCII name, and names that look like official ones (e.g. `official-claude-plugins`). Pick a neutral name without "claude"/"anthropic".
- `owner`: object, `name` required, optional `email`, `url`.
- `plugins`: array of entries. Each entry is validated separately.
- Optional: `$schema` (official repo uses `https://anthropic.com/claude-code/marketplace.schema.json`), `description` (validator warns if missing), `version`, `metadata.description`/`metadata.version`, `metadata.pluginRoot` (lets you write bare names, v2.1.239+), `forceRemoveDeletedPlugins`, `renames`, `allowCrossMarketplaceDependenciesOn`.

Plugin entry fields: **`name` and `source` are required.** Optional: `description`,
`version`, `category`, `tags`, `strict` (default `true`), `displayName`, `defaultEnabled`,
`dependencies`, `relevance`, `metadata`, `headers`/`headersHelper` (archive sources), plus
any `plugin.json` field.

Plugin `source` types:

| Type | Shape | Notes |
| :- | :- | :- |
| relative path | `"./plugins/unreal-dev"` | inside this marketplace repo; must start with `./`; no `..`; forward slashes; `"."`/`"./"` = repo root |
| `github` | `{"source":"github","repo":"owner/repo","ref":"v1","sha":"<40-hex>"}` | separate repo |
| `url` | `{"source":"url","url":"https://...git","ref":..,"sha":..}` | any git URL |
| `git-subdir` | `{"source":"git-subdir","url":..,"path":..,"ref":..,"sha":..}` | sparse checkout of one subdir |
| `npm` | `{"source":"npm","package":..,"version":..}` | |
| `archive` | `{"source":"archive","url":"https://...zip","sha256":..}` | v2.1.224+ |
| `command` | `{"source":"command","command":..}` | v2.1.229+ |

Relative paths only resolve when Claude Code has the whole repo, i.e. marketplaces added from
`github`, `git`, `file` or `directory`. They do **not** work for a marketplace added by a
direct `marketplace.json` URL.

`strict`: with the default `true`, `plugin.json` is the authority and the entry's component
fields are appended. With `strict: false` and a `plugin.json` present, declaring components
in the entry is a conflict and the plugin fails to load. With no `plugin.json`, the entry
**is** the manifest.

### 3.2 Minimal `marketplace.json` for a one-repo skills collection

```json
{
  "name": "gamedev-skills",
  "description": "Personal Claude skills for UE5, FiveM and GTA V Enhanced",
  "owner": { "name": "Your Name" },
  "plugins": [
    {
      "name": "unreal-dev",
      "source": "./plugins/unreal-dev",
      "description": "Unreal Engine 5 C++/Blueprint/build skills"
    },
    {
      "name": "fivem-dev",
      "source": "./plugins/fivem-dev",
      "description": "FiveM / Cfx.re Lua, natives, fxmanifest and txAdmin skills"
    }
  ]
}
```

Repo layout that matches:

```
<repo>/
├── .claude-plugin/marketplace.json
└── plugins/
    ├── unreal-dev/{.claude-plugin/plugin.json, skills/<skill>/SKILL.md ...}
    └── fivem-dev/{.claude-plugin/plugin.json, skills/<skill>/SKILL.md ...}
```

Alternative pattern used by `anthropics/skills` (skills kept in one flat `skills/` dir and
grouped into plugins by the marketplace entry, with no per-plugin `plugin.json`):

```json
{
  "name": "anthropic-agent-skills",
  "owner": { "name": "..." },
  "plugins": [
    { "name": "document-skills", "source": "./", "strict": false,
      "skills": ["./skills/xlsx", "./skills/docx", "./skills/pptx", "./skills/pdf"] }
  ]
}
```

When an entry whose source is the marketplace root lists `skills`, **only** those subdirectories
load. This pattern suits a repo whose `skills/<name>/` folders must also be ZIP-uploadable to
claude.ai unchanged.

### 3.3 Adding a marketplace and installing (user side)

```text
/plugin marketplace add owner/repo                 # GitHub; also owner/repo#v1.2.0 or @ref
/plugin marketplace add https://host/x/y.git       # any git host (https:// prefix required)
/plugin marketplace add ./local-dir                # local path (start with ./ or ../)
/plugin install unreal-dev@gamedev-skills          # opens details pane, you choose a scope
/plugin install unreal-dev --marketplace owner/repo   # add + install in one step (v2.1.275+)
/plugin                                            # Discover / Installed / Marketplaces / Errors tabs
/reload-plugins
```

From a shell: `claude plugin marketplace add owner/repo [--scope project]`,
`claude plugin install unreal-dev@gamedev-skills [--scope user|project|local]`,
`claude plugin list`, `claude plugin update`, `claude plugin marketplace update`.
`/plugin market` is accepted as a short form.

Install scopes: **user** (`~/.claude/settings.json`), **project** (`.claude/settings.json`,
committed), **local** (`.claude/settings.local.json`). Precedence: local > project > user;
managed settings override everything.

### 3.4 Private GitHub repo

- Claude Code has **no token of its own**, and `marketplace.json` has no token field. It runs `git` non-interactively with whatever credentials the machine already has.
- `owner/repo` shorthand: Claude Code probes `ssh -T git@github.com`. If the probe succeeds it clones over SSH, otherwise over HTTPS. `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` skips the probe.
- HTTPS: a credential helper must already hold a credential. On GitHub: `gh auth login` then `gh auth setup-git`. Interactive prompts are suppressed, so an unauthenticated host simply fails.
- SSH: the key must work without a passphrase prompt (ssh-agent) and the host must be in `known_hosts`.
- `GITHUB_TOKEN`/`GH_TOKEN` in the environment does **not** by itself authenticate background auto-update. It only works through a helper such as `gh auth setup-git`.
- CI (GitHub Actions): export a PAT/app token with read access as `GH_TOKEN`, then `gh auth setup-git`. The default workflow token cannot read another repo.
- `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` keeps the last checkout when a background refresh cannot authenticate.

### 3.5 Auto-enable a marketplace and plugins for a project (`.claude/settings.json`)

Exact shape (settings reference, `extraKnownMarketplaces` and `enabledPlugins`):

```json
{
  "extraKnownMarketplaces": {
    "gamedev-skills": {
      "source": {
        "source": "github",
        "repo": "OWNER/REPO"
      },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "unreal-dev@gamedev-skills": true,
    "fivem-dev@gamedev-skills": true
  }
}
```

- Use the marketplace's `name` from `marketplace.json` as the map key. Claude Code matches declarations to marketplaces by that name, and the troubleshooting page lists "source doesn't match its extraKnownMarketplaces entry" errors when the two disagree. For a `settings` source the docs state this explicitly ("the `name` must match the marketplace key"). `enabledPlugins` keys are `<entry-name>@<marketplace-name>` to boolean.
- Other source forms: `{"source":"git","url":"https://...git","ref":"main"}`, `{"source":"directory","path":...}`, `{"source":"file","path":...}`, `{"source":"url","url":".../marketplace.json","headers":{...}}`, `{"source":"settings","name":..,"plugins":[...]}`. `github`/`git` also take `ref`, `path` (default `.claude-plugin/marketplace.json`) and `sparsePaths`.
- `autoUpdate` defaults to `false` for third-party marketplaces. Set it to `true` if you want pushes to arrive automatically.
- Shortcut that writes the marketplace part: `claude plugin marketplace add OWNER/REPO --scope project`, then commit `.claude/settings.json`.
- **Workspace trust gate:** a repo's `extraKnownMarketplaces` applies only after the user accepts the trust dialog for that folder. In an untrusted folder, and in `-p` runs in never-trusted folders, it is ignored **silently**. `enabledPlugins` itself is read at session start.
- **Install behaviour:** plugins whose entry uses a **relative-path source** load straight from the marketplace copy once it is registered, so no per-user install is needed. Plugins whose entry points to an **external** source (`github`, `url`, `npm`, ...) are not fetched from project settings alone. Each user sees `Plugin "<name>" is enabled in project settings but isn't installed` until they run `claude plugin install <name>@<marketplace> --scope project`. **Use relative-path entries in our repo.**
- Opt out on one machine: set `"name@market": false` in `.claude/settings.local.json` (project beats user settings, so `false` in `~/.claude/settings.json` does not override a project `true`).
- CI/`-p`: installs run in the background. `CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1` makes the first query wait for them.
- In a session with several repos, only `enabledPlugins` and `extraKnownMarketplaces` are read from each repo's `.claude/settings.json`.

---

## 4. Does this work in Claude Code on the web (cloud sessions at claude.ai/code)?

**No, not for plugins.** The cloud-environments page ("What carries over from your setup")
and the install page ("Cloud session" tab) both say so:

| In a cloud session | Available? |
| :- | :- |
| repo `CLAUDE.md`, `.claude/rules/` | yes |
| repo `.claude/skills/`, `.claude/agents/`, `.claude/commands/` | **yes** (part of the clone) |
| repo `.claude/settings.json` hooks + permission rules | yes, in a single-repo session |
| repo `.mcp.json` | yes, in a single-repo session |
| **plugins/marketplaces declared in repo `.claude/settings.json`** (`enabledPlugins`, `extraKnownMarketplaces`) | **no**. A cloud session never shows the trust dialog and does not install them |
| `~/.claude/skills`, `~/.claude/CLAUDE.md`, user-scope plugins on your PC | no |
| skills enabled on your **claude.ai account** | **yes** (synced at session start) |
| org plugins via server-managed settings (Team/Enterprise) | yes |
| `/plugin` command | not available in cloud sessions |

What works on the web:
1. **Commit the skills into the game repo's `.claude/skills/`**, either as a copy or via a sync script from the skills repo. This is the most reliable option.
2. **Upload the skill as a ZIP to claude.ai** (section 6). Claude.ai-enabled skills load in cloud sessions, Cowork and signed-in terminal sessions. Only the six spec frontmatter keys are allowed.
3. Untested ideas (not documented as supported, so verify before relying on them): a cloud-environment **setup script** that runs `claude plugin marketplace add ...` and `claude plugin install ...` in the VM, or setting `CLAUDE_CODE_PLUGIN_DIRS=/abs/path/to/clone/plugins/x` as an environment variable. Private marketplace clones from inside the VM may also fail, because the cloud GitHub proxy is scoped to the session's repos.
4. Git submodules for `.claude/skills/` are untested in cloud sessions (unknown whether the clone is recursive). Avoid them.

---

## 5. Personal vs project skills (quick reference)

- Personal: `~/.claude/skills/<name>/SKILL.md` (Windows: `%USERPROFILE%\.claude\skills\...`). Available in every local project, the desktop app's local sessions and VS Code (they share settings files). Not in cloud/Cowork.
- Project: `<repo>/.claude/skills/<name>/SKILL.md`, committed. Available to every collaborator, in cloud sessions, and in nested/monorepo setups.
- Precedence on name clash: enterprise > personal > project.
- Remove: delete the folder. Plugin skills: `/plugin uninstall <plugin>@<marketplace>`.
- A personal skills dir can contain **symlinks** to folders in a cloned skills repo, which gives a cheap "install" without a marketplace.

---

## 6. Adding a custom skill in the claude.ai app

From the support articles (custom skills article dated about 2026-07-22) and the platform overview:

- **Where:** **Customize > Skills**, then click **"+"**, **"+ Create skill"**, **"Upload a skill"**, and upload a ZIP. The skill then appears in the list and can be toggled. (Older docs and the platform overview still say "Settings > Features" or "Settings > Capabilities". The current help centre uses **Customize > Skills**.)
- **Prerequisite:** "Code execution and file creation" must be on. Individual plans: **Settings > Capabilities**. Team/Enterprise: owner enables "Code execution and file creation" and "Skills" under **Organization settings > Plugins & skills > Policy** (Team: on by default).
- **Plans:** the help centre now says **Free, Pro, Max, Team and Enterprise**. The platform overview still says "Pro, Max, Team, and Enterprise". Treat Free as likely supported but unconfirmed.
- **ZIP structure:** the skill **folder** must be the ZIP root entry, and the folder name should match the skill name:
  ```
  my-skill.zip
    └── my-skill/
        ├── SKILL.md      (help centre spells it skill.md; SKILL.md is the canonical name everywhere else)
        └── resources/ ...
  ```
  Files directly at the ZIP root are wrong.
- **Frontmatter:** only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Anything else is rejected (section 1.3).
- **Visibility:** uploaded skills are personal. Team/Enterprise can **share** them with people or groups (view-only for recipients) or **publish to the org** library (optional review; "Available to install" / "Installed by default" / "Required").
- **Sync into Claude Code:** skills enabled on claude.ai are downloaded into Claude Code terminal sessions signed in with that account (v2.1.273+, into `~/.claude/skills/synced/`, re-checked about every 10 min), and into cloud and Cowork sessions. They are invoked as `/<name>`, or as `/anthropic-skills:<name>` when the short name collides (v2.1.269+). Turn this off with `"syncClaudeAiSkills": false`.
- Example templates: https://github.com/anthropics/skills/tree/main/skills

---

## 7. Useful built-ins for our domain (verified in `claude-plugins-official/.claude-plugin/marketplace.json`)

- `lua-lsp@claude-plugins-official`: runs `lua-language-server` for `.lua`. Combine it with a project `.luarc.json` that loads the FiveM natives addon (see docs/external-resources.md), so Claude sees FiveM type errors after edits.
- `clangd-lsp@claude-plugins-official`: `clangd --background-index` for C/C++. For UE5 it needs a `compile_commands.json` (generate it with UnrealBuildTool's clang-database mode; untested here).
- `unreal-engine-skills-for-claude-code@claude-plugins-official`: **Epic Games' official** plugin (MIT, v3.1.1). Skills plus a SessionStart hook for the UE 5.8 experimental `ModelContextProtocol` editor plugin (default `http://127.0.0.1:8000/mcp`). Details are in docs/external-resources.md.
- `skill-creator@claude-plugins-official` and `plugin-dev@claude-plugins-official` help author and evaluate skills and plugins.

---

## 8. Recent changes (2026) to be aware of

- Docs moved to `code.claude.com/docs/en/...`. Plugin docs were split into `/plugins/overview`, `/plugins/manifest-reference`, `/plugins/marketplace-reference`, `/plugins/host-marketplace`, `/plugins/loading`, and so on. Old `docs.claude.com/en/docs/claude-code/plugin-marketplaces` links are outdated.
- `plugin.json` is now **optional**. A plugin may be just a root `SKILL.md`.
- Skill frontmatter grew: `when_to_use`, `arguments`, `effort`, `background` (v2.1.218), `paths`, `shell`, `metadata` (v2.1.222), `license`/`compatibility` accepted. The listing cap is 1,536 chars for `description` + `when_to_use`.
- claude.ai to Claude Code skill **and plugin** sync in terminal sessions (v2.1.273). The `anthropic-skills:` namespace is reserved (v2.1.269 to v2.1.281 changes).
- `/plugin install <name> --marketplace <source>` (v2.1.275). More reserved marketplace names (`npm`, `github`, `gh`, v2.1.275; look-alike spellings, v2.1.280).
- `extraKnownMarketplaces` same-name entries now replace whole entries instead of merging field by field (v2.1.228). `skipLfs` is a no-op (v2.1.274). LFS is never fetched.
- `CLAUDE_CODE_PLUGIN_DIRS` env var (v2.1.280). `claude plugin validate` checks MCP entries (v2.1.281).
- Official LSP plugins (incl. `lua-lsp`, `clangd-lsp`). Epic's official Unreal plugin is in the official marketplace.
- Cloud sessions explicitly **do not** load repo-declared plugins (documented in the cloud-environments table).
- claude.ai UI moved skills to **Customize > Skills**. Team/Enterprise gained skill sharing and org publishing. The help centre lists the Free plan as supported.

## 9. Uncertain or conflicting points

1. **Description length on claude.ai:** the help centre article says `description` is max **200 characters**, while the Agent Skills spec and platform docs say 1024. The upload validator's real limit was not tested. Keep descriptions short (≤200 chars if the skill must be uploaded, or test one upload).
2. The help centre lists `dependencies` as an optional field and names the file `skill.md`. Both contradict the six-key validator described in the Claude Code docs. Follow the Claude Code docs and spec (`SKILL.md`, six keys).
3. The platform overview says claude.ai custom skills "do not sync across surfaces" and "cannot be centrally managed". The newer Claude Code docs and help centre describe claude.ai-to-Claude-Code sync and org sharing/publishing. The newer sources are probably right, and the platform page is stale.
4. Epic's plugin README says teammates "are prompted to install it automatically" via `enabledPlugins`. The Claude Code docs say external-source plugins enabled only in project settings are **not** fetched until each user runs `claude plugin install ... --scope project`. Expect to install it manually once per machine.
5. Whether synced claude.ai **plugins** (not just skills) load in cloud sessions is not stated (docs mention Cowork and terminal only).
6. The cloud-session workarounds in section 4 (setup script, `CLAUDE_CODE_PLUGIN_DIRS`, submodules) are untested.
7. agentskills.io, dev.epicgames.com and docs.fivem.net could not be fetched from this sandbox (egress policy). The spec was read from its GitHub source. Epic page facts come from search-index snippets and Epic's own GitHub README.
