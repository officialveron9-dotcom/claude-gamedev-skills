# Sources (all accessed 2026-10-10)

Method: forum.cfx.re, docs.fivem.net and most community sites did not resolve from the research environment.
Official docs were read from their source repos, and code from cloned GitHub repos (HEAD commit given). Forum items
were seen only as search-engine summaries and are marked **snippet**. Everything else was **read directly**.

## Primary, read directly

| URL | Backs up |
|---|---|
| https://github.com/citizenfx/fivem-docs/blob/master/content/docs/assets-manual/beginner-series/part-8.md (= docs.fivem.net/docs/assets-manual/beginner-series/part-8/, HEAD `c2b2125`, 2026-10-01) | Official door workflow: templates `v_ilev_bl_door_l`, `prop_facgate_07b`, `lr_prop_supermod_door_01`; origin per type; Special Attribute 7/8/5; flags Dynamic + Enable Door Physics; Copy Transforms to the template bone; new Bound Composite after collision edits |
| .../assets-manual/beginner-series/part-3.md | Vertex colour `Color 1` green = interior / red = exterior; Sollumz export Native/Gen8 |
| .../server-manual/server-commands.md | `increase_pool_size` pools and limits (PortalInst, OcclusionPortalInfo/Entity, InteriorProxy, OcclusionInteriorInfo); Pool Monitor |
| https://github.com/citizenfx/natives `OBJECT/*.md` (HEAD `7263f21`, 2026-08-17) | Signatures and notes: AddDoorToSystem (local door system, scriptDoor cap), DoorSystemSetDoorState (states 0-6, physics-loaded note), SetOpenRatio (-1..1), SetAutomaticRate/Distance, SetHoldOpen, IsDoorRegisteredWithSystem, FindExistingDoor (0.5 radius), RemoveDoorFromSystem, IsDoorClosed, GetClosestObjectOfType, DoorControl / SetStateOfClosestDoorOfType "not in multiplayer" |
| https://github.com/citizenfx/fivem `ext/native-decls` (HEAD `0105063`, 2026-10-09) | `DoorSystemGetActive`, `DoorSystemGetSystemSize`, interior portal natives (`Get/SetInteriorPortalFlag`, ...), `AddStateBagChangeHandler` |
| https://github.com/citizenfx/fivem `data/shared/citizen/scripting/lua/scheduler.lua` | `GlobalState = NewStateBag('global')` (bag filter `global`) |
| https://github.com/overextended/ox_doorlock (v1.22.1, HEAD `ba092ff`, 2026-07-03): `client/main.lua`, `client/utils.lua`, `server/main.lua`, `server/hooks.lua`, `server/convert.lua`, `sql/*.sql`, `web/src` labels, `config.lua` | Door fields, DB storage, `/doorlock`, state 4 snap, auto/doorRate/holdOpen handling, rate 10.0 for non-auto, E = control 38, exports/events, ACE `doorlock.<name>`, no distance check, hook can only grant, server TriggerEvent bypass, sound names, maxDistance default only in the UI |
| https://github.com/qbcore-framework/qb-doorlock (HEAD `4a8e911`, 2026-08-24): `config.lua`, `configs/example.lua`, `client.lua`, `server.lua` | `Config.DoorList` format, doorType values, garage/sliding = automatic distance 30/0 + rate 1.0, 30 m registration range, `prop_com_gar_door_01` example, `updateState` trusting `unlockAnyway`/`sentSource` |
| https://github.com/Sollumz/Sollumz (2.9.0-dev, HEAD `07d6a49`, 2026-10-10): `ytyp/properties/{ytyp,flags,extensions,mlo}.py`, `ytyp/operators/portal.py`, `ytyp/gizmos/mlo.py`, `yft/{properties,ui,yftexport}.py`, `ybn/{collision_materials,properties}.py`, `ydr/render_bucket.py`, `sollumz_preferences.py` | SpecialAttribute enum (5, 7, 8, 9, 10, 12...), archetype/portal/room/entity flag names, Door extension fields, portal From/To + corners + Create From Verts (viewport-sorted) + Flip, portal arrow formula, entity Attached Portal, breakable glass export rules and warnings, glass types Pane/Security/Pane Weak, glass collision materials, render bucket descriptions, Gen8/Gen9 export targets |
| https://github.com/Sollumz/Sollumz (same HEAD) bpy-level API: `sollumz_properties.py`, `tools/{blenderhelper,boundhelper,drawablehelper,meshhelper}.py`, `ydr/operators/{drawables,materials}.py`, `ydr/properties.py`, `ybn/{operators,properties}.py`, `lods.py`, `sollumz_helper.py`, `sollumz_preferences.py`, `ytyp/operators/ytyp.py`, `ytyp/properties/ytyp.py` | `sollum_type` values, Drawable/model/composite/bound layout, `UVMap 0`/`Color 1` names, `sz_lods` slots, `sollumz.createshadermaterial(shader_index)` + `wm.sz_shader_materials`, `sollumz.clearandcreatecollisionmaterial` + `wm.sz_collision_material_index`, `sollumz.createbound` applies the default flag preset, `createytyp` / `new_archetype()` / `special_attribute` / `flags.flagN`, export relative to the Drawable, "Apply Parent Transforms" default off; physics dictionary auto-set to the asset name |
| https://pypi.org/project/bpy/ (wheels 5.2.2 on Python 3.13 and 4.2.0 on Python 3.11, installed with uv) | Headless execution of all generators in procedural-modeling.md: 51/51 checks on both; stale `matrix_world` after setting `location` until `view_layer.update()` |
| https://pypi.org/project/szio/ (1.3.0 wheel, Sollumz dependency): `szio/gta5/Shaders.xml`, `ShadersG9ParamsDefaults.json` | Glass shader names, buckets, samplers and parameter defaults; no `decal_glass`; all `glass_*` present for Gen9 |
| https://github.com/Sollumz/wiki (= docs.sollumz.org, HEAD `ab7338c`, 2026-09-25) | Archetype flag descriptions (Enable Door Physics needs special attribute; Draw Last; Double-sided), ytyp fields, create-ytyp tutorial (Room -> Limbo, arrow, Flip Direction), fragments (Dynamic flag for physics; GlassWindows "not supported" note), FAQ (wrong Room ID → MLO disappears; vertex paint), light flags, LOD lights bake, occluders, Enhanced conversion notes |
| https://github.com/dexyfex/CodeWalker (HEAD `485d56b`, 2025-04-11): `CodeWalker/Project/Panels/EditYtyp{Archetype,MloPortal,MloRoom}Panel.Designer.cs`, `CodeWalker.Core/GameFiles/MetaTypes/MetaTypes.cs` | Numeric values of archetype (e.g. 131072, 67108864), portal and room flags; `CExtensionDefDoor` fields |
| https://github.com/nikez/gtav_audio_occlusion_documentation `stream/v_int_66.ytyp.xml` (vanilla `v_shop_247` export) | Vanilla door/window setup: door entity origin at z = 1.15 (mid-height of the leaf), both 24/7 leaves extending along local −X (the left one rotated 180°), doors and glass attached to room->limbo portals, portal flags 8192/8/1796, door extension values, entity flags/lodDist, portal corner order and offset from glass, room flags 96/608 |
| https://github.com/sinanovicanes/cfx-anes-gates (HEAD `50da4a3`, 2024-03-28) | Automatic distance/rate behaviour of gates and barriers (rate ≥ 1.5, refresh), `prop_sec_barier_02a` is not a door |
| https://github.com/citizenfx/fivem/issues/2563 (fetched) | Map doors not networked; each client has its own copy; script-sync workaround |
| https://github.com/citizenfx/rfc/discussions/360 (fetched; Enhanced patch notes 2026-08-04) | Door opening speed frame-rate independent; GetClosestObjectOfType/GetGamePool crash near MLOs fixed |

