---
name: ue5-multiplayer
description: "Pitfalls and correct patterns for Unreal Engine 5 replication in C++ (UE 5.0-5.8): GetLifetimeReplicatedProps, DOREPLIFETIME/_CONDITION/_WITH_PARAMS_FAST, ReplicatedUsing OnRep (not auto-called on server in C++), Server/Client/NetMulticast RPCs, Reliable/Unreliable, _Implementation, WithValidation/_Validate, RPC ownership (\"No owning connection for actor\"), HasAuthority, GetLocalRole, IsLocallyControlled, framework classes per machine (GameMode server-only, PlayerController owning client only, PlayerState 1 Hz), component/subobject replication, Push Model, Iris (opt-in, production-ready 5.8), relevancy/dormancy, dedicated server testing. Use when writing or debugging multiplayer code: RPC not firing, variable not replicating. German triggers: Multiplayer Replikation, Netzwerk, RPC funktioniert nicht, Variable repliziert nicht, Dedicated Server."
---

# UE5 Multiplayer — pitfalls & correct patterns

Target UE 5.8 (current, 2026-10). Detailed snippets: [references/replication-patterns.md](references/replication-patterns.md). Symptom tables + log messages + console commands: [references/troubleshooting.md](references/troubleshooting.md).

## Before writing networked code — checklist

- [ ] Decide **where** each piece of logic runs (server / owning client / all) before coding. Gameplay state changes only on the server.
- [ ] Actor: `bReplicates = true` in ctor and **spawned on the server**. Client-spawned actors never replicate.
- [ ] Component: `SetIsReplicatedByDefault(true)` in its ctor (owner actor must replicate too).
- [ ] Every `Replicated`/`ReplicatedUsing` property has a `DOREPLIFETIME*` line, and `Super::GetLifetimeReplicatedProps` is called. `#include "Net/UnrealNetwork.h"`.
- [ ] Server RPCs only on actors the calling client owns (its PlayerController, possessed Pawn, PlayerState, or actors whose Owner chain leads to its PlayerController).
- [ ] UI, input, camera, sounds, VFX: never on a dedicated server; guard with `IsLocallyControlled()`/`IsLocalController()`/`GetNetMode() != NM_DedicatedServer`.
- [ ] Test with **Play As Client** (spawns a dedicated server) and **2+ players**, not just Standalone/listen with 1 player.

## Where things exist

| Class | Server | Owning client | Other clients | Trap |
|---|---|---|---|---|
| GameMode | yes | **no** | no | `GetAuthGameMode()` returns null on clients. Put shared state in GameState. |
| GameState | yes | yes | yes | Always relevant. |
| PlayerController | yes (all) | own only | **no** | `GetPlayerController(0)` on a listen server = host's PC; on clients only their own. Don't use index 0 in server logic. |
| PlayerState | yes | yes | yes | Default `NetUpdateFrequency` is **1 Hz** (UE 5.7 source) — raise it for GAS/attributes (`SetNetUpdateFrequency(100.f)` in ctor). |
| Pawn/Character | yes | yes | yes (if relevant) | `PossessedBy` runs **server only**; clients use `OnRep_PlayerState`/`OnRep_Controller`/`PawnClientRestart`/`NotifyControllerChanged`. |
| HUD, UUserWidget | no | own only | no | Never replicate widgets; feed them from replicated state. |
| GameInstance, subsystems | each machine, not replicated | | | |

## Authority/role — wrong vs right

```cpp
// WRONG: "server" check that is true on clients for client-spawned/non-replicated actors and in standalone
if (GetLocalRole() == ROLE_AutonomousProxy) { ApplyDamage(); }
// RIGHT
if (HasAuthority()) { ApplyDamage(); }            // server (or standalone) copy

// WRONG: use IsLocallyControlled on things that aren't pawns, or before possession
// RIGHT
if (APawn* P = GetPawn(); P && P->IsLocallyControlled()) { /* local player only */ }
if (PC->IsLocalController()) { CreateHUD(); }
if (GetNetMode() == NM_DedicatedServer) { return; }   // skip cosmetics
```
- `HasAuthority()` is true on the server **and** for actors spawned locally on a client (non-replicated) — not proof of "being the server" (`GetNetMode() < NM_Client` is).
- Listen server host is both server and a local player: code must handle `HasAuthority() && IsLocallyControlled()`.

## Property replication — wrong vs right

