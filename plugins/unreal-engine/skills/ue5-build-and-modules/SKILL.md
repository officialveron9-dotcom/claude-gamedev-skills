---
name: ue5-build-and-modules
description: Fixes and prevents Unreal Engine 5 build, link and packaging failures (UE 5.0-5.8). Covers Build.cs Public vs Private dependencies, .uproject/.uplugin module and plugin entries, LNK2019/LNK2001 unresolved external symbol (missing module dependency, missing MYGAME_API, MinimalAPI/UE_API), C1083 include errors, IWYU and unity-build hidden includes, Live Coding vs editor restart, regenerating project files, clean rebuild, UnrealBuildTool/UHT errors, Target.cs BuildSettingsVersion/IncludeOrderVersion, Visual Studio 2022/2026, MSVC, Windows SDK, Rider, Linux/clang and dedicated server targets, cooking/packaging errors (UnrealEd in runtime module, missing precompiled manifest). Use whenever a compile, link, UBT, cook or package error appears or modules/plugins are added. German triggers: Kompilierfehler, Linkerfehler, Build fehlgeschlagen, Paketierung Fehler, Unreal Fehler beim Kompilieren, Projektdateien neu generieren.
---

# UE5 build, modules, packaging — pitfalls & fixes

Target UE 5.8 (current, 2026-10; hotfixes 5.8.1-5.8.3). Version tags where behaviour differs.
Exact error texts: [references/common-errors.md](references/common-errors.md) — read it first when an error is pasted.

## Before adding code that uses a new engine feature

- [ ] Find the **module** that owns the header (path `Engine/Source/Runtime/<Module>/...` or `Engine/Plugins/.../Source/<Module>/...`). See [references/module-map.md](references/module-map.md).
- [ ] Add it to `PrivateDependencyModuleNames` (or `Public...` only if your **public headers** include its headers / expose its types).
- [ ] If the module lives in a plugin: also enable the plugin in `.uproject` (or as dependency in your `.uplugin`). Build.cs alone is not enough.
- [ ] Include with the module-relative path: `#include "GameFramework/Character.h"`, not `"Character.h"` or absolute paths.
- [ ] Editor-only modules (`UnrealEd`, `ToolMenus`, `*Editor`) only inside `if (Target.bBuildEditor)` or in a separate `Type: Editor` module; code under `#if WITH_EDITOR`.
- [ ] Changed Build.cs/.uproject/.uplugin or added/removed files? Regenerate project files.

## Build.cs — wrong vs right

```csharp
// WRONG: everything public, editor module in runtime deps, missing plugin module
PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "UnrealEd", "UMG" });

// RIGHT
public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput" });
        PrivateDependencyModuleNames.AddRange(new[] { "UMG", "Slate", "SlateCore", "GameplayTags" });
        if (Target.bBuildEditor)
        {
            PrivateDependencyModuleNames.Add("UnrealEd");
        }
    }
}
```
- Public = transitively visible to modules depending on you; only for types in your Public headers. Over-publicizing slows builds and causes circular deps.
- `PrivateIncludePathModuleNames` gives headers only — no linking (LNK2019 if you call non-inline functions).
- UE 5.5+: `StructUtils` plugin/module is deprecated; `FInstancedStruct` lives in CoreUObject (include path `StructUtils/InstancedStruct.h` still valid). Remove the dependency to silence the warning.
- Iris: `SetupIrisSupport(Target);` in Build.cs (see ue5-multiplayer).

## Linker errors (LNK2019 / LNK2001) — decision order

1. Symbol from an engine/plugin module -> module missing in Build.cs (or only in `PrivateIncludePathModuleNames`). Add dependency.
2. Plugin module -> plugin not enabled in `.uproject`/`.uplugin`.
3. Symbol from **your other module** -> class/function lacks `MYMODULE_API`:
   ```cpp
   class MYCORE_API UInventoryComponent : public UActorComponent   // export whole class
   MYCORE_API void FreeHelper();                                    // export free function at declaration
   ```
