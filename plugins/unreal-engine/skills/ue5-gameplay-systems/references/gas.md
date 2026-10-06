# Gameplay Ability System — setup, traps, version changes

Verified against GameplayAbilities headers from UE 5.5-5.7 copies (see sources). 5.8-only items are marked "(third-party audit)".

## ASC on PlayerState (multiplayer players)

```cpp
// AMyPlayerState
AMyPlayerState::AMyPlayerState()
{
    ASC = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("ASC"));
    ASC->SetIsReplicated(true);
    ASC->SetReplicationMode(EGameplayEffectReplicationMode::Mixed);
    Attributes = CreateDefaultSubobject<UMyAttributeSet>(TEXT("Attributes")); // subobject of the ASC OWNER -> auto-registered
    SetNetUpdateFrequency(100.f);   // UE 5.5+ setter; default PlayerState rate is 1 Hz
}
UAbilitySystemComponent* AMyPlayerState::GetAbilitySystemComponent() const { return ASC; }

// AMyCharacter : public ACharacter, public IAbilitySystemInterface
UAbilitySystemComponent* AMyCharacter::GetAbilitySystemComponent() const
{
    const AMyPlayerState* PS = GetPlayerState<AMyPlayerState>();
    return PS ? PS->GetAbilitySystemComponent() : nullptr;
}
void AMyCharacter::PossessedBy(AController* NewController)        // SERVER
{
    Super::PossessedBy(NewController);
    if (AMyPlayerState* PS = GetPlayerState<AMyPlayerState>())
    {
        PS->GetAbilitySystemComponent()->InitAbilityActorInfo(PS, this);
        GrantStartupAbilitiesOnce(PS);                               // GiveAbility only here (server)
    }
}
void AMyCharacter::OnRep_PlayerState()                              // CLIENT
{
    Super::OnRep_PlayerState();
    if (AMyPlayerState* PS = GetPlayerState<AMyPlayerState>())
    {
        PS->GetAbilitySystemComponent()->InitAbilityActorInfo(PS, this);
    }
}
```
Pawn-owned ASC: create on the pawn, `InitAbilityActorInfo(this, this)` in `PossessedBy` (server) and in the client possession path (`AcknowledgePossession` on the PC, or `OnRep_Controller`). AI: same on server only, replication mode `Minimal`.

Traps:
- `Minimal` mode does not work for owned (player) ASCs — engine comment: "this does not work for Owned AbilitySystemComponents (Use Mixed instead)".
- `Mixed` needs the OwnerActor's Owner = Controller. PlayerState satisfies it; a custom owner actor must `SetOwner(Controller)`.
- Respawn: new pawn -> call `InitAbilityActorInfo` again with the new avatar; abilities on PS persist, don't re-grant.
- Abilities that need the avatar (montages, movement) break if `InitAbilityActorInfo` ran before the pawn was possessed.

## AttributeSet

