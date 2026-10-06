# Brotato mod troubleshooting: message -> cause -> fix

First step every time: read `%APPDATA%\Brotato\logs\modloader.log` and `godot.log` (macOS `~/Library/Application Support/Brotato/logs/`) from the top. The first `FATAL-ERROR`/`ERROR`/`Parse Error` is the cause; later lines are follow-ups. Start with `--log-debug` in Steam launch options to see info lines. Versions: Brotato 1.1.15.4, Mod Loader 6.2.0/6.3.0, Godot 3.7-dev.

## Mod not loading

| Message / symptom | Cause | Fix |
|---|---|---|
| Mod missing in the Mods menu, nothing in `modloader.log` | Zip not where ML looks (Steam build = Workshop item folders), or Steam has not finished downloading | Put/keep the zip in `steamapps/workshop/content/1942280/<id>/`; check `Checking workshop items, with path:` lines |
| `The mod zip at path "X" does not have the correct file structure.` | Zip root is not `mods-unpacked/<ModId>/` | Re-zip from the folder that contains `mods-unpacked` |
| `X.zip failed to load.` | Corrupt/unsupported zip | Rebuild with Python `zipfile` or 7-Zip, deflate or store |
| `Dictionary is missing required fields: [...]` | Required manifest key missing | Add root keys `name, namespace, version_number, website_url, description, dependencies, extra` and `extra.godot` keys `authors, compatible_mod_loader_version, compatible_game_version` |
| `Error parsing JSON` | Trailing comma, comment, smart quotes in `manifest.json` | Validate the JSON |
| `Invalid name or namespace: "My-Mod". You may only use letters, numbers and underscores.` | Hyphen/space/dot in `name` or `namespace` | `[A-Za-z0-9_]{3,}` only; the hyphen is only the separator in the mod ID |
| `Invalid semantic version: "1.0" in field "version_number" ...` | Not `X.Y.Z` / leading zero | Use `1.0.0` |
| `"compatible_mod_loader_version" is a required field.` | Missing or empty | `["6.2.0", "6.3.0"]` |
| `Mod directory name "A" does not match the data in manifest.json. Expected "N-M" ...` | Folder name != `namespace-name` | Rename folder (case-sensitive) |
| Same message with `Expected "-"` | Manifest rejected earlier, fields empty | Fix the first fatal line |
| `ERROR - X is missing a required file: res://mods-unpacked/X/mod_main.gd` | Missing/renamed `mod_main.gd` or `manifest.json`, wrong case | Exact lowercase names in the mod root |
| `Missing dependency - mod: -> A dependency -> B` | B not installed/active or ID typo | Subscribe/enable B, or move it to `optional_dependencies` |
| `The mod "X" lists itself as "dependency" ...` / `lists the same mod(s) ... in "dependencies" and "incompatibilities"` | Manifest list errors | Clean up the lists |
| Mod listed but inactive | Disabled in the in-game Mods menu (`mod_user_profiles.json` `is_active: false`), or game started with `--disable-mods` | Enable it, restart |
| Game says "Unexpected error in mod X. Mods have been temporarily disabled." | Brotato found errors from a mod in the previous run's log and disabled mods | Fix the script error. Reported recovery: delete `%APPDATA%\Brotato\logs`, re-enable mods; outdated mods (pre-Oct-2024) trigger this repeatedly |
| Old version of your mod still runs | Two zips for the same mod in the Workshop folder, or Steam re-downloaded the published version | Keep one zip; log your version in `_ready`; unsubscribe/resubscribe to force a clean download |

## Script extension problems

| Message / symptom | Cause | Fix |
|---|---|---|
| `The child script path 'res://mods-unpacked/...' does not exist` | Path typo or wrong case (zip/pck paths are case-sensitive even on Windows) | Build paths from `ModLoaderMod.get_unpacked_dir().plus_file(MOD_ID)` |
| `Attempt to call function 'set_meta' in base 'null instance' on a null instance.` (in `addons/mod_loader/internal/script_extension.gd`) | Extension script failed to compile; `load()` returned null | Fix the `Parse Error` reported just before it |
| `Parse Error: Unexpected '@'` | Godot 4 annotation (`@export`, `@onready`, `@tool`) | `export var`, `onready var`, `tool` |
| `Parse Error: The identifier "await" isn't declared in the current scope.` / `Expected end of statement after expression...` | Godot 4 `await`, lambdas, `super` | `yield(obj, "signal")`, named methods, `.method()` |
| `Parse Error: Expected an identifier for the local variable name.` (or `...member variable name.`, `...for an argument.`) | Variable/argument named like a GDScript built-in (`range`, `min`, `max`, `sign`, `str`, `len`, `hash`, `load`, `print`, `char`, `ord`, `step_decimals`) | Rename |
| `Parse Error: Mixed tabs and spaces in indentation.` | Editor inserted spaces | Tabs only |
| `Parse Error: The function signature doesn't match the parent. Parent signature is: "void _on_X(int, Node)".` (editor/debug) | Override differs in arg count/types/defaults/return type | Copy the vanilla signature exactly. The release game skips this check, so mismatches surface later as wrong-arg-count errors |
| `Parse Error: Couldn't fully preload the script, possible cyclic reference or compilation error. Use "load()" instead...` | `preload` cycle between your scripts, or preloading a script with errors | `load()` at runtime; break the cycle |
| Extension never runs, no error | Installed after the target was instanced (autoload extended outside `mod_main._init()`), extending the wrong script (`shop.gd` vs `coop_shop.gd`), or another mod overrides the method without calling `.method()` | Install in `_init()`; check which script the node really uses (`node.get_script().resource_path` / `get_base_script()`); load after the other mod via `optional_dependencies` |
| Vanilla behaviour runs twice (duplicated players in `EntitySpawner`, doubled UI, double rewards) | Extension calls `._ready()`/`._process()`/`._input()` although Godot 3 already calls the parent's | Remove the parent call for engine callbacks |
| Your code after `.method()` sees stale state | Vanilla method `yield`s; `.method()` returned a `GDScriptFunctionState` | `var s = .method(); if s is GDScriptFunctionState: yield(s, "completed")` |
| `ERROR: Cannot load source code from file 'res://tests/partial_doubles/pd_player.gd'` | ML reloads every global subclass of an extended class (`Player`); a dev test class is not shipped | Harmless |
| Extension `_init()` side effects happen once at startup (6.2.0) | ML 6.2.0 instantiates each extension once when installing it | Keep extension `_init()` empty |
| Content of a DLC script extension crashes for players without the DLC | `res://dlcs/dlc_1/...` does not exist for them | Install DLC extensions inside a `ProgressData.check_for_available_dlcs()` override, guarded by `File.new().file_exists("res://dlcs/dlc_1/dlc_data.tres")` |

