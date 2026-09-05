---
name: tradingagents
description: >
  TradingAgents 多智能体金融投研与量化交易决策系统。
  触发条件：
  (1) 用户要求对美股、港股或加密货币进行投研分析（如 NVDA, AAPL, TSLA, 0700.HK, BTC-USD）
  (2) 用户询问某只股票的投资决策建议、买卖点、仓位规划或牛熊辩论研报
  (3) 用户要求生成技术面、基本面、情绪面、宏观新闻面的综合研报
  (4) 用户提及 "TradingAgents"、"多智能体研报"、"投委会决策" 等相关词汇
---

# TradingAgents 投研分析系统

基于大语言模型的多智能体金融分析与交易决策框架（TauricResearch / LangGraph）。后台通过并发调动 4 位专业分析师 Agent（技术面、基本面、散户情绪、宏观新闻），组织多轮牛熊攻防辩论，最终由交易员与风控模块输出结构化投资评级（**BUY / SELL / HOLD**）与详细报告。

## 调用方式

在终端或通过 Agent 工具执行 `scripts/analyze.py` 脚本：

```bash
# 基础用法：分析指定标的（默认分析最近一个交易日）
python3 <skill_dir>/scripts/analyze.py <TICKER>

# 指定历史日期进行回测分析 (YYYY-MM-DD)
python3 <skill_dir>/scripts/analyze.py <TICKER> 2025-03-15

# 加密货币分析
python3 <skill_dir>/scripts/analyze.py BTC-USD --asset-type crypto
```

> **注意**：`<skill_dir>` 为当前 Skill 所在的实际路径（例如 `~/.hermes/skills/tradingagents`、`~/Ai-Companion/Card/.pi/skills/tradingagents` 或 `~/Projects/mine/tayhe-skills/tradingagents`）。

## 参数说明

| 参数 | 说明 | 示例 |
|---|---|---|
| `ticker` (必填) | 资产标的代码 | 美股: `AAPL`, `NVDA`<br>港股: `0700.HK`<br>加密货币: `BTC-USD` |
| `date` (选填) | 分析基准日期 (YYYY-MM-DD)，不填默认最近交易日 | `2025-03-15` |
| `--asset-type` | 资产类型，可选 `stock` 或 `crypto`，默认 `stock` | `--asset-type crypto` |
| `--raw` | 输出原始 JSON 格式数据（默认输出格式化 Markdown） | `--raw` |
| `--base-url` | 指定后台服务地址（默认自动探测 `localhost` 或 Tailscale 节点） | `--base-url http://100.100.200.1:8000` |

## 耗时与交互预期

- **耗时**：后台多 Agent 数据采集与辩论通常需要 **2 ~ 4 分钟**。
- **调用时应先向用户告知**：正在提交后台投研团队并发分析（技术面/基本面/情绪/新闻）并进行多轮辩论，请稍候。
- **报告输出格式**：
  1. 🎯 **核心投资评级**（BUY / SELL / HOLD）
  2. 📝 **交易员投资策略与仓位规划**
  3. 📊 **四大维度研报精要**（技术面支撑压力位、财报关键指标、新闻事件、市场情绪）
  4. ⚠️ **核心风险警示**
