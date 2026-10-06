# Core C++ errors: message -> cause -> fix

Match on the quoted fragment (paths/names vary). Linker (LNK) and UBT errors live in `ue5-build-and-modules/references/common-errors.md`.

## UnrealHeaderTool (UHT)

| Message (fragment) | Cause | Fix |
|---|---|---|
| `#include found after .generated.h file - the .generated.h file should always be the last #include in a header` | Include placed after `X.generated.h` | Move `#include "X.generated.h"` to be the last include. |
| `No #include found for the .generated.h file` | Reflected type in header without its generated include | Add `#include "<FileName>.generated.h"` (file name, not class name). |
| `Expected a GENERATED_BODY() at the start of the class` (or similar) | `GENERATED_BODY()` missing / not first in body | Put `GENERATED_BODY()` as first statement in UCLASS/USTRUCT/UINTERFACE body (and in the `I` interface class). |
| `BlueprintReadWrite should not be used on private members` / `BlueprintReadOnly should not be used on private members` | Private/protected-without-meta property exposed to BP | Add `meta=(AllowPrivateAccess="true")` or make it protected/public. |
| `Invalid BlueprintType enum base - currently only uint8 supported` (wording may vary) | `UENUM(BlueprintType)` with non-`uint8` base | `enum class EFoo : uint8`. |
| `Unable to find 'class', 'delegate', 'enum', or 'struct' with name 'X'` | Type used in a reflected signature is not reflected or its header isn't included | Include the header that declares it (structs by value need full include), or make the type a USTRUCT/UENUM. |
| `Unrecognized type 'X' - type must be a UCLASS, USTRUCT, UENUM, or global delegate` | Non-reflected type in UPROPERTY/UFUNCTION signature | Remove UPROPERTY/UFUNCTION or reflect the type; for `std::` types use UE containers. |
| UHT/compile error on a `UObject` member/param declared by value | UObjects can't be values | Always pointers (`TObjectPtr<T>` members, `T*` params). |
| `'X' must not be declared ... nested containers` / `The type 'TArray<TArray<...>>' can not be used` | Nested containers in UPROPERTY | Wrap inner container in a USTRUCT. |
| `Replicated TMap/TSet are not supported` (wording varies) | `Replicated` on TMap/TSet | Replicate a `TArray` of structs (or FastArraySerializer). |
| `Function 'Foo' ... BlueprintPure ... must have a return value` (wording varies) | `BlueprintPure` on void function | Return a value or use `BlueprintCallable`. |
| `Class name prefix ... should be ...` (wording varies) | `U`/`A` prefix doesn't match base class | `A` for AActor-derived, `U` for other UObjects. |
| `'X.generated.h' already included, missing '#pragma once' in X.h` | Header guard missing | Add `#pragma once` as first line. |
| UHT error about `BlueprintNativeEvent` function defined in header | You wrote a body for `Foo()` | Implement only `Foo_Implementation()` in .cpp. UHT generates `Foo()`. |
| `Cannot expose property to blueprints in a struct that is not a BlueprintType` | BP specifier on member of non-BP struct | `USTRUCT(BlueprintType)`. |

## Compiler (MSVC/Clang) in core code

