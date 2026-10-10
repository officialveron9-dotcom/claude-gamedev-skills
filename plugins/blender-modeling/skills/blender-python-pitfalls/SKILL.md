---
name: blender-python-pitfalls
description: "Blender Python (bpy) mistakes Claude makes from outdated memory, with wrong-vs-right code checked against the Blender 5.2 source, for scripts run headless or through a Blender MCP server. Covers version detection, temp_override vs removed context dicts, operator poll failures, selection and active object since 2.80, data API and BMesh vs bpy.ops speed, evaluated meshes and modifier apply, Auto Smooth/calc_normals/face maps removal, Principled BSDF socket renames, surface_render_method, node group interface, GN modifier inputs (5.2), bgl removal, EEVEE engine ids, FBX units and axes for Unreal, blender -b arguments, add-on vs extension (blender_manifest.toml). Use when writing, fixing or porting any bpy script or add-on, or when a bpy error message appears. German triggers Blender Script, bpy Fehler, Blender automatisieren, Blender Python, Skript laeuft nicht, Addon geht nicht mehr."
---

# Blender Python pitfalls (2.80 → 5.3)

Scope: generic bpy correctness. The owner drives Blender from Claude (MCP or `blender -b`) for GTA V/FiveM MLOs, texture work and UE 5.8 clothing. Sollumz/MLO/GTA texture specifics belong to `fivem-mlo-creation`, `fivem-mlo-doors-windows`, `gta-texture-editing`; garment fitting to `clothing-creation-pipeline`. Deeper vendored references in this plugin: `blender-current-api` (full old→new table), `scenario-blender-expert` (bpy reliability, 5.2 deltas), `blender-game-export`, `blender-verify`.

Facts marked **[src 5.2]** were read in `blender/blender` branch `blender-v5.2-release` (d13f752); older/newer labels were checked on the matching release branch. Details: [references/api-changes.md](references/api-changes.md), error table: [references/common-errors.md](references/common-errors.md), provenance: [references/sources.md](references/sources.md).

## 0. Before writing any bpy

1. Get the version, do not assume it: `bpy.app.version` → e.g. `(5, 2, 1)`. Current lines (2026-10): **5.2 LTS** (Jul 2026), 4.5 LTS, 4.2 LTS; 5.3 is on its release branch (beta). Python 3.11 up to 5.0, **3.13 from 5.1**.
2. Unsure if a name exists? Ask Blender, not memory: `"prop" in bpy.types.Mesh.bl_rna.properties`, `dir(bpy.ops.mesh)`, `[s.name for s in node.inputs]`. `hasattr(bpy.types.X, "prop")` is False for RNA properties (only functions) – test on an instance.
3. Prefer the data API (`bpy.data`, `mesh.attributes`, `node_tree.nodes/links`). Use `bpy.ops` only where no data API exists, and then with an explicit context.

## 1. Context overrides and operators

```python
# WRONG (3.x style) – 4.0+: ValueError: 1-2 args execution context is supported
bpy.ops.object.modifier_apply({"object": ob}, modifier="Bevel")

# RIGHT (3.2+, required 4.0+)
with bpy.context.temp_override(object=ob, active_object=ob,
                               selected_objects=[ob], selected_editable_objects=[ob]) as ov:
    # ov.logging_set(True)   # 5.0+: logs which context members the operator reads
    bpy.ops.object.modifier_apply(modifier="Bevel")
```

- Positional args left for operators: only the execution context string (`'EXEC_DEFAULT'`, `'INVOKE_DEFAULT'`) and the undo bool **[src 5.2, 4.0; 3.6 accepted 1-3 args]**.
- `RuntimeError: Operator bpy.ops.X.poll() failed, context is incorrect` (or `poll() <custom message>`) means mode, selection, active object or editor area is wrong. Check `bpy.ops.mesh.subdivide.poll()` first.
- Headless (`-b`) there is a window but **no 3D View area**: `view3d.*`, `uv.*` ops that need the UV editor, screenshots, modal operators and `bpy.app.timers` do not work. Use the data API or a GUI/MCP session.
- Operators return `{'FINISHED'}` / `{'CANCELLED'}`, never data. `uv.unwrap` and `object.bake` can report FINISHED/CANCELLED without raising – check the result data.
- Operator `RPT_ERROR` reports become `RuntimeError: Error: <message>` **[src 5.2]**.

## 2. Selection, active object, visibility (2.80+)

