# Chrome DevTools MCP 集成指南

若希望将远程 Windows Chrome 的全套 Chrome DevTools 协议能力作为 **MCP（Model Context Protocol）工具集** 直接注入给 AI Agent，可通过 `chrome-devtools-mcp` 将其包装为标准 MCP Server。

---

## 1. MCP 客户端配置

在 Agent 的 MCP 配置文件（例如 `mcp_config.json` 或各 Client 设置）中添加如下配置，连接到已有的 Windows 远程实例：

```json
{
  "mcpServers": {
    "remote-chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--browserUrl=http://100.100.1.118:9222",
        "--no-usage-statistics"
      ]
    }
  }
}
```

**关键启动参数说明**：
- `--browserUrl=http://100.100.1.118:9222`：直连 Windows 端的 PortProxy CDP 接口，复用当前正在运行的桌面浏览器与登录态。
- `--slim`（可选）：精简模式，仅暴露导航、脚本执行与截图 3 个基础工具，避免占用过多 Tool Context。

---

## 2. 适合由 MCP 驱动的高级能力

普通网页浏览、抓取与截图优先使用本 Skill 内置的 Playwright / CLI 工具；当需要以下**深度诊断能力**时，推荐使用该 MCP Server：

1. **性能追踪（Performance Profiling）**：
   - 工具：`performance_start_trace` / `performance_stop_trace`
   - 提取 Web 性能指标（LCP、INP、CLS）与性能瓶颈诊断分析。
2. **底层网络监控（Network Inspection）**：
   - 工具：`list_network_requests` / `get_request_details`
   - 抓取页面在渲染过程中发出的所有 XHR/Fetch 请求、响应头与状态码。
3. **设备与环境模拟（Emulation）**：
   - 模拟不同机型分辨率（如 `--viewport="390x844x3,mobile,touch"`）。
   - 模拟弱网环境（`--networkConditions="Slow 4G"`）或地理位置模拟。