## Secondary, search snippets only

| URL | Backs up |
|---|---|
| https://forum.cfx.re/t/guide-lock-doors-like-a-boss-how-to-use-gtas-built-in-door-locking-system/4259344 (**snippet**) | Lock state set while out of range is applied when the door comes into scope; locking an ajar door closes it, then locks it |
| https://forum.cfx.re/t/doorsystemsetopenratio/5201027 (**snippet**) | `DoorSystemSetOpenRatio(h, -1.0, true, true)` on an unlocked door oscillates (b2944 canary, unresolved) |
| https://forum.cfx.re/t/noted-issues-so-far/3379798 (**snippet**) | OneSync: door states missing for other players; fixed by broadcasting state events |
| fivemx.com "How To Create FiveM MLOs" / forum.cfx.re thread 5283564 (**snippet**, source not pinned) | "Blue arrow should point out, i.e. from room to limbo"; check floor/room IDs for flicker |

## Not verified (marked "(verify)" in the skill)

Semantics of portal flags 8/64/8192 and `exteriorVisibiltyDepth`; special attributes 9/10/12 in practice; the
ratio + lock garage pattern per model; `prop_sc1_21_g_door_01`; ymap-placed doors inside MLO doorways; entity scale
on dynamic doors; whether broken glass resets; which assets fill the portal pools; E key (control 38) in vehicles;
ray-traced glass on Enhanced; the exact motion of Garage Door (5) (lift vs tilt) and the slide direction of type 8;
whether a skeleton-less custom drawable works as a door; which bound flags vanilla doors use; the leaf-along-−X
convention for templates other than the 24/7 doors; all `sz_*` Sollumz calls in the generators (not executed).
