---
name: google-cli
description: Use the local Google terminal CLI at <path_to_GoogleCLI.py> for Gmail, Google Drive, and Google Calendar tasks. Use this when asked to list/read/search/analyze emails, send SMTP emails, list/download Drive files, or list/create calendar events.
---

# Google CLI

Use the local script for Google operations in this workspace.

## ⚠️ CRITICAL: Mandatory setup before ANY command

You **MUST** follow these two rules for **EVERY** command. Skipping either will cause failures.

### 1. Always use the venv Python

The system Python does NOT have the required dependencies. You must use the virtual environment's Python executable.

**Preferred method** — use the full venv Python path directly (works without activation):

```bash
# Windows
& "<path_to_repo>\google\.venv\Scripts\python.exe" .\GoogleCLI.py <args>

# Linux / macOS
<path_to_repo>/google/.venv/bin/python ./GoogleCLI.py <args>
```

Alternative — activate venv first, then use `python`:

```bash
# Windows
& "<path_to_repo>\google\.venv\Scripts\Activate.ps1"
python .\GoogleCLI.py <args>

# Linux / macOS
source <path_to_repo>/google/.venv/bin/activate
python ./GoogleCLI.py <args>
```

### 2. Always pass --token-path

```bash
--token-path <path_to_token.json>
```

This is required for all Gmail (except `send-smtp`), Drive, and Calendar commands.

---

**Base command template** (use this for every call):

```bash
<path_to_venv_python> GoogleCLI.py --token-path <path_to_token.json> <service> <command> <flags>
```

Working directory for all commands should be the directory containing `GoogleCLI.py`.

If dependencies are missing even with venv, install them using the venv's pip: 
`pip install google-auth google-auth-oauthlib google-api-python-client python-dotenv beautifulsoup4 html2text`

## Gmail — Reading & Searching

| Command | Purpose |
|---|---|
| `gmail list` | List recent messages |
| `gmail count` | Count messages |
| `gmail search` | Search with Gmail query syntax |
| `gmail read-by-id` | Read full email by message ID |
| `gmail get-by-subject` | Find email by subject |
| `gmail list-by-sender` | List emails from a sender |
| `gmail unique-senders` | List unique senders |
| `gmail analyze` | Mailbox analytics summary |

**Examples** (all use the base command template above, showing only the `<service> <command> <flags>` part):

```
gmail list --max-results 5 --label INBOX --read-status all
gmail count --label INBOX --read-status unread
gmail search --query "from:alerts@example.com newer_than:7d" --max-results 50 --label ALL --read-status all
gmail search --query "after:2026/03/19 before:2026/03/20" --max-results 50 --label INBOX --read-status all
gmail read-by-id --id "<MESSAGE_ID>" --render-html
gmail get-by-subject --subject "Invoice" --label INBOX --read-status all --render-html
gmail list-by-sender --sender "example@domain.com" --max-results 10 --label INBOX --read-status all
gmail unique-senders --max-scan 600 --label INBOX --read-status all
gmail analyze --label INBOX --read-status all --query "newer_than:30d" --max-scan 0 --top 20
```

Common flags for read commands: `--label` (INBOX, SENT, SPAM, TRASH, STARRED, IMPORTANT, ALL), `--read-status` (all, unread, read).

The output of `list`, `search`, and `read-by-id` includes a `Message-ID` field for each email. This is the RFC Message-ID header used for thread replies (see below).

## Gmail — Sending Emails (SMTP)

SMTP credentials (`EMAIL_USER` and `EMAIL_PASSWORD`) are loaded automatically from the `.env` file at the root of the project or `<path_to_.env>`. There are no command-line flags for credentials — they must be in the `.env` file.

### Send command structure

```
gmail send-smtp --subject "<subject>" --body "<body>" --to "<email>" [--attachment "<path>"] [--html] [--in-reply-to "<Message-ID>"]
```

- `--subject` (required): email subject
- `--body` (required): email body text
- `--to` (required): one or more recipient emails
- `--attachment`: file path to attach (can be repeated for multiple files)
- `--html`: send body as HTML instead of plain text
- `--in-reply-to`: Message-ID header value for thread replies (see below)

**Note:** `send-smtp` does NOT need `--token-path` — it uses the SMTP credentials from `.env`.

### Thread reply workflow

To reply within an existing email thread:

1. Find the email using `gmail search`, `gmail list`, or `gmail read-by-id` — these all include a `Message-ID` field in their output.
2. Copy the `Message-ID` value (looks like `<abc123@mail.gmail.com>`).
3. Send the reply:

```
gmail send-smtp --subject "Re: Original Subject" --body "Reply text" --to "person@domain.com" --in-reply-to "<abc123@mail.gmail.com>"
```

4. Gmail will automatically group the reply into the same conversation thread.

## Drive

```
drive list --max-results 10
drive download --file-name "report.pdf" --destination-path "<path_to_downloads_folder>"
```

## Calendar

```
calendar list-upcoming --max-results 5
calendar create-event --summary "Meeting" --start-dt "2026-03-20T10:00:00-03:00" --end-dt "2026-03-20T11:00:00-03:00"
```

Optional flags for `create-event`: `--location`, `--description`, `--attendee` (repeatable), `--reminders-json`, `--extra-fields-json`.

## Output Modes

- Global output format: `--format text|json|csv|ndjson` (default: `text`).
- Optional file output: `--output-file <path_to_output_file.json>`.
- In `json`/`ndjson`, scalar responses (e.g. `gmail count`) are emitted as JSON numbers.
- In `csv`, nested payloads (e.g. `gmail analyze`) are flattened into tabular rows with a `section` column.

Example with format and output file:

```
--format json --output-file "<path_to_temp_dir>/inbox_summary.json" gmail analyze --label INBOX --max-scan 0 --top 20
```

## Auth

- `token.json` = OAuth token cache (refresh/access token + granted scopes).
- "Client config" = OAuth app config JSON (only needed when creating a new token or requesting new scopes).
- If no scope override is provided, the CLI reads scopes from `token.json` and selects the ones for the requested service.
- Prefer `--scope <scope>` (repeat for multiples) over `--scopes`.

If OAuth client config is needed, provide one of: `--client-config-file`, `--client-config-json`, `GOOGLE_CLIENT_SECRET_FILE`, or `GOOGLE_CLIENT_SECRET_JSON`.

## Operating Rules

1. **Always use the venv Python and --token-path** as described at the top.
2. **Never pass credentials via command line.** SMTP credentials are loaded automatically from the `.env` file.
3. Default to read-only commands first.
4. Always confirm with the user before state-changing actions (`gmail send-smtp`, `drive download`, `calendar create-event`).
5. When replying in a thread, always use `--in-reply-to` with the correct `Message-ID` from the original email, and prefix the subject with `Re:`.
6. For broad mailbox requests, prefer `gmail analyze` → `gmail search`/`gmail list` → `gmail read-by-id` (progressively deeper detail).

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `SMTP credentials missing` | `.env` file not found or missing `EMAIL_USER`/`EMAIL_PASSWORD` | Ensure `.env` exists at `<path_to_.env>` with both vars set |
| `Client config not found` | Token path not being used, or token lacks required scopes | Pass `--token-path` explicitly. If scope issue, provide OAuth app config and re-consent |
| `ModuleNotFoundError` / `Missing ...` | Not using the venv Python | Use the full path to your virtual environment Python executable instead of simply `python` |
| `--output-file` fails | Destination directory not writable | Ensure the directory exists and is writable |

Check token scopes: `<path_to_venv_python> -c "import json; print(json.load(open(r'<path_to_token.json>')).get('scopes'))"`
