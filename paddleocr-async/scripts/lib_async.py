"""
PaddleOCR Async — Core Library

Provides: submit_job, poll_job, download_jsonl
"""

import os
import time
from dataclasses import dataclass
from typing import Optional

import httpx


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ConfigError(Exception):
    pass


class InputError(Exception):
    pass


class JobFailedError(Exception):
    pass


class APIError(Exception):
    pass


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def _get_env(key: str) -> str:
    return os.getenv(key, "").strip()


def get_config(api_url_var: str, token_var: str) -> tuple[str, str]:
    api_url = _get_env(api_url_var)
    token = _get_env(token_var)

    if not api_url:
        raise ConfigError(f"{api_url_var} is not set.  Get your API URL from AI Studio.")
    if not token:
        raise ConfigError(f"{token_var} is not set.  Get your token from AI Studio.")

    return api_url, token


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class JobResult:
    job_id: str
    total_pages: int  # known after polling
    result_url: str  # populated after job is done


# ---------------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------------


def submit_job(
    *,
    file_path: Optional[str] = None,
    file_url: Optional[str] = None,
    model: str = "PaddleOCR-VL-1.5",
    optional_payload: dict[str, bool],
    token: str = "",
) -> JobResult:
    """
    Submit a parsing job to the async API.

    Returns JobResult with jobId and totalPages (known from the response).
    Raises ConfigError / InputError / APIError.
    """
    if bool(file_path) == bool(file_url):
        raise InputError("Provide exactly one of file_path or file_url")

    api_url, token = get_config(
        "PADDLEOCR_ASYNC_API_URL", "PADDLEOCR_ASYNC_TOKEN"
    )
    if not token:
        token = _get_env("PADDLEOCR_ASYNC_TOKEN")

    headers = {"Authorization": f"bearer {token}"}

    if file_url:
        headers["Content-Type"] = "application/json"
        payload = {
            "fileUrl": file_url,
            "model": model,
            "optionalPayload": optional_payload,
        }
        resp = httpx.post(api_url, json=payload, headers=headers, timeout=60)

    else:
        if not os.path.exists(file_path):
            raise InputError(f"File not found: {file_path}")

        files = {
            "file": open(file_path, "rb"),
        }
        data = {
            "model": model,
            "optionalPayload": optional_payload,
        }
        resp = httpx.post(api_url, headers=headers, data=data, files=files, timeout=120)
        files["file"].close()

    if resp.status_code != 200:
        raise APIError(f"[{resp.status_code}] {resp.text[:300]}")

    body = resp.json()
    data_dict = body.get("data", {})

    return JobResult(
        job_id=data_dict["jobId"],
        total_pages=0,  # unknown until job completes
        result_url="",  # filled after polling
    )


# ---------------------------------------------------------------------------
# Poll
# ---------------------------------------------------------------------------


def poll_job(
    job_id: str,
    *,
    token: str = "",
    interval: int = 5,
    verbose: bool = False,
) -> dict:
    """
    Poll GET <api_url>/<jobId> until the job reaches 'done' or 'failed'.

    Returns the final job-data dict.

    Raises JobFailedError when the server reports state == 'failed'.
    Raises APIError on HTTP error.
    """
    import sys

    api_url, token = get_config("PADDLEOCR_ASYNC_API_URL", "PADDLEOCR_ASYNC_TOKEN")
    if not token:
        token = _get_env("PADDLEOCR_ASYNC_TOKEN")

    headers = {"Authorization": f"bearer {token}"}
    url = f"{api_url}/{job_id}"

    while True:
        resp = httpx.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise APIError(f"[{resp.status_code}] {resp.text[:300]}")

        data_dict = resp.json().get("data", {})
        state = data_dict.get("state", "pending")

        if state == "pending":
            if verbose:
                print("[pending] Waiting for job to start...", file=sys.stderr)
        elif state == "running":
            try:
                ep = data_dict["extractProgress"]
                total = ep.get("totalPages", "?")
                done = ep.get("extractedPages", "?")
                if verbose:
                    print(f"[running] Pages: {done}/{total}", file=sys.stderr)
            except KeyError:
                if verbose:
                    print("[running] Processing...", file=sys.stderr)
        elif state == "done":
            if verbose:
                print("[done]", file=sys.stderr)
            return data_dict  # contains resultUrl.jsonUrl
        elif state == "failed":
            msg = data_dict.get("errorMsg", "Unknown error")
            raise JobFailedError(msg)

        time.sleep(interval)


# ---------------------------------------------------------------------------
# Download JSONL
# ---------------------------------------------------------------------------


def download_jsonl(jsonl_url: str, token: str = "") -> list[dict]:
    headers = {"Authorization": f"bearer {token}"}
    resp = httpx.get(jsonl_url, headers=headers, timeout=300)

    if resp.status_code != 200:
        raise APIError(f"[{resp.status_code}] {resp.text[:300]}")

    lines = []
    for raw in resp.text.splitlines():
        if not (line := raw.strip()):
            continue
        lines.append(json.loads(line))

    return lines