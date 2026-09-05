#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents CLI & Agent Skill Client
调用后台 TradingAgents 多智能体系统对指定标的进行投研分析并输出决策报告。
仅使用 Python 标准库，零第三方依赖。
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def get_api_key() -> str | None:
    key = os.environ.get("TRADINGAGENTS_API_KEY")
    if key:
        return key

    # 尝试从本地 server-config 目录读取
    candidates = [
        Path.home() / "Documents/server-config/docker/tradingagents/.env",
        Path.home() / "server-config/docker/tradingagents/.env",
    ]
    for env_path in candidates:
        if env_path.exists():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("TRADINGAGENTS_API_KEY="):
                        val = line.split("=", 1)[1].strip()
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        return val
            except Exception:
                pass
    return None


def probe_base_url() -> str:
    override_url = os.environ.get("TRADINGAGENTS_URL")
    if override_url:
        return override_url.rstrip("/")

    candidates = [
        "http://127.0.0.1:8000",
        "http://100.100.200.1:8000",
        "http://tayhe-cloud.cat-hawksbill.ts.net:8000",
    ]
    for url in candidates:
        try:
            req = urllib.request.Request(f"{url}/health")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    return url
        except Exception:
            continue
    return "http://127.0.0.1:8000"


def submit_job(base_url: str, api_key: str | None, ticker: str, date: str, asset_type: str) -> str:
    url = f"{base_url}/analyze"
    payload = json.dumps({"ticker": ticker, "date": date, "asset_type": asset_type}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["job_id"]
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} ({e.reason}): {err_msg}") from e
    except Exception as e:
        raise RuntimeError(f"提交分析任务失败: {e}") from e


def poll_job(base_url: str, api_key: str | None, job_id: str, timeout_sec: int = 600, poll_sec: int = 6) -> dict:
    url = f"{base_url}/jobs/{job_id}"
    req = urllib.request.Request(url)
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")

    start_time = time.time()
    sys.stderr.write(f"[*] 任务已提交 (ID: {job_id})，后台多 Agent 辩论中，预计耗时 2~4 分钟...\n")
    sys.stderr.flush()

    last_dot = start_time
    while time.time() - start_time < timeout_sec:
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                status = result.get("status")
                if status == "done":
                    sys.stderr.write("\n[✓] 投研辩论完成！\n")
                    sys.stderr.flush()
                    return result
                elif status == "failed":
                    sys.stderr.write("\n[✗] 任务执行失败！\n")
                    sys.stderr.flush()
                    raise RuntimeError(f"TradingAgents 内部错误: {result.get('error')}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                pass
            else:
                sys.stderr.write(f"\n[!] 轮询警告: HTTP {e.code}\n")
        except Exception:
            pass

        time.sleep(poll_sec)
        sys.stderr.write(".")
        sys.stderr.flush()

    raise TimeoutError(f"任务在 {timeout_sec} 秒内未完成")


def format_markdown(data: dict, ticker: str, date: str) -> str:
    decision = data.get("decision", "UNKNOWN")
    state = data.get("state") or {}

    out = []
    out.append(f"# TradingAgents 投研分析报告: {ticker}")
    out.append(f"\n- **分析标的**：`{ticker}`")
    out.append(f"- **基准日期**：`{date}`")
    out.append(f"- **投委会最终决策**：**【 {decision} 】**\n")
    out.append("---\n")

    # 交易员最终投资计划
    trader_plan = state.get("trader_investment_plan") or state.get("final_trade_decision") or ""
    if trader_plan:
        out.append("## 1. 交易员投资策略与决策摘要\n")
        out.append(trader_plan.strip())
        out.append("\n---\n")

    # 各分项研报
    reports = [
        ("技术面与市场研报 (Market Analyst)", state.get("market_report")),
        ("基本面财务研报 (Fundamentals Analyst)", state.get("fundamentals_report")),
        ("新闻面宏观研报 (News Analyst)", state.get("news_report")),
        ("市场情绪研报 (Sentiment Analyst)", state.get("sentiment_report")),
    ]

    for title, content in reports:
        if content and content.strip():
            out.append(f"## {title}\n")
            out.append(content.strip())
            out.append("\n---\n")

    out.append("> *免责声明：本报告由 TradingAgents 多智能体系统通过模拟投研辩论生成，仅供技术研究参考，不构成任何投资建议。*")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="TradingAgents Multi-Agent Financial Research CLI")
    parser.add_argument("ticker", help="资产代码 (例如: AAPL, NVDA, 0700.HK, BTC-USD)")
    parser.add_argument("date", nargs="?", default="", help="分析日期 YYYY-MM-DD (默认最近可用交易日)")
    parser.add_argument("--asset-type", choices=["stock", "crypto"], default="stock", help="资产类别 (默认: stock)")
    parser.add_argument("--raw", action="store_true", help="直接输出原始 JSON 结果")
    parser.add_argument("--base-url", default="", help="指定后台服务地址 (默认自动探测)")
    parser.add_argument("--timeout", type=int, default=600, help="最长超时等待秒数 (默认 600s)")

    args = parser.parse_args()
    ticker = args.ticker.upper().strip()

    # 日期计算
    target_date = args.date.strip()
    if not target_date:
        # 如果是周日(6)或周六(5)，回退到周五
        now = datetime.datetime.now()
        if now.weekday() == 6:  # Sunday
            now -= datetime.timedelta(days=2)
        elif now.weekday() == 5:  # Saturday
            now -= datetime.timedelta(days=1)
        target_date = now.strftime("%Y-%m-%d")

    base_url = args.base_url.rstrip("/") if args.base_url else probe_base_url()
    api_key = get_api_key()

    if not api_key:
        sys.stderr.write("[!] 警告: 未找到 TRADINGAGENTS_API_KEY，尝试无鉴权调用...\n")

    sys.stderr.write(f"[*] 标的: {ticker} | 日期: {target_date} | 端点: {base_url}\n")
    job_id = submit_job(base_url, api_key, ticker, target_date, args.asset_type)
    result = poll_job(base_url, api_key, job_id, timeout_sec=args.timeout)

    if args.raw:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(result, ticker, target_date))


if __name__ == "__main__":
    main()
