-- luacheck-Konfiguration fuer FiveM-Resources (CfxLua, Lua 5.4).
-- Aufbau nach GoatG33k/fivem-lua-lint-action (MIT), aber ohne die generierten Natives-Listen:
-- Natives und Framework-Objekte beginnen mit einem Grossbuchstaben und werden ueber das Muster in
-- `ignore` nicht als "accessing undefined variable" (113) gemeldet. Alle anderen Checks bleiben aktiv
-- (Syntaxfehler, unbenutzte/ueberdeckte Variablen, kleingeschriebene unbekannte Globals).
-- Vollstaendige Natives-Listen (finden Tippfehler in Natives) erzeugt generate-rc.ts aus dem Action-Repo
-- aus https://runtime.fivem.net/doc/natives.json und natives_cfx.json.
std = "max"
codes = true
max_line_length = 160
max_cyclomatic_complexity = 60
ignore = {
    "113/[A-Z][A-Za-z0-9_]*", -- Natives und Framework-Globals (CreateThread, GetPlayerPed, ESX, QBCore, ...)
    "611", "612", "613", "614", -- Whitespace-Warnungen
}

-- CfxLua-Laufzeit (Legacy und Enhanced), beide Seiten
globals = { GlobalState = { other_fields = true } }
read_globals = {
    Citizen = { fields = { "Wait", "CreateThread", "SetTimeout", "Await", "Trace", "InvokeNative" } },
    exports = { other_fields = true },
    json = { fields = { "encode", "decode" } },
    msgpack = { fields = { "pack", "unpack", "new" } },
    "Wait", "CreateThread", "SetTimeout", "Await", "Trace", "joaat",
    "vec", "vec2", "vec3", "vec4", "vector2", "vector3", "vector4", "quat",
    "AddEventHandler", "RegisterNetEvent", "TriggerEvent", "RemoveEventHandler", "AddStateBagChangeHandler",
    "GetCurrentResourceName", "GetResourceState", "LoadResourceFile", "GetGameTimer", "GetHashKey",
    "lib", "cache", -- ox_lib
    "ESX", "QBCore", "exports",
}

-- Serverseite
files["**/server/**/*.lua"].read_globals = {
    "source", "TriggerClientEvent", "TriggerLatentClientEvent", "RegisterServerEvent",
    "GetPlayers", "GetPlayerIdentifiers", "PerformHttpRequest", "MySQL",
}
files["**/server.lua"].read_globals = files["**/server/**/*.lua"].read_globals
files["**/sv_*.lua"].read_globals = files["**/server/**/*.lua"].read_globals

-- Clientseite
files["**/client/**/*.lua"].read_globals = { "TriggerServerEvent", "RegisterNUICallback", "SendNUIMessage", "SetNuiFocus", "PlayerPedId", "PlayerId" }
files["**/client.lua"].read_globals = files["**/client/**/*.lua"].read_globals
files["**/cl_*.lua"].read_globals = files["**/client/**/*.lua"].read_globals

-- Manifest: eigene DSL (fx_version 'cerulean' usw.), keine Global-Checks
files["**/fxmanifest.lua"] = { ignore = { "111", "113", "611", "614" } }
files["**/__resource.lua"] = { ignore = { "111", "113", "611", "614" } }

-- Fremde Dateien nicht pruefen. Eckige Klammern sind in luacheck-Globs Zeichenklassen; Ordner wie
-- resources/[cfx-default] deshalb nicht hier eintragen, sondern luacheck nur auf eigene Resources aufrufen.
exclude_files = { "**/node_modules/**", "**/*.fxap", "**/stream/**" }
