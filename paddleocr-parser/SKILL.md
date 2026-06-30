---
name: paddleocr-parser
description: >-
  Parse documents using PaddleOCR's API. Supports both sync and async modes for PDFs
  and images. Handles large documents (100+ pages) via async jobs, small files via sync API.
  Extracts structured Markdown with tables (cell-level precision), formulas (LaTeX),
  figures, seals, charts, headers/footers, and correct reading order.
  Trigger terms: 文档解析, 版面分析, 版面还原, 表格提取, 公式识别, 多栏排版, 扫描件结构化,
  发票, 财报, 复杂 PDF, PDF转Markdown, 图表, 阅读顺序, 大文档, 整本书, 超长PDF,
  异步解析, 书籍OCR, 批量解析, 多页文档, 100页以上文档, reading order, formula, LaTeX,
  layout parsing, structure extraction, PP-StructureV3, PaddleOCR-VL,
  async jobs, large PDF, book parsing, batch OCR, 100+ pages, long document.
license: Apache-2.0
compatibility: Requires Python 3.9+, uv, and internet access.
metadata:
  openclaw:
    requires:
      env:
        - PADDLEOCR_ACCESS_TOKEN
      bins:
        - uv
    primaryEnv: PADDLEOCR_ACCESS_TOKEN
    emoji: "📄"
    homepage: https://github.com/PaddlePaddle/PaddleOCR
---

# PaddleOCR Parser — Unified Document Parsing Skill

## When to Use This Skill

**Trigger keywords (routing)**: Bilingual trigger terms (Chinese and English) are listed in the YAML `description` above—use that field for discovery and routing.

**Use this skill for**:

- Documents with tables (invoices, financial reports, spreadsheets)
- Documents with mathematical formulas (academic papers, scientific documents)
- Documents with charts and diagrams
- Multi-column layouts (newspapers, magazines, brochures)
- Complex document structures requiring layout analysis
- Large documents (100+ pages, books, reports) via async mode
- Any document requiring structured understanding

**Do not use for**:

- Simple text-only extraction
- Quick OCR tasks where speed is critical
- Screenshots or simple images with clear text

## Mode Selection

| Use Case | Recommended Mode |
|----------|-----------------|
| Small images (< 10MB) | Sync |
| Single page PDFs | Sync |
| Large PDFs (> 10MB or 100+ pages) | Async |
| Multi-page documents | Async |
| Batch processing | Async |
| Quick text extraction | Sync |

## Installation

