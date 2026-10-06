---
name: ue5-cpp-core
description: "Pitfalls and correct patterns for core Unreal Engine 5 C++ (UE 5.0-5.8): UObject lifetime and garbage collection (UPROPERTY, TObjectPtr, TWeakObjectPtr, TStrongObjectPtr, FGCObject, AddToRoot, IsValid, dangling pointers), reflection (UCLASS, UPROPERTY, UFUNCTION, USTRUCT, UENUM, GENERATED_BODY, .generated.h last include), constructor vs PostInitializeComponents vs BeginPlay, CreateDefaultSubobject, ConstructorHelpers, delegates (AddDynamic, AddWeakLambda), FString/FName/FText, UE_LOG/UE_LOGFMT format errors, check/ensure/verify, TArray/TMap invalidation, Blueprint interop (BlueprintNativeEvent _Implementation, Execute_ interfaces, meta) and Core Redirects. Use when writing/reviewing Unreal gameplay C++ or on crashes, GC or UHT errors. German triggers: Unreal C++, Absturz, Garbage Collection, Zeiger ungueltig, Blueprint Schnittstelle, Kompilierfehler UHT."
---

# UE5 C++ Core — pitfalls & correct patterns

Target UE 5.8 (current, 2026-10). Untagged statements hold for all UE 5.x.

## Before writing code — checklist

- [ ] Every UObject member that must stay alive is `UPROPERTY()` (prefer `TObjectPtr<T>` members). Raw pointers only for params/locals.
- [ ] Possibly-outliving refs use `TWeakObjectPtr<T>`; lambdas/timers capture weak, not `this`.
- [ ] No `new`/`delete`/`TSharedPtr`/`TUniquePtr` on UObjects.
- [ ] `#include "X.generated.h"` is the last include; `GENERATED_BODY()` is the first line of the body; class has `MYGAME_API` if used outside its module.
- [ ] Constructor: only `CreateDefaultSubobject`, `SetupAttachment`, defaults, tick flags, `bReplicates = true`. Nothing that needs a World.
- [ ] Every lifecycle override calls `Super::` (BeginPlay, EndPlay, Tick, PostInitializeComponents, GetLifetimeReplicatedProps, NativeConstruct...).
- [ ] `IsValid(Obj)` (null + not garbage) for anything destroyable; never `Obj != nullptr` alone.
- [ ] Format strings are `TEXT()` literals with matching specifiers (`%s` gets `*Str`). UE 5.8 rejects mismatches at compile time.

## After writing code — checklist

- [ ] Timers cleared / native delegates removed in `EndPlay` (`GetWorldTimerManager().ClearAllTimersForObject(this)`).
- [ ] No side effects inside `check()` (compiled out in Shipping).
- [ ] No hardcoded asset paths (`ConstructorHelpers`, `LoadObject("/Game/...")`) where an `EditDefaultsOnly` property would do.
- [ ] Renamed any reflected class/property/function/struct/enum? -> add Core Redirect before opening the editor.
- [ ] BP-callable `BlueprintNativeEvent` is invoked via `Foo()` / `IMyInterface::Execute_Foo(Obj)`, never `Foo_Implementation()` directly.

## GC & lifetime — wrong vs right

