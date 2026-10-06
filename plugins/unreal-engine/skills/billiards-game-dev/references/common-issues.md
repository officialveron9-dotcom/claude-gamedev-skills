# Common problems: symptom → cause → fix

## Physics (custom simulator)

| Symptom | Likely cause | Fix |
|---|---|---|
| Simulation hangs or hits MaxEvents on the break | Balls racked exactly touching, which causes zero-time event cascades (Zeno) | Rack with a gap: random placement within (1 + 1e-3)·R [S1]. Accept only *approaching* contacts. Keep a MaxEvents cap that logs and stops balls instead of hanging. |
| Ball frozen to a rail fires endless cushion events | Missing `n̂·v < 0` check, or the root at t ≈ 0 is accepted | Require approach. Ignore roots below ε. After resolving, ensure the ball's normal velocity points away from the cushion. |
| Missed collisions on thin cuts | Grazing hit gives a near-double quartic root, lost to precision | Polish roots with Newton steps. Verify the distance at the root. Treat the discriminant ≈ 0 case as a hit if the minimum distance ≤ 2R + tolerance. |
| False collision between separating balls | Root accepted outside the state window, or receding pair | Restrict t to (ε, min(τ_i, τ_j)] and check d\|Δr\|²/dt < 0. |
| Balls overlap slightly after events | Evolution and detection use different formulas, or float32 is used | One shared evolve function, `double` everywhere. Assert no overlap in debug builds. |
| Balls never fully stop, or tiny drift | Transitions use exact zero, so the ε logic misses | Classify the state with ε on \|u\|, \|v\| and \|ωz\|. Snap to Stationary at the transition time. |
| Spin has no effect off the cushion | Cushion modelled at h = R (centre height) or without friction | Han 2005 with the real nose height (h ≈ 1.27R for pool) and f_c ≈ 0.2. |
| Ball jumps over the cushion or into the air | Elevated-cue vz kept with no table bounce model, or cushion too low | Either 2D (zero vz after the strike) or a proper Airborne state with e_t. Check that h is in the 0.625–0.645·D range. |
| Draw shots too weak or strong; follow wrong | Tip offset vs contact offset mixed up, or wrong ωR/v | Contact offset = tip offset / (1 + r_tip/R). ωR/v = 2.5·b̂. Verify the natural-roll test (b̂ = 0.4 gives no sliding). |
| Squirt goes the wrong way | Sign convention | Right english squirts **left**, i.e. rotate v toward ẑ × ŝ. Elevated right english then swerves back to the right. |
| No throw, so pots are "too easy" | Frictionless ball–ball collision | Frictional model with μb (TP A-14 speed-dependent fit) [S10]. |
| Break is inconsistent between attempts | Rack jitter, which is realistic | Seed it. Expose a "perfect rack" option for practice. Make sure online peers get the server's seed or positions. |
| Balls rattle in or out of the pockets unrealistically | Physics jaws don't match the mesh, or a capture circle that is too large or too small | Generate the render mesh and the physics segments from one pocket spec. Tune the capture radius against WPA mouth widths [S17]. |

## Chaos (tuned-Chaos approach)

| Symptom | Cause | Fix |
|---|---|---|
| Balls pass through cushions or each other | Small fast spheres with large dt | `Use CCD` plus fixed sub-steps at 1/240 s or finer [S22]. Box/convex cushions. |
| Fast balls slide instead of rolling, and draw is clipped | Max Angular Velocity cap (3600 deg/s default) [S39] | Raise it to ≥ 30,000 deg/s. |
| Soft hits don't bounce, balls "stick" | Bounce Threshold Velocity [S23] | Lower it, e.g. to 5–20 cm/s. |
| Balls roll forever | No rolling resistance [S37] | Custom −μr·m·g·v̂ force per physics step plus a rest clamp. |
| Jitter or creep at rest | Sleep thresholds, solver noise | Physical-material sleep thresholds [S25] plus a manual sleep clamp. |
| Random bumps while rolling | Trimesh bed or seams | Single box collision for the bed. |
| Different outcomes in editor vs packaged, or at different FPS | Variable sub-step count | Fixed physics step. Do not expect determinism at all for competitive play: switch to the custom simulator. |

## Multiplayer

| Symptom | Cause | Fix |
|---|---|---|
| Clients disagree on the break result | Floating-point divergence, amplified by chaotic dynamics | Server-authoritative simulation with event-log playback. Lockstep only with the full checklist in `multiplayer-determinism.md`. |
| Shooter's aim line differs from the actual shot | Prediction uses unquantised inputs or a different model | Quantise params first, and run the same simulation on both sides. |
| Visible pause between stroke and ball motion | RPC sent at tip contact | Send at stroke start. The cue animation hides the round trip. |
| Late joiner sees the wrong table | Only RPCs are used for state | Replicate the resting table state and game state as properties. |
| Desync after a reconnect mid-shot | Playback clock not restored | Include the shot id and the server playback start time. Fast-forward the closed form to "now". |
| Cheater shoots perfect bank shots | Client computes its own full prediction | Unavoidable client-side. Rely on server-side stats and anomaly detection, and on shorter aim lines in ranked play. |

## Gameplay / AI / presentation

| Symptom | Cause | Fix |
|---|---|---|
| AI is too perfect or robotic | No execution noise, or noise added only at execution | Gaussian noise on all params, scaled per difficulty. Plan with the same noise (Monte Carlo) [S36]. Add a thinking delay. |
| AI plays absurd shots | Evaluated noiselessly, or no position or safety term | Use expected value under noise, a position term (easy next shots) and a safety term (opponent's best). |
| AI stalls the frame | Thousands of simulations on the game thread | Geometric pruning, worker tasks, time-slicing. |
| Fine aim jumps or is frame-rate dependent | Mouse delta scaled by DeltaTime, or float yaw drift | Raw deltas, quantised yaw, a fine-aim modifier. |
| Power feels random | Speed taken from the last frame delta | Linear fit over 50–80 ms of time-stamped stroke history. |
| Numbers on balls strobe | Rotation aliasing at high ω | Motion blur. Integrate the quaternion in simulation time. |
| Balls roll backwards visually | Mirrored axis mapping without the pseudovector ω transform | Map ω with det(M)·M, or don't mirror. |
| Aim line missing in Shipping | `DrawDebugLine` used | Spline mesh, Niagara ribbon or dynamic mesh. |
| Sounds spam on the break | No concurrency limits | Sound concurrency per category, and a volume floor by impact speed. |
| Foul shown before the ball visibly misses | Rules verdict displayed on receipt | Gate the UI on playback time ≥ the event time. |
