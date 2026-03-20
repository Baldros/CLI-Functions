#!/usr/bin/env python3
"""Terminal CLI for Gmail, Google Drive, and Google Calendar."""

from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import io
import json
import os
import pathlib
import smtplib
import sys
from collections import Counter
from email import encoders
from email.utils import parseaddr
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Iterable


CLI_FUNCTIONS_ROOT = pathlib.Path("/home/techbrain/CLI-Functions")
DEFAULT_DOTENV_PATH = CLI_FUNCTIONS_ROOT / ".env"
GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
GMAIL_MODIFY_SCOPE = "https://www.googleapis.com/auth/gmail.modify"
GMAIL_FULL_SCOPE = "https://mail.google.com/"
DRIVE_READONLY_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
CALENDAR_READONLY_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"
CALENDAR_EVENTS_SCOPE = "https://www.googleapis.com/auth/calendar.events"
CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar"
DEFAULT_TOKEN_PATH = pathlib.Path.home() / ".codex" / "token" / "google_token.json"
PROJECT_TOKEN_PATH = CLI_FUNCTIONS_ROOT / "google" / "token" / "token.json"
READ_STATUS_CHOICES = ("all", "unread", "read")
LABEL_CHOICES = ("INBOX", "SPAM", "SENT", "TRASH", "STARRED", "IMPORTANT", "ALL")
OUTPUT_FORMAT_CHOICES = ("text", "json", "csv", "ndjson")
DEFAULT_TOP_LIMIT = 20

GMAIL_ANALYZE_CATEGORY_KEYWORDS = {
    "Career and jobs": (
        "linkedin",
        "job",
        "jobboard",
        "job alert",
        "application",
        "recruit",
        "catho",
        "jobleads",
        "gupy",
    ),
    "Tech and development": (
        "github",
        "gitlab",
        "devpost",
        "kaggle",
        "nvidia",
        "developer",
        "api",
        "deploy",
    ),
    "Education and courses": (
        "course",
        "certificate",
        "learning",
        "cambly",
        "udemy",
        "alura",
        "coursera",
        "dio",
    ),
    "Finance and purchases": (
        "invoice",
        "bill",
        "payment",
        "tax invoice",
        "order",
        "receipt",
    ),
    "Security and access": (
        "code",
        "verification",
        "otp",
        "2fa",
        "login",
        "security",
        "signin",
        "password",
    ),
    "Social and community": (
        "tiktok",
        "twitch",
        "community",
        "academia-mail",
        "discord",
    ),
    "Newsletters and content": (
        "newsletter",
        "digest",
        "medium",
        "news",
        "substack",
        "estantevirtual",
        "g1",
    ),
}

GMAIL_ANALYZE_CATEGORY_PRIORITY = (
    "Security and access",
    "Finance and purchases",
    "Career and jobs",
    "Education and courses",
    "Tech and development",
    "Social and community",
    "Newsletters and content",
)


def load_cli_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise RuntimeError(
            "Missing python-dotenv. Install with: pip install python-dotenv"
        ) from exc

    load_dotenv(dotenv_path=DEFAULT_DOTENV_PATH, override=False)


def _import_google_auth():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise RuntimeError(
            "Missing Google auth dependencies. Install with: "
            "pip install google-auth google-auth-oauthlib google-api-python-client"
        ) from exc
    return Request, Credentials, InstalledAppFlow


def _import_google_discovery():
    try:
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Missing google-api-python-client. Install with: "
            "pip install google-api-python-client"
        ) from exc
    return build


def _import_media_downloader():
    try:
        from googleapiclient.http import MediaIoBaseDownload
    except ImportError as exc:
        raise RuntimeError(
            "Missing google-api-python-client. Install with: "
            "pip install google-api-python-client"
        ) from exc
    return MediaIoBaseDownload


def _load_client_config_from_env() -> dict[str, Any] | None:
    raw = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GOOGLE_CLIENT_SECRET_JSON is not valid JSON.") from exc


