# UMG & CommonUI — traps and patterns

## C++ base widget pattern

```cpp
UCLASS(Abstract)
class UHealthBar : public UUserWidget
{
    GENERATED_BODY()
protected:
    UPROPERTY(meta=(BindWidget)) TObjectPtr<UProgressBar> HealthBar;          // name must match designer exactly
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UTextBlock> HealthText;   // may be null -> check
    UPROPERTY(Transient, meta=(BindWidgetAnim)) TObjectPtr<UWidgetAnimation> DamageFlash;

    virtual void NativeOnInitialized() override;   // once per widget instance: bind delegates here
    virtual void NativeConstruct() override;       // every time added to parent/viewport
    virtual void NativeDestruct() override;        // every removal: unbind what NativeConstruct bound
};
```
Widget BP must reparent to `UHealthBar`. Build.cs: `UMG`, `Slate`, `SlateCore`.

## Lifecycle traps

| Function | Runs | Trap |
|---|---|---|
| `NativePreConstruct` | in the designer too | No gameplay calls (no world/pawn). Guard `IsDesignTime()`. |
| `NativeOnInitialized` | once after creation | Best place for one-time delegate binding. |
| `NativeConstruct` | every AddToViewport/AddChild | Binding here without unbinding in `NativeDestruct` = duplicate callbacks after re-adding. |
| `NativeTick` | every frame if visible | Use events/delegates instead of polling. |

- Property bindings (designer "Bind" functions) run every frame — avoid for anything but prototypes.
- `CreateWidget<T>(OwningPlayerController, Class)`; `GetOwningPlayer()`/`GetOwningPlayerPawn()` depend on it. Pass the owning PlayerController explicitly (a World/GameInstance owner falls back to a default/first local player, wrong for split-screen and confusing in listen-server PIE).
- Widgets aren't actors: no replication. Update from replicated state (OnRep -> delegate -> widget) on the owning client.
- Create HUD widgets only where `IsLocalController()`; on a dedicated server `CreateWidget` is pointless and some calls assert.
- Hold widget pointers in `UPROPERTY()` (HUD/PC) — unreferenced widgets removed from parent get GC'd.
- Input mode: `SetInputMode(FInputModeGameAndUI())` + `bShowMouseCursor`; remember to restore `FInputModeGameOnly`. Focus widgets with `SetUserFocus`/`SetKeyboardFocus` only after they're constructed.

## CommonUI traps

- Plugin CommonUI; modules `CommonUI`, `CommonInput`.
- Project Settings > Engine > General Settings > **Game Viewport Client Class = `CommonGameViewportClient`** (or subclass). Without it, input routing/back handling doesn't work.
- Create an input data asset (Click/Back actions) and set it in Project Settings > Common Input Settings per platform; CommonUI "Input Action Data Tables" are separate from Enhanced Input unless Enhanced Input support is enabled in CommonInput settings.
- Use `UCommonActivatableWidget` + `UCommonActivatableWidgetStack`/`Queue` (push/pop), not raw AddToViewport for menus.
- Override `GetDesiredInputConfig()` on activatable widgets (menu = Menu/UI mode, HUD = Game) instead of calling `SetInputMode` yourself — manual calls fight CommonUI's input routing.
- `bIsBackHandler`/`NativeOnHandleBackAction` for back navigation; set `bAutoActivate`/activation carefully or widgets never get input.
- Buttons: `UCommonButtonBase` subclasses with style assets. C++: `Button->OnClicked().AddUObject(this, &UMyMenu::HandleClick)`; Blueprint event: `OnButtonBaseClicked`.
