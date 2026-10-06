---
name: billiards-game-dev
description: Builds realistic billiards games (pool 8/9-ball, snooker, carom/three-cushion) in Unreal Engine 5. Covers a custom event-driven ball simulation (sliding/rolling/spinning, cue tip offset to spin, squirt, swerve, masse, throw, Han cushion model, pocket jaws), the Chaos traps for casual games, server-authoritative turn-based multiplayer with shot replay, aim camera, ghost-ball/trajectory line, stroke power input, rules engines, noisy Monte-Carlo AI, and ball/felt/audio presentation. Use when the user mentions billiards, pool, snooker, carom, cue ball, spin/english, cushion/rail, pocket, break shot, aim or trajectory line, or German terms such as Billard, Queue, Effet, Bande, Kugelphysik, Stoß, Tasche, Anstoß.
---

# Billiards game development (UE5)

Pitfall-first guide. Use SI units and `double` in the simulation; convert to UE cm only for rendering. Constants and their sources are in `references/constants.md`. Version facts as of 2026-10-06: UE 5.8 is current (released June 2026) [S30].

## 1. Pick the physics architecture first

| Goal | Use | Why |
|---|---|---|
| Competitive, realistic, online, aim line, replays | **Custom event-driven simulation in pure C++**. The engine only renders. | Exact collision times (no tunnelling), frame-rate independent, spin and throw physics you control, a cheap whole-shot preview for the aim line and AI, and a replayable event log. Shipped UE snooker games (Snooker 19) used their own physics engine [S35]. |
| Casual or party game, no aim line, no ranked play | Tuned Chaos rigid bodies | Faster to prototype, but read `references/chaos-tuning.md`. The defaults are wrong for billiards. |

Stock Chaos traps that rule it out for competitive play: the default Max Angular Velocity of 3600 deg/s caps rolling at about 1.8 m/s; Bounce Threshold Velocity kills restitution in soft hits; there is no rolling resistance and no vertical-axis spin friction; small fast spheres tunnel without CCD and sub-steps; contacts against box cushions sit at the ball's centre height instead of the nose height; and results are not deterministic across platforms or builds [S22–S27][S37–S39].

Always hide the physics behind an `IBallSimulation` interface, so a Chaos prototype can be swapped out later.

## 2. Module layout (custom simulation)

```
BilliardsSim (pure C++, no UObject, no engine includes; ideally a separately compiled static lib)
  TableSpec, BallParams, ShotParams(quantised) → Simulate() → ShotResult{events[], finalState, hash}
  Evaluate(ShotResult, t) → per-ball r, v, w, quat     // closed form; used for playback
BilliardsRules (pure C++): ShotResult + GameState → RulesVerdict
BilliardsAI (pure C++ + UE::Tasks): candidate generation, Monte Carlo over Simulate()
UE layer: ABilliardTable (renders balls from Evaluate at playback time), cue/character actors,
          camera, UI, audio scheduled from event timestamps, replication (server-authoritative)
```
- Run `Simulate()` for the **whole shot instantly** at strike time, then play the result back with a clock. Slow motion, replays and scrubbing all evaluate the same closed form.
- Never let rendering or Tick feed back into the simulation.
- Build settings, static libraries and module boundaries are covered in `ue5-build-and-modules`. C++ conventions are in `ue5-cpp-core`.

## 3. Physics essentials (details and code: `references/physics-model.md`)

Per ball: r, v, w, and state ∈ {Sliding, Rolling, Spinning, Stationary, Pocketed[, Airborne]}.
Slip at the cloth contact: `u = (vx − R·wy, vy + R·wx, 0)`.

| State | Evolution (acceleration constant inside the state) | Ends at |
|---|---|---|
| Sliding | v −= μs·g·t·û (û fixed); w_xy −= (5μs g/2R)·t·(û×ẑ) | τ = 2\|u₀\|/(7μs g) |
| Rolling | v −= μr·g·t·v̂; w_xy = (ẑ×v)/R | τ = \|v₀\|/(μr g) |
| Spinning / any state | ωz decays linearly at α = 5·μsp·g/(2R) ≈ 10.9 rad/s² | τ = \|ωz\|/α |

