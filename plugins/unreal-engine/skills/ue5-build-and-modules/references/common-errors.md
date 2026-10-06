# Build / link / package errors: message -> cause -> fix

Match on the quoted fragment. Core C++/UHT messages: `ue5-cpp-core/references/common-errors.md`. Replication runtime messages: `ue5-multiplayer/references/troubleshooting.md`.

## Linker (MSVC)

| Message (fragment) | Cause | Fix |
|---|---|---|
| `error LNK2019: unresolved external symbol "..." referenced in function ...` | Module dependency missing; plugin not enabled; missing `*_API`; engine member not exported (`MinimalAPI`/no `UE_API`); declared-not-defined | See decision order in SKILL.md. Add module to `PrivateDependencyModuleNames`, enable plugin, add `MYMODULE_API`, implement the function. |
| `error LNK2001: unresolved external symbol "__declspec(dllimport) ... StaticClass"` / `GetPrivateStaticClass` | The UCLASS in another module lacks `MYMODULE_API` (or module not a dependency) | `class MYMODULE_API UFoo`; add dependency. |
| `LNK2019 ... ServerFoo_Implementation` / `..._Validate` / `Foo_Implementation` | RPC/BlueprintNativeEvent body missing or signature differs | Define `X_Implementation` (and `X_Validate` with `WithValidation`) with exactly the same params (`const FVector&` vs `FVector` matters). |
| `LNK2005 ... already defined in ...obj` | Function/variable defined in a header without `inline`; same .cpp compiled twice | `inline`/`static` or move definition to .cpp. |
| `LNK1169 one or more multiply defined symbols found` | Follows LNK2005 | Fix LNK2005. |
| `fatal error LNK1104: cannot open file '...UnrealEditor-MyGame.dll'` / `.lib` | Editor (or a zombie `UnrealEditor.exe`) has the DLL locked; or path missing | Close editor/kill process, or use Live Coding; for third-party libs check `PublicAdditionalLibraries` path. |
| `LNK1181 cannot open input file 'X.lib'` | Wrong path for third-party lib | `Path.Combine(ModuleDirectory, ...)`. |
| `LNK4099 PDB ... was not found` | Third-party lib without PDB | Harmless. |

## Compiler