## Runtime errors (often after a game update)

| Message / symptom | Cause | Fix |
|---|---|---|
| `Invalid call to function 'clean_up_room' in base 'Node (main.gd)'. Expected 0 arguments.` (any method) | Vanilla signature changed in the patch | Re-decompile, update the override/call (example: `clean_up_room` lost its 3 bool args by 1.1.15.4) |
| `Invalid call. Nonexistent function 'x' in base 'Node (run_data.gd)'.` | Method removed/renamed, or called on the wrong object | Check the new source; guard optional calls with `has_method` |
| `Invalid get index 'gold' (on base: 'Node (run_data.gd)').` | 1.0-era field (`RunData.gold`, `RunData.effects`, string stat keys) or renamed private member | Use `RunData.get_player_gold(i)`, hashes, `players_data[i]` |
| Stat/effect change "does nothing" | String key instead of hash, or cached stat | `Keys.<x>_hash` / `Keys.generate_hash()`, then `Utils.reset_stat_cache(player_index)` |
| Only player 1 gets the effect | Hard-coded index 0 | Loop `for player_index in RunData.get_player_count()` |
| `Attempt to call function 'x' in base 'previously freed instance' on a null instance.` | Kept a reference to a freed/pooled node across waves | `is_instance_valid(node)` before use; clear references on wave end (`main._cleaning_up`) |
| `Resumed function 'f()' after yield, but class instance is gone.` | `yield` on a timer/signal and the node was freed (wave ended, scene changed) | Use a child `Timer` node or `connect(..., CONNECT_ONESHOT)` instead of yielding in nodes that can die |
| `Condition "!data.tree" is true. Returned: nullptr` then null-instance error | `get_tree()` called in `mod_main._init()` or on a node not yet in the tree | Move to `_ready()` / `call_deferred` |
| `Parent node is busy setting up children, add_node() failed. Consider using call_deferred("add_child", child) instead.` | Adding nodes inside another node's `_ready` chain | `parent.call_deferred("add_child", node)` |
| `Can't change this state while flushing queries. Use call_deferred() or set_deferred() to change monitoring state instead.` | Toggling collision/monitoring inside a physics callback | `set_deferred("monitoring", false)` / `call_deferred` |
| `Error calling method from signal 'x': 'Node(...)::_on_y': Method not found.` | `connect()` uses a method name that does not exist (string-based, unchecked) | Fix the name; keep handler names in one place |
| `Signal "x" from "A" is already connected to given method "y" in "B".` | Connecting again every wave/scene | `if not obj.is_connected("x", self, "y"): obj.connect(...)` |
| `bad comparison function; sorting will be broken` | `sort_custom` comparator is not a strict weak ordering (`<=`, random, inconsistent) | Return `a < b` strictly; the release game skips the check and can crash |
| Clicks on your overlay go to the game / never arrive in co-op | Godot 3 input picking by tree order; `FocusEmulator` consumes mouse in multiplayer | Keep your CanvasLayer last under `/root`, handle input in `_input`, `FOCUS_NONE` on overlay controls |
| `No loader found for resource: res://mods-unpacked/.../x.png` | Raw asset without `.import` data in the zip | Ship `.import` + `.stex`, or build textures from PNG bytes |
| Translations show raw keys | `.translation` not added, wrong locale, or CSV never compiled | `ModLoaderMod.add_translation(...)` with a compiled file, or runtime `Translation` objects |

## Tooling / Workshop

| Message / symptom | Cause | Fix |
|---|---|---|
| `Steam could not initialize: ... No appID found`, upload stuck at `creating new workshop item...` | `GodotWorkshopUtility.exe` started outside Steam | Start via the `modding` beta launch option, or add `steam_appid.txt` = `1942280` beside it |
| Every upload creates a new Workshop item | Workshop ID left blank | Paste the existing item id |
| Workshop title keeps changing | Uploader uses the zip filename as title | Name the zip like the title, or upload with SteamCMD |
| Uploader or game crashes after a mod used `register_global_classes_from_array` | `override.cfg` written into the game folder | Restart the game once; delete `override.cfg` before running other Godot tools |
| Item invisible to others | Hidden visibility or Workshop legal agreement not accepted / account < USD 5 spent | Fix on the item page / Steam account |
| Deprecation fatal in the editor (`DEPRECATED: The method "ModLoader.install_script_extension" has been deprecated since version 6.0.0...`) | Old API | Use `ModLoaderMod.*`, `ModLoaderLog.*`; the shipped game only warns |
