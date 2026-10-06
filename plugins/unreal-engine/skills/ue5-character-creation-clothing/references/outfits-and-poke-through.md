# Outfits, fitting and poke-through (UE 5.8)

Contents: modular methods (Leader Pose, Copy Pose, Merge) · MetaHuman wardrobe and parametric outfits · fitting third-party clothes · hiding the body · LODs · Mutable · grooms and hats.

---

## 1. Modular skeletal meshes

Epic's comparison (Working with Modular Characters):

| Method | Setup | Game thread | Render thread | Physics | Morph targets |
|---|---|---|---|---|---|
| Leader Pose Component | Min | Min | High | No | Yes |
| Copy Pose From Mesh | Medium | High | High | AnimDynamics or RigidBody | Yes |
| Skeletal Mesh Merge | High | Medium | Low | Yes | No |

### Leader Pose (default for heroes)

```cpp
// Character.h
UPROPERTY(VisibleAnywhere) TObjectPtr<USkeletalMeshComponent> Torso;
UPROPERTY(VisibleAnywhere) TObjectPtr<USkeletalMeshComponent> Legs;

// Character.cpp (constructor)
Torso = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Torso"));
Torso->SetupAttachment(GetMesh());
Legs  = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Legs"));
Legs->SetupAttachment(GetMesh());

// After assigning or swapping meshes (BeginPlay, OnRep_Outfit, ...)
void AMyCharacter::ApplyOutfit(USkeletalMesh* TorsoMesh, USkeletalMesh* LegsMesh)
{
    Torso->SetSkeletalMeshAsset(TorsoMesh);
    Legs->SetSkeletalMeshAsset(LegsMesh);
    for (USkeletalMeshComponent* Piece : {Torso.Get(), Legs.Get()})
    {
        Piece->SetLeaderPoseComponent(GetMesh(), /*bForceUpdate*/ true);
        Piece->bUseBoundsFromLeaderPoseComponent = true;
    }
}
```

