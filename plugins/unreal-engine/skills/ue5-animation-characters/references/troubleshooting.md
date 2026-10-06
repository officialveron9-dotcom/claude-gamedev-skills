# Animation troubleshooting: symptom → cause → fix

## Montages, slots, notifies

| Symptom | Cause | Fix |
|---|---|---|
| `Play Montage` succeeds, mesh does not move | No `Slot` node with the montage's slot name in the AnimGraph | Add `Slot 'FullBody'` (or match the name) between locomotion and IK |
| Montage visible only on the upper body or only on the legs | The slot is in a `Layered blend per bone` branch, or the montage uses the wrong slot | Use a full-body slot for stance montages |
| Montage plays on the body but clothing stays in idle | Clothing parts are not following | `SetLeaderPoseComponent(Body)` on the parts, or have the MetaHuman Blueprint wire it |
| Montage plays, then immediately blends out | Another montage in the same slot group interrupted it, or a stop/blend-out call ran elsewhere | Check for interrupts in `OnMontageEnded(bInterrupted)` and use separate groups for parallel layers |
| `Montage_Play` returns 0 | Mesh has no anim instance, montage skeleton mismatch, or a null montage | Assign the AnimBP and use a compatible skeleton (or compatible skeletons list) |
| Notify fires sometimes | Queued notify at high play rate or near the blend-out, or the mesh is throttled | Use a Branching Point, move it earlier, raise the trigger weight threshold handling, exempt the mesh from throttling |
| Notify never fires off-screen | `OnlyTickPoseWhenRendered` | `OnlyTickMontagesWhenNotRendered` or `AlwaysTickPose` |
| Section loop never exits | The loop section links to itself and nobody jumps out | `Montage_JumpToSection` or `Montage_SetNextSection` from game code on input or event |
| Notify state `End` missing | The montage was interrupted, so the state ended early | Handle cleanup in `OnMontageEnded` as well as in NotifyEnd |

## Root motion, Motion Warping, movement

| Symptom | Cause | Fix |
|---|---|---|
| Mesh walks away and the capsule snaps back | Root motion not enabled on the sequence, or the AnimBP root motion mode ignores it | Enable root motion on the asset and use montages under `Root Motion from Montages Only` |
| Mixamo clip: capsule never moves | No root bone (the motion is on the hips) | Retarget with the Root Motion op `Generate From Target Pelvis`, or add a root in the DCC |
| Motion Warping has no effect | Warp target name mismatch, target set after `Play Montage`, missing `MotionWarpingComponent`, or no root motion in the window | Set the target first with matching names and use root-motion clips |
| Character slides back from the table at the end of the warp | Capsule collision with the table pushes it out | Shrink the capsule or ignore the table channel during the window |
| AI `MoveTo` aborted when the montage starts | Root motion overrides path following | Finish the move first, then play the montage |
| Root motion jitters for remote players | Not using montage root motion, or the montage only plays locally | See `ue5-multiplayer`. Use `Root Motion from Montages Only` and play on the server |
| Foot sliding while turning in place (MM) | Capsule rotation does not match the animated root rotation | `Offset Root Bone` (Experimental) or turn-in-place clips, orientation warping |
| Feet slide when stopping at the stance point | Time-based stop clip | `DistanceMatchToTarget` toward the stance point |

## IK, Control Rig

| Symptom | Cause | Fix |
|---|---|---|
| Hands fly off when the character turns | World-space targets fed to the rig | Convert to component space on the game thread |
| Whole body slides toward the hand targets | FBIK feet not pinned | Add foot effectors at their animated transforms with high strength |
| Elbow or knee flips | No pole/preferred angle, or limits missing | Set preferred angles and limits in FBIK bone settings, or a pole vector |
| IK fine up close, broken at distance | Node `LOD Threshold` reached | Raise it for the shooter and accept the cost. NPCs use Two Bone IK |
| IK Rig node has no goal pins | Goals not exposed | IK Rig asset → goal → *Expose Position/Rotation* |
| Control Rig node has no input pins | Rig variables not public, or not enabled as pins | Make the rig variables public (eye icon) and compile, then enable them as pins in the AnimBP Control Rig node's Details (Input section) |
| Montage overrides IK during the shot | Slot is after Control Rig | Move the slot before Control Rig |
| Hands lag one frame behind the cue | Targets read through Property Access with batch latency, or the cue moves after anim update | Move the cue before the anim update (tick prerequisites or tick group). Accept one frame for NPCs |

## Retargeting

| Symptom | Cause | Fix |
|---|---|---|
| T-pose result | Chains unmapped, wrong target IK Rig, or source and target swapped | Auto Retarget Chains and check the mapping and the asset assignment |
| Arms raised or crossed | Retarget pose mismatch (T vs A) | Auto Align the retarget pose |
| Character sinks into or floats above the floor | Pelvis height scaling or root height source | Pelvis Motion op settings. Root Motion op root height `Copy Height From Source` vs target |
| Fingers clawed | Finger chains unmapped, or there are twist bones in the chains | Map them or exclude them |
| Shorter character's pelvis bobs too little | 5.8 option to prevent damping of vertical pelvis motion | Enable it in the Pelvis op (5.8) |
| Retargeting is slow at runtime | Runtime `Retarget Pose From Mesh` with FBIK | Bake offline, or use cheaper limb solvers and disable the IK op at distance |
| Auto Generate Retargeter fails | Skeleton type not recognized | Build the IK Rigs and retargeter by hand |

## Motion Matching

| Symptom | Cause | Fix |
|---|---|---|
| Node outputs a reference pose | Database empty, schema skeleton mismatch, or the database is still indexing | Check database assets and the schema, then let indexing finish (watch the editor notifications) |
| Constant pops | Too few clips, bad channel weights, blend time too short | Inspect costs in the Rewind Debugger, tune weights, add coverage |
| Character ignores input direction | Trajectory not fed or not in component space | Copy the current GASP trajectory generation and wire `Pose History` |
| Old tutorial nodes missing | API changed after 5.4 (trajectory component pattern) | Follow the current GASP version |

## MetaHuman

| Symptom | Cause | Fix |
|---|---|---|
| Hair disappears or turns into cards up close | Groom LOD set to cards at LOD0, or Forced LOD | Strands at LOD0 for heroes only |
| Face frozen on NPCs | Facial Animation LOD Threshold below the current LOD | Expected for background NPCs. Raise it for near ones |
| Clothing tears at distance | Outfit lacks LODs that match LODSync | Generate clothing LODs or force a LOD |
| GPU cost spikes with several MetaHumans in frame | Strand grooms plus Cine assemblies | Re-assemble with UE Optimized, use cards, disable groom simulation |
| Assembled MetaHuman renders wrong in a new project | Groom or RigLogic plugins off, or skin cache unsupported | Enable the plugins and *Support Compute Skin Cache*, then restart |
| Wrong LOD under dynamic resolution or split-screen (Nanite) | Bug fixed in 5.8.3 | Update the hotfix |

## Performance

| Symptom | Cause | Fix |
|---|---|---|
| Large game-thread time in AnimBP update | Event Graph logic or Blueprint VM nodes in the AnimGraph | Thread-safe update with Property Access, `Warn About Blueprint Usage` |
| Background NPCs cost as much as heroes | No URO, budget or tick option, full LODs | Apply the tier plan in performance.md |
| Budgeted NPC animation looks choppy | Allocator interpolation and tick rates under pressure | Raise `a.Budget.BudgetMs`, tune `a.Budget.InterpolationMaxRate`, set significance properly |
| Gameplay reads wrong curve values on some NPCs | URO skipping evaluations | Disable URO on those meshes |
