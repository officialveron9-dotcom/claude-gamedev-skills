# Symptom → cause → fix (characters and clothing, UE 5.8)

Work top to bottom inside each group. The most common causes come first. Animation-only symptoms (foot sliding, bad retarget pose, montages not playing) are in `ue5-animation-characters`.

## Import and skeleton

| Symptom | Likely cause | Fix |
|---|---|---|
| Mesh 100× too big or too small, or root bone scale 100 | DCC units: Blender without *Apply Scalings: FBX All* / unit scale 0.01. Maya in meters | Re-export in cm or with unit conversion. Don't fix it with actor scale (it breaks physics, cloth and IK) |
| Mesh lies on its back or faces sideways | Axis conversion. Daz root rotated 90°. Interchange front-axis handling | Fix the root orientation in the DCC. Try the legacy importer's *Force Front XAxis* / *Convert Scene*. For Daz, use the bridge's root options |
| Imports as a T-pose "exploded" mesh, or limbs twisted | Bone axes changed on export. *Use T0 As Ref Pose* baked an anim frame in. Twist bones (Daz) | Default bone axes (Y primary, X secondary). T0 off. Daz: *Fix Twist Bones* |
| New skeleton created for every garment | *Skeleton* left empty on import | Re-import with the body skeleton selected, or set Compatible Skeletons. Delete the duplicates |
| "Mesh contains root bone as root but animation doesn't contain the root track" | Mixamo clips imported onto a skeleton that later gained a root | One skeleton for all clips. Re-import consistently, or retarget |
| Extra "Armature" bone at the top | Blender armature object exported as a bone | Name the armature `root`, or match the target hierarchy before export |
| Morph targets missing | *Import Morph Targets* off. Morphs dropped by the bridge | Enable it and re-import. Check the morph count in the mesh editor |
| Crash importing a CC character | Morphs + *Use T0 As Ref Pose* together. Auto Setup version mismatch | T0 off. Use the Auto Setup build for your engine version |
| Faceted or shading seams on clothing | Normals recomputed. Wrong tangent space | *Normal Import Method* = Import Normals (and Tangents) |
| Daz to Unreal plugin won't compile on 5.7/5.8 | Bridge not updated for the engine | Community fork, or a manual FBX + IK Retargeter path |

## Clothing does not follow / deforms wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| Garment frozen in A/T-pose while the body animates | Leader Pose not set, set before the mesh was assigned, or lost after swapping meshes | Call `SetLeaderPoseComponent(Body, true)` after every `SetSkeletalMeshAsset`. Clear the follower's Anim Class |
| Garment lags one frame behind the hands | Copy Pose From Mesh reading before the source ticked | Attach to the body (parent ticks first) or add a tick prerequisite. Prefer Leader Pose |
| Vertices stretch toward the world origin (wrists, fingers) | Garment weighted to bones the leader lacks, or that the leader's current LOD removed. Skeleton mismatch | Re-skin to the body skeleton. Same *Bones to Remove* per LOD on body and garments. Check that MetaHuman wardrobe items match the body type |
| Garment correct at LOD0, broken at distance | Garment LOD count or screen sizes differ from the body's. Not in LODSync | Match LODs. Add it to LODSync *Components to Sync* |
| Garment morphs (e.g. sleeve roll) don't respond | `SetMorphTarget` called on the follower (overridden). Curve names differ | Drive morphs via curves on the leader with matching names |
| Merged mesh lost facial animation or morphs | Skeletal Mesh Merge drops morph targets | Keep the head separate (Leader Pose on the merged body) |
| Clothing stretched downward after a validation "Fix-up" (UEFN) | 5.8 known issue: the fix-up corrupts MetaHuman clothing | Don't run that fix-up |
| MetaHuman outfit fits in Creator but clips on the final body | Body edited after fitting. Fixed outfit on a parametric body | Re-wear and re-assemble. Use a compatibility body for fixed clothing. Add source sizes to the parametric outfit |

## Poke-through and clipping

| Symptom | Likely cause | Fix |
|---|---|---|
| Skin through the shirt at shoulders/elbows in the stroke pose | Body correctives deform the body but not the garment. Weights differ at the joints. Garment too tight in the extreme pose | Hidden faces under opaque cloth. Copy body weights at the joints. Add garment correctives/morphs. Refit with real poses |
| Skin through at hips/armpits on a custom MetaHuman body | Fixed-size clothing on a reshaped body | Parametric outfit, refit, or compatibility body |
| Fingers through gloves | Body hands not hidden | Body Hidden Face Map for the hands. CC Delete Hidden Mesh |
| Hidden body faces still visible after assembly | Mask fully black (bug). Mask set after assembly. Two wardrobe items with separate masks | At least some white. Set it before assembly. Merge masks into one |
| Layered clothes clip each other (jacket over shirt) | Both layers weighted independently, no offset | Inner layer weights copied from the outer layer near the overlap. Delete hidden inner faces. Shrink the inner layer |
| Hair through hat | Groom not authored for a hat | Hat-specific groom/cards variant. Hide groups. Swap on equip |
| Skin flickers through thin cloth only at distance | Lower LODs of body and garment reduced independently | Remove the body faces in all LODs. Match LOD reduction settings |