Traps:
- **Bone mapping is by name.** Follower bones missing from the leader (or stripped by the leader's LOD bone reduction) do not follow, so vertices stretch or sit in the bind pose. Keep the garment's skeleton a **subset** of the body's. Never strip bones in a body LOD that a garment LOD still weights to.
- **Followers run no AnimBP.** Clear the follower's *Anim Class*. An AnimBP left on a follower costs CPU and fights the leader.
- **Morph targets:** the leader's anim curves propagate to followers whose morph targets have the same names. Calling `SetMorphTarget` directly on a follower was historically overridden by Leader Pose (UE-22271). Drive garment morphs from curves on the leader.
- **Bounds and culling:** without `bUseBoundsFromLeaderPoseComponent`, a follower can cull or shadow-pop at the screen edge. Bounds come from the body's Physics Asset, so it must enclose the whole silhouette, including skirts and coats. *Bounds Scale* is the last resort.
- **Physics on followers:** none. A follower's own Physics Asset does not simulate. Use cloth (Chaos Cloth Component) or Copy Pose for physics.
- **Leader is a PoseableMeshComponent:** an access-violation crash when updating curves and morphs was fixed in 5.5 (UE-217626). Avoid that setup on older branches.

### Copy Pose From Mesh

- Add an AnimBP to the piece with the **Copy Pose From Mesh** node. Set *Source Mesh Component*, or tick *Use Attached Parent*, plus *Copy Curves* if the piece has morphs.
- The source must tick first, or you copy last frame's pose (1-frame lag, visible as sleeves trailing hands on the cue stroke). Attach the piece to the body (the parent ticks first) or add a tick prerequisite.
- Use it only for pieces that need their own RigidBody/AnimDynamics (a dangling chain or a loose tie). Everything else uses Leader Pose.

### Skeletal Mesh Merge (`SkeletalMerging` plugin, runtime)

```cpp
// Build.cs: PrivateDependencyModuleNames.Add("SkeletalMerging");
#include "SkeletalMergingLibrary.h"

FSkeletalMeshMergeParams P;
P.MeshesToMerge = { BodyMesh, ShirtMesh, PantsMesh, ShoesMesh };
P.Skeleton = BodyMesh->GetSkeleton();   // leave null to generate one
P.StripTopLODS = 0;                     // e.g. 1 for distant NPCs
USkeletalMesh* Merged = USkeletalMergingLibrary::MergeMeshes(P);
if (Merged) { GetMesh()->SetSkeletalMeshAsset(Merged); }
```

- Morph targets are lost. Use it for NPCs without facial animation, or keep the head separate (head Leader-Posed to the merged body).
- Merged sections keep their materials. Use `MeshSectionMappings` and `UVTransformsPerMesh` to combine sections into one atlas material for the best draw-call savings.
- All inputs need the same skeleton (or a compatible one), the same LOD count and compatible LOD screen sizes.
- Cache merged meshes per outfit combination. Merging every spawn causes hitches.
- Assume cloth data and per-piece physics assets do not survive a merge *(not verified, so test)*. Keep simulated garments as separate Chaos Cloth Components.

---

## 2. MetaHuman clothing (5.6+)

Two kinds of clothing:

| Kind | Asset | Fits | Sim |
|---|---|---|---|
| Skeletal (fixed) | Skeletal Mesh skinned to the MetaHuman body (+ optional `WI_*` Wardrobe Item) | One body shape | Your own Cloth Asset/legacy cloth |
| Parametric (resizable) | **Chaos Outfit Asset** containing one or more Cloth Assets, made from several **source bodies** | Warped to the target body. Picks the closest source size | Stripped by assembly in 5.8 (see below) |

**Authoring flow (Epic "Creating Parametric Clothing for MetaHuman"):**
1. Copy the **Combined Skel Mesh** and skeleton (via *Export Combined Skel Mesh*) into an `Outfits` folder. Export it to the DCC as FBX for fitting.
2. Create and configure the **Chaos Cloth Asset** (skin weights transferred from the body, sim regions painted).
3. Create the **Outfit Asset** and a **MetaHuman Creator Wardrobe Item**.
4. Test it: new MetaHuman Character → *Hair & Clothing* → *Outfit Clothing* → drag the outfit in → **Wear** → change the body in *Head & Body* and watch it switch source sizes. If a body type fits badly, export that body and add it as a new source size.
5. Retarget a Manny animation onto the MetaHuman and test the motion range.

**Body Hidden Face Map** (wardrobe item → *Pipeline > Editor Pipeline > Outfit > Body Hidden Face Map*):
- A texture in the **MetaHuman body UV layout**: white = visible, black = removed. Paint it from the body UVs in your DCC.
- Applied **at assembly**: removed triangles are gone from the assembled body (and it renders faster). To change it, edit the mask and re-assemble.
- Only one mask per character (5.6). When combining a shirt with gloves, author a merged mask.
- Do not make it fully black. Reported bug: the assembled body comes back fully visible.

**Making simulated MetaHuman clothing work in a game (workaround for the stripped sim):**
- Treat Creator outfits as a **fitting tool**. After assembly you have a resized, fixed garment for *this* character's body.
- Build a Cloth Asset from that resized garment (Dataflow: import → transfer weights from the assembled body → paint MaxDistance on the loose parts → physics asset → terminal). Add it as a **Chaos Cloth Component** under the body with Leader Pose, and remove the static garment mesh, or keep it as the non-simulated LOD.
- Third-party products exist that keep Chaos Cloth through assembly (for example a "MetaHuman Cloth Assembly" plugin on Fab). These are unverified, so evaluate them before relying on them.

**LODs:** the assembled MetaHuman uses **LODSync**. In *Components to Sync*, Body and Face are *Drive* by default. Add each extra garment, groom and cloth component so it switches with the body. Use *Forced LOD* / *Min LOD* for seated spectators (cost details in `ue5-animation-characters`).

---

## 3. Fitting third-party clothes to MetaHuman or Manny

**Route A: DCC (most control)**
1. Export the target body: MetaHuman *Combined Skel Mesh* FBX, or `SK_Mannequin`.
2. Fit the garment to the body in the bind (A-)pose. Fix the scale first (cm).
3. Transfer weights from the body (Blender Data Transfer / Maya Copy Skin Weights), then smooth. Lock collar, cuff and waistband weights to match the body exactly.
4. Check extreme poses with real clips (bridge stance, full stroke, sitting). Fix with offset and weights, not by inflating the mesh.
5. Build LODs that match the body's LOD count, or generate them in UE with the same screen sizes.
6. Export the garment and the *same* armature only. Import with *Skeleton* = the body skeleton.

**Route B: in-engine**
- **Skeletal Mesh Editing Tools** plugin (*Edit > Plugins*, Animation category): skin weight painting and bone editing in the Skeletal Mesh editor, including transferring weights from a source skeletal mesh.
- Static → skeletal garment: Epic's *Create an Action Utility for Transferring Skin Weights* uses the Geometry Script **TransferBoneWeightsFromMesh** (source skeletal mesh → target static mesh → new skeletal mesh). It assumes the meshes are aligned.
- Cloth Assets: Dataflow **TransferSkinWeights** (body → sim and render mesh). This is the quickest route to "follower clothing", even with no simulation.

Good transfer requires aligned meshes, the same bind pose and units, and the garment near the body surface. Loose garments (long coat, skirt) need manual weight cleanup or cloth.

---

## 4. Hiding the body under clothing

| Method | When | Cost / trap |
|---|---|---|
| Delete hidden triangles per outfit variant (DCC) | Fixed outfits, NPCs | Needs one body variant per outfit, or a modular body (head/hands/torso/legs) |
| MetaHuman Body Hidden Face Map | MetaHuman wardrobe | Assembly-time, one mask (see above) |
| CC **Delete Hidden Mesh** on export | Reallusion characters | One-way. Keep the CC source |
| Mutable *Remove Mesh Blocks* / *Clip Mesh With Mesh* | Runtime combinations | A 5.8 forum report shows artifacts when combined with Mesh Reshape on the same component |
| Skin material opacity mask (Masked) | Last resort, runtime toggle | Masked skin costs more, can't use some skin features, and changes shadows. Avoid on hero faces |
| Modular body parts hidden by component | Gloves, boots | Seams at the boundaries. Hide the part and its LODs together |

`HideBoneByName` collapses the vertices weighted to a bone (it scales them to zero). It's useful for hiding a whole limb segment under a cast or prosthetic, but not for cloth-shaped regions.

---

## 5. Clothing LODs

- Same LOD count as the body and **same screen sizes**. Otherwise garment and body switch at different distances, giving gaps or poke-through at mid-range.
- LOD bone reduction (*Bones to Remove*): apply the same list to body and garments. A garment weighted to a removed bone stretches or freezes.
- Cloth: simulate only at LOD0 (maybe LOD1) for heroes. Disabled LODs fall back to skinned. Make sure the skinned fallback looks acceptable, or the cloth will pop when it switches.
- Grooms: strands at LOD0 for heroes, cards below, meshes at the far LODs. Background NPCs get cards or meshes only.

---

## 6. Mutable (Customizable Objects)

- Status: the 5.8 release notes say Mutable reached production readiness ("dataless" COs evaluate parameters at runtime for faster iteration and patching). Some indexes still list the plugin as Beta, so check *Edit > Plugins*.
- Use it when players choose among many combinations (a lobby character creator). For a fixed cast of characters, Leader Pose or merged meshes are simpler.
- **Cloth:** Mutable does **not** support Panel Cloth / Cloth Asset. Legacy skeletal-mesh cloth is the recommended route with Mutable.
- Physics: by default the generated mesh uses the reference mesh's Physics Asset. For parts with very different proportions, enable *Object Properties > Compile Options > Enable Physics Asset Merging*.
- Body hiding: *Remove Mesh Blocks* (UV blocks) or *Clip Mesh With Mesh*. Test them combined with reshape/morph modifiers.
- 5.8 forum reports include crashes in Mutable mesh updates. Pin a hotfix version and test packaged builds.

---

## 7. Hair (grooms), hats and helmets

**Binding**
- Right-click the Groom → **Create Binding**. *Target Skeletal Mesh* (required) = the exact head/face or body mesh it renders on. *Source Skeletal Mesh* (optional) = the mesh the groom was authored on. It may differ in topology but **must share UVs**.
- *Num Interpolation Points* (≤ ~100) is used with *RBF Interpolation* (Groom editor > Interpolation) to keep the shape under large deformations.
- *Matching Section* restricts the transfer to one mesh section.
- Rebuild the binding whenever the target mesh changes (re-assembled MetaHuman, edited face).
- Requirements: *Support Compute Skin Cache* (Project Settings > Rendering) on, and the component's Skin Cache Usage enabled. Without them grooms can vanish after binding.
- LOD: with strands, `SetForcedLOD` on the groom doesn't sync with the binding. Switch the **skeletal mesh** LOD and let the groom follow.

**Geometry types:** *Strands* (skinning, RBF, sim; expensive), *Cards* (skinning, RBF, sim), *Meshes* (RBF only). One LOD may hold strands *and* cards for scalability fallback.

**Hats and helmets** (practice, no Epic doc found):
- Make a hat-specific hair variant: a flattened or short groom, or cards authored under the hat. Swap it in when the hat goes on. The groom solver will not push strands under a rigid hat convincingly.
- Hide the groom groups that would show through. Keep fringe/sideburn groups outside the hat.
- A brim or helmet needs a matching body-hidden-faces or scalp treatment only if the hat is open.
- Hair sim collides with the Physics Asset (collision radius per strand). Add a head-capsule extension for the hat if the strands simulate.
