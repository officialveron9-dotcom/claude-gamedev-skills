# Character sources and pipelines (UE 5.8)

Contents: MetaHuman · Fab · Reallusion CC4/CC5 · Daz · Mixamo · Blender/custom · Marvelous Designer/CLO · per-source import checklists.

Retargeting animations between these skeletons (IK Rig, IK Retargeter, root motion) is covered in `ue5-animation-characters`. Here we only cover getting the *mesh, skeleton and clothes* in cleanly.

---

## MetaHuman (5.6+ in-editor Creator)

**Creation path**
- Right-click in the Content Browser → *MetaHuman > MetaHuman Character* → double-click to open **MetaHuman Creator** inside the editor. The web Creator and Quixel Bridge download path are legacy.
- Tools: *Head & Body* (presets, sliders, parametric body), *Hair & Clothing* (grooms, wardrobe; the **Outfit Clothing** section is at the bottom). To apply a wardrobe item, drag it in, then double-click it or click **Wear**.
- Autorig and texture synthesis call Epic cloud services. Plan for being online and logged in.
- **Assemble** the character with a pipeline. Use **UE Optimized** (High/Medium/Low quality, textures at most 2K) for games. **UE Cine** is for cinematics only (large memory). LOD and performance knobs are in `ue5-animation-characters`.
- Packaging and sharing between projects: `.mhpkg` via the MetaHuman Manager. **5.8 known issue:** an assembly that uses clothing or grooms from *outside* the MetaHuman plugin's bundled content packages into an `.mhpkg` without its parent materials. Clothing then renders with the world-grid material and grooms revert. Re-point the materials after import, or migrate the parent materials too.

**Bodies**
- The parametric body (5.6+) gives near-infinite body shapes. Legacy skeletal clothing was made for the **18 fixed bodies** (3 heights × 3 weights × 2 sexes). Enable them via *Project Settings > Plugins > MetaHuman Character > Show Compatibility Mode Bodies*. Use a fixed body when you need old fixed-size clothing to fit without refitting.
- Changing proportions stretches the body. Fixed-size clothing does **not** follow, so expect clipping at the hips, armpits and groin. Either use parametric (resizable) outfits or refit the garment to the final body.
- 5.8: Mesh to MetaHuman conforms **head and body** from an arbitrary scan or mesh in one workflow.

**Skeleton:** the MetaHuman body skeleton is an extended UE5 Manny skeleton (same core bones). Manny animations transfer via retargeting. Epic recommends retargeting *to Manny* and then playing on the MetaHuman. Clothing must be skinned to the **MetaHuman** body skeleton, not to Manny, if you want twist/corrective bones to drive it.

**License (5.6+):** MetaHumans fall under the standard **Unreal Engine EULA** plus a MetaHuman content addendum. You may use them in other engines and DCCs and sell MetaHuman characters, clothing and animations on Fab. You may **not** use them as training data for generative AI. *(Secondary sources summarising the EULA. Read the addendum before shipping.)*

**Known issues worth knowing (5.6–5.8)**
- Parametric outfit **cloth sim is stripped** when the outfit goes through the wardrobe and assembly, so the garment ends up static (5.8 forum, with an official reply).
- Baking a resize into a Cloth Asset with the Dataflow `ApplyResizing` node corrupted the sim-to-render deformation around simulated regions (5.8 forum).
- *Long Messy Hair* groom detaches and clips through the head on **Medium** quality (5.8 known issues). Use another quality level or groom.
- Clothing on some 5.6 characters stretched at the wrists toward the origin, and forcing LODs did not help (forum, unresolved). Check that garment bones and LOD bone reduction match (see common-issues).
- An all-black Body Hidden Face Map leaves the body fully visible after assembly (forum bug analysis).
- Historic: sending a MetaHuman to Maya added a 2-unit Z offset on the face mesh, so the bound groom floated. Zero the offset before re-exporting.

---

## Fab (Epic marketplace)

**License (Fab Standard License, Epic Content License Agreement):**
- Tiers: **Personal** (buyer under USD 100k gross revenue in the last 12 months) and **Professional** (above that). **Both grant the same rights** and both allow commercial games.
- Standard-licensed assets may be used in **any engine or tool**, *except* items designated **UE-Only Content**, which may be used only with Unreal Engine (and UE-based products such as Twinmotion).
- Never redistribute the source assets (no resale, no public download of the raw files).
- Content marked **NoAI** must not be used in datasets for, development of, or as input to generative AI programs.
- Some listings use Creative Commons instead. Read the listing's license field.

