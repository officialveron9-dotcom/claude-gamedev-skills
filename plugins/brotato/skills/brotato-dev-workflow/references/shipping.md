# Shipping to the Steam Workshop and surviving updates

Checked 2026-10-08. Steam app id `1942280`. Upload rules confirmed in Combat Tracker's `tools/workshop_upload.py` (Steamworks UGC flat API, tested 2026-10-01), Synergies' `publish-steamcmd.sh` and FullMapCamera's `docs/publishing.md`. Zip layout, GodotWorkshopUtility basics and the in-game Mods menu are in `brotato-modding`; the pre-release checklist is in `brotato-stability-performance`.

## Contents
- Three upload paths
- SteamCMD setup and `.vdf`
- First upload
- Every update
- What breaks players
- After a Brotato patch

## Three upload paths

| Path | Pros | Cons |
|---|---|---|
| `GodotWorkshopUtility.exe` in the game folder (launch via Steam beta branch `modding`, or put `steam_appid.txt` = `1942280` beside it) | nothing to install | title = zip filename on every upload, no description/changenote fields, blank Workshop ID silently creates a new item, breaks if `override.cfg` exists in the game folder |
| **SteamCMD** `+workshop_build_item item.vdf` | title/description/changenote versioned in git, scriptable, works on Windows/macOS/Linux | first login interactive (Steam Guard), description only in one language per file |
| Python + `steam_api64.dll` from the game folder (Combat Tracker, MIT) | per-language titles/descriptions, tags, visibility, preview in one run, uses the running Steam client's login, no `steam_appid.txt` | 64-bit Python, Steam client must run, Steam shows you "playing Brotato" meanwhile |

Use SteamCMD for a one-author mod; copy Combat Tracker's script when you need several Workshop languages.

## SteamCMD setup and `.vdf`

Install: Windows `steamcmd.zip` from Valve's SteamCMD page, macOS `brew install --cask steamcmd`, Linux `apt install steamcmd` (multiverse) or the tarball.

`workshop_item.vdf` (template; `publish.py`/`.sh` fills absolute paths - SteamCMD resolves relative paths against its own cwd):

```
"workshopitem"
{
	"appid"            "1942280"
	"publishedfileid"  "0"
	"contentfolder"    "__CONTENT__"
	"previewfile"      "__PREVIEW__"
	"title"            "QoLPack - Online co-op quality of life"
	"description"      "[h1]QoLPack[/h1]..."
	"changenote"       "v1.0.0 - first release"
}
```

`tools/publish.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ACCOUNT=${1:?usage: publish.sh <steam_account>}
REPO=$(cd "$(dirname "$0")/.." && pwd)
python "$REPO/tools/validate_manifest.py" "$REPO/mods-unpacked/YourName-QoLPack" >/dev/null
ZIP=$(python "$REPO/tools/pack.py" | head -1)
CONTENT="$REPO/build/workshop"; rm -rf "$CONTENT"; mkdir -p "$CONTENT"; cp "$ZIP" "$CONTENT/"   # ONLY the zip
VERSION=$(python -c "import json;print(json.load(open('$REPO/mods-unpacked/YourName-QoLPack/manifest.json'))['version_number'])")
NOTE=$(cat "$REPO/docs/workshop/changenotes/v$VERSION.txt")
DESC=$(cat "$REPO/docs/workshop/description.txt")
python - "$REPO/workshop_item.vdf" "$CONTENT" "$REPO/docs/workshop/preview.png" "$NOTE" "$DESC" > "$REPO/build/item.vdf" <<'PY'
import sys; t = open(sys.argv[1], encoding="utf-8").read()
esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
print(t.replace("__CONTENT__", sys.argv[2]).replace("__PREVIEW__", sys.argv[3])
       .replace('"changenote"       "v1.0.0 - first release"', '"changenote"       "%s"' % esc(sys.argv[4]))
       .replace('"description"      "[h1]QoLPack[/h1]..."', '"description"      "%s"' % esc(sys.argv[5])))
PY
grep -q '"publishedfileid"  "0"' "$REPO/build/item.vdf" && echo "publishedfileid 0: this CREATES a new item; paste the printed id into workshop_item.vdf afterwards"
steamcmd +login "$ACCOUNT" +workshop_build_item "$REPO/build/item.vdf" +quit
```

