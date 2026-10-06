# Tuned-Chaos approach (casual / party games only)

Use this only when the game does not need replicated competitive outcomes, an exact aim line or physically correct spin. Each item below is a trap stock Chaos falls into with billiard balls. Verify every setting name in your engine version, since the names below come from UE 5.x docs and API pages [S22–S26].

## Traps and fixes

| Trap | Why it bites billiards | Fix |
|---|---|---|
| **Max Angular Velocity cap** (default 3600 deg/s) [S39] | A pool ball rolling at 1.8 m/s already needs 3600 deg/s (ω = v/R). Faster balls are forced to slide, and draw/follow is clipped. | Raise the project-wide `Max Angular Velocity`, or per body (`MaxAngularVelocity` override on the body instance; UE4 docs list a `SetPhysicsMaxAngularVelocity` setter, so check the UE5 variant's name), to ≥ 30,000 deg/s. |
| **Bounce Threshold Velocity** (documented as "minimum relative velocity required for an object to bounce"; a 200 cm/s default is reported) [S23] | Most ball–ball hits are below 2 m/s, so restitution is ignored and soft shots look dead or "sticky". | Lower it substantially (try 5–20 cm/s) and re-test stack and rest stability. |
| **No rolling resistance** in the contact model [S37] | Balls roll forever. Angular damping slows them, but the slow-down is wrong because it is exponential, not the constant μr·g. | Apply F = −μr·m·g·v̂ yourself every physics step while the ball touches the bed and is rolling. Clamp to zero when below a threshold. |
| **No spin (vertical-axis) friction** | English never decays, and side spin off rails stays forever. | Apply torque about Z: τ = −sign(ωz)·I·α_sp, with α_sp ≈ 10.9 rad/s². Clamp at zero. |
| **Friction/Restitution combine modes** (default Average) [S24] | Average(ball, cloth) and Average(ball, cushion) couple values you want independent. | Set `Override Friction/Restitution Combine Mode` (Min/Multiply/Max) on the ball material, so the *other* material's value dominates. Document the pairing table. |
| **Tunnelling** of small fast spheres [S38] | At 12 m/s and 60 Hz a ball moves 20 cm per frame, about 3.5 diameters. | Enable `Use CCD` on balls, plus sub-stepping (`Substepping`, `Max Substep Delta Time` ≈ 1/240–1/500 s, `Max Substeps`) [S22], or async physics with a fixed `Async Fixed Time Step Size` (documented as experimental) [S23]. Note: forums report CCD hitches in some UE5 versions (UE-82340) [S38]. |
| **Cushion contact height** | A box cushion contacts the ball at the centre height (h = R). Real noses sit at 0.635·D (h ≈ 1.27R), so spin barely affects rebounds. | Accept it, or intercept rail hits and apply Han 2005 yourself (§3 of `physics-model.md`) with Chaos contact modification (advanced, version-dependent API) or by overwriting velocities after the hit. |
| **Bed is a mesh** | Triangle seams create "bumps" and kick balls sideways. | Make the bed collision one box. Make cushions boxes or convexes. Never use complex-as-simple trimesh for play surfaces. |
| **Jitter / creeping at rest** | Solver noise and sleep thresholds tuned for metres-sized props. | Set sleep thresholds on the ball physical material (`SleepLinearVelocityThreshold`, `SleepAngularVelocityThreshold`, `SleepCounterThreshold`) [S25]. Also force-sleep in code: if speed < 0.5 cm/s and ω < small for N steps, call `PutRigidBodyToSleep()` (UE4-era API, so verify it in your version). |
| **Frame-rate dependent outcome** | Variable substep count per frame changes results. Editor and packaged builds then differ. | Use a fixed physics step (async fixed step, no variable substeps) when reproducibility matters. Even then, Chaos is *not* guaranteed deterministic across platforms or builds [S27]. |
| **Mass/units** | UE uses cm and kg, and default gravity is −980 cm/s². | Set `Mass (kg)` override to 0.17 and radius to 2.8575 cm. Do not let density auto-compute from mesh scale. |
| **Async physics slows down at low FPS** | Reported on the forums: bodies appear to slow down when the game thread falls behind the async step [S23]. | Profile at the minimum target FPS. Keep the game thread light. |

## Minimal setup checklist

- [ ] Ball: sphere simple collision, `Simulate Physics`, mass override 0.17 kg, `Use CCD`, Max Angular Velocity ≥ 30,000 deg/s, physical material with Friction ≈ 0.2 and Restitution ≈ 0.95, combine-mode overrides set.
- [ ] Cushion physical material: Restitution ≈ 0.85, low friction. Bed: Friction ≈ 0.2, Restitution ≈ 0.5.
- [ ] Project: Bounce Threshold Velocity lowered; fixed step (sub-stepping or async) at ≤ 1/240 s.
- [ ] Custom forces in a physics-step callback (`AsyncPhysicsTickComponent` when async physics is on; it runs per physics step [S26]): rolling resistance, spin decay, rest clamp.
- [ ] Pockets: trigger volumes. On overlap, disable physics and play a canned drop.
- [ ] Debug with Chaos Visual Debugger (Beta since UE 5.4 [S28]).
- [ ] Do **not** build an aim line on Chaos. Draw a geometric ghost-ball line instead (see `gameplay-systems.md`).
- [ ] Migration path: keep game code talking to an `IBallSimulation` interface, so the custom simulator can replace Chaos later without rewriting rules, AI or UI.
