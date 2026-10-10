# Sources (accessed 2026-10-10)

Legend: **D** = read directly (cloned repository / source file); **S** = search-result snippet only; **N** = not verified / practice.
Blocked from this environment: `developer.blender.org` (release notes), `docs.blender.org`, `projects.blender.org`, `blender.org`, `extensions.blender.org`. Release-note facts therefore come from the Blender source itself (D) or from the vendored upstream skills that tested them (U in the other files).

## Blender source (D)

`github.com/blender/blender`, sparse/blobless clone. Branch heads used:

| Branch / tag | Commit | Date |
|---|---|---|
| `blender-v5.2-release` | `d13f752e3b9c` | 2026-09-14 |
| `blender-v5.3-release` | `dd3a1f3975b7` | 2026-10-10 |
| `blender-v5.1-release` | `ec6e62d40fa9` | 2026-05-18 |
| `blender-v5.0-release` | `9ab5c215851a` | 2026-04-27 |
| `blender-v4.5-release` | `62c1db4` | 2026-09-14 |
| `blender-v4.4-release` | `802179c` | 2025-04-29 |
| `blender-v4.2-release` | `d0cbe84` | 2026-07-20 |
| `blender-v4.1-release` | `2c29fd4` | 2024-04-22 |
| `blender-v4.0-release` | `0378823` | 2024-06-05 |
| `blender-v3.6-release` | `e467db7` | 2025-06-16 |
| tags `v2.80`, `v2.79b` | `f6cb5f54`, `f4dc9f9` | 2019 / 2018 |

