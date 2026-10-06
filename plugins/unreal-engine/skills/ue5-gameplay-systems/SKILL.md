---
name: ue5-gameplay-systems
description: Pitfalls and correct C++ patterns for Unreal Engine 5 gameplay frameworks (UE 5.0-5.8). Covers Enhanced Input (UInputMappingContext, UInputAction, UEnhancedInputLocalPlayerSubsystem, BindAction, ETriggerEvent; legacy BindAxis/BindAction deprecated), Gameplay Ability System (AbilitySystemComponent on PlayerState vs Pawn, InitAbilityActorInfo on server and client, replication mode Mixed/Minimal/Full, AttributeSet, ATTRIBUTE_ACCESSORS, GameplayEffect components, prediction, NonInstanced removed), Gameplay Tags (UE_DEFINE_GAMEPLAY_TAG), Subsystems, Data Assets/Primary Assets/Asset Manager, TSoftObjectPtr async loading (FStreamableManager), UMG (BindWidget, NativeConstruct) and CommonUI, World Partition/OFPA, StateTree, Smart Objects, Mass, Mover. Use when implementing or debugging input, abilities, tags, subsystems, asset loading, UI or level streaming. German triggers: Eingabe funktioniert nicht, Enhanced Input, Fähigkeiten GAS, Attribute, Widget, Asset laden, Subsystem, Unreal Fehler.
---

# UE5 Gameplay systems — pitfalls & correct patterns

Target UE 5.8 (current, 2026-10). Each section: traps first, then the correct pattern. Deep dives in `references/`.

## Enhanced Input (legacy input deprecated since 5.1)

Checklist:
- [ ] `EnhancedInput` in Build.cs + plugin enabled. Project Settings > Input: Default Player Input Class `EnhancedPlayerInput`, Default Input Component Class `EnhancedInputComponent` (UE4-upgraded projects often still have the legacy classes -> `CastChecked` crash).
- [ ] Mapping context added **only for local players**, after a LocalPlayer exists (`NotifyControllerChanged`/`PawnClientRestart` on the pawn, or `BeginPlay` of the PC when `IsLocalController()`).
- [ ] Choose the trigger event deliberately: with no trigger in the IMC, `ETriggerEvent::Triggered` fires **every frame** while held. One-shot actions: `Started` (or a Pressed trigger).

```cpp
// WRONG: legacy API (deprecated), or adding the context on the server for remote players
PlayerInputComponent->BindAxis("MoveForward", this, &AMyChar::MoveForward);
// RIGHT
void AMyChar::NotifyControllerChanged()
{
    Super::NotifyControllerChanged();
    if (APlayerController* PC = Cast<APlayerController>(Controller))
        if (UEnhancedInputLocalPlayerSubsystem* Sub = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
            Sub->AddMappingContext(DefaultIMC, 0);          // GetLocalPlayer() is null for remote PCs on the server
}
void AMyChar::SetupPlayerInputComponent(UInputComponent* PIC)
{
    Super::SetupPlayerInputComponent(PIC);
    if (UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PIC))
    {
        EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyChar::Move);
        EIC->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
        EIC->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
    }
}
void AMyChar::Move(const FInputActionValue& V) { const FVector2D Axis = V.Get<FVector2D>(); /* ... */ }
```
More (modifiers for WASD, rebinding, 5.6-5.8 API changes): [references/enhanced-input.md](references/enhanced-input.md).

## Gameplay Ability System

Checklist:
- [ ] Modules `GameplayAbilities`, `GameplayTags`, `GameplayTasks`; plugin GameplayAbilities enabled.
- [ ] ASC on **PlayerState** for players that respawn (attributes/effects survive death), on the Pawn for AI/simple actors. Pawn implements `IAbilitySystemInterface` either way.
- [ ] `InitAbilityActorInfo(Owner, Avatar)` on **server** (`PossessedBy`) **and client** (`OnRep_PlayerState` for PS-ASC; `AcknowledgePossession`/`OnRep_Controller` path for pawn-ASC). Missing client init -> "Can't activate LocalOnly or LocalPredicted ability ... when not local!" and no prediction.
- [ ] Replication mode: players `Mixed`, AI `Minimal`, single-player `Full`. `Mixed` requires the OwnerActor's Owner to be the Controller (automatic for PlayerState; for pawn-ASC the pawn gets the controller as owner on possession).
- [ ] PlayerState `SetNetUpdateFrequency(100.f)` (default 1 Hz -> laggy attributes/tags).
- [ ] Grant abilities on the server only (`GiveAbility`), once (guard against re-granting on respawn).
- [ ] Every ability path ends in `EndAbility` (also on cancel/fail), `CommitAbility` checked.
- [ ] AttributeSets created as default subobjects of the ASC's owner actor (constructor) or added via `AddAttributeSetSubobject`.

