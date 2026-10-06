---
name: ue5-version-notes
description: Version-specific Unreal Engine 5 coding facts from UE 5.0 to the current UE 5.8 (2026): deprecated/removed/renamed C++ APIs with replacements and the version they changed (NetUpdateFrequency setters, NonInstanced abilities, AbilityTags, StackingType, EAllowShrinking, ANY_PACKAGE, FindObject ExactClass flags, IsPendingKill, legacy input, UInputMappingContext Mappings, ClassDefaultObject, bEnforceIWYU, BuildSettingsVersion/IncludeOrderVersion), new defaults (C++20, Iris opt-in, compile-time checked format strings in 5.8), upgrade checklist (5.x -> 5.8), version-guard macros, and known 5.7/5.8 bugs with workarounds (VS 2026 detection, hash_map, plugin binaries). Use when code targets a specific engine version, after an engine upgrade, when C4996 deprecation warnings or "is not a member" errors appear, or when unsure whether an API exists in the user's version. German triggers: Unreal Version, veraltet, deprecated Warnung, Engine Upgrade, nach dem Update kaputt, Unreal 5.8.
---

# UE5 version notes (5.0 -> 5.8) — for coding

Current: **UE 5.8** (5.8.0 released 2026-06-17; hotfixes 5.8.1 2026-07-28, 5.8.2 2026-08-31, 5.8.3 after). Epic called 5.8 the last *planned* UE5 release; a 5.9 has been mentioned but was not released as of 2026-10. UE6 (Verse/Scene Graph) targets Early Access end of 2027 — irrelevant for current C++ code.

## Before writing code

- [ ] Read `EngineAssociation` in the `.uproject` (e.g. `"5.8"`); don't emit APIs newer than that version, and don't emit APIs deprecated at/before it.
- [ ] Unsure whether an API exists/changed? Grep the engine header for the symbol and `UE_DEPRECATED(` near it; the message names the replacement.
- [ ] Code that must compile on several versions:
```cpp
#include "Misc/EngineVersionComparison.h"
#if UE_VERSION_OLDER_THAN(5, 5, 0)
    NetUpdateFrequency = 30.f;
#else
    SetNetUpdateFrequency(30.f);
#endif
// or: #if ENGINE_MAJOR_VERSION == 5 && ENGINE_MINOR_VERSION >= 5   (Runtime/Launch/Resources/Version.h)
```

## "Don't emit -> emit instead" (most common Claude mistakes)

| Don't write | Write | Since |
|---|---|---|
| `BindAxis`/`BindAction(FName, ...)`, project Action/Axis mappings | Enhanced Input (`UInputAction`, `UInputMappingContext`, `UEnhancedInputComponent::BindAction`) | 5.1 deprecated |
| `IsPendingKill()`, `MarkPendingKill()` | `IsValid(Obj)`, `MarkAsGarbage()` | 5.0 |
| `FindObject<T>(ANY_PACKAGE, Name)` | `FindFirstObject<T>(Name, EFindFirstObjectOptions::NativeFirst)` or full path | 5.1 |
| `FindObject<T>(Outer, Name, true)` / `StaticFindObject(..., bExactClass)` | `EFindObjectFlags::ExactClass` | 5.7 |
| `Arr.Pop(false)`, `RemoveAt(i, 1, false)`, `SetNum(n, false)` | `EAllowShrinking::No` | 5.4 added; bool overloads warn for game code since 5.6 |
| `NetUpdateFrequency = X`, `MinNetUpdateFrequency = X`, `NetCullDistanceSquared = X` | `SetNetUpdateFrequency()`, `SetMinNetUpdateFrequency()`, `SetNetCullDistanceSquared()` (+ getters) | 5.5 |
| `EGameplayAbilityInstancingPolicy::NonInstanced` | `InstancedPerActor` | 5.5 (removed) |
| `UGameplayAbility::AbilityTags` | `GetAssetTags()` / `SetAssetTags()` (ctor) | 5.5 |
| GE properties `InheritableOwnedTagsContainer`, `RemoveGameplayEffectsWithTags`, `GrantedApplicationImmunityTags`, `ConditionalGameplayEffects`, `GrantedAbilities`, `UIData` ... | GameplayEffect components (`UTargetTagsGameplayEffectComponent`, ...) | 5.3 |
| `GE->StackingType` | `GE->GetStackingType()` | 5.7 |
| `UInputMappingContext::Mappings` direct access | `GetMappings()` / `MapKey()` / `UnmapKey()` (`DefaultKeyMappings`) | 5.7 |
| `UPlayerMappableInputConfig` | `UEnhancedInputUserSettings` | 5.3 |
| `SomeClass->ClassDefaultObject` | `GetDefault<T>()`, `GetMutableDefault<T>()`, `Class->GetDefaultObject<T>()` | 5.6 |
| `ToRawPtrArrayUnsafe(MutableArray)` on `TArray<TObjectPtr<>>` | `MutableView(Array)` | 5.6 |
| `AActor::BeginReplication()`/`EndReplication()` overrides | `OnReplicationStartedForIris` / `OnStopReplicationForIris` / `FillReplicationParams` | 5.7 |
| `bEnforceIWYU = true` (Build.cs) | `IWYUSupport = IWYUSupport.Full` | 5.2 |
| `ShadowVariableWarningLevel = ...` etc. on Module/TargetRules | `CppCompileWarningSettings.ShadowVariableWarningLevel` | 5.6 |
| `StructUtils` module/plugin dependency | nothing (`FInstancedStruct` in CoreUObject; include path unchanged) | 5.5 |
| `UAbilitySystemGlobals::Get().InitGlobalData()` in AssetManager | nothing (automatic) | 5.3 |
| Printf/UE_LOG with mismatched specifiers or runtime format | matching literal format / `UE_LOGFMT` | 5.8 (compile error) |
| `IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_1..Unreal5_5` | `Unreal5_8` or `Latest` (with `BuildSettingsVersion.V7`/`Latest`) | 5.8 |

