# Ball physics model: equations, events, collisions, C++ sketches

Event-driven model (Leckie & Greenspan [S3], pooltool [S1][S2]): closed-form motion per state, exact next-event time, analytic advance. Conventions: XY table plane, Z up, ball centre at z = R, SI units, `double`. Per-ball state is r, v, w and s.

## 1. Motion states and closed-form evolution

Contact-point slip velocity (ball against cloth):
`u = v + w × (−R ẑ) = (vx − R·wy, vy + R·wx, 0)`

| State | Condition | Lasts until |
|---|---|---|
| Sliding | \|u\| > ε | τ_s = 2\|u₀\| / (7 μs g) → Rolling |
| Rolling | u = 0, \|v\| > ε | τ_r = \|v₀\| / (μr g) → Spinning (if wz ≠ 0) or Stationary |
| Spinning | v = 0, \|wz\| > ε | τ_sp = \|wz₀\|·2R / (5 μsp g) → Stationary |
| Stationary | everything ≈ 0 | — |
| Pocketed | removed from play | — |
| Airborne (optional) | vz ≠ 0 or z > R | Parabola until z = R, then ball–table bounce (e_t) |

**Sliding.** The slip direction û = u₀/|u₀| stays constant during the slide. That is why the path is a parabola, which is the swerve curve.
```
r(t) = r0 + v0 t − ½ μs g t² û
v(t) = v0 − μs g t û
w_xy(t) = w0_xy − (5 μs g / (2R)) t (û × ẑ)      // x,y components only
wz(t)   = spin-decay(wz0, t)                      // see below
```
**Rolling.** v̂ is constant.
```
r(t) = r0 + v0 t − ½ μr g t² v̂
v(t) = v0 − μr g t v̂
w_xy(t) = (ẑ × v(t)) / R                          // no-slip constraint
wz(t) = spin-decay(wz0, t)
```
**Spin decay** applies in every state:
`wz(t) = wz0 − sign(wz0)·α·min(t, |wz0|/α)`, with `α = 5 μsp g / (2R)`, which is about 10.9 rad/s² with the pooltool defaults.

The evolve function must handle state changes inside the requested interval. Evolve up to τ, switch state, then evolve the remainder, as pooltool's `evolve_ball_motion` does. This keeps evaluation at an arbitrary render time t exact.

## 2. Event detection

Inside a state, each ball's acceleration a_i is constant: −μs g û (sliding), −μr g v̂ (rolling), 0 otherwise. Every event time is therefore a polynomial root.

| Event | Equation in t | Degree |
|---|---|---|
| State transition | closed form (τ_s, τ_r, τ_sp) | — |
| Ball–ball | \|Δr(t)\|² = (2R)², Δr(t) = Δr₀ + Δv t + ½ Δa t² | quartic |
| Ball–linear cushion | n̂·r(t) − d = R (n̂ = inward normal of the cushion nose line) | quadratic |
| Ball–circular segment (jaw tip, radius ρ) | \|r_xy(t) − c\|² = (R + ρ)² | quartic |
| Ball–pocket capture | \|r_xy(t) − p\|² = r_pocket² | quartic |

Ball–ball quartic coefficients (A t⁴ + B t³ + C t² + D t + E = 0):
```
A = ¼ |Δa|²
B = Δa·Δv
C = |Δv|² + Δa·Δr0
D = 2 Δv·Δr0
E = |Δr0|² − 4R²
```
Rules that prevent bugs:
- Accept only roots in (ε, min(τ_i, τ_j)], that is, inside **both** balls' current state windows. After a transition the coefficients change, so recompute them.
- Accept only approaching contacts: d/dt |Δr|² < 0 at the root. For cushions, accept only n̂·v < 0. Without these checks, balls frozen together or frozen to a rail generate zero-time events forever.
- Use a robust quartic solver. Find all real roots, polish each with 1–2 Newton steps, then verify the distance at the root. Grazing hits produce near-double roots, which are the classic missed-collision source.
- Cache pairwise event times and invalidate only the pairs involving balls changed by the last event. For 16 balls there are 120 pairs; snooker's 22 balls give 231.

