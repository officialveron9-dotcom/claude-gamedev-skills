# Sources (accessed 2026-10-06)

| URL | Backs up |
|---|---|
| https://docs.fivem.net/docs/server-manual/server-commands/ (source: citizenfx/fivem-docs, 2026-10-01) | Build table up to 3889 + aliases, `sv_replaceExeToSwitchBuilds`, `sv_maxClients` OneSync rules, startup-only convars, `increase_pool_size` pools, `sv_master1`, ACE commands, endpoints, `sv_pureLevel`, `sv_kvsName` |
| https://github.com/citizenfx/fivem/blob/master/code/client/shared/CrossBuildRuntime.h | Default/mandated GTA5 build 3258 when unset; build enum (3570, 3751, 3788 patch, 3889) |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/ServerResources.cpp and citizen-resources-core/src/ResourceManagerConstraintsComponent.cpp | Constraint failure messages |
| https://github.com/citizenfx/fivem tags (git ls-remote; tag commit dates) | Builds 35245 (2026-08-20), 36727 (2026-09-28), 36897 (2026-09-30); 12913 = Node 22 update (2025-02-17) |
| https://www.verygames.com/en/nyuusu/pg-40-fivem-fxserver-35245-updata-2026-10-15 (search snippet only, page blocked) and other hosting blogs via search | 35245 Recommended since 2026-08-20; client cutoff for older servers 2026-10-15 - secondary, unverified against forum.cfx.re |
| https://docs.fivem.net/docs/server-manual/end-of-support-end-of-life/ | Support windows, 3-month joinability |
| https://github.com/jgscripts/fivem-artifacts-db (db.json 2026-09-10) | Known-bad artifact ranges |
| https://docs.fivem.net/docs/server-manual/setting-up-a-server-vanilla/ + static/examples/config/server.cfg | Example server.cfg, Linux/Windows archive names, common issues |
| https://docs.fivem.net/docs/support/server-issues/ | Listing troubleshooting, 48-slot limit, Defender exclusion, info.json check |
| https://forum.cfx.re/t/introducing-new-client-changes/5377566 (search snippet) | Listing limits: project name 40, server name 120, description 250 chars |
| https://github.com/citizenfx/txAdmin (v8.1.1, docs/env-config.md, docs/events.md, docs/recipe.md, core/lib/fxserver/fxsConfigHelper.ts, core/modules/FxRunner/utils.ts) | TXHOST_* vars, deprecated convars, onesync via txAdmin, endpoint validation, shutdown/restart events, recipe tasks |
| https://overextended.dev/oxmysql (source: overextended/overextended.github.io) | MariaDB over MySQL 8 / XAMPP, connection string formats and forbidden chars |
| https://github.com/esx-framework/esx_core server.cfg, https://github.com/Qbox-project/qbox-project.github.io (converting.mdx) | Framework start orders, Qbox cfg files, collation |
| https://docs.fivem.net/docs/scripting-reference/resource-manifest/ and https://docs.fivem.net/docs/game-references/data-files/ | `data_file` types, glob support, `this_is_a_map`, `/policy:subdir_file_mapping` |
| https://docs.fivem.net/docs/assets-manual/beginner-series/part-4/ | Map resource: stream folder, `this_is_a_map`, `_manifest.ymf` |
| https://docs.fivem.net/docs/cookbook/2021/04/09/fyi-fivem-and-redm-support-raw-ymap-ytyp-files/ | Raw XML ymap/ytyp |
| https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/ResourceStreamComponent.cpp | Asset size warning thresholds |
| https://forum.cfx.re/t/how-to-streaming-addon-clothes-and-ped-props-for-mp-freemode-models/458854 , https://fivemx.com/tutorials/how-to-stream-addon-clothes-props-fivem-models (search snippets) | `^` separator naming, SHOP_PED_APPAREL_META_FILE usage - secondary |
| https://docs.fivem.net/docs/developers/legacy-vs-enhanced/ | Enhanced file names, only newest build |
