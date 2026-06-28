---
name: browser-cdp
description: "Browser automation via raw CDP (Chrome DevTools Protocol) using Python websockets. Use when needing browser control, screenshots, JS execution, console monitoring, navigation, or debugging web pages. No dependency on openclaw or any MCP server — direct JSON-RPC to Chrome's debugging port."
---

# Browser CDP — Raw Python Websockets

Autonomous browser control via Chrome DevTools Protocol. Uses Python `websockets` library to send JSON-RPC commands directly to Chrome's debugging port. No dependency on openclaw, no MCP server needed.

## Prerequisites

- Python `websockets` library (`pip install websockets` or `uv pip install websockets`)
- Chrome/Chromium installed
- Chrome 已启动并开启远程调试端口（参见全局规则中的启动命令）

## Step 1: Verify Chrome is Accessible

```bash
curl -s http://127.0.0.1:9222/json
```

Returns JSON array of open pages. Each page has an `id` field used for CDP connection.

## Step 2: List Pages / Open New Tab

```bash
# List all pages
curl -s http://127.0.0.1:9222/json | python3 -c "
import json,sys
for p in json.load(sys.stdin):
    if p['type']=='page':
        print(f\"{p['id']}: {p['title'][:60]} -> {p['url'][:80]}\")"

# Open new tab
curl -s -X PUT "http://127.0.0.1:9222/json/new?http://localhost:5173/"
```

## Step 3: Control via Python Websockets

### Core Helper Functions

```python
import asyncio, json, websockets

async def eval_js(ws, expr, msg_id=1):
    """Execute JS in the page and return the result."""
    await ws.send(json.dumps({
        'id': msg_id,
        'method': 'Runtime.evaluate',
        'params': {'expression': expr, 'returnByValue': True}
    }))
    while True:
        raw = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
        if raw.get('id') == msg_id:
            return raw.get('result', {}).get('result', {}).get('value', 'N/A')

async def drain(ws, duration=2):
    """Drain all messages for `duration` seconds. Returns console logs."""
    logs = []
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration:
        try:
            raw = asyncio.wait_for(ws.recv(), timeout=0.3)
            msg = json.loads(await raw)
            if msg.get('method') == 'Runtime.consoleAPICalled':
                args = msg.get('params', {}).get('args', [])
                text = ' '.join(str(a.get('value', '')) for a in args)
                logs.append(text)
        except (asyncio.TimeoutError, Exception):
            continue
    return logs
```

### Common Operations

```python
async def main():
    page_id = 'F185FA89040C62A3BA5C0D6B4A1625D4'  # from curl /json
    cdp_url = f'ws://127.0.0.1:9222/devtools/page/{page_id}'

    async with websockets.connect(cdp_url, max_size=10*1024*1024) as ws:
        # Enable events (required for console logs, page load events)
        await ws.send(json.dumps({'id': 0, 'method': 'Page.enable', 'params': {}}))
        await ws.send(json.dumps({'id': 0, 'method': 'Runtime.enable', 'params': {}}))
        await drain(ws)

        # Navigate
        await ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': 'http://localhost:5173/'}}))
        await drain(ws, 5)  # wait for page load

        # Check page state
        title = await eval_js(ws, 'document.title')
        url = await eval_js(ws, 'location.href')

        # Execute JS
        result = await eval_js(ws, 'document.querySelector(".my-class")?.textContent')

        # Screenshot
        await ws.send(json.dumps({'id': 2, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}}))
        raw = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
        import base64
        with open('/tmp/screenshot.png', 'wb') as f:
            f.write(base64.b64decode(raw['result']['data']))

        # Reload
        await ws.send(json.dumps({'id': 3, 'method': 'Page.reload', 'params': {}}))

        # Monitor console (after Runtime.enable)
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < 5:
            try:
                raw = asyncio.wait_for(ws.recv(), timeout=0.3)
                msg = json.loads(await raw)
                if msg.get('method') == 'Runtime.consoleAPICalled':
                    args = msg['params']['args']
                    text = ' '.join(str(a.get('value', '')) for a in args)
                    print(f'Console: {text}')
            except (asyncio.TimeoutError, Exception):
                continue

        # Inject script before page load (requires Page.enable first)
        await ws.send(json.dumps({
            'id': 4,
            'method': 'Page.addScriptToEvaluateOnNewDocument',
            'params': {'source': 'window.__myFlag = true;'}
        }))

        # Bring tab to foreground
        await ws.send(json.dumps({'id': 5, 'method': 'Page.bringToFront', 'params': {}}))

asyncio.run(main())
```

## Key CDP Methods Reference

| Method | Purpose | Notes |
|--------|---------|-------|
| `Runtime.evaluate` | Execute JS, return result | Use `returnByValue: true` for JSON |
| `Page.captureScreenshot` | Screenshot (base64 PNG) | Returns `{result: {data: "..."}}` |
| `Page.navigate` | Go to URL | |
| `Page.reload` | Refresh page | `ignoreCache: true` to bypass cache |
| `Page.enable` | Enable page events | **Required before** `addScriptToEvaluateOnNewDocument` |
| `Runtime.enable` | Enable console events | **Required before** capturing `Runtime.consoleAPICalled` |
| `Page.bringToFront` | Focus the tab | |
| `Page.addScriptToEvaluateOnNewDocument` | Inject JS before page load | Must call `Page.enable` first |

## Event Handling

After `Runtime.enable`, the websocket receives events:

```python
# Runtime.consoleAPICalled — console.log/warn/error
{'method': 'Runtime.consoleAPICalled', 'params': {'args': [{'value': 'hello'}]}}

# Runtime.exceptionThrown — uncaught errors
{'method': 'Runtime.exceptionThrown', 'params': {'exceptionDetails': {'text': '...'}}}
```

Events arrive interleaved with command responses. Filter by checking `msg.get('method')`.

## Waiting for Page State

Don't use blind `asyncio.sleep()`. Wait for observable state:

```python
# Wait for element to exist
async def wait_for(ws, js_predicate, timeout=10):
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < timeout:
        result = await eval_js(ws, js_predicate)
        if result:
            return result
        await asyncio.sleep(0.3)
    raise TimeoutError(f'Condition not met: {js_predicate}')

# Usage
await wait_for(ws, '!!window.__live2dModel')
await wait_for(ws, 'document.querySelector(".loaded") !== null')
```

## Gotchas

- **`Page.addScriptToEvaluateOnNewDocument` requires `Page.enable` first** — otherwise the injected script silently doesn't run
- **Background tab rAF throttling**: Chrome throttles `requestAnimationFrame` to 0fps in background tabs. Use `setInterval` for animations that must work when tab is not focused
- **Console events interleaved with responses**: Always check `msg.get('method')` to distinguish events from command responses
- **`--user-data-dir` flag**: If Chrome is already running without it, launching with a new user-data-dir creates a separate instance. Without it, the second launch just opens a new window in the existing instance (and CDP may not be enabled)
