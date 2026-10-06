# Specifier cheatsheet (traps only)

Only specifiers that are commonly misused. All exist in UE 5.x; version tags where relevant.

## UCLASS

| Specifier | Trap |
|---|---|
| `Blueprintable` / `NotBlueprintable` | Inherited. A base you want BP children of must be Blueprintable (Actor already is). |
| `BlueprintType` | Needed to use the class as a BP variable type (UObject subclasses that aren't Actors/Components). |
| `Abstract` | Prevents placing/instancing; use for base classes and for subsystem bases (abstract subsystems are not instantiated). |
| `Config=Game` + `UPROPERTY(Config)` | Reads `[/Script/Module.ClassName]` in `DefaultGame.ini`. `SaveConfig()` writes to Saved/, not Default*.ini. |
| `DefaultToInstanced`, `EditInlineNew` | Needed for `UPROPERTY(Instanced)` inline-created UObjects in details panels. |
| `MinimalAPI` | Only exports the type info (Cast/StaticClass); non-inline member functions are not linkable from other modules (LNK2019). Engine headers increasingly use `MinimalAPI` + per-member `UE_API` (seen in 5.6/5.7 headers). |
| `Within=Outer` | Restricts Outer type; NewObject with other outer asserts. |
| `meta=(BlueprintSpawnableComponent)` | Required for a C++ component to appear in BP "Add Component" list. |

## UPROPERTY

| Specifier | Trap |
|---|---|
| (none) `UPROPERTY()` | Still needed for GC tracking of UObject refs. |
| `EditAnywhere` / `EditDefaultsOnly` / `EditInstanceOnly` | `EditDefaultsOnly` for class-wide tuning in BP defaults; `EditInstanceOnly` for per-placed-actor data. |
| `VisibleAnywhere` | Use for component pointers created via `CreateDefaultSubobject`. |
| `BlueprintReadOnly/ReadWrite` | Private needs `meta=(AllowPrivateAccess="true")`. `BlueprintReadWrite` bypasses setters/validation — prefer ReadOnly + BlueprintCallable setter. |
| `Transient` | Not saved. Use for runtime caches and `BindWidgetAnim` animations. |
| `Replicated` / `ReplicatedUsing=OnRep_X` | Also requires `DOREPLIFETIME` in `GetLifetimeReplicatedProps`; see ue5-multiplayer. |
| `Instanced` | Per-instance subobject (with `EditInlineNew` class). |
| `SaveGame` | Only matters if you serialize with `ArIsSaveGame` (e.g. `FObjectAndNameAsStringProxyArchive` with `ArIsSaveGame = true`). |
| `Category="A|B"` | Required for BP-exposed properties in engine-style code; nested with `|`. |
| `BlueprintAssignable` | Only on dynamic multicast delegates. |
| `meta=(ClampMin, ClampMax, UIMin, UIMax)` | Clamp only applies in editor UI, not at runtime. |
| `meta=(EditCondition="bUseX", EditConditionHides)` | Condition is an expression string; bool member must exist. |
| `meta=(ExposeOnSpawn=true)` | Needs `BlueprintReadWrite`/`EditAnywhere`-style visibility; pin appears on SpawnActor/CreateWidget. |
| `meta=(AllowedClasses="...")`, `meta=(MustImplement="Interface")` | Asset/class picker filtering. |
| `meta=(Categories="Ability.Skill")` | Filters GameplayTag pickers on `FGameplayTag`/`FGameplayTagContainer` properties. |
| `meta=(BindWidget)`, `BindWidgetOptional`, `BindWidgetAnim` | UMG: name must match the designer widget exactly; anims also need `Transient`. |
| `meta=(HidePinAssetPicker)` | UE 5.6+ name; `HideAssetPicker` deprecated in 5.6 (per third-party 5.8 header audit). |

## UFUNCTION

| Specifier | Trap |
|---|---|
| `BlueprintCallable` | Needs `Category` in plugins/engine-style code. `const` -> Pure node unless `BlueprintPure=false`. |
| `BlueprintPure` | Must return a value; re-evaluated per connected pin. |
| `BlueprintImplementableEvent` | No C++ body. Can have return value (becomes a function in BP, not event). |
| `BlueprintNativeEvent` | Implement `X_Implementation`; call `X()`. In interfaces call `IFoo::Execute_X(Obj, ...)`. |
| `BlueprintAuthorityOnly` | BP node only runs on authority — silently does nothing on clients. |
| `BlueprintCosmetic` | Doesn't run on dedicated server. |
| `Exec` | Console command; only works on certain classes (PlayerController, Pawn, HUD, GameMode, CheatManager, GameInstance). |
| `CallInEditor` | Button in details panel (editor only). |
| `Server/Client/NetMulticast`, `Reliable/Unreliable`, `WithValidation` | See ue5-multiplayer. |
| `meta=(WorldContext="WorldContextObject")` | For static library functions needing a world; pin hidden in BP, filled automatically. |
| `meta=(DefaultToSelf="Target")`, `meta=(HidePin="X")` | Auto-fill self / hide pins. |
| `meta=(ExpandEnumAsExecs="Result")` | Enum out-param becomes exec pins (enum must be `UENUM(BlueprintType)`). |
| `meta=(AutoCreateRefTerm="Param")` | Lets `const T&` struct/array params be left unconnected. |
| `meta=(DeterminesOutputType="Class", DynamicOutputParam="Out")` | Typed return pins for class-param getters. |
| `meta=(Latent, LatentInfo="LatentInfo")` | Latent BP node; needs `FLatentActionInfo` param. Prefer `UBlueprintAsyncActionBase` for new code. |
| `meta=(DisplayName="...")`, `meta=(Keywords="...")` | BP search/display only. |

## USTRUCT / UENUM

- `USTRUCT(BlueprintType)`; members `UPROPERTY(EditAnywhere, BlueprintReadWrite)`; give defaults with in-class initializers.
- Make/Break nodes auto-generated for BlueprintType structs; custom: `meta=(HasNativeMake="Module.Lib.Func")`.
- `UENUM(BlueprintType) enum class E : uint8 { A UMETA(DisplayName="Alpha"), MAX UMETA(Hidden) };`
- Bitflags: `UENUM(meta=(Bitflags, UseEnumValuesAsMaskValuesInEditor="true"))` + `UPROPERTY(meta=(Bitmask, BitmaskEnum="/Script/Module.EMyFlags")) int32 Flags;`
- Struct `operator==` is needed for some uses (TSet keys need `GetTypeHash`).
