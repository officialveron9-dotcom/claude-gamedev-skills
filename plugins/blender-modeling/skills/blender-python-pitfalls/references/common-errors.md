# bpy error message → cause → fix

Message formats marked **D** were read in the Blender 5.2 source (`bpy_operator_function.cc`, `bpy_rna.cc`, `rna_object_api.cc`, `object_modifier.cc`, `bpy_capi_utils.cc`, `_bpy_restrict_state.py`) or are plain Python errors; **U** = reported by a vendored upstream skill on 5.2.1; **N** = practice. `X`, `Cube` etc. are placeholders. Operator error reports always arrive as `RuntimeError: Error: <message>` (D).

Add new rows at the bottom of the matching table when a bug is solved: exact message, cause, fix, Blender version.

## Operators and context

| Exact message | Cause | Fix | Version |
|---|---|---|---|
| `ValueError: 1-2 args execution context is supported` | Context dict passed positionally: `bpy.ops.x.y({"object": ob}, ...)` | `with bpy.context.temp_override(object=ob, ...): bpy.ops.x.y(...)` | 4.0+ (D) |
| `RuntimeError: Operator bpy.ops.object.mode_set.poll() failed, context is incorrect` | No/hidden/unselectable active object, wrong mode, or missing area (headless) | Link object to a view-layer collection, `view_layer.objects.active = ob`, `ob.select_set(True)`, unhide; or do it through the data API | all (D) |
| `RuntimeError: Operator bpy.ops.view3d.<op>.poll() failed, context is incorrect` in `blender -b` | No 3D View area in background mode | Data API equivalent, or run in a GUI/MCP session; `temp_override(area=..., region=...)` only works when such an area exists | all (D/U) |
| `RuntimeError: Operator bpy.ops.object.vertex_group_add.poll() No active editable object` (any `poll() <text>`) | Operator set its own poll message | Read the text; fix that condition | 3.x+ (D) |
| `AttributeError: Calling operator "bpy.ops.import_scene.obj" error, could not be found` | Operator removed/renamed or its add-on disabled | 4.0+: `bpy.ops.wm.obj_import`; add-on ops: enable the add-on first | 4.0+ (D) |
| `TypeError: Converting py args to operator properties:: keyword "export_textures" unrecognized` (double colon is real) | Keyword renamed/removed in this version | `print(bpy.ops.wm.usd_export.get_rna_type().properties.keys())`; e.g. USD `export_textures` → `export_textures_mode` (5.0, U) | all (D) |
| `RuntimeError: Calling operator "bpy.ops.X" error, cannot modify blend data in this state (drawing/rendering)` | Operator called from `draw()`, a render handler or other restricted state | Move the call to an operator `execute()` or a `bpy.app.timers` callback (GUI) | all (D) |
| `AttributeError: Writing to ID classes in this context is not allowed: Cube, Object data-block, error setting Object.location` | Writing data inside `Panel.draw()` / restricted context | Draw code must only read; write in an operator | all (D) |
| `AttributeError: bpy_struct: Context property "active_object" is read-only` | `bpy.context.active_object = ob` | `bpy.context.view_layer.objects.active = ob` | 2.80+ (D) |
| `RuntimeError: Error: Object 'Cube' cannot be selected because it is not in View Layer 'ViewLayer'!` | Object not linked to any collection of the active view layer (or collection excluded) | `bpy.context.collection.objects.link(ob)` / un-exclude the layer collection, then `select_set` | 2.80+ (D) |
| `AttributeError: 'Object' object has no attribute 'select'` | 2.7x API | `ob.select_set(True)` / `ob.select_get()` | 2.80+ (D) |
| `TypeError: Element-wise multiplication: not supported between 'Matrix' and 'Vector' types` (Matrix × Matrix silently multiplies element-wise) | 2.7x `*` matrix multiply | `@` | 2.80+ (D) |

## Modifiers, meshes, evaluation

