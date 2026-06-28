"""
PaddleOCR Async — Job-based Document Parsing

Submit a job, poll until done, download JSONL, write Markdown + images per page.

Usage:
    uv run scripts/ocr_job.py --file-url "URL"
    uv run scripts/ocr_job.py --file-path "doc.pdf"
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "httpx>=0.24.0",
# ]
# ///

import argparse
import base64
import json
import os
import sys
import io
from pathlib import Path
from typing import Any, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))

from lib_async import (
    submit_job,
    poll_job,
    download_jsonl,
    JobResult,
    ConfigError,
    JobFailedError,
    APIError,
    InputError,
)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_page(
    output_dir: Path, page_index: int, page_data: dict[str, Any]
) -> tuple[str, list[str]]:
    """
    Write one page's Markdown and extract its images.
    Returns (markdown_text, image_files).
    """
    page_dir = output_dir / f"doc_{page_index}"
    page_dir.mkdir(parents=True, exist_ok=True)

    markdown_text = page_data.get("markdown", {}).get("text", "")

    # Write Markdown
    md_path = page_dir / f"doc_{page_index}.md"
    md_path.write_text(markdown_text, encoding="utf-8")

    # Extract inline images from markdown.images
    image_files: list[str] = []
    images_map = page_data.get("markdown", {}).get("images", {})
    for rel_path, img_data in images_map.items():
        img_path = page_dir / rel_path
        img_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(img_data, str) and img_data.startswith("data:"):
            # base64 embedded image
            _, b64 = img_data.split(",", 1)
            img_path.write_bytes(base64.b64decode(b64))
        else:
            import httpx
            img_bytes = httpx.get(img_data, timeout=30).content
            img_path.write_bytes(img_bytes)
        image_files.append(str(img_path))

    # Extract outputImages (named images from the layout result)
    output_images = page_data.get("outputImages") or {}
    for img_name, img_url in output_images.items():
        img_path = page_dir / f"{img_name}_{page_index}.jpg"
        import httpx
        img_bytes = httpx.get(img_url, timeout=30).content
        img_path.write_bytes(img_bytes)
        image_files.append(str(img_path))

    return markdown_text, image_files


# ---------------------------------------------------------------------------
# Resume support
# ---------------------------------------------------------------------------


def already_done(output_dir: Path, total_pages: int) -> bool:
    """Return True when every page already has a .md file."""
    for i in range(total_pages):
        if not (output_dir / f"doc_{i}.md").exists():
            return False
    return True


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _error(code: str, message: str, code_exit: int) -> None:
    print(
        json.dumps(
            {"ok": False, "text": "", "result": None, "error": {"code": code, "message": message}}
        )
    )
    sys.exit(code_exit)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PaddleOCR Async — submit a job, poll, and write Markdown per page.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scripts/ocr_job.py --file-url "https://example.com/book.pdf"
  uv run scripts/ocr_job.py --file-path "book.pdf" --output-dir ./output --pretty

Exit codes:
  0  Success (markdown files written)
  1  API / network error
  2  Job failed on server
  3  Not configured
  4  Input / file error

Configuration:
  PADDLEOCR_ASYNC_API_URL  — API base URL
  PADDLEOCR_ASYNC_TOKEN    — bearer token
        """,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file-url", help="Remote URL to the document")
    input_group.add_argument("--file-path", help="Local file to upload")

    parser.add_argument(
        "--output-dir", default="output", help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "--model", default="PaddleOCR-VL-1.5", help="Model name"
    )
    parser.add_argument(
        "--token", help="One-shot token override (skip env var)"
    )
    parser.add_argument(
        "--no-deskew", action="store_true", help="Disable document unwarping"
    )
    parser.add_argument(
        "--no-orientation", action="store_true", help="Disable auto-rotation"
    )
    parser.add_argument(
        "--charts", action="store_true", help="Enable chart parsing"
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print progress"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip pages that already have a .md file (resumable)",
    )

    args = parser.parse_args()

    # Build optional payload
    optional_payload: dict[str, bool] = {
        "useDocUnwarping": not args.no_deskew,
        "useDocOrientationClassify": not args.no_orientation,
        "useChartRecognition": args.charts,
    }

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Submit job
    try:
        job_result: JobResult = submit_job(
            file_path=args.file_path,
            file_url=args.file_url,
            model=args.model,
            optional_payload=optional_payload,
            token=args.token or "",
        )
    except InputError as e:
        _error("INPUT_ERROR", str(e), 4)
    except ConfigError as e:
        _error("CONFIG_ERROR", str(e), 3)
    except APIError as e:
        _error("API_ERROR", str(e), 1)

    job_id = job_result.job_id

    # 2. Poll until done
    if args.skip_existing:
        total_pages = 0  # unknown until job completes
        if already_done(output_dir, 999999):
            if args.pretty:
                print("All pages already done — nothing to do.", file=sys.stderr)
            print(
                json.dumps(
                    {"ok": True, "text": "Already complete", "result": {"jobId": job_id}, "error": None}
                )
            )
            sys.exit(0)

    try:
        final_data = poll_job(job_id, token=args.token or "", verbose=args.pretty)
    except JobFailedError as e:
        _error("JOB_FAILED", str(e), 2)
    except APIError as e:
        _error("API_ERROR", str(e), 1)

    # Extract result URL
    result_url_dict = final_data.get("resultUrl") or {}
    jsonl_url = result_url_dict.get("jsonUrl") or ""

    if not jsonl_url:
        _error("API_ERROR", "resultUrl.jsonUrl not found in response", 1)

    # 3. Download JSONL
    try:
        raw_lines = download_jsonl(jsonl_url, token=args.token or "")
    except APIError as e:
        _error("API_ERROR", str(e), 1)

    # 4. Parse & write pages
    all_texts: list[str] = []
    written = 0

    for line in raw_lines:
        result_obj = line.get("result") or {}
        layout_results: list[dict] = result_obj.get("layoutParsingResults") or []

        for page_index, page_data in enumerate(layout_results):
            if args.skip_existing and (output_dir / f"doc_{page_index}.md").exists():
                continue
            markdown_text, _ = write_page(output_dir, page_index, page_data)
            all_texts.append(markdown_text)
            written += 1

    full_text = "\n\n".join(all_texts)

    print(
        json.dumps(
            {
                "ok": True,
                "text": full_text,
                "result": {
                    "jobId": job_id,
                    "pagesWritten": written,
                },
                "error": None,
            },
            ensure_ascii=False,
        )
    )

    sys.exit(0)


if __name__ == "__main__":
    main()