**Before buying a character or outfit, read the listing's technical details:**
- [ ] "Rigged to Epic skeleton: Yes" and "IK bones included: Yes" mean it uses the UE5 Manny/Quinn skeleton. Check **which** Epic skeleton (UE4 Mannequin ≠ UE5 Manny; UE4 needs retargeting).
- [ ] For MetaHuman clothing: "parametric/resizable" (Outfit Asset) vs "skeletal/fixed" (made for specific fixed bodies, e.g. "All MH bodies"). Check that the supported engine version is ≥ yours.
- [ ] Vertex counts per LOD, number of LODs, number of materials (each material section is a draw call), morph targets, texture resolution.
- [ ] Modular (separate head/torso/legs) vs single mesh. Check whether a body mask or hidden-face variants are included.
- [ ] License: Standard vs UE-Only (matters only if you might leave UE) and NoAI.

**After import:** open the skeletal mesh. Check *Skeleton* = your shared skeleton (or use a compatible skeleton), play one of your own animations on it, and check its LOD count against your body.

---

## Reallusion Character Creator 4 / 5

**Skeletons:** CC exports with skeleton mapping for UE4 and UE5. **CC5 HD** characters add about 10 spine/head bones for 1:1 mapping with the UE5 Mannequin and MetaHuman (Reallusion counts: MetaHuman 342 bones, UE5 Mannequin 89, UEFN 88). Bind-pose presets exist for UE4, UE5/MetaHuman and UEFN. Pick the one that matches your target skeleton.

