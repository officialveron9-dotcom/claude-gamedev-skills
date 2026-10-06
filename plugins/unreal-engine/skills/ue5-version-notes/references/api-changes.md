# Code-relevant changes per version (UE 5.0 -> 5.8)

Only changes that affect C++/Build.cs/config you write. "(3p)" = taken from a third-party audit of 5.8 headers (quodsoler/unreal-engine-skills), not independently verified; everything else verified in engine source copies or Epic material (see sources.md).

## 5.0
- Large World Coordinates: `FVector`, `FRotator`, `FQuat`, `FTransform` are double-precision (`UE::Math::TVector<double>`). Use `FVector3f` etc. for float data (GPU, compact network/serialization). Expect double->float conversion warnings.
- `TObjectPtr<T>` for UPROPERTY UObject members (optional in game code, recommended).
- Pending-kill concept removed by default: `IsPendingKill()` deprecated -> `IsValid()`; `MarkPendingKill()` -> `MarkAsGarbage()`.
- Chaos is the only physics backend (PhysX removed).
- Editor binary `UnrealEditor.exe` (was `UE4Editor`), Editor target build config names unchanged.
- Live Coding default; Hot Reload legacy.
- World Partition + One File Per Actor available (default in Open World template).

## 5.1
- Legacy input (Action/Axis mappings, `BindAxis`/`BindAction(FName)`) deprecated -> Enhanced Input.
- `ANY_PACKAGE` deprecated; `StaticFindObjectFast(..., bAnyPackage)` deprecated -> `FindFirstObject<T>()` / full paths.
- Registered replicated subobject list (`bReplicateUsingRegisteredSubObjectList`, `AddReplicatedSubObject`) introduced.
- Iris replication introduced (experimental).
- Data Layers became asset-based (`UDataLayerAsset`); name-based Data Layer actor APIs deprecated.

## 5.2
- `ModuleRules.bEnforceIWYU` obsolete -> `IWYUSupport` ("Deprecated in UE5.2 - Use IWYUSupport instead.").
- `UE_LOGFMT` structured logging (`Logging/StructuredLog.h`).

## 5.3
- C++20 is the default language standard for engine and projects.
- VS 2019 deprecated (removed in 5.4).
- GAS: GameplayEffect components replace many GE properties (`UTargetTagsGameplayEffectComponent`, `UAssetTagsGameplayEffectComponent`, `UTargetTagRequirementsGameplayEffectComponent`, `URemoveOtherGameplayEffectComponent`, `UImmunityGameplayEffectComponent`, `UChanceToApplyGameplayEffectComponent`, `UCustomCanApplyGameplayEffectComponent`, `UAdditionalEffectsGameplayEffectComponent`, `UAbilitiesGameplayEffectComponent`; `UGameplayEffectUIData` is a component). `FGameplayEffectSpec::TargetEffectSpecs` deprecated.
- GAS: `UAbilitySystemGlobals::InitGlobalData()` called automatically.
- Enhanced Input: `UPlayerMappableInputConfig` deprecated -> `UEnhancedInputUserSettings`.
- Replication pausing APIs on AActor deprecated.
- `FReferenceCollector::AddReferencedObject` with raw `UObject*&` members deprecated in favour of `TObjectPtr` members (3p).

## 5.4
- `EAllowShrinking` enum added for `TArray::RemoveAt/Pop/SetNum/...` (bool overloads later deprecated).
- UBT bans MSVC 14.39.33519-14.39.99999.
- Incremental reachability GC (`gc.AllowIncrementalReachability`, experimental).
- `AActor::GetAssetRegistryTags(TArray&)` -> version taking `FAssetRegistryTagsContext`.
- Mover plugin introduced (experimental).

## 5.5
- AActor: `NetUpdateFrequency`, `MinNetUpdateFrequency`, `NetCullDistanceSquared` public access deprecated -> `Set*/Get*` functions.
- AActor: templated `FindComponentByInterface` that cast to the `U` interface type deprecated -> `FindComponentByInterface<IMyInterface>()`.
- GAS: `NonInstanced` abilities removed (CVar `AbilitySystem.Fix.AllowNonInstancedAbilities` for migration); `UGameplayAbility::AbilityTags` -> `GetAssetTags()/SetAssetTags()`; `GetAbilitySystemComponentFromActorInfo_Checked` -> `_Ensured`; `FGameplayAbilitySpec::DynamicAbilityTags` -> `GetDynamicSpecSourceTags()`; `UAbilitySystemBlueprintLibrary::MakeSpecHandle` -> `MakeSpecHandleByClass` (3p); GAS config moved to `UGameplayAbilitiesDeveloperSettings`; `RemoveActiveGameplayEffect_NoReturn` deprecated for game code.
- `EAllowShrinking`: bool overloads deprecated for engine code (`UE_DEPRECATED_FORENGINE`).
- StructUtils plugin deprecated; `FInstancedStruct` and friends live in CoreUObject (include `StructUtils/InstancedStruct.h` unchanged).
- `bUsesSteam` in Target.cs obsolete (3p).

