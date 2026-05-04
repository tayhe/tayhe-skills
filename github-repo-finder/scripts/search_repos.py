#!/usr/bin/env python3
"""
GitHub Repo Search Helper
Wraps `gh search repos` to return structured JSON output.
"""
import subprocess
import json
import sys
import shutil

def search_repos(query, language=None, limit=5, sort="stars"):
    if not shutil.which("gh"):
        return {"error": "'gh' CLI is not installed. Install from https://cli.github.com/"}
    
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
        return {"error": result.stderr.strip() or "Command failed"}
    
    return {"results": json.loads(result.stdout)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: search_repos.py <query> [language] [limit]", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else None
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    output = search_repos(query, language, limit)
    print(json.dumps(output, indent=2, ensure_ascii=False))