4. Engine class is `UCLASS(MinimalAPI)` / members not marked `*_API`/`UE_API` -> only inline/virtual members and `StaticClass()`/`Cast` are usable cross-module. Many engine headers (seen in 5.6/5.7, e.g. GameplayAbilities) use `MinimalAPI` + per-member `UE_API`; a member without `UE_API` cannot be called from your module. Use another (exported) API, or subclass and use virtuals.
5. Declared but never defined (typo in signature, `const` mismatch, function only defined under `#if WITH_EDITOR`).
6. `static` member / template defined in .cpp but used elsewhere.
7. `_Implementation`/`_Validate` for RPC or BlueprintNativeEvent missing in the .cpp.
Signature mismatch hint: copy the mangled name from the error; `__declspec(dllimport)` in the message = case 3/4.

## Include / IWYU traps

- Unity builds merge .cpp files and hide missing includes; the error appears later when adaptive unity removes a changed file from the blob. Verify with a non-unity build (`-DisableUnity` on the UBT command line, or `bUseUnityBuild = false` temporarily in Target.cs).
- Include what you use; don't rely on `Engine.h`/`EngineMinimal.h` monolithic headers.
- `IWYUSupport = IWYUSupport.Full` replaces `bEnforceIWYU` (UE 5.2+; `bEnforceIWYU` gives CS0618 obsolete warning).
- Every .cpp includes its own header **first**.

## Live Coding vs restart

| Change | Live Coding (Ctrl+Alt+F11) | Close editor + build from IDE |
|---|---|---|
| Function body in .cpp | OK | — |
| New non-reflected .cpp/helper function | Usually OK | if it misbehaves |
| Add/remove/reorder `UPROPERTY`, `UFUNCTION`, change `UCLASS`/`USTRUCT`/`UENUM`, base class, `GENERATED_BODY` types | **No** (unsafe; reinstancing is experimental and can corrupt BPs) | **Required** |
| Constructor defaults / `CreateDefaultSubobject` changes | Not applied to existing CDOs/instances reliably | **Required** |
| New module, Build.cs, .uproject, .uplugin, Target.cs | No | Required + regenerate project files |
| Header-only changes to reflected types | No | Required |

- IDE build while the editor runs with Live Coding: "Unable to build while Live Coding is active. Exit the editor and game, or press Ctrl+Alt+F11 if iterating on code in the editor or game".
- Turn off "Enable Reinstancing" (Editor Preferences > Live Coding) to avoid BP corruption; after header changes always restart.
- Never save Blueprints that show errors right after a Live Coding patch of headers; restart first.
- Hot Reload is legacy; with Live Coding enabled it's disabled. Don't use the old "Compile" button workflow.

## Clean rebuild procedure (stale binaries, "could not be compiled", weird UHT state)

1. Close editor and IDE.
2. Delete `Binaries/`, `Intermediate/`, `.vs/` (+ plugin `Binaries/`/`Intermediate/` for project plugins). Keep `Saved/` unless config corruption suspected; `DerivedDataCache/` only for shader/DDC issues.
3. Right-click `.uproject` -> Generate Visual Studio project files (or `UnrealBuildTool -projectfiles -project="<path>.uproject" -game -engine`).
4. Build `MyGameEditor` / `Development Editor` / `Win64` from the IDE, then launch.

## Target.cs traps

```csharp
// UE 5.8 template values (V7 + Unreal5_8); "Latest" is the low-maintenance choice for a solo project
DefaultBuildSettings = BuildSettingsVersion.V7;            // or BuildSettingsVersion.Latest
IncludeOrderVersion  = EngineIncludeOrderVersion.Unreal5_8; // or EngineIncludeOrderVersion.Latest
```
- After an engine upgrade, old include orders (<= Unreal5_5) are obsolete (warnings) and old BuildSettings versions produce deprecation warnings. Update both Target.cs files (Game + Editor) together.
- With a Launcher (installed) engine, the Editor target must use the shared build environment. Setting compiler flags (e.g. `bStrictConformanceMode`, warning levels) that differ from UnrealEditor fails with "... modifies the values of properties: [...]. This is not allowed, as <Target> has build products in common with UnrealEditor." Remove the override, or (source engine only) `BuildEnvironment = TargetBuildEnvironment.Unique;`.
- Launcher engine cannot build `Server`/`Client` targets or unique-environment targets ("Server targets are not currently supported from this engine distribution." / "Targets with a unique build environment cannot be built with an installed engine."). Use a source build from GitHub.
- UE 5.6+: warning-level properties moved under `CppCompileWarningSettings` (e.g. `CppCompileWarningSettings.ShadowVariableWarningLevel`); old direct properties are `[Obsolete]`.

