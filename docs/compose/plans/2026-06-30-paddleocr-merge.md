# PaddleOCR Skills 合并实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 3 个 PaddleOCR skill 合并为统一的 `paddleocr-parser`

**Architecture:** 单一 CLI 入口 + 独立的 sync/async 库模块，通过 `--mode` 参数选择运行模式，保留所有原有功能（断点续传、PDF 分割、图片优化、每页输出）

**Tech Stack:** Python 3.9+, httpx (PEP 723 inline metadata), uv

## Global Constraints

- 所有脚本使用 PEP 723 inline metadata 声明依赖，零安装摩擦
- HTTP 库统一使用 httpx（不保留 requests/curl 版本）
- 输出 envelope 统一为 `{ok, text, result, error}` 格式
- Windows 编码修复（stdout/stderr UTF-8 TextIOWrapper）
- 环境变量向后兼容旧名称映射

---

### Task 1: 创建目录结构和 SKILL.md

**Covers:** S2, S3

**Files:**
- Create: `paddleocr-parser/SKILL.md`
- Create: `paddleocr-parser/_meta.json`
- Create: `paddleocr-parser/references/output_schema.md`

**Interfaces:**
- Produces: skill 元数据和文档

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p paddleocr-parser/references
mkdir -p paddleocr-parser/scripts
```

- [ ] **Step 2: 创建 _meta.json**

```json
{
  "owner": "tayhe",
  "slug": "paddleocr-parser",
  "version": "1.0.0"
}
```

- [ ] **Step 3: 创建 SKILL.md**

内容包括：
- YAML frontmatter（name, description, trigger terms, env vars, bins）
- When to Use（同步 vs 异步场景）
- Installation（PEP 723 + uv）
- Usage（所有 CLI 参数说明）
- Configuration（环境变量）
- Output format（JSON envelope + 每页文件）
- Error handling

- [ ] **Step 4: 创建 output_schema.md**

从 paddleocr-doc-parsing/references/output_schema.md 复制并更新

- [ ] **Step 5: 提交**

```bash
git add paddleocr-parser/
git commit -m "feat(paddleocr-parser): create unified skill structure and docs"
```

---

### Task 2: 创建 lib_sync.py — 同步 API 库

**Covers:** S3, S4

**Files:**
- Create: `paddleocr-parser/scripts/lib_sync.py`

**Interfaces:**
- Produces: `parse_document(file_path?, file_url?, file_type?, **options) -> dict`
- Produces: `get_config() -> tuple[str, str]`
- Produces: error classes: `ConfigError`, `APIError`, `InputError`

- [ ] **Step 1: 创建 lib_sync.py**

从 `paddleocr-doc-parsing/scripts/lib.py` 复制并修改：
1. 统一环境变量名：`PADDLEOCR_SYNC_API_URL`（兼容 `PADDLEOCR_DOC_PARSING_API_URL` 和 `PADDLEOCR_API_URL`）
2. Token 统一为 `PADDLEOCR_ACCESS_TOKEN`
3. 添加环境变量向后兼容映射逻辑
4. 保留所有核心功能：`parse_document()`、`get_config()`、`_detect_file_type()`、`_load_file_as_base64()`、`_make_api_request()`、`_extract_text()`

关键代码结构：
```python
# 环境变量兼容映射
def _get_env_compat(key: str, *fallbacks: str) -> str:
    for k in [key, *fallbacks]:
        val = os.getenv(k, "").strip()
        if val:
            return val
    return ""

def get_config() -> tuple[str, str]:
    api_url = _get_env_compat("PADDLEOCR_SYNC_API_URL", "PADDLEOCR_DOC_PARSING_API_URL", "PADDLEOCR_API_URL")
    token = _get_env_compat("PADDLEOCR_ACCESS_TOKEN", "PADDLEOCR_ASYNC_TOKEN")
    # ... 验证逻辑
