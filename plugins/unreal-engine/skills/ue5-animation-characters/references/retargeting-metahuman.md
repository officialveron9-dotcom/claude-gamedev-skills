# Retargeting and MetaHumans: workflow traps (UE 5.6–5.8)

## IK Rig / IK Retargeter (5.6+ op stack)

The 5.6 refactor replaced the old chain/root settings with ops, so pre-5.6 tutorials show a UI that no longer exists. The default op order is **Pelvis Motion → FK Chains → IK Chains → Run IK Rig → Root Motion**. 5.8 adds a foot plane/toe definition for the target, splits Blend to Source, Scale Goals and Offset Goals into separate ops, and adds **Retarget Override Sets**: one retargeter asset with alternative op/property sets, which can be bound to a curve or variable.

Checklist per new skeleton:
- [ ] IK Rig: retarget root = pelvis/hips (never the root bone). Run **Auto Retarget Chains**, then check spine chain counts, fingers and twist bones by hand.
- [ ] Leg/arm IK goals with a **Full Body IK** solver whose root is the pelvis. Assign the goals to the solver, or the goals do nothing.
- [ ] Retargeter: the source and target IK Rigs are set and the chain mapping has no `None` on limbs.
- [ ] Retarget pose: use **Auto Align**, applied to the whole skeleton or to selected bones. Handle T-pose (Mixamo) vs A-pose (Manny/MetaHuman) here, never in the clips.
- [ ] Root Motion op source: `Copy From Source Root` (source has a real root) or `Generate From Target Pelvis` (source has no root, as with Mixamo).
- [ ] Export: *Export Selected Animations*, or right-click clips → **Retarget Animation Assets** with *Auto Generate Retargeter*. Auto-generation only works for skeleton types the engine recognizes. Batch jobs use Python `BatchRetargetSettings` (`auto_generate_retargeter`).
- [ ] Foot sliding after retargeting (very different leg lengths): follow Epic's "Fix Foot Sliding with IK Retargeter" speed-planting setup, which adds FBIK foot goals on the target IK Rig with the solver root on the pelvis.

## Mixamo specifics

| Trap | Fix |
|---|---|
| No root bone, so root-motion clips leave the capsule behind | Root Motion op = `Generate From Target Pelvis`, or add a root in a DCC. For loops, download "In Place" variants |
| T-pose source vs A-pose target gives raised or crossed arms | Auto Align the retarget pose |
| Hips used as the retarget root on a skeleton without a root | Set the IK Rig retarget root to the hips (`mixamorig:Hips`), never to a parent the skeleton lacks |
| Finger chains unmapped, giving claw hands | Map the finger chains, or exclude them and keep the target's reference fingers |
| Scale mismatch (tiny or huge) | Fix the import scale (the FBX unit). Do not compensate in the retargeter |

Third-party helpers (UNAmedia "Mixamo Animation Retargeting" on Fab) automate root bones and rigs. They are optional.

## Runtime vs offline retargeting

- Runtime: `Retarget Pose From Mesh` (in the AnimBP of the target, which follows a source mesh). It costs CPU every frame, and **Run IK Rig/FBIK costs the most**. Epic suggests replacing FBIK with cheaper limb solvers for runtime use, and disabling the IK op at distance.
- Offline: export retargeted sequences once. **Ship this way** for the opponent and NPCs. Use runtime retargeting only for prototyping (GASP's MetaHuman sandbox uses it).

## MetaHuman pipeline (5.6+)

- The MetaHuman Creator **plugin in the editor** (the cloud-streamed Creator is retired) produces a **MetaHuman Character** asset, which you **Assemble** with a pipeline:
  - `UE Optimized` with **High/Medium/Low** quality, textures at most 2K: use this for the game.
  - `UE Cine`: full quality with bakes up to 8K. Use it for cinematics only, because the memory cost is large.
  - The UEFN export is not relevant here.
- Autorig and texture synthesis call Epic cloud services, so they need an internet connection and an Epic login. From 5.6 MetaHumans fall under the UE EULA.
- If an assembled character comes into a project without MetaHuman Creator, enable the **Groom** and **RigLogic** plugins. Turn on *Support Compute Skin Cache* (Project Settings → Rendering → Optimizations) and restart.
- 5.8 additions: Mesh to MetaHuman also conforms **bodies**, unbaked texture/material export, **MetaHuman Collections** (Experimental crowds; see `ue5-npc-ai`), better MetaHuman Animator solves, and Live Link Face video streaming. Core MetaHuman libraries were open-sourced under MIT.
- 5.8.3 hotfix: fixes dynamic resolution and split-screen wrongly affecting Nanite LOD for MetaHumans. Stay on the latest hotfix.

## LOD and cost controls

| Control | Where | Use |
|---|---|---|
| `LODSync` component | MetaHuman Blueprint | Keeps head (8 LODs) and body (4 LODs) switching together. `Num LODs` (-1 = derive), **`Forced LOD`** for distant or seated spectators |
| Groom geometry type | Groom asset → LOD settings: Strands → **Cards** | Strands only for heroes at LOD0. Cards (or meshes) for the rest. Disable groom simulation on NPCs |
| Enable Body Correctives | MetaHuman component | Off on spectators (worse deformation, cheaper) |
| Enable Neck Correctives | MetaHuman component | Epic notes a minimal visual difference and a significant cost, so turn it off first |
| Neck procedural Control Rig | MetaHuman component | Off or LOD-limited on NPCs |
| Facial Animation LOD Threshold | MetaHuman component | RigLogic is evaluated up to and including this LOD. Use 1–2 for NPCs and -1 (always) only for heroes in close-ups |
| Rigid Body LOD Threshold | MetaHuman component (when a Control Rig class is set) | Physics simulation up to this LOD. -1 = always, so avoid it for NPCs |

Traps:
- Outfits without matching LODs tear or clip when LODSync drops LODs. Generate LODs for custom clothing, or force a LOD.
- Animating clothing pieces with their own AnimBPs is costly. Use Leader Pose so they follow the body.
- Expecting Nanite skinned meshes to rescue MetaHuman cost does not work: they are Experimental and unsupported for grooms, morphs and cloth.
- Applying "hero" quality to everyone: a photoreal pool hall at 60 fps cannot afford strand grooms and full correctives on 10+ characters. Plan tiers (see performance.md).

## Facial animation options

| Need | Option |
|---|---|
| Player/opponent cutscene or close-up dialogue | MetaHuman Animator from video or depth (iPhone/stereo/mono camera), offline |
| NPC barks and voice lines | **Audio-driven** MetaHuman Animator, solved **offline** (needs 5.6+) into anim sequences, played as face montages. 5.8 adds emotion detection and procedural blinks |
| Live puppeteering or testing | MetaHuman Live Link plugin (webcam or mono camera) or the Live Link Face app (iOS/Android) |

Trap: running real-time audio-driven solving for many NPCs at runtime. Bake it instead.
