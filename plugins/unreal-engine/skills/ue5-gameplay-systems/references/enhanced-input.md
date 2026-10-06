# Enhanced Input — traps and patterns

## Setup checklist

1. Build.cs: `EnhancedInput` (+ `InputCore` if using `FKey`/`EKeys`).
2. Project Settings > Engine > Input: Default Player Input Class = `EnhancedPlayerInput`, Default Input Component Class = `EnhancedInputComponent` (DefaultInput.ini `[/Script/Engine.InputSettings]`). UE4-upgraded projects keep the old classes -> `Cast<UEnhancedInputComponent>` returns null.
3. Assets: one `UInputAction` per action (Value Type: Digital bool / Axis1D / Axis2D / Axis3D), one or more `UInputMappingContext`.
4. Character exposes `UPROPERTY(EditDefaultsOnly) TObjectPtr<UInputMappingContext> DefaultIMC;` and `TObjectPtr<UInputAction>` members, assigned in the BP subclass (don't hardcode paths).
5. Add IMC on the local player; bind actions in `SetupPlayerInputComponent` (pawn) or `SetupInputComponent` (PC).

## Trigger events

| Event | Fires | Use |
|---|---|---|
| `Started` | first frame of actuation | one-shot press |
| `Ongoing` | while a trigger (e.g. Hold) is evaluating | charge UI |
| `Triggered` | every frame the trigger condition is met (default trigger = every frame while held) | movement/look, or once if IMC trigger is Pressed/Released/Tap |
| `Completed` | trigger finished (released after Triggered) | stop jump/fire |
| `Canceled` | trigger aborted (e.g. Hold released early) | cancel charge |

Traps:
- Binding a fire action to `Triggered` without a Pressed trigger = full-auto fire every frame.
- `Completed` doesn't fire if the action never reached `Triggered` (e.g. Hold released early -> `Canceled`).
- Several bindings to the same action/event all fire; don't bind in both PC and Pawn unless intended.

## WASD to a 2D action

IMC mapping for `IA_Move` (Axis2D):
- W: modifier `Swizzle Input Axis Values` (YXZ)
- S: `Swizzle` (YXZ) + `Negate`
- A: `Negate`
- D: none
Gamepad stick: `Dead Zone` modifier. Mouse look: `Negate` on Y if you want non-inverted pitch with `AddControllerPitchInput`.

```cpp
void AMyChar::Move(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();
    const FRotator YawRot(0.f, GetControlRotation().Yaw, 0.f);
    AddMovementInput(FRotationMatrix(YawRot).GetUnitAxis(EAxis::X), Axis.Y);
    AddMovementInput(FRotationMatrix(YawRot).GetUnitAxis(EAxis::Y), Axis.X);
}
```

## Contexts at runtime

- `AddMappingContext(IMC, Priority)`: higher priority wins for the same key; lower-priority mappings of a consumed key are blocked only if the action has `bConsumeInput` (default true).
- Remove contexts when switching modes (vehicle, menu): `RemoveMappingContext(IMC)`; `ClearAllMappings()` also drops contexts added elsewhere.
- Contexts live on the `ULocalPlayer` subsystem, so they survive pawn changes and level travel of the local player — remove pawn-specific contexts on unpossess instead of assuming they disappear with the pawn.
- UI focus: `SetInputMode(FInputModeUIOnly)` stops game input; with CommonUI let activatable widgets drive input config instead.

## Rebinding / user settings

- Enable "User Settings" in Project Settings > Engine > Enhanced Input; mark actions/mappings player-mappable (`UPlayerMappableKeySettings` on the action or mapping).
- `UPlayerMappableInputConfig` is deprecated since 5.3 -> use `UEnhancedInputUserSettings` (`Subsystem->GetUserSettings()`).
- UE 5.6: key profile APIs switched from `FGameplayTag` IDs to `FString` IDs (`SetActiveKeyProfile(FString)`, `GetActiveKeyProfile()`, `ProfileIdString`, `SupportedKeyProfileIds`); the tag-based versions are deprecated (per third-party 5.8 header audit).
- After changing mappings call `ApplySettings()` and `SaveSettings()` on the user settings object.

## Version changes affecting code

| Version | Change |
|---|---|
| 5.1 | Legacy Action/Axis mappings deprecated ("Axis and Action mappings are now deprecated, please use Enhanced Input Actions and Input Mapping Contexts instead"). Templates use Enhanced Input. |
| 5.3 | `UPlayerMappableInputConfig` deprecated -> `UEnhancedInputUserSettings`. |
| 5.6 | `UEnhancedPlayerInput::GetAppliedInputContexts()` -> `GetAppliedInputContextData()`; key-profile IDs become strings (third-party audit). |
| 5.7 | `UInputMappingContext` mappings stored in `DefaultKeyMappings` (+ per-profile overrides); direct `Mappings` access deprecated — use `GetMappings()`/`MapKey()`/`UnmapKey()`. |
| 5.8 | `UInputTriggerCombo` (+ `FInputComboStepData`, `FInputCancelAction`) deprecated with no replacement (third-party audit). `UEnhancedInputWorldSubsystem` (input for non-possessed actors) is experimental. |

## Multiplayer

- Input exists only on the owning client (and listen host for its own pawn). Never add IMCs for remote players on the server (`GetLocalPlayer()` is null there).
- Input handlers call Server RPCs (or GAS ability activation); they must not change replicated state directly.
