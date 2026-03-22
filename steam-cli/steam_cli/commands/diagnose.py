from __future__ import annotations

import platform

import typer

from steam_cli.config import DEFAULT_DOTENV_PATH, DEFAULT_STEAM_DOMAIN, get_settings
from steam_cli.models.result import CliResult
from steam_cli.output import emit_result

app = typer.Typer(help="Diagnostic commands")


@app.command("config")
def diagnose_config(ctx: typer.Context) -> None:
    settings = get_settings()
    warnings: list[str] = []
    if not settings.steam_token:
        warnings.append("STEAM_TOKEN is not set. Authenticated API commands will fail.")
    if not settings.steam_identity:
        warnings.append("STEAM_IDENTITY is not set. Pass identity explicitly for library commands.")
    if settings.raw_domain_name and settings.raw_domain_name != settings.domain_name:
        warnings.append(
            f"DOMAIN_NAME='{settings.raw_domain_name}' is invalid for Steam Web API. Using fallback '{DEFAULT_STEAM_DOMAIN}'."
        )

    result = CliResult.success(
        source="local",
        official=True,
        auth_type="none",
        warnings=warnings,
        data={
            "steam_token_configured": bool(settings.steam_token),
            "steam_identity_configured": bool(settings.steam_identity),
            "raw_domain_name": settings.raw_domain_name,
            "effective_domain_name": settings.domain_name,
            "output_format": settings.output_format,
            "timeout_seconds": settings.timeout_seconds,
            "shared_dotenv_path": str(DEFAULT_DOTENV_PATH),
        },
    )
    emit_result(ctx, result)


@app.command("client")
def diagnose_client(ctx: typer.Context) -> None:
    result = CliResult.success(
        source="steam_client",
        official=False,
        experimental=False,
        auth_type="none",
        data={
            "platform": platform.platform(),
            "protocol_hint": "steam://",
            "notes": "Use 'steam client open library --dry-run' to test URI generation without launching GUI.",
        },
    )
    emit_result(ctx, result)
