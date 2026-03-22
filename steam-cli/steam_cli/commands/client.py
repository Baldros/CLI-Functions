from __future__ import annotations

from typing import Annotated

import typer

from steam_cli.models.result import CliResult
from steam_cli.output import emit_result
from steam_cli.services.client_actions import ClientActionsService

app = typer.Typer(help="Steam desktop client actions")


def _build_result(data: dict, spec, *, dry_run: bool) -> CliResult:
    warnings: list[str] = []
    if spec.experimental:
        warnings.append("This action is experimental and may break depending on Steam client version.")
    if dry_run:
        warnings.append("Dry run enabled. No URI was launched.")

    return CliResult.success(
        source="steam_client",
        official=False,
        experimental=spec.experimental,
        auth_type="none",
        warnings=warnings,
        data=data,
    )


@app.command("open")
def client_open(
    ctx: typer.Context,
    target: Annotated[
        str,
        typer.Argument(help="library|friends|downloads|settings|store|store-app|community-app|library-app"),
    ],
    appid: Annotated[int | None, typer.Argument(help="AppID when target requires it")] = None,
    dry_run: bool = typer.Option(False, "--dry-run", help="Only render URI, do not launch Steam."),
) -> None:
    service = ClientActionsService()

    try:
        data, spec = service.execute(action="open", target=target, appid=appid, dry_run=dry_run)
        result = _build_result(data, spec, dry_run=dry_run)
    except ValueError as exc:
        result = CliResult.failure(
            source="steam_client",
            official=False,
            experimental=False,
            auth_type="none",
            error_code="invalid_client_action",
            message=str(exc),
        )

    emit_result(ctx, result)


@app.command("run")
def client_run(
    ctx: typer.Context,
    appid: int = typer.Argument(..., help="Steam AppID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only render URI, do not launch Steam."),
) -> None:
    service = ClientActionsService()
    data, spec = service.execute(action="run", appid=appid, dry_run=dry_run)
    emit_result(ctx, _build_result(data, spec, dry_run=dry_run))


@app.command("install")
def client_install(
    ctx: typer.Context,
    appid: int = typer.Argument(..., help="Steam AppID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only render URI, do not launch Steam."),
) -> None:
    service = ClientActionsService()
    data, spec = service.execute(action="install", appid=appid, dry_run=dry_run)
    emit_result(ctx, _build_result(data, spec, dry_run=dry_run))
