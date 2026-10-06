# Chaos Cloth for characters (UE 5.8)

Contents: which system · Cloth Asset Dataflow recipe · collision · stability settings · teleport/reset · wind · LOD and performance · multiplayer · debugging · billiards specifics.

---

## Which cloth system

| System | Where it's authored | Status in 5.8 | Use when |
|---|---|---|---|
| **Cloth Asset** (Dataflow cloth editor, formerly "Panel Cloth") on a **Chaos Cloth Component** | Its own asset with a Dataflow graph. Non-destructive | **Production-ready, default cloth editor** (Beta in 5.7) | All new garments. MetaHuman outfits (Cloth/Outfit Assets) |
| Legacy Clothing Tool (clothing data painted on a Skeletal Mesh section) | Inside the Skeletal Mesh editor | Supported (older pipeline) | Existing assets, and **Mutable** (which doesn't support Cloth Assets) |

- Convert legacy clothing with the `DF_LegacyClothingAssetTemplate` Dataflow template (legacy `UClothingAssetCommon` → `UChaosClothAsset`).
- `UChaosClothComponent` derives from `USkinnedMeshComponent`. Its asset can be a Cloth Asset **or an Outfit Asset**.
- 5.8 also added support for a "ClothAsset SKM clothing asset" and Skeletal-Mesh-level Dataflow nodes (release notes). Treat that as a bridge between the two pipelines and test before relying on it.

---

## Cloth Asset recipe (follower garment with partial sim)

1. Import the garment as a Static Mesh, FBX or USD (Marvelous/CLO USD can carry panels and sim data).
2. *Content Browser > right-click > Physics > Cloth Asset* and open it (the Dataflow editor).
3. Graph (verified node names; your template may differ slightly):
   - Garment input: `StaticMeshImport` (or the USD import node).
   - `TransferSkinWeights`: source = the **body skeletal mesh** that the character renders (MetaHuman Combined/assembled body, or Manny). It writes weights to the sim and/or render mesh.
   - `WeightMap`: paint *MaxDistance* (0 = fully skinned and kinematic, >0 = simulated). Paint 0 everywhere the garment touches skin.
   - `SimulationDefaultConfig`: default properties in the old cloth editor's format.
   - `SimulationMaxDistanceConfig`: Low/High range applied to the painted map.
   - `SimulationBackstopConfig`: keeps particles from going behind the skinned surface (inside the body).
   - `SimulationLongRangeAttachmentConfig`: tethers to the nearest fixed point (anti-stretch when iterations are low).
   - `SimulationCollisionConfig`: *Cloth Collision Thickness*, simple colliders (spheres, capsules, convex, boxes), complex colliders (SkinnedLevelSet, MLLevelSet), skinned triangle mesh collision, **CCD**.
   - `SimulationSelfCollisionConfig`: *SelfCollisionThickness* is per side, so the total thickness is 2×.
   - `SimulationVelocityScaleConfig`: linear and angular velocity scale, `MaxVelocityScale`, `FictitiousAngularScale`, max linear velocity.
   - `SimulationAerodynamicsConfig`: drag and lift (wind).
   - `SimulationSolverConfig`: iterations and substeps.
   - `SetPhysicsAsset`: the body's physics asset to collide with.
   - `ClothAssetTerminal`: writes the asset.
4. In the character: add a **Chaos Cloth Component** as a child of the body mesh, assign the Cloth Asset, and set its **Leader Pose** to the body (it is a skinned mesh component).
5. Remove the static or skeletal copy of the same garment, or keep it only for LODs where the cloth is disabled.

---

## Collision

- The **Physics Asset** is the main collider set. Capsules on bones under the garment are cheapest and most stable. 5.8 updated the tapered capsule cloth collision primitive. Legacy behaviour used only spheres and capsules. Other shapes are supported but cost more.
- Tight garments: a **kinematic collider** (a skinned collision mesh that moves with the body; 5.4/5.5+) or **skinned triangle mesh** collision gives far better contact than capsules. Use it on heroes only.
- Reported trap (5.5.4 forum): cloth clips through the skin where the physics-asset bodies are *simulated with soft constraints*. With body simulation off, collision was correct. Keep the collision bodies kinematic (no ragdoll, no physical animation) while dressed, or use a separate collision setup.
- Cloth must start **outside** all colliders. Particles that begin inside a capsule get pushed out violently on the first frame. Shrink the capsules or offset the garment.
- CCD for fast limbs (arm on the cue stroke). It costs more, so heroes only.
- Cloth vs world: don't rely on garment-world collision for the pool table. Keep the torso skinned (MaxDistance 0) and solve rail contact with animation/IK.

---

## Stability: jitter, explosion, stretching

| Problem | Settings to change (in this order) |
|---|---|
| Jitter at rest | Raise iterations/substeps (`SimulationSolverConfig`). Lower self-collision thickness. Use local-space simulation if far from the world origin. Check that no collider starts intersecting |
| Explosion on the first frame or after a move | Teleport/reset (below). Colliders intersecting the rest pose. Velocity scales too high. Huge DeltaTime after a hitch |
| Stretching or "rubber" sleeves | Long Range Attachment (tethers). More iterations. Higher stretch stiffness. MaxDistance too high in tight areas |
| Lag behind fast turns | Lower the angular velocity scale and `FictitiousAngularScale`, clamp with `MaxVelocityScale` |
| Falls through the body | Collision thickness > 0. Physics bodies cover the area. CCD. Backstop. Colliders not simulating with soft constraints |
| Self-intersection or crumpling | Self-collision on with correct thickness (2× per-side value). More substeps |
| Breaks in Movie Render Queue with temporal samples or motion blur | `p.ChaosCloth.UseTimeStepSmoothing 0` (forum fix, partial) |

Simulation is time-step dependent. Retune if you change the fixed frame rate or the substepping.

---

## Teleport and reset

Cloth integrates velocity from the previous positions. A teleport looks like a huge velocity, so the cloth explodes.

- Legacy skeletal-mesh cloth: `USkeletalMeshComponent::ForceClothNextUpdateTeleportAndReset()` (also in Blueprint).
- Chaos Cloth Component: Blueprint *ClothComponent* category has **Force Next Update Teleport** (and a reset variant; check autocomplete). Call it on the cloth component, not on the body.
- Moving the actor: use teleport semantics (`SetActorLocation(..., ETeleportType::TeleportPhysics)` / `TeleportTo`) instead of sweeping across the map.
- Call it on: spawn/respawn, placing a player at the table for a shot, Sequencer camera cuts that **move** the character, unpausing after a long pause, and after attaching to a seat.

---

## Wind

- Cloth reacts to wind only with aerodynamics configured (`SimulationAerodynamicsConfig` drag/lift > 0).
- `SetAerodynamics` on the clothing interactor is deprecated. Use `SetWind`.
- Indoor pool hall: no wind. Leave drag at a small value for air resistance on fast motion and skip Wind Directional Sources.

---

## LOD, performance, culling

- Budget (secondary, rough): about 0.2–1 ms per simulated character depending on particle count. Profile your own (`stat` and Insights; see `ue5-performance-optimization`).
- Per-LOD simulation: disable sim on LOD1+ for most garments. Disabled LODs snap to the skinned pose, so make the transition happen at a distance where nobody notices.
- Runtime: `SetEnableSimulation(false)` or *Suspend Simulation* (keeps the last simulated pose) for off-screen or distant characters. For legacy cloth, `SuspendClothingSimulation` / `ResumeClothingSimulation`.
- `bDisableClothSimulation` on a skeletal mesh component is effectively a construction-time switch, not a runtime toggle.
- Sim particle count: build a **lower-resolution sim mesh** than the render mesh (Remesh/sim-mesh nodes). Simulate only the loose region.
- Tiering for this game: player and opponent get cloth on loose parts at LOD0–1. Named NPCs get skinned-only clothing (or one hem). Background NPCs get no cloth at all (merged meshes).

---

## Multiplayer

- Cloth is cosmetic and **not replicated**. Each client simulates locally, so cloth will differ between machines. Never use cloth for gameplay.
- Replicate the **outfit selection** (IDs) and build the outfit in `OnRep`. Call the teleport/reset after applying it.
- Dedicated server: don't create cloth or groom components (`GetNetMode() == NM_DedicatedServer`), and don't load those assets.
- See `ue5-multiplayer` for replication patterns.

---

## Debugging

- CVars and commands seen in Epic's cloth troubleshooting material: `p.ClothPhysics` (global toggle), `p.ChaosCloth.Reset`, `p.ChaosCloth.DebugStep`, `p.ChaosCloth.UseTimeStepSmoothing`, `r.Mobile.EnableCloth`. Confirm exact names with console autocomplete (`p.ChaosCloth.`).
- Use the Dataflow editor's simulation preview with your real animations (bridge stance, stroke, walk-in). Visualise colliders and kinematic vs dynamic particles in the cloth debug views.
- Isolate the problem: turn off self-collision, then collision, then aerodynamics. Re-enable one at a time.

---

## Billiards-specific notes

- Shooting stance: the torso leans to the rail and the cue arm swings fast. Keep shirts and vests skinned. Simulate only loose hems or an open jacket.
- The cue is not in the character's Physics Asset, so cloth does not collide with it. Prevent sleeve/cue overlaps with animation and garment fit.
- Close-ups during the aim: this is where poke-through and cloth jitter are most visible. Test garments in the aim camera, not only in the editor viewport.