| Exact message | Cause | Fix | Version |
|---|---|---|---|
| `RuntimeError: Error: Modifier cannot be applied to a mesh with shape keys` | Applying a constructive modifier on a mesh with shape keys | Apply shape keys first, or `new_from_object(evaluated)` route, or an add-on that applies per shape key | all (D) |
| `RuntimeError: Error: Modifiers cannot be applied to multi-user data` | Linked duplicates share the mesh | `ob.data = ob.data.copy()` first | all (D) |
| `RuntimeError: Error: Modifiers cannot be applied in edit mode` | Object in Edit Mode | `bpy.ops.object.mode_set(mode='OBJECT')` | all (D) |
| `RuntimeError: Error: Modifier is disabled, skipping apply` | Modifier off in viewport or invalid (e.g. Boolean without operand) | Enable it / set its target | all (D) |
| Info: `Applied modifier was not first, result may not be as expected` | Applying a modifier that is not at the top of the stack | Apply from the top, or accept | all (D) |
| `AttributeError: 'Mesh' object has no attribute 'use_auto_smooth'` | Auto Smooth removed | `mesh.shade_smooth(); mesh.set_sharp_from_angle(angle=math.radians(30))` or `bpy.ops.object.shade_auto_smooth()` | 4.1+ (D) |
| `AttributeError: 'Mesh' object has no attribute 'calc_normals'` | Removed (normals are lazy) | Delete the call | 4.0+ (D) |
| `AttributeError: 'Mesh' object has no attribute 'calc_normals_split'` | Split normals API removed | Read `mesh.corner_normals` | 4.1+ (D) |
| `AttributeError: 'Object' object has no attribute 'face_maps'` | Face maps removed | Integer face attribute (`mesh.attributes.new("fmap", 'INT', 'FACE')`) | 4.0+ (D) |
| `IndexError: BMElemSeq[index]: outdated internal index table, run ensure_lookup_table() first` | Indexing BMesh sequence after creation/change | `bm.verts.ensure_lookup_table()` (also `edges`, `faces`) | all (D) |
| `ReferenceError: StructRNA of type Object has been removed` | Python kept a reference across undo, removal, mode switch or array reallocation | Store names, re-fetch from `bpy.data` | all (D) |
| Vertex counts/bounds ignore modifiers | Reading `ob.data` instead of evaluated mesh | `ob.evaluated_get(depsgraph).to_mesh()` … `to_mesh_clear()` | 2.80+ (N) |
| `matrix_world` still old after setting `location` | Depsgraph not updated | `bpy.context.view_layer.update()` | 2.80+ (U, gotchas doc D) |
| `RuntimeError` from `foreach_set` (size) / `TypeError` (dtype) | Wrong array length or float64 vs float32 | `np.empty(n*3, np.float32)` sized to the data | 4.1+ type check (U) |

## Materials, nodes, rendering

| Exact message | Cause | Fix | Version |
|---|---|---|---|
| `KeyError: 'bpy_prop_collection[key]: key "Specular" not found'` | Principled v1 socket name | `"Specular IOR Level"` (also `Subsurface Weight`, `Transmission Weight`, `Coat Weight`, `Sheen Weight`, `Emission Color`) | 4.0+ (D) |
| `KeyError: 'bpy_prop_collection[key]: key "Principled BSDF" not found'` | Node renamed, or created with a translated UI (*Translate New Data Names*) | Find by type: `n.bl_idname == "ShaderNodeBsdfPrincipled"` | all (D format, cause U) |
| Emission set but object does not glow | `Emission Strength` default is 0.0 | Set strength > 0 | 4.0+ (D) |
| `AttributeError: 'GeometryNodeTree' object has no attribute 'inputs'` (or `'NodeTree' …`) | Pre-4.0 group socket API | `tree.interface.new_socket(...)` | 4.0+ (D) |
| `TypeError` when setting `mod["Socket_2"] = …` on a Geometry Nodes modifier | 5.2 moved GN inputs to RNA | `getattr(mod.properties.inputs, ident).value = …` | 5.2+ (D struct, U error) |
| `TypeError: bpy_struct: item.attr = val: enum "BLENDER_EEVEE_NEXT" not found in ('BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'CYCLES')` | 4.2–4.5 engine id used on 5.x (or vice versa) | `'BLENDER_EEVEE' if bpy.app.version >= (5, 0, 0) else 'BLENDER_EEVEE_NEXT'` (4.2+) | 5.0+ (D) |
| `ModuleNotFoundError: No module named 'bgl'` | `bgl` removed | `gpu` module | 5.0+ (D) |
| `AttributeError: 'Scene' object has no attribute 'node_tree'` (compositor) | Compositor tree is a node group | `scene.compositing_node_group` | 5.0+ (U) |
| `AttributeError: 'Action' object has no attribute 'fcurves'` | Legacy action API removed | channelbag via `bpy_extras.anim_utils` | 5.0+ (U) |
| Texture maps look washed out / normal map wrong | Data image left in sRGB | `img.colorspace_settings.name = "Non-Color"` | all (N) |
| Alpha-clip material (fences, foliage, decals) renders soft/noisy instead of a hard cut | `blend_method = 'CLIP'` now maps to `surface_render_method = 'DITHERED'`; EEVEE Next has no clip mode | Threshold in the shader (Math *Greater Than* 0.5 on alpha → Alpha), set `surface_render_method` directly | 4.2+ (D mapping in `rna_Material_blend_method_set`, fix U) |

