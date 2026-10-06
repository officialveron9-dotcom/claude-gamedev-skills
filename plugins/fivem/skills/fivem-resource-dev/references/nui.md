# NUI traps and patterns

Read when building or debugging an NUI page (HTML/React/Vue UI inside FiveM).

## Wiring

```lua
-- client.lua
local open = false

local function setOpen(state)
    open = state
    SetNuiFocus(state, state)                 -- keyboard, mouse
    SendNUIMessage({ action = 'setVisible', data = state })
end

RegisterCommand('tablet', function() setOpen(not open) end, false)

RegisterNUICallback('close', function(_, cb)
    setOpen(false)
    cb({ ok = true })                         -- ALWAYS answer
end)

RegisterNUICallback('buy', function(data, cb)
    -- data is untrusted user input: forward to server, validate there
    local ok = lib.callback.await('shop:buy', false, data.item, data.amount)
    cb({ ok = ok })
end)

AddEventHandler('onResourceStop', function(res)
    if res == GetCurrentResourceName() and open then SetNuiFocus(false, false) end
end)
```

```js
// page
window.addEventListener('message', (e) => {
  const { action, data } = e.data;
  if (action === 'setVisible') app.visible = data;
});

async function post(name, body = {}) {
  const res = await fetch(`https://${GetParentResourceName()}/${name}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=UTF-8' },
    body: JSON.stringify(body),
  });
  return res.json();
}
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') post('close'); });
```

## Traps

| Symptom | Cause | Fix |
|---|---|---|
| fetch never resolves / UI freezes on click | `cb` not called in `RegisterNUICallback` (no warning is printed), or the handler errored: `error during NUI callback <name>: <err>` in F8 | Call `cb(...)` on every path, including early returns; fix the Lua error. |
| fetch to `https://cfx-nui-myres/close` 404 | Mixed up URL schemes | Callbacks: `https://<resourceName>/<callback>`. Files: `https://cfx-nui-<resourceName>/<path>`. |
| `http://myres/cb` fails | `fx_version 'cerulean'` loads NUI as secure context | Use `https://`. |
| Blank page, JS/CSS 404 | Build assets not in `files`, or Vite `base` absolute | `files { 'web/dist/**/*' }`; set Vite `base: './'`. |
| Player stuck with cursor, cannot move | Focus not released (resource restarted/crashed while open) | Release in close path and `onResourceStop`. Debug: `SetNuiFocus(false,false)`. |
| Game keys still needed while UI open | `SetNuiFocus` blocks input | `SetNuiFocusKeepInput(true)` and disable specific controls each frame while open. |
| `GetParentResourceName is not defined` in local browser dev | Only exists inside FiveM CEF | Mock it in dev (`window.GetParentResourceName ??= () => 'myres'`). |
| UI eats FPS while hidden | Animations/blur/`backdrop-filter`/video running when invisible, or `SendNUIMessage` every frame | Unmount or `display:none` when hidden; push state on change, not per frame. |
| Data typed wrongly | NUI JSON: Lua integer keys -> JSON object, empty table -> `[]` or `{}` ambiguity | Send arrays as sequential tables; normalise on the JS side. |
| Escrowed resource UI unreadable | NUI is not escrow-encrypted | Never put secrets/logic that must stay private in NUI. |

## Devtools

`nui_devTools` in F8 (developer mode) or open `http://localhost:13172/` in a Chromium browser while the game runs.

## Security

Every NUI callback is client-controlled: a cheater can POST to it directly or call the server event behind it. Validate on the server as for any net event (item exists, price from server config, quantity bounds, distance to shop).