Default pool constants: μs 0.2, μr 0.01, e_ball 0.95, μ_ball-ball 0.05 (or the TP A-14 speed fit), e_cushion 0.85, f_cushion 0.2, e_table 0.5, R 0.028575 m, m 0.17 kg, cushion nose 0.635·D [S1][S7][S17].

Event detection:
- **Ball–ball**: quartic `|Δr₀ + Δv t + ½Δa t²|² = 4R²`.
- **Linear cushion**: quadratic.
- **Jaw arcs and pocket capture**: quartic.
- **Transitions**: closed form.

Take the earliest event, advance all balls analytically to it, resolve it, and invalidate only the cached pairs that involve the affected balls.

Implementation traps (each one is a real bug class):
- Accept a root only if it lies in (ε, min(τ_i, τ_j)] **and** the pair is approaching (cushion: n̂·v < 0). Otherwise frozen balls cause infinite zero-time loops.
- Rack with gaps of about 1e-3·R and seeded jitter [S1]. Exactly touching balls hang the event loop on the break. Keep a `MaxEvents` guard that logs and stops balls.
- Polish quartic roots with Newton and verify the distance at the root. Grazing cuts otherwise miss.
- Ball–ball resolution must include friction (throw). Use the inelastic normal part plus a Coulomb-limited tangential impulse, and switch to the no-slip "gearing" solution if friction would reverse the slip.
- Cushion: Han 2005 with the contact angle `sinθ = h/R − 1` (h = nose height, ≈ 1.27R for pool). A centre-height contact makes english useless off the rail.
- Pockets: build the jaws as linear plus circular cushion segments and use a capture circle as the point of no return. Then play a choreographed drop animation. Build the render mesh and the physics segments from one spec.

## 4. Cue strike (TP A-30 [S8], squirt TP A-31 via pooltool [S1])

```
(â,b̂) = tipCentreOffset/(1 + rTip/R)            // contact offset, normalised; â right, b̂ up
if |(â,b̂)| > ~0.5 → miscue                      // [S13]
J/m = (1+e_tip)·V0 / (1 + m/M + 2.5(â²+b̂²))      // along cue axis d̂ = cosθ ŝ − sinθ ẑ
v   = (J/m)·d̂   (2D game: zero the z part; cap θ)
ω   = 5(J/m)/(2R) · ( â(cosθ ẑ + sinθ ŝ) + b̂ (ẑ×ŝ) )
α_squirt = atan(2.5â√(1−â²) / (1 + m/m_e + 2.5(1−â²)))  → right english squirts LEFT
```
Sanity checks: b̂ = 0.4 with θ = 0 gives natural roll (no slide); ωR/v = 2.5·b̂; a stun shot ends at 5/7·v₀; with m/m_e = 30 and â = 0.5 the squirt is ≈ 1.9°. The elevated side-spin term (sinθ ŝ) is what makes swerve and masse curve during sliding. Sweep the cue capsule against rails and balls to get the minimum elevation.

## 5. Multiplayer and determinism (`references/multiplayer-determinism.md`)

- Send **quantised shot parameters** (yaw, elevation, â, b̂, V0, ball-in-hand position) in a Server RPC **when the forward stroke starts**, so the animation hides the round trip. Never send ball positions while balls move.
- The server validates the shot, simulates it, runs the rules, and broadcasts `FShotResult` (event keyframes plus final state plus hash). Clients play back the keyframes, so no client depends on float determinism.
- Billiards is chaotic: one ulp changes a break. Lockstep re-simulation is safe only with the same binary, strict FP (no fast-math, no FMA contraction), only + − × ÷ and sqrt in the hot path (no sin/cos/atan2/exp/cbrt), deterministic iteration order, and a server-seeded PRNG. Otherwise correct to the server's final state.
- Replicate the resting table state and game state as properties for late joiners. Do not use Chaos networked physics or resimulation for this; it targets real-time bodies [S27].
- Anti-cheat: reject out-of-range power, offsets and elevation, out-of-turn shots and illegal ball-in-hand. Compute every outcome server-side. Aim bots cannot be prevented client-side, so detect them statistically and limit aim-line length in ranked play.

