# Remote CDP Setup (Windows Chrome Debug Mode)

Verified with Chrome/147 on Windows via `--remote-debugging-port=9222`.

## Step 1: Start Chrome in debug mode (PowerShell)

```powershell
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$argList = @(
  "--remote-debugging-port=9222",
  "--remote-allow-origins=*",
  "--user-data-dir=$env:LOCALAPPDATA\Google\Chrome\cdp-profile"
)
Start-Process $chromePath -ArgumentList $argList
```

## Step 2: Verify Chrome is listening

```bash
curl http://127.0.0.1:9222/json/version
```

Expected output includes `"webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/browser/..."`.

## Step 3: Configure OpenClaw remote profile

In `~/.openclaw/openclaw.json`:

```json
{
  "browser": {
    "profiles": {
      "remote": {
        "cdpUrl": "ws://127.0.0.1:9222",
        "color": "#00AA00"
      }
    }
  }
}
```

Use the raw `webSocketDebuggerUrl` value from Step 2 as `cdpUrl`.

## Step 4: Connect and verify

```bash
openclaw browser --browser-profile remote start
openclaw browser --browser-profile remote snapshot
openclaw browser --browser-profile remote screenshot
```

## Cross-network variants

| OpenClaw location | Chrome host | `cdpUrl` |
|---|---|---|
| Same Windows machine | Same machine | `ws://127.0.0.1:9222` |
| WSL2 on Windows | Windows host | `http://host.docker.internal:9222` (HTTP discovery) |
| Docker on Windows | Windows host | `http://host.docker.internal:9222` (HTTP discovery) |
| Remote machine | External host | `ws://<windows-ip>:9222` |

HTTP discovery (`http://` prefix) lets OpenClaw call `/json/version` to find the WebSocket URL automatically.