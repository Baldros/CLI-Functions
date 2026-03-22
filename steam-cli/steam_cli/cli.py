from __future__ import annotations

import typer

from steam_cli.commands.app import app as app_commands
from steam_cli.commands.client import app as client_commands
from steam_cli.commands.diagnose import app as diagnose_commands
from steam_cli.commands.games import app as games_commands
from steam_cli.commands.user import app as user_commands
from steam_cli.config import get_settings

app = typer.Typer(help="Steam CLI for terminal agents and human operators")
app.add_typer(user_commands, name="user")
app.add_typer(games_commands, name="games")
app.add_typer(app_commands, name="app")
app.add_typer(client_commands, name="client")
app.add_typer(diagnose_commands, name="diagnose")


@app.callback()
def main(
    ctx: typer.Context,
    output_format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: text or json",
    ),
) -> None:
    settings = get_settings()
    fmt = (output_format or settings.output_format or "text").strip().lower()
    if fmt not in {"text", "json"}:
        raise typer.BadParameter("--format must be either 'text' or 'json'")
    ctx.obj = {"output_format": fmt}


def run() -> None:
    app()
