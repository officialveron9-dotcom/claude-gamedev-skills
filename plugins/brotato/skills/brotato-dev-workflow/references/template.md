# Repo template for a Brotato mod

Checked 2026-10-08. All scripts are Python 3.8+ standard library, run from the repo root. Replace `YourName-QoLPack`, `qolpack_` and the version-const location.

## Contents
- Layout
- `tools/pack.py`
- `tools/validate_manifest.py`
- `gdlintrc`, `.editorconfig`, `.pre-commit-config.yaml`
- GitHub Actions: `check.yml`, `release.yml`
- `.gitignore`, `CHANGELOG.md`, versioning
- `CLAUDE.md` for the mod repo

## Layout

```
qolpack/
├── mods-unpacked/YourName-QoLPack/   # ships; folder == "<namespace>-<name>" from manifest.json
│   ├── manifest.json                  # see brotato-modding for the required keys
│   ├── mod_main.gd                    # const VERSION := "1.0.0" (checked by pack.py), installs extensions in _init()
│   ├── extensions/<mirrors vanilla path>.gd
│   ├── core/                          # pure GDScript, no game or ModLoader globals -> unit-testable
│   ├── game/                          # everything that touches RunData, signals, nodes
│   └── ui/                            # see brotato-ui-qol
├── tests/            # smoke.gd / lan.gd (loop C), driver.gd, unit/test_*.gd (GUT); never packed
├── tools/            # pack.py validate_manifest.py check_logs.py build_testpack.py run_test.py sync.py
├── docs/workshop/    # description.txt (BBCode < 8000 bytes), changenotes/v1.0.0.txt, preview.png (< 1 MB)
├── .github/workflows/check.yml, release.yml
├── .import/          # only cooked files of YOUR assets (qolpack_*.stex), copied from the editor project
├── CLAUDE.md  CHANGELOG.md  README.md  LICENSE  gdlintrc  .editorconfig  .pre-commit-config.yaml  .gitignore
└── project.godot     # optional, only for GUT (config_version=4)
```

Why not `src/`: `ModLoaderMod.install_script_extension` paths must contain `res://mods-unpacked/<Id>/`, the junction into the decompiled project points straight at the repo folder, `pack.py` needs no rename step, and every reference repo (Combat Tracker, FullMapCamera, Synergies, ShareMoney) uses this layout.

## `tools/pack.py`

```python
"""Build dist/<ModId>-<version>.zip with the exact root Mod Loader expects. Usage: python tools/pack.py [vX.Y.Z]"""
import hashlib, json, os, re, sys, zipfile

MOD_ID = "YourName-QoLPack"
VERSION_CONST = ("mod_main.gd", r'^const VERSION := "([^"]+)"')   # file (relative to the mod dir) + regex
ASSET_PREFIX = "qolpack_"                                           # your cooked assets in .import/
SKIP_EXT = {".md", ".bak", ".pyc", ".ps1", ".py"}

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mod_dir = os.path.join(repo, "mods-unpacked", MOD_ID)
with open(os.path.join(mod_dir, "manifest.json"), encoding="utf-8") as f:
    manifest = json.load(f)
version = manifest["version_number"]
if manifest["namespace"] + "-" + manifest["name"] != MOD_ID:
    sys.exit("manifest namespace-name != %s" % MOD_ID)
with open(os.path.join(mod_dir, VERSION_CONST[0]), encoding="utf-8") as f:
    m = re.search(VERSION_CONST[1], f.read(), re.M)
if m and m.group(1) != version:
    sys.exit("version mismatch: manifest %s, %s %s" % (version, VERSION_CONST[0], m.group(1)))
if len(sys.argv) > 1 and sys.argv[1].lstrip("v") != version:
    sys.exit("tag %s != manifest version %s" % (sys.argv[1], version))

entries = []
for root, dirs, files in os.walk(mod_dir):
    dirs.sort()
    for name in sorted(files):
        if os.path.splitext(name)[1].lower() in SKIP_EXT:
            continue
        path = os.path.join(root, name)
        entries.append((os.path.relpath(path, repo).replace(os.sep, "/"), path))
import_dir = os.path.join(repo, ".import")
if os.path.isdir(import_dir):
    for name in sorted(os.listdir(import_dir)):
        if name.startswith(ASSET_PREFIX):
            entries.append((".import/" + name, os.path.join(import_dir, name)))

os.makedirs(os.path.join(repo, "dist"), exist_ok=True)
out = os.path.join(repo, "dist", "%s-%s.zip" % (MOD_ID, version))
with zipfile.ZipFile(out, "w") as z:
    for arcname, path in entries:
        info = zipfile.ZipInfo(arcname, (2026, 1, 1, 0, 0, 0))     # fixed time, stored: byte-identical everywhere
        info.compress_type = zipfile.ZIP_STORED
        info.create_system = 3
        info.external_attr = 0o644 << 16
        with open(path, "rb") as f:
            z.writestr(info, f.read())
with open(out, "rb") as f:
    print(out)
    print("sha256", hashlib.sha256(f.read()).hexdigest())
```