## Toolchain quick facts (details: [references/toolchain.md](references/toolchain.md))

- UE 5.8: VS 2022 17.14+ minimum, VS 2026 (18.x) recommended; MSVC min 14.38, recommended 14.50; Windows SDK min 10.0.22621.0, default 10.0.26100.0 (release notes also list .NET 10.0 for VS 2026); Linux clang 20.1.8.
- The authoritative list is `Engine/Config/Windows/Windows_SDK.json` (and `Engine/Config/Linux/Linux_SDK.json`) of your engine install — non-English docs for 5.8 were reported wrong.
- MSVC 14.39.33519-14.39.99999 is banned by UBT (compiler bug) — install 14.38 or newer than 14.39.
- 5.8 + VS 2026 known issues: UBT still demanding VS 2022 ("Visual Studio 2022 x64 must be installed in order to build this target") — check `%APPDATA%\Unreal Engine\UnrealBuildTool\BuildConfiguration.xml` and project/plugin Target.cs for a forced `WindowsPlatform.Compiler`/`<Compiler>` value and remove it; source builds fail in `nvtesslib` (`Cannot open include file: 'hash_map'`) — patch or build that part with VS 2022.

## Packaging / cooking traps

- Read the log from the **first** `Error:` line (UAT output `UATHelper: Packaging (Windows): ... Error:`), not the final "Unknown Cook Failure"/"BUILD FAILED".
- Runtime module depending on `UnrealEd` -> "Unable to instantiate UnrealEd module for non-editor targets" / "Missing precompiled manifest for 'UnrealEd'". Guard with `Target.bBuildEditor` and `#if WITH_EDITOR`.
- `WITH_EDITORONLY_DATA` members accessed outside `#if WITH_EDITORONLY_DATA` compile in editor but fail in Game target. Build the `Development` (game) target from the IDE before packaging.
- Assets only referenced by string paths / soft refs from code are not cooked unless reachable or listed (Asset Manager primary asset rules or "Additional Asset Directories to Cook").
- Maps: Project Settings > Packaging > "List of maps to include" (otherwise only referenced/default maps are cooked).
- Code plugins from Fab/Marketplace must be rebuilt for each engine minor version (and sometimes per hotfix): "Plugin 'X' failed to load because module 'X' does not appear to be compatible with the current version of the engine."
- "Platform Win64 is not a valid platform to build. Check that the SDK is installed properly." -> Windows SDK / MSVC components missing in VS Installer (install "Game development with C++" + matching MSVC + Windows SDK), then restart editor.

## Dedicated server / Linux traps

- Needs source-built engine; add `Source/MyGameServer.Target.cs` (`Type = TargetType.Server;`, same `ExtraModuleNames`). Build `Development Server`, then package with Server config (`WindowsServer`/`LinuxServer`).
- Code: guard client-only code (UI, audio, input, rendering) with `IsNetMode(NM_DedicatedServer)`/`IsRunningDedicatedServer()` checks or `#if !UE_SERVER`; `UE_SERVER` is 1 only in server-target builds.
- Linux from Windows: install Epic's cross-compile toolchain matching the engine (v26 / clang 20.1.8 for 5.7-5.8; check `Linux_SDK.json`), set `LINUX_MULTIARCH_ROOT`, restart IDE/editor so UBT sees it.
- Case-sensitive file systems on Linux: `#include "myactor.h"` vs `MyActor.h` breaks only on Linux builds.

## References

- [references/common-errors.md](references/common-errors.md) — exact error text -> cause -> fix (compiler, linker, UHT, UBT, Live Coding, cook, runtime module load).
- [references/module-map.md](references/module-map.md) — feature/class -> Build.cs module -> plugin to enable.
- [references/toolchain.md](references/toolchain.md) — IDE/compiler/SDK per UE version and setup traps.
- [references/sources.md](references/sources.md) — sources.
