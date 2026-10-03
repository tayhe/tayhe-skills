# Raw CDP over Python Websockets

当环境受限、无法使用 Playwright，或需要极其轻量的单脚本零外部重量级依赖时，可使用 Python 原生 `websockets` 库直接向远端 Chrome 的 CDP WebSocket 发送 JSON-RPC 报文。

---

## 1. 依赖与执行（基于 uv）

无需安装本地浏览器，只需 `websockets` 库：
```bash
uv run --with websockets python cdp_raw_task.py
```

---

## 2. 关键：跨机 WebSocket 地址重写

Windows 端 `/json/version` 返回的 `webSocketDebuggerUrl` 通常为本地回环形式（`ws://127.0.0.1:9222/...`）。从 Linux 跨机连接时，**必须将 Host 替换为 Windows 的 Tailscale IP**（`100.100.1.118`）：

```python
import json
import urllib.request

ENDPOINT = "http://100.100.1.118:9222"

# 1. 获取目标 Page 或 Browser 的 WebSocket URL
pages = json.loads(urllib.request.urlopen(f"{ENDPOINT}/json").read())
page = [p for p in pages if p["type"] == "page"][0]
raw_ws = page["webSocketDebuggerUrl"]

# 2. 必须重写 Host，避免连到 Linux 本地的 127.0.0.1
target_ws = raw_ws.replace("127.0.0.1:9222", "100.100.1.118:9222")
```

---

## 3. 完整示例脚本模板

```python
import asyncio
import base64
import json
import urllib.request
import websockets

ENDPOINT = "http://100.100.1.118:9222"


async def eval_js(ws, expr, msg_id=1):
    """在当前页面执行 JS 并返回求值结果"""
    await ws.send(json.dumps({
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {"expression": expr, "returnByValue": True}
    }))
    while True:
        raw = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
        if raw.get("id") == msg_id:
            return raw.get("result", {}).get("result", {}).get("value", None)


async def drain_events(ws, duration=2.0):
    """排空并监听 duration 秒内的控制台或页面事件"""
    logs = []
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=0.3)
            msg = json.loads(raw)
            if msg.get("method") == "Runtime.consoleAPICalled":
                args = msg.get("params", {}).get("args", [])
                text = " ".join(str(a.get("value", "")) for a in args)
                logs.append(text)
        except (asyncio.TimeoutError, Exception):
            continue
    return logs


async def main():
    # 查找已有标签页
    pages = json.loads(urllib.request.urlopen(f"{ENDPOINT}/json").read())
    active_pages = [p for p in pages if p.get("type") == "page"]
    if not active_pages:
        # 没有则新建
        new_tab = json.loads(urllib.request.urlopen(f"{ENDPOINT}/json/new?https://example.com").read())
        target_ws = new_tab["webSocketDebuggerUrl"].replace("127.0.0.1:9222", "100.100.1.118:9222")
    else:
        target_ws = active_pages[0]["webSocketDebuggerUrl"].replace("127.0.0.1:9222", "100.100.1.118:9222")

    async with websockets.connect(target_ws, max_size=15 * 1024 * 1024) as ws:
        # 启用必要领域事件
        await ws.send(json.dumps({"id": 10, "method": "Page.enable", "params": {}}))
        await ws.send(json.dumps({"id": 11, "method": "Runtime.enable", "params": {}}))

        # 导航
        await ws.send(json.dumps({
            "id": 12,
            "method": "Page.navigate",
            "params": {"url": "https://example.com"}
        }))
        await drain_events(ws, 3.0)

        # 获取页面信息
        title = await eval_js(ws, "document.title", msg_id=13)
        print(f"Page Title: {title}")

        # 截图
        await ws.send(json.dumps({"id": 14, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
        raw = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
        img_bytes = base64.b64decode(raw["result"]["data"])
        with open("/tmp/raw_screenshot.png", "wb") as f:
            f.write(img_bytes)
        print("截图已保存至 /tmp/raw_screenshot.png")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. 常用核心 CDP 方法速查

| CDP Method | 作用 | 关键参数 / 说明 |
| :--- | :--- | :--- |
| `Runtime.evaluate` | 执行 JavaScript 脚本 | `params: {"expression": "...", "returnByValue": True}` |
| `Page.captureScreenshot` | 截取页面图像 | `params: {"format": "png"}`，返回 Base64 字符串 |
| `Page.navigate` | 跳转到目标网址 | `params: {"url": "https://..."}` |
| `Page.reload` | 刷新当前页面 | `params: {"ignoreCache": True}` |
| `Page.enable` / `Runtime.enable` | 开启页面与控制台事件推送 | 调用前置，否则收不到 Console 与 Lifecycle 事件 |
| `Page.bringToFront` | 将该标签页置于前端焦点 | 调试时唤醒桌面前台展示 |
