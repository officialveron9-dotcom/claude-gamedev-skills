# Packaging, dev loops, decompiling and Workshop upload

## Contents
- Zip layout and build script
- Assets (.import), translations, audio
- Dev loop A: shipped game + Workshop folder
- Dev loop B: decompiled project in the Godot 3 editor
- Dev loop C: automated runs
- Workshop upload
- Updating after a game patch
- Legal

## Zip layout and build script

```
YourName-QoLPack-1.0.0.zip
├── .import/                         # only if you ship imported assets - only YOUR files
│   └── qolpack_icon.png-<md5>.stex
└── mods-unpacked/
    └── YourName-QoLPack/
        ├── manifest.json
        ├── mod_main.gd
        ├── extensions/...
        └── assets/qolpack_icon.png(.import)
```

- Root entries must be `mods-unpacked/` (and `.import/`). Zipping the mod folder itself, or wrapping everything in an extra top folder, gives `The mod zip at path "..." does not have the correct file structure.`
- One mod per zip. ML keys the zip by the first new folder it finds under `mods-unpacked/`.
- Entry names need `/` separators; check with `python -m zipfile -l file.zip`.
- Zips cannot replace vanilla files (mounted with `replace_files = false`); use `take_over_path` in code.
- Do not include `.md`, test folders, dev tooling or anything from the game.

Minimal deterministic builder (Python 3, run from the repo root that contains `mods-unpacked/`):

```python
import os, sys, zipfile
mod_id, version = sys.argv[1], sys.argv[2]           # e.g. YourName-QoLPack 1.0.0
src = os.path.join("mods-unpacked", mod_id)
out = f"dist/{mod_id}-{version}.zip"
os.makedirs("dist", exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(src):
        dirs.sort()
        for f in sorted(files):
            if f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            z.write(p, p.replace(os.sep, "/"))
    for f in sorted(os.listdir(".import")) if os.path.isdir(".import") else []:
        if f.startswith("qolpack_"):                    # your asset prefix only
            z.write(os.path.join(".import", f), ".import/" + f)
print(out)
```

Check that `version_number` in `manifest.json` matches the version you pass (mods that print their version in-game catch "old zip still loaded" instantly).

## Assets (.import), translations, audio

- Exported Godot 3 games cannot import raw PNG/WAV/OGG at runtime through `load()`. The zip needs `<asset>.import` next to the asset and the cooked file in root `.import/` (`.stex` textures, `.sample`/`.oggstr` audio). Produce them by opening a Godot 3.x editor project containing `res://mods-unpacked/<ModId>/` and letting it import. Missing: `No loader found for resource: res://mods-unpacked/...`.
- Prefix every asset filename (`qolpack_*.png`) so your `.import` entries are easy to pick and never collide.
- No-editor alternative for images: read the PNG bytes with `File` and build an `ImageTexture` (see SKILL.md). Cache results; decoding per frame is expensive.
- Translations: either ship editor-generated `*.translation` and call `ModLoaderMod.add_translation`, or parse a CSV at runtime into `Translation.new()` objects (`locale`, `add_message`) and `TranslationServer.add_translation`. Keys show raw (e.g. `MYMOD_TITLE`) if the translation was never added.
- Reuse game fonts (`res://resources/fonts/actual/base/font_26.tres`) instead of shipping fonts.

## Dev loop A: shipped game + Workshop folder (most reliable)

Brotato's Steam build runs Mod Loader in Steam Workshop mode: it loads `*.zip` from `steamapps/workshop/content/1942280/<item_id>/`. Several authors report it ignores a local `mods/` folder; one reports `<game>/mods/` working. Check `logs/modloader.log` (`Checking workshop items, with path: ...`, `<zip> loaded.`) to see what your install does.

1. Upload a first build as a hidden/private Workshop item (below), subscribe to it.
2. Build, then overwrite the zip inside `steamapps/workshop/content/1942280/<item_id>/`. Keep exactly one zip there (old versions with the same mod folder load too).
3. Restart Brotato (mods load only at startup). Enable the mod in the in-game Mods menu if needed.
4. Read `%APPDATA%\Brotato\logs\godot.log` and `modloader.log` (macOS: `~/Library/Application Support/Brotato/logs/`). For more output set Steam launch options `--log-debug`.
5. Steam may restore the original zip on "Verify integrity" or when the item updates.