## Cloth simulation

| Symptom | Likely cause | Fix |
|---|---|---|
| Explodes on spawn, respawn or a cut | No teleport/reset. Colliders start inside the cloth | Teleport/reset API. Shrink colliders. Garment starts outside the body |
| Jitters while standing still | Too few iterations/substeps. Self-collision thickness too large. Far from the origin | More iterations/substeps. Lower thickness. Local-space sim |
| Falls through or sinks into the body | No physics bodies there. Thickness 0. No CCD. Backstop off. Bodies simulating with soft constraints | Add capsules (tapered). Thickness > 0. CCD. Backstop. Kinematic collider for tight fits |
| Long stretched sleeves or skirt | No tethers. Low iterations. MaxDistance too large | Long Range Attachment. More iterations. Paint lower MaxDistance |
| Cloth trails far behind on fast turns | Velocity scales at 1 | Lower angular velocity / `FictitiousAngularScale`, clamp `MaxVelocityScale` |
| Cloth stiff and frozen | MaxDistance map 0 everywhere. Sim disabled on this LOD. Simulation suspended | Paint the sim region. Check LOD sim flags and `SetEnableSimulation` |
| MetaHuman parametric outfit lost its simulation | Assembly strips the sim mesh (5.8 report) | Rebuild a Cloth Asset on the assembled body and add a Chaos Cloth Component |
| Resized cloth asset deforms wrong where simulated | `ApplyResizing` baked into the Cloth Asset (5.8 report) | Don't bake the resize into a simulated asset. Build sim from the final resized mesh |
| Cloth pops when the LOD changes | Sim disabled on the next LOD, so it snaps to skinned | Make the skinned fallback match. Switch at a larger distance. Keep sim through LOD1 for heroes |
| Cloth ignores wind | Aerodynamics off (drag/lift 0) | `SimulationAerodynamicsConfig`. Use `SetWind` (not `SetAerodynamics`) |
| Cloth broken in Movie Render Queue | Time-step smoothing vs temporal samples | `p.ChaosCloth.UseTimeStepSmoothing 0` |
| Mutable character's cloth doesn't work | Cloth Asset not supported by Mutable | Use legacy skeletal-mesh cloth in Mutable parts |

## Hair and grooms

| Symptom | Likely cause | Fix |
|---|---|---|
| Hair floats above the head or is offset | Binding against a different or edited mesh. 2-unit Z offset from a Maya round-trip. Mismatched LOD | Rebuild the binding against the exact mesh. Zero the offset. Switch the skeletal mesh LOD, not the groom |
| Groom disappears after binding | Skin Cache off | *Support Compute Skin Cache* on (restart). Component Skin Cache Usage = Enabled |
| Binding fails: target "could be missing UVs" | Target mesh lacks the UVs the transfer expects | Use the correct mesh. Source and target must share UV layout |
| Hair detaches or clips on medium-quality MetaHumans | 5.8 known issue (Long Messy Hair on Medium) | Different quality level or groom |
| Hair shape collapses under big deformations | RBF interpolation off | Enable RBF and set *Num Interpolation Points* (≤ ~100) |
| Grooms reset or lose materials after `.mhpkg` import | 5.8 known issue: missing parent materials for non-bundled grooms/clothes | Migrate parent materials and re-assign them |

## Rendering, shadows, culling

| Symptom | Likely cause | Fix |
|---|---|---|
| Garment disappears at screen edges or up close | Follower bounds | `bUseBoundsFromLeaderPoseComponent`. Physics Asset covers the silhouette |
| Whole character pops out at some camera angles | Physics Asset root body too small (bounds come from it) | Enlarge or fix the bodies. *Bounds Scale* as a last resort |
| Clothing shadow flickers or missing | Opacity/masked material without shadow. Capsule shadows from a wrong Shadow Physics Asset | Check the material shadow settings (RL opacity materials reportedly cast no shadow). Fix the Shadow Physics Asset |
| Clothing renders world-grid after migration | Parent materials missing | Migrate the parent materials (MetaHuman `.mhpkg` known issue) |

## Performance

| Symptom | Likely cause | Fix |
|---|---|---|
| Render-thread cost grows with each NPC | Many Leader Pose followers × material sections | Merge meshes for NPCs, atlas the materials, reduce sections |
| Game-thread spikes when outfits change | Runtime `MergeMeshes` per spawn. Mutable updates | Cache merged meshes. Pre-generate Mutable instances. Spread the work out |
| GPU cost from hair | Strands on everyone | Cards/meshes for NPCs. Strands only for heroes at LOD0 |
| CPU cost from cloth | Simulated cloth on every character | Disable on LOD1+, off-screen and NPCs. Use a lower-resolution sim mesh |
| Memory spike | UE Cine MetaHumans. 4K–8K clothing textures | UE Optimized. 2K heroes, 1K NPCs (starting points) |
