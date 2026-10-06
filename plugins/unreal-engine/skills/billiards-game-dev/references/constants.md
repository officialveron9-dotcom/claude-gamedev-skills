# Billiards constants: equipment, coefficients, sanity values

All values are SI (m, kg, s, rad) unless stated. In UE, multiply lengths by 100 (cm) only at the render boundary; keep the simulation in SI doubles. Source tags such as `[S7]` point to `sources.md`. Values marked *pooltool default* come from the pooltool source code (Apache-2.0). Treat them as tuned defaults, not as measurements of one particular table.

## Balls

| Game | Diameter | Radius R | Mass | Notes |
|---|---|---|---|---|
| Pool (8/9-ball, WPA) | 57.15 mm (2.25 in, +0.005 in) | 0.028575 | 156–170 g (5.5–6 oz) | pooltool default m = 0.170097 kg [S1][S17] |
| Snooker (WPBSA) | 52.5 mm ±0.05 mm | 0.02625 | No fixed mass. A set may vary by at most 3 g between balls. | pooltool snooker preset: R = 0.02619375 m, m = 0.140 kg [S1][S19] |
| Carom / 3-cushion | 61–61.5 mm | ~0.03075 | 205–220 g (typ. 210 g) | pooltool billiard preset: R = 0.03075, m = 0.210 [S1][S20] |

Moment of inertia (solid sphere): I = 2/5 · m · R².

## Tables (playing surface between cushion noses)

| Table | Playing surface | Cushion nose height h | Source |
|---|---|---|---|
| 9-ft pool | 2.54 × 1.27 m (100 × 50 in, ±1/8 in) | 62.5–64.5 % of ball diameter (nominal 63.5 % ≈ 36.3 mm) | WPA [S17][S18] |
| 7-ft pool (bar box) | 1.9812 × 0.9906 m | 0.64 · 2R | *pooltool default* [S1] |
| Snooker | 3.569 × 1.778 m (±13 mm) | 0.028 m (*pooltool default*, not verified against WPBSA) | [S19][S1] |
| Carom match table | 2.84 × 1.42 m | 0.037 m (*pooltool default*) | UMB via pooltool [S1] |

Cushion-contact geometry used by the Han 2005 model: sin θ_a = h/R − 1. For a WPA pool table, h ≈ 1.27 R, which gives θ_a ≈ 15.7°. Do not put the cushion contact at h = R (the ball centre height). With the contact at R, spin has almost no effect off the rail, and that looks wrong at once.

### Pockets (WPA pool) [S17]

| Item | Corner | Side |
|---|---|---|
| Mouth (cushion nose to nose) | 4.5–4.625 in (114.3–117.5 mm) | 5–5.125 in (127–130.2 mm) |
| Mouth cut angle (cushion + liner) | 142° ±1° | 104° ±1° |
| Shelf depth | 1–2.25 in | 0–0.375 in |
| Vertical pocket angle (back draft) | 12–15° | 12–15° |

pooltool's pocket table spec (7-ft defaults) uses these parameters: `corner_pocket_width 0.118`, `corner_pocket_angle 5.3°`, `corner_pocket_depth 0.0417`, `corner_pocket_radius 0.062`, `corner_jaw_radius 0.02095`, `side_pocket_width 0.137`, `side_pocket_angle 7.14°`, `side_pocket_depth 0.0685`, `side_pocket_radius 0.0645`, `side_jaw_radius 0.00795`. Use them as a parameterisation template: linear jaw segments, circular jaw tips and a capture circle [S1].

## Friction and restitution