```python
# WRONG (2.7x)                       # RIGHT (2.80+)
ob.select = True                      ob.select_set(True)
bpy.context.scene.objects.active = ob bpy.context.view_layer.objects.active = ob
bpy.context.active_object = ob        # AttributeError: ... Context property "active_object" is read-only
scene.objects.link(ob)                bpy.context.collection.objects.link(ob)   # or a named collection
scene.update()                        bpy.context.view_layer.update()
ob.matrix_world * v                   ob.matrix_world @ v   # 2.80+: '*' is element-wise or TypeError
bpy.utils.register_module(__name__)   for c in classes: bpy.utils.register_class(c)
```

- An object must be linked into a collection of the active view layer before `select_set`/`hide_set`: otherwise `RuntimeError: Error: Object 'X' cannot be selected because it is not in View Layer 'ViewLayer'!` **[src 5.2]**.
- Visibility has three levels: `collection.hide_viewport` (global), `layer_collection.exclude/hide_viewport` (per view layer), `ob.hide_set()` (per view layer, what the eye icon does) vs `ob.hide_viewport` (global, monitor icon). Use `ob.visible_get()` for the combined answer.
- Many operators act on **selected** objects, not only the active one. Deselect all (`for o in bpy.context.selected_objects: o.select_set(False)`) before selecting what you want.

## 3. Speed: data API and BMesh, not operators in loops

- Measured upstream on 5.2.1: 600× `primitive_monkey_add` 4.16 s vs 600× `bpy.data.objects.new` + link 0.015 s; reading 491k vertex positions: Python loop 105 ms, `foreach_get("co")` 7 ms, `attributes["position"].data.foreach_get("vector")` 0.1 ms (float32 numpy). Never call `bpy.ops` inside per-object or per-vertex loops.
- Build meshes with `me.from_pydata(verts, [], faces)` then `me.validate()`, or BMesh:

```python
import bmesh
bm = bmesh.new(); bm.from_mesh(me)            # Object Mode
bm.verts.ensure_lookup_table()                # before bm.verts[i] (also after adding)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bm.normal_update(); bm.to_mesh(me); bm.free(); me.update()

bm = bmesh.from_edit_mesh(me)                 # Edit Mode: do NOT free, then:
bmesh.update_edit_mesh(me)
```

- While an object is in Edit Mode, `ob.data` is stale: call `ob.update_from_editmode()` before reading it. References into mesh/BMesh data die on mode switches, undo and bulk adds – store names/indices, re-fetch.
- Iterate copies when renaming/removing: `for ob in bpy.data.objects[:]`. The name you request is not always the name you get (`Cube.001`): keep the returned object.

## 4. Evaluated data and applying modifiers

```python
dg = bpy.context.evaluated_depsgraph_get()
ob_eval = ob.evaluated_get(dg)
me_eval = ob_eval.to_mesh()                  # temporary, owned by ob_eval
tris = sum(len(p.vertices) - 2 for p in me_eval.polygons)
ob_eval.to_mesh_clear()                      # always clear
baked = bpy.data.meshes.new_from_object(ob_eval)   # persistent copy, 0 users until linked
```

- `ob.data` ignores modifiers; counts, bounds and BVH/raycasts on the final shape need the evaluated object. `BVHTree.FromObject` needs an **evaluated** depsgraph (4.0).
- `matrix_world` is stale after changing location/parent/constraints until `view_layer.update()`.
- `bpy.ops.object.modifier_apply(modifier=name)` needs Object Mode, single-user data and no shape keys (except deform-only on shapes): errors `Modifiers cannot be applied in edit mode`, `Modifiers cannot be applied to multi-user data`, `Modifier cannot be applied to a mesh with shape keys` **[src 5.2]**. Non-destructive alternative: `new_from_object` on the evaluated object, then swap `ob.data`.
- `scene.frame_set(f)` (not `frame_current = f`) re-evaluates animation before you read geometry.

## 5. Mesh API removals