```

- [ ] **Step 2: 验证导入**

```bash
uv run python -c "from lib_sync import parse_document, get_config; print('OK')"
```
Expected: OK

- [ ] **Step 3: 提交**

```bash
git add paddleocr-parser/scripts/lib_sync.py
git commit -m "feat(paddleocr-parser): add sync API library"
```

---

### Task 3: 创建 lib_async.py — 异步 API 库

**Covers:** S3, S4

**Files:**
- Create: `paddleocr-parser/scripts/lib_async.py`

**Interfaces:**
- Produces: `submit_job(file_path?, file_url?, model, optional_payload, token?) -> JobResult`
- Produces: `poll_job(job_id, token?, interval, verbose) -> dict`
- Produces: `download_jsonl(jsonl_url, token?) -> list[dict]`
- Produces: `JobResult` dataclass
- Produces: error classes: `ConfigError`, `JobFailedError`, `APIError`, `InputError`

- [ ] **Step 1: 创建 lib_async.py**

从 `paddleocr-async/scripts/lib_async.py` 复制并修改：
1. 统一环境变量名：`PADDLEOCR_ASYNC_API_URL`（默认值 `https://paddleocr.aistudio-app.com/api/v2/ocr/jobs`）
2. Token 统一为 `PADDLEOCR_ACCESS_TOKEN`（兼容 `PADDLEOCR_ASYNC_TOKEN`）
3. 添加环境变量向后兼容映射逻辑

关键代码结构：
```python
def _get_env_compat(key: str, *fallbacks: str) -> str:
    for k in [key, *fallbacks]:
        val = os.getenv(k, "").strip()
        if val:
            return val
    return ""

def get_config(api_url_var: str, token_var: str) -> tuple[str, str]:
    api_url = _get_env_compat(api_url_var)
    token = _get_env_compat(token_var, "PADDLEOCR_ACCESS_TOKEN", "PADDLEOCR_ASYNC_TOKEN")
    # ...
```

- [ ] **Step 2: 验证导入**

```bash
uv run python -c "from lib_async import submit_job, poll_job, download_jsonl; print('OK')"
```
Expected: OK

- [ ] **Step 3: 提交**

```bash
git add paddleocr-parser/scripts/lib_async.py
git commit -m "feat(paddleocr-parser): add async API library"
```

---

### Task 4: 创建统一 CLI 入口 paddleocr_parse.py

**Covers:** S3, S4, S5

**Files:**
- Create: `paddleocr-parser/scripts/paddleocr_parse.py`

**Interfaces:**
- Consumes: `lib_sync.parse_document()`, `lib_async.submit_job()`, `lib_async.poll_job()`, `lib_async.download_jsonl()`
- Produces: CLI with `--mode`, `--file-url`, `--file-path`, `--stdout`, `--output`, `--output-per-page`, `--skip-existing`, `--model`, `--no-deskew`, `--no-orientation`, `--charts`, `--optimize`, `--split-pages`

- [ ] **Step 1: 创建 paddleocr_parse.py**

核心结构：

