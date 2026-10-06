# Gameplay systems: camera, aim line, stroke input, cue sync, rules, AI

General Enhanced Input, camera and gameplay framework usage is covered in `ue5-gameplay-systems`. IK, Control Rig and character setup are in `ue5-animation-characters`. Behaviour trees and general NPC AI are in `ue5-npc-ai`. This file covers only the billiards-specific traps.

## Aiming camera

| Mode | Setup | Trap |
|---|---|---|
| Orbit / aim | Spring arm pivoted at the cue-ball centre. Yaw = aim direction, pitch clamped to about 5–60°, zoom = arm length. | Spring-arm collision tests snap the camera when it brushes the lamp or rails. Disable them, or use a channel that ignores table props. |
| Fine aim | Modifier (hold) scales yaw sensitivity by ×0.05–0.1. Show the aim angle to 0.01°. | Mouse acceleration and frame-time-scaled deltas make fine aim inconsistent. Use raw deltas, do not multiply by DeltaTime, and quantise the yaw exactly as it is sent on the network. |
| Top-down | Separate camera, orthographic or narrow FOV, fit to table bounds. | A perspective top view distorts angles near the edges. Prefer orthographic for planning. |
| Shot / follow | After the strike, blend (`SetViewTargetWithBlend`) to a follow or broadcast camera. Return to aim when all balls rest. | Do not follow the cue ball directly at break speed. Lead it, or cut to a wide view. |

## Aim / trajectory prediction line

- Draw from the **same simulator** and the **same quantised shot params** as the real shot, for example run `Simulate` with a `MaxTime`, a "stop at first object-ball contact" option, or both. A separate "cheap" line (ray + reflection) disagrees with the shot as soon as squirt, swerve or throw matter, and players will report it as a bug.
- Typical assist levels: (1) ghost ball at first contact, plus the object-ball direction and the cue-ball tangent line, with short lengths; (2) the cue-ball path until the first cushion; (3) full simulated paths (practice mode). Show throw-corrected object-ball directions only if you want "honest" assistance.
- The ghost-ball position for a pot is `G = O − 2R · normalize(P − O)` (O = object ball, P = pocket target point). Aim the cue ball at G, not at O.
- Re-simulate only when the input changes: aim, spin, power or elevation. Throttle to every frame or less, and run the simulation on a worker task (`UE::Tasks::Launch`) if it ever costs more than about 1 ms.
- Rendering: spline meshes, a Niagara ribbon or a dynamic mesh. Do **not** ship `DrawDebugLine`, because debug drawing is compiled out in Shipping builds.
- In ranked online play, the aim line is the cheat surface (see multiplayer). Limit its length per mode.

## Shot power: stroke input

Prefer a physical stroke over a charge bar. Pull back, then push forward. The cue speed at the moment the tip reaches the ball becomes V0.
```cpp
// Enhanced Input: IA_StrokeHold (bool), IA_Stroke (Axis1D: mouse Y / right stick Y), IA_FineAim, IA_Spin (Axis2D)
void UCueStrokeComponent::OnStrokeAxis(const FInputActionValue& Val)
{
    const double DeltaCm = Val.Get<float>() * StrokeCmPerUnit;        // raw delta, NOT * DeltaTime
    TipOffsetCm = FMath::Clamp(TipOffsetCm + DeltaCm, 0.0, MaxBackswingCm);
    History.Add({GetWorld()->GetTimeSeconds(), TipOffsetCm});        // ring buffer, last ~100 ms
    if (bArmed && TipOffsetCm <= 0.0 && PrevOffsetCm > 0.0)          // tip reached the ball
    {
        const double SpeedCmS = ForwardSpeedFromHistory(History);     // linear fit over ~50-80 ms
        const double V0 = PowerCurve(SpeedCmS / MaxInputSpeedCmS) * MaxV0;  // MaxV0 ≈ 12 m/s
        SubmitShot(QuantizeShot(AimYaw, Elevation, TipA, TipB, V0));  // see multiplayer flow
        bArmed = false;
    }
    PrevOffsetCm = TipOffsetCm;
}
```
Traps:
- Estimate the speed from a time-stamped history, not from a single frame delta. A single delta is noisy and frame-rate dependent.
- Add a dead zone and require a minimum backswing, so accidental twitches do not shoot.
- Gamepad: map stick displacement to cue *position*, not velocity. Players can then feel the backswing.
- Accessibility: also offer a hold-and-release power meter. Both must produce the same `FShotParams`.

## Cue stick and character sync

