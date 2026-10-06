# Determinism and turn-based multiplayer

Pool is chaotic: a 1-ulp difference before the break produces a different rack outcome. Design so that correctness **never** depends on two machines computing bit-identical floats, then add determinism only as an optimisation. General UE replication (RPC semantics, ownership, relevancy, Iris) is covered in the `ue5-multiplayer` skill.

## Recommended flow: server-authoritative sim, clients play back the result

```
Client (shooter)                 Server                              All clients
aim + local prediction line
forward stroke starts ──ServerSubmitShot(FShotParams, TurnId)──▶
                                 validate (turn, ranges, ball-in-hand, rate)
                                 strike + Simulate() → FShotResult
                                 rules engine → FGameStateDelta
                                 ◀── Multicast/replicated FShotResult ──▶  play back event log
                                                                          rules UI after playback ends
```
- Send the shot when the **forward stroke starts**. The 100–300 ms cue animation then hides the round trip. Never send the shot after the tip has visibly hit the ball.
- `FShotParams` should be quantised and small: yaw (int32 micro-degrees), elevation, tip offset (â, b̂ as int16), V0 (mm/s), and the cue-ball position for ball-in-hand. Quantise **before** simulating, on both sides, so the shooter's local prediction uses the same inputs the server uses.
- `FShotResult` holds the shot id, the quantised params, the post-strike cue-ball state, and the event keyframes `{time, ballId, r, v, w, state, quat}`, plus the final table state and its hash. Clients evaluate the closed-form motion between keyframes. Playback is then exact without any determinism, because each keyframe re-anchors the trajectory.
- Payload size is roughly events × 2 balls × ~40 bytes (float32, cm). Breaks can produce hundreds of events, so keep RPC payloads small and chunk or compress if needed. Alternatively replicate a `TArray` property (fast-array serialisation) keyed by shot id, which also serves late joiners.
- Replicate the authoritative **resting** table state, game state and turn owner as properties, for reconnects and late joins. Ball positions never stream while balls move.
- Listen-server and P2P setups: the host is the authority. With a dedicated server, the server needs only the pure C++ sim (no rendering).

## Optional lockstep path (bandwidth-free playback)

Clients re-simulate from `FShotParams`. The server sends only `FinalStateHash` and the final state. On a mismatch, ease balls to the authoritative final positions. Lockstep holds only when **all** of these are true:

- [ ] Same simulation binary/library on every peer. A Windows client against a Linux server is a different compiler and libm.
- [ ] No fast-math. Strict FP model: MSVC `/fp:precise` or `/fp:strict`; clang/gcc without `-ffast-math`, with `-ffp-contract=off` (no FMA contraction) [S33][S34]. UE build configurations have historically mixed FP models (forum reports cite `/fp:fast` in some configurations), so do not assume. Compile the sim as a separately built static library with explicit flags, linked via `PublicAdditionalLibraries` (see `ue5-build-and-modules`), or wrap it in MSVC `#pragma float_control(precise, on, push)` and `#pragma fp_contract(off)`.
- [ ] Only + − × ÷ and `sqrt` in the hot path. These are correctly rounded by IEEE 754. `sin`, `cos`, `atan2`, `exp`, `cbrt` and `acos` differ between libm implementations [S34]. Use vector projections instead of angles, use an iterative quartic solver (Newton/bisection on a bracketed interval) instead of the closed-form Ferrari/Cardano (cbrt/acos), and replace the `exp` in the TP A-14 friction with a table or a constant μb. Compute the squirt `atan` on the server and ship the post-strike state.
- [ ] Fixed evaluation order: no `TMap`/`TSet` iteration order in the sim, and no multithreading inside one simulation. Break ties between simultaneous events deterministically (sort by time, then type, then ball ids).
- [ ] No uninitialised memory or time/frame-dependent inputs. Rack jitter uses a seeded PRNG of your own (not `FMath::Rand`), and the seed comes from the server.
- [ ] A CI test runs 10⁴ recorded shots on every target platform and compares hashes.

## Server-side validation (anti-cheat basics)

| Check | Reject / clamp |
|---|---|
| Turn ownership and `TurnId` matches | reject |
| V0 ≤ MaxV0, elevation within [θmin(obstacles), θmax] | clamp or reject |
| √(â² + b̂²) ≤ max offset | reject (the client should have shown a miscue) |
| Ball-in-hand position: inside the legal area (kitchen/D/anywhere), not overlapping balls or cushions | reject |
| Rate limit: one shot per turn, minimum interval | reject |
| Called pocket/ball (8-ball call shot, snooker nominated colour) is legal | reject |

Accept that the client sees the full table, so a perfect aim-assist bot is always possible. Mitigate with server-side statistics (shot precision far beyond the human distribution, superhuman decision timing) and by limiting prediction-line length in ranked modes. Do not trust any client-reported outcome: pocketed balls, fouls and scores are computed only on the server from its own simulation.

## Chaos networked physics: not needed here

UE's networked physics (default replication, predictive resimulation, the Network Physics Component) targets real-time player-driven bodies [S27]. A turn-based billiards game does not need it. Using it for balls adds correction artefacts without fixing determinism.