| Old | Gone in | Use |
|---|---|---|
| `mesh.calc_normals()` | 4.0 | nothing (normals are lazy) |
| `ob.face_maps`, `mesh.face_maps` | 4.0 | integer face attribute |
| `edge.bevel_weight`, `edge.crease` | 4.0 | attributes `bevel_weight_edge`, `crease_edge` (`..._vert`) |
| `mesh.use_auto_smooth`, `auto_smooth_angle` | 4.1 | `mesh.shade_smooth()` + `mesh.set_sharp_from_angle(angle=a)`, or `bpy.ops.object.shade_auto_smooth(angle=a)` (adds a pinned "Smooth by Angle" GN modifier) |
| `calc_normals_split()`, `loop.normal` reads | 4.1 | `mesh.corner_normals`, `mesh.normals_domain` |
| Boolean solver `'FAST'` | 5.0 | `'FLOAT'` (default `'EXACT'`, `'MANIFOLD'` 4.5+) |

Removals checked on the release branches before/after **[src]**; attribute names from the vendored skills. Smooth by Angle is a modifier: the exporter must apply modifiers or its sharp edges never reach FBX/glTF.

## 6. Materials and nodes

```python
mat = bpy.data.materials.get("M_Wall") or bpy.data.materials.new("M_Wall")
# mat.use_nodes = True    # 5.0+: deprecated, no effect, always True – drop it (keep only for <5.0)
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")  # not nodes["Principled BSDF"] (localized/renamed)
bsdf.inputs["Specular IOR Level"].default_value = 0.5     # was "Specular" (≤3.6)
bsdf.inputs["Emission Color"].default_value = (1, 0.5, 0, 1)  # was "Emission"
bsdf.inputs["Emission Strength"].default_value = 3.0      # default 0.0 since 4.0: emission is OFF until set
img_node.image.colorspace_settings.name = "Non-Color"     # normal/roughness/metal/AO maps; only albedo+emission are sRGB
mat.surface_render_method = 'DITHERED'   # 4.2+; or 'BLENDED'. blend_method is deprecated; 'CLIP' maps to DITHERED (threshold alpha in the shader)
```

- 4.0 Principled v2 names **[src 5.2]**: `Subsurface Weight`, `Specular IOR Level`, `Specular Tint` (now a color), `Transmission Weight`, `Coat Weight`, `Sheen Weight`, `Emission Color`; `Subsurface Color` removed (uses Base Color). Old names raise `KeyError: 'bpy_prop_collection[key]: key "Specular" not found'`. 5.2 adds `Thin Wall`; 5.3 (beta) adds `Transmission Dispersion Scale/Abbe Number`.
- Node group sockets (4.0): `tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')`; iterate `tree.interface.items_tree`. `tree.inputs.new()` no longer exists.
- GN modifier inputs (**5.2**, new `NodesModifier.properties`): `getattr(mod.properties.inputs, ident).value = 5.0` where `ident` comes from the interface socket's `identifier`; `mod["Socket_2"] = 5.0` is the ≤5.1 way and fails on 5.2. Branch on `bpy.app.version`.
- Compositor (5.0): `scene.compositing_node_group = bpy.data.node_groups.new("Comp", "CompositorNodeTree")`; `scene.node_tree` is gone.

## 7. Render engine ids, drawing, properties

- EEVEE id **[src]**: `'BLENDER_EEVEE'` ≤4.1 (legacy) → `'BLENDER_EEVEE_NEXT'` 4.2–4.5 → `'BLENDER_EEVEE'` again 5.0+. Wrong one: `TypeError: bpy_struct: item.attr = val: enum "BLENDER_EEVEE_NEXT" not found in ('BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'CYCLES')`.
- `import bgl` fails from 5.0 (module removed, deprecated since 4.0) → `gpu` (`gpu.state.blend_set('ALPHA')`, `gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')`, `gpu.texture.from_image(img)` instead of `Image.bindcode`). 5.2: call `gpu.init()` before GPU drawing in `--background`.
- 5.0: `bpy.props` properties are attribute-only (`scene.cycles`, `ob.my_addon`); `scene["cycles"]`/`ob.get("my_prop")` no longer reach them. Render pass names, `image_settings.media_type` (set before `file_format`) also changed – see `blender-current-api`.

## 8. Headless runs

```bash
blender -b scene.blend --factory-startup --python-exit-code 1 -P build.py -- --out "D:/exports" --lod 2
```

```python
import sys, argparse
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
args = argparse.ArgumentParser().parse_args(argv)
```