Version traps: UE 5.5 removed `NonInstanced` abilities (use `InstancedPerActor`) and deprecated direct `AbilityTags` (use `GetAssetTags()`/`SetAssetTags()` in ctor). UE 5.3 moved most GameplayEffect settings into GE Components (`UTargetTagsGameplayEffectComponent`, `UImmunityGameplayEffectComponent`, ...). UE 5.7 deprecated direct `StackingType` access (`GetStackingType()`) and the replicated-loose-tag containers (use `AddLooseGameplayTag(Tag, Count, EGameplayTagReplicationState::...)`). Full GAS guide with code: [references/gas.md](references/gas.md).

## Gameplay Tags

```cpp
// WRONG: string lookup every call; ensures if tag isn't registered
FGameplayTag T = FGameplayTag::RequestGameplayTag(FName("State.Dead"));
// RIGHT: native tags (Header) UE_DECLARE_GAMEPLAY_TAG_EXTERN(TAG_State_Dead);
UE_DEFINE_GAMEPLAY_TAG(TAG_State_Dead, "State.Dead");                // .cpp only (static_assert otherwise)
UE_DEFINE_GAMEPLAY_TAG_COMMENT(TAG_State_Stunned, "State.Stunned", "Cannot act");
```
- `HasTag(A.B)` matches parents: a container with `State.Dead.Burning` HasTag(`State.Dead`) = true. Use `HasTagExact` when you mean exact.
- Tags typed in config/tables must exist in `Config/DefaultGameplayTags.ini` (or tag tables/native tags); otherwise "Requested Gameplay Tag X was not found, tags must be loaded from config or registered as a native tag".
- Tag renames: use the Gameplay Tag redirects in Project Settings (`GameplayTagRedirects`), not delete+recreate.
- `meta=(Categories="Ability")` on `FGameplayTag` properties to filter pickers.

## Subsystems

| Base | Lifetime | Trap |
|---|---|---|
| `UGameInstanceSubsystem` | whole game session | Survives map travel; don't hold actor pointers strongly (use weak). |
| `UWorldSubsystem` (+ `UTickableWorldSubsystem`) | per world | Also created for **editor and preview worlds** — override `DoesSupportWorldType(EWorldType::Type)` to restrict to `Game`/`PIE`. |
| `ULocalPlayerSubsystem` | per local player | Not on dedicated server (no local players). |
| `UEngineSubsystem` / `UEditorSubsystem` | engine / editor | Editor subsystem only in editor module. |

- Mark abstract base subsystems `UCLASS(Abstract)` (otherwise instantiated too); override `ShouldCreateSubsystem` for conditional creation.
- Depend on another subsystem in `Initialize`: `Collection.InitializeDependency<UOtherSubsystem>();`.
- Not replicated. For networked state use GameState/PlayerState actors.
- PIE vs packaged init order differs (UE-186247) — don't assume world subsystems exist during `UGameInstance::Init`.

## Data assets, Asset Manager, soft references

```cpp
// WRONG: hard ref to every item mesh -> everything loads with the first item
UPROPERTY(EditDefaultsOnly) TObjectPtr<UStaticMesh> Mesh;
// RIGHT for optional/large content
UPROPERTY(EditDefaultsOnly) TSoftObjectPtr<UStaticMesh> Mesh;

// WRONG: handle not stored -> asset may be GC'd right after callback; or LoadSynchronous in gameplay hitch path
UAssetManager::GetStreamableManager().RequestAsyncLoad(Mesh.ToSoftObjectPath(), FStreamableDelegate::CreateUObject(this, &AMyActor::OnLoaded));
// RIGHT
LoadHandle = UAssetManager::GetStreamableManager().RequestAsyncLoad(      // TSharedPtr<FStreamableHandle> member
    Mesh.ToSoftObjectPath(), FStreamableDelegate::CreateUObject(this, &AMyActor::OnLoaded));
void AMyActor::OnLoaded() { if (UStaticMesh* M = Mesh.Get()) { MeshComp->SetStaticMesh(M); } }
```
- Primary data assets need a `PrimaryAssetTypesToScan` entry (Project Settings > Asset Manager) or `GetPrimaryAssetIdList`/`LoadPrimaryAsset` return nothing and the assets may not be cooked.
- `UPrimaryDataAsset::GetPrimaryAssetId()` uses the asset's class: a Blueprint subclass of your data asset class changes the type name — override `GetPrimaryAssetId()` to return a fixed type.
Details + code: [references/assets-and-loading.md](references/assets-and-loading.md).

