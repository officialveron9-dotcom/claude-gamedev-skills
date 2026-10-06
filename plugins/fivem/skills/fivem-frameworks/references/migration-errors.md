# Framework / DB errors after installs and migrations

Read when a console/F8 error mentions ESX, QBCore, Qbox, ox_* or MySQL.

| Message (excerpt) | Cause | Fix |
|---|---|---|
| `attempt to index a nil value (global 'ESX')` | Old `TriggerEvent('esx:getSharedObject')` pattern, or es_extended not started before the script, or import missing on that side | `shared_script '@es_extended/imports.lua'`; ensure es_extended earlier; for client-only scripts the import must be in `client_scripts`/`shared_scripts`. |
| `attempt to index a nil value (global 'QBCore')` | `QBCore:GetObject` event or missing `GetCoreObject()` call | `local QBCore = exports['qb-core']:GetCoreObject()`. |
| `attempt to call a nil value (field 'AddItem')` on `Player.Functions` | qb-core no longer has item functions | `exports['qb-inventory']:AddItem(...)` or ox_inventory. |
| `attempt to index a nil value (local 'xPlayer'/'Player')` | Player not loaded (char select), wrong `source` (captured after `Wait`), string source | Nil-check; `local src = source` first; `tonumber`. |
| `No such export getSharedObject in resource es_extended` | es_extended not started / crashed while loading (look above for its own error, e.g. missing esx_lib or DB) | Fix es_extended start; `ensure esx_lib` before es_extended (1.14+). |
| `No such export GetCoreObject in resource qb-core` with Qbox | `qbx:enablebridge` false, or qbx_core failed to start | Enable bridge or port to `exports.qbx_core`. |
| qbx_core prints `inventory:framework must be set to "qbx"` and server quits | Missing convar | `setr inventory:framework "qbx"` before `ensure qbx_core`. |
| qbx_core: `ox_lib version 3.20.0 or higher is required` / `ox_inventory version 2.42.1 ...` | Outdated ox resources | Update from github.com/overextended releases. |
| qbx_core: `OneSync Infinity is not enabled` | OneSync off | txAdmin settings -> OneSync on (or `+set onesync on`). |
| `ox_lib must be started before this resource.` | Start order | `ensure ox_lib` before dependants; add `dependency 'ox_lib'`. |
| `Cannot load ox_lib more than once.` | `@ox_lib/init.lua` listed twice (often also inside a bridge) | Keep one entry. |
| ox_lib UI blank / `web/build/index.html` not found | Cloned source instead of release | Download the release zip or `cd web && bun i && bun run build`. |
| `callback 'x' does not exist` / `callback event 'x' timed out` (ox_lib) | Callback not registered on the other side, wrong name, or handler errored | Register on the correct side; check `SCRIPT ERROR` above; ensure the provider resource started. |
| `Unable to establish a connection to the database (ECONNREFUSED)` | DB not running / wrong host/port | Start MariaDB, check `mysql_connection_string` host/port (127.0.0.1 vs localhost). |
| `... (ER_ACCESS_DENIED_ERROR)` | Wrong user/password or user not allowed from host | Fix credentials/grants; special chars in password -> other connection-string format. |
| `... (ER_BAD_DB_ERROR)` | Database name does not exist | Create DB / fix name. |
| `Requested authentication using unknown plugin auth_gssapi_client` | MariaDB user uses GSSAPI auth | Use a normal password user. |
| `mysql_connection_string structure was invalid` | Malformed string | Use `mysql://user:pass@host:3306/db` or `user=..;password=..;host=..;database=..`. |
| `Expected N parameters, but received M.` | Placeholder count mismatch | Match `?` count to the params array. |
| `ER_PARSE_ERROR` near `group` / `stored` | MySQL 8 reserved word | Backtick-quote identifiers or use MariaDB. |
| `ER_NO_SUCH_TABLE` after installing a script | SQL file not imported | Import the resource's `.sql`; ESX/QB/Qbox base SQL too. |
| `Illegal mix of collations` / FK error on `citizenid` (Qbox migration) | Collation mismatch | Set `utf8mb4_unicode_ci` on all `citizenid` columns; rerun `qbx_core.sql`. |
| `<res> took N.NNNNms to execute a query!` (oxmysql slow query) | Missing index / big table scans | Add indexes on `identifier`/`citizenid`/`owner`/`plate`; `set mysql_debug ["res"]` to inspect. |
| mysql-async script: `attempt to index a nil value (global 'MySQL')` | `@mysql-async/lib/MySQL.lua` reference or no lib include | Use `@oxmysql/lib/MySQL.lua` (oxmysql provides mysql-async exports, not its lib path). |
| Items exist in DB but not usable in ox_inventory | Items defined only in framework table | Add to `ox_inventory/data/items.lua`; restart ox_inventory. |
| ESX default inventory gone, F2 does nothing | `ox_inventory` folder present -> ESX switched to ox mode | Remove the folder or run ox_inventory properly. |
