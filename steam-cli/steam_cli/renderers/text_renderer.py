from __future__ import annotations

from typing import Any

from steam_cli.models.result import CliResult


def _to_text(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return str(value)
    return "" if value is None else str(value)


def render_text(result: CliResult) -> str:
    lines: list[str] = []
    lines.append(
        f"ok={str(result.ok).lower()} source={result.source} official={str(result.official).lower()} experimental={str(result.experimental).lower()}"
    )

    if result.ok:
        for key, value in result.data.items():
            lines.append(f"{key}: {_to_text(value)}")
        for warning in result.warnings:
            lines.append(f"warning: {warning}")
    else:
        lines.append(f"error_code: {result.error_code or 'unknown_error'}")
        if result.message:
            lines.append(f"message: {result.message}")

    return "\n".join(lines)
