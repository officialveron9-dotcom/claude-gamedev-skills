# Toolchain per UE version and setup traps

Authoritative per install: `Engine/Config/Windows/Windows_SDK.json`, `Engine/Config/Linux/Linux_SDK.json` (read these when a version question matters; docs can lag — the 5.8 Chinese/Japanese docs listed a wrong MSVC version).

| UE | Visual Studio | MSVC | Windows SDK | Linux clang / toolchain |
|---|---|---|---|---|
| 5.8 (Jun 2026; hotfixes 5.8.1 Jul 28, 5.8.2 Aug 31, 5.8.3 later) | VS 2022 17.14+ (minimum), VS 2026 18.x recommended | min 14.38, recommended 14.50 (VS 2026 toolset v145) | min 10.0.22621.0, default 10.0.26100.0 | clang 20.1.8 (cross toolchain v26) ; LLVM-for-Windows clang min 18.1.8, preferred 20.1.8 |
| 5.7 (Nov 2025) | VS 2022 17.8+ (17.14 default); VS 2026 partially working (plugin Target.cs forcing VS2022 broke generation) | preferred 14.44 | 10.0.26100 recommended | `v26_clang-20.1.8-rockylinux8` |
| 5.6 (Jun 2025) | VS 2022 17.8+ | min 14.38 | min 10.0.22621.0 | see Linux_SDK.json (v24/clang 19 reported problematic for 5.6/5.7) |
| 5.4-5.5 | VS 2022 (VS 2019 removed in 5.4, deprecated in 5.3) | 14.38 is the safe choice; **14.39.33519-14.39.99999 banned** by UBT | 10.0.22621.0 | clang 18.x |

Rider: use a Rider release from 2026.1 or later for 5.8 projects (2026.1.3 showed false-positive errors right after 5.7.4 -> 5.8.0 upgrades; update Rider / RiderLink plugin). Rider installs RiderLink into the project or engine on first open.

## VS Installer components (Windows)

- Workload "Game development with C++" (includes Unreal Engine installer/integration options) and/or "Desktop development with C++".
- Individual components: MSVC x64/x86 build tools of the required version (e.g. "MSVC v143 - VS 2022 C++ x64/x86 build tools (v14.44...)", or the v145 toolset in VS 2026), Windows 11 SDK (10.0.22621 or 10.0.26100), .NET SDK.
- Multiple MSVC versions can coexist; UBT picks the preferred one from Windows_SDK.json. Force a version (source/advanced users) via `BuildConfiguration.xml`:
```xml
<?xml version="1.0" encoding="utf-8" ?>
<Configuration xmlns="https://www.unrealengine.com/BuildConfiguration">
  <WindowsPlatform>
    <CompilerVersion>14.44.35207</CompilerVersion>
  </WindowsPlatform>
</Configuration>
```
Locations: `%APPDATA%\Unreal Engine\UnrealBuildTool\BuildConfiguration.xml`, `Documents\Unreal Engine\UnrealBuildTool\BuildConfiguration.xml`, `<Project>/Saved/UnrealBuildTool/BuildConfiguration.xml`. A forgotten `<Compiler>VisualStudio2022</Compiler>` here causes "Visual Studio 2022 x64 must be installed" after switching to VS 2026.

## Known toolchain issues

- UE 5.8.x + VS 2026: UBT asks for VS 2022 although VS 2026 is installed (forced compiler in BuildConfiguration.xml or a plugin Target.cs; also check both VS versions' C++ workloads). Community tutorial on Epic's learning portal covers re-linking UE 5.8 to VS 2026.
- UE 5.8 source build + VS 2026: `nvtess.h(154): fatal error C1083: Cannot open include file: 'hash_map'`.
- UE 5.8.1 + VS 2026 (18.8.x): IntelliSense/compile errors reported in `StaticAssertCompleteType.h` / `IsContiguousContainer.h` when opening classes; may be IntelliSense-only — verify with an actual build before changing `CppStandard`.
- UE 5.6.1 + VS 2026: required a workaround (forum "UE5.6.1 with Visual Studio 2026 bug and hack") — use VS 2022 for 5.6.
- MSVC 14.39.33519-14.39.99999: banned by UBT for 5.3/5.4+ (compiler bug).

## Linux / cross-compile

- Cross-compile from Windows: download Epic's toolchain for your engine version, run installer, it sets `LINUX_MULTIARCH_ROOT`; restart IDE/Editor/Launcher. Mismatched toolchain -> UBT "Linux SDK not found"/clang version errors.
- Native Linux: run `Setup.sh`, `GenerateProjectFiles.sh`, build with `make` or `Engine/Build/BatchFiles/Linux/Build.sh`; the bundled toolchain is downloaded by Setup.
- Supported distros per 5.8 notes: Ubuntu 22.04+, Rocky/RHEL 8+.
- Linux file systems are case-sensitive: include paths and asset references must match case.
