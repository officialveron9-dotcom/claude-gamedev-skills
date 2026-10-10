# bpy API changes by version (2.80 → 5.3)

Legend: **D** = checked in the Blender source on the named release branch(es) of `github.com/blender/blender` (sparse clone, 2026-10-10); **U** = stated by a vendored upstream skill that tested it on 5.2.1 (`scenario-blender-expert`, `blender-current-api`) but not re-read here; **N** = practice, not verified. Release notes on `developer.blender.org` were unreachable from this environment.

How a "D" removal was checked: the identifier is present on the last branch before the change and absent on the first branch after it (e.g. `"use_auto_smooth"` in `rna_mesh.cc`: 4.0 yes, 4.1 no).

## Version and Python matrix

| Blender | Released | Python (D: `versions.cmake`) | Notes |
|---|---|---|---|
| 2.80 | 2019 | 3.7 | new selection/collections API |
| 3.6 LTS | 2023 | 3.10 | last with context dicts |
| 4.0 | Nov 2023 | 3.10 | Principled v2, interface API |
| 4.1 | Mar 2024 | 3.11 | Auto Smooth removed |
| 4.2 LTS | Jul 2024 | 3.11 | EEVEE Next, extensions |
| 4.5 LTS | 2025 | 3.11 (D: 3.11.15) | last with `bgl` |
| 5.0 | Nov 2025 | 3.11 (D: 3.11.13) | big cleanup release |
| 5.1 | 17 Mar 2026 | 3.13 (D: 3.13.9) | user site-packages off |
| 5.2 LTS | 14 Jul 2026 | 3.13 (D: 3.13.13) | GN modifier `properties` |
| 5.3 | branch `blender-v5.3-release` exists (beta, 2026-10-10) | – | treat as preview |

Release dates for 5.1/5.2 from blender.org via search snippets; older dates N.

## 2.80 (2019) – the "2.7x tutorial" break

| Old (2.7x) | New | Check |
|---|---|---|
| `ob.select = True`, `ob.select` | `ob.select_set(True)`, `ob.select_get()` | D (`rna_object_api.c` v2.79b vs v2.80) |
| `scene.objects.active = ob` | `view_layer.objects.active = ob` | N (well known) |
| `scene.objects.link(ob)` | `collection.objects.link(ob)` | N |
| `ob.hide = True` | `ob.hide_set(True)` (view layer) / `ob.hide_viewport` (global) | N |
| `scene.update()` | `view_layer.update()` | N |
| `matrix * vector` | `matrix @ vector` (`*` is element-wise) | D (`mathutils_Matrix.c` v2.80) |
| `bpy.utils.register_module(__name__)` | `bpy.utils.register_class(cls)` per class | D (`bpy/utils/__init__.py` v2.80 has no `register_module`) |
| `prop = bpy.props.FloatProperty()` in classes | annotation `prop: bpy.props.FloatProperty()` | N |
| Class names `MyOperator` | `CATEGORY_OT_name`, `CATEGORY_PT_name` | N |

## 3.x

| Change | Version | Check |
|---|---|---|
| `bpy.context.temp_override(**members)` added | 3.2 | U (3.2 release notes, quoted by upstream) |
| Context dict still accepted, deprecated warnings | 3.2–3.6 | D (3.6 `ops.py`: "1-3 args execution context") |
| Vertex colors → color attributes (`mesh.color_attributes`) | 3.2 | U |
| Curves hair object | 3.3 | U |

## 4.0 (Nov 2023)

| Old | New | Check |
|---|---|---|
| `bpy.ops.x.y(context_dict, ...)` | `with bpy.context.temp_override(...)` | D (`ops.py` 4.0: "1-2 args execution context is supported") |
| `mesh.calc_normals()` | none needed | D (`rna_mesh_api` 3.6 yes, 4.0 no) |
| `ob.face_maps` | integer face attribute | D (`rna_object` 3.6 yes, 4.0 no) |
| `edge.bevel_weight`, `edge.crease` | `bevel_weight_edge`, `crease_edge` attributes | D removal (`rna_mesh` 3.6 yes, 4.0 no); attribute names U |
| `tree.inputs.new()` / `outputs.new()` on node groups | `tree.interface.new_socket(name, in_out, socket_type)` | D (`rna_node_tree_interface.cc` 4.0 yes, 3.6 no) |
| Principled `Specular`, `Subsurface`, `Transmission`, `Coat`/`Clearcoat`, `Sheen`, `Emission` | `Specular IOR Level`, `Subsurface Weight`, `Transmission Weight`, `Coat Weight`, `Sheen Weight`, `Emission Color` | D (5.2 socket list); 4.0 timing U |
| `Emission Strength` default | 0.0 (emission off until set) | D (5.2 default) |
| `bone.layers`, `pose.bone_groups` | bone collections, bone colors | U |
| `import_scene.obj` / `export_scene.obj`, Python PLY | `wm.obj_import/export`, `wm.ply_import/export` | U |
| `BVHTree.FromObject` with unevaluated depsgraph | pass the evaluated depsgraph | U |
| Default view transform Filmic | AgX | U |
| `bgl` | deprecated (removed 5.0) | D (removal) |

## 4.1 (Mar 2024)

