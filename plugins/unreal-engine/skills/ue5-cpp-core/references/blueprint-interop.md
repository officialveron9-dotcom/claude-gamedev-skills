# Blueprint <-> C++ interop: patterns and traps

## Event hooks C++ -> BP

```cpp
// BP may implement, C++ has no default:
UFUNCTION(BlueprintImplementableEvent, Category="Combat") void OnDamaged(float Amount);
// C++ default, BP may override (call Super via "Parent" node in BP):
UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Combat") float ModifyDamage(float In);
float AMyChar::ModifyDamage_Implementation(float In) { return In; }

// C++ subclass override of a native event: override the _Implementation
virtual float ModifyDamage_Implementation(float In) override;
```
Traps:
- Calling `ModifyDamage_Implementation()` directly skips Blueprint overrides.
- In the declaring class UHT generates the `_Implementation` declaration (declaring it yourself is optional); in C++ subclasses declare `virtual ... _Implementation(...) override`.
- BP events on actors fire only after `BeginPlay` has routed through `Super::BeginPlay()`.

## Interfaces

```cpp
UINTERFACE(MinimalAPI, Blueprintable)
class UInteractable : public UInterface { GENERATED_BODY() };

class MYGAME_API IInteractable
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Interact")
    void Interact(AActor* Instigator);
    // pure C++-only virtual is fine too, but invisible to BP and not implementable by BP classes:
    virtual bool CanInteractNative() const { return true; }
};

// Call site — works for C++ AND Blueprint implementers
if (Target && Target->Implements<UInteractable>())
{
    IInteractable::Execute_Interact(Target, this);
}
```
Traps:
- `Cast<IInteractable>(Obj)` and `Obj->GetInterface...` return null for Blueprint-only implementations; `Execute_` is mandatory for BP-implementable functions.
- `TScriptInterface<IInteractable>` for UPROPERTY storage; check `GetObject()` validity.
- Interface `UFUNCTION`s must be `BlueprintNativeEvent`/`BlueprintImplementableEvent` (or not UFUNCTION at all) if the interface is `Blueprintable`.
- `Implements<U...>()` takes the `U` class, `Execute_` lives on the `I` class.

## Function libraries

```cpp
UCLASS()
class MYGAME_API UMyGameStatics : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="MyGame", meta=(WorldContext="WorldContextObject"))
    static AMyGameState* GetMyGameState(const UObject* WorldContextObject);
};
// .cpp: GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull)
```
- Without `WorldContext` meta, static helpers that need a world fail in BP function libraries/objects without world.

## Async BP nodes (preferred over latent meta)

```cpp
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDone, bool, bSuccess);
UCLASS()
class UWaitForThing : public UBlueprintAsyncActionBase
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintAssignable) FOnDone OnDone;
    UFUNCTION(BlueprintCallable, meta=(BlueprintInternalUseOnly="true", WorldContext="WorldContextObject"))
    static UWaitForThing* WaitForThing(UObject* WorldContextObject);
    virtual void Activate() override;   // start work here; call SetReadyToDestroy() when finished
};
```
- Register with a game instance/world (`RegisterWithGameInstance`) or keep it referenced; otherwise GC can collect it mid-wait.

## Exposing data

- Expose state via `BlueprintReadOnly` + `BlueprintCallable` setters that validate (and replicate/mark dirty), not `BlueprintReadWrite`.
- `BlueprintGetter=Fn` / `BlueprintSetter=Fn` on a UPROPERTY route BP access through functions.
- Spawn parameters: `meta=(ExposeOnSpawn=true)` + `SpawnActorDeferred<T>()` / `FinishSpawning()` in C++ when values must be set before `BeginPlay`/construction script.

## Renaming reflected symbols (Core Redirects)

Add to `Config/DefaultEngine.ini` **before** opening the editor with the renamed code, then open, resave referencing assets (or run a "Resave packages"/fix-up), then optionally delete the redirect.

```ini
[CoreRedirects]
+ClassRedirects=(OldName="/Script/MyGame.OldName",NewName="/Script/MyGame.NewName")
+StructRedirects=(OldName="/Script/MyGame.OldStruct",NewName="/Script/MyGame.NewStruct")
+EnumRedirects=(OldName="/Script/MyGame.EOld",NewName="/Script/MyGame.ENew",ValueChanges=(("OldValue","NewValue")))
+PropertyRedirects=(OldName="/Script/MyGame.MyClass.OldProp",NewName="/Script/MyGame.MyClass.NewProp")
+FunctionRedirects=(OldName="/Script/MyGame.MyClass.OldFunc",NewName="/Script/MyGame.MyClass.NewFunc")
+PackageRedirects=(OldName="/Game/Old/Path",NewName="/Game/New/Path")
```
Traps:
- Type names drop the `U`/`A`/`F` prefix (`AEnemyBase` -> `EnemyBase`); enums keep the `E`.
- Moving a class to another module = class redirect with the new `/Script/NewModule.` path.
- PropertyRedirects use the **owning class** path; for struct members use the struct path.
- Without a redirect, Blueprints show "Unknown class"/broken pins and child BPs reparent to nothing — data loss on save. Don't save broken BPs; add redirect, restart editor.
- Renaming a UPROPERTY also changes its serialized name in level/save data — redirect it even if no BP uses it.