```cpp
// WRONG: raw member, GC may collect it -> dangling pointer crash minutes later
UMyHelper* Helper;
// RIGHT
UPROPERTY() TObjectPtr<UMyHelper> Helper;

// WRONG: UObject in smart pointer / new
TSharedPtr<UMyHelper> H = MakeShared<UMyHelper>();
// RIGHT
Helper = NewObject<UMyHelper>(this);          // Outer = this (outer does NOT keep it alive; the UPROPERTY does)

// WRONG: lambda captures this; actor destroyed before timer/async callback fires
GetWorldTimerManager().SetTimer(H, [this]{ DoThing(); }, 1.f, false);
// RIGHT
GetWorldTimerManager().SetTimer(H, FTimerDelegate::CreateUObject(this, &AMyActor::DoThing), 1.f, false);
// or for a lambda
Delegate.AddWeakLambda(this, [this]{ DoThing(); });
TWeakObjectPtr<AMyActor> WeakThis(this);
AsyncTask(ENamedThreads::GameThread, [WeakThis]{ if (AMyActor* Self = WeakThis.Get()) Self->DoThing(); });

// Non-UObject holder (plain struct, Slate, module) that must keep a UObject alive
TStrongObjectPtr<UMyHelper> Keep;             // or derive from FGCObject:
class FMyHolder : public FGCObject {
  TObjectPtr<UMyHelper> Obj;
  virtual void AddReferencedObjects(FReferenceCollector& C) override { C.AddReferencedObject(Obj); }
  virtual FString GetReferencerName() const override { return TEXT("FMyHolder"); } // pure virtual, required
};
```
- UE 5.0+: `IsPendingKill()` deprecated -> `IsValid()`; `MarkPendingKill()` -> `MarkAsGarbage()`.
- Garbage elimination (`gc.GarbageEliminationEnabled`, default 1): GC nulls `UPROPERTY` refs to destroyed actors/garbage objects. Non-UPROPERTY raw pointers are **not** nulled.
- `Destroy()` is deferred: the actor is garbage until next GC; `IsValid()` already returns false — stop using it.
- `AddToRoot()` only for true singletons, always paired with `RemoveFromRoot()`. A rooted object that references a World (or whose Outer is a level) causes PIE "World Memory Leaks"/"not cleaned up by garbage collection" errors.
- GC cadence (~60 s or on level load) hides bugs: "works for a minute, then crashes" = missing `UPROPERTY`.
- UE 5.4+ incremental reachability (`gc.AllowIncrementalReachability`, experimental, default 0): never depend on GC timing.

## Reflection traps

```cpp
// WRONG: include after generated.h -> UHT error
#include "MyActor.generated.h"
#include "Components/BoxComponent.h"
// RIGHT: generated.h always last
#include "Components/BoxComponent.h"
#include "MyActor.generated.h"

// WRONG: BP enum not uint8 -> UHT error
UENUM(BlueprintType) enum class EMode : int32 { A, B };
// RIGHT
UENUM(BlueprintType) enum class EMode : uint8 { A, B };

// WRONG: private BP-visible property -> "BlueprintReadOnly should not be used on private members"
private: UPROPERTY(BlueprintReadOnly) int32 Ammo;
// RIGHT
private: UPROPERTY(BlueprintReadOnly, meta=(AllowPrivateAccess="true")) int32 Ammo;

// WRONG: nested container as UPROPERTY (unsupported)
UPROPERTY() TArray<TArray<int32>> Grid;
// RIGHT: wrap inner array in a USTRUCT
USTRUCT() struct FRow { GENERATED_BODY() UPROPERTY() TArray<int32> Cells; };
UPROPERTY() TArray<FRow> Grid;
```
- `TMap`/`TSet` UPROPERTYs cannot replicate. USTRUCTs cannot have `UFUNCTION`s.
- Forward-declare pointer types in headers; by-value struct UPROPERTYs need the full include.
- Default subobject pointers: `VisibleAnywhere`/`VisibleDefaultsOnly`, not `EditAnywhere` (you edit the component, not the pointer).
- Specifier details & meta tags: [references/specifiers-cheatsheet.md](references/specifiers-cheatsheet.md).

## Lifecycle traps (actors)

Order: Constructor (also CDO + editor) -> PostInitProperties -> PostLoad (loaded only) -> OnConstruction (editor, every move) -> PreInitializeComponents -> PostInitializeComponents -> BeginPlay -> ... -> EndPlay.

