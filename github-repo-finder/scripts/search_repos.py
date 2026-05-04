#!/usr/bin/env python3
"""
Batch GitHub repo search helper for find-repo skill.
Wraps `gh search repos` for multiple keyword groups.

Usage:
  python3 search_repos.py "keyword1" "keyword2" ...
  python3 search_repos.py --language python "keyword1" "keyword2"
"""
import subprocess
import json
import sys
import shutil


def search_repos(query, language=None, limit=5, sort="stars"):
    if not shutil.which("gh"):
        return {"error": "'gh' CLI not installed. See https://cli.github.com/"}

    cmd = [
        "gh", "search", "repos", query,
        "--sort", sort,
        "--limit", str(limit),
        "--json", "name,fullName,url,description,stargazersCount,updatedAt,language,license"
    ]
    if language:
        cmd.extend(["--language", language])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"query": query, "error": result.stderr.strip() or "Command failed"}

    try:
        repos = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"query": query, "error": "Failed to parse JSON"}

    return {"query": query, "count": len(repos), "results": repos}


def main():
    language = None
    queries = []

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--language" and i + 1 < len(args):
            language = args[i + 1]
            i += 2
        else:
            queries.append(args[i])
            i += 1

    if not queries:
        print("Usage: search_repos.py [--language LANG] query1 [query2 ...]", file=sys.stderr)
        sys.exit(1)

    all_results = []
    seen_ids = set()

    for q in queries:
        resp = search_repos(q, language=language)
        if "error" in resp:
            print(json.dumps(resp, ensure_ascii=False))
            continue
        for repo in resp["results"]:
            rid = repo.get("fullName") or repo.get("name")
            if rid not in seen_ids:
                seen_ids.add(rid)
                all_results.append(repo)

    all_results.sort(key=lambda r: r.get("stargazersCount", 0), reverse=True)
    print(json.dumps(all_results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
