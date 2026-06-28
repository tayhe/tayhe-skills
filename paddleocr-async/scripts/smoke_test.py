"""
PaddleOCR Async — Configuration & API connectivity test.

Usage:
    uv run scripts/smoke_test.py
    uv run scripts/smoke_test.py --skip-api
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "httpx>=0.24.0",
# ]
# ///

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

API_URL_VAR = "PADDLEOCR_ASYNC_API_URL"
TOKEN_VAR = "PADDLEOCR_ASYNC_TOKEN"
SMOKE_URL = "https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/main/doc/imgs lidar_det.jpg"


def get_env(key: str) -> str:
    return os.getenv(key, "").strip()


def check_config() -> tuple[str, str]:
    api_url = get_env(API_URL_VAR)
    token = get_env(TOKEN_VAR)

    errors = []
    if not api_url:
        errors.append(f"{API_URL_VAR} is not set")
    if not token:
        errors.append(f"{TOKEN_VAR} is not set")

    if errors:
        print("Configuration errors:")
        for e in errors:
            print(f"  ✗  {e}")
        print(
            f"\nGet values from  https://ai.baidu.com/ai-doc/AISTUDIO/Cmkz2mam\n"
        )
        return None, None

    print(f"  ✓  {API_URL_VAR}")
    print(f"  ✓  {TOKEN_VAR}")
    return api_url, token


def check_api(api_url: str, token: str) -> None:
    print("\nTesting API connectivity...")

    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "fileUrl": SMOKE_URL,
        "model": "PaddleOCR-VL-1.5",
        "optionalPayload": {
            "useDocUnwarping": False,
            "useDocOrientationClassify": False,
            "useChartRecognition": False,
        },
    }

    try:
        resp = httpx.post(api_url, json=payload, headers=headers, timeout=60)
    except httpx.RequestError as e:
        print(f"  ✗  Request error: {e}")
        sys.exit(1)

    if resp.status_code == 401 or resp.status_code == 403:
        print(f"  ✗  Auth error: [{resp.status_code}]  check your token")
        sys.exit(1)
    elif resp.status_code != 200:
        print(f"  ✗  HTTP {resp.status_code}: {resp.text[:200]}")
        sys.exit(1)

    body = resp.json()
    job_id = body.get("data", {}).get("jobId")
    print(f"  ✓  API reachable — job submitted:  {job_id}")

    # Clean up: tell the user to delete the job later
    print(f"\n  →  Job will be auto-cancelled by AI Studio shortly.")
    print("  →  Or delete it manually at:  https://ai.baidu.com/ai-doc/AISTUDIO/lkqzugiw4")


def main() -> None:
    parser = argparse.ArgumentParser(description="PaddleOCR Async — smoke test")
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Skip API connectivity test",
    )
    args = parser.parse_args()

    print("Checking configuration...")
    api_url, token = check_config()
    if api_url is None:
        sys.exit(1)

    print()
    if not args.skip_api:
        check_api(api_url, token)

    print("\n✓  All checks passed")


if __name__ == "__main__":
    main()