```python
#!/usr/bin/env python3
"""PaddleOCR Unified Document Parser"""

# /// script
# requires-python = ">=3.9"
# dependencies = ["httpx>=0.24.0"]
# ///

import argparse, base64, json, os, sys, io
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))

from lib_sync import parse_document, ConfigError as SyncConfigError, APIError as SyncAPIError
from lib_async import submit_job, poll_job, download_jsonl, JobResult, ConfigError, JobFailedError, APIError, InputError


def auto_detect_mode(file_path: str | None, file_url: str | None) -> str:
    """根据文件类型自动选择 sync/async"""
    target = file_path or file_url or ""
    if target.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp")):
        return "sync"
    return "async"  # PDF 和未知格式默认用 async（无页数限制）


def write_page(output_dir: Path, page_index: int, page_data: dict) -> tuple[str, list[str]]:
    """写入单页 Markdown + 提取图片（复用自 paddleocr-async）"""
    # ... 复用 ocr_job.py 的 write_page 逻辑


def run_sync(args) -> dict:
    """执行同步解析"""
    result = parse_document(
        file_path=args.file_path,
        file_url=args.file_url,
        useDocUnwarping=not args.no_deskew,
        useDocOrientationClassify=not args.no_orientation,
        useChartRecognition=args.charts,
    )
    return result


def run_async(args) -> dict:
    """执行异步解析"""
    optional_payload = {
        "useDocUnwarping": not args.no_deskew,
        "useDocOrientationClassify": not args.no_orientation,
        "useChartRecognition": args.charts,
    }
    
    job_result = submit_job(
        file_path=args.file_path,
        file_url=args.file_url,
        model=args.model,
        optional_payload=optional_payload,
        token=args.token or "",
    )
    
    final_data = poll_job(job_result.job_id, token=args.token or "", verbose=args.pretty)
    jsonl_url = final_data.get("resultUrl", {}).get("jsonUrl", "")
    
    if not jsonl_url:
        return {"ok": False, "text": "", "result": None, "error": {"code": "API_ERROR", "message": "No result URL"}}
    
    raw_lines = download_jsonl(jsonl_url, token=args.token or "")
    
    # 组装结果
    all_texts = []
    all_results = []
    for line in raw_lines:
        result_obj = line.get("result", {})
        layout_results = result_obj.get("layoutParsingResults", [])
        for page in layout_results:
            all_texts.append(page.get("markdown", {}).get("text", ""))
            all_results.append(page)
        
        # 写入每页文件
        if args.output_per_page:
            output_dir = Path(args.output_per_page)
            for i, page in enumerate(layout_results):
                if args.skip_existing and (output_dir / f"doc_{i}.md").exists():
                    continue
                write_page(output_dir, i, page)
    
    return {
        "ok": True,
        "text": "\n\n".join(all_texts),
        "result": {"mode": "async", "pages": len(all_results), "layoutParsingResults": all_results},
        "error": None,
    }


def main():
    parser = argparse.ArgumentParser(description="PaddleOCR Unified Document Parser")
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file-url", help="Remote URL to the document")
    input_group.add_argument("--file-path", help="Local file to upload")
    
    parser.add_argument("--mode", choices=["auto", "sync", "async"], default="auto")
    parser.add_argument("--model", default="PaddleOCR-VL-1.5")
    parser.add_argument("--token", help="One-shot token override")
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--output", "-o", help="Save result to JSON file")
    parser.add_argument("--output-per-page", help="Write one Markdown per page to DIR")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-deskew", action="store_true")
    parser.add_argument("--no-orientation", action="store_true")
    parser.add_argument("--charts", action="store_true")
    parser.add_argument("--optimize", action="store_true", help="Auto-compress large images")
    parser.add_argument("--split-pages", help="PDF page ranges (e.g. '1-5,8')")
    
    args = parser.parse_args()
    
    # 图片优化
    if args.optimize and args.file_path:
        # 调用 optimize_file.py 逻辑
        pass
    
    # PDF 分割
    if args.split_pages and args.file_path:
        # 调用 split_pdf.py 逻辑
        pass
    
    # 选择模式
    mode = args.mode
    if mode == "auto":
        mode = auto_detect_mode(args.file_path, args.file_url)
    
    # 执行
    if mode == "sync":
        result = run_sync(args)
    else:
        result = run_async(args)
    
    # 输出
    indent = 2 if args.pretty else None
    json_output = json.dumps(result, indent=indent, ensure_ascii=False)
    
    if args.stdout:
        print(json_output)
    elif args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json_output, encoding="utf-8")
        print(f"Result saved to: {args.output}", file=sys.stderr)
    else:
        print(json_output)
    
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 验证帮助信息**

```bash
uv run paddleocr-parser/scripts/paddleocr_parse.py --help
```
Expected: 显示所有参数说明

- [ ] **Step 3: 提交**

```bash
git add paddleocr-parser/scripts/paddleocr_parse.py
git commit -m "feat(paddleocr-parser): add unified CLI entry point"
```

---

### Task 5: 添加工具脚本（split_pdf.py, optimize_file.py）

**Covers:** S3

**Files:**
- Create: `paddleocr-parser/scripts/split_pdf.py`
- Create: `paddleocr-parser/scripts/optimize_file.py`

**Interfaces:**
- Produces: `split_pdf.py` CLI — `uv run scripts/split_pdf.py input.pdf output.pdf --pages "1-5"`
- Produces: `optimize_file.py` CLI — `uv run scripts/optimize_file.py input.png output.jpg --quality 85`

- [ ] **Step 1: 复制 split_pdf.py**

从 `paddleocr-doc-parsing/scripts/split_pdf.py` 复制到 `paddleocr-parser/scripts/split_pdf.py`，无需修改（独立工具，不依赖环境变量）

- [ ] **Step 2: 复制 optimize_file.py**

从 `paddleocr-doc-parsing/scripts/optimize_file.py` 复制到 `paddleocr-parser/scripts/optimize_file.py`，无需修改

- [ ] **Step 3: 验证工具可用**

```bash
uv run paddleocr-parser/scripts/split_pdf.py --help
uv run paddleocr-parser/scripts/optimize_file.py --help
```
Expected: 两个命令都显示帮助信息

- [ ] **Step 4: 提交**

```bash
git add paddleocr-parser/scripts/split_pdf.py paddleocr-parser/scripts/optimize_file.py
git commit -m "feat(paddleocr-parser): add split_pdf and optimize_file utilities"
```

---

### Task 6: 创建 smoke_test.py

**Covers:** S7

**Files:**
- Create: `paddleocr-parser/scripts/smoke_test.py`

**Interfaces:**
- Produces: CLI — `uv run scripts/smoke_test.py [--skip-api]`

- [ ] **Step 1: 创建 smoke_test.py**

合并两个版本的 smoke test 逻辑：

```python
#!/usr/bin/env python3
"""PaddleOCR Parser — Smoke Test"""

