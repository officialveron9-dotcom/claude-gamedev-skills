# Known issues and regressions (coding/build relevant)

Status as reported on Epic forums up to 2026-10; check whether a newer hotfix fixed it before applying workarounds.

| Version | Symptom (exact text where known) | Cause / workaround |
|---|---|---|
| 5.8.x + VS 2026 | `Visual Studio 2022 x64 must be installed in order to build this target.` / `Visual Studio C++ 2022 installation not found` | UBT forced to VS 2022 via `%APPDATA%\Unreal Engine\UnrealBuildTool\BuildConfiguration.xml`, project or plugin Target.cs. Remove the forced `Compiler` setting; ensure VS 2026 has the C++ game workload + MSVC toolset. Epic community tutorial "Check or Fix a Corrupted Pathway Between UE 5.8 and Visual Studio 2026" covers it. |
| 5.8 source + VS 2026 | `nvtess.h(154,1): fatal error C1083: Cannot open include file: 'hash_map'` | Legacy MSVC header gone. Community source patch, or build with the VS 2022 toolset. |
| 5.8.1 + VS 2026 18.8.x | Errors in `StaticAssertCompleteType.h` / `IsContiguousContainer.h` when opening classes | Often IntelliSense-only; build to confirm. Forum suggestion: `CppStandard = CppStandardVersion.Cpp20;` in Build.cs if the compiler really fails. |
| 5.8.0 | Non-editor (Development/DebugGame) builds crash before `main` with `xSharedMemoryException`, even template projects | Stale/mixed binaries; delete Binaries/Intermediate/Saved/DerivedDataCache/.vs, regenerate, rebuild. |
| 5.8 upgrade | `A call to an immediate function is not a constant expression` in `TCheckedFormatStringPrivate` | New compile-time format checks; fix the format/args. |
| 5.8 upgrade | Code iterating `FJsonObject::Values` fails to compile | Key type change to support `UE::FSharedString`; adapt key type (`auto&`). |
| 5.8 upgrade | Sub-level navmeshes deleted on load; navigation system crash (one studio's report) | Rebuild navigation after upgrade; keep a backup of nav data; check hotfix notes. |
| 5.8 custom installed builds | Plugins built against 5.8.0/5.8.1 rejected by a 5.8.2 installed build ("Missing Modules", BuildId mismatch) | Rebuild plugins for the exact hotfix; Launcher builds not affected per report. |
| 5.8 docs | Chinese/Japanese "Setting up Visual Studio" pages list a wrong MSVC version | Trust `Engine/Config/Windows/Windows_SDK.json` / English docs. |
| 5.8.0 Rider 2026.1.3 | False-positive red code after upgrading a 5.7.4 project | Update Rider/RiderLink, refresh project model, regenerate project files. |
| 5.7 + VS 2026 | Project file generation fails; Datasmith Max exporter plugin Target.cs forces VS 2022 | Delete the forcing lines / `BuildConfiguration.xml`. |
| 5.6.1 + VS 2026 | Build fails; forum "UE5.6.1 with Visual Studio 2026 bug and hack" | Use VS 2022 for 5.6. |
| 5.3-5.4+ | UBT rejects MSVC 14.39.33519-14.39.99999 | Install 14.38 or a newer toolset. |
| All 5.x | GameInstance vs world subsystem initialization order differs between PIE and standalone (UE-186247) | Don't depend on cross-subsystem init order in `UGameInstance::Init`; use `InitializeDependency`/lazy access. |
| All 5.x Launcher builds | `Server targets are not currently supported from this engine distribution.` | Not a bug: dedicated server needs a source build. |
