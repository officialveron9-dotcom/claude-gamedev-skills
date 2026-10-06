# Animation performance: levers, CVars, traps

## Measure first

- `stat anim`, `stat game`: a quick per-frame view.
- Unreal Insights (CPU, with the animation trace) shows game-thread vs worker split and which AnimBPs dominate.
- Rewind Debugger plus the Animation Insights plugin: poses, curves, montage and notify timeline, and Motion Matching choices.
- `ShowDebug ANIMATION`, `ShowDebug Bones`, `a.VisualizeLODs 1` show the LOD each mesh actually uses.

## Verified console variables

| CVar | Effect | Use |
|---|---|---|
| `a.ParallelAnimUpdate` | Blend tree, native update, asset players and montages update on worker threads | Keep at 1. Set 0 only to A/B test |
| `a.ParallelAnimEvaluation` | Pose evaluation through the task graph | Keep at 1 |
| `a.URO.Enable` | Global URO toggle | A/B test |
| `a.URO.Draw` | Color-coded boxes showing each mesh's anim rate | Verify throttling |
| `a.URO.ForceAnimRate N` | Force evaluation every N frames | Preview what aggressive URO looks like |
| `a.URO.ForceInterpolation 1` | Force interpolation between evaluations | Preview |
| `a.Budget.Enabled` | Turns the Animation Budget Allocator on or off | Must be 1 for the allocator to work |
| `a.Budget.BudgetMs` | Target ms for budgeted meshes | Set per platform via scalability |
| `a.Budget.Debug.Enabled` | On-screen allocator overlay | Tuning |
| `a.Budget.AlwaysTickFalloffAggression` | How fast "always tick" meshes are reduced under load (default 0.8) | Tuning |
| `a.Budget.InterpolationMaxRate` | Tick rate while interpolating (default 6) | Tuning |
| `a.Budget.MaxTickRate` | Maximum tick rate the allocator allows | Tuning |
| `a.Budget.BudgetPressureSmoothingSpeed` | Smoothing of budget pressure (default 3.0) | Tuning |
| `a.Budget.BudgetFactorBeforeAggressiveReducedWork` | When reduced work kicks in | Tuning |
| `a.VisualizeLODs` | LOD overlay | Debug |

5.8 added more `a.Budget.*` CVars (per Tom Looman's 5.8 notes). Type `a.Budget.` in the console and autocomplete instead of guessing names.

## URO vs Budget Allocator vs tick option

| Mechanism | Scope | Trap |
|---|---|---|
| **URO** (`Enable Update Rate Optimizations` on the mesh, plus `Display Debug Update Rate Optimizations`) | Per mesh, reduces the rate by screen size or LOD | Curves read by gameplay (forum: unexpected anim curve values with URO) and notifies get coarse. Disable URO on meshes whose curves or notifies drive gameplay |
| **Animation Budget Allocator** (plugin, Component Class `SkeletalMeshComponentBudgeted`) | A global ms budget that throttles meshes by significance | It controls the tick rate externally, so do not also hand-tune URO on the same mesh. A forum report says interpolation can feel like a frame drop, so check `InterpolationMaxRate`. Hero meshes should stay plain `SkeletalMeshComponent` |
| **VisibilityBasedAnimTickOption** | Off-screen behavior | `OnlyTickPoseWhenRendered` freezes montages and notifies off-screen. `OnlyTickMontagesWhenNotRendered` keeps montages running but skips the AnimGraph. `AlwaysTickPose` ticks without refreshing bones. `AlwaysTickPoseAndRefreshBones` also refreshes bones, which socket-attached props need when off-screen |

Budget Allocator setup:
1. Enable the plugin. Set the mesh component's Component Class to `SkeletalMeshComponentBudgeted` (in C++, `USkeletalMeshComponentBudgeted`).
2. `a.Budget.Enabled 1`, then set `a.Budget.BudgetMs` per scalability level.
3. Significance: let the component compute it automatically, or set it yourself from a Significance Manager. Without meaningful significance, important NPCs get throttled like background ones.
4. Tune with `a.Budget.Debug.Enabled 1`.

## Tier plan (starting point, measure on target hardware)

| Tier | Who | AnimBP | IK | MetaHuman / LOD | Tick |
|---|---|---|---|---|---|
| Hero | Player, active opponent | Full, MM optional | FBIK shot rig, look-at | Optimized High, strands LOD0, correctives on | Always, no URO or budget |
| Near | Bartender, players at the next table | Simplified (state machine, slots) | Look-at only | Optimized Medium, cards, neck correctives off, face LOD threshold 1 | URO or budgeted |
| Background | Seated or standing spectators | Animation Sharing or Leader Pose groups | None | Optimized Low, `Forced LOD`, no grooms simulation, no correctives | Budgeted, `OnlyTickPoseWhenRendered` |
| Crowd (arena) | Hundreds | VAT (AnimToTexture, Experimental) or MetaHuman Collections (Experimental, 5.8) | None | ISM/ISKM | GPU-driven |

Initial budgets for 60 fps: keep the animation game-thread cost well under 1 ms and the worker cost at about 2 ms total for the hall, with `a.Budget.BudgetMs` around 1 ms for budgeted NPCs. These are assumptions, not Epic numbers. Validate them in Insights.

## Other levers and traps

- **Skeletal mesh LODs:** remove finger and face bones on low LODs (bone reduction). Every skeletal control node has an `LOD Threshold`. Physics assets and cloth should end at a LOD as well.
- **Leader Pose** (`SetLeaderPoseComponent`, renamed from Master Pose in 5.1) for modular clothing on the same skeleton. Use `Copy Pose From Mesh` only when the skeletons differ, because it costs more.
- **Blueprint VM in the AnimGraph:** `Warn About Blueprint Usage` lists the culprits. Bind pins to members or Property Access.
- **Curves:** MetaHuman faces carry hundreds of curves. Limit RigLogic by LOD rather than evaluating it everywhere.
- **Cast To in the AnimBP every frame** is cheap on its own but forces game-thread work. Cache the owner once in `NativeInitializeAnimation`.
- **Zero-weight branches are not evaluated** after a blend completes. Put expensive optional work (FBIK, look-at) behind `Blend Poses by bool`. A node with `Alpha = 0` skips most of its own solve, but it still updates along with its whole input chain, so don't rely on alpha for savings.
