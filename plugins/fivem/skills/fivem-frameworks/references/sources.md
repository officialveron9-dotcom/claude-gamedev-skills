# Sources (accessed 2026-10-06)

Repositories were cloned at HEAD on 2026-10-06; tag dates from git.

| URL | Backs up |
|---|---|
| https://github.com/esx-framework/esx_core (tag 1.15.2, 2026-09-06; 1.14.0 2026-07-17) | es_extended manifest, `getSharedObject` export + legacy event handler, imports.lua, xPlayer methods, callbacks via esx_lib, events, ox_inventory auto-detection, sample server.cfg start order, esx_lib introduced in 1.14.0 |
| https://docs.esx-framework.org/en/tutorial/updating (via search snippet) | `esx:getSharedObject` event deprecated (since 1.9) in favour of export/import |
| https://github.com/qbcore-framework/qb-core (manifest 1.3.0, HEAD 2026-08-24) | GetCoreObject (filters), Player class + Functions wrappers, money rules (MinusLimit, DontAllowMinus), callbacks implementation, events, no item functions |
| https://github.com/qbcore-framework/qb-inventory (2.2.3, 2026-09-11) | AddItem/RemoveItem/HasItem export signatures, ItemBox event |
| https://github.com/qbcore-framework/qb-docs | Event reference, core object docs |
| https://github.com/Qbox-project/qbx_core (v1.24.0 2026-08-22, HEAD 2026-09-30) | `provide 'qb-core'`, startup requirements, exports (GetPlayer, AddMoney, RemoveMoney, SetJob, HasGroup, Notify, ExploitBan), string=citizenid resolution, bridge convars |
| https://github.com/Qbox-project/qbox-project.github.io (docs.qbox.re source) | Converting from QBCore (grade numbers, collation, replacements), convars, modules |
| https://github.com/overextended/ox_lib (v3.40.0, 2026-10-03) | Maintenance back at overextended since 2026-04-24 ("update name and refs"), init.lua errors, callback API/timeout, cache keys, strict-mode advisory, server lib.notify deprecated |
| https://github.com/overextended/overextended.github.io (overextended.dev source, 2026-08-27) | "Discontinued in 2025 ... development resumed in 2026", ox_lib/ox_target/ox_inventory/oxmysql docs |
| https://github.com/overextended/ox_inventory (v2.48.0, 2026-10-03) | Convars (`inventory:framework`, accounts, imagepath), bridges esx/nd/ox/qbx only, AddItem/RemoveItem/CanCarryItem/Search/GetItemCount/RegisterStash, item callback events |
| https://github.com/overextended/ox_target (v1.18.1) | API functions, framework detection (no qb), qtarget compat only, auto-cleanup on resource stop |
| https://github.com/overextended/oxmysql (v2.14.3, 2026-10-06) | lib/MySQL.lua methods, convars, `provide mysql-async/ghmattimysql`, node 22 + `/server:12913`, error messages |
| https://overextended.dev/oxmysql (source above) | MariaDB recommendation, connection string formats, named placeholders deprecated, prepare limitations, upsert advice |
| https://github.com/CommunityOx/ox_lib, /ox_inventory, /oxmysql, /ox_target | Fork versions stalled (3.32.3 / 2.45.0 / 2.13.1 / 1.18.0, Feb-Apr 2026) |
| https://github.com/CommunityOx/ox_inventory/releases (search snippet) | Repository archived 2026-04-28 |
| https://docs.fivem.net/docs/server-manual/frameworks/ | Official framework list (ESX, ND, QBCore, Qbox, vRP) |
