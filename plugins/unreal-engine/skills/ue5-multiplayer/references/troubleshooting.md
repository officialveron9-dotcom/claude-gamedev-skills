# Multiplayer troubleshooting

## "RPC not firing"

| Check | Symptom / log | Fix |
|---|---|---|
| Caller owns the actor? (Server RPC) | `LogNet: Warning: ... No owning connection for actor X. Function Y will not be processed.` | Call via PlayerController/possessed Pawn/PlayerState, or `SetOwner(PC)` on server. |
| Actor replicates and exists on both sides? | Nothing happens on remote side | `bReplicates = true`; spawn on server only; don't call on client-only actors. |
| Called on the right machine? | Multicast called on client runs only locally; Client RPC called on client runs locally | Multicast/Client RPCs must be called by the server (`HasAuthority()`). |
| GameMode involved? | Client code calls into GameMode -> null | GameMode is server-only. Use GameState or RPC to server. |
| `_Validate` returned false | Client gets disconnected | Fix validation logic; don't use validation for normal gameplay rejection. |
| Reliable spam | `Can't send function 'X' on 'Y': Reliable buffer overflow` then disconnect | Make it Unreliable, rate-limit, or replicate state instead. |
| Actor not relevant to that client | Multicast never arrives on distant clients | Use replicated properties for state; adjust `NetCullDistanceSquared`/`bAlwaysRelevant`. |
| Actor dormant | No RPC/property traffic | `FlushNetDormancy()` / `SetNetDormancy(DORM_Awake)`. |
| BP/C++ mismatch | `_Implementation` not called because BP overrides the event without calling parent | Call parent in BP or don't override. |
| Called too early (BeginPlay on client before possession/owner set) | Server RPC dropped on first frame | Call after possession (`NotifyControllerChanged`, `OnRep_PlayerState`, `AcknowledgePossession`) or retry. |
| Component RPC | Component not replicated | `SetIsReplicatedByDefault(true)`; owner actor replicates and is owned by the client. |

## "Variable not replicating"

| Check | Fix |
|---|---|
| `Replicated`/`ReplicatedUsing` specifier **and** `DOREPLIFETIME` present? | Both required. Missing specifier + DOREPLIFETIME = fatal `Attempt to replicate property '...' that was not tagged to replicate! Please use 'Replicated' or 'ReplicatedUsing' keyword in the UPROPERTY() declaration.` |
| `Super::GetLifetimeReplicatedProps(Out)` called? | Otherwise parent class properties stop replicating. |
| Set on the server? | Client writes are local only and get overwritten. |
| Actor/component replicates? | `bReplicates`, `SetIsReplicatedByDefault(true)`. |
| Push model on? | Every write needs `MARK_PROPERTY_DIRTY_FROM_NAME`. |
| Condition hides it? | `COND_OwnerOnly`/`COND_SkipOwner`/`COND_InitialOnly` — verify which client you test with. |
| OnRep "not called" but value correct? | Value already equal locally (REPNOTIFY_OnChanged) -> use `REPNOTIFY_Always`; on server C++ OnRep is never automatic. |
| Value is a UObject pointer and arrives null | Target object not replicated/net-addressable yet, or not supported for networking; replicate the object first or send an ID. |
| TMap/TSet | Not supported; use TArray of structs / FastArray. |
| Struct member missing `UPROPERTY()` | Non-UPROPERTY struct members don't replicate. Mark members `NotReplicated` to exclude intentionally. |
| PlayerState value lags ~1 s | Default PlayerState `NetUpdateFrequency` is 1 Hz; raise it. |
| Dormant / not relevant | Flush dormancy; check relevancy settings. |
| Subobject properties | `IsSupportedForNetworking()` true, registered via `AddReplicatedSubObject` with `bReplicateUsingRegisteredSubObjectList = true` (required with Iris). |
| Iris enabled and something stopped working | Legacy `ReplicateSubobjects()` overrides ignored; check registered subobject list; compare with `-UseIrisReplication=0`. |

## Lifecycle on each machine (character)

| Function | Server | Owning client | Simulated clients |
|---|---|---|---|
| Constructor, BeginPlay | yes | yes | yes |
| `PossessedBy` / `AController::OnPossess` | yes | no | no |
| `OnRep_PlayerState`, `OnRep_Controller` | no (call manually if needed) | yes | PlayerState yes |
| `AcknowledgePossession` (PC) | listen host only for its pawn | yes | no |
| `PawnClientRestart` | listen host's pawn | yes | no |
| `NotifyControllerChanged` | yes | yes | — |
| `SetupPlayerInputComponent` | locally controlled pawns only | yes | no |

## PIE / testing setup

- Editor Play dropdown: Net Mode **Play As Client** (launches a dedicated server in the background) with Number of Players >= 2; also test **Play As Listen Server** (host-specific bugs).
- Uncheck "Run Under One Process" to catch bugs that rely on shared memory/singletons between instances (slower).
- Network emulation: Editor Preferences > Level Editor > Play > Multiplayer Options > Enable Network Emulation (latency/packet loss), or console `NetEmulation.PktLag 150`, `NetEmulation.PktLoss 5`.
- Standalone dedicated server from the editor binary: `UnrealEditor.exe "<path>\MyGame.uproject" /Game/Maps/MyMap -server -log`; client: `UnrealEditor.exe "<path>\MyGame.uproject" 127.0.0.1 -game -log`.

## Debug commands

| Command | Use |
|---|---|
| `stat net` | Bandwidth, packet loss, RPC counts. |
| `log LogNet Verbose` (or `VeryVerbose`) | Ownership/RPC drop warnings. |
| `p.NetShowCorrections 1` | Visualize CharacterMovement server corrections. |
| `NetEmulation.PktLag <ms>` / `NetEmulation.PktLoss <percent>` | Simulate bad network. |
| `DisplayAll <Class> <Property>` | Watch a property value on the local machine. |
| Network Insights: launch with `-NetTrace=1 -trace=net` and open Unreal Insights | Per-property/RPC bandwidth and timeline. |
| `net.IsPushModelEnabled` | Check push model state. |
| `-UseIrisReplication=0/1` | A/B test Iris. |
