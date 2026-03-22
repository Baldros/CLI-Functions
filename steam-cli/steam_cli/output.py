from __future__ import annotations

import typer

from steam_cli.models.result import CliResult
from steam_cli.renderers.json_renderer import render_json
from steam_cli.renderers.text_renderer import render_text


def get_output_format(ctx: typer.Context) -> str:
    if ctx.obj and isinstance(ctx.obj, dict):
        return str(ctx.obj.get("output_format", "text"))
    return "text"


def emit_result(ctx: typer.Context, result: CliResult) -> None:
    fmt = get_output_format(ctx)
    if fmt == "json":
        typer.echo(render_json(result))
        return
    typer.echo(render_text(result))
