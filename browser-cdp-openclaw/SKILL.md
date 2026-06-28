---
name: browser-cdp-openclaw
description: "OpenClaw browser automation tips and patterns via CDP (Chrome DevTools Protocol). Use when needing browser control, multi-step flows, tab management, stale ref recovery, profile selection, remote CDP, existing-session attach, or troubleshooting browser actions. Covers: snapshot/action loops, tab labeling, ref stability, wait patterns, error recovery, existing-session vs managed browser, remote CDP, and debug workflows."
---

# Browser CDP Tips

OpenClaw controls browsers via CDP (Chrome DevTools Protocol). The browser tool wraps Playwright on top of CDP, giving agents a stable interface while local/remote browsers and profiles swap underneath.

## Core Pattern: Snapshot → Act Loop

Always snapshot before acting. Refs are not stable across navigations.

```
snapshot → act → snapshot again (after navigation/change) → repeat
```

| Snapshot style | Ref format | When to use |
|---|---|---|
| AI (default) | `12`, `23` (numeric) | Default; good for most actions |
| Role (`--interactive`) | `e12` | Precise role-based targeting, fewer strict-mode violations |
| ARIA (`--format aria`) | `ax12` | Inspection; may not be actionable without Playwright |

```json
{ "action": "snapshot", "targetId": "t1", "refs": "aria" }
```

After snapshot, use the **same `targetId`** for follow-up actions on that tab.

### Action checklist

- **Pre-action:** Is the targetId on the same tab as the ref?
- **Post-navigation/modal/submit:** Snapshot again before next action
- **Stale ref:** Resnapshot once → retry with new ref → report blocker if still fails

## Tab Hygiene

- Open tabs with `label` for stable targeting: `{ "action": "open", "url": "https://example.com", "label": "task" }`
- Target by label: `{ "action": "snapshot", "targetId": "task" }`
- Before opening: list tabs with `{ "action": "tabs" }` and reuse existing matching label/URL
- Close duplicates: `{ "action": "close", "targetId": "t3" }`
- Never pass bare numbers like `"2"` as `targetId`; use `label`, `tabId`, or `sugestedTargetId`

## Ref Stability Rules

1. **Refs are per-snapshot** — invalid after navigation or major UI change
2. **axN refs fail fast** on stale/unbound refs; resnapshot instead of falling through
3. **Resnapshot once, retry once**; report blocker if still fails
4. **After modal, form submit, navigation:** snapshot before the next click/type

## Wait Patterns

Avoid blind sleeps. Wait for observable state:

```json
{ "action": "wait", "selector": "#main", "url": "**/dash", "load": "networkidle" }
```

- `--url` — glob patterns supported
- `--load` — `load`, `domcontentloaded`, `networkidle`
- `--fn` — JS predicate, e.g. `"window.ready===true"`
- `--selector` — wait for element visibility

## Error Recovery

When an action fails ("not visible", "strict mode violation", "covered"):

1. `snapshot --interactive` — get fresh role refs
2. `highlight <ref>` — see what Playwright is targeting
3. `errors --clear` then reproduce — check console errors
4. `requests --filter api --clear` — check network issues
5. Still failing: `trace start` → reproduce → `trace stop` (prints `TRACE:<path>`)

## Profile Selection

| Profile | When to use |
|---|---|
| `openclaw` (default) | Isolated agent browser, no login state |
| `user` | User's real Chrome with existing cookies/login |
| Custom `remote` CDP | Browser running elsewhere via `cdpUrl` |

### Remote CDP (Windows Chrome debug mode)

See [references/remote-cdp.md](references/remote-cdp.md) for verified step-by-step setup with PowerShell Chrome launch, config, and cross-network variants.

### Existing-session Chrome MCP

For `profile="user"`:

1. Open `chrome://inspect/#remote-debugging` in the target browser
2. Enable remote debugging
3. Keep the browser running and approve the attach consent prompt

Requirements: Chromium-based browser version 144+, remote debugging enabled, user at the computer to approve the prompt.

**Constraints:** Actions still working — page/element screenshots, `click-coords`. Not supported — CSS element selectors, `full-page` with `--ref`, `wait --load networkidle`, per-call timeouts on most actions.

## State Knobs

```json
{ "action": "cookies" }
{ "action": "storage", "kind": "local", "op": "get" }
{ "action": "set", "offline": true }
{ "action": "set", "headers": { "X-Debug": "1" } }
{ "action": "set", "credentials": { "user": "myuser", "pass": "mypass" } }
{ "action": "set", "geo": { "latitude": 37.7749, "longitude": -122.4194 } }
{ "action": "set", "device": "iPhone 14" }
```

## Blockers: Report, Don't Guess

When the page needs login, 2FA, captcha, camera/mic approval, or manual intervention — inspect the visible UI first. A permission screen is progress, not failure. Describe exactly what manual action is needed; do not loop or retry blindly.

## CLI Quick Reference

```bash
# Status & tabs
openclaw browser status
openclaw browser tabs

# Inspection
openclaw browser snapshot --interactive --labels
openclaw browser screenshot --full-page
openclaw browser errors --clear

# Actions
openclaw browser click e12
openclaw browser type 23 "hello" --submit
openclaw browser wait --url "**/dash" --load networkidle

# Debug
openclaw browser highlight e12
openclaw browser trace start && trace stop

# State
openclaw browser cookies set session abc --url "https://example.com"
openclaw browser set device "iPhone 14"
```

## Related

- [browser-automation skill](/plugin-skills/browser-automation) — higher-level operating loop
- [Browser tool reference](/tools/browser) — configuration, profiles, security
- [Browser control API reference](/tools/browser-control) — HTTP API and scripting patterns