| Message (fragment) | Cause | Fix |
|---|---|---|
| `Invalid argument(s) passed to FString::Printf` / `... FMsg::Logf` (static_assert) | FString (not `*Str`) or other non-POD passed to printf-style varargs | Pass `*MyString`, `*GetNameSafe(Obj)`, numeric types. |
| `Formatting string must be a TCHAR array` / `... const TCHAR array` | Format arg is a runtime `FString`/`TCHAR*` | Use `TEXT("%s"), *Str`. |
| `A call to an immediate function is not a constant expression` (UE 5.8+) | Checked format strings: specifier count/type mismatch, or non-literal format | Fix specifiers (`%d` int32, `%lld` int64, `%f` float/double, `%s` `TCHAR*`); use `UE_LOGFMT`/`FString::Format` for dynamic patterns. |
| `C4996 ... has been deprecated ... Please update your code to the new API before upgrading to the next release` | `UE_DEPRECATED` API used | Use the replacement named in the message; see `ue5-version-notes`. |
| `C2248 cannot access private/protected member` on engine members (e.g. `NetUpdateFrequency`, `bReplicates` outside subclass) | Member made private in a newer version | Use setter/getter (e.g. `SetNetUpdateFrequency()`, UE 5.5+). |
| `C2027 use of undefined type 'UFoo'` | Only forward-declared | `#include` the full header in the .cpp. |
| `C2664 ... cannot convert argument ... TObjectPtr` | Passing `TObjectPtr<T>&`/containers where `T*` expected | `.Get()`, or `MutableView(Array)`/`ToRawPtrTArrayUnsafe` (latter deprecated for mutable arrays in 5.6). |
| `C4458 declaration of 'X' hides class member` (as error) | Shadowing; UE treats as error | Rename local/param. |
| `C4668 'FOO' is not defined as a preprocessor macro, replacing with '0'` | `#if FOO` with undefined macro (error with newer build settings) | Define the macro in all configurations or use `#ifdef`/`defined()`. |
| `error: no member named 'Super'` / `Super` ambiguity | Missing `GENERATED_BODY()` | Add it. |

## Runtime (log / crash)

| Message (fragment) | Cause | Fix |
|---|---|---|
| `Unable to bind delegate to 'X' (function might not be marked as a UFUNCTION or object may be pending kill)` | `AddDynamic` to non-UFUNCTION or invalid object | Mark handler `UFUNCTION()`; bind on a valid object. |
| `Ensure condition failed: InvocationList[ CurFunctionIndex ] != InDelegate` | Same dynamic delegate bound twice | `AddUniqueDynamic`, or `RemoveDynamic` first / bind once. |
| `FObjectFinders can't be used outside of constructors to find <path>` (Fatal) | `ConstructorHelpers` outside a constructor | Use in constructor only, or `LoadObject`/soft refs at runtime. |
| `Failed to find object 'Class /Script/...'` / `CDO Constructor (X): Failed to find /Game/...` | Asset path in `ConstructorHelpers` wrong/moved, or missing `_C` for BP classes | Fix path (`/Game/Dir/Asset.Asset`; BP class: `/Game/Dir/BP_X.BP_X_C`); better: EditDefaultsOnly property. |
| `Access violation reading location 0x...` in your code after time/level change | Dangling raw UObject pointer (no UPROPERTY) or destroyed actor used | `UPROPERTY()`/`TWeakObjectPtr`, `IsValid()` checks, clear timers in `EndPlay`. |
| `Old World ... not cleaned up by garbage collection` / `World Memory Leaks` | Something (rooted object, static, `TStrongObjectPtr`, delegate in long-lived object) references the old world | Remove the reference on `EndPlay`/world cleanup; avoid `AddToRoot`; use weak refs in subsystems/statics. |
| `Requested Gameplay Tag X was not found, tags must be loaded from config or registered as a native tag` | Tag not registered | Add to `DefaultGameplayTags.ini`/tag table or `UE_DEFINE_GAMEPLAY_TAG`. |
| Crash/assert when calling `CreateDefaultSubobject` outside a constructor | Only valid during construction | Runtime: `NewObject<T>(Owner)` + `RegisterComponent()`. |
| `Assertion failed: IsInGameThread()` | UObject/engine API touched from worker thread (Async, TaskGraph) | Marshal back with `AsyncTask(ENamedThreads::GameThread, ...)`; capture weak pointers. |
| `SetReplicates called on actor 'X' that is not valid for having its role modified.` | `SetReplicates` on a client copy | Call on the server (authority) only; in ctor use `bReplicates = true`. |