| Old | New | Check |
|---|---|---|
| `mesh.use_auto_smooth`, `auto_smooth_angle` | `mesh.shade_smooth()` + `mesh.set_sharp_from_angle(angle=)`, or `object.shade_auto_smooth` (Smooth by Angle modifier) | D (`rna_mesh.cc` 4.0 yes, 4.1 no; `set_sharp_from_angle` in 5.2) |
| `calc_normals_split()`, `loop.normal` | `mesh.corner_normals`, `normals_domain` | D (4.0 yes / 4.1 no; `corner_normals` 4.1+) |
| Light probe `CUBEMAP/PLANAR/GRID` | `SPHERE/PLANE/VOLUME` | U |
| `mat.cycles.displacement_method` | `mat.displacement_method` | U |
| `foreach_set` wrong type silently accepted | raises `TypeError` | U |

## 4.2 LTS (Jul 2024)

| Old | New | Check |
|---|---|---|
| Engine `'BLENDER_EEVEE'` | `'BLENDER_EEVEE_NEXT'` | D (`eevee_next/eevee_engine.cc` 4.2) |
| `mat.blend_method`, `shadow_method` | `mat.surface_render_method` (`'DITHERED'`, `'BLENDED'`); `blend_method` kept but marked deprecated | D (description "Deprecated: use 'surface_render_method'" 4.2; property exists already in 4.1) |
| `bl_info` add-ons | extensions with `blender_manifest.toml` (legacy add-ons still load) | D (`bl_pkg` manifest keys) |
| Most bundled add-ons (LoopTools, Bool Tool, Extra Objects …) | extensions.blender.org | U |
| `scene.eevee.use_motion_blur` etc. | `scene.render.use_motion_blur` | U |
| IDProperties of `bpy.props`/GN inputs | statically typed | U |

## 4.3 – 4.5

| Change | Version | Check |
|---|---|---|
| `AttributeGroup` split per type (`AttributeGroupMesh` …) | 4.3 | U |
| Grease Pencil v3 rewrite; brushes are assets | 4.3 | U |
| Subclass `__init__` must call `super().__init__(*args, **kwargs)` | 4.4 | U |
| Slotted Actions; `bpy.types.Sequence` → `Strip` | 4.4 | U |
| `'BLENDER_EEVEE_NEXT'` still the id | 4.5 | D |
| Boolean solver `'MANIFOLD'` | 4.5 | D (`rna_modifier.cc` 4.4 no, 4.5 yes) |
| `gpu.types.GPUShader()` deprecated | 4.5 | U |
| C++ FBX importer `bpy.ops.wm.fbx_import` exists (Python `import_scene.fbx` still there in 5.2) | 4.5 | D (`io_fbx_ops.cc` 4.5, 5.0, 5.2) |

## 5.0 (Nov 2025)

| Old | New | Check |
|---|---|---|
| `import bgl` | `gpu` module | D (`python/generic/bgl*` 4.5 present, 5.0 absent) |
| `'BLENDER_EEVEE_NEXT'` | `'BLENDER_EEVEE'` | D (5.0 and 5.2 engine id) |
| `mat.use_nodes = True` | always True, setting has no effect (removal planned 6.0) | D (`RNA_def_property_deprecated(..., 500, 600)` in 5.2/5.3) |
| `scene.node_tree` (compositor) | `scene.compositing_node_group` | U |
| `action.fcurves`, `action.groups` | channelbags (`bpy_extras.anim_utils.action_ensure_channelbag_for_slot`) | U |
| `scene["cycles"]`, `ob["my_prop"]` for `bpy.props` | attribute access only | U |
| Boolean `'FAST'` | `'FLOAT'` | D (4.5 `FAST`, 5.0 `FLOAT`) |
| `image_settings.file_format` alone | set `media_type` first | U |
| Collada (`.dae`) import/export | removed | D (`editors/io` collada files 4.5 yes, 5.0 no) |
| `brush.sculpt_tool` | `brush.sculpt_brush_type` | U |
| `bpy_restrict_state` etc. as public modules | private (`_bpy_restrict_state`) | D (5.2 module name) |
| `temp_override(...).logging_set(True)` | new debugging aid | U |

## 5.1 (Mar 2026)

| Change | Check |
|---|---|
| Python 3.13 | D |
| User site-packages not loaded; `--python-use-user-env` restores | D (CLI doc in `creator_args.cc` 5.2) + U |
| `brush.stroke_method` enum replaces `use_airbrush`/`use_space`/… | U |
| VSE strip time props renamed (old names deprecated) | U |

## 5.2 LTS (Jul 2026)

| Change | Check |
|---|---|
| GN modifier inputs via `mod.properties.inputs.<identifier>.value` (`NodesModifierProperties`); `mod["Socket_2"]` fails | D (struct absent in 5.1, present in 5.2/5.3) + U (error) |
| `gpu.init()` for GPU drawing in `--background` | D (`gpu_py_api.cc` 5.1 no, 5.2 yes) |
| Principled BSDF `Thin Wall` input | D |
| Sculpt automasking moved into `mesh_automasking_settings` | U |
| LoopTools Circle/Flatten/Space built in (`mesh.circularize`, `mesh.flatten`, `mesh.space_edge_loops_evenly`) | U |
| FBX add-on 5.15.0 (`bl_info` blender 5.0) | D |

## 5.3 (beta branch, 2026-10-10)

| Change | Check |
|---|---|
| Principled gains `Transmission Dispersion Scale`, `Transmission Dispersion Abbe Number` | D (`node_shader_bsdf_principled.cc` on `blender-v5.3-release`) |
| `blend_method` and deprecated `use_nodes` still present; FBX add-on still 5.15.0 | D |

Re-check this section when 5.3 is released.