Scripts declare their dependencies inline ([PEP 723](https://peps.python.org/pep-0723/)). No separate install step is needed — [uv](https://docs.astral.sh/uv/) resolves dependencies automatically:

```bash
uv run scripts/paddleocr_parse.py --help
```

## Usage

> **Working directory**: All `uv run scripts/...` commands below should be run from this skill's root directory (the directory containing this SKILL.md file).

### Sync Mode (Default)

For small files and quick processing:

```bash
# Parse local image
uv run scripts/paddleocr_parse.py --file-path "document.jpg" --pretty

# Parse PDF
uv run scripts/paddleocr_parse.py --file-path "document.pdf" --file-type 0 --pretty

# Parse from URL
uv run scripts/paddleocr_parse.py --file-url "https://example.com/document.jpg" --pretty

# Save output to file
uv run scripts/paddleocr_parse.py --file-path "document.jpg" --output result.json --pretty

# Print JSON to stdout without saving a file
uv run scripts/paddleocr_parse.py --file-url "URL" --stdout --pretty
```

### Async Mode

For large documents (100+ pages) with progress tracking:

```bash
# Parse large PDF with async mode
uv run scripts/paddleocr_parse.py --file-path "large-document.pdf" --async-mode --pretty

# Parse from URL with async mode
uv run scripts/paddleocr_parse.py --file-url "https://example.com/doc.pdf" --async-mode --pretty

# Save async result to file
uv run scripts/paddleocr_parse.py --file-path "document.pdf" --async-mode --output result.json --pretty
```

### Optional Payload Flags

| Flag | Effect |
|------|--------|
| `--no-deskew` | Disable document unwarping |
| `--no-orientation` | Disable auto-rotation |
| `--charts` | Enable chart parsing (bars/pies → tables) |

### File Type Detection

- `--file-type 0`: PDF
- `--file-type 1`: image
- If omitted, the type is auto-detected from the file extension. For local files, a recognized extension (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.tif`, `.webp`) is required; otherwise pass `--file-type` explicitly.

### Performance Notes

- **Sync mode**: Parsing time scales with document complexity. Single-page images typically complete in 1-5 seconds; large PDFs (50+ pages) may take several minutes.
- **Async mode**: Jobs are submitted and polled until completion (up to 3000 pages/day). Full flow is resumable — if `--skip-existing` is used, pages with `.md` files are skipped.

## Configuration

Requires one environment variable:

| Variable | Value |
|----------|-------|
| `PADDLEOCR_ACCESS_TOKEN` | Your bearer token (from AI Studio) |

Optionally configure:

| Variable | Value |
|----------|-------|
| `PADDLEOCR_MODEL` | Model selection (default: `PaddleOCR-VL-1.5`) |

### First-Time Configuration

**When API is not configured**, the script outputs:

```json
{
  "ok": false,
  "text": "",
  "result": null,
  "error": {
    "code": "CONFIG_ERROR",
    "message": "PADDLEOCR_ACCESS_TOKEN not configured. Get your API at: https://paddleocr.com"
  }
}
```

**Configuration workflow**:

1. **Show the exact error message** to the user.

2. **Guide the user to obtain credentials**: Visit the [PaddleOCR website](https://www.paddleocr.com), click **API**, select a model (`PP-StructureV3`, `PaddleOCR-VL`, or `PaddleOCR-VL-1.5`), then copy the `Token`. They map to this environment variable:
   - `PADDLEOCR_ACCESS_TOKEN` — 40-character alphanumeric string

   Optionally configure `PADDLEOCR_MODEL` for model selection. Recommend using the host application's standard configuration method rather than pasting credentials in chat.

3. **Apply credentials** — one of:
   - **User configured via the host UI**: ask the user to confirm, then retry.
   - **User pastes credentials in chat**: warn that they may be stored in conversation history, help the user persist them using the host's standard configuration method, then retry.

## Output Format

### Output Envelope

The script returns an envelope with `ok`, `text`, `result`, and `error`. Use `text` for the full document content; navigate `result.result.layoutParsingResults[n]` for per-page structured data.

For the complete schema and field-level details, see `references/output_schema.md`.

On success:
```json
{
  "ok": true,
  "text": "Extracted text from all pages",
  "result": { ... },
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
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

### Exit Codes

- `0` — Success
- `1` — API / network error
- `2` — Job failed on server (async mode)
- `3` — Not configured
- `4` — Input / file error

## Error Handling

All errors return JSON with `ok: false`. Show the error message and stop — do not fall back to your own vision capabilities. Identify the issue from `error.code` and `error.message`:

**Authentication failed (403)** — `error.message` contains "Authentication failed"

- Token is invalid, reconfigure with correct credentials

**Quota exceeded (429)** — `error.message` contains "API rate limit exceeded"

- Daily API quota exhausted, inform user to wait or upgrade

**Unsupported format** — `error.message` contains "Unsupported file format"

- File format not supported, convert to PDF/PNG/JPG

**No content detected**:

- `text` field is empty
- Document may be blank, image-only, or contain no extractable text

## Tips for Better Results

If parsing quality is poor:

- **Large or high-resolution images**: Compress with `optimize_file.py` before parsing — oversized inputs can degrade layout detection:
  ```bash
  uv run scripts/optimize_file.py input.png optimized.jpg --quality 85
  ```
- **Process specific pages (PDF only)**: If you only need certain pages from a large PDF, extract them first:
  ```bash
  uv run scripts/split_pdf.py large.pdf pages_1_5.pdf --pages "1-5"
  uv run scripts/paddleocr_parse.py --file-path "pages_1_5.pdf" --pretty
  ```
- **Check confidence**: `result.result.layoutParsingResults[n].prunedResult` includes confidence scores per layout element — low values indicate regions worth reviewing

## Testing the Skill

To verify the skill is working properly:

```bash
uv run scripts/smoke_test.py
uv run scripts/smoke_test.py --skip-api-test
```

The first form tests configuration and API connectivity. `--skip-api-test` checks configuration only.

## Reference Documentation

- `references/output_schema.md` — Full output schema, field descriptions, and command examples
- [AI Studio API docs](https://ai.baidu.com/ai-doc/AISTUDIO/Xmjclapam)
- [PaddleOCR on GitHub](https://github.com/PaddlePaddle/PaddleOCR)