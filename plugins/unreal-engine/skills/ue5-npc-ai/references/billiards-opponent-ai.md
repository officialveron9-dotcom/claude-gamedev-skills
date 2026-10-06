# Billiards opponent AI: decision vs presentation

## The split (do not blur it)

```
MatchManager (rules, turn, ball-in-hand, fouls)
   │  TurnBegan(Opponent)
   ▼
ShotPlanner (pure C++ game logic, no AI module)   ← uses the billiards sim (see billiards-game-dev)
   │  FShotPlan {TargetBall, Pocket, AimDir, Elevation, Speed, TipOffset, Kind(Pot/Safety/Break), Confidence, ThinkTime}
   ▼
OpponentAIController + StateTree (presentation flow)
   │  walk → get down → aim → stroke → watch → react
   ▼
Animation (ue5-animation-characters: FShotPresentation, Control Rig, montages)
   │  events: StanceReached, StrokeFinished
   ▼
Cue/strike system (gameplay) applies the impulse from FShotPlan (+ the error model)
```

| Wrong | Right |
|---|---|
| A BT service evaluates shots every 0.2 s | The planner runs once per turn, time-sliced across frames or on a worker thread over a **copy** of the table state |
| The decision reads animation or bone positions | The decision reads only the rules and ball state. Animation reads only `FShotPlan` / `FShotPresentation` |
| Skill implemented as "slower animations" | Skill = aim, speed and spin error, shot-selection depth and safety awareness. Animation tempo is personality only |
| The impulse is fired by the AI when its "Shoot" state starts | The impulse comes from the gameplay stroke at contact time. The AI only requests the stroke |
| Error added to the visual cue direction | The error goes into `FShotPlan` **before** presentation, so the cue visibly points where the ball actually goes (players notice mismatches) |

## Planner pipeline (game logic)

1. **Legal targets** from the rules (8-ball group, lowest ball in 9-ball, ball in hand).
2. **Candidates:** for each target × pocket, compute the ghost-ball position: `Ghost = Ball − 2R · normalize(PocketAim − Ball)`, using a pocket aim point inside the jaws, not the pocket center.
3. **Cheap filters:** cue ball → ghost path clear (swept sphere vs other balls), ball → pocket path clear, cut angle below ~75–80°, the cue can physically be placed (no ball or rail behind the cue ball at that angle beyond what elevation allows).
4. **Score:** cut angle, distances, pocket angle, cue-ball travel. Then **simulate** the top N with the deterministic billiards sim (several speed/spin variants each) to score position for the next shot and the scratch risk.
5. **Fallbacks:** a safety shot (minimize the opponent's best follow-up), a kick or bank when nothing is directly pottable, a dedicated break plan.
6. **Error model per difficulty:** sample aim error `σθ(skill, cut, distance)`, speed error, spin error. Clamp to a believable range. Weaker AIs also choose worse candidates (soft-max over scores with a temperature) and ignore position play.
7. **Think time:** derived from difficulty and how close the top scores were. Feed it to the Aim state (looks human, and hides time-sliced planning).

Traps:
- Planning on the live physics state while balls still move: wait for `BallsAtRest` from the match manager.
- Using Chaos rigid bodies for rollouts gives non-deterministic, slow and frame-dependent results. Use the custom deterministic sim from `billiards-game-dev` for both gameplay and planning.
- Planning on the game thread in one frame causes a hitch on high-difficulty searches. Time-slice it (a budget of N candidates per frame) or use an async task over copied data.
- Perfect AIs feel unfair. Cap the success rate per difficulty and validate it with automated matches.

## Stance feasibility (shared with animation)

The stance solve lives in game code (see `ue5-animation-characters` → billiards-shot-animation.md). Planner scores must include **reachability**: a shot that needs the mechanical rest or a behind-the-back stance is harder (raise the error, lower the score) and must pick that animation variant. Never plan a shot that has no valid stance variant.

## Turn-flow StateTree (presentation)

| State | Enter | Exit (event / condition) | Timeout fallback |
|---|---|---|---|
| WaitTurn | Sit or stand at its Smart Object, watch the table | `Match.TurnBegan.Self` | — |
| Plan | Request planner (async) | `AI.ShotPlanned` | 3–5 s → play the simplest legal shot |
| Walk | `MoveTo(ApproachPoint)` | Move succeeded | Path failed → teleport-fade or pick an alternate approach side |
| GetDown | Shot montage `Enter` with a Motion Warping target | `Anim.StanceReached` | 3 s → skip to Aim (snap under a camera cut) |
| Aim | Look along the cue line, practice strokes (personality), wait `ThinkTime` | Timer | — |
| Stroke | Request the gameplay stroke with `FShotPlan` | `Shot.StrokeFinished` | 3 s → force the stroke completion |
| Watch | Stand up, look at the cue ball or object ball | `Match.BallsAtRest` | Long cap → MatchManager decides |
| React | Chooser picks a reaction (pot, miss, foul, win) | Montage ended | 4 s |

Rules:
- Every wait has a timeout. A stuck montage or a missed event must never soft-lock the match.
- The MatchManager is authoritative for whose turn it is. The AI never ends its own turn.
- The player can skip AI presentation (fast-forward). Design the states so skipping only jumps to `Stroke` with the same `FShotPlan`, because the result must not change.

## Testing

- Headless AI vs AI matches via an automation test or commandlet: log pot %, fouls and average think time per difficulty.
- Visual Logger: log candidate ghost balls, chosen line and error sample (`UE_VLOG_SEGMENT` / `UE_VLOG_LOCATION`) to see in Tools → Debug → Visual Logger why a shot was chosen.
- A determinism check: the same table state, seed and difficulty must give the same `FShotPlan`.
