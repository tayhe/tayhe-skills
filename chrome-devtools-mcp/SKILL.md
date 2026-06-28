---
name: chrome-devtools-mcp
description: "Chrome DevTools MCP server for advanced browser debugging, performance analysis, and automation. Use when needing performance traces, network debugging, console inspection, Lighthouse audits, or full Chrome DevTools capabilities via MCP protocol."
---

# Chrome DevTools MCP

Chrome DevTools MCP (`chrome-devtools-mcp`) is an MCP server that provides full Chrome DevTools capabilities for coding agents. It offers advanced debugging, performance analysis, and browser automation.

## Installation

```bash
# Via npx (recommended)
npx -y chrome-devtools-mcp@latest

# Or install globally
npm install -g chrome-devtools-mcp
```

## Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### Common options

```bash
# Headless mode (no UI)
npx chrome-devtools-mcp@latest --headless

# Slim mode (3 tools only: navigation, script execution, screenshots)
npx chrome-devtools-mcp@latest --slim

# Connect to existing Chrome instance
npx chrome-devtools-mcp@latest --browserUrl=http://127.0.0.1:9222

# Use specific Chrome channel
npx chrome-devtools-mcp@latest --channel=stable

# Custom Chrome executable
npx chrome-devtools-mcp@latest --executablePath=/path/to/chrome

# Disable usage statistics
npx chrome-devtools-mcp@latest --no-usage-statistics

# Disable CrUX (field data) integration
npx chrome-devtools-mcp@latest --no-performance-crux
```

## CLI Usage

Chrome DevTools MCP provides a CLI for direct usage:

### Daemon management

```bash
# Start daemon
chrome-devtools start --headless

# Check status
chrome-devtools status

# Stop daemon
chrome-devtools stop
```

### Navigation and inspection

```bash
# List pages
chrome-devtools list_pages

# Navigate
chrome-devtools navigate_page --type=url --url="https://example.com"

# Screenshot
chrome-devtools take_screenshot

# Page snapshot (accessibility tree)
chrome-devtools take_snapshot
```

### Debugging

```bash
# Performance trace
chrome-devtools performance_start_trace

# Console messages
chrome-devtools list_console_messages

# Execute script
chrome-devtools evaluate_script "() => document.title"

# Network requests
chrome-devtools list_network_requests
```

### Element interactions

```bash
# Click element (use UID from take_snapshot)
chrome-devtools click <uid>

# Fill input
chrome-devtools fill <uid> <value>

# Hover
chrome-devtools hover <uid>

# Type text
chrome-devtools type_text "text"

# Press key
chrome-devtools press_key "Enter"
```

### Emulation

```bash
# Mobile device viewport
chrome-devtools emulate --viewport="390x844x3,mobile,touch"

# Custom user agent
chrome-devtools emulate --userAgent="Custom UA"

# CPU throttling
chrome-devtools emulate --cpuThrottlingRate=2

# Network throttling
chrome-devtools emulate --networkConditions="Slow 4G"

# Geolocation
chrome-devtools emulate --geolocation="37.7749,-122.4194"
```

## Key Features

- **Performance analysis**: Record traces, get Core Web Vitals (LCP, INP, CLS), analyze insights
- **Network debugging**: List requests, get request details, filter by resource type
- **Console inspection**: List messages, get message details with source-mapped stack traces
- **Element interaction**: Click, fill, hover, type, drag based on accessibility tree
- **Emulation**: Device viewport, user agent, geolocation, network throttling, CPU throttling
- **Memory debugging**: Heap snapshots (requires `--memoryDebugging=true`)
- **Lighthouse audits**: Accessibility, SEO, best practices

## Workflow Pattern

1. Start daemon: `chrome-devtools start --headless`
2. Navigate: `chrome-devtools navigate_page --type=url --url="https://example.com"`
3. Snapshot: `chrome-devtools take_snapshot` (get element UIDs)
4. Interact: `chrome-devtools click <uid>`
5. Verify: `chrome-devtools take_snapshot` or `take_screenshot`
6. Stop: `chrome-devtools stop`

## Performance Analysis

### Record and analyze traces

```bash
# Start performance trace
chrome-devtools performance_start_trace

# Navigate to page (trace will record automatically)
chrome-devtools navigate_page --type=url --url="https://example.com"

# Get detailed insights
chrome-devtools performance_analyze_insight --insightSetId="NAVIGATION_0" --insightName="LCPBreakdown"
```

### Lighthouse audits

```bash
# Run Lighthouse audit
chrome-devtools lighthouse_audit --mode=navigation --device=desktop
```

## Troubleshooting

- **Chrome not found**: Use `--executablePath` to specify Chrome binary path
- **Protocol errors**: Ensure Chrome is running and accessible
- **Headless issues**: Add `--chromeArg='--no-sandbox'` for sandboxed environments
- **Slow startup**: Increase timeout with `--timeout=30000`
- **Target closed**: Chrome may have crashed; restart daemon

## Related

- [Chrome DevTools MCP GitHub](https://github.com/ChromeDevTools/chrome-devtools-mcp) — Official repository
- [Tool Reference](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md) — Complete tool documentation