## Dev loop B: decompiled project in the Godot 3 editor

1. Decompile your own copy for reference: GDRE Tools (`gdre_tools`, MIT) -> *RE Tools > Recover project* on `<Brotato>/Brotato.pck`, or `gdre_tools --headless --recover=Brotato.pck`. It restores `project.godot`, scripts and source assets.
2. Open it with a Godot **3.x** editor close to the game's engine (the game runs a custom 3.7-dev build; mod authors use `Godot_v3.7-dev1` or 3.6). Never open it in Godot 4 - the converter rewrites the project.
3. Put your mod unpacked in `res://mods-unpacked/<ModId>/`. Do not put zips into `res://mods/` at the same time (loading a zip in the editor wipes unpacked mods).
4. In the editor, ML fatal errors `assert` and stop at the first manifest/deprecation problem - useful. Some platform/Steam code of the game may log errors without Steam; ignore those, not yours.
5. Final testing must happen in the shipped game: the editor is a debug build (extra checks such as override signature validation, `assert`, sort validation) while the shipped game is a release build.

## Dev loop C: automated runs

- Headless script runner against the decompiled project (used by mojimoon's mods): `Godot_v3.7-dev1 --no-window --audio-driver Dummy --path <project> -s res://mods/tests/run.gd`, with `APPDATA` pointed at a temp folder so saves and ML profiles are isolated. Fail the run on any `SCRIPT ERROR`/`Parse Error` or `ERROR:` line that mentions `mods-unpacked/<ModId>` and on `bad comparison function`.
- Running the real `Brotato.exe` with a locally patched copy of the pack (`--main-pack <copy.pck> --mods-path <dir> --audio-driver Dummy`, options.tres patched to non-Workshop mode, custom user dir) is what the Combat Tracker and FullMapCamera authors do. Keep such pack copies private and out of git.

## Workshop upload

Option 1 - GodotWorkshopUtility (ships in the game folder):
- Launch it through Steam: Brotato > Properties > Betas > `modding` branch, then start the game from Steam and pick the uploader; or run `GodotWorkshopUtility.exe` directly with `steam_appid.txt` containing `1942280` next to it. Without an app id the log shows `Steam could not initialize: ... No appID found` and uploads hang at `creating new workshop item...`.
- Select the zip and a preview image. Leave Workshop ID empty only for the first upload; afterwards paste the item id (from the item URL) or you create a duplicate item.
- It sets the Workshop title from the zip filename on every upload and has no description/changenote field: name the zip as the title you want and edit description, visibility and changenotes on the item page.
- Switch the beta branch back to none afterwards.

Option 2 - SteamCMD (`workshop_build_item` with a `.vdf`: `appid 1942280`, `publishedfileid` (0 = create), `contentfolder` that contains only the zip, `previewfile`, `title`, `description`, `changenote`) keeps title/description stable. Use absolute paths in the vdf.

Steam requirements: account with at least USD 5 spent, Workshop legal agreement accepted (items stay invisible otherwise), preview < 1 MB, description BBCode < 8000 bytes UTF-8. New items start hidden. A changenote is only recorded when the uploaded files changed.

## Updating after a game patch

1. Re-decompile the new `Brotato.pck` into a fresh folder and diff it against the previous one (only the scripts you extend or call).
2. For each override: compare signature and body; for each private member you read: confirm it still exists.
3. Update `compatible_game_version` (informational only; ML never blocks on it) and bump `version_number`.
4. Run a full loop: main menu -> character/weapon/difficulty -> wave -> level-up -> shop -> next wave -> end screen, solo and 2-player local.

## Legal

- Brotato's code and assets belong to Blobfish/Evil Empire. Decompile only for local reference; never commit decompiled scripts, ship vanilla files in a zip, or publish patched packs. The Mod Loader wiki asks the same ("including creating a public repo containing the code/assets").
- Copying small vanilla snippets into overrides is common practice in mods but is still redistribution of game code; prefer calling `.method()` and adding logic around it.
- Mod Loader is CC0; check the license of any mod you copy from (many Brotato mod repos have none, which means all rights reserved).
