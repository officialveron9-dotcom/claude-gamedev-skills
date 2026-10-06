# Feature -> Build.cs module -> plugin

If the "Plugin" column is filled, the plugin must be enabled (`.uproject` `Plugins` or a `.uplugin` dependency) in addition to the Build.cs entry. Module names verified against community/engine Build.cs files; when unsure, look for `<Name>.Build.cs` next to the header in the engine tree.

| Feature / typical classes | Module(s) | Plugin |
|---|---|---|
| Actors, components, GameFramework | `Core`, `CoreUObject`, `Engine` | — |
| `FKey`, `EKeys` | `InputCore` | — |
| Enhanced Input (`UInputAction`, `UInputMappingContext`, `UEnhancedInputComponent`, `UEnhancedInputLocalPlayerSubsystem`) | `EnhancedInput` | EnhancedInput (enabled by default in UE5 templates) |
| UMG (`UUserWidget`, `UTextBlock`, `UButton`) | `UMG`, `Slate`, `SlateCore` | — |
| CommonUI (`UCommonActivatableWidget`, `UCommonButtonBase`) | `CommonUI`, `CommonInput` | CommonUI |
| MVVM (`UMVVMViewModelBase`) | `ModelViewViewModel` | ModelViewViewModel |
| Gameplay Tags | `GameplayTags` | — (module in engine) |
| Gameplay Ability System | `GameplayAbilities`, `GameplayTags`, `GameplayTasks` | GameplayAbilities |
| AI (`AAIController`, BehaviorTree, Perception) | `AIModule`, `GameplayTasks` | — |
| Navigation (`UNavigationSystemV1`) | `NavigationSystem` | — |
| StateTree | `StateTreeModule`, `GameplayStateTreeModule` (+ `PropertyBindingUtils` for property-binding code in 5.6+ projects, as used in Tom Looman's sample) | StateTree, GameplayStateTree |
| Smart Objects | `SmartObjectsModule` | SmartObjects |
| Mass | `MassEntity`, `MassCommon`, `MassSpawner`, ... | MassGameplay / MassAI |
| Niagara | `Niagara` | Niagara (default on) |
| Push model replication | `NetCore` | — |
| Iris | `SetupIrisSupport(Target);` in Build.cs | Iris |
| Replication Graph | `ReplicationGraph` | ReplicationGraph |
| Online Subsystem | `OnlineSubsystem`, `OnlineSubsystemUtils` | OnlineSubsystem (+ platform OSS, e.g. OnlineSubsystemSteam) |
| Game Features / Modular Gameplay | `GameFeatures`, `ModularGameplay` | GameFeatures, ModularGameplay |
| Developer Settings (`UDeveloperSettings`) | `DeveloperSettings` | — |
| Chaos / physics types | `PhysicsCore`, `Chaos` | — |
| Animation runtime nodes | `AnimGraphRuntime` | — |
| Sequencer at runtime | `LevelSequence`, `MovieScene` | — |
| JSON | `Json`, `JsonUtilities` | — |
| HTTP | `HTTP` | — |
| Mover (experimental in 5.8) | `Mover` | Mover |
| Instanced structs (`FInstancedStruct`) | `CoreUObject` (UE 5.5+; `StructUtils` deprecated) | — |
| Editor-only (`UnrealEd`, `ToolMenus`, `PropertyEditor`, `AssetTools`) | as named | Only in `Type: Editor` modules or `if (Target.bBuildEditor)` |

## .uproject / .uplugin entries

```json
"Modules": [
  { "Name": "MyGame", "Type": "Runtime", "LoadingPhase": "Default" },
  { "Name": "MyGameEditor", "Type": "Editor", "LoadingPhase": "PostEngineInit" }
],
"Plugins": [
  { "Name": "GameplayAbilities", "Enabled": true },
  { "Name": "Iris", "Enabled": true }
]
```
Traps:
- Module `Name` must equal folder name, `<Name>.Build.cs` class name and `IMPLEMENT_MODULE(..., Name)`.
- `Type: Editor` modules are stripped from packaged games; anything a cooked asset needs at runtime must be in a `Runtime` module.
- A second game module must also be added to `ExtraModuleNames` in both Target.cs files (or be loaded via .uproject).
- `LoadingPhase` too late -> classes not registered when assets load ("Failed to find class" on startup). Use `PreDefault`/`Default` for gameplay classes.
- Plugin `.uplugin` must list plugins it depends on in its own `Plugins` array.