Rules: `contentfolder` must contain only the zip (Steam replaces the item's content with the whole folder); `previewfile` < 1 MB; description BBCode < 8000 bytes UTF-8; title <= 128 bytes; the zip filename is what players see in `workshop/content/1942280/<id>/`, keep it `<ModId>-<version>.zip`.

## First upload

1. Account requirements: >= USD 5 spent on Steam, Workshop legal agreement accepted (`https://steamcommunity.com/sharedfiles/workshoplegalagreement`), otherwise the item stays invisible to others (`needs_agreement = true` in the submit result).
2. Upload with `publishedfileid 0` (SteamCMD prints `PublishedFileID`) or a blank ID in GodotWorkshopUtility. New items start **hidden**. Paste the id into `workshop_item.vdf` / `docs/workshop/workshop.json` immediately and commit it.
3. Subscribe with your own account, wait for the download, compare: `sha256sum "<Steam>/steamapps/workshop/content/1942280/<id>/YourName-QoLPack-1.0.0.zip" dist/YourName-QoLPack-1.0.0.zip` - identical hashes (FullMapCamera's publish check).
4. Play one full loop from the Workshop copy (menu, wave, shop, end screen, quit), run `check_logs.py`. Test from a second account if you have one.
5. Set visibility to public on the item page (or `--visibility public` with the Steamworks script). Add tags (`Utilities`, `GUI`, ...) there if the uploader did not.

## Every update

1. `CHANGELOG.md` + `docs/workshop/changenotes/v<new>.txt`, bump `version_number` + `VERSION`, run the full definition-of-done (SKILL.md section 8) and the release checklist from `brotato-stability-performance`.
2. Tag `v<new>` (GitHub release zip from CI), then upload the same zip (`sha256` equal) to the Workshop.
3. Changenote behaviour (measured by Combat Tracker 2026-10-01): a changenote is recorded only on a submit whose **files changed**; a submit without file changes drops the changenote; the note is stored under the submit language and shown to all languages lacking a translation; other languages are added on the item's changelog web page.
4. Keep `dist/<previous>.zip`: rolling back is re-uploading it with a new changenote.
5. Steam pushes the new zip to subscribers automatically; they get it at their next game start (mods load at startup only). Nothing can be hot-reloaded for players.

## What breaks players

| Change | Effect on subscribers | Rule |
|---|---|---|
| Renaming `namespace` or `name` | new mod ID: their enable state (`user://mod_user_profiles.json`) and configs (`user://configs/<OldId>/`) no longer apply, the old ID lingers as a ghost entry | never rename after the first public release |
| Removing or retyping a `config_schema` property | existing `default.json` configs validate against the new schema; invalid defaults -> `The default config values for X are invalid. Configs will not be loaded.` | add properties with defaults, never remove or change types; read with fallbacks |
| Changing network message formats | mixed versions in one lobby desync or crash | bump the protocol version and refuse mismatched peers with a clear message (`brotato-online-multiplayer`) |
| Shipping two zips or a stale zip in the item folder | both load, last one wins per file | `contentfolder` holds exactly one zip |
| Logged `ERROR` on a common path | CrashReporter disables all mods for everyone who hits it | zero errors in a full loop before upload |
| Adding a hard `dependencies` entry | players without it get `Missing dependency` and your mod does not load | prefer `optional_dependencies` + runtime `get_node_or_null("/root/ModLoader/<Id>")` |

## After a Brotato patch

Brotato patches change signatures and private members without notice (`clean_up_room()` lost its arguments in 1.1.15.4; the hash refactor in 1.1.14 broke every string-keyed mod). The day a patch lands:

1. Read the version line at the top of `godot.log` (engine) and the game's version.
2. Re-decompile into a fresh folder, `diff -r` only the scripts you extend or read (`extensions/` mirrors them, so `diff -r old/ new/ --include=main.gd --include=run_data.gd ...`).
3. Loop A: open the project with the new scripts, launch - signature mismatches are parse errors here only.
4. Loop C: `run_test.py` with the new `Brotato.pck`, then the LAN matrix if you ship netcode.
5. Update `compatible_game_version`, `BUILT_FOR_GAME` (or similar) constant, CHANGELOG, bump the patch version, upload. If a fix needs time, ship a version whose extensions switch themselves off with one logged warning on the untested game version instead of leaving a mod that disables everyone's mods.
6. Watch the Workshop comments and Steam discussions for "Unexpected error in mod" reports for a week.