```cpp
// WRONG: world access / spawning / gameplay in constructor (runs for CDO and in editor)
AMyActor::AMyActor() { GetWorld()->SpawnActor<AFoo>(); Health = GetMaxHealthFromGameMode(); }
// RIGHT
AMyActor::AMyActor() {
  Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
  SetRootComponent(Mesh);
  bReplicates = true;            // runtime toggle: SetReplicates() on the server only
}
void AMyActor::BeginPlay() { Super::BeginPlay(); /* gameplay init here */ }

// WRONG: CreateDefaultSubobject at runtime (only valid inside constructors)
void AMyActor::AddLight() { CreateDefaultSubobject<UPointLightComponent>(TEXT("L")); }
// RIGHT
UPointLightComponent* L = NewObject<UPointLightComponent>(this);
L->SetupAttachment(GetRootComponent());
L->RegisterComponent();
AddInstanceComponent(L);         // optional: show in Details panel

// WRONG: hardcoded asset path, fatal outside ctor ("FObjectFinders can't be used outside of constructors to find ...")
static ConstructorHelpers::FObjectFinder<UStaticMesh> M(TEXT("/Game/Meshes/SM_Rock.SM_Rock"));
// RIGHT: designer-set reference on a BP subclass / data asset
UPROPERTY(EditDefaultsOnly) TSoftObjectPtr<UStaticMesh> RockMesh;
```
- Changing a C++ default does not update instances/BPs that already saved an override. Renaming a subobject `TEXT("Name")` orphans BP child data.
- Bind component delegates (`OnComponentBeginOverlap.AddDynamic`) in `BeginPlay`/`PostInitializeComponents`, not the constructor (unreliable for BP children).
- On clients, replicated values may not be there in `BeginPlay` — react in `OnRep_`.
- PIE vs standalone init order differs (UE-186247): world subsystems of the startup map may exist before `UGameInstance::Init` in PIE only.

## Delegate traps

```cpp
// WRONG: handler not UFUNCTION -> runtime ensure "Unable to bind delegate to '...' (function might not be marked as a UFUNCTION or object may be pending kill)"
void OnHit(UPrimitiveComponent* C, AActor* O, UPrimitiveComponent* OC, FVector N, const FHitResult& H);
// RIGHT
UFUNCTION() void OnHit(UPrimitiveComponent* C, AActor* O, UPrimitiveComponent* OC, FVector N, const FHitResult& H);

// WRONG: binding twice (BeginPlay re-run, respawn) -> ensure in Add (duplicate binding)
OnDeath.AddDynamic(this, &UMyComp::HandleDeath);
// RIGHT
OnDeath.AddUniqueDynamic(this, &UMyComp::HandleDeath);
```
- Dynamic delegates (`DECLARE_DYNAMIC_MULTICAST_DELEGATE_*`) only for `BlueprintAssignable`; native ones (`DECLARE_MULTICAST_DELEGATE_*`) are faster — keep the `FDelegateHandle` and `Remove` it.
- `AddLambda([this]...)` = no lifetime tracking. Use `AddUObject`, `AddWeakLambda`, `AddSP`.

## Strings, logging, asserts

```cpp
// WRONG
UE_LOG(LogTemp, Log, TEXT("Name %s"), Name);   // FString by value -> static_assert "Invalid argument(s) passed to ..."
UE_LOG(LogTemp, Log, *SomeRuntimeString);      // non-literal -> "Formatting string must be a ... TCHAR array"
FString::Printf(TEXT("%d %d"), A);             // count/type mismatch: UE 5.8 compile error
                                               // "A call to an immediate function is not a constant expression"
                                               // (<= 5.7: compiled, printed garbage or crashed)
// RIGHT
UE_LOG(LogMyGame, Log, TEXT("Name %s"), *Name);
UE_LOG(LogMyGame, Log, TEXT("%s"), *SomeRuntimeString);
UE_LOGFMT(LogMyGame, Log, "Hit {Target} for {Dmg}", GetNameSafe(Target), Dmg); // UE 5.2+, #include "Logging/StructuredLog.h"
```
- Custom category: `DECLARE_LOG_CATEGORY_EXTERN(LogMyGame, Log, All);` in a header, `DEFINE_LOG_CATEGORY(LogMyGame);` in exactly one .cpp.
- `FText` for anything shown to players (`LOCTEXT` needs `#define LOCTEXT_NAMESPACE "X"` ... `#undef` in the .cpp). `FName` for identifiers (case-insensitive). `FString` for work strings.
- `check/checkf`: fatal, **expression not evaluated in Shipping**. `verify`: always evaluated. `ensure/ensureMsgf`: non-fatal, returns bool: `if (!ensure(Comp)) { return; }`.