def _load_client_config_from_file(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Client config file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in client config file: {path}") from exc


def _load_scopes_from_token_file(token_path: pathlib.Path) -> set[str]:
    try:
        payload = json.loads(token_path.read_text(encoding="utf-8"))
    except Exception:
        return set()

    raw_scopes = payload.get("scopes")
    if isinstance(raw_scopes, list):
        return {scope for scope in raw_scopes if isinstance(scope, str) and scope}

    raw_scope = payload.get("scope")
    if isinstance(raw_scope, str):
        return {scope for scope in raw_scope.split() if scope}

    return set()


def resolve_client_config(args: argparse.Namespace) -> dict[str, Any]:
    if args.client_config_json:
        try:
            return json.loads(args.client_config_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError("--client-config-json must be valid JSON.") from exc

    env_json = _load_client_config_from_env()
    if env_json:
        return env_json

    config_file = pathlib.Path(args.client_config_file).expanduser() if args.client_config_file else None
    if not config_file and os.getenv("GOOGLE_CLIENT_SECRET_FILE"):
        config_file = pathlib.Path(os.getenv("GOOGLE_CLIENT_SECRET_FILE", "")).expanduser()
    if config_file:
        return _load_client_config_from_file(config_file)

    raise RuntimeError(
        "Client config not found. Provide one of: "
        "--client-config-json, --client-config-file, GOOGLE_CLIENT_SECRET_JSON, "
        "or GOOGLE_CLIENT_SECRET_FILE."
    )


def get_credentials(
    token_path: pathlib.Path,
    scopes: list[str],
    client_config: dict[str, Any] | None = None,
):
    Request, Credentials, InstalledAppFlow = _import_google_auth()

    creds = None
    if token_path.exists():
        token_scopes = _load_scopes_from_token_file(token_path)
        if token_scopes and not _required_scopes_satisfied(scopes, token_scopes):
            creds = None
        else:
            # Keep token's granted scopes to avoid narrowing token metadata on refresh/save.
            requested = list(token_scopes) if token_scopes else scopes
            creds = Credentials.from_authorized_user_file(str(token_path), requested)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if client_config is None:
                raise RuntimeError(
                    "Client config not found. Provide one of: "
                    "--client-config-json, --client-config-file, GOOGLE_CLIENT_SECRET_JSON, "
                    "or GOOGLE_CLIENT_SECRET_FILE."
                )
            flow = InstalledAppFlow.from_client_config(client_config, scopes)
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds


def _scope_implies(granted: str, required: str) -> bool:
    if granted == required:
        return True

    implication_map = {
        GMAIL_FULL_SCOPE: {GMAIL_MODIFY_SCOPE, GMAIL_READONLY_SCOPE},
        GMAIL_MODIFY_SCOPE: {GMAIL_READONLY_SCOPE},
        DRIVE_SCOPE: {DRIVE_READONLY_SCOPE},
        CALENDAR_SCOPE: {CALENDAR_READONLY_SCOPE, CALENDAR_EVENTS_SCOPE},
        CALENDAR_EVENTS_SCOPE: {CALENDAR_READONLY_SCOPE},
    }
    return required in implication_map.get(granted, set())


def _required_scopes_satisfied(required_scopes: list[str], granted_scopes: set[str]) -> bool:
    for required in required_scopes:
        if any(_scope_implies(granted, required) for granted in granted_scopes):
            continue
        return False
    return True


def resolve_token_path(args: argparse.Namespace) -> pathlib.Path:
    if args.token_path:
        return pathlib.Path(args.token_path).expanduser()

    env_token = os.getenv("GOOGLE_TOKEN_PATH")
    if env_token:
        return pathlib.Path(env_token).expanduser()

    if DEFAULT_TOKEN_PATH.exists():
        return DEFAULT_TOKEN_PATH

    if PROJECT_TOKEN_PATH.exists():
        return PROJECT_TOKEN_PATH

    return DEFAULT_TOKEN_PATH


def resolve_scopes_for_command(args: argparse.Namespace) -> list[str]:
    if args.scopes:
        return args.scopes
    if getattr(args, "scope_items", None):
        return args.scope_items

    token_path = resolve_token_path(args)
    if token_path.exists():
        token_scopes = _load_scopes_from_token_file(token_path)
        service_scopes = [
            scope for scope in token_scopes if _scope_matches_service(args.service, scope)
        ]
        if service_scopes:
            return sorted(service_scopes)

    if args.service == "gmail":
        return [GMAIL_READONLY_SCOPE]
    if args.service == "drive":
        return [DRIVE_READONLY_SCOPE]
    if args.service == "calendar":
        if args.calendar_cmd == "create-event":
            return [CALENDAR_EVENTS_SCOPE]
        return [CALENDAR_READONLY_SCOPE]
    return []


def _scope_matches_service(service: str | None, scope: str) -> bool:
    if service == "gmail":
        return scope.startswith("https://www.googleapis.com/auth/gmail") or scope == GMAIL_FULL_SCOPE
    if service == "drive":
        return scope.startswith("https://www.googleapis.com/auth/drive")
    if service == "calendar":
        return scope.startswith("https://www.googleapis.com/auth/calendar")
    return False


def get_service(args: argparse.Namespace, api_name: str, version: str, scopes: list[str]):
    token_path = resolve_token_path(args)
    try:
        creds = get_credentials(token_path=token_path, scopes=scopes)
    except RuntimeError as exc:
        if "Client config not found" not in str(exc):
            raise
        client_config = resolve_client_config(args)
        creds = get_credentials(token_path=token_path, client_config=client_config, scopes=scopes)
    build = _import_google_discovery()
    return build(api_name, version, credentials=creds)


def _build_gmail_query_params(
    label: str = "INBOX",
    read_status: str = "all",
    extra_query: str = "",
) -> tuple[list[str] | None, str | None]:
    query_parts = []
    if read_status == "unread":
        query_parts.append("is:unread")
    elif read_status == "read":
        query_parts.append("is:read")
    if extra_query:
        query_parts.append(extra_query)

    query = " ".join(query_parts) if query_parts else None
    label_ids = None if label.upper() == "ALL" else [label.upper()]
    return label_ids, query


def _decode_b64(data: str) -> str:
    if not data:
        return ""
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="ignore")


def _extract_message_content(payload: dict[str, Any]) -> str:
    parts = payload.get("parts", [])
    if not parts:
        return _decode_b64(payload.get("body", {}).get("data", ""))

    for mime in ("text/html", "text/plain"):
        for part in parts:
            if part.get("mimeType") == mime:
                return _decode_b64(part.get("body", {}).get("data", ""))

    for part in parts:
        nested = part.get("parts")
        if nested:
            found = _extract_message_content(part)
            if found:
                return found

    return _decode_b64(parts[0].get("body", {}).get("data", ""))


def render_html_terminal(html_content: str) -> str:
    try:
        import html2text

        return html2text.html2text(html_content)
    except Exception:
        try:
            from bs4 import BeautifulSoup

            return BeautifulSoup(html_content, "html.parser").get_text()
        except Exception:
            return html_content


def _merge_gmail_query(base_query: str | None, extra_query: str | None) -> str | None:
    extra = (extra_query or "").strip()
    if base_query and extra:
        return f"{base_query} {extra}".strip()
    if base_query:
        return base_query
    return extra or None


def _get_header_value(headers: list[dict[str, Any]], name: str, default: str = "") -> str:
    lname = name.lower()
    for header in headers:
        if header.get("name", "").lower() == lname:
            return header.get("value", default)
    return default


def _classify_gmail_message(from_addr: str, subject: str) -> str:
    haystack = f"{from_addr} {subject}".lower()
    for category in GMAIL_ANALYZE_CATEGORY_PRIORITY:
        if any(keyword in haystack for keyword in GMAIL_ANALYZE_CATEGORY_KEYWORDS[category]):
            return category
    return "Outros"


def gmail_analyze_messages(
    service,
    label: str,
    read_status: str,
    query: str,
    max_scan: int,
    top: int,
) -> dict[str, Any]:
    label_ids, base_query = _build_gmail_query_params(label, read_status)
    merged_query = _merge_gmail_query(base_query, query)

    labels_resp = service.users().labels().list(userId="me").execute()
    label_name_map = {
        item.get("id", ""): item.get("name", item.get("id", ""))
        for item in labels_resp.get("labels", [])
        if item.get("id")
    }

    sender_counts: Counter[str] = Counter()
    domain_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()

    scanned = 0
    fetch_errors = 0
    unread = 0
    page_token = None
    scan_limit = max_scan if max_scan and max_scan > 0 else None

    while True:
        if scan_limit is not None and scanned >= scan_limit:
            break

        remaining = scan_limit - scanned if scan_limit is not None else 500
        page_size = min(500, remaining) if scan_limit is not None else 500
        params: dict[str, Any] = {"userId": "me", "maxResults": page_size}
        if label_ids:
            params["labelIds"] = label_ids
        if merged_query:
            params["q"] = merged_query
        if page_token:
            params["pageToken"] = page_token

        results = service.users().messages().list(**params).execute()
        messages = results.get("messages", [])
        if not messages:
            break

        for msg in messages:
            try:
                detail = service.users().messages().get(
                    userId="me",
                    id=msg["id"],
                    format="metadata",
                    metadataHeaders=["Subject", "From"],
                ).execute()
            except Exception:
                fetch_errors += 1
                continue

            scanned += 1
            msg_labels = detail.get("labelIds", [])
            for lbl in msg_labels:
                label_counts[lbl] += 1
            if "UNREAD" in msg_labels:
                unread += 1

            headers = detail.get("payload", {}).get("headers", [])
            subject = _get_header_value(headers, "Subject", "(no subject)")
            from_addr = _get_header_value(headers, "From", "(unknown)")

            display_name, email_addr = parseaddr(from_addr)
            email_addr = email_addr.lower().strip()
            if email_addr and display_name:
                sender_key = f"{display_name} <{email_addr}>"
            elif email_addr:
                sender_key = email_addr
            else:
                sender_key = from_addr.strip() or "(unknown)"
            sender_counts[sender_key] += 1

            if "@" in email_addr:
                domain_counts[email_addr.split("@", 1)[1]] += 1

            category = _classify_gmail_message(from_addr, subject)
            category_counts[category] += 1

            if scan_limit is not None and scanned >= scan_limit:
                break

        page_token = results.get("nextPageToken")
        if not page_token:
            break

    by_label = {
        label_name_map.get(label_id, label_id): count
        for label_id, count in label_counts.most_common()
    }
    by_category = {name: count for name, count in category_counts.most_common()}
    top_senders = [{"sender": sender, "count": count} for sender, count in sender_counts.most_common(top)]
    top_domains = [{"domain": domain, "count": count} for domain, count in domain_counts.most_common(top)]

    return {
        "generated_at": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
        "filters": {
            "label": label,
            "read_status": read_status,
            "query": query.strip() or None,
            "max_scan": scan_limit,
        },
        "total": scanned,
        "unread": unread,
        "fetch_errors": fetch_errors,
        "by_label": by_label,
        "by_category": by_category,
        "top_senders": top_senders,
        "top_domains": top_domains,
    }


def gmail_list_messages(service, max_results: int, label: str, read_status: str) -> str:
    label_ids, query = _build_gmail_query_params(label, read_status)
    list_params: dict[str, Any] = {"userId": "me", "maxResults": max_results}
    if label_ids:
        list_params["labelIds"] = label_ids
    if query:
        list_params["q"] = query

    results = service.users().messages().list(**list_params).execute()
    messages = results.get("messages", [])
    if not messages:
        return f"No emails found in '{label}'."

    output_lines = [f"Emails in '{label}' ({read_status}) - {len(messages)} found:", ""]
    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()
        headers = detail.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
        from_addr = next((h["value"] for h in headers if h["name"] == "From"), "(unknown)")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "(no date)")
        output_lines.extend(
            [
                f"- ID: {msg['id']}",
                f"  From: {from_addr}",
                f"  Subject: {subject}",
                f"  Date: {date}",
                "",
            ]
        )

    return "\n".join(output_lines).strip()


