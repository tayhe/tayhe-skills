---
name: paddleocr-async
description: >-
  Use this skill to parse large PDF documents (100+ pages) or books via the PaddleOCR
  async jobs API. Handles long documents with no page limits — submits a job, polls
  until completion, downloads JSONL, and writes Markdown per page with inline images.
  Trigger terms:  大文档,  整本书,  超长PDF,  异步解析,  书籍OCR,  批量解析,
  多页文档,  100页以上文档,  3000页配额,  长文档解析,  整本PDF,
  aistudio,  AIStudio,  async jobs,  large PDF,  book parsing,
  batch OCR,  100+ pages,  long document.
license: Apache-2.0
compatibility: Requires Python 3.9+, uv, and internet access.
metadata:
  openclaw:
    requires:
      env:
        - PADDLEOCR_ASYNC_API_URL
        - PADDLEOCR_ASYNC_TOKEN
      bins:
        - uv
    primaryEnv: PADDLEOCR_ASYNC_TOKEN
    emoji: "📚"
    homepage: https://github.com/PaddlePaddle/PaddleOCR
---

# PaddleOCR Async — Document Parsing Skill

## When to Use This Skill

**Trigger keywords** (see YAML `description`) — **routing**.

Use this skill for:

- **Large documents** (100+ pages, books, reports)
- **Long PDFs** that exceed the synchronous API 100-page limit
- Any document where completeness matters more than sub-second latency
- Documents that need layout analysis (tables, formulas, figures)

**Do not use for:**

- Simple single-page OCR tasks (use `paddleocr-text-recognition` instead)
- Quick text extraction where speed is critical

## How It Works

```
1. Submit a parsing job (file or URL)
2. Poll until completion (up to 3000 pages/day)
3. Download JSONL
4. Write one Markdown per page + extract images
```

## Installation

Scripts declare their dependencies inline ([PEP 723](https://peps.python.org/pep-0723/)). No separate install step — [uv](https://docs.astral.sh/uv/) resolves automatically:

```bash
uv run scripts/ocr_job.py --help
```

## Usage

> **Working directory**: All `uv run scripts/...` commands below should be run from this skill's root directory.

### Basic Workflow

```bash
# URL mode — submit a remote document
uv run scripts/ocr_job.py --file-url "https://example.com/book.pdf" --pretty

# Local file mode — submit a local document
uv run scripts/ocr_job.py --file-path "book.pdf" --pretty
```

- Default output: `output/doc_N.md` files + images under `output/` in the current directory
- `--pretty`  — pretty-print progress to stderr
- `--output-dir` overrides the output directory (default: `./output`)
- `--model` selects the model (default: `PaddleOCR-VL-1.5`)
- `--token` overrides env var for one-shot use

### Optional Payload Flags

| Flag | Effect |
|------|--------|
| `--no-deskew` | Disable document unwarping |
| `--no-orientation` | Disable auto-rotation |
| `--charts` | Enable chart parsing (bars/pies → tables) |

### Output

```
output/
├── doc_0/
│   ├── doc_0.md
│   └── imgs/...
├── doc_1/
│   ├── doc_1.md
│   └── imgs/...
└── ...
```

Each `doc_N.md` contains the page Markdown; images are embedded as relative paths.

## Configuration

Requires two environment variables:

| Variable | Value |
|----------|-------|
| `PADDLEOCR_ASYNC_API_URL` | `https://paddleocr.aistudio-app.com/api/v2/ocr/jobs` |
| `PADDLEOCR_ASYNC_TOKEN` | Your bearer token (from AI Studio) |

Set them in the host's standard config, or pass `--token` for one-shot use.

## Verification

```bash
uv run scripts/smoke_test.py
uv run scripts/smoke_test.py --skip-api
```

First form tests API connectivity end-to-end (submits a minimal job). Second form checks configuration only.

## Understanding the Output

### Output Envelope (JSON on stdout)

On success:
```json
{
  "ok": true,
  "text": "Page 0 markdown\n\nPage 1 markdown...",
  "result": {
    "jobId": "...",
    "pagesWritten": N
  },
  "error": null
}
```

On error:
```json
{
  "ok": false,
  "text": "",
  "result": null,
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

### Exit Codes

- `0`  — Success (markdown files written)
- `1`  — API / network error
- `2`  — Job failed on server
- `3`  — Not configured
- `4`  — Input / file error

## Architecture

```
submit_job()          POST /api/v2/ocr/jobs
poll_job()            GET  /api/v2/ocr/jobs/{jobId}  (5s interval)
download_jsonl()      GET  resultUrl.jsonUrl
write_page()          Write output/doc_N.md + images/
```

Full flow is **resumable** — if `output/` already exists and `--skip-existing` is used, pages with `.md` files are skipped.

## Reference

- [AI Studio API docs](https://ai.baidu.com/ai-doc/AISTUDIO/Xmjclapam)
- [PaddleOCR on GitHub](https://github.com/PaddlePaddle/PaddleOCR)