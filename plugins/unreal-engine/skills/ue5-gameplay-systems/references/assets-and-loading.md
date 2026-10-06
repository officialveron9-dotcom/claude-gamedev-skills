# Data assets, Asset Manager, soft references, async loading

## Choosing the container

| Need | Use | Trap |
|---|---|---|
| Static tuning data per item/enemy type | `UPrimaryDataAsset` subclass (C++), instances in Content Browser | Hard refs inside it load everything it references when it loads. |
| Spreadsheet-like rows | `UDataTable` with a `USTRUCT : FTableRowBase` | Row struct changes break CSV import; `FindRow` needs the context string; row names are `FName`. |
| Single global settings | `UDeveloperSettings` subclass (`Config=Game`, `defaultconfig`) | Read via `GetDefault<UMySettings>()`; asset refs in it should be soft and loaded explicitly. |
| Runtime mutable state | UObject/struct in a subsystem/actor | Never mutate data assets at runtime (changes leak into the asset in PIE). |

## Primary assets & Asset Manager

```cpp
UCLASS()
class UItemData : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditDefaultsOnly) FText DisplayName;
    UPROPERTY(EditDefaultsOnly, meta=(AssetBundles="World")) TSoftObjectPtr<UStaticMesh> WorldMesh;
    UPROPERTY(EditDefaultsOnly, meta=(AssetBundles="UI")) TSoftObjectPtr<UTexture2D> Icon;

    // Fixed type even for Blueprint subclasses of UItemData (default would use the instance's class name, e.g. "BP_Weapon_C")
    virtual FPrimaryAssetId GetPrimaryAssetId() const override { return FPrimaryAssetId(TEXT("Item"), GetFName()); }
};
```
DefaultGame.ini (or Project Settings > Game > Asset Manager > Primary Asset Types to Scan):
```ini
[/Script/Engine.AssetManagerSettings]
+PrimaryAssetTypesToScan=(PrimaryAssetType="Item",AssetBaseClass="/Script/MyGame.ItemData",bHasBlueprintClasses=False,bIsEditorOnly=False,Directories=((Path="/Game/Items")),Rules=(Priority=-1,ChunkId=-1,bApplyRecursively=True,CookRule=AlwaysCook))
```
Traps:
- Type in `GetPrimaryAssetId` must equal `PrimaryAssetType` in the scan rule, or the asset isn't found.
- Directory not scanned / wrong base class -> `GetPrimaryAssetIdList` empty in packaged builds even if it works in editor.
- `CookRule` matters: assets only reachable through the Asset Manager are not cooked unless a rule says so (`AlwaysCook`) or they're referenced.
- Custom `UAssetManager` subclass must be set in Project Settings (`AssetManagerClassName`) — otherwise your overrides never run.

Loading:
```cpp
UAssetManager& AM = UAssetManager::Get();
TSharedPtr<FStreamableHandle> H = AM.LoadPrimaryAsset(FPrimaryAssetId("Item", "DA_Sword"), {TEXT("UI")},
    FStreamableDelegate::CreateUObject(this, &UMyInv::OnItemLoaded));
// Keep loaded: store H, or call AM.LoadPrimaryAsset again; AM.UnloadPrimaryAsset(Id) to release.
```

## Soft references & async loading

```cpp
UPROPERTY(EditDefaultsOnly) TSoftObjectPtr<UNiagaraSystem> HitFX;
UPROPERTY(EditDefaultsOnly) TSoftClassPtr<AActor> SpawnClass;
TSharedPtr<FStreamableHandle> LoadHandle;                       // member: keeps assets alive

void AMyActor::PreloadFX()
{
    if (HitFX.IsNull()) return;                                 // unset in editor
    if (HitFX.IsValid()) { OnFXLoaded(); return; }              // already in memory
    LoadHandle = UAssetManager::GetStreamableManager().RequestAsyncLoad(
        HitFX.ToSoftObjectPath(),
        FStreamableDelegate::CreateWeakLambda(this, [this]{ OnFXLoaded(); }));
}
```
Traps:
- `IsNull()` = no path set; `IsValid()`/`Get()` = currently loaded. `Get()` on an unloaded soft ptr returns null — not a bug in the asset.
- Without storing the handle (or holding a hard UPROPERTY ref after load), the asset can be garbage-collected right after the callback.
- `LoadSynchronous()` on the game thread during gameplay causes hitches (and can flush async loading) — OK in editor tools / loading screens only.
- `TSoftClassPtr<AActor>::LoadSynchronous()` returns `UClass*`; spawn with `SpawnActor<AActor>(Class)`.
- Callback may run after the requesting object died — use `CreateUObject`/`CreateWeakLambda`.
- Soft references in cooked content are followed by the cooker (assets get cooked if referenced softly from cooked assets); string paths built at runtime (`FSoftObjectPath(TEXT("/Game/..."))`) are not.
- Blueprint class paths need the `_C` suffix: `/Game/BP/BP_Enemy.BP_Enemy_C`.

## Hard reference chains

- A Blueprint/class default with hard refs loads those assets whenever the class loads (e.g. GameMode -> Character BP -> all weapons -> all meshes). Check with Reference Viewer / Size Map; convert heavy optional refs to soft.
- `TSubclassOf<>` is a hard reference to the class (and its defaults).
- Casting to a Blueprint class in another Blueprint creates a hard dependency; prefer C++ base classes or interfaces.