Check the result: `python -m zipfile -l dist/YourName-QoLPack-1.0.0.zip` - every entry starts with `mods-unpacked/YourName-QoLPack/` or `.import/`, forward slashes only. Do not use Windows PowerShell 5.1 `Compress-Archive` (backslash entry names) or zip the mod folder itself. `tools/sync.py` = `pack.py` + delete `*.zip` in the Workshop item folder + copy.

## `tools/validate_manifest.py`

Mirrors `mod_manifest.gd` (6.2.0/6.3.0): required keys, regexes, exact failure conditions.

```python
"""Validate a mod folder like Mod Loader 6.x does. Usage: python tools/validate_manifest.py mods-unpacked/<ModId>"""
import json, os, re, sys

ROOT = ["name", "namespace", "version_number", "website_url", "description", "dependencies", "extra"]
EXTRA = ["authors", "compatible_mod_loader_version", "compatible_game_version"]
LISTS = ["dependencies", "optional_dependencies", "load_before", "incompatibilities"]
NAME = re.compile(r"^[a-zA-Z0-9_]{3,}$")
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def check(mod_dir):
    errors = []
    folder = os.path.basename(os.path.abspath(mod_dir))
    try:
        with open(os.path.join(mod_dir, "manifest.json"), encoding="utf-8") as f:
            m = json.load(f)                      # strict JSON: trailing commas and comments fail here, as in the game
    except (OSError, ValueError) as e:
        return ["manifest.json: %s" % e]
    g = m.get("extra", {}).get("godot", {})
    errors += ["missing root key %s" % k for k in ROOT if k not in m]
    errors += ["missing extra.godot key %s" % k for k in EXTRA if k not in g]
    if errors:
        return errors
    for k in ("name", "namespace"):
        if not NAME.match(str(m[k])):
            errors.append('%s "%s": only letters, digits, _ and at least 3 chars' % (k, m[k]))
    if not SEMVER.match(str(m["version_number"])):
        errors.append('version_number "%s" must be X.Y.Z without leading zeros' % m["version_number"])
    cmv = g["compatible_mod_loader_version"]
    if not isinstance(cmv, list) or not cmv or not all(SEMVER.match(str(v)) for v in cmv):
        errors.append("compatible_mod_loader_version must be a non-empty array of X.Y.Z (a string is deprecated)")
    mod_id = "%s-%s" % (m["namespace"], m["name"])
    if folder != mod_id:
        errors.append('folder "%s" != "%s"' % (folder, mod_id))
    seen = {}
    for key in LISTS:
        for dep in list(m.get(key) or []) + list(g.get(key) or []):
            parts = dep.split("-")
            if len(parts) != 2 or not all(NAME.match(p) for p in parts):
                errors.append('%s: "%s" is not Namespace-Name with exactly one hyphen' % (key, dep))
            if dep == mod_id:
                errors.append("%s lists the mod itself" % key)
            if dep in seen and seen[dep] != key:
                errors.append('"%s" appears in both %s and %s' % (dep, seen[dep], key))
            seen[dep] = key
    for prop, schema in ((g.get("config_schema") or {}).get("properties") or {}).items():
        if "default" not in schema:
            errors.append("config_schema property %s has no default (default config would be invalid)" % prop)
    if not os.path.isfile(os.path.join(mod_dir, "mod_main.gd")):
        errors.append("missing mod_main.gd")
    return errors


if __name__ == "__main__":
    problems = check(sys.argv[1])
    print("\n".join(problems) or "manifest OK")
    sys.exit(1 if problems else 0)
```

## `gdlintrc`, `.editorconfig`, `.pre-commit-config.yaml`

`gdlint -d` writes the full default `gdlintrc`; edit these keys (the rest of the defaults fit Godot 3 style):

```yaml
max-line-length: 120          # vanilla signatures are long; gdformat -l 120 to match
max-file-lines: 1500
disable: []                   # keep class-definitions-order: it catches vars declared after funcs
excluded_directories: !!set { .git: null, build: null, dist: null, .local: null, reference: null, addons: null }
```

Override names must equal the vanilla name even when `function-name` dislikes them: `func _on_EntitySpawner_player_spawned(player):  # gdlint:ignore = function-name`.

`.editorconfig` (editors and AI tools then default to tabs): `[*.gd]` `indent_style = tab`, `end_of_line = lf`, `charset = utf-8`, `insert_final_newline = true`.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Scony/godot-gdscript-toolkit
    rev: 3.6.0
    hooks:
      - id: gdlint
        additional_dependencies: ["setuptools<81"]   # gdtoolkit 3.x imports pkg_resources
      - id: gdformat
        additional_dependencies: ["setuptools<81"]
  - repo: local
    hooks:
      - id: manifest
        name: validate manifest
        entry: python tools/validate_manifest.py mods-unpacked/YourName-QoLPack
        language: system
        pass_filenames: false
