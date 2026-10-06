# Presentation: balls, felt, table, cameras, replay, audio

Lighting setup (Lumen, MegaLights, shadows, reflections) belongs to `ue5-lighting-rendering`, and frame budgets to `ue5-performance-optimization`. Only the billiards-specific traps are listed here.

## Ball rendering

| Item | Do | Trap |
|---|---|---|
| Shading | Glossy dielectric with a clear coat. Use the legacy **Clear Coat** shading model (Clear Coat, Clear Coat Roughness) [S32], or **Substrate** (Slab + Vertical Layering). Substrate is production-ready from UE 5.7 [S29]. | A plain low-roughness default lit material looks like plastic. The sharp lamp highlight on a clear coat sells the "phenolic resin" look. |
| Numbers / stripes | One material for all balls. Pass ball id, base colour and stripe flag via **Custom Primitive Data**, and index a number atlas. Each number appears in two circles at opposite poles. | 16 material instances or decal actors per ball add draw calls, and decals smear on spheres. |
| Imperfections | Very subtle roughness breakup, micro-scratches (normal intensity ≪ 0.1), chalk smudges on the cue ball, slight per-ball tint variation. | Overdone grime reads as dirty, cheap balls. Check at the close-up camera, not in the editor viewport. |
| Rotation | Drive the quaternion from the simulation (see `physics-model.md` §7). Keep motion blur on. | At about 400 rad/s a ball turns ~6.7 rad per 60 Hz frame. Without motion blur the numbers strobe (wagon-wheel). |
| Coordinate mapping | Map sim SI metres to UE cm (×100). If you mirror an axis, transform ω as a pseudovector: ω' = det(M)·M·ω. | Balls that visibly roll "backwards" means a mirrored position mapping with an unmirrored ω. |
| Contact shadow | Small, sharp contact shadows under every ball; the ball sits *on* the cloth (z = R). | Missing contact shadows make balls float. Check shadow resolution at gameplay camera distance. |
| Reflections | Lamps and the room must reflect in the balls. Screen-space reflections fail on small spheres at grazing angles, so prefer Lumen or ray-traced reflections, or a captured cubemap per table. | Black or flat balls in reflective close-ups. |

## Felt (cloth)

- Use the **Cloth** shading model (Fuzz Color, Cloth) [S32], or Substrate Slab Fuzz (Fuzz Amount, Fuzz Color, Fuzz Roughness) [S31]. Add a fine weave normal at high tiling plus macro colour variation. Pool cloth is worsted wool or nylon; snooker cloth is napped.
- Add wear: faint ball-path tracks, chalk dust near spots and the break area, slightly darker cushion edges. Table markings (spots, baulk line, D, head string) go in a mask texture, not as separate meshes (z-fighting).
- Trap: a texel-dense weave normal at gameplay distance causes moiré and shimmer. Mip it out, or fade it by distance.
- Snooker nap: real napped cloth makes slow balls drift. Simulate it only if you also model it in physics (direction-dependent rolling friction or drift term). Otherwise skip it.

## Table and room

- Rails are wood with a clear coat. Add diamonds/sights (inlay), pocket leather or netting, and visible cushion rubber under the cloth. Pocket meshes must match the physics jaw geometry exactly, or players will see balls "bounce off air".
- Rectangular overhead lamps over the table are the signature look. Use rect lights matching the lamp shades, plus a darker room.

## Cameras and cinematics

- Close-up DOF: use a Cine Camera with focus tracking the cue ball (aim) or the target ball (shot). Use a shallow aperture for drama only in replays and cinematic cuts. During aiming, the ghost ball and object ball must stay sharp.
- Broadcast-style cuts: a director system reads the event log *in advance*, because the outcome is known before playback. Examples: cut to a pocket cam for slow pots or jaw rattles, slow motion for close calls or doubles, crowd reaction on a frame-winning ball.
- Slow motion and replay: scale the playback clock you use to evaluate the closed-form trajectories (`tPlay += dt * rate`). Scrubbing and reverse are free. Do **not** use global time dilation for the simulation, since the simulation is already done. It is fine for VFX and audio pitch consistency.
- Store per-shot `FShotResult` objects for instant replay, highlight reels and bug reports. They are tiny and deterministic.

## Audio

| Sound | Drive with | Trap |
|---|---|---|
| Ball–ball click | Normal relative speed at impact. Volume in dB ∝ log(speed), slight pitch/sample randomisation, sample layering for hard hits. | Linear volume mapping sounds wrong. Limit voices with concurrency, because the break has dozens of hits within ~100 ms. |
| Cushion thud | Normal speed into the cushion. Use a softer, lower sample than ball–ball. | Do not reuse the click sample. |
| Cue strike | V0 and tip offset. Miscue gets a distinct "clack". | — |
| Pocket | Capture event, then drop, then roll in the return or net (choreographed, matches the drop animation). Jaw rattles come from the cushion events at the jaws. | — |
| Rolling loop | One looping voice per moving ball. Volume and low-pass driven by speed (e.g. MetaSound float parameters). Fade out at rest. Optional cloth-type variation. | Loops that never stop because a ball creeps. Gate them on the motion state from the simulator, not on velocity noise. |

Schedule every one-shot from the **event timestamps** in the shot result as playback time passes each event. Do not use physics hit callbacks; that keeps the timing exact in slow motion and replays.