```cpp
// Header
UPROPERTY(ReplicatedUsing=OnRep_Health) float Health = 100.f;
UFUNCTION() void OnRep_Health(float OldHealth);      // must be UFUNCTION; optional param = previous value

// .cpp
#include "Net/UnrealNetwork.h"
void AMyChar::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);                  // WRONG to forget: parent props stop replicating
    DOREPLIFETIME(AMyChar, Health);
    DOREPLIFETIME_CONDITION(AMyChar, Ammo, COND_OwnerOnly);
}

// WRONG: OnRep expected to run on server
void AMyChar::TakeHit(float D) { Health -= D; }            // server UI/logic never updates
// RIGHT: C++ OnRep is NOT called on the server — call it yourself
void AMyChar::TakeHit(float D) { check(HasAuthority()); const float Old = Health; Health -= D; OnRep_Health(Old); }

// WRONG: client writes a replicated property (overwritten, never sent)
void AMyChar::ClientPressedReload() { Ammo = MaxAmmo; }
// RIGHT: ask the server
UFUNCTION(Server, Reliable) void ServerReload();
```
- Blueprint RepNotify **is** called on the server; C++ `OnRep_` is not. Don't port that assumption.
- Default `REPNOTIFY_OnChanged`: OnRep doesn't fire if the client's local value already equals the new one (e.g. client-predicted). Use `DOREPLIFETIME_CONDITION_NOTIFY(..., COND_None, REPNOTIFY_Always)` when you need every update (GAS attributes do).
- Never wrap `DOREPLIFETIME` in runtime conditions; use `COND_*` or `DOREPLIFETIME_ACTIVE_OVERRIDE_FAST` in `PreReplication`.
- Not replicable: `TMap`, `TSet`, raw non-UObject pointers. UObject pointers replicate only if the target is replicated/net-addressable (stable named asset or replicated actor/subobject); otherwise arrives as null.
- Property updates are not ordered relative to RPCs and may be batched/skipped (only latest value is sent). Don't encode events as property changes without a counter.
- Initial replication may arrive after `BeginPlay` on clients; use OnRep for initialization that depends on server data.

## RPCs — rules

| Type | Called on | Runs on | Requirement |
|---|---|---|---|
| `Server` | owning client (or server: runs locally) | server | Calling client must **own** the actor; else dropped with log `No owning connection for actor X. Function Y will not be processed.` |
| `Client` | server | owning client | Actor must have an owning connection (PC, possessed pawn, owned actor). On listen host's own actor runs locally. |
| `NetMulticast` | server | server + all clients where actor is relevant | Called on a client = runs only locally. Not sent to clients where actor isn't relevant; late joiners never get it. |

```cpp
// Header
UFUNCTION(Server, Reliable, WithValidation) void ServerFire(FVector_NetQuantize Dir);
UFUNCTION(NetMulticast, Unreliable) void MulticastFireFX(FVector_NetQuantize Dir);
// .cpp — WRONG: defining ServerFire() itself, or calling ServerFire_Implementation() directly
void AMyChar::ServerFire_Implementation(FVector_NetQuantize Dir) { /* authoritative */ MulticastFireFX(Dir); }
bool AMyChar::ServerFire_Validate(FVector_NetQuantize Dir) { return Dir.IsNormalized(); } // false = client kicked
void AMyChar::MulticastFireFX_Implementation(FVector_NetQuantize Dir) { /* cosmetic only */ }
```
- `WithValidation` is optional in UE5; if present, `_Validate` must exist. Returning false disconnects the client — validate cheat-relevant input, don't use for normal gameplay rejection.
- `Reliable` for gameplay-critical one-offs; never call Reliable RPCs every tick (reliable buffer overflow -> disconnect). Cosmetics: `Unreliable`.
- State that late joiners must see = replicated property, not multicast.
- RPCs sent in the same frame an actor is spawned on the server may arrive before/without the actor on the client — prefer replicated properties + OnRep for spawn-time data.
- Server RPC from an AI-controlled or world actor: clients don't own it -> route through the player's PlayerController/Pawn (e.g. `PC->ServerInteract(TargetActor)`).
- RPC params: no non-replicated UObject pointers; pass replicated actors or IDs. Use `FVector_NetQuantize*` to save bandwidth.

## Components & subobjects

