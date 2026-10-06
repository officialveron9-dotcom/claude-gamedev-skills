# Sources (accessed 2026-10-06)

Legend: **[src]** = read directly (cloned repo or raw file from GitHub), **[snippet]** = seen only in search-result snippets, **[knowledge]** = well-established Godot 3/4 API facts not re-checked line by line in this session.

| Source | Backs up |
|---|---|
| https://github.com/godotengine/godot/tree/3.x `version.py` **[src]** | 3.x branch = "3.7 dev" (Brotato's engine is a custom build of this line) |
| `modules/gdscript/gdscript_tokenizer.cpp` (3.x) **[src]** | Keyword list (`onready`, `tool`, `export`, `setget`, `yield`, `remote`, `master`, `puppet`, ...; no `await`/`super`); `Unexpected '@'`; built-in function names always tokenized as functions (so `var range` fails) |
| `modules/gdscript/gdscript_functions.cpp` (3.x) **[src]** | Full list of built-in functions (`rand_range`, `stepify`, `deg2rad`, `str2var`, `deep_equal`, `is_instance_valid`, no `is_finite`) |
| `modules/gdscript/gdscript_parser.cpp` (3.x) **[src]** | Exact parse errors: `Expected an identifier for the local variable name.`, `Mixed tabs and spaces in indentation.`, `The function signature doesn't match the parent. Parent signature is: ...` (inside `DEBUG_ENABLED`), `The assigned value doesn't have a set type...`, `Couldn't fully preload the script, possible cyclic reference...`, `The identifier "x" isn't declared in the current scope.` |
| `modules/gdscript/gdscript.cpp` (3.x) **[src]** | `Parse Error:` / `Compile Error:` prefixes; `call_multilevel` / `call_multilevel_reversed` implementation; `notification` on all levels |
| `modules/gdscript/gdscript_function.cpp` (3.x) **[src]** | Runtime errors (`previously freed instance`, `Invalid call. Nonexistent ...`, `Invalid get index ...`, yield errors, `Resumed function ... after yield, but class instance is gone.`) |
| `scene/main/node.cpp`, `node.h`, `scene_tree.cpp`, `viewport.cpp`, `scene/2d/canvas_item.cpp` (3.x) **[src]** | Which callbacks are multilevel and in which order; input dispatch order; `create_timer(time_sec, pause_mode_process = true)`; `create_tween`; `get_tree()` error; `add_child`/busy-parent messages |
| `main/main.cpp` (3.x) **[src]** | Autoloads instanced first, then added to root in order |
| `core/object.cpp`, `core/object.h` (3.x) **[src]** | `connect(signal, target, method, binds, flags)`; connection error messages; `CONNECT_ONESHOT`; `PROPERTY_USAGE_SCRIPT_VARIABLE = 8192` |
| `core/array.cpp`, `core/dictionary.cpp`, `core/variant_op.cpp` (3.x) **[src]** | `Array.slice` inclusive end; Array `==` element-wise, Dictionary `==` by reference |
| `core/sort_array.h` (3.x) **[src]** | `bad comparison function; sorting will be broken`, validation only with `DEBUG_ENABLED` |
| `servers/physics_2d/*.cpp` (3.x) **[src]** | `Can't change this state while flushing queries...`, `Space state is inaccessible right now...` |
| `doc/classes/ProjectSettings.xml`, `PackedScene.xml`, `KinematicBody2D.xml` (3.x) **[src]** | `load_resource_pack(pack, replace_files = true, offset = 0)`, `instance()`, `move_and_slide(linear_velocity, ...)` returns `Vector2` |
| https://github.com/GodotModding/godot-mod-loader wiki history, page Script-Extensions **[src, git history]** | "You can't override virtual functions in a script extension"; `_ready` order; don't call `._ready()` |
| https://github.com/xx666zz/BrotatoOnline `extensions/main_safe_pool_exit.gd` **[src]** | Real-world bug: `._ready()` in an extension ran `Main._ready()` twice |
| https://github.com/MattieTK/brotato-extended-coop-8 `extensions/singletons/coop_service.gd` **[src]** | `_input` runs in addition to vanilla (multilevel) |
| https://github.com/hhoangg/brotato-synergies `CONTRIBUTING.md` **[src]** | Tabs only; built-in names as identifiers; `:=` inference failures in 3.x |
| https://github.com/mojimoon/BrotatoMods `tests/*/run_tests.sh` **[src]** | Release build crashes on bad comparators; headless test runner flags |
| https://github.com/DPS-Love/brotato-combat-tracker `docs/DEVELOPMENT.md` **[src]** | Godot 3 GUI picking by tree order, `_input` reverse order, FocusEmulator, `FOCUS_NONE` overlays |
| Godot 4 names in the rename table **[knowledge]** | Godot 4.x API (`@export`, `await`, `super`, `CharacterBody2D`, `Packed*Array`, `FileAccess`, `instantiate`, `process_mode`, `queue_redraw`, theme override renames, `ResourceSaver.save(res, path)`) |
