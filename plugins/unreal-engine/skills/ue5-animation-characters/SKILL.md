---
name: ue5-animation-characters
description: Pitfalls and fixes for character animation in Unreal Engine 5 (current 5.8) in a photorealistic billiards game. Covers thread-safe AnimBP and Property Access traps, linked anim layers, state machine vs Motion Matching/Chooser choices, montages, slots and notifies for the cue strike, root motion and Motion Warping into the stance, Control Rig/Full Body IK for bridge hand, cue grip and lean, foot IK, IK Rig/IK Retargeter (Mixamo, Manny, MetaHuman), MetaHuman LOD/groom cost, and animation performance (Budget Allocator, URO, a. CVars). Use it when building or debugging an AnimBP, Motion Matching, Control Rig, IK Retargeter or MetaHuman setup, or for foot sliding, a T-pose after retargeting, a montage not playing, or anim cost. German triggers: Animation, Charakter, Retargeting, Animations-Blueprint, Stoßanimation, Billard-Queue, Hand-IK, MetaHuman-Performance.
---

# UE5 character animation: pitfalls and fixes (billiards)

Scope: player and opponent at the table, plus cheap pool-hall NPCs. AI decisions are in `ue5-npc-ai`, replication in `ue5-multiplayer`, ball and cue physics in `billiards-game-dev`.

**Version (checked 2026-10-06):** UE 5.8 is current (released 2026-06-17, hotfix 5.8.3 seen). Do not build on these **Experimental** features: Mover (keep CMC), UAF/AnimNext (AnimBP successor), Offset Root Bone and Foot Placement nodes, MetaHuman Collections, Nanite skinned meshes (no grooms, morphs or cloth). Production-ready: Motion Matching (5.4+), Control Rig, IK Retargeter (op stack refactored in 5.6, so pre-5.6 tutorials show the wrong UI). Choosers were Beta in 5.4 and are now called production-ready by Epic staff, though some docs still say Experimental.

## Top traps (read first)

1. **Firing the ball impulse from an AnimNotify.** Queued notifies fire late and in batches. URO, the Budget Allocator and the off-screen tick option skip or delay them. **Right:** game code moves the cue along the aim axis on a stroke curve and applies the impulse at the computed contact time. Hands follow the cue by IK. Notifies only drive SFX, VFX and camera.
2. **Attaching the cue to `hand_r` and aiming by animation.** The tip never lands on the aim line. **Right:** the cue transform comes from aim data and both hands are IK goals on the cue (grip) and the cloth (bridge).
3. **Montage "plays" but nothing moves.** The AnimGraph has no `Slot` node with that name, the slot sits after IK that overwrites it, or the montage plays on the wrong mesh (a MetaHuman clothing part or face instead of the body).
4. **Logic in `Event Blueprint Update Animation`.** It runs serially on the game thread for every character. **Right:** use `BlueprintThreadSafeUpdateAnimation` plus Property Access, and enable `Warn About Blueprint Usage` in Class Settings.
5. **Hand-tuning URO on a mesh that is also `SkeletalMeshComponentBudgeted`.** The Budget Allocator controls that mesh's tick rate. Pick one system per mesh, and exempt the active shooter from both.
6. **Retargeting by editing clips.** A T-pose or bent limbs come from a bad retarget pose or chain map. Fix them in the IK Rig and Retargeter with **Auto Retarget Chains** and **Auto Align**.
7. **Mixamo root motion.** Mixamo has no root bone, so the capsule stays while the mesh walks away. Retarget with the Root Motion op set to `Generate From Target Pelvis`, or use In-Place clips.
8. **Strand hair on every MetaHuman.** Grooms dominate the GPU cost. Use strands only on hero characters at LOD0 and cards everywhere else, and turn off groom simulation on NPCs.
9. **FBIK always on.** Full Body IK is the most expensive IK option. Keep it in a branch with zero weight when no shot is active (zero-weight branches are not evaluated) and set `LOD Threshold` 0–1.
10. **Starting a root-motion montage while the AI is path following.** Root motion overrides CMC velocity and the move gets aborted. Finish the `MoveTo`, then play the montage.

