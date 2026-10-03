#!/usr/bin/env python3
"""
Remote Chrome CLI Helper for Agents
Connects to Windows Chrome (tayhe-desktop) from Linux (tayhe-cloud) via CDP over Tailscale.

Usage:
    uv run --with playwright python chrome_remote.py check
    uv run --with playwright python chrome_remote.py tabs
    uv run --with playwright python chrome_remote.py open <url>
    uv run --with playwright python chrome_remote.py screenshot <output_path> [--url <url>] [--tab <idx>] [--full-page]
    uv run --with playwright python chrome_remote.py eval "<js>" [--tab <idx>]
    uv run --with playwright python chrome_remote.py text [--tab <idx>]
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

DEFAULT_ENDPOINT = "http://100.100.1.118:9222"


def get_version(endpoint: str, timeout: float = 3.0) -> Optional[Dict[str, Any]]:
    url = f"{endpoint.rstrip('/')}/json/version"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RemoteChrome-Agent"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    return None


def get_tabs(endpoint: str, timeout: float = 3.0) -> List[Dict[str, Any]]:
    url = f"{endpoint.rstrip('/')}/json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RemoteChrome-Agent"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return [p for p in data if p.get("type") == "page"]
    except Exception:
        return []
    return []


def cmd_check(args):
    print(f"Checking Remote Chrome at {args.endpoint}...")
    version = get_version(args.endpoint)
    if not version:
        print(f"[FAIL] 无法连通 {args.endpoint}/json/version")
        print("\n排查步骤：")
        print("1. 检查 Tailscale 状态: `tailscale status | grep tayhe-desktop`")
        print("2. 确认 Windows 端已运行 Start-ChromeDebug.ps1 启动 Chrome")
        print("3. 确认 Windows 端已运行 Enable-RemoteChrome.ps1 开放 9222 端口转发")
        sys.exit(1)

    print("[OK] Remote Chrome 就绪：")
    print(f"     Browser : {version.get('Browser')}")
    print(f"     Protocol: {version.get('Protocol-Version')}")
    print(f"     UserAgent: {version.get('User-Agent')}")
    tabs = get_tabs(args.endpoint)
    print(f"     当前已打开标签页数: {len(tabs)}")


def cmd_tabs(args):
    tabs = get_tabs(args.endpoint)
    if not tabs:
        print(f"[WARN] 未获取到标签页或无法连通 {args.endpoint}")
        sys.exit(1)

    print(f"共发现 {len(tabs)} 个网页标签：")
    for i, t in enumerate(tabs):
        print(f"[{i}] {t.get('title', 'Untitled')} -> {t.get('url', '')}")


def cmd_open(args):
    from playwright.sync_api import sync_playwright

    print(f"正在通过 Remote Chrome 打开 URL: {args.url}")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(args.endpoint)
        except Exception as e:
            print(f"[FAIL] 无法连接到 CDP 端点: {e}")
            sys.exit(1)

        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            page.goto(args.url, timeout=30000)
            page.wait_for_load_state("domcontentloaded")
            print(f"[OK] 成功打开页面：")
            print(f"     标题: {page.title()}")
            print(f"     URL : {page.url}")
        finally:
            browser.close()


def cmd_screenshot(args):
    from playwright.sync_api import sync_playwright

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(args.endpoint)
        except Exception as e:
            print(f"[FAIL] 无法连接到 CDP 端点: {e}")
            sys.exit(1)

        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            if args.url:
                page = context.new_page()
                page.goto(args.url, timeout=30000)
                page.wait_for_load_state("domcontentloaded")
            else:
                pages = context.pages
                if not pages:
                    print("[FAIL] Windows 端当前无打开的标签页，请使用 --url 指定目标网页")
                    sys.exit(1)
                idx = args.tab if args.tab is not None and args.tab < len(pages) else 0
                page = pages[idx]

            page.screenshot(path=output_path, full_page=args.full_page)
            print(f"[OK] 截图已保存至: {output_path}")
            print(f"     页面标题: {page.title()}")
            print(f"     页面 URL : {page.url}")
        finally:
            browser.close()


def cmd_eval(args):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(args.endpoint)
        except Exception as e:
            print(f"[FAIL] 无法连接到 CDP 端点: {e}")
            sys.exit(1)

        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            pages = context.pages
            if not pages:
                print("[FAIL] Windows 端当前无打开的标签页")
                sys.exit(1)
            idx = args.tab if args.tab is not None and args.tab < len(pages) else 0
            page = pages[idx]

            result = page.evaluate(args.expr)
            if isinstance(result, (dict, list)):
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result)
        finally:
            browser.close()


def cmd_text(args):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(args.endpoint)
        except Exception as e:
            print(f"[FAIL] 无法连接到 CDP 端点: {e}")
            sys.exit(1)

        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            pages = context.pages
            if not pages:
                print("[FAIL] Windows 端当前无打开的标签页")
                sys.exit(1)
            idx = args.tab if args.tab is not None and args.tab < len(pages) else 0
            page = pages[idx]

            title = page.title()
            url = page.url
            body_text = page.evaluate("() => document.body.innerText")
            print(f"=== [{idx}] {title} ({url}) ===")
            print(body_text.strip())
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="Remote Chrome CLI Helper for Agents")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help=f"CDP HTTP endpoint (default: {DEFAULT_ENDPOINT})")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    p_check = subparsers.add_parser("check", help="Check remote Chrome CDP connectivity")
    p_check.set_defaults(func=cmd_check)

    # tabs
    p_tabs = subparsers.add_parser("tabs", help="List all open tabs")
    p_tabs.set_defaults(func=cmd_tabs)

    # open
    p_open = subparsers.add_parser("open", help="Open a new URL")
    p_open.add_argument("url", help="URL to navigate to")
    p_open.set_defaults(func=cmd_open)

    # screenshot
    p_ss = subparsers.add_parser("screenshot", help="Take a screenshot of a tab or URL")
    p_ss.add_argument("output", help="Output file path (e.g. /tmp/page.png)")
    p_ss.add_argument("--url", help="URL to load before screenshot", default=None)
    p_ss.add_argument("--tab", type=int, help="Tab index (0-based) to capture", default=0)
    p_ss.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    p_ss.set_defaults(func=cmd_screenshot)

    # eval
    p_eval = subparsers.add_parser("eval", help="Evaluate JS expression in a tab")
    p_eval.add_argument("expr", help="JavaScript expression to evaluate")
    p_eval.add_argument("--tab", type=int, help="Tab index (0-based)", default=0)
    p_eval.set_defaults(func=cmd_eval)

    # text
    p_text = subparsers.add_parser("text", help="Extract text content from a tab")
    p_text.add_argument("--tab", type=int, help="Tab index (0-based)", default=0)
    p_text.set_defaults(func=cmd_text)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