```cpp
UMyComp::UMyComp() { SetIsReplicatedByDefault(true); }   // WRONG: SetIsReplicated(true) in ctor (runtime API)
// UObject subobject (UE 5.1+ registered list)
AMyActor::AMyActor() { bReplicates = true; bReplicateUsingRegisteredSubObjectList = true; }
void AMyActor::BeginPlay() { Super::BeginPlay(); if (HasAuthority()) { Item = NewObject<UMyItem>(this); AddReplicatedSubObject(Item); } }
// UMyItem must override: virtual bool IsSupportedForNetworking() const override { return true; } + its own GetLifetimeReplicatedProps
```
- `bReplicateUsingRegisteredSubObjectList` defaults to false (project-wide `net.SubObjects.DefaultUseSubObjectReplicationList`); Iris requires the registered list.
- `RemoveReplicatedSubObject` before destroying/replacing the subobject.

## Push Model (optional optimization)

- Requires `"NetCore"` in Build.cs, `bWithPushModel = true;` in **non-editor** Target.cs (editor targets have it), and `net.IsPushModelEnabled=1` (`[SystemSettings]` in DefaultEngine.ini). Until both are on, properties are compared normally.
```cpp
#include "Net/Core/PushModel/PushModel.h"
FDoRepLifetimeParams P; P.bIsPushBased = true; P.RepNotifyCondition = REPNOTIFY_OnChanged;
DOREPLIFETIME_WITH_PARAMS_FAST(AMyActor, Score, P);
void AMyActor::SetScore(int32 S) { Score = S; MARK_PROPERTY_DIRTY_FROM_NAME(AMyActor, Score, this); }
```
- Trap: any write path that forgets `MARK_PROPERTY_DIRTY_FROM_NAME` silently stops replicating (BP writes, direct member writes). Funnel writes through setters.

## Iris (status per version)

- 5.1 experimental, 5.7 beta (compiled in, off by default), **5.8 production-ready but still opt-in**. Gameplay API (UPROPERTY replication, RPCs, conditions, push model) is unchanged.
- Enable: Iris plugin in .uproject, `SetupIrisSupport(Target);` in Build.cs, `bUseIris = true;` in Target.cs (per Epic doc), DefaultEngine.ini `[SystemSettings]` `net.SubObjects.DefaultUseSubObjectReplicationList=1` and `net.Iris.UseIrisReplication=1`. Runtime toggle `-UseIrisReplication=1/0`.
- Traps: subobjects must use the registered list; legacy `ReplicateSubobjects()` overrides are ignored; `AActor::BeginReplication()`/`EndReplication()` overrides deprecated in 5.7 (use `OnReplicationStartedForIris`/`OnStopReplicationForIris`/`FillReplicationParams`). Don't enable Iris just because — only if you test both client and server with it.

## Relevancy, frequency, dormancy

- UE 5.5+: use `SetNetUpdateFrequency()`, `SetMinNetUpdateFrequency()`, `SetNetCullDistanceSquared()` (direct member writes deprecated).
- `bAlwaysRelevant`, `bOnlyRelevantToOwner`, `NetCullDistanceSquared`: an actor out of relevancy is **destroyed on the client** and respawned when relevant again (state comes back via replication, RPCs in between are lost).
- Dormant actors (`SetNetDormancy(DORM_DormantAll)`) don't replicate changes until `FlushNetDormancy()` — call it **before** changing properties.
- `ForceNetUpdate()` for an immediate send after a rare change on low-frequency actors.

## Dedicated server traps

- `BeginPlay` runs on the server for everything; skip cosmetic/local-player work there.
- No local player: `GetFirstPlayerController()` returns a remote client's PC (or null). Don't use it in server code.
- World Partition: the server does **not** stream by default (`wp.Runtime.EnableServerStreaming` = 0 in UE 5.7) — whole map loaded on server.
- Build needs a source engine + `MyGameServer.Target.cs` (see ue5-build-and-modules).

## References

- [references/replication-patterns.md](references/replication-patterns.md) — full code: replicated actor, component, subobject, push model, server-authoritative interaction via PlayerController, OnRep init, FastArray. Read when implementing.
- [references/troubleshooting.md](references/troubleshooting.md) — "RPC not firing"/"variable not replicating" symptom tables, exact log messages, console commands and PIE settings. Read when debugging.
- [references/sources.md](references/sources.md) — sources.
- GAS replication (ASC on PlayerState, replication modes): `ue5-gameplay-systems/references/gas.md`.