### Event loop

```cpp
// Pure C++ (no UObjects), deterministic, single-threaded per simulation.
ShotResult Simulate(TableState s, const ShotParams& shot, const SimConfig& cfg)
{
    ShotResult out;
    ApplyCueStrike(s, shot, cfg, out);                 // §4: sets cue ball v, w, state
    double t = 0.0;
    for (int n = 0; n < cfg.MaxEvents; ++n)            // hard cap: Zeno / bug guard
    {
        Event e = FindNextEvent(s, cfg);               // min over transitions, pairs, cushions, pockets
        if (!e.IsValid()) break;                       // all balls stationary or pocketed
        EvolveAll(s, e.Time - t, cfg);                 // closed form, no integration error
        t = e.Time;
        Resolve(s, e, cfg);                            // §3 collision models / state change
        out.Events.Add(Snapshot(e, s));                // keyframe: time + states of involved balls
    }
    if (!AllAtRest(s)) StopAllBalls(s);                // cap hit: log it, never hang
    out.FinalState = s;
    return out;
}
```

## 3. Collision resolution

### Ball–ball: frictional, inelastic, equal masses

This follows Alciatore TP A-5/A-6/A-14 as extended by pooltool `FrictionalInelastic` [S1][S10]. Throw (collision-induced and spin-induced) comes out of it automatically.
```cpp
void ResolveBallBall(Ball& b1, Ball& b2, double R, double e)
{
    const Vec3 n = Normalize(b2.r - b1.r);                     // line of centres
    const double v1n = Dot(b1.v, n), v2n = Dot(b2.v, n);
    const double w1n = Dot(b1.w, n), w2n = Dot(b2.w, n);       // spin about n is unchanged
    const Vec3 v1t = b1.v - v1n * n, v2t = b2.v - v2n * n;
    const Vec3 w1t = b1.w - w1n * n, w2t = b2.w - w2n * n;

    const double v1nF = 0.5 * ((1 - e) * v1n + (1 + e) * v2n);
    const double v2nF = 0.5 * ((1 + e) * v1n + (1 - e) * v2n);
    const double Jn = 0.5 * (1 + e) * std::abs(v1n - v2n);     // normal impulse / m
    // (pooltool uses |v2nF - v1nF| = e·|Δvn| here; the difference is small)

    auto Surf = [R](Vec3 v, Vec3 w, Vec3 d) { return v + Cross(w, R * d); };
    const Vec3 slip = Surf(v1t, w1t, n) - Surf(v2t, w2t, -n);  // relative contact velocity

    Vec3 dv, dw; bool sticks = Length(slip) < kEps;
    if (!sticks) {
        const double mu = 9.951e-3 + 0.108 * std::exp(-1.088 * Length(slip)); // TP A-14 fit
        dv = -mu * Jn * Normalize(slip);
        dw = (2.5 / R) * Cross(n, dv);                         // same Δw for both balls
        const Vec3 slipAfter = Surf(v1t + dv, w1t + dw, n) - Surf(v2t - dv, w2t + dw, -n);
        sticks = Dot(slip, slipAfter) <= 0;                    // friction would reverse slip
    }
    if (sticks) {                                              // "gearing": no slip at exit
        dv = -(1.0 / 7.0) * (v1t - v2t + R * Cross(w1t + w2t, n));
        dw = -(5.0 / 14.0) * (Cross(n, v1t - v2t) / R + w1t + w2t);
    }
    b1.v = v1t + dv + v1nF * n;   b2.v = v2t - dv + v2nF * n;
    b1.w = w1t + dw + w1n * n;    b2.w = w2t + dw + w2n * n;
    b1.s = ClassifyMotion(b1);    b2.s = ClassifyMotion(b2);   // almost always Sliding
}
```
`std::exp` is a transcendental function. If you need cross-platform bitwise determinism, see `multiplayer-determinism.md`, and either tabulate the function or use a constant μb. A better upgrade is the Mathavan et al. 2014 numerical model [S5], which is available in pooltool as `FRICTIONAL_MATHAVAN`.

