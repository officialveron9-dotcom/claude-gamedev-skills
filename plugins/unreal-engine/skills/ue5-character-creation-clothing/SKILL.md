---
name: ue5-character-creation-clothing
description: Pitfalls, exact settings and fixes for creating and dressing characters in Unreal Engine 5 (current 5.8). Covers MetaHuman Creator outfits and parametric clothing; Fab, Character Creator, Daz and Mixamo imports and licenses; modular outfits (Leader Pose, Copy Pose, Skeletal Mesh Merge, Mutable); skin weights, poke-through and clothing LODs; Chaos Cloth Asset/Dataflow; grooms and hats. Use when importing or dressing a character, or when clothing clips, stretches or explodes, or hair floats. German: Charakter erstellen, Kleidung, anziehen, Klamotten, Stoffsimulation, Haare, MetaHuman Fehler.
---

# UE5 characters and clothing: workflows, traps, fixes

Scope: player, opponent and pool-hall NPCs in a photoreal billiards game, built by a solo developer. Animation (AnimBP, retargeting, Control Rig, MetaHuman LOD and performance tuning) lives in `ue5-animation-characters`. Skin and cloth *materials* (Substrate) live in `ue5-lighting-rendering`. Crowds live in `ue5-npc-ai`, outfit replication in `ue5-multiplayer`, and frame budgets in `ue5-performance-optimization`.

## Version status (checked 2026-10-06)

The current release is **UE 5.8** (5.8.x hotfixes). 5.9 has been mentioned informally but is not released. Statuses below come from release notes or doc extracts. Re-check them after any engine upgrade.

| Feature | Status | What it means for you |
|---|---|---|
| Chaos **Cloth Asset** + Dataflow cloth editor (formerly "Panel Cloth") | **Production-ready and the default cloth editor in 5.8** (Beta in 5.7) | Author new cloth here. The legacy Clothing Tool (painted inside the Skeletal Mesh editor) still works and is still required with Mutable |
| MetaHuman Creator **inside the editor** + parametric body + **Outfit Asset** | 5.6+ (the web Creator is retired) | Characters are a `MetaHuman Character` asset that you *assemble*. Autorig and texture synthesis use Epic cloud services, so you need to be online and logged in |
| Mutable (Customizable Object) | The 5.8 release notes say it "reaches production readiness". A secondary plugin index still lists it as Beta | Check the plugin's flag in *Edit > Plugins*. It does **not** support Cloth Asset (panel) cloth |
| Interchange FBX importer | Default since 5.5 | Option names differ from old FBX tutorials (see below) |
| Substrate | Production-ready since 5.7 | Skin and cloth shading: see `ue5-lighting-rendering` |
| MetaHuman Crowd / Collections, Nanite skinned meshes | Experimental | Do not ship characters on them. Nanite skinned meshes do not support grooms, morph targets or cloth |

## Pick a source per role

| Role | Recommended source | Why | Main risk |
|---|---|---|---|
| Player / opponent (close-ups at the table) | MetaHuman (UE Optimized, High) or CC5 HD | Facial rig, skin, grooms | Cost, and clothing fit on custom bodies |
| Named NPCs (bartender, referee) | MetaHuman (UE Optimized, Medium/Low) or CC | Same skeleton as the heroes | Groom cost. Use cards |
| Background NPCs | Fab modular characters on the **UE5 Manny/Quinn skeleton**, merged meshes | Cheap. Shares animations | License type and skeleton must be checked *before* buying |
| Prototype | Manny/Quinn, Mixamo | Fast | Mixamo has no root bone, and its license is separate |

Skeleton map: MetaHuman body = an **extended UE5 Manny skeleton** (same core bones, plus extra twist/corrective bones). CC5 HD adds about 10 spine/head bones for 1:1 mapping to UE5/MetaHuman. Daz Genesis and Mixamo use their own hierarchies, so they **need IK Retargeting** (see `ue5-animation-characters`). Details per source: [references/sources-pipelines.md](references/sources-pipelines.md).

## Top traps (read first)