```

## GitHub Actions

Packaging, lint and manifest checks need no game. Anything that runs Brotato stays on a machine with the game (Combat Tracker says the same). `.github/workflows/check.yml`:

```yaml
name: check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install "gdtoolkit==3.*" "setuptools<81"
      - run: gdlint mods-unpacked && gdformat --check mods-unpacked
      - run: python tools/validate_manifest.py mods-unpacked/YourName-QoLPack
      - run: python tools/pack.py
      - uses: actions/upload-artifact@v4
        with: { name: mod-zip, path: dist/*.zip }
  unit:                      # only if you use GUT on core/ (needs project.godot at the repo root)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          wget -q https://github.com/godotengine/godot-builds/releases/download/3.7-dev1/Godot_v3.7-dev1_linux_headless.64.zip
          unzip -q Godot_v3.7-dev1_linux_headless.64.zip
          ./Godot_v3.7-dev1_linux_headless.64 --audio-driver Dummy --path . -s addons/gut/gut_cmdln.gd -gdir=res://tests/unit -ginclude_subdirs -gexit -glog=1
```

Alternative container: `barichello/godot-ci:3.6` (Docker Hub tags `3.5.2`, `3.6`, `3.6.2` exist; no 3.7 image) with `godot` on the PATH.

`.github/workflows/release.yml` (tag `v1.2.3` = release; `pack.py` refuses a tag/manifest mismatch):

```yaml
name: release
on:
  push:
    tags: ["v*"]
permissions: { contents: write }
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python tools/validate_manifest.py mods-unpacked/YourName-QoLPack && python tools/pack.py "${GITHUB_REF_NAME}"
      - run: gh release create "${GITHUB_REF_NAME}" dist/*.zip --title "${GITHUB_REF_NAME}" --notes-file docs/workshop/changenotes/${GITHUB_REF_NAME}.txt
        env: { GH_TOKEN: "${{ github.token }}" }
```

The Workshop upload is never done from CI: it needs the author's logged-in Steam client (shipping.md).

## `.gitignore`, `CHANGELOG.md`, versioning

```
build/
dist/
.local/
reference/            # decompiled game scripts for diffing (never commit)
*.pck
*.zip
__pycache__/
.import/*             # then whitelist your own cooked assets:
!.import/qolpack_*
mods-unpacked/*/assets/third_party/   # anything you may not redistribute
```

- `CHANGELOG.md`: one `## 1.2.0 - 2026-10-08 (Brotato 1.1.15.4, ML 6.2/6.3)` block per version, bullets `Added/Changed/Fixed`, plus "Known incompatibilities". `docs/workshop/changenotes/v1.2.0.txt` is the same text in BBCode and feeds both the GitHub release and the Workshop changenote.
- Semver as Synergies' house rules: patch = fix, minor = feature, major = breaking (config schema changed incompatibly, network protocol changed, requires other mods to change). Bump on every change that ships; the in-game watermark/log line `loaded v1.2.0` tells testers which zip is really loaded.
- Version lives in exactly two places: `manifest.json` `version_number` and `mod_main.gd` `const VERSION`. `pack.py` fails on mismatch; Combat Tracker and Synergies both enforce this.

## CLAUDE.md for the mod repo

```markdown
# QoLPack - Brotato mod (online co-op + QoL)

Target: Brotato 1.1.15.x = custom Godot **3.7-dev** + Godot Mod Loader **6.2/6.3**. GDScript 3 only:
`.method()` parent calls, `yield`, `connect("sig", self, "_m")`, `export`, `onready`, tabs. A single Godot 4
token (`@export`, `await`, `super`) breaks the whole mod. Load skills `brotato-modding`,
`godot3-gdscript-pitfalls`, `brotato-dev-workflow` (and `brotato-online-multiplayer` for netcode).

## Commands (repo root)
- Lint/format: `gdlint mods-unpacked && gdformat --check mods-unpacked` (fix: `gdformat mods-unpacked`)
- Manifest: `python tools/validate_manifest.py mods-unpacked/YourName-QoLPack`
- Pack: `python tools/pack.py` -> `dist/YourName-QoLPack-<version>.zip`; inspect with `python -m zipfile -l`
- Game test (needs Brotato installed, `BROTATO_GAME_DIR` optional): `python tools/run_test.py`
- Log check after any manual run: `python tools/check_logs.py YourName-QoLPack`
- Headless run in the decompiled project (`C:\dev\brotato-decompiled`, not in this repo): `bash tests/run_headless.sh`
- Push to the Workshop folder for manual play: `python tools/sync.py`
- Logs: `%APPDATA%\Brotato\logs\godot.log` and `modloader.log`; launch option `--log-info`

## Rules
- Never commit or paste game code: `reference/`, the decompiled project, `*.pck`, `build/`, `dist/`, `.local/`, logs.
- Override signatures are copied from the current decompiled script, never guessed; every override calls `.method()`.
- Extensions are installed in `mod_main._init()`; `core/` never references RunData/ItemService/ModLoader*.
- Bump `version_number` + `VERSION` and add a CHANGELOG line with every shipped change.

## Done means
gdlint + gdformat --check clean, manifest OK, pack built and listed, `check_logs.py` clean after a game run
(or state that no game is available here), headless run passed if the project exists. Report what did not run.
```
