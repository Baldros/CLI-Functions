from __future__ import annotations

import typer

from steam_cli.errors import SteamCliError
from steam_cli.models.result import CliResult
from steam_cli.output import emit_result
from steam_cli.providers.steam_web_api import SteamWebApiProvider
from steam_cli.services.identity import IdentityService

app = typer.Typer(help="User profile commands")


@app.command("resolve")
def user_resolve(ctx: typer.Context, vanity: str = typer.Argument(..., help="Custom Steam vanity URL")) -> None:
    provider = SteamWebApiProvider()
    service = IdentityService(provider)

    try:
        steamid = service.resolve_input(vanity)
        result = CliResult.success(
            source=provider.source,
            official=True,
            auth_type="token",
            data={"input": vanity, "steamid64": steamid},
        )
    except SteamCliError as exc:
        result = CliResult.failure(
            source=provider.source,
            official=True,
            auth_type="token",
            error_code=exc.code,
            message=exc.message,
        )

    emit_result(ctx, result)


@app.command("summary")
def user_summary(
    ctx: typer.Context,
    identity: str = typer.Argument(..., help="steamid64 or vanity"),
) -> None:
    provider = SteamWebApiProvider()
    identity_service = IdentityService(provider)

    try:
        steamid = identity_service.resolve_input(identity)
        player = provider.get_player_summary(steamid)

        result = CliResult.success(
            source=provider.source,
            official=True,
            auth_type="token",
            data={
                "input": identity,
                "steamid64": steamid,
                "personaname": player.get("personaname", ""),
                "profileurl": player.get("profileurl", ""),
                "avatarfull": player.get("avatarfull", ""),
                "personastate": player.get("personastate", ""),
                "communityvisibilitystate": player.get("communityvisibilitystate", ""),
            },
        )
    except SteamCliError as exc:
        result = CliResult.failure(
            source=provider.source,
            official=True,
            auth_type="token",
            error_code=exc.code,
            message=exc.message,
        )

    emit_result(ctx, result)