| Quantity | Typical | Range | Source |
|---|---|---|---|
| Ball–cloth sliding friction μs | 0.2 | 0.15–0.4 | Alciatore [S7][S11]; pooltool u_s = 0.2 |
| Ball–cloth rolling resistance μr | 0.01 | 0.005–0.015 | [S7][S11]; pooltool u_r = 0.01 |
| Ball–cloth spin (about vertical axis) deceleration | ≈ 10.9 rad/s² | 5–15 rad/s² | [S7]. pooltool: u_sp = (10·2/5/9)·R gives α = 5·u_sp·g/(2R) ≈ 10.9 rad/s² |
| Ball–ball restitution e_b | 0.94–0.95 | 0.92–0.98 | [S7][S11]; pooltool e_b = 0.95 |
| Ball–ball friction μb | ≈ 0.06 (constant model) | 0.03–0.08 | [S7]. pooltool constant u_b = 0.05 |
| Ball–ball friction (speed-dependent, TP A-14 fit) | μb = 9.951e-3 + 0.108·exp(−1.088·v_rel) | v_rel = relative surface slip speed at contact (m/s) | [S10] via pooltool `AlciatoreBallBallFriction` |
| Ball–cushion restitution e_c | 0.85 | 0.6–0.9 | [S7]; pooltool e_c = 0.85 (citing van Balen thesis) |
| Ball–cushion friction f_c | 0.2 | — | pooltool f_c = 0.2 (snooker preset 0.5, carom 0.15) |
| Mathavan 2010 cushion model fit | e = 0.98, μ = 0.14 | — | [S4]. These belong to *their* model. Do not plug them into Han 2005. |
| Ball–table restitution e_t | 0.5–0.6 | — | pooltool 0.5; Alciatore TP 0.6 [S11]. Used for jump and hop. |
| g | 9.81 m/s² | — | — |

pooltool's snooker preset uses u_s = 0.5 and f_c = 0.5. These are tuned, not measured, so validate against footage before you copy them.

## Cue

| Quantity | Value | Source |
|---|---|---|
| Pool cue mass M | ≈0.51–0.6 kg (18–21 oz). pooltool 0.567 kg. Alciatore ratio m_ball/M = 6/19 | [S1][S11] |
| Snooker cue mass | pooltool 0.478 kg | [S1] |
| Tip radius (curvature) | pooltool 0.0106 m (≈ "nickel" radius) | [S1] |
| Effective end mass m_e (for squirt) | pooltool m_ball/30. A low-deflection shaft is lower. | [S1][S9] |
| Tip–ball restitution ("efficiency") | ≈0.71–0.75 for playing cues with medium tips, ≈0.81–0.87 for phenolic break/jump tips. TP uses η = 0.87. | [S15][S11] |
| Miscue limit (contact offset from centre) | ≈ 0.5 R | [S13] |
| Offset for maximum spin rate at fixed cue speed | ≈ 0.73 R. This is beyond the miscue limit, so it is unreachable in practice. | TP A-30 [S8] |
| Typical squirt at large english | ≈ 2.5° for a standard shaft, ≈ 1.8° for low-squirt. Fast speed. | [S14] |

Tip-centre offset vs contact-point offset: contact = tipCentreOffset / (1 + r_tip/R) [S1].

## Speeds (for UI scaling, caps and tests)

| Situation | Speed |
|---|---|
| Pro men's break (Onoda) | 22–26 mph (9.8–11.6 m/s), avg 24 mph [S16] |
| Pro women's break | 18–21 mph (≈8–9.4 m/s) [S16] |
| Practical V0 cap for a game | ≈ 12–13 m/s cue-ball speed. Design choice. |
| Angular speed while rolling at 12 m/s (pool) | ω = v/R ≈ 420 rad/s ≈ 24,000 deg/s. UE's default Max Angular Velocity is 3600 deg/s. |

## Derived values to unit-test against

- Slide phase duration: τ_slide = 2·|u₀| / (7·μs·g), where u₀ is the initial contact-point slip velocity [S1].
- A centre-ball hit (no initial spin) on a level cue ends sliding at v = 5/7 · v₀.
- Natural roll needs no sliding phase. It occurs for contact offset b = 0.4 R above centre with a level cue (ωR/v = 5/2 · b/R).
- Rolling stop distance: d = v² / (2·μr·g). With μr = 0.01, a ball rolling at 1 m/s travels ≈ 5.1 m.
- Rolling duration: τ_roll = |v| / (μr·g).
- Spin-down time: τ_spin = |ω_z| · 2R / (5·u_sp·g) [S1].
- Head-on stun shot: the cue ball keeps v·(1−e)/2 (= 2.5 % for e = 0.95).
- Stun cut shot: the balls separate at a little under 90°, because e < 1 and because of throw. A rolling cue ball near a half-ball hit deflects ≈ 30° once it rolls again.
- Throw: maximum ≈ 6°, for a slow stun shot near a half-ball hit (30° cut). Throw is larger at slow speeds [S12].