## 5.6
- Engine headers increasingly use `UCLASS(MinimalAPI)` + per-member `UE_API` exports -> calling a non-exported engine member from your module = LNK2019.
- `UClass::ClassDefaultObject` direct access deprecated -> `GetDefault<T>()`/`GetMutableDefault<T>()`/`GetDefaultObject<T>()`.
- `TObjectPtr` construction from a reference deprecated; mutable `ToRawPtrArrayUnsafe()`/`ToRawPtrTArrayUnsafe()` deprecated -> `MutableView()`; swapping/exchanging between `TArray<TObjectPtr<>>` and raw-pointer arrays deprecated.
- `EAllowShrinking` bool overloads now deprecated for game code too (warnings).
- AActor `LastRenderTime` direct access -> `GetLastRenderTime()/SetLastRenderTime()`.
- UBT: warning-level properties moved under `CppCompileWarningSettings` (e.g. `ShadowVariableWarningLevel`, `UnsafeTypeCastWarningLevel`, `DeprecationWarningLevel`) (3p).
- GAS: `FGameplayEffectSpec::GetModifierMagnitude(int32, bool)` -> `GetModifierMagnitude(int32)`.
- Enhanced Input: key profile IDs `FGameplayTag` -> `FString` (`SetActiveKeyProfile`, `GetActiveKeyProfile`, `ProfileIdString`, `SupportedKeyProfileIds`); `GetAppliedInputContexts()` -> `GetAppliedInputContextData()` (3p).
- Networking: `UNetConnection::GetConnectionId()` -> `GetConnectionHandle()`; `UNetDriver::GetConnectionById` -> `GetConnectionByHandle` (3p).
- `meta=(HideAssetPicker)` -> `meta=(HidePinAssetPicker)` (3p).

## 5.7
- Iris: Beta, compiled in, still off by default. `AActor::BeginReplication()`/`EndReplication()` overrides deprecated "as part of iris beta" -> `OnReplicationStartedForIris`, `OnStopReplicationForIris`, `FillReplicationParams`.
- `StaticFindObject`/`FindObject` bool `bExactClass` overloads deprecated -> `EFindObjectFlags::ExactClass`.
- GAS: `UGameplayEffect::StackingType` -> `GetStackingType()`; replicated loose-tag containers deprecated -> `AddLooseGameplayTag(Tag, Count, EGameplayTagReplicationState::TagOnly/CountToOwner/...)`.
- Enhanced Input: `UInputMappingContext::Mappings` -> `DefaultKeyMappings` storage (+ per-profile overrides); use `GetMappings()`/`MapKey()`.
- `FObjectInitializer` remote-object override constructors deprecated (`FRemoteObjectConstructionOverridesScope`) — only matters for engine-level code.
- `TIsConst<T>` deprecated -> `std::is_const_v` (3p); `bUseFastPDBLinking` obsolete (3p).
- Toolchain: MSVC 14.44 preferred; Linux clang 20.1.8 (v26 toolchain); VS 2026 early support with issues.

## 5.8
- Printf-style formatting (`UE_LOG`, `FString::Printf`, ...) validated at compile time: mismatched specifiers/arg counts or non-literal formats fail with "A call to an immediate function is not a constant expression". (`FUtf8String::Printf` with `const UTF8CHAR*` reported rejected — use literals.)
- Target.cs: templates emit `BuildSettingsVersion.V7` and `EngineIncludeOrderVersion.Unreal5_8`; include orders <= 5.5 obsolete.
- `FJsonObject` key type can be `UE::FSharedString` (was `FString`) — code iterating `Values` with explicit `TPair<FString, ...>` may break.
- Iris production-ready (still opt-in).
- Deprecated (3p unless noted): `TMap::TIterator(Map, bRequiresRehashOnRemoval)` -> `CreateIterator()` + manual `Compact()/Shrink()`; `FThreadSafeRefCountedObject`/`FRefCountBase` -> `FRefCountedObject`; `FCoreDelegates::OnPostEngineInit` -> `FCoreDelegates::GetOnPostEngineInit()`; `ProcessMulticastDelegate` -> `ProcessDelegate`; `TObjectPtr::IsRemote()` -> `GetResidence()`; `TIsMemberPointer` -> `std::is_member_pointer_v`; Enhanced Input `UInputTriggerCombo`, `FInputComboStepData`, `FInputCancelAction` (no replacement); GAS `FActiveGameplayEffectHandle(int32)`, `ResetGlobalHandleMap()`, `RemoveFromGlobalMap()` -> `GenerateNewHandle()`; `AddReplicatedLooseGameplayTag` removed; Iris `UObjectReplicationBridge::DetachInstanceFromRemote` -> `DetachRootObjectFromRemote`/`DetachSubObjectFromRemote`.
- `FStringTable` CSV import: bool/`ImportStrings` forms deprecated in favour of `ImportStringsFromCSVFile` (seen in plugin code guards).
- Mass: composition descriptor uses a unified bitset (`GetElementsBitSet()`), old `GetFragments()`-style accessors deprecated (seen in MassAPI plugin guards).
- Release notes also list deprecation of LightWeightInstances code and of `FField` virtuals `Bind()`, `PostLoad()`, `BeginDestroy()` (search excerpt).
- Toolchain: VS 2026 recommended, VS 2022 17.14+ minimum, MSVC 14.38 min / 14.50 recommended.