## Add-ons, extensions, headless

| Exact message | Cause | Fix | Version |
|---|---|---|---|
| `AttributeError: '_RestrictContext' object has no attribute 'scene'` | Accessing `bpy.context.scene` in `register()` / at import | Defer to operator/handler/timer | all (D) |
| `AttributeError: '_RestrictData' object has no attribute 'objects'` | Accessing `bpy.data` in `register()` | Same | all (D) |
| `ValueError: register_class(...): already registered as a subclass 'MY_OT_op'` | Script re-run without `unregister()` | Unregister first, or guard `if hasattr(bpy.types, "MY_OT_op")` | all (D) |
| `ModuleNotFoundError: No module named 'my_addon'` inside an extension | Absolute import of the own package | Relative imports `from . import x`; package is `bl_ext.<repo>.<id>` | 4.2+ (N) |
| Manifest validation error on `tagline` | Longer than 64 chars or ends with punctuation | Shorten, drop the final period | 4.2+ (D) |
| `ModuleNotFoundError` for a pip package that worked before | 5.1+ no longer loads user site-packages | `--python-use-user-env`, or ship wheels in the extension | 5.1+ (D/U) |
| Script failed but exit code 0 | `--python-exit-code` missing | `blender -b ... --python-exit-code 1 -P script.py` | all (U) |
| Render settings from the CLI ignored | `-o`/`-F`/`-E` placed after `-f`/`-a` | Put them before the render action | all (U) |
| Saved `.blend` lacks the new mesh/collection | Data-block had 0 users | Link it (`collection.objects.link`, `children.link`) or `use_fake_user = True` | all (U) |
| `TypeError: Converting py args to operator properties:: keyword "use_selection" unrecognized` on `wm.obj_export` | Different option names than the old Python exporter | `export_selected_objects=True` (C++ OBJ exporter) – check with `get_rna_type()` | 4.0+ (D format; name N) |

## Export

| Symptom | Cause | Fix | Version |
|---|---|---|---|
| Mesh 100× too big/small in UE | Unit scale / unapplied scale / UE unit conversion off | `scale_length = 1.0`, `transform_apply(scale=True)`, `apply_unit_scale=True` + `apply_scale_options='FBX_SCALE_ALL'`, UE *Convert Scene Unit*; test with a 1 m cube | all (N; option names D) |
| Rig rotated 90° or extra root bone in UE | Armature object transform / axis | Apply rotation on armature + meshes, keep FBX axes default (`-Z`, `Y`), check UE skeleton root | all (N) |
| Extra `_end` bones | `add_leaf_bones=True` is the default | `add_leaf_bones=False` | all (D default) |
| Shape keys missing in FBX | `use_mesh_modifiers=True` (add-on warns it prevents shape keys) | Apply modifiers yourself first, export with `use_mesh_modifiers=False` | all (D warning) |
| Hard edges smooth in UE | Smooth by Angle modifier not applied / normals recalculated in UE | Export with modifiers applied or `shade_smooth_by_angle`; UE *Import Normals* | 4.1+ (U) |
| Armature animation broken with `bake_space_transform=True` | Option marked experimental, broken with armatures | Leave `False` | all (D description) |
