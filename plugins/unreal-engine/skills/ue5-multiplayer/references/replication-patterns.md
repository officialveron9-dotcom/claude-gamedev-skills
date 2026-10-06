# Replication patterns (correct code)

All snippets UE 5.5+ (setter APIs). Includes: `Net/UnrealNetwork.h`; push model also `Net/Core/PushModel/PushModel.h` + `NetCore` module.

## 1. Replicated pickup actor (server-spawned, OnRep-driven visuals)

```cpp
UCLASS()
class MYGAME_API APickup : public AActor
{
    GENERATED_BODY()
public:
    APickup();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    void Collect(APawn* By);                         // server only
protected:
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(ReplicatedUsing=OnRep_Collected) bool bCollected = false;
    UFUNCTION() void OnRep_Collected();
};

APickup::APickup()
{
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    SetRootComponent(Mesh);
    bReplicates = true;
    SetNetUpdateFrequency(10.f);                     // UE 5.5+ setter
}

void APickup::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);
    DOREPLIFETIME(APickup, bCollected);
}

void APickup::Collect(APawn* By)
{
    if (!HasAuthority() || bCollected) return;
    bCollected = true;
    OnRep_Collected();                               // server/listen host needs it too
    SetLifeSpan(2.f);                                // destroy later so clients receive bCollected
}

void APickup::OnRep_Collected()
{
    Mesh->SetVisibility(!bCollected);                // cosmetic, runs everywhere
}
```
Trap: `Destroy()` immediately after a property change — the client may never receive the change; tear-off (`TearOff()`) or delayed destroy if clients need the final state.

## 2. Client interacts with a world actor it doesn't own

```cpp
// WRONG: Server RPC on the door (owned by nobody) -> "No owning connection for actor Door. Function ServerOpen will not be processed."
Door->ServerOpen();

// RIGHT: route through something the client owns
UFUNCTION(Server, Reliable) void ServerInteract(AActor* Target);          // on AMyPlayerController or the Pawn
void AMyPlayerController::ServerInteract_Implementation(AActor* Target)
{
    if (!IsValid(Target) || !GetPawn()) return;
    if (FVector::DistSquared(Target->GetActorLocation(), GetPawn()->GetActorLocation()) > FMath::Square(300.f)) return; // validate
    if (Target->Implements<UInteractable>()) IInteractable::Execute_Interact(Target, GetPawn());
}
```
Alternatively `Target->SetOwner(PC)` on the server (only if exactly one player should own it).

## 3. Replicated actor component

```cpp
UHealthComponent::UHealthComponent()
{
    SetIsReplicatedByDefault(true);                 // ctor API; SetIsReplicated() is for runtime
    PrimaryComponentTick.bCanEverTick = false;
}
void UHealthComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);
    DOREPLIFETIME_CONDITION_NOTIFY(UHealthComponent, Health, COND_None, REPNOTIFY_Always);
}
```
Owner actor must replicate. Components added at runtime: create on the server with `NewObject` + `RegisterComponent()`; they replicate if `SetIsReplicated(true)`.

## 4. Replicated UObject subobject (registered list, UE 5.1+, required for Iris)

```cpp
UCLASS()
class UInventoryItem : public UObject
{
    GENERATED_BODY()
public:
    virtual bool IsSupportedForNetworking() const override { return true; }
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override
    {
        Super::GetLifetimeReplicatedProps(Out);
        DOREPLIFETIME(UInventoryItem, Count);
    }
    UPROPERTY(Replicated) int32 Count = 0;
};

// Owner actor
AInventoryActor::AInventoryActor() { bReplicates = true; bReplicateUsingRegisteredSubObjectList = true; }
void AInventoryActor::AddItem()
{
    check(HasAuthority());
    UInventoryItem* Item = NewObject<UInventoryItem>(this);
    Items.Add(Item);                                  // UPROPERTY(Replicated) TArray<TObjectPtr<UInventoryItem>> Items;
    AddReplicatedSubObject(Item);
}
void AInventoryActor::RemoveItem(UInventoryItem* Item)
{
    RemoveReplicatedSubObject(Item);
    Items.Remove(Item);
}
```
For subobjects owned by a component use `UActorComponent::AddReplicatedSubObject` and set `bReplicateUsingRegisteredSubObjectList = true` on the component.

## 5. Push model property

```cpp
// Target.cs (Game/Server targets): bWithPushModel = true;  DefaultEngine.ini [SystemSettings] net.IsPushModelEnabled=1
void AScoreBoard::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);
    FDoRepLifetimeParams Params;
    Params.bIsPushBased = true;
    DOREPLIFETIME_WITH_PARAMS_FAST(AScoreBoard, Score, Params);
}
void AScoreBoard::AddScore(int32 Delta)
{
    Score += Delta;
    MARK_PROPERTY_DIRTY_FROM_NAME(AScoreBoard, Score, this);   // forget this = no replication
}
```
Arrays of structs: mark the array dirty after any element change.

## 6. Owner-only and initial-only data

```cpp
DOREPLIFETIME_CONDITION(AMyChar, Ammo, COND_OwnerOnly);        // HUD data only for owning client
DOREPLIFETIME_CONDITION(AMyChar, CosmeticSeed, COND_InitialOnly);
DOREPLIFETIME_CONDITION(AMyChar, ReplicatedAimPitch, COND_SkipOwner); // owner has local value
```

## 7. Large arrays: Fast Array Serializer (delta replication + per-item callbacks)

```cpp
USTRUCT() struct FInvEntry : public FFastArraySerializerItem
{
    GENERATED_BODY()
    UPROPERTY() int32 ItemId = 0;
    UPROPERTY() int32 Count = 0;
    void PostReplicatedAdd(const struct FInvList& List);
    void PostReplicatedChange(const struct FInvList& List);
    void PreReplicatedRemove(const struct FInvList& List);
};
USTRUCT() struct FInvList : public FFastArraySerializer
{
    GENERATED_BODY()
    UPROPERTY() TArray<FInvEntry> Items;
    bool NetDeltaSerialize(FNetDeltaSerializeInfo& Parms)
    { return FFastArraySerializer::FastArrayDeltaSerialize<FInvEntry, FInvList>(Items, Parms, *this); }
};
template<> struct TStructOpsTypeTraits<FInvList> : public TStructOpsTypeTraitsBase2<FInvList>
{ enum { WithNetDeltaSerializer = true }; };
// Server edits: Items[i].Count++; MarkItemDirty(Items[i]);  after Add: MarkItemDirty(NewItem); after Remove: MarkArrayDirty();
```
Header: `Net/Serialization/FastArraySerializer.h` (module `NetCore`). Trap: forgetting `MarkItemDirty`/`MarkArrayDirty` = no replication; callbacks run on clients only.

## 8. Possession-time init (works on server, owning client, listen host)

```cpp
void AMyChar::PossessedBy(AController* NewController)   // server only
{
    Super::PossessedBy(NewController);
    InitFromPlayerState();
}
void AMyChar::OnRep_PlayerState()                        // clients
{
    Super::OnRep_PlayerState();
    InitFromPlayerState();
}
void AMyChar::NotifyControllerChanged()                  // local input setup (server host + owning client)
{
    Super::NotifyControllerChanged();
    if (APlayerController* PC = Cast<APlayerController>(Controller); PC && PC->IsLocalController()) { AddInputMappingContext(PC); }
}
```
