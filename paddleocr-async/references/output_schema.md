# PaddleOCR Async — Output Schema

## Envelope (JSON on stdout)

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

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success — markdown files written |
| 1 | API / network error |
| 2 | Job failed on server |
| 3 | Not configured |
| 4 | Input / file error |

## Output Directory Layout

```
output/
├── doc_0/
│   ├── doc_0.md
│   └── imgs/...    (inline images)
├── doc_1/
│   ├── doc_1.md
│   └── imgs/...
└── ...
```

Markdown files embed images as **relative paths** — compatible with any tool that follows paths.

## JSONL Raw Format

Each line is a JSON object:
```
{"result": {"layoutParsingResults": [...]}}
```

`layoutParsingResults[n]` per page:
- `markdown.text` — page content in Markdown
- `markdown.images` — map of relative-path → base64 or URL
- `outputImages` — map of name → URL

## Polling States

| State | Action |
|-------|--------|
| `pending` | Log and sleep 5s |
| `running` | Log progress (pages extracted / total) and sleep 5s |
| `done` | Download JSONL from `resultUrl.jsonUrl` |
| `failed` | Exit with code 2 |