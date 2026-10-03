---
name: remote-chrome
description: "Remote Chrome browser automation and debugging via CDP over Tailscale. Use when needing to control Windows Chrome (tayhe-desktop) from Linux: opening URLs, scraping web content with existing desktop cookies/login sessions, taking screenshots, evaluating JavaScript, inspecting DOM, or automating browser interactions."
---

# Remote Chrome CDP Skill

从 Linux 开发服务器（`tayhe-cloud`，`100.100.1.1`）通过 Tailscale 专网和 Chrome DevTools Protocol（CDP 协议）远程控制 Windows 台式机（`tayhe-desktop`，`100.100.1.118`）的 Chrome 浏览器。

特点：
- **方案一直连模式**：基于 Windows 内核 PortProxy 转发，Linux 端零后台常驻守护，无状态随起随用。
- **登录态复用**：直接控制 Windows 桌面真实 Chrome，复用已登录的各类网站 Cookie 与会话。
- **免本地浏览器二进制**：Linux 端仅需 Python 客户端（通过 `uv` 运行），无需执行 `playwright install`。

---

## 端点配置

| 参数 | 值 |
| :--- | :--- |
| **Windows 目标主机** | `100.100.1.118` (`tayhe-desktop.cat-hawksbill.ts.net`) |
| **CDP 调试端口** | `9222` |
| **CDP 基础 URL** | `http://100.100.1.118:9222` |

> **前置要求（Windows 端）**：
> 1. Chrome 以调试模式启动：`.\Start-ChromeDebug.ps1`
> 2. 端口转发与防火墙配置已生效：`.\Enable-RemoteChrome.ps1`

---

## Step 1: 连通性快速检查

在执行任何网页操作前，先验证 Windows Chrome CDP 接口是否可达：

```bash
# 方式 A：使用内置辅助脚本
uv run python /home/tayhe/Projects/mine/tayhe-skills/remote-chrome/scripts/chrome_remote.py check

# 方式 B：直接 curl 探测
curl -s --connect-timeout 2 http://100.100.1.118:9222/json/version | python3 -m json.tool
```

**连通失败排查**：
1. Tailscale 专网状态：`tailscale status | grep tayhe-desktop`（确认 Windows 设备在线）。
2. Windows 端 Chrome 是否启动：在 Windows 执行 `Start-ChromeDebug.ps1`。
3. Windows 端 9222 是否开放：在 Windows 执行 `Enable-RemoteChrome.ps1`。

---

## Step 2: 常见操作方式

### 方式 1：使用内置 CLI 辅助工具（推荐快速调用）

内置脚本路径：`/home/tayhe/Projects/mine/tayhe-skills/remote-chrome/scripts/chrome_remote.py`

```bash
# 1. 查看 Windows 端当前所有打开的标签页
uv run python /home/tayhe/Projects/mine/tayhe-skills/remote-chrome/scripts/chrome_remote.py tabs

# 2. 在 Windows 端打开新网页
uv run --with playwright python /home/tayhe/Projects/mine/tayhe-skills/remote-chrome/scripts/chrome_remote.py open "https://example.com"

# 3. 提取指定标签页（默认第 0 个）的纯文本内容
uv run --with playwright python /home/tayhe/Projects/mine/tayhe-skills/remote-chrome/scripts/chrome_remote.py text --tab 0

# 4. 网页截图（支持指定 URL 或已有标签页序号）
uv run --with playwright python /home/tayhe/Projects/mine/tayhe-skills/remote-chrome/scripts/chrome_remote.py screenshot ~/Documents/multimedia/page.png --url "https://example.com" --full-page

# 5. 执行一段 JavaScript 表达式
uv run --with playwright python /home/tayhe/Projects/mine/tayhe-skills/remote-chrome/scripts/chrome_remote.py eval "document.title" --tab 0
```

---

### 方式 2：编写 Python Playwright 脚本（适用于复杂自动化任务）

编写复杂的自动化、数据抓取、表单提交或交互流程时，可在任务临时目录创建 Python 脚本并用 `uv` 运行：

```bash
uv run --with playwright python my_automation.py
```

**标准脚本模板**：
```python
from playwright.sync_api import sync_playwright

CDP_ENDPOINT = "http://100.100.1.118:9222"

with sync_playwright() as p:
    # 1. 连接远端 CDP
    browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)

    # 2. 复用已有的浏览器上下文（共享已登录 Cookie）
    context = browser.contexts[0] if browser.contexts else browser.new_context()

    # 3. 复用现有页面或新建标签页
    page = context.new_page()
    try:
        page.goto("https://www.example.com", timeout=30000)
        page.wait_for_load_state("networkidle")

        print("Page Title:", page.title())

        # 执行交互或数据抓取
        # page.click("#submit-btn")
        # content = page.locator(".content").inner_text()

    finally:
        # 关闭当前测试标签页（避免残留孤儿标签页）
        page.close()
        # 断开 CDP 连接（关键：仅关闭连接，不会杀死 Windows 端的 Chrome 进程）
        browser.close()
```

---

### 方式 3：直接 HTTP / JSON API（超轻量操作）

```bash
# 获取所有标签页元数据
curl -s http://100.100.1.118:9222/json

# 在 Windows 新建标签页并导航至指定网址
curl -s -X PUT "http://100.100.1.118:9222/json/new?https://example.com"

# 切换/置顶指定标签页
curl -s "http://100.100.1.118:9222/json/activate/<PAGE_ID>"

# 关闭指定标签页
curl -s "http://100.100.1.118:9222/json/close/<PAGE_ID>"
```

---

## Agent 执行避坑守则

1. **禁止执行 `playwright install`**：
   Linux 控制端仅作为客户端驱动远端浏览器，不需要在本地下载几百兆的 Chromium 二进制。
2. **务必复用 `browser.contexts[0]`**：
   Windows 端的 Chrome 实例自带 `contexts[0]`，包含用户的浏览器登录态和 Cookie。新建 context 会导致隔离无 Cookie 状态。
3. **安全断开 `browser.close()`**：
   Playwright 连接远端 CDP 实例时，`browser.close()` 只断开当前的 WebSocket 连接，**不会退出 Windows 端正在运行的 Chrome 浏览器**。
4. **媒体文件存放位置**：
   若生成或保存网页截图等媒体文件，请遵从多媒体存放规则，保存到 `~/Documents/multimedia/` 目录下。
