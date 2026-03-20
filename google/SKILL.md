---
name: google-cli
description: Use the local Google terminal CLI at /home/techbrain/CLI-Functions/google/GoogleCLI.py for Gmail, Google Drive, and Google Calendar tasks. Use this when asked to list/read/search/analyze emails, send SMTP emails, list/download Drive files, or list/create calendar events.
---

# Google CLI

Use the local script for Google operations in this workspace.

## Runtime

- Working directory: `/home/techbrain/CLI-Functions/google`
- Script path: `/home/techbrain/CLI-Functions/google/GoogleCLI.py`
- Env file auto-loaded by script: `/home/techbrain/CLI-Functions/.env`
- Activate venv: `source /home/techbrain/CLI-Functions/google/.venv/bin/activate`
- If dependencies are missing: `pip install google-auth google-auth-oauthlib google-api-python-client python-dotenv beautifulsoup4 html2text`

## Auth

Important distinction:

- `token.json` is an authorized-user token cache (contains refresh/access token and granted scopes).
- "Client config" is OAuth app config JSON (file name can vary: `credentials.json`, `client_secret_*.json`, etc.).
- Client config is needed only when creating a brand-new token or requesting scopes not present in the current token.

Scope behavior (current code):

- If no scope override is provided, the CLI first reads scopes from `token.json` and selects the ones for the requested service (`gmail`, `drive`, `calendar`).
- Hardcoded command scopes are now only a fallback when token scopes are unavailable.

Token path resolution when `--token-path` is omitted:

1. `GOOGLE_TOKEN_PATH`
2. `~/.codex/token/google_token.json` (if exists)
3. `/home/techbrain/CLI-Functions/google/token/token.json` (if exists)
4. fallback write target: `~/.codex/token/google_token.json`

Recommended in this workspace:

- Always use: `--token-path /home/techbrain/CLI-Functions/google/token/token.json`
- Or persist in `.env`: `GOOGLE_TOKEN_PATH=/home/techbrain/CLI-Functions/google/token/token.json`

If OAuth client config is needed, provide one of:

- `--client-config-file /path/to/oauth_app_config.json`
- `--client-config-json '<json>'`
- `GOOGLE_CLIENT_SECRET_FILE`
- `GOOGLE_CLIENT_SECRET_JSON`

Scope override guidance:

- Prefer `--scope <scope>` and repeat it for multiples.
- Use `--scopes` only if needed; it is easier to parse incorrectly with subcommands.

## Output modes

- Global output format: `--format text|json|csv|ndjson` (default: `text`).
- Optional file output: `--output-file /path/file.json`.
- In `--format json` and `--format ndjson`, scalar responses (for example `gmail count`) are emitted as JSON numbers.
- In `--format csv`, nested payloads (for example `gmail analyze`) are flattened into tabular rows with a `section` column.

## Gmail

- List: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json gmail list --max-results 5 --label INBOX --read-status all`
- Count: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json gmail count --label INBOX --read-status unread`
- Search (paginated up to `--max-results`): `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json gmail search --query 'from:alerts@example.com newer_than:7d' --max-results 50 --label ALL --read-status all`
- Search today: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json gmail search --query 'after:2026/03/19 before:2026/03/20' --max-results 50 --label INBOX --read-status all`
- Read by id: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json gmail read-by-id --id '<MESSAGE_ID>' --render-html`
- Read by subject: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json gmail get-by-subject --subject 'Invoice' --label INBOX --read-status all --render-html`
- List by sender: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json gmail list-by-sender --sender 'example@domain.com' --max-results 10 --label INBOX --read-status all`
- Unique senders (paginated up to `--max-scan`): `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json gmail unique-senders --max-scan 600 --label INBOX --read-status all`
- Analyze mailbox summary: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json --format json gmail analyze --label INBOX --read-status all --query 'newer_than:30d' --max-scan 0 --top 20`
- Analyze + save report file: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json --format json --output-file /tmp/inbox_summary.json gmail analyze --label INBOX --max-scan 0 --top 20`
- Analyze in CSV: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json --format csv --output-file /tmp/inbox_summary.csv gmail analyze --label INBOX --max-scan 0 --top 20`
- Count in NDJSON: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json --format ndjson gmail count --label INBOX --read-status unread`
- Send SMTP: `python GoogleCLI.py gmail send-smtp --subject 'Hi' --body 'Message' --to 'person@domain.com'`
- SMTP optional flags: `--from-email`, `--password`, `--attachment`, `--html`
- SMTP fallback env vars: `EMAIL_USER`, `EMAIL_PASSWORD`

## Drive

- List files: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json drive list --max-results 10`
- Download by exact name: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json drive download --file-name 'report.pdf' --destination-path '/tmp'`

## Calendar

- List upcoming: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json calendar list-upcoming --max-results 5`
- Create event: `python GoogleCLI.py --token-path /home/techbrain/CLI-Functions/google/token/token.json calendar create-event --summary 'Meeting' --start-dt '2026-03-20T10:00:00-03:00' --end-dt '2026-03-20T11:00:00-03:00'`
- Calendar optional flags: `--location`, `--description`, `--attendee`, `--reminders-json`, `--extra-fields-json`

## Operating Rules

- Default to read-only commands first.
- Always confirm before state-changing actions (`gmail send-smtp`, `drive download`, `calendar create-event`).
- For broad mailbox requests, prefer `gmail analyze` for complete summary, then use `gmail search`/`gmail list`, and finally `gmail read-by-id` for deep dive.

## Troubleshooting

- Error: `Client config not found...`
- Cause A: token path not being used.
- Fix A: pass `--token-path /home/techbrain/CLI-Functions/google/token/token.json` explicitly.
- Cause B: token does not include required scopes.
- Fix B: provide OAuth app config and re-consent with needed scopes.
- Check token scopes quickly: `python3 -c "import json;print(json.load(open('/home/techbrain/CLI-Functions/google/token/token.json')).get('scopes'))"`
- If `--output-file` fails, ensure the destination directory is writable.