def gmail_count_messages(service, label: str, read_status: str) -> int:
    label_ids, query = _build_gmail_query_params(label, read_status)
    count = 0
    page_token = None

    while True:
        params: dict[str, Any] = {"userId": "me", "maxResults": 500}
        if page_token:
            params["pageToken"] = page_token
        if label_ids:
            params["labelIds"] = label_ids
        if query:
            params["q"] = query
        results = service.users().messages().list(**params).execute()
        messages = results.get("messages", [])
        count += len(messages)
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    return count


def gmail_get_by_subject(
    service,
    subject: str,
    label: str,
    read_status: str,
    render_html: bool,
) -> str:
    label_ids, query = _build_gmail_query_params(label, read_status, f"subject:{subject}")
    params: dict[str, Any] = {"userId": "me", "maxResults": 10}
    if label_ids:
        params["labelIds"] = label_ids
    if query:
        params["q"] = query

    results = service.users().messages().list(**params).execute()
    messages = results.get("messages", [])
    if not messages:
        return f"No emails found with subject '{subject}' in '{label}'."

    if len(messages) > 1:
        lines = [
            f"{len(messages)} emails found with subject '{subject}'.",
            "Use `gmail read-by-id --id <MESSAGE_ID>` to read the specific email.",
            "",
        ]
        for msg in messages:
            detail = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            ).execute()
            headers = detail.get("payload", {}).get("headers", [])
            subject_hdr = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
            from_addr = next((h["value"] for h in headers if h["name"] == "From"), "(unknown)")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "(no date)")
            lines.extend(
                [
                    f"- ID: {msg['id']}",
                    f"  From: {from_addr}",
                    f"  Subject: {subject_hdr}",
                    f"  Date: {date}",
                    "",
                ]
            )
        return "\n".join(lines).strip()

    msg_id = messages[0]["id"]
    return gmail_read_by_id(service=service, message_id=msg_id, render_html=render_html)


