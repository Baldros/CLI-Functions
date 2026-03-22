from __future__ import annotations

import typer

from steam_cli.config import get_settings
from steam_cli.errors import ConfigError, SteamCliError
from steam_cli.models.result import CliResult
from steam_cli.output import emit_result
from steam_cli.providers.steam_web_api import SteamWebApiProvider
from steam_cli.services.identity import IdentityService

app = typer.Typer(help="Games/library commands")


@app.command("owned")
def games_owned(
    ctx: typer.Context,
    identity: str | None = typer.Argument(None, help="steamid64 or vanity (optional if STEAM_IDENTITY is set)"),
) -> None:
    settings = get_settings()
    input_identity = (identity or settings.steam_identity or "").strip()
    provider = SteamWebApiProvider()
    identity_service = IdentityService(provider)

    try:
        if not input_identity:
            raise ConfigError(
                "Missing identity. Pass <steamid|vanity> or set STEAM_IDENTITY in the shared .env."
            )

        steamid = identity_service.resolve_input(input_identity)
        owned = provider.get_owned_games(steamid)

        sorted_games = sorted(
            owned["games"],
            key=lambda game: int(game.get("playtime_forever", 0) or 0),
            reverse=True,
        )

        game_names: list[str] = []
        for game in sorted_games:
            appid = game.get("appid")
            name = str(game.get("name") or "").strip()
            if name:
                game_names.append(name)
            elif appid is not None:
                game_names.append(f"appid:{appid}")

        result = CliResult.success(
            source=provider.source,
            official=True,
            auth_type="token",
            data={
                "input": input_identity,
                "steamid64": steamid,
                "game_count": owned["game_count"],
                "games": game_names,
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
