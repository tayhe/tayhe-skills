"""
PaddleOCR Document Parsing — Unified CLI

Single entry point supporting both sync and async modes.

Usage:
    uv run paddleocr_parse.py --file-url "https://example.com/doc.pdf"
    uv run paddleocr_parse.py --file-path "scan.png" --mode sync
    uv run paddleocr_parse.py --file-path "doc.pdf" --output-per-page ./pages

Mode auto-detection:
    - Image files (png/jpg/bmp/tiff/webp) → sync
    - PDF files → async
    - Unknown → async
"""

# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27"]
# ///

import argparse
import base64
import io
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))

import lib_async
import lib_sync
from lib_async import (
    ConfigError,
    InputError,
    JobFailedError,
    APIError,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp")
DEFAULT_MODEL = "PaddleOCR-VL-1.5"


# ---------------------------------------------------------------------------
# Auto mode detection
# ---------------------------------------------------------------------------


def detect_mode(file_path: Optional[str], file_url: Optional[str]) -> str:
    """Auto-detect the appropriate mode based on input file type.

    Image → sync, PDF → async, Unknown → async.
    """
    source = file_path or file_url or ""
    lower = source.lower()

    for ext in IMAGE_EXTENSIONS:
        if lower.endswith(ext):
            return "sync"

    if lower.endswith(".pdf"):
        return "async"

    return "async"


# ---------------------------------------------------------------------------
# Async helpers
# ---------------------------------------------------------------------------


def _write_page(
    output_dir: Path, page_index: int, page_data: dict[str, Any]
) -> tuple[str, list[str]]:
    """Write one page's Markdown and images. Returns (markdown_text, image_files)."""
    page_dir = output_dir / f"doc_{page_index}"
    page_dir.mkdir(parents=True, exist_ok=True)

    markdown_text = page_data.get("markdown", {}).get("text", "")

    md_path = page_dir / f"doc_{page_index}.md"
    md_path.write_text(markdown_text, encoding="utf-8")

    image_files: list[str] = []
    images_map = page_data.get("markdown", {}).get("images", {})
    for rel_path, img_data in images_map.items():
        img_path = page_dir / rel_path
        img_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(img_data, str) and img_data.startswith("data:"):
            _, b64 = img_data.split(",", 1)
            img_path.write_bytes(base64.b64decode(b64))
        else:
            import httpx as _httpx
            img_bytes = _httpx.get(img_data, timeout=30).content
            img_path.write_bytes(img_bytes)
        image_files.append(str(img_path))

    output_images = page_data.get("outputImages") or {}
    for img_name, img_url in output_images.items():
        img_path = page_dir / f"{img_name}_{page_index}.jpg"
        import httpx as _httpx
        img_bytes = _httpx.get(img_url, timeout=30).content
        img_path.write_bytes(img_bytes)
        image_files.append(str(img_path))

    return markdown_text, image_files


# ---------------------------------------------------------------------------
# Envelope builder
# ---------------------------------------------------------------------------


def _make_envelope(
    ok: bool,
    text: str = "",
    result: Optional[dict] = None,
    error: Optional[dict] = None,
) -> dict:
    return {"ok": ok, "text": text, "result": result, "error": error}


# ---------------------------------------------------------------------------
# Exit helper
# ---------------------------------------------------------------------------


def _exit_with_error(code: int, envelope: dict, pretty: bool) -> None:
    indent = 2 if pretty else None
    print(json.dumps(envelope, ensure_ascii=False, indent=indent))
    sys.exit(code)


# ---------------------------------------------------------------------------
# Parse --split-pages into a set of 0-based page indices
# ---------------------------------------------------------------------------


def _parse_split_pages(ranges_str: str, total_pages: int) -> list[int]:
    """Parse ranges like '1-3,5,7-9' into sorted 0-based indices."""
    indices = set()
    for part in ranges_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s) - 1
            end = int(end_s) - 1
            for i in range(start, end + 1):
                if 0 <= i < total_pages:
                    indices.add(i)
        else:
            idx = int(part) - 1
            if 0 <= idx < total_pages:
                indices.add(idx)
    return sorted(indices)


# ---------------------------------------------------------------------------
# Sync path
# ---------------------------------------------------------------------------


def run_sync(args: argparse.Namespace) -> None:
    """Execute sync mode: single API call via lib_sync."""
    options: dict[str, Any] = {}
    if args.no_deskew:
        options["useDocUnwarping"] = False
    if args.no_orientation:
        options["useDocOrientationClassify"] = False
    if args.charts:
        options["useChartRecognition"] = True

    raw = lib_sync.parse_document(
        file_path=args.file_path,
        file_url=args.file_url,
        **options,
    )

    envelope = _make_envelope(
        ok=raw["ok"],
        text=raw.get("text", ""),
        result={"mode": "sync", **(raw.get("result") or {})},
        error=raw.get("error"),
    )

    if not envelope["ok"]:
        _exit_with_error(1, envelope, args.pretty)

    # Per-page output
    if args.output_per_page:
        out_dir = Path(args.output_per_page).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        result = raw.get("result") or {}
        pages = (result.get("result") or {}).get("layoutParsingResults") or []
        for idx, page in enumerate(pages):
            _write_page(out_dir, idx, page)

    _write_output(envelope, args)


# ---------------------------------------------------------------------------
# Async path
# ---------------------------------------------------------------------------