**Export:** *Export > FBX > Clothed Character* → preset for UE5 (Reallusion's docs call the preset item *UE 5 (Skeleton)*). The gear icon sets the target bone structure and bind pose. **Delete Hidden Mesh** removes body faces under clothing (prevents poke-through), but the character can no longer go back into CC. Keep a CC master file.

**Auto Setup plugin (UE side):** it builds materials, skin, eyes, hair and the rig. Version trouble is common:
- *UE Auto Setup All-in-One 2.0* announced support for **UE 5.7** (it integrates the CC Control Rig and Live Link). Reports exist of crashes on import in 5.5.4, 5.6.4 and 5.7.4, and of the character not being recognised in 5.7.2. **5.8 support was not confirmed by this research.** Check Reallusion's download page before upgrading the engine.
- **Morphs + Use T0 As Ref Pose on → crash** in the FBX morph import (Reallusion tracker). Keep T0 off.
- RL opacity materials (e.g. `RL_Standard_Opacity`) reportedly do not cast shadows. Check hair cards and eyelashes.

**License:** exported content needs export rights. For commercial games, Reallusion distinguishes a **Standard** license (outputs for a single character) from an **Extended** license (mass character outputs). Raw content may never be made publicly downloadable.

---

## Daz Studio + Daz to Unreal (DTU)

- **The bridge is open source** (github.com/daz3d/DazToUnreal). The latest seen was v5.7.0.521 (Nov 2025). Compile errors were reported against UE 5.7.x, the Fab listing had not been updated since June 2025, and community forks exist. **Expect to compile the plugin yourself for 5.8, or export FBX manually.**
- Supports Genesis 3, 8/8.1 and 9 (Genesis 9 has IK Rig/retarget support). Genesis 9 has its own skeleton and **always needs retargeting** to Manny/MetaHuman animations.
- Twist bones: enable **Fix Twist Bones** in the Daz export, which adds the skeleton to "Skeletons with Twist Fix" in the UE plugin. On 5.4 users also had to **uncheck "Zero root rotation"** in the bridge settings.
- A root rotated 90° breaks IK Retargeter results (jumps lying along the floor). Fix the root orientation before building the IK Rig.
- Meshes are dense, with many material zones and HD morphs. Budget LODs and decimation, and merge materials.
- **License:** every Daz store product used as 3D data in a distributed game (free or paid) needs that product's **Interactive License**. That includes the Genesis base figure's Essentials product. Some products offer no Interactive License at all, so they cannot ship in a game. You may develop privately before buying, but buy before anyone else gets a build.

---

## Mixamo

- The auto-rigger writes a **65-bone** `mixamorig:` skeleton with **no root bone**, in a T-pose. The service is in maintenance mode, with intermittent outages since 2025 *(secondary source)*.
- Import the character once *With Skin*, then animations *Without Skin* onto **that** skeleton. Mixing in a skeleton that later gained a root bone gives "Mesh contains root bone as root but animation doesn't contain the root track".
- Root motion, T-pose vs A-pose and IK Rig setup: see `ue5-animation-characters` (Mixamo section).
- Mixamo characters are prototype-grade (no facial rig, single material). Do not dress them with Manny or MetaHuman clothing. The skeletons differ.

---

## Blender / custom characters

- Units: *Apply Scalings: FBX All* with Apply Unit on (or scene Unit Scale 0.01). Leaving both at default gives a root bone scaled 100.
- *Add Leaf Bones* off. Primary bone axis Y and secondary X (defaults). Changing them rotates bones 90°.
- The armature object becomes a bone in UE. Name it `root` when matching Manny/MetaHuman, or you get an extra "Armature" root bone and a skeleton mismatch *(community practice)*.
- Forward -Z / Up Y defaults are fine. UE's scene conversion rotates into Z-up, X-forward. A forum thread reports front-axis problems with the **Interchange** FBX importer on skeletal meshes. If a mesh imports rotated, compare against the legacy FBX path.
- For clothing: import the **target body** (MetaHuman Combined Skel Mesh FBX, or Manny) into Blender, model or fit the garment, use Data Transfer for weights from the body, clean up, and export **only the garment plus the same armature** (no new bones).

---

## Marvelous Designer / CLO → MetaHuman (USD)

Official MD and CLO articles describe this flow (5.6+):
1. In UE: MetaHuman Character → *Export Combined Skel Mesh* (from the MetaHuman Creator menu). Export that skeletal mesh as FBX for MD/CLO as the avatar.
2. Drape and fit the garment in MD/CLO, then export **USD** (it can carry simulation data and panel structure for Chaos Cloth).
3. In UE: import the USD → create a **Cloth Asset** (*right-click > Physics > Cloth Asset*) → configure its Dataflow (skin weight transfer from the body, sim weight maps, physics asset).
4. Create an **Outfit Asset** (for resizable use, with several source bodies) → configure it → test and apply it in MetaHuman Creator.

5.8 adds non-destructive round-trip editing with CLO/Marvelous, import of USD constraints and cloth attributes, and preserved panel structure, springs and sim metadata.

Source bodies for resizable outfits: you don't need all 18. Epic suggests **6** (one height) or **4** (excluding the "unw" bodies). More source bodies mean less warping.

---

## Per-source import checklists

**MetaHuman**
- [ ] UE Optimized pipeline chosen at the right quality per role. Hero = High. NPCs = Medium/Low.
- [ ] Body type decided *before* dressing (parametric vs compatibility body). Clothing is fixed or parametric to match.
- [ ] Wardrobe items applied, Body Hidden Face Map set **before** assembly, then assembled.
- [ ] After assembly: check garment LODs vs body LODs, LODSync components, groom quality per LOD, and any cloth sim that needs re-adding.
- [ ] Project settings: *Support Compute Skin Cache* on, Groom and RigLogic plugins enabled when moving assets to a project without MetaHuman Creator.

**Fab character**
- [ ] License (Standard / UE-Only / NoAI) recorded in your asset log.
- [ ] Skeleton = UE5 Manny/Quinn (or retarget plan). Assign the *existing* skeleton on import, or add it as a compatible skeleton.
- [ ] LODs, materials and texture sizes within budget. The Physics Asset covers the silhouette.

**Character Creator**
- [ ] Engine version supported by the current Auto Setup build.
- [ ] UE5 export preset and bind pose match the target. Delete Hidden Mesh decided. Morphs on, T0 off.
- [ ] License: export rights, and an Extended license if many characters ship.

**Daz**
- [ ] Interactive Licenses bought for every product in the character (figure, morphs, clothes, hair).
- [ ] DTU builds against your engine version, or plan a manual FBX path. Fix Twist Bones on. Root orientation checked.
- [ ] IK Rig and Retargeter to your animation skeleton built and tested.

**Mixamo**
- [ ] Prototype only. Root bone strategy decided. One skeleton for all clips.

**Custom (Blender/Maya)**
- [ ] Units, leaf bones, armature/root name and bone axes as above. One shared skeleton asset in UE.