## Shot sequence: wrong vs right

| Step | Wrong | Right |
|---|---|---|
| Stance position | Walk to the cue ball and let IK stretch | Game code computes the stance transform (cue ball, aim, handedness, bridge length, table bounds). If it falls inside the table footprint, a Chooser switches the variant (rail bridge, rest, sit on rail) |
| Getting down | `SetActorLocation` snap or a blind montage | Root-motion montage with a `Motion Warping` notify-state window (target name `Stance`). Call `AddOrUpdateWarpTargetFromLocationAndRotation` **before** `Play Montage`. The character needs a `MotionWarpingComponent` |
| Aim loop | Idle animation, head off the cue line | Looping montage section plus Control Rig head/spine aim at a point on the cue line |
| Stroke | Montage timing decides contact | Gameplay stroke curve. Montage play rate scaled to the stroke duration. IK absorbs the rest |
| Contact | `AnimNotify_Strike` → AddImpulse | Contact event from the gameplay curve (sub-step accurate). Branching Point notify only for presentation |
| Throttling | Shooter under URO/Budget, `OnlyTickPoseWhenRendered` | Shooter exempt, `VisibilityBasedAnimTickOption = AlwaysTickPose` (use `AlwaysTickPoseAndRefreshBones` if anything is socket-attached while off-screen) |
| Left-handers | Duplicate animations | Mirror Data Table plus the `Mirror` node (or mirrored database entries) |

Full recipe with Control Rig inputs, FBIK settings and bridge variants: [references/billiards-shot-animation.md](references/billiards-shot-animation.md). Read it before you implement stance, aim or stroke.

## AnimBP checklist

- [ ] Graph order: Locomotion → Linked Anim Layer (context) → `Slot FullBody` → `Layered blend per bone` + `Slot UpperBody` → additive slot → look-at → Control Rig (shot IK) → foot IK → Output.
- [ ] The *Allow Multi Threaded Animation Update* project setting and the per-class `Use Multi Threaded Animation Update` are on. No game-object access in thread-safe functions, and no compiler warnings.
- [ ] Context switches (table, seated, bar) use `Link Anim Class Layers` and run only on change. Calling it per frame reinitializes the instances.
- [ ] Targets reach Control Rig in **component space** and are computed in the thread-safe update.
- [ ] Every IK or Control Rig node has an `LOD Threshold`. NPCs have no FBIK.
- [ ] Shot, idle and reaction selection is a Chooser table, not nested `Select` or branches.
- [ ] Root Motion Mode is `Root Motion from Montages Only` unless you have a single-player reason for anything else.

Details and the state machine vs MM vs Chooser decision: [references/animbp-architecture.md](references/animbp-architecture.md). Read it when you set up or refactor an AnimBP or copy patterns from GASP or Lyra.

## Montage and notify checklist

- [ ] The montage slot name exactly matches an AnimGraph `Slot` node (e.g. `DefaultGroup.FullBody`).
- [ ] `Montage_Play` returns > 0. If it returns 0, the mesh has no anim instance or the montage is invalid.
- [ ] `OnMontageBlendingOut`, `OnMontageEnded` and `bInterrupted` are handled. A timeout fallback covers "never ended" (interrupted by another montage in the same group).
- [ ] Section jumps and gameplay-relevant notifies use **Branching Point**. Spans use `AnimNotifyState`. High play rates and early blend-outs skip Queued notifies.
- [ ] Off-screen opponents use at least `OnlyTickMontagesWhenNotRendered`, otherwise their montages freeze.
- [ ] Loop sections (AimLoop) point to themselves. Leave the montage via `Montage_JumpToSection` or `Montage_SetNextSection`, not `Stop` (which pops).

## Retargeting and MetaHuman checklist