Full table incl. less common APIs and per-version defaults: [references/api-changes.md](references/api-changes.md).

## Upgrade checklist (any 5.x -> 5.8)

1. Commit/back up; close editor.
2. Install toolchain for 5.8 (VS 2022 17.14+ or VS 2026, MSVC >= 14.38 — see ue5-build-and-modules), then switch engine version (right-click .uproject).
3. Update both Target.cs files (`BuildSettingsVersion.V7`/`Latest`, `EngineIncludeOrderVersion.Unreal5_8`/`Latest`).
4. Delete `Binaries/`, `Intermediate/`, `.vs/` (+ plugin Binaries/Intermediate), regenerate project files, build Development Editor from IDE.
5. Fix errors, then treat C4996 deprecation warnings as to-do list (they become errors next version).
6. Rebuild/upgrade code plugins (Fab plugins need the 5.8 build).
7. Open editor, check Output Log/Message Log for asset load errors and Blueprint compile errors before saving anything; resave/fix redirectors.
8. Package a Development build (game target catches editor-only code) and test multiplayer in Play As Client.

## Known issues (5.7/5.8) — quick list

| Issue | Workaround |
|---|---|
| 5.8 + VS 2026: "Visual Studio 2022 x64 must be installed in order to build this target" | Remove forced compiler (`BuildConfiguration.xml`, project/plugin Target.cs); install C++ workload + MSVC toolset in VS 2026. |
| 5.8 source build + VS 2026: `nvtess.h ... Cannot open include file: 'hash_map'` | Patch header (community fix) or use VS 2022 toolset. |
| 5.8 upgrade: `A call to an immediate function is not a constant expression` in old plugins | Fix printf specifiers/arguments. |
| 5.8 upgrade: code iterating `FJsonObject::Values` with `FString` keys fails | Key type changed (supports `UE::FSharedString`); use `auto&` / accessor functions, adapt key type. |
| 5.8: non-editor builds crash at startup (`xSharedMemoryException`) after upgrade | Clean Binaries/Intermediate/Saved/DDC/.vs, regenerate, rebuild. |
| 5.8 custom installed builds reject plugin binaries built against earlier 5.8.x (BuildId mismatch) | Rebuild plugins per hotfix (Launcher builds not affected per report). |
| 5.7 + VS 2026 project generation fails due to a plugin Target.cs forcing VS2022 | Remove the forced compiler line / BuildConfiguration.xml. |
More: [references/known-issues.md](references/known-issues.md).

## References

- [references/api-changes.md](references/api-changes.md) — per-version table of code-relevant changes (5.0-5.8). Read when upgrading or when a symbol is missing/deprecated.
- [references/known-issues.md](references/known-issues.md) — bugs/regressions with exact symptoms and workarounds.
- [references/sources.md](references/sources.md) — sources.
