# OpenClaw 配合 Remote Chrome 使用指南

若在工作流中需要使用 [OpenClaw](https://github.com/openclaw) CLI 进行基于 AI 视觉/可访问性树的交互式浏览器自动化，可通过以下配置将其接入本方案的 Windows 远程 Chrome 实例。

---

## 1. 配置 OpenClaw Remote Profile

编辑 `~/.openclaw/openclaw.json`（或在启动命令中指定），添加指向 Windows Tailscale 端点的 Profile：

```json
{
  "browser": {
    "profiles": {
      "remote-windows": {
        "cdpUrl": "http://100.100.1.118:9222",
        "color": "#00AA00"
      }
    }
  }
}
```

> **提示**：使用 `http://` 前缀时，OpenClaw 会自动调用 `/json/version` 解析出实际可用的 WebSocket 调试地址并建立连接。

---

## 2. 核心操作模式：Snapshot → Act 循环

OpenClaw 依靠在操作前获取页面快照生成稳定的 Ref（元素引用编号）：

```text
snapshot → act → snapshot again (页面跳转或状态变更后) → repeat
```

```bash
# 启动连接远端 Profile
openclaw browser --browser-profile remote-windows start

# 检查标签页
openclaw browser --browser-profile remote-windows tabs

# 获取交互式快照（生成 role refs，如 e12、e23）
openclaw browser --browser-profile remote-windows snapshot --interactive

# 点击元素并输入文本
openclaw browser --browser-profile remote-windows click e12
openclaw browser --browser-profile remote-windows type e15 "搜索关键词" --submit

# 显式等待网络空闲
openclaw browser --browser-profile remote-windows wait --url "**/dashboard" --load networkidle

# 截图保存
openclaw browser --browser-profile remote-windows screenshot ~/Documents/multimedia/openclaw_snapshot.png --full-page
```

---

## 3. 常见避坑与恢复规则

1. **Ref 仅在当前快照生命周期内有效**：
   页面发生模态框弹出、表单提交或 URL 跳转后，旧的 Ref 立即作废，必须重新 `snapshot` 后再操作。
2. **避免盲等 sleep**：
   使用条件等待 `--load networkidle` 或指定元素选择器 `--selector "#main-content"`。
3. **遇到阻断（验证码 / 2FA 登录）**：
   因为浏览器运行在 Windows 实体机桌面上，遇到人机验证或 2FA 时，可提示用户直接在 Windows 物理屏幕上人工通过，随后 Agent 继续在 Linux 侧执行。