- Without `--python-exit-code N` a Python exception still exits 0. Redirect to a log and check `$?`; a pipe into `tail` hides it.
- Arguments run left to right: `.blend` before `-P`; `-o/-F/-E` before `-f/-a`; script args only after `--`.
- `--factory-startup` keeps the user's add-ons/prefs out (cleaner, reproducible). Drop it when the script needs an add-on the user installed (e.g. Sollumz); `--addons <module>` or `bpy.ops.preferences.addon_enable(module=...)` enables one by module name (extensions: `bl_ext.<repo>.<id>`; installed names: `import addon_utils; [m.__name__ for m in addon_utils.modules()]`, enabled ones: `bpy.context.preferences.addons.keys()`).
- 5.1+: the user site-packages are not on `sys.path`; pass `--python-use-user-env` if a script needs pip-installed modules.
- Save to an absolute path; never overwrite the user's file: `bpy.ops.wm.save_as_mainfile(filepath=p, copy=True)`. Data-blocks with 0 users are dropped on save.

## 9. FBX to Unreal 5.8 (verify with a 1 m test cube)

```python
bpy.ops.export_scene.fbx(
    filepath=path, use_selection=True, object_types={'MESH', 'ARMATURE', 'EMPTY'},
    apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL',   # default 'FBX_SCALE_NONE'
    axis_forward='-Z', axis_up='Y',                               # exporter defaults
    bake_space_transform=False,      # add-on marks it experimental, "known to be broken with armatures/animations"
    use_mesh_modifiers=True,         # WARNING in add-on: prevents exporting shape keys
    mesh_smooth_type='FACE',         # default 'OFF' (normals only) – UE warns about missing smoothing groups
    use_tspace=True, add_leaf_bones=False, use_armature_deform_only=True,
    path_mode='COPY', embed_textures=False)
```

Option names/defaults **[src 5.2, io_scene_fbx 5.15.0]**. Model at metric, `unit_settings.scale_length = 1.0`, apply rotation/scale (`transform_apply`) before export; in UE keep *Convert Scene* and *Convert Scene Unit* on. UCX_/LOD naming, per-clip animation files and glTF: `blender-game-export`. GTA/Sollumz export: not FBX – see `fivem-mlo-creation`.

## 10. Add-on vs extension (4.2+)

- New packages are **extensions**: `blender_manifest.toml` next to `__init__.py`; `bl_info` is legacy-only. Required keys **[src 5.2 bl_pkg]**: `schema_version`, `id`, `version`, `name`, `tagline` (≤64 chars, no trailing punctuation), `maintainer`, `type` (`"add-on"`/`"theme"`), `license` (list, e.g. `["SPDX:GPL-3.0-or-later"]`), `blender_version_min`. Optional: `permissions` (`network`, `files`, …), `wheels`, `platforms`.
- Inside an extension use relative imports (`from . import ops`), never `import my_addon`; the package is `bl_ext.<repo>.<id>`. Bundle third-party Python as wheels, do not `pip install` at runtime.
- Store files with `bpy.utils.extension_path_user(__package__, path="cache", create=True)`; the extension folder is wiped on update.
- Check/build: `blender -c extension validate`, `blender -c extension build` (run in the package folder).
- In `register()`, `bpy.context`/`bpy.data` are restricted: `AttributeError: '_RestrictContext' object has no attribute 'scene'`. Defer scene work to an operator, handler or `bpy.app.timers.register(fn, first_interval=0)` (GUI only).
- Subclasses of Blender types that define `__init__` must call `super().__init__(*args, **kwargs)` (4.4+).

## 11. MCP sessions (official Blender Lab server or ahujasid)

- Code runs in the user's open file on the main thread: make each call small, idempotent (get-or-create by name, tag owned objects) and save a copy first.
- Return a compact JSON-able summary (counts, names, dimensions), not whole meshes. On the official server assign it to `result` (see `blender-verify`).
- Never `time.sleep`/long loops in the GUI session; heavy batch work goes to `blender -b` subprocesses.
- Look at a screenshot or render before saying done (`blender-verify`).

## Done checklist

- [ ] `bpy.app.version` read; version-specific branches only where needed.
- [ ] No context dicts, no `bgl`, no `use_auto_smooth`, no `tree.inputs.new`, no old Principled names, no `mat.use_nodes` reliance.
- [ ] No `bpy.ops` in loops; BMesh freed; `to_mesh_clear()` called.
- [ ] Objects linked to a view-layer collection; selection explicit; Object Mode at the end.
- [ ] Headless run used `--python-exit-code 1`; log has no `Traceback`.
- [ ] Export: transforms applied, test cube size checked in the target.
- [ ] Solved a new bpy bug? Add a row to [references/common-errors.md](references/common-errors.md) with the exact message and version.