## 6. Gameplay checklist (`references/gameplay-systems.md`)

- [ ] Orbit camera pivoted on the cue ball, with clamped pitch, zoom and a fine-aim modifier (raw deltas, no DeltaTime scaling). Orthographic top-down view for planning. Disable spring-arm collision near table props.
- [ ] Aim line from the **same simulator and the same quantised inputs** as the real shot. Ghost ball `G = O − 2R·normalize(P − O)`. Assist level limits the path length. No `DrawDebugLine` in Shipping.
- [ ] Stroke input: Enhanced Input axis drives the cue tip position. V0 comes from a time-stamped linear fit over ~50–80 ms when the tip crosses the ball. Dead zone, minimum backswing, and a power-meter fallback for accessibility.
- [ ] The cue actor is driven by input, and the character follows it via IK (`ue5-animation-characters`). Fire the strike exactly when the tip-to-ball distance reaches 0.
- [ ] Rules as data-driven pure C++ consuming the event log: first contact, rails after contact, pocketed order, scratches. Covers 8-ball, 9-ball (3 fouls, push-out), snooker (penalty = max(4, ball on, balls involved), free ball, miss, respotting). Gate the UI on playback time.
- [ ] AI: enumerate legal target × pocket × speed/spin candidates, prune geometrically, run Monte Carlo `Simulate()` with **the same noise it will execute with**, and score pot probability + position − foul risk − opponent's best. Use per-difficulty Gaussian σ on all five parameters [S36], worker tasks and a thinking delay (`ue5-npc-ai` for the framework).

## 7. Presentation checklist (`references/presentation.md`)

- [ ] Balls: Clear Coat shading model or Substrate (production-ready since UE 5.7 [S29]). One material with Custom Primitive Data for number, colour and stripe. Subtle imperfections. Motion blur on (at 400 rad/s the numbers alias).
- [ ] Orientation integrated in simulation time and stored per keyframe, so every client sees identical numbers. If an axis is mirrored when mapping sim to UE, transform ω as a pseudovector.
- [ ] Felt: Cloth model or Substrate Fuzz, a fine weave normal that fades with distance, and markings in a mask. Pocket mesh equals the physics jaws.
- [ ] Lamps: rect lights over the table, with reflections that work on small spheres. Lighting and performance are covered in `ue5-lighting-rendering` and `ue5-performance-optimization`.
- [ ] Cinematics: a director reads the event log ahead of playback (pocket cams, slow motion on close pots). Slow motion = scale the playback clock. Cine-camera DOF only in replays and cuts.
- [ ] Audio scheduled from event timestamps: click volume ∝ log(normal speed), a separate cushion thud, a rolling loop per moving ball gated on the simulator state, and concurrency limits for the break.

## 8. Verification before shipping

- [ ] Physics unit tests (`physics-model.md` §9): 5/7 rule, natural roll, stop shot, 90°/30° rules, throw ≤ ~6°, energy never increases.
- [ ] Fuzz test: 10⁵ random shots including breaks. Never hits MaxEvents, no overlaps, no ball outside the cushions.
- [ ] Hash test: the same input gives the same `FinalState` hash on every shipping platform (if lockstep is used).
- [ ] Aim-line vs actual-shot divergence = 0 for identical inputs.
- [ ] Profile Simulate() for the break and the AI's worst-case search at the minimum target hardware.

## References (one level deep)

| File | Read when |
|---|---|
| `references/physics-model.md` | Implementing or debugging the simulator: equations, quartic events, ball–ball/cushion/strike C++ sketches, tests |
| `references/constants.md` | You need any number: ball/table/pocket specs (pool, snooker, carom), friction and restitution, cue data, speeds |
| `references/chaos-tuning.md` | The project insists on Chaos rigid bodies (casual mode or prototype) |
| `references/multiplayer-determinism.md` | Online play, replays, anti-cheat, FP-determinism flags |
| `references/gameplay-systems.md` | Camera, aim line, stroke input, cue/character sync, rules, AI |
| `references/presentation.md` | Ball, felt and table look, cinematics, replay, audio |
| `references/common-issues.md` | Something is broken: symptom → cause → fix tables |
| `references/sources.md` | Checking where a number or claim came from |