- The cue is its own actor, placed procedurally along the aim line: tip at the contact point plus a back-offset of TipOffsetCm, axis tilted by the elevation. **The input drives the cue, and the character follows the cue** via IK (bridge hand fixed on the cloth, back hand on the butt). Never derive the shot from an animation's root motion.
- Fire the strike exactly when the tip-to-ball distance reaches 0. Trigger impact audio and VFX from that same moment.
- Before accepting the shot, sweep the cue capsule against rails, balls and the character. Raise the elevation or block the shot when blocked, and show this in the UI.
- After the strike, play follow-through at a speed that matches V0. Hide the cue or blend it away when the camera cuts.

## Rules engine (pure C++, unit-tested)

The input is the server's `FShotResult` event log plus the pre-shot `FGameState`. The output is a `FRulesVerdict`: legal or foul (type, penalty), balls to spot, ball in hand and its area, next player, and game or frame over. Keep it free of UObjects and rendering.

Facts to extract from the log: first ball the cue ball contacts, every cushion contact after that first contact, pocketed balls in order, cue ball pocketed, balls off the table (only if jumps are supported), and object balls contacting a rail on the break.

| Game | Must-implement rules (verify details against the official rulebook) |
|---|---|
| 8-ball (WPA) | Legal break: pocket a ball, or drive ≥ 4 object balls to a rail. Open table until groups are assigned. Called shot. "No rail after contact" foul (after contact, a ball must be pocketed or some ball must reach a rail). 8-ball pocketed early = loss. Scratch on the 8 = loss. Ball in hand after fouls. |
| 9-ball (WPA) | First contact must be the lowest-numbered ball. Push-out option after the break. Three successive fouls = loss of game (a warning is required before the third). 9 on a legal shot wins. 9 pocketed on a foul is re-spotted [S21]. |
| Snooker (WPBSA) | Ball "on" sequence: red, then a nominated colour, then the colours in order. Foul penalty = max(4, value of the ball on, values of balls involved), capped at 7 [S19]. Free ball after a foul that leaves a snooker. Miss rule (the referee's judgement of a reasonable attempt; make it configurable). Colours re-spotted to their own spot, otherwise the highest-value free spot, otherwise as near as possible. Respotted black for ties. |
| Carom / 3-cushion | Cue ball must contact 3 cushions before the second object ball. Needs accurate cushion timing from the event log. |

Traps:
- Spotting balls needs a "find free position" routine that uses the simulator's overlap test. Snooker "as near as possible to its spot" is a search along the long axis toward the top cushion.
- League variants (blackball, APA, BCA) differ. Use a data-driven rule configuration instead of `if` chains.
- Do not show the outcome (foul or scored) before playback reaches the event that determines it.

## AI opponent (shot selection)

```
candidates = []
for target in LegalTargets(state):                      // rules engine supplies "ball on"
  for pocket in Pockets:
    P = PocketAimPoint(pocket, target)                   // account for jaws: aim inside the mouth
    if !PathClear(cue→Ghost(target,P)) or !PathClear(target→P): continue
    for (V0, a, b) in SpinSpeedGrid:                     // e.g. 3–5 speeds × 5 spin options
      candidates += Shot(aimYaw(Ghost), V0, a, b)
candidates += BankAndKickShots(...) + SafetyShots(...)   // safeties: hide cue ball, leave long shots
for c in TopK(candidates by cheap geometric score):      // cut angle, distances, obstacles
  outcomes = [Simulate(state, Perturb(c, noise(difficulty))) for _ in 1..N]   // Monte Carlo
  c.value = mean(potProb·(1 + positionValue(nextState)) − foulRisk·penalty − opponentBest(nextState))
choose argmax(value); then execute Perturb(choice, noise(difficulty))
```
- Human-like error: add zero-mean Gaussian noise to every shot parameter (yaw, elevation, V0, â, b̂). Computer-pool research ran tournaments at fixed noise levels, where the "high noise" setting used 5× the standard deviations of the "low noise" one [S36]. Scale σ per difficulty and tune it until pot percentages per cut angle and distance look human. Starting points for tuning (not from literature): pro yaw σ ≈ 0.05–0.1°, beginner ≈ 0.5–1°; V0 σ ≈ 3–10 %.
- The AI must plan with the noise it will execute with. Evaluating noiseless and then executing noisy produces stupid, overambitious shots.
- Budget: candidates × N simulations can reach thousands. Prune geometrically first, run on worker tasks, and time-slice across frames. Add a "thinking" delay of about 1–4 s for pacing, even when the search is done earlier.
- Personality: aggression (pot vs safety threshold), spin preference, and a rate of deliberate "mistakes" (e.g. poor position play) separate from aim noise.
- Fairness: the AI uses the same simulation, the same rules and the same noise model. It must never read hidden information such as future rack jitter.