# /// script
# requires-python = ">=3.9"
# dependencies = ["httpx>=0.24.0"]
# ///

import os
import sys

def check_config():
    """检查环境变量配置"""
    token = os.getenv("PADDLEOCR_ACCESS_TOKEN", "").strip()
    sync_url = os.getenv("PADDLEOCR_SYNC_API_URL", "").strip()
    async_url = os.getenv("PADDLEOCR_ASYNC_API_URL", "").strip()
    
    if not token:
        # 检查兼容变量
        token = os.getenv("PADDLEOCR_ASYNC_TOKEN", "").strip() or os.getenv("PADDLEOCR_DOC_PARSING_TOKEN", "").strip()
    
    print(f"Token: {'OK (' + token[:8] + '...)' if token else 'MISSING'}")
    print(f"Sync URL: {sync_url or '(default)'}")
    print(f"Async URL: {async_url or '(default)'}")
    
    return bool(token)

def check_api():
    """测试 API 连通性"""
    # 提交一个最小测试任务
    pass

def main():
    skip_api = "--skip-api" in sys.argv
    
    print("=== PaddleOCR Parser Smoke Test ===\n")
    
    print("1. Configuration Check:")
    config_ok = check_config()
    
    if not skip_api and config_ok:
        print("\n2. API Connectivity Check:")
        check_api()
    elif skip_api:
        print("\n2. API Check: SKIPPED (--skip-api)")
    
    print("\n=== Done ===")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 提交**

```bash
git add paddleocr-parser/scripts/smoke_test.py
git commit -m "feat(paddleocr-parser): add smoke test"
```

---

### Task 7: 清理旧目录并最终验证

**Covers:** S7

**Files:**
- Delete: `paddleocr-async/`
- Delete: `paddleocr-doc-parsing/`
- Delete: `paddleocr-doc-parsing-v2/`

**注意：此任务需要用户确认**

- [ ] **Step 1: 验证新 skill 完整性**

```bash
# 检查文件结构
tree paddleocr-parser/

# 验证所有脚本可运行
uv run paddleocr-parser/scripts/paddleocr_parse.py --help
uv run paddleocr-parser/scripts/split_pdf.py --help
uv run paddleocr-parser/scripts/optimize_file.py --help
uv run paddleocr-parser/scripts/smoke_test.py --skip-api
```

- [ ] **Step 2: 删除旧目录（需用户确认）**

```bash
# 使用 trash-put 而非 rm
trash-put paddleocr-async paddleocr-doc-parsing paddleocr-doc-parsing-v2
```

- [ ] **Step 3: 最终提交**

```bash
git add -A
git commit -m "feat(paddleocr-parser): merge 3 paddleocr skills into unified paddleocr-parser"
```

---

## 依赖关系图

```
Task 1 (结构)
    ↓
Task 2 (lib_sync) ← Task 3 (lib_async)
    ↓                   ↓
    └─── Task 4 (CLI) ──┘
             ↓
Task 5 (工具脚本) ← Task 4
             ↓
Task 6 (smoke test)
             ↓
Task 7 (清理)
```