```cpp
UCLASS()
class UMyAttributeSet : public UAttributeSet
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_Health) FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS_BASIC(UMyAttributeSet, Health)            // engine macro in recent UE5 (5.7 headers); older projects define ATTRIBUTE_ACCESSORS themselves
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_MaxHealth) FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS_BASIC(UMyAttributeSet, MaxHealth)
    UPROPERTY(BlueprintReadOnly) FGameplayAttributeData IncomingDamage; // meta attribute: not replicated
    ATTRIBUTE_ACCESSORS_BASIC(UMyAttributeSet, IncomingDamage)

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void PreAttributeChange(const FGameplayAttribute& Attr, float& NewValue) override;
    virtual void PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data) override;
protected:
    UFUNCTION() void OnRep_Health(const FGameplayAttributeData& Old) { GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, Health, Old); }
    UFUNCTION() void OnRep_MaxHealth(const FGameplayAttributeData& Old) { GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, MaxHealth, Old); }
};

void UMyAttributeSet::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);
    DOREPLIFETIME_CONDITION_NOTIFY(UMyAttributeSet, Health, COND_None, REPNOTIFY_Always);   // Always: prediction
    DOREPLIFETIME_CONDITION_NOTIFY(UMyAttributeSet, MaxHealth, COND_None, REPNOTIFY_Always);
}
void UMyAttributeSet::PreAttributeChange(const FGameplayAttribute& Attr, float& NewValue)
{
    Super::PreAttributeChange(Attr, NewValue);
    if (Attr == GetHealthAttribute()) NewValue = FMath::Clamp(NewValue, 0.f, GetMaxHealth()); // clamps CurrentValue only
}
void UMyAttributeSet::PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data)
{
    Super::PostGameplayEffectExecute(Data);                          // server, instant/periodic GEs (BaseValue changes)
    if (Data.EvaluatedData.Attribute == GetIncomingDamageAttribute())
    {
        const float Dmg = GetIncomingDamage(); SetIncomingDamage(0.f);
        SetHealth(FMath::Clamp(GetHealth() - Dmg, 0.f, GetMaxHealth()));
    }
}
```
Traps:
- `PreAttributeChange` clamps the current value only; it doesn't stop BaseValue drift from permanent modifiers — clamp BaseValue in `PreAttributeBaseChange` or `PostGameplayEffectExecute`.
- Don't trigger gameplay events (death etc.) in `PreAttributeChange` — it also runs for aggregator re-evaluations. React in `PostGameplayEffectExecute` (server) or attribute change delegates (`GetGameplayAttributeValueChangeDelegate`).
- Missing `REPNOTIFY_Always` + `GAMEPLAYATTRIBUTE_REPNOTIFY` -> predicted values aren't corrected / UI doesn't update.
- Attribute set not a subobject of the ASC owner -> attributes silently missing (`GetNumericAttribute` returns 0).
- Meta attributes (damage) should not replicate.

## Abilities

- `InstancingPolicy`: `InstancedPerActor` (default choice). `NonInstanced` deprecated/removed in UE 5.5 (CVar `AbilitySystem.Fix.AllowNonInstancedAbilities` only for migration).
- UE 5.5: `AbilityTags` -> `GetAssetTags()`; set defaults in the ctor with `SetAssetTags(...)`. `GetAbilitySystemComponentFromActorInfo_Checked` -> `_Ensured`. `FGameplayAbilitySpec::DynamicAbilityTags` -> `GetDynamicSpecSourceTags()`.
- Always `CommitAbility` (cost+cooldown) and end with `EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled)` on every path (including task failure/cancel delegates); otherwise ability stays active and blocks re-activation.
- Net execution policy: `LocalPredicted` for player actions, `ServerOnly`/`ServerInitiated` for AI/server logic. Predicted abilities spawn projectiles on the server only (`HasAuthority(&CurrentActivationInfo)`).
- `GiveAbility` must run on the server; calling on the client does nothing useful.
- Ability tasks (`UAbilityTask_PlayMontageAndWait`, `WaitGameplayEvent`): call `ReadyForActivation()`; bind all completion delegates (OnCompleted, OnInterrupted, OnCancelled) and end the ability in each.

## Gameplay Effects (UE 5.3+ GE Components)

UE 5.3 deprecated many UGameplayEffect properties in favour of components:
| Old property | Component |
|---|---|
| InheritableOwnedTagsContainer (granted tags) | `UTargetTagsGameplayEffectComponent` (read via `GetGrantedTags()`) |
| InheritableGameplayEffectTags (asset tags) | `UAssetTagsGameplayEffectComponent` (`GetAssetTags()`) |
| Application/Ongoing tag requirements | `UTargetTagRequirementsGameplayEffectComponent` |
| RemoveGameplayEffectsWithTags / RemoveGameplayEffectQuery | `URemoveOtherGameplayEffectComponent` |
| GrantedApplicationImmunityTags/Query | `UImmunityGameplayEffectComponent` |
| ChanceToApplyToTarget | `UChanceToApplyGameplayEffectComponent` |
| ApplicationRequirements | `UCustomCanApplyGameplayEffectComponent` |
| ConditionalGameplayEffects, Premature/Routine expiration effects | `UAdditionalEffectsGameplayEffectComponent` |
| GrantedAbilities | `UAbilitiesGameplayEffectComponent` |
| UIData | `UGameplayEffectUIData` is now a GE component (`FindComponent<UGameplayEffectUIData>()`) |