### Ball–cushion: Han 2005 [S6], ported from pooltool `han2005`

Use a frame where +x is the cushion normal pointing *into* the cushion. The incoming ball has vx > 0. h is the nose height.
```cpp
void ResolveBallCushionHan(Vec3& v, Vec3& w, double R, double m, double h, double e, double mu)
{
    const double sT = h / R - 1.0, cT = std::sqrt(1.0 - sT * sT);   // contact angle θa
    const double sx = v.x * sT - v.z * cT + R * w.y;
    const double sy = -v.y - R * w.z * cT + R * w.x * sT;
    const double c  = -v.x * cT;
    const double II = 0.4 * m * R * R, A = 3.5 / m, B = 1.0 / m;
    const double PzE = -(1 + e) * c / B;
    const double s0 = std::sqrt(sx * sx + sy * sy);
    double PxE, PyE;
    if (s0 / A <= mu * PzE) { PxE = sx / A; PyE = sy / A; }          // sticking
    else { PxE = mu * PzE * sx / s0; PyE = mu * PzE * sy / s0; }     // sliding
    const double PX = -PxE * sT - PzE * cT, PY = PyE, PZ = PxE * cT - PzE * sT;
    v.x += PX / m;  v.y += PY / m;                                   // vz ignored (2D)
    w.x += -R / II * PY * sT;
    w.y +=  R / II * (PX * sT - PZ * cT);
    w.z +=  R / II * PY * cT;
}
```
Rotate into the cushion frame with the cushion normal, resolve, then rotate back. Use vector projections rather than `atan2` and angles, which is better for determinism. For circular jaw segments, the normal is `normalize(r_xy − c)`. Mathavan 2010 [S4] is more accurate, but it integrates the impact numerically (pooltool caps it at 5000 steps by default). Use it offline to fit Han's e and μ, or adopt it if profiling allows.

Defaults: e_c = 0.85 and f_c = 0.2 for pool. Han's paper also discusses speed-dependent restitution. pooltool keeps a disabled variant: `max(0.40, 0.50 + 0.257·vn − 0.044·vn²)`.

### Pockets

- Model the jaws as linear segments (facing angles) plus circular segments at the jaw tips. Real rattles and jaw rejections then emerge from the cushion model.
- Use a capture circle (pooltool: centre + radius) as the point of no return. When a ball crosses it, mark it Pocketed and remove it from collision.
- Do not simulate the drop physically. Play a choreographed drop animation (shelf, back draft, net/return) from the capture event. It stays deterministic and looks better.

## 4. Cue strike (instantaneous point impact, TP A-30 [S8])

Inputs: cue speed V0, aim direction ŝ (horizontal unit), elevation θ, and tip **contact** offsets (â right, b̂ up), normalised by R and measured perpendicular to the cue axis. Masses: m (ball), M (cue). Tip restitution e_tip.

Derivation (cue axis d̂ = cosθ ŝ − sinθ ẑ, left vector l̂ = ẑ × ŝ):
```
contactOffset = tipCentreOffset / (1 + rTip/R)             // [S1]
if (|(â,b̂)| > MiscueLimit≈0.5) → Miscue                    // [S13]
J/m  = (1+e_tip)·V0 / (1 + m/M + 2.5·(â² + b̂²))            // ball speed along d̂
v    = (J/m)·d̂                                             // 2D game: drop the z part
ω    = (5·(J/m) / (2R)) · ( â·(cosθ ẑ + sinθ ŝ) + b̂·l̂ )
```
This formula equals pooltool's `cue_strike` with e_tip = 1, written in the cue frame. It was cross-checked numerically, including for θ = 15° and offsets (0.3, 0.2). Checks: with θ = 0 and b̂ = 0.4, ω = v/R along l̂, which is natural roll with no slide. ωR/v = 2.5·b̂, so draw comes from b̂ < 0. Side english tilts the spin axis toward ŝ when θ > 0. That tilt is the source of swerve and masse curvature during the sliding phase.