def gmail_search_messages(
    service,
    query: str,
    max_results: int,
    label: str,
    read_status: str,
) -> str:
    label_ids, base_query = _build_gmail_query_params(label, read_status)
    q = _merge_gmail_query(base_query, query)
    messages: list[dict[str, Any]] = []
    page_token = None

    while len(messages) < max_results:
        remaining = max_results - len(messages)
        params: dict[str, Any] = {"userId": "me", "maxResults": min(500, remaining)}
        if label_ids:
            params["labelIds"] = label_ids
        if q:
            params["q"] = q
        if page_token:
            params["pageToken"] = page_token

        results = service.users().messages().list(**params).execute()
        chunk = results.get("messages", [])
        if not chunk:
            break
        messages.extend(chunk)
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    if not messages:
        return f"No emails found for query: {query}"

    lines = [f"Results for query: {query}", f"{len(messages)} email(s) found:", ""]
    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()
        headers = detail.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
        from_addr = next((h["value"] for h in headers if h["name"] == "From"), "(unknown)")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "(no date)")
        snippet = detail.get("snippet", "")
        lines.extend(
            [
                f"- ID: {msg['id']}",
                f"  Thread: {msg.get('threadId', '')}",
                f"  From: {from_addr}",
                f"  Subject: {subject}",
                f"  Date: {date}",
                f"  Snippet: {snippet}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def gmail_read_by_id(service, message_id: str, render_html: bool) -> str:
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = msg.get("payload", {}).get("headers", [])
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
    from_addr = next((h["value"] for h in headers if h["name"] == "From"), "(unknown)")
    date = next((h["value"] for h in headers if h["name"] == "Date"), "(no date)")
    to_addr = next((h["value"] for h in headers if h["name"] == "To"), "(unknown)")

    content = _extract_message_content(msg.get("payload", {}))
    if render_html:
        content = render_html_terminal(content)
    content = content or "(empty content)"

    return "\n".join(
        [
            f"ID: {message_id}",
            f"Thread: {msg.get('threadId', '')}",
            f"From: {from_addr}",
            f"To: {to_addr}",
            f"Subject: {subject}",
            f"Date: {date}",
            "",
            content,
        ]
    )


def gmail_list_by_sender(
    service,
    sender: str,
    max_results: int,
    label: str,
    read_status: str,
) -> str:
    label_ids, query = _build_gmail_query_params(label, read_status, f"from:{sender}")
    params: dict[str, Any] = {"userId": "me", "maxResults": max_results}
    if label_ids:
        params["labelIds"] = label_ids
    if query:
        params["q"] = query
    results = service.users().messages().list(**params).execute()
    messages = results.get("messages", [])
    if not messages:
        return f"No emails found from sender '{sender}' in '{label}'."

    lines = [f"Emails from '{sender}' in '{label}' ({read_status}) - {len(messages)} found:", ""]
    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()
        headers = detail.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
        from_addr = next((h["value"] for h in headers if h["name"] == "From"), "(unknown)")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "(no date)")
        lines.extend(
            [
                f"- ID: {msg['id']}",
                f"  From: {from_addr}",
                f"  Subject: {subject}",
                f"  Date: {date}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def gmail_list_unique_senders(
    service,
    label: str,
    read_status: str,
    max_scan: int,
) -> str:
    label_ids, query = _build_gmail_query_params(label, read_status)
    messages: list[dict[str, Any]] = []
    page_token = None

    while len(messages) < max_scan:
        remaining = max_scan - len(messages)
        params: dict[str, Any] = {"userId": "me", "maxResults": min(500, remaining)}
        if label_ids:
            params["labelIds"] = label_ids
        if query:
            params["q"] = query
        if page_token:
            params["pageToken"] = page_token

        results = service.users().messages().list(**params).execute()
        chunk = results.get("messages", [])
        if not chunk:
            break
        messages.extend(chunk)
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    if not messages:
        return f"No emails found in '{label}'."

    senders = []
    for msg in messages:
        try:
            detail = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From"],
            ).execute()
            headers = detail.get("payload", {}).get("headers", [])
            from_addr = next((h["value"] for h in headers if h["name"] == "From"), None)
            if from_addr:
                senders.append(from_addr)
        except Exception:
            continue

    if not senders:
        return "Could not extract senders from emails."

    sender_counts = Counter(senders).most_common()
    lines = [f"Unique senders in '{label}' ({read_status}) - {len(sender_counts)} found:", ""]
    for sender, count in sender_counts:
        lines.append(f"- [{count}x] {sender}")
    return "\n".join(lines).strip()


def smtp_send_email(
    subject: str,
    body: str,
    recipients: Iterable[str],
    sender: str,
    password: str,
    attachments: list[str] | None,
    html: bool,
) -> str:
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["Subject"] = subject
    recipients = list(recipients)
    msg["To"] = ", ".join(recipients)

    body_type = "html" if html else "plain"
    msg.attach(MIMEText(body, body_type, "utf-8"))

    if attachments:
        for file_path in attachments:
            if not os.path.exists(file_path):
                print(f"Warning: file not found: {file_path}", file=sys.stderr)
                continue
            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file_path)}",
            )
            msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
    return "Email sent successfully."