Files read (5.2 unless a branch is named):
- `source/blender/python/intern/bpy_operator_function.cc` – "1-2 args execution context is supported", poll error format, "could not be found", "cannot modify blend data in this state", keyword conversion prefix.
- `scripts/modules/bpy/ops.py` on 3.6 ("1-3 args") and 4.0 ("1-2 args").
- `source/blender/python/intern/bpy_rna.cc` – "StructRNA of type %s has been removed", `bpy_prop_collection[key]: key "%s" not found`, enum "not found in", context property read-only, "Writing to ID classes in this context is not allowed", `register_class(...): already registered as a subclass`, keyword "unrecognized".
- `source/blender/python/intern/bpy_capi_utils.cc` + `blenkernel/intern/report.cc` – reports become `RuntimeError: Error: <msg>`.
- `source/blender/python/bmesh/bmesh_py_types.cc` – "outdated internal index table, run ensure_lookup_table() first".
- `source/blender/python/intern/bpy_rna_context.cc` – `temp_override`.
- `scripts/modules/_bpy_restrict_state.py` (5.0+; `bpy_restrict_state.py` on 4.5) – `_RestrictContext`, `_RestrictData`.
- `source/blender/makesrna/intern/rna_mesh.cc` / `rna_mesh.c` (3.6, 4.0, 4.1, 5.2) – `use_auto_smooth`, `bevel_weight`/`crease` edge properties, `corner_normals`, `normals_domain`.
- `rna_mesh_api.cc` / `.c` (3.6, 4.0, 4.1, 5.2) – `calc_normals`, `calc_normals_split`, `set_sharp_from_angle`, `validate`.
- `scripts/modules/_bpy_types.py` – `Mesh.shade_smooth()`, `shade_flat()`, `from_pydata()`.
- `rna_object.cc` / `.c` (3.6, 4.0) – `face_maps`; `rna_object_api.cc`/`.c` (v2.79b, v2.80, 5.2) – `select_set`, `hide_set`, `visible_get`, `to_mesh`, `to_mesh_clear`, "cannot be selected because it is not in View Layer".
- `rna_material.cc` (4.1, 4.2, 5.2, 5.3) – `surface_render_method` items `DITHERED`/`BLENDED`, `blend_method` deprecation text and setter mapping, `use_nodes` deprecated 500→600.
- `source/blender/nodes/shader/nodes/node_shader_bsdf_principled.cc` (4.2, 4.5, 5.2, 5.3) – socket names and defaults (`Emission Strength` 0.0, `Specular IOR Level` 0.5, `Thin Wall`, 5.3 dispersion inputs).
- `rna_node_tree_interface.cc` (3.6, 4.0, 5.2) – `new_socket`, `new_panel`, `items_tree`.
- `rna_modifier.cc` (4.4, 4.5, 5.0, 5.1, 5.2, 5.3) – Boolean solver ids, `NodesModifierProperties`.
- `source/blender/editors/object/object_modifier.cc` – modifier apply error reports.
- `source/blender/draw/engines/eevee_next/eevee_engine.cc` (4.2), `draw/engines/eevee/eevee_engine.cc` (4.5, 5.0, 5.2) – engine ids.
- `source/blender/python/generic/` listing (4.5 vs 5.0) – `bgl` removal; `source/blender/python/gpu/gpu_py_api.cc` (5.1 vs 5.2) – `gpu.init`.
- `source/blender/editors/io/` listing (4.5, 5.0, 5.2) – `io_fbx_ops.cc` (`WM_OT_fbx_import`), Collada removal; `io_obj.cc` – `export_selected_objects`.
- `scripts/addons_core/io_scene_fbx/__init__.py` (5.2, 5.3; add-on 5.15.0) – export option names, defaults and descriptions (`bake_space_transform` warning, `use_mesh_modifiers` shape-key warning, `add_leaf_bones` default True, `mesh_smooth_type` default `OFF`, `apply_scale_options` items, axis defaults `-Z`/`Y`).
- `scripts/addons_core/bl_pkg/cli/blender_ext.py`, `example_extension/blender_manifest.toml` – manifest keys, tagline 64-char rule, `build`/`validate` subcommands with current-directory defaults.
- `scripts/modules/bpy/utils/__init__.py` (v2.80, 5.2) – no `register_module` in 2.80; `extension_path_user`.
- `scripts/modules/addon_utils.py` – `bl_ext` package prefix.
- `source/creator/creator_args.cc` – `-b`, `-c/--command`, `--python-expr`, `--python-exit-code`, `--python-use-user-env` doc, `--factory-startup`, `--addons`.
- `source/blender/python/mathutils/mathutils_Matrix.c` (v2.80) – `@` operator, element-wise `*` error text.
- `build_files/build_environment/cmake/versions.cmake` (v2.80, 3.6, 4.0, 4.1, 4.2, 4.5, 5.0, 5.1, 5.2) – bundled Python.
- `doc/python_api/rst/info_gotchas_operators.rst`, `info_gotchas_internal_data_and_python_objects.rst`, `info_gotchas_meshes.rst` – poll failures, `view_layer.update()`, BMesh/mesh sync.

## Vendored skills used as secondary evidence (D, read in full)

- `scenario-labs/skills` @ `f6f8ab71aa1f` – `scenario-blender-expert/references/blender-5.2-deltas.md` and `bpy-reliability.md` (empirical probes on Blender 5.2.1, 2026-09-24: operator vs data API timings, `foreach_get` timings, headless limits, GN modifier `TypeError`, `--python-use-user-env`).
- `luckyfried/code-tools` @ `c46388134a16` – `blender-current-api/references/removed-apis.md` (old→new table keyed to release notes), `blender-game-export` (FBX/glTF practice), `blender-verify` (official MCP tool names, `result` variable).
- `majidmanzarpour/blender-game-skills` @ `f0ef29385a03` – `references/blender-5-notes.md` (node names translated in non-English UIs; GN input change).

## Release dates (S)

- https://www.blender.org/download/releases/ (via search snippet): 5.1 released 17 Mar 2026, 5.2 LTS 14 Jul 2026.
- 5.3 schedule: no source found; only the existence of branch `blender-v5.3-release` (D).

## Not verified (N)

- UE 5.8 import options *Convert Scene*, *Convert Scene Unit*, *Import Normals* and the UE "no smoothing groups" warning (practice; UE docs not fetched here).
- `FBX_SCALE_ALL` as the best choice for UE: option exists (D), recommendation is practice – check with a 1 m cube.
- Exact wording of Python's own `AttributeError: 'X' object has no attribute 'y'` / `ModuleNotFoundError` lines (standard CPython formats).