## UMG / CommonUI

```cpp
// WRONG: name differs from designer widget -> BP compile error "A required widget binding "X" of type ... was not found."
UPROPERTY(meta=(BindWidget)) TObjectPtr<UTextBlock> HealthTxt;     // designer widget is "HealthText"
// WRONG: animation binding without Transient
UPROPERTY(meta=(BindWidgetAnim)) TObjectPtr<UWidgetAnimation> FadeIn;
// RIGHT
UPROPERTY(meta=(BindWidget)) TObjectPtr<UTextBlock> HealthText;
UPROPERTY(Transient, meta=(BindWidgetAnim)) TObjectPtr<UWidgetAnimation> FadeIn;
```
- `NativeOnInitialized` runs once; `NativeConstruct` runs **every** time the widget is added to a parent/viewport — bind delegates in `NativeOnInitialized` or unbind in `NativeDestruct`, otherwise double bindings.
- `CreateWidget<UMyWidget>(PlayerController, Class)` with the owning PC; create UI only where `IsLocalController()`; never on dedicated server.
- `RemoveFromParent()` doesn't destroy; keep a `UPROPERTY` ref if you re-add, drop it to let GC free it.
- CommonUI: set Game Viewport Client Class to `CommonGameViewportClient`, use activatable widget stacks, override `GetDesiredInputConfig()` instead of calling `SetInputMode*` manually.
Details: [references/ui-umg-commonui.md](references/ui-umg-commonui.md).

## World Partition / One File Per Actor

- OFPA stores each placed actor in `Content/__ExternalActors__/...` (and `__ExternalObjects__`); the `.umap` is a shell. Commit/lock those folders — forgetting them = empty level for others; renaming a map without them loses actors.
- Actors referenced by an always-loaded actor are pulled into the same loading set; hard references between spatially loaded actors defeat streaming. Use soft refs or tags/lookup.
- An actor in an unloaded cell doesn't exist — `GetAllActorsOfClass` / stored pointers miss or become null; use `TWeakObjectPtr`/`TSoftObjectPtr<AActor>` and handle null.
- Set "Is Spatially Loaded" off for managers that must always exist (or put them in GameMode/GameState/subsystems).
- Server: `wp.Runtime.EnableServerStreaming` defaults to 0 (UE 5.7 source) -> dedicated server loads the whole partitioned world; client streaming follows player streaming sources.
- Level Blueprint logic doesn't scale with WP; prefer actors/subsystems.

## StateTree, Smart Objects, Mass, Mover (brief traps)

- StateTree: modules `StateTreeModule` + `GameplayStateTreeModule`; plugins StateTree + GameplayStateTree. Pick the matching schema (component vs AI component); after changing C++ task/condition structs recompile the StateTree asset. C++ tasks are USTRUCTs with a separate instance-data struct — don't store per-run state in the task struct itself.
- Smart Objects: plugin SmartObjects, module `SmartObjectsModule`; always release claimed slots (failure paths too) or the slot stays occupied.
- Mass (MassEntity/MassGameplay): large API churn between versions (e.g. 5.8 composition/bitset accessor changes); avoid for a small project unless thousands of agents are needed.
- Mover: still experimental in 5.8 (didn't reach beta); APIs and data formats change between versions. Use CharacterMovementComponent for shipping multiplayer characters.

## References

- [references/gas.md](references/gas.md) — GAS setup code (PlayerState ASC), AttributeSet macros, clamping hooks, GE components, deprecations per version, common GAS errors. Read before writing any GAS code.
- [references/enhanced-input.md](references/enhanced-input.md) — input setup, modifiers, rebinding/user settings, version changes.
- [references/assets-and-loading.md](references/assets-and-loading.md) — Asset Manager config, primary assets, async loading, cooking rules.
- [references/ui-umg-commonui.md](references/ui-umg-commonui.md) — widget lifecycle, bindings, CommonUI input routing.
- [references/sources.md](references/sources.md) — sources.