def drive_list_files(service, max_results: int) -> str:
    results = service.files().list(
        pageSize=max_results,
        fields="files(id, name, mimeType)",
    ).execute()
    files = results.get("files", [])
    if not files:
        return "No files found."
    lines = ["Drive files:", ""]
    for item in files:
        lines.append(f"- {item['name']} (ID: {item['id']}, type: {item['mimeType']})")
    return "\n".join(lines)


def drive_download_file(service, file_name: str, destination_path: str | None) -> str:
    query = f"name = '{file_name}'"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get("files", [])
    if not items:
        return f"File '{file_name}' not found in Drive."

    file_id = items[0]["id"]
    target_dir = pathlib.Path(destination_path).expanduser() if destination_path else pathlib.Path.cwd()
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / file_name

    MediaIoBaseDownload = _import_media_downloader()
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(file_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"Download: {pct}%")

    return f"File saved at: {file_path}"


def calendar_list_upcoming(service, max_results: int) -> str:
    now = dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")
    events = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute().get("items", [])

    if not events:
        return "No upcoming events found."

    lines = ["Upcoming events:", ""]
    for event in events:
        start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
        summary = event.get("summary", "(no title)")
        lines.append(f"- {start} - {summary}")
    return "\n".join(lines)


def calendar_create_event(
    service,
    summary: str,
    start_dt: str,
    end_dt: str,
    location: str | None,
    description: str | None,
    attendees: list[str],
    reminders_json: str | None,
    extra_fields_json: str | None,
) -> str:
    event_body: dict[str, Any] = {
        "summary": summary,
        "start": {"dateTime": start_dt},
        "end": {"dateTime": end_dt},
    }
    if location:
        event_body["location"] = location
    if description:
        event_body["description"] = description
    if attendees:
        event_body["attendees"] = [{"email": email} for email in attendees]
    if reminders_json:
        event_body["reminders"] = json.loads(reminders_json)
    if extra_fields_json:
        event_body.update(json.loads(extra_fields_json))

    created = service.events().insert(
        calendarId="primary",
        body=event_body,
        sendUpdates="all",
    ).execute()
    return f"Event created: {created.get('htmlLink', '(no link)')}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Google CLI for Gmail, Drive, and Calendar.",
    )
    parser.add_argument(
        "--token-path",
        default=None,
        help=(
            "Path for OAuth token cache. Resolution order when omitted: "
            "GOOGLE_TOKEN_PATH env, "
            f"{DEFAULT_TOKEN_PATH} (if exists), "
            f"{PROJECT_TOKEN_PATH} (if exists), else {DEFAULT_TOKEN_PATH}."
        ),
    )
    parser.add_argument(
        "--client-config-file",
        help="Path to Google OAuth client config JSON file.",
    )
    parser.add_argument(
        "--client-config-json",
        help="Inline Google OAuth client config JSON string.",
    )
    parser.add_argument(
        "--scopes",
        nargs="+",
        help=(
            "Optional OAuth scopes override. If omitted, the CLI uses "
            "minimal command-specific scopes."
        ),
    )
    parser.add_argument(
        "--scope",
        action="append",
        dest="scope_items",
        help="Optional single scope override. Repeat --scope for multiple scopes.",
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=OUTPUT_FORMAT_CHOICES,
        default="text",
        help="Output format. Default: text.",
    )
    parser.add_argument(
        "--output-file",
        help="Optional file path to write command output.",
    )

    top = parser.add_subparsers(dest="service", required=True)

    gmail = top.add_parser("gmail", help="Gmail commands")
    gmail_sub = gmail.add_subparsers(dest="gmail_cmd", required=True)

    g_list = gmail_sub.add_parser("list", help="List recent messages")
    g_list.add_argument("--max-results", type=int, default=5)
    g_list.add_argument("--label", choices=LABEL_CHOICES, default="INBOX")
    g_list.add_argument("--read-status", choices=READ_STATUS_CHOICES, default="all")

    g_count = gmail_sub.add_parser("count", help="Count messages")
    g_count.add_argument("--label", choices=LABEL_CHOICES, default="INBOX")
    g_count.add_argument("--read-status", choices=READ_STATUS_CHOICES, default="all")

    g_subject = gmail_sub.add_parser("get-by-subject", help="Get first email body by subject")
    g_subject.add_argument("--subject", required=True)
    g_subject.add_argument("--label", choices=LABEL_CHOICES, default="INBOX")
    g_subject.add_argument("--read-status", choices=READ_STATUS_CHOICES, default="all")
    g_subject.add_argument("--render-html", action="store_true")

    g_sender = gmail_sub.add_parser("list-by-sender", help="List emails by sender")
    g_sender.add_argument("--sender", required=True)
    g_sender.add_argument("--max-results", type=int, default=10)
    g_sender.add_argument("--label", choices=LABEL_CHOICES, default="INBOX")
    g_sender.add_argument("--read-status", choices=READ_STATUS_CHOICES, default="all")

    g_unique = gmail_sub.add_parser("unique-senders", help="List unique senders")
    g_unique.add_argument("--max-scan", type=int, default=100)
    g_unique.add_argument("--label", choices=LABEL_CHOICES, default="INBOX")
    g_unique.add_argument("--read-status", choices=READ_STATUS_CHOICES, default="all")

    g_send = gmail_sub.add_parser("send-smtp", help="Send email via Gmail SMTP")
    g_send.add_argument("--subject", required=True)
    g_send.add_argument("--body", required=True)
    g_send.add_argument("--to", nargs="+", required=True)
    g_send.add_argument("--from-email", dest="from_email", help="Sender Gmail address")
    g_send.add_argument("--password", help="Gmail app password")
    g_send.add_argument("--attachment", action="append", default=[])
    g_send.add_argument("--html", action="store_true")

    g_search = gmail_sub.add_parser("search", help="Search emails using Gmail query syntax")
    g_search.add_argument("--query", required=True, help="Gmail query (from:, subject:, newer_than:, etc.)")
    g_search.add_argument("--max-results", type=int, default=10)
    g_search.add_argument("--label", choices=LABEL_CHOICES, default="ALL")
    g_search.add_argument("--read-status", choices=READ_STATUS_CHOICES, default="all")

    g_read = gmail_sub.add_parser("read-by-id", help="Read a specific email by message ID")
    g_read.add_argument("--id", required=True, dest="message_id")
    g_read.add_argument("--render-html", action="store_true")

    g_analyze = gmail_sub.add_parser("analyze", help="Analyze mailbox and return summary metrics")
    g_analyze.add_argument("--label", choices=LABEL_CHOICES, default="ALL")
    g_analyze.add_argument("--read-status", choices=READ_STATUS_CHOICES, default="all")
    g_analyze.add_argument("--query", default="", help="Optional Gmail query filter.")
    g_analyze.add_argument(
        "--max-scan",
        type=int,
        default=0,
        help="Limit scanned messages. Use 0 to scan all matching messages.",
    )
    g_analyze.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP_LIMIT,
        help=f"Number of top senders/domains to return. Default: {DEFAULT_TOP_LIMIT}.",
    )

    drive = top.add_parser("drive", help="Google Drive commands")
    drive_sub = drive.add_subparsers(dest="drive_cmd", required=True)
    d_list = drive_sub.add_parser("list", help="List files")
    d_list.add_argument("--max-results", type=int, default=10)
    d_download = drive_sub.add_parser("download", help="Download file by exact name")
    d_download.add_argument("--file-name", required=True)
    d_download.add_argument("--destination-path")

    calendar = top.add_parser("calendar", help="Google Calendar commands")
    cal_sub = calendar.add_subparsers(dest="calendar_cmd", required=True)
    c_list = cal_sub.add_parser("list-upcoming", help="List upcoming events")
    c_list.add_argument("--max-results", type=int, default=5)
    c_create = cal_sub.add_parser("create-event", help="Create event in primary calendar")
    c_create.add_argument("--summary", required=True)
    c_create.add_argument("--start-dt", required=True, help="ISO 8601 datetime")
    c_create.add_argument("--end-dt", required=True, help="ISO 8601 datetime")
    c_create.add_argument("--location")
    c_create.add_argument("--description")
    c_create.add_argument("--attendee", action="append", default=[])
    c_create.add_argument("--reminders-json")
    c_create.add_argument("--extra-fields-json")

    return parser