| Message (fragment) | Cause | Fix |
|---|---|---|
| `fatal error C1083: Cannot open include file: 'X.h': No such file or directory` | Module not a dependency; wrong relative path (must be relative to the module's `Public/`/`Classes/`); plugin disabled; Linux case mismatch | Add module; use path like `GameFramework/SpringArmComponent.h`; enable plugin; fix case. |
| `C1083: Cannot open include file: 'X.generated.h'` | UHT didn't run for that header / header not in a module's source dir / stale intermediates | Regenerate project files; ensure header is under `Source/<Module>/`; clean rebuild. |
| `C1083: Cannot open include file: 'hash_map'` (in `ThirdParty/nvtesslib/inc/nvtess.h`) | UE 5.8 **source** build with VS 2026 (legacy header removed) | Apply the community patch to nvtess.h or build engine with VS 2022 toolset. |
| `C2039: 'X': is not a member of 'Y'` after upgrade | API renamed/removed | Search the engine header for `UE_DEPRECATED`; see ue5-version-notes. |
| `C2065: undeclared identifier` for engine types | Missing include (hidden earlier by unity build) | Include the header explicitly. |
| `C4996: '...': ... has been deprecated ...` | Deprecated API | Use replacement in message. Treat as error before upgrading again. |
| `error C4668: 'X' is not defined as a preprocessor macro, replacing with '0' for '#if/#elif'` | Undefined macro in `#if` (newer build settings treat as error) | Define macro (`PublicDefinitions.Add("X=0")`) or use `#if defined(X)`. |
| `C4458/C4456/C4459: declaration of 'X' hides ...` | Shadowing, error in UE | Rename. |
| `C4800`/`C4244` conversion warnings as errors (double->float) | LWC: `FVector` is double since 5.0 | `FVector3f` for float data, explicit `static_cast<float>`. |
| `fatal error C1060: compiler is out of heap space` / `C3859` | Parallel compile memory exhaustion | Reduce parallel actions (BuildConfiguration.xml `MaxParallelActions`), increase page file. |
| `A call to an immediate function is not a constant expression` (UE 5.8) | Checked printf format mismatch | Fix specifiers/args (see ue5-cpp-core). |

## UnrealBuildTool / project generation

| Message (fragment) | Cause | Fix |
|---|---|---|
| `Could not find definition for module 'X', (referenced via ...)` | Typo in Build.cs/.uproject/Target `ExtraModuleNames`, missing `X.Build.cs`, or plugin providing it disabled | Fix name; enable plugin. |
| `Unable to find plugin 'X' (referenced via MyGame.uproject)` | Plugin folder missing (Fab plugin not installed for this engine version) | Install plugin for this engine version or remove entry. |
| `Plugin 'X' (referenced via ...) does not contain the 'Y' module, but lists it` | `.uplugin` `Modules` doesn't match `Source/` folders | Fix `.uplugin`. |
| `Warning: Plugin 'A' does not list plugin 'B' as a dependency, but module 'A' depends on module 'B'.` | Missing `.uplugin` dependency | Add `{ "Name": "B", "Enabled": true }` to A's `Plugins` array. |
| `Expecting to find a type to be declared in a target rules named 'MyGameTarget'` | Target.cs class name mismatch | `public class MyGameTarget : TargetRules` in `MyGame.Target.cs`. |
| `Circular dependency for 'A.Build.cs' detected` | A depends on B depends on A | Extract shared interfaces into a third module; or dynamic loading. |
| `... modifies the values of properties: [ ... ]. This is not allowed, as <X>Editor has build products in common with UnrealEditor.` | Installed engine + Target.cs overrides shared settings | Remove the override; or source engine + `BuildEnvironment = TargetBuildEnvironment.Unique`. |
| `Targets with a unique build environment cannot be built with an installed engine.` | Same (often Shipping-logging flags, custom defines in Target) | Source engine, or remove settings. |
| `Server targets are not currently supported from this engine distribution.` | Launcher engine | Source-built engine. |
| `Visual Studio 2022 x64 must be installed in order to build this target.` / `Visual Studio C++ 2022 installation not found` | Compiler forced to VS2022 (BuildConfiguration.xml / Target.cs / plugin Target.cs) while only VS 2026 installed; or C++ workload missing | Remove forced compiler setting in `%APPDATA%\Unreal Engine\UnrealBuildTool\BuildConfiguration.xml` and Target files; install "Desktop/Game development with C++" + MSVC v14.38+ toolset. |
| `Platform Win64 is not a valid platform to build. Check that the SDK is installed properly.` | Windows SDK/MSVC missing or not detected | Install SDK + MSVC via VS Installer; restart editor/launcher. |
| UBT warning about MSVC `14.39.33519-14.39.99999` being banned/unsupported | Known-bad compiler | Install MSVC 14.38 or a version newer than 14.39. |
| `'ModuleRules.bEnforceIWYU' is obsolete: 'Deprecated in UE5.2 - Use IWYUSupport instead.'` | Old Build.cs | `IWYUSupport = IWYUSupport.Full;` (or remove). |
| `Unable to build while Live Coding is active. Exit the editor and game, or press Ctrl+Alt+F11 if iterating on code in the editor or game` | IDE build with editor + Live Coding running | Close editor, or Ctrl+Alt+F11. |
| `Live coding: ... changes to class layout ... not supported` / object reinstancing warnings | Header/reflection change via Live Coding | Close editor, full build. |

## Editor launch

| Message (fragment) | Cause | Fix |
|---|---|---|
| `The following modules are missing or built with a different engine version: ... Would you like to rebuild them now?` | Project binaries missing/outdated (new engine version, pulled code) | "Yes" (only works if code compiles), else build from IDE. |
| `MyGame could not be compiled. Try rebuilding from source manually.` | Compile error during the auto-rebuild | Build from IDE to see the real error; check `Saved/Logs/` and `%LOCALAPPDATA%\UnrealBuildTool\Log.txt`. |
| `Plugin 'X' failed to load because module 'X' could not be found.` | Plugin binaries missing for this engine version | Build from IDE (project plugins) or install matching Fab version. |
| `Plugin 'X' failed to load because module 'X' does not appear to be compatible with the current version of the engine.` | Prebuilt plugin binaries from other engine version/hotfix | Rebuild plugin; update plugin version. |
| `ModuleManager: Unable to load module 'X' because InitializeModule function was not found.` | Missing `IMPLEMENT_MODULE`/`IMPLEMENT_PRIMARY_GAME_MODULE` | Add it in the module's .cpp with the exact module name. |
| Startup crash `xSharedMemoryException` in non-editor builds (UE 5.8 reports) | Stale/mixed binaries after upgrade | Delete Binaries/Intermediate/Saved/DDC/.vs, regenerate, rebuild. |

## Cook / package

| Message (fragment) | Cause | Fix |
|---|---|---|
| `Unable to instantiate module 'UnrealEd': Unable to instantiate UnrealEd module for non-editor targets.` | Runtime module depends on UnrealEd | `if (Target.bBuildEditor)` around the dependency; editor code in `#if WITH_EDITOR` or an Editor module. |
| `Missing precompiled manifest for 'X'` | Installed engine + dependency on a module not precompiled for game targets (often editor modules) | Remove/guard dependency; or source build. |
| `error: ... WITH_EDITORONLY_DATA ...` / undeclared editor-only member in Game target | Editor-only member used in runtime code | Wrap in `#if WITH_EDITORONLY_DATA`/`WITH_EDITOR`. |
| `LogCook: Error: ... Failed to load '/Game/...': Can't find file.` | Broken reference (deleted/moved asset, redirector not fixed) | Fix up redirectors (Content Browser > Fix Up), repair referencing asset. |
| `LogBlueprint: Error: ... Node ... cannot be found` / BP compile errors during cook | BP references removed C++ symbol | Core Redirect or fix BP; cook fails on BP errors. |
| `Unknown Cook Failure` / `BUILD FAILED` | Generic tail message | Scroll up to first `Error:`; also see `Saved/Logs/` and `Engine/Programs/AutomationTool/Saved/Logs/`. |
| `Ensure condition failed: ...` during cook (treated as error) | Code ensures in editor/cook path | Fix the ensure; don't silence. |
| Packaged game: `Failed to find object` / missing assets at runtime | Asset loaded only by path, not cooked | Hard/soft reference it from a cooked asset, Asset Manager primary asset rules, or "Additional Asset Directories to Cook". |