Other: UE 5.6 `GetModifierMagnitude(int32, bool bFactorInStackCount)` deprecated -> `GetModifierMagnitude(int32)`. UE 5.7 `StackingType` direct access deprecated -> `GetStackingType()`. UE 5.8: `FActiveGameplayEffectHandle(int32)` ctor and global handle map functions deprecated -> `GenerateNewHandle()` (third-party audit).

Traps:
- Execution calculations (`UGameplayEffectExecutionCalculation`) are not predicted; use modifiers/MMCs for predicted changes.
- Instant GEs modify BaseValue; Duration/Infinite modify CurrentValue (removed when the GE ends).
- Applying GEs from client code to others: only server-applied GEs are authoritative; client may only predict within a predicted ability.
- `MakeOutgoingSpec` level and SetByCaller: missing SetByCaller magnitude logs an error and uses 0.

## Tags on the ASC

- Loose tags are local unless you pass a replication state (UE 5.7 headers): `ASC->AddLooseGameplayTag(Tag, 1, EGameplayTagReplicationState::TagOnly)`; states: `None`, `SimulatedTagOnly`, `TagOnly`, `CountToOwner`, `TagAndCountToAll`. `AddReplicatedLooseGameplayTag` route deprecated 5.7 (removed in 5.8 per third-party audit).
- Tag-blocked activation: `ActivationBlockedTags`, `ActivationRequiredTags`, `BlockAbilitiesWithTag`, `CancelAbilitiesWithTag` live on the ability CDO.

## Setup / config traps

- UE 5.3+: `UAbilitySystemGlobals::InitGlobalData()` is called automatically; older guides call it in AssetManager `StartInitialLoading` — not needed anymore.
- UE 5.5+: GAS settings moved to `UGameplayAbilitiesDeveloperSettings` (Project Settings > Gameplay Abilities); direct `UAbilitySystemGlobals` config members deprecated.
- `AbilitySystemGlobalsClassName` override only if you subclass globals.

## Common GAS errors

| Message / symptom | Cause | Fix |
|---|---|---|
| `Can't activate LocalOnly or LocalPredicted ability %s when not local!` | Client never called `InitAbilityActorInfo`, or activation from non-local copy | Init on client (`OnRep_PlayerState`), activate only on locally controlled pawn. |
| Attributes always 0 / `GetNumericAttribute` fails | AttributeSet not owned by ASC owner, or ASC not initialized | Create set as subobject of OwnerActor before `InitAbilityActorInfo`; or `AddAttributeSetSubobject`. |
| Attribute UI updates ~1 s late | PlayerState 1 Hz net update | `SetNetUpdateFrequency(100.f)` on PS. |
| Ability activates once then never again | `EndAbility` not called on some path | End in every delegate (completed/interrupted/cancelled/failed). |
| Cooldown/cost not applied | `CommitAbility` not called or GE missing tags/modifiers | Call `CommitAbility`; cooldown GE needs `UTargetTagsGameplayEffectComponent` granting cooldown tag (5.3+). |
| Effects not visible on simulated proxies | `Mixed`/`Minimal` only send tags/cues to non-owners | Expected; use GameplayCues/tags for others. |
| Compile errors on `NonInstanced`, `AbilityTags`, `StackingType` after upgrade | Version deprecations | See tables above. |