def _print_and_exit(message: str, code: int = 0) -> int:
    output = sys.stderr if code else sys.stdout
    print(message, file=output)
    return code


def _is_scalar_value(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _to_json_compatible(payload: Any) -> Any:
    if isinstance(payload, (dict, list, int, float, bool)) or payload is None:
        return payload
    return {"message": str(payload)}


def _to_cell_value(value: Any) -> Any:
    if _is_scalar_value(value):
        return value
    return json.dumps(value, ensure_ascii=False)


def _to_tabular_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        if all(isinstance(item, dict) for item in payload):
            return [{key: _to_cell_value(value) for key, value in item.items()} for item in payload]
        return [{"index": idx, "value": _to_cell_value(item)} for idx, item in enumerate(payload)]

    if isinstance(payload, dict):
        rows: list[dict[str, Any]] = []
        scalar_items = []
        for key, value in payload.items():
            if _is_scalar_value(value):
                scalar_items.append((key, value))
                continue
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    rows.append({"section": key, "key": subkey, "value": _to_cell_value(subvalue)})
                continue
            if isinstance(value, list):
                if all(isinstance(item, dict) for item in value):
                    for item in value:
                        row = {"section": key}
                        row.update({item_key: _to_cell_value(item_value) for item_key, item_value in item.items()})
                        rows.append(row)
                else:
                    for idx, item in enumerate(value):
                        rows.append({"section": key, "index": idx, "value": _to_cell_value(item)})
                continue
            rows.append({"section": key, "value": _to_cell_value(value)})

        for key, value in scalar_items:
            rows.append({"section": "summary", "key": key, "value": _to_cell_value(value)})
        return rows

    return [{"value": _to_cell_value(payload)}]


def _render_csv(payload: Any) -> str:
    rows = _to_tabular_rows(payload)
    if not rows:
        return ""

    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({name: row.get(name, "") for name in fieldnames})
    return output_buffer.getvalue().rstrip("\n")


def _render_ndjson(payload: Any) -> str:
    if isinstance(payload, list):
        entries = payload
    else:
        entries = [payload]
    lines = [json.dumps(_to_json_compatible(entry), ensure_ascii=False) for entry in entries]
    return "\n".join(lines)


def _render_output(payload: Any, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(_to_json_compatible(payload), ensure_ascii=False, indent=2)
    if output_format == "csv":
        return _render_csv(payload)
    if output_format == "ndjson":
        return _render_ndjson(payload)

    if isinstance(payload, str):
        return payload
    if isinstance(payload, (int, float, bool)):
        return str(payload)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _emit_output(payload: Any, args: argparse.Namespace, code: int = 0) -> int:
    output_format = getattr(args, "output_format", "text")
    rendered = _render_output(payload, output_format)

    output = sys.stderr if code else sys.stdout
    print(rendered, file=output)

    output_file = getattr(args, "output_file", None)
    if output_file:
        out_path = pathlib.Path(output_file).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(f"{rendered}\n", encoding="utf-8")

    return code


def main(argv: list[str] | None = None) -> int:
    args: argparse.Namespace | None = None
    try:
        load_cli_env()
        parser = build_parser()
        args = parser.parse_args(argv)

        if args.service == "gmail":
            if args.gmail_cmd == "send-smtp":
                sender = args.from_email or os.getenv("EMAIL_USER")
                password = args.password or os.getenv("EMAIL_PASSWORD")
                if not sender or not password:
                    return _emit_output(
                        "SMTP credentials missing. Use --from-email/--password or EMAIL_USER/EMAIL_PASSWORD.",
                        args,
                        code=2,
                    )
                result = smtp_send_email(
                    subject=args.subject,
                    body=args.body,
                    recipients=args.to,
                    sender=sender,
                    password=password,
                    attachments=args.attachment,
                    html=args.html,
                )
                return _emit_output(result, args)

            service = get_service(
                args,
                "gmail",
                "v1",
                scopes=resolve_scopes_for_command(args),
            )
            if args.gmail_cmd == "list":
                return _emit_output(
                    gmail_list_messages(
                        service=service,
                        max_results=args.max_results,
                        label=args.label,
                        read_status=args.read_status,
                    ),
                    args,
                )
            if args.gmail_cmd == "count":
                total = gmail_count_messages(
                    service=service,
                    label=args.label,
                    read_status=args.read_status,
                )
                return _emit_output(total, args)
            if args.gmail_cmd == "get-by-subject":
                return _emit_output(
                    gmail_get_by_subject(
                        service=service,
                        subject=args.subject,
                        label=args.label,
                        read_status=args.read_status,
                        render_html=args.render_html,
                    ),
                    args,
                )
            if args.gmail_cmd == "list-by-sender":
                return _emit_output(
                    gmail_list_by_sender(
                        service=service,
                        sender=args.sender,
                        max_results=args.max_results,
                        label=args.label,
                        read_status=args.read_status,
                    ),
                    args,
                )
            if args.gmail_cmd == "unique-senders":
                return _emit_output(
                    gmail_list_unique_senders(
                        service=service,
                        label=args.label,
                        read_status=args.read_status,
                        max_scan=args.max_scan,
                    ),
                    args,
                )
            if args.gmail_cmd == "search":
                return _emit_output(
                    gmail_search_messages(
                        service=service,
                        query=args.query,
                        max_results=args.max_results,
                        label=args.label,
                        read_status=args.read_status,
                    ),
                    args,
                )
            if args.gmail_cmd == "read-by-id":
                return _emit_output(
                    gmail_read_by_id(
                        service=service,
                        message_id=args.message_id,
                        render_html=args.render_html,
                    ),
                    args,
                )
            if args.gmail_cmd == "analyze":
                if args.top <= 0:
                    return _emit_output("--top must be greater than zero.", args, code=2)
                if args.max_scan < 0:
                    return _emit_output("--max-scan cannot be negative.", args, code=2)
                return _emit_output(
                    gmail_analyze_messages(
                        service=service,
                        label=args.label,
                        read_status=args.read_status,
                        query=args.query,
                        max_scan=args.max_scan,
                        top=args.top,
                    ),
                    args,
                )

        if args.service == "drive":
            service = get_service(
                args,
                "drive",
                "v3",
                scopes=resolve_scopes_for_command(args),
            )
            if args.drive_cmd == "list":
                return _emit_output(drive_list_files(service, max_results=args.max_results), args)
            if args.drive_cmd == "download":
                return _emit_output(
                    drive_download_file(
                        service=service,
                        file_name=args.file_name,
                        destination_path=args.destination_path,
                    ),
                    args,
                )

        if args.service == "calendar":
            service = get_service(
                args,
                "calendar",
                "v3",
                scopes=resolve_scopes_for_command(args),
            )
            if args.calendar_cmd == "list-upcoming":
                return _emit_output(
                    calendar_list_upcoming(service, max_results=args.max_results),
                    args,
                )
            if args.calendar_cmd == "create-event":
                return _emit_output(
                    calendar_create_event(
                        service=service,
                        summary=args.summary,
                        start_dt=args.start_dt,
                        end_dt=args.end_dt,
                        location=args.location,
                        description=args.description,
                        attendees=args.attendee,
                        reminders_json=args.reminders_json,
                        extra_fields_json=args.extra_fields_json,
                    ),
                    args,
                )

        if args is not None:
            return _emit_output("Invalid command.", args, code=2)
        return _print_and_exit("Invalid command.", code=2)
    except Exception as exc:
        if args is not None:
            return _emit_output(f"Error: {exc}", args, code=1)
        return _print_and_exit(f"Error: {exc}", code=1)


if __name__ == "__main__":
    raise SystemExit(main())