- [ ] One IK Rig per skeleton. The retarget root is the pelvis. Chains come from Auto Retarget Chains and are checked by hand for fingers and the spine count.
- [ ] Retarget pose fixed with Auto Align, with the source in T-pose and the target in A-pose.
- [ ] Animations are baked offline for shipping. Runtime `Retarget Pose From Mesh` costs CPU every frame, and its Run IK Rig/FBIK step costs the most.
- [ ] MetaHumans are assembled with `UE Optimized` (High/Medium/Low, 2K textures max), not `UE Cine` (up to 8K). Autorig and texture synthesis need Epic's cloud services.
- [ ] `LODSync`: `Forced LOD` for distant spectators. Groom LOD geometry type set to Cards beyond LOD0. Neck correctives disabled first (high cost, minimal visual gain).

Full workflow and Mixamo specifics: [references/retargeting-metahuman.md](references/retargeting-metahuman.md). Read it before any import, retarget or MetaHuman quality decision.

## Performance quick reference

Measure with `stat anim`, Unreal Insights, the Rewind Debugger (Animation Insights plugin), `ShowDebug ANIMATION` and `a.VisualizeLODs 1`.

| Lever | Setting / CVar |
|---|---|
| Worker-thread update/eval | `a.ParallelAnimUpdate`, `a.ParallelAnimEvaluation` (both on by default; set to 0 only to A/B test) |
| URO | Mesh: `Enable Update Rate Optimizations`. `a.URO.Enable`, `a.URO.Draw 1`, `a.URO.ForceAnimRate N`, `a.URO.ForceInterpolation 1` |
| Budget Allocator | Plugin. Component Class `SkeletalMeshComponentBudgeted`. `a.Budget.Enabled 1`, `a.Budget.BudgetMs`, `a.Budget.Debug.Enabled 1` (5.8 added more `a.Budget.*` CVars; use autocomplete) |
| Off-screen | `VisibilityBasedAnimTickOption`: `OnlyTickPoseWhenRendered` for ambient NPCs |
| Modular parts | Leader Pose (`SetLeaderPoseComponent`), not one AnimBP per part |

Tiers, budgets and interactions: [references/performance.md](references/performance.md). Read it when animation shows up in a profile or when you plan NPC counts.

## Symptom → cause → fix (most common)

| Symptom | Cause | Fix |
|---|---|---|
| Montage plays, mesh unchanged | Missing or mismatched `Slot` node, or wrong mesh | Add the slot before IK and play on the body mesh |
| T-pose or twisted limbs after retarget | Unmapped chain, retarget pose mismatch, wrong target skeleton | Auto Retarget Chains → Auto Align → check the chain map |
| Feet slide in walk or stop | Play rate does not match capsule speed, or leg proportions differ | Stride warping or distance matching, the retargeter speed-planting setup |
| Mesh walks off the capsule | Mixamo clip without a root, or root motion off | `Generate From Target Pelvis`, enable root motion |
| Strike late or missing | Notify-driven impulse on a throttled mesh | Gameplay-driven contact, exempt the shooter |
| Hands drift from the cue on a far camera | IK LOD Threshold or URO interpolation | Raise the threshold and disable URO on the shooter |
| Opponent frozen when off-screen, then pops | `OnlyTickPoseWhenRendered` | `AlwaysTickPose` while it is the active shooter |
| Thread-safe function never runs or data is stale | Multithreaded update off, or values read directly instead of through Property Access | Turn the settings on and use Property Access. Expect a one-frame latency |

More rows (MetaHuman, Control Rig, Motion Matching, Motion Warping): [references/troubleshooting.md](references/troubleshooting.md).

## References

- [references/animbp-architecture.md](references/animbp-architecture.md): AnimBP layout traps, thread safety, linked layers, MM vs state machine vs Chooser, what to copy from GASP and Lyra.
- [references/billiards-shot-animation.md](references/billiards-shot-animation.md): stance solve, Motion Warping, Control Rig/FBIK for cue and bridge, stroke sync.
- [references/retargeting-metahuman.md](references/retargeting-metahuman.md): retarget workflow, Mixamo, MetaHuman assembly, LODs, grooms, facial animation.
- [references/performance.md](references/performance.md): CVars, URO vs Budget Allocator, tick options, tier table.
- [references/troubleshooting.md](references/troubleshooting.md): extended symptom → cause → fix.
- [references/sources.md](references/sources.md): URLs and what each one supports (accessed 2026-10-06).