```cpp
// WRONG: side effect disappears in Shipping
check(Inventory->RemoveItem(Id));
// RIGHT
const bool bRemoved = Inventory->RemoveItem(Id); check(bRemoved);   // or verify(Inventory->RemoveItem(Id));
```

## Container traps

```cpp
// WRONG: reference invalidated by reallocation
FItem& First = Items[0]; Items.Add(NewItem); First.Count++;    // dangling
// WRONG: removing while ranged-for
for (FItem& I : Items) if (I.Count == 0) Items.Remove(I);
// RIGHT
Items.RemoveAll([](const FItem& I){ return I.Count == 0; });
for (int32 i = Items.Num() - 1; i >= 0; --i) { if (Items[i].Count == 0) Items.RemoveAtSwap(i); }
```
- `TMap::Find` pointer is invalid after any `Add`/`Remove` on that map.
- UE 5.4+: `EAllowShrinking::No/Yes` replaces bool `bAllowShrinking` (bool overloads warn in game code since 5.6).
- `TSharedPtr` default mode is thread-safe in UE5; use only for non-UObject data.

## Blueprint interop traps

```cpp
// Header
UFUNCTION(BlueprintNativeEvent, BlueprintCallable) void Interact(AActor* By);
// WRONG: defining Interact() yourself, or calling Interact_Implementation() (skips BP override)
// RIGHT
void AMyDoor::Interact_Implementation(AActor* By) { /* default C++ behaviour */ }
Door->Interact(Player);

// Interfaces: WRONG for BP-implemented interfaces (Cast returns null)
if (IInteractable* I = Cast<IInteractable>(Actor)) I->Interact(Player);
// RIGHT
if (Actor->Implements<UInteractable>()) IInteractable::Execute_Interact(Actor, Player);
```
- `BlueprintImplementableEvent`: no C++ body at all.
- `BlueprintPure` nodes re-run per connected output pin; must return a value. `const` BlueprintCallable functions become Pure unless `BlueprintPure=false`.
- Renames need Core Redirects (`DefaultEngine.ini`, `[CoreRedirects]`, names **without** U/A/F prefix): see [references/blueprint-interop.md](references/blueprint-interop.md).

## Naming

`U` UObject, `A` Actor, `S` Slate, `I` interface (native), `F` struct/other, `T` template, `E` enum, `b` bool member. UHT rejects reflected classes whose prefix does not match the base. Keep file name = class name without prefix.

## References

- [references/common-errors.md](references/common-errors.md) — exact UHT/compiler/runtime messages -> cause -> fix. Read first when an error/crash text is pasted.
- [references/specifiers-cheatsheet.md](references/specifiers-cheatsheet.md) — UCLASS/UPROPERTY/UFUNCTION/meta specifiers and their traps. Read when choosing specifiers.
- [references/blueprint-interop.md](references/blueprint-interop.md) — interfaces, function libraries, latent/async nodes, Core Redirect variants. Read when exposing C++ to BP or renaming.
- [references/sources.md](references/sources.md) — sources.
- Other skills: link/build errors -> `ue5-build-and-modules`; replication -> `ue5-multiplayer`; version deltas -> `ue5-version-notes`.