**Squirt** (TP A-31 via pooltool; m_e = effective cue end mass):
```
α = atan( 2.5·â·sqrt(1−â²) / (1 + m/m_e + 2.5·(1−â²)) )
rotate v about ẑ by +α   // right english (â>0) squirts LEFT (toward l̂)
```
With m/m_e = 30 and â = 0.5, α ≈ 1.9°, which matches the published 1.8–2.5° [S14]. Expose `SquirtScale` and `SpinScale` multipliers, like pooltool's throttles, to support "arcade" modes.

**Miscue.** Beyond the limit, randomise a large direction error, cut speed, remove most spin, and play the miscue sound. This is not a foul in itself, but the outcome usually is.

**Elevation.** Compute the minimum elevation from obstacles: sweep the cue's capsule against rails and balls, and clamp or auto-raise θ. If jump shots are out of scope, set vz = 0 after the strike. That is a 2D approximation which ignores the table impulse, so cap θ, for example at 30–35°, and keep masse arcade-tuned. For jumps, add the Airborne state and a ball–table bounce with e_t ≈ 0.5.

## 5. Rack and break specifics

- Never rack balls exactly touching. pooltool places each ball randomly inside a radius of (1 + 1e-3)·R and warns against 0 [S1]. Touching balls give zero-time event cascades (Zeno).
- Rack jitter makes breaks vary, and that is realistic. Seed it from the server (see multiplayer), so all peers rack identically.
- The break is the hardest case: many near-simultaneous events. Keep `MaxEvents` generous (thousands) and log any shot that hits the cap.

## 6. Fixed-step alternative (simpler, still robust)

If you do not want quartics, step at a fixed dt of 1/1000 s or finer. Per step: evolve each ball with the **closed-form** state evolution, then sweep pairs and cushions for a time of impact inside the step. Use the earliest one, sub-step to it, resolve, and continue the remainder. This is event-driven inside each step. Never use naive Euler with penetration correction: the energy errors and ordering artefacts are visible in the break and on frozen balls.

## 7. Orientation for rendering only

Orientation does not feed back into the physics. Integrate it for visuals in **simulation time**, at fixed sub-steps with |ω|·dt ≤ ~0.1 rad: `q ← q ⊗ quat(axis = ω̂, angle = |ω| dt)`. Store each ball's quaternion at every event keyframe. Playback and replays then show identical number orientations on every client.

## 8. Licensing note

pooltool is Apache-2.0. If you port its code rather than re-deriving the formulas, keep the licence and NOTICE attribution in your third-party notices.

## 9. Minimum test suite (run headless, e.g. UE Automation or plain gtest)

1. Stun hit → final rolling speed is 5/7·v0 (±1e-9).
2. b̂ = 0.4, θ = 0 → state after the strike is Rolling, not Sliding.
3. Head-on stun → cue ball residual speed is (1−e)/2·v0.
4. Stun cut, directly after impact → separation angle is a little under 90°. The reference port with e = 0.95 and the TP A-14 friction gives 82–88° for 20–50° cuts, and about 79° at a 10° cut. After the cue ball's slide ends, a rolling cue ball at a half-ball hit deflects ≈ 30°.
5. Throw vs cut angle (stun) → peaks near a 30–40° cut and stays at or below ~6° [S12]. The reference port gives ≈ 4.9° at 0.5 m/s, ≈ 4.2° at 1 m/s and ≈ 1.8° at 3 m/s (30° cut). Throw is speed-independent at small cuts (≈ 1.5° at 10°).
6. Total kinetic energy (linear + rotational) never increases across any event.
7. Re-simulating the same input gives bitwise-identical output (hash FinalState).
8. Fuzz test: 10⁵ random shots, including breaks, finish under the MaxEvents cap. Afterwards no balls overlap and no ball is outside the cushions.