def run_async(args: argparse.Namespace) -> None:
    """Execute async mode: submit → poll → download → assemble."""
    optional_payload: dict[str, bool] = {
        "useDocUnwarping": not args.no_deskew,
        "useDocOrientationClassify": not args.no_orientation,
        "useChartRecognition": args.charts,
    }

    # 1. Submit
    try:
        job = lib_async.submit_job(
            file_path=args.file_path,
            file_url=args.file_url,
            model=args.model,
            optional_payload=optional_payload,
            token=args.token or "",
        )
    except InputError as e:
        _exit_with_error(4, _make_envelope(False, error={"code": "INPUT_ERROR", "message": str(e)}), args.pretty)
    except ConfigError as e:
        _exit_with_error(3, _make_envelope(False, error={"code": "CONFIG_ERROR", "message": str(e)}), args.pretty)
    except APIError as e:
        _exit_with_error(1, _make_envelope(False, error={"code": "API_ERROR", "message": str(e)}), args.pretty)

    job_id = job.job_id

    # 2. Poll
    try:
        final_data = lib_async.poll_job(
            job_id, token=args.token or "", verbose=args.stdout is None
        )
    except JobFailedError as e:
        _exit_with_error(2, _make_envelope(False, error={"code": "JOB_FAILED", "message": str(e)}), args.pretty)
    except APIError as e:
        _exit_with_error(1, _make_envelope(False, error={"code": "API_ERROR", "message": str(e)}), args.pretty)

    # 3. Download JSONL
    jsonl_url = (final_data.get("resultUrl") or {}).get("jsonUrl") or ""
    if not jsonl_url:
        _exit_with_error(1, _make_envelope(False, error={"code": "API_ERROR", "message": "resultUrl.jsonUrl not found"}), args.pretty)

    try:
        raw_lines = lib_async.download_jsonl(jsonl_url, token=args.token or "")
    except APIError as e:
        _exit_with_error(1, _make_envelope(False, error={"code": "API_ERROR", "message": str(e)}), args.pretty)

    # 4. Assemble results
    all_texts: list[str] = []
    all_pages: list[dict] = []

    for line in raw_lines:
        result_obj = line.get("result") or {}
        layout_results: list[dict] = result_obj.get("layoutParsingResults") or []
        for page in layout_results:
            md_text = page.get("markdown", {}).get("text", "")
            all_texts.append(md_text)
            all_pages.append(page)

    # 5. Per-page output
    if args.output_per_page:
        out_dir = Path(args.output_per_page).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        for idx, page in enumerate(all_pages):
            if args.skip_existing and (out_dir / f"doc_{idx}.md").exists():
                continue
            _write_page(out_dir, idx, page)

    full_text = "\n\n".join(all_texts)

    envelope = _make_envelope(
        ok=True,
        text=full_text,
        result={
            "mode": "async",
            "jobId": job_id,
            "pages": len(all_pages),
            "layoutParsingResults": all_pages,
        },
    )

    _write_output(envelope, args)


# ---------------------------------------------------------------------------
# Output handling
# ---------------------------------------------------------------------------


def _write_output(envelope: dict, args: argparse.Namespace) -> None:
    """Write the JSON envelope to the requested destinations."""
    indent = 2 if args.pretty else None
    json_str = json.dumps(envelope, ensure_ascii=False, indent=indent)

    if args.output:
        out_path = Path(args.output).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json_str, encoding="utf-8")

    if args.stdout or not args.output:
        print(json_str)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paddleocr_parse",
        description="PaddleOCR document parsing — unified CLI with sync/async modes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s --file-url "https://example.com/scan.png"
  %(prog)s --file-path "doc.pdf" --output result.json --pretty
  %(prog)s --file-path "doc.pdf" --output-per-page ./pages
  %(prog)s --file-url "https://example.com/doc.pdf" --mode async --skip-existing

exit codes:
  0  success
  1  API / network error
  2  job failed on server (async)
  3  not configured
  4  input / file error

env vars:
  PADDLEOCR_SYNC_API_URL  — sync endpoint (ends with /layout-parsing)
  PADDLEOCR_ASYNC_API_URL — async endpoint (default: paddleocr.aistudio-app.com)
  PADDLEOCR_ACCESS_TOKEN  — bearer token
  PADDLEOCR_ASYNC_TOKEN   — fallback token
""",
    )

    # Input (mutually exclusive, required)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file-url", help="Remote URL to the document")
    input_group.add_argument("--file-path", help="Local file to upload")

    # Mode
    parser.add_argument(
        "--mode",
        choices=["auto", "sync", "async"],
        default="auto",
        help="Run mode (default: auto-detect from file type)",
    )

    # Model & auth
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--token", help="One-shot token override (skip env var)")

    # Output
    parser.add_argument("--stdout", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--output", metavar="FILE", help="Write JSON envelope to file")
    parser.add_argument("--output-per-page", metavar="DIR", help="Write one Markdown per page to directory")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    # Processing options
    parser.add_argument("--skip-existing", action="store_true", help="Skip pages with existing .md files (async only)")
    parser.add_argument("--no-deskew", action="store_true", help="Disable document unwarping")
    parser.add_argument("--no-orientation", action="store_true", help="Disable auto-rotation")
    parser.add_argument("--charts", action="store_true", help="Enable chart parsing")
    parser.add_argument("--optimize", action="store_true", help="Auto-compress large images before upload")
    parser.add_argument("--split-pages", metavar="RANGES", help="PDF page ranges, e.g. 1-3,5,7-9")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Resolve mode
    mode = args.mode
    if mode == "auto":
        mode = detect_mode(args.file_path, args.file_url)

    if args.skip_existing and mode == "sync":
        print("[warn] --skip-existing is only supported in async mode; ignoring.", file=sys.stderr)

    if mode == "sync":
        run_sync(args)
    else:
        run_async(args)


if __name__ == "__main__":
    main()
