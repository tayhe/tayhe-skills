"""
PaddleOCR Parser — Configuration & API connectivity smoke test.

Verifies that all required environment variables are set and optionally
tests both sync and async API connectivity.

Usage:
    uv run paddleocr-parser/scripts/smoke_test.py
    uv run paddleocr-parser/scripts/smoke_test.py --skip-api
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "httpx>=0.24.0",
# ]
# ///

import argparse
import os
import sys
from pathlib import Path

import httpx

# Auto-load .env from skill root
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.is_file():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ---------------------------------------------------------------------------
# Env helpers (mirrors lib_sync / lib_async)
# ---------------------------------------------------------------------------

_DEFAULT_ASYNC_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"


def _get_env(key: str) -> str:
    return os.getenv(key, "").strip()


def _get_env_compat(key: str, *fallbacks: str) -> str:
    for env_key in (key, *fallbacks):
        val = _get_env(env_key)
        if val:
            return val
    return ""


# ---------------------------------------------------------------------------
# Config check
# ---------------------------------------------------------------------------

def _check_config() -> bool:
    """Check all configuration variables. Returns True if all required are present."""
    ok = True

    # Token
    token = _get_env_compat("PADDLEOCR_ACCESS_TOKEN", "PADDLEOCR_ASYNC_TOKEN")
    if token:
        print(f"  ✓  PADDLEOCR_ACCESS_TOKEN — OK")
    else:
        # Show which vars were tried
        a = _get_env("PADDLEOCR_ACCESS_TOKEN")
        b = _get_env("PADDLEOCR_ASYNC_TOKEN")
        if a or b:
            print(f"  ✓  PADDLEOCR_ACCESS_TOKEN — OK")
        else:
            print(f"  ✗  PADDLEOCR_ACCESS_TOKEN — MISSING")
            print(f"     (also checked PADDLEOCR_ASYNC_TOKEN)")
            ok = False

    # Sync API URL
    sync_url = _get_env_compat(
        "PADDLEOCR_SYNC_API_URL",
        "PADDLEOCR_DOC_PARSING_API_URL",
        "PADDLEOCR_API_URL",
    )
    if sync_url:
        print(f"  ✓  PADDLEOCR_SYNC_API_URL — OK")
    else:
        found_fb = False
        for fb in ("PADDLEOCR_DOC_PARSING_API_URL", "PADDLEOCR_API_URL"):
            if _get_env(fb):
                found_fb = True
                break
        if found_fb:
            print(f"  ✓  PADDLEOCR_SYNC_API_URL — OK (via fallback)")
        else:
            print(f"  ✗  PADDLEOCR_SYNC_API_URL — MISSING")
            print(f"     (also checked PADDLEOCR_DOC_PARSING_API_URL, PADDLEOCR_API_URL)")
            ok = False

    # Async API URL (has a default)
    async_url = _get_env_compat("PADDLEOCR_ASYNC_API_URL")
    if async_url:
        print(f"  ✓  PADDLEOCR_ASYNC_API_URL — OK")
    else:
        print(f"  ○  PADDLEOCR_ASYNC_API_URL — using default")
        print(f"     {_DEFAULT_ASYNC_URL}")

    return ok


# ---------------------------------------------------------------------------
# API connectivity tests
# ---------------------------------------------------------------------------

def _test_sync_api(token: str) -> bool:
    """Make a minimal sync API request. Returns True on success."""
    sync_url = _get_env_compat(
        "PADDLEOCR_SYNC_API_URL",
        "PADDLEOCR_DOC_PARSING_API_URL",
        "PADDLEOCR_API_URL",
    )
    if not sync_url:
        print("  ✗  Sync API URL not configured, skipping")
        return False

    print(f"\nTesting sync API connectivity...")
    print(f"  URL: {sync_url}")

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
        "Client-Platform": "official-skill",
    }
    # Minimal request — empty file field will fail validation but confirms auth+reachability
    payload = {"file": "", "fileType": 1, "visualize": False}

    try:
        resp = httpx.post(sync_url, json=payload, headers=headers, timeout=30)
    except httpx.RequestError as e:
        print(f"  ✗  Request error: {e}")
        return False

    if resp.status_code == 401 or resp.status_code == 403:
        print(f"  ✗  Auth error: [{resp.status_code}] — check your token")
        return False
    elif resp.status_code == 200:
        print(f"  ✓  Sync API reachable (HTTP 200)")
        return True
    else:
        # Non-200 is expected for invalid payload; as long as we got a response,
        # the endpoint is reachable and auth is accepted
        body_snippet = resp.text[:120].replace("\n", " ")
        print(f"  ✓  Sync API reachable (HTTP {resp.status_code}): {body_snippet}")
        return True


def _test_async_api(token: str) -> bool:
    """Make a minimal async API request. Returns True on success."""
    async_url = _get_env_compat("PADDLEOCR_ASYNC_API_URL") or _DEFAULT_ASYNC_URL

    print(f"\nTesting async API connectivity...")
    print(f"  URL: {async_url}")

    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
    }
    # Minimal request — missing fileUrl will fail validation but confirms auth+reachability
    payload = {
        "model": "PaddleOCR-VL-1.5",
        "optionalPayload": {
            "useDocUnwarping": False,
            "useDocOrientationClassify": False,
            "useChartRecognition": False,
        },
    }

    try:
        resp = httpx.post(async_url, json=payload, headers=headers, timeout=30)
    except httpx.RequestError as e:
        print(f"  ✗  Request error: {e}")
        return False

    if resp.status_code == 401 or resp.status_code == 403:
        print(f"  ✗  Auth error: [{resp.status_code}] — check your token")
        return False
    elif resp.status_code == 200:
        body = resp.json()
        job_id = body.get("data", {}).get("jobId")
        print(f"  ✓  Async API reachable — job submitted: {job_id}")
        return True
    else:
        body_snippet = resp.text[:120].replace("\n", " ")
        print(f"  ✓  Async API reachable (HTTP {resp.status_code}): {body_snippet}")
        return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="PaddleOCR Parser — configuration & API smoke test"
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Skip API connectivity tests, only check configuration",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("PaddleOCR Parser — Smoke Test")
    print("=" * 60)

    # Step 1: config
    print("\n[1] Checking configuration...")
    config_ok = _check_config()
    if not config_ok:
        print(
            "\nGet credentials from: https://www.paddleocr.com"
        )
        return 1

    if args.skip_api:
        print("\n[2] Skipping API connectivity tests (--skip-api)")
        print("\n" + "=" * 60)
        print("✓  Configuration OK")
        print("=" * 60)
        return 0

    # Step 2: API connectivity
    token = _get_env_compat("PADDLEOCR_ACCESS_TOKEN", "PADDLEOCR_ASYNC_TOKEN")

    sync_ok = _test_sync_api(token)
    async_ok = _test_async_api(token)

    print("\n" + "=" * 60)
    if sync_ok and async_ok:
        print("✓  All checks passed")
    elif sync_ok or async_ok:
        print("○  Partial — some API endpoints unreachable")
    else:
        print("✗  API connectivity tests failed")
        return 1
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