1. **Clothing skinned to a different hierarchy than the body.** Leader Pose maps by bone name. Bones the follower has but the leader lacks (or the leader's LOD strips) leave vertices stuck or stretched to the origin. **Fix:** skin every garment to the body's own skeleton. For a MetaHuman, use the *Export Combined Skel Mesh* body; for Manny, use `SK_Mannequin`. Do not add bones to garments.
2. **One AnimBP per clothing piece.** Use **Leader Pose** (followers run no animation). Use Copy Pose From Mesh only where a piece needs its own physics or anim nodes. Merge meshes for background NPCs.
3. **Assuming MetaHuman parametric-outfit cloth sim survives assembly.** It doesn't. 5.8 forum reports (one with an official reply) say Creator/assembly strips the sim mesh, so the garment becomes static. For fixed game characters, re-add the simulation after assembly: build a Cloth Asset from the *resized* garment and put it on a Chaos Cloth Component.
4. **Body Hidden Face Map set after assembly, or several masks at once.** The mask is applied **during assembly**. Only one body-hide mask applies (5.6), so build a unified mask for combined garments. An all-black mask fails (the body comes back fully visible), so leave at least some faces visible.
5. **Garments without matching LODs**, or garment components not handled by LODSync. At distance the body drops a LOD and the garment doesn't (or the reverse), giving tearing, gaps or poke-through. Give every garment the same LOD count and screen sizes as the body, and add it to *Components to Sync*.
6. **Simulating whole garments.** Keep Max Distance = 0 (fully skinned) on everything that touches the body. Simulate only loose regions (hem, open jacket front, skirt). In a billiards stance the torso folds over the rail, and a fully simulated shirt jitters and clips.
7. **No cloth reset after teleports, respawns or Sequencer cuts.** The "velocity" of the jump explodes the cloth. Call the teleport/reset API (see [references/cloth-sim.md](references/cloth-sim.md)).
8. **Fixing poke-through with bigger cloth thickness or more sim.** Solve it in this order instead: authoring offset → hidden body faces → skin weights → correctives/morphs → cloth (see below).
9. **Misreading licenses.** Fab *Standard License* (Personal or Professional tier) allows commercial games in any engine, except content marked **UE-Only** (Unreal only) and NoAI restrictions. **Daz** content needs a paid **Interactive License** per product before you distribute it, even for free games. **Reallusion** content needs export rights, and an Extended License for "mass character outputs".
10. **Import defaults.** Morph targets are not reliably imported, and normals may be recomputed (flat or faceted seams). Set *Import Morph Targets* on and *Normal Import Method* = Import Normals (and Tangents). Reallusion's tracker reports that **morphs + Use T0 As Ref Pose crashes** the FBX morph import.
11. **Followers culled or flickering at screen edges and in close-ups.** Followers use their own bounds. Set `bUseBoundsFromLeaderPoseComponent = true`, and make the body's Physics Asset (which drives bounds) cover the whole silhouette.
12. **Groom bound to the wrong mesh or LOD, or Skin Cache off.** Hair floats, offsets or disappears. Rebuild the Groom Binding against the exact final body/face mesh, enable *Support Compute Skin Cache*, and switch LODs on the skeletal mesh, not on the groom.

## Dressing method decision

| Method | Game thread | Render thread | Physics on pieces | Morph targets | Use for |
|---|---|---|---|---|---|
| **Set Leader Pose Component** | Min | High (each piece skinned and drawn separately) | No | Yes | Default for player/opponent outfits |
| **Copy Pose From Mesh** (AnimBP node per piece) | High | High | AnimDynamics / RigidBody | Yes | A piece that needs its own physics or anim nodes |
| **Skeletal Mesh Merge** (`SkeletalMerging` plugin) | Medium | **Low** | Yes | **No** | Background NPCs, fixed outfits |
| **Mutable** Customizable Object | Generated at runtime or in editor | One merged mesh | Legacy cloth only | Via Mutable | Many combinations (character creator UI) |
| **MetaHuman assembly** | – | – | Re-add cloth (trap 3) | MetaHuman correctives | MetaHuman heroes |

The cost table is Epic's (modular-characters doc). Code, pitfalls and MetaHuman specifics: [references/outfits-and-poke-through.md](references/outfits-and-poke-through.md).

Minimal Leader Pose setup (C++):

```cpp
// Constructor: pieces are children of the body mesh (GetMesh()).
Shirt = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Shirt"));
Shirt->SetupAttachment(GetMesh());
// BeginPlay (or after swapping meshes at runtime):
Shirt->SetLeaderPoseComponent(GetMesh(), /*bForceUpdate*/ true);
Shirt->bUseBoundsFromLeaderPoseComponent = true;
```

Each follower still costs a draw call per material section, plus skinning. For four or more pieces on NPCs, merge them.

## Poke-through: fix in this order

1. **Authoring:** in the DCC, the garment sits at least a few mm off the skin in the bind pose *and* in extreme poses (bridge stance, arm fully back on the stroke). Test with the actual stroke animations.
2. **Remove hidden body faces:** MetaHuman *Body Hidden Face Map* (assembly time), CC *Delete Hidden Mesh* on export, Mutable *Remove Mesh Blocks* / *Clip Mesh With Mesh*, or delete triangles in the DCC per outfit variant. An opacity mask in the skin material is the last resort, because it switches the skin to Masked.
3. **Skin weights:** transfer them from the body, then smooth. Garment and body must share weights where they touch (collar, cuffs, waistband).
4. **Correctives:** MetaHuman body correctives deform the body but not your garment. Add matching morphs or corrective bones to the garment, or turn the correctives off for that character (cost note in `ue5-animation-characters`).
5. **Cloth sim:** collision with the Physics Asset, or a kinematic collider for loose parts only. Never use cloth to hide skinning errors.

## Cloth simulation: quick rules (UE 5.8)

- New garments: **Cloth Asset** (Dataflow graph) on a **Chaos Cloth Component** that is a child of the body, with Leader Pose set to the body. Existing legacy clothing data can be converted (the `DF_LegacyClothingAssetTemplate` Dataflow template).
- Graph spine (verified node names): garment import (`StaticMeshImport`, or USD) → `TransferSkinWeights` (from the body) → `WeightMap` (paint the MaxDistance area) → `SimulationDefaultConfig` + `SimulationMaxDistanceConfig` + `SimulationCollisionConfig` / `SimulationSelfCollisionConfig` / `SimulationBackstopConfig` / `SimulationLongRangeAttachmentConfig` / `SimulationVelocityScaleConfig` / `SimulationSolverConfig` → `SetPhysicsAsset` → `ClothAssetTerminal`.
- Stability: raise solver iterations and substeps before stiffness. Add Long Range Attachment (tethers) against stretching. Clamp the velocity scales (`MaxVelocityScale`, `FictitiousAngularScale`) for fast turns. Use local-space sim when far from the origin.
- Collision: Physics Asset capsules on the bones under the garment. 5.8 adds a tapered capsule update. Kinematic or skinned-triangle-mesh colliders handle tight fits. Turn on CCD for fast limbs.
- Cost: disable the simulation on lower LODs and when off-screen or distant (`SetEnableSimulation(false)` / suspend). NPCs get no simulated cloth.
- Multiplayer: cloth is cosmetic and never replicated. Replicate the outfit ID and build it locally. Skip cloth/groom components on a dedicated server.

Full settings and jitter/explosion triage: [references/cloth-sim.md](references/cloth-sim.md).

## Import settings that matter (skeletal meshes)

| Setting | Value | Why |
|---|---|---|
| Skeleton | Pick the existing body skeleton (Manny / MetaHuman / source rig) | Leaving it empty creates a duplicate skeleton, which makes animations and Leader Pose incompatible |
| Import Morph Targets | On (when the garment has morphs or correctives) | Not reliably on by default |
| Normal Import Method | Import Normals (and Tangents for baked normal maps) | Recomputed normals break smoothing at seams |
| Use T0 As Ref Pose | **Off** for meshes (on only when frame 0 really is the bind pose) | Combined with morphs it crashes Reallusion imports. A wrong T0 bakes an animation pose in as the bind pose |
| Create Physics Asset | On for the **body only**. Off for garments (they use the body's) | A garment physics asset is unused and confuses bounds |
| Units / axis (legacy FBX: *Convert Scene Unit*, *Force Front XAxis*) | Export in cm or with unit conversion. Blender: *Apply Scalings: FBX All* (or unit scale 0.01), *Add Leaf Bones* off | Wrong scale = 100x or 0.01x mesh, a root bone scaled 100, IK and physics broken |
| Import Meshes in Bone Hierarchy | Off unless you mean it | Otherwise meshes under bones turn into bones (or the reverse) |

## Checklist: add a new outfit to an existing character

- [ ] License allows game distribution (Fab Standard and not UE-Only for another engine; Daz Interactive; Reallusion export).
- [ ] Skeleton matches. Fab listing says "Rigged to Epic skeleton: Yes" (UE5 Manny), or the item is a MetaHuman wardrobe item (`WI_*`, `.mhpkg`, parametric/outfit).
- [ ] Garment skinned to the body's skeleton with no extra bones. Import with *Skeleton* set to the body skeleton.
- [ ] Bind pose matches (A-pose for Manny/MetaHuman). If it doesn't, re-skin in the DCC; don't "fix" it with T0.
- [ ] LOD count and screen sizes equal the body's. The garment is added to LODSync *Components to Sync* (MetaHuman).
- [ ] Hidden body faces handled (mask, delete, Mutable). Test the bridge stance, cue stroke follow-through, sitting and walking.
- [ ] Leader Pose set, `bUseBoundsFromLeaderPoseComponent` on, Physics Asset bounds cover the outfit.
- [ ] Cloth only on loose parts. Max Distance is 0 where the garment touches skin. Teleport/reset is wired. Cloth is disabled on lower LODs.
- [ ] Shadows: the garment casts shadows. For capsule shadows, check the body's Shadow Physics Asset.
- [ ] Materials: textures 2K for heroes, 1K or lower for NPCs (starting points). Uses the project's material path (Substrate or legacy).
- [ ] Packaged build tested (missing parent materials in `.mhpkg` exports are a 5.8 known issue).

Per-source import checklists (MetaHuman, Fab, CC4/CC5, Daz, Mixamo, Blender/Marvelous/CLO): [references/sources-pipelines.md](references/sources-pipelines.md).

## Fast triage (full table in common-issues.md)

| Symptom | First check |
|---|---|
| Skin pokes through at elbows/shoulders/hips | Correctives or body shape differ from the garment's source body. Use hidden faces and garment correctives |
| Garment stays in T/A-pose while the body animates | Leader Pose not set (or set before the mesh was assigned), or a different skeleton |
| Vertices stretch to the world origin | Bones missing in the leader or its LOD, or garment weights reference bones not in the body |
| Mesh is huge or tiny, or the root is scaled 100 | Unit export settings |
| Cloth explodes on spawn or cut | No teleport/reset. Collision bodies start inside the cloth |
| Cloth jitters while idle | Too few iterations/substeps, self-collision thickness too large, far from the origin |
| Cloth falls through the body | Physics Asset lacks bodies there, collision thickness 0, no CCD, physics bodies simulating with soft constraints |
| Hair floats or sits offset | Binding built against another mesh or LOD, a Z offset after a DCC round-trip, Skin Cache off |
| Clothing vanishes or changes at distance | Garment LODs missing or not in LODSync. Cloth disabled per LOD snaps to bind pose |
| Frame drops with many dressed NPCs | Too many follower components. Merge them, cards instead of strands, no NPC cloth |

## References

- [references/sources-pipelines.md](references/sources-pipelines.md): read when choosing or importing from MetaHuman, Fab, CC4/CC5, Daz, Mixamo, Blender, Marvelous/CLO. Covers licenses, skeletons, known import bugs and per-source checklists.
- [references/outfits-and-poke-through.md](references/outfits-and-poke-through.md): read when building outfits. Covers Leader Pose/Copy Pose/Merge code, MetaHuman wardrobe and parametric outfits, skin weight transfer, hidden faces, LODs, Mutable, grooms and hats.
- [references/cloth-sim.md](references/cloth-sim.md): read when adding or debugging Chaos Cloth. Covers the Dataflow graph, collision, stability, teleport, wind, LOD/perf, multiplayer and CVars.
- [references/common-issues.md](references/common-issues.md): read when something looks wrong. A large symptom → cause → fix table.
- [references/sources.md](references/sources.md): URLs and how each was verified.
