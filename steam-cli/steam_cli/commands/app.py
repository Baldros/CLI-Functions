from __future__ import annotations

import typer

from steam_cli.errors import SteamCliError
from steam_cli.models.result import CliResult
from steam_cli.output import emit_result
from steam_cli.services.app_info import AppInfoService
from steam_cli.services.app_resolver import AppResolverService

app = typer.Typer(help="App/store commands")


def _match_quality(query: str, candidate_name: str) -> str:
    q = query.strip().lower()
    name = candidate_name.strip().lower()
    if name == q:
        return "exact"
    if name.startswith(q):
        return "prefix"
    if q in name:
        return "contains"
    return "fuzzy"


@app.command("appid")
def app_appid(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Game name query"),
    cc: str = typer.Option("br", "--cc", help="Country code for storefront"),
    lang: str = typer.Option("portuguese", "--lang", help="Store language"),
) -> None:
    resolver = AppResolverService()

    try:
        payload = resolver.search(query, cc=cc, lang=lang, limit=10)
        matches = payload.get("matches", [])
        best = resolver.choose_best(query, matches)

        if not best:
            result = CliResult.failure(
                source="steam_storefront",
                official=False,
                auth_type="public",
                error_code="not_found",
                message=f"No matches found for query: {query}",
            )
            emit_result(ctx, result)
            return

        best_name = str(best.get("name") or "")
        quality = _match_quality(query, best_name)
        warnings: list[str] = []
        if quality == "fuzzy":
            warnings.append("Best match is fuzzy. Confirm appid before using in automated commands.")

        result = CliResult.success(
            source="steam_storefront",
            official=False,
            auth_type="public",
            warnings=warnings,
            data={
                "query": query,
                "appid": best.get("appid"),
                "name": best_name,
                "match_quality": quality,
                "candidates": matches[:5],
            },
        )
    except SteamCliError as exc:
        result = CliResult.failure(
            source="steam_storefront",
            official=False,
            auth_type="public",
            error_code=exc.code,
            message=exc.message,
        )

    emit_result(ctx, result)


@app.command("search")
def app_search(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Game name query"),
    cc: str = typer.Option("br", "--cc", help="Country code for storefront"),
    lang: str = typer.Option("portuguese", "--lang", help="Store language"),
    limit: int = typer.Option(10, "--limit", min=1, max=50),
) -> None:
    resolver = AppResolverService()

    try:
        payload = resolver.search(query, cc=cc, lang=lang, limit=limit)
        result = CliResult.success(
            source="steam_storefront",
            official=False,
            auth_type="public",
            data={
                "query": query,
                "cc": cc,
                "lang": lang,
                "total": payload.get("total", 0),
                "matches": payload.get("matches", []),
            },
        )
    except SteamCliError as exc:
        result = CliResult.failure(
            source="steam_storefront",
            official=False,
            auth_type="public",
            error_code=exc.code,
            message=exc.message,
        )

    emit_result(ctx, result)


@app.command("details")
def app_details(
    ctx: typer.Context,
    appid: int = typer.Argument(..., help="Steam appid"),
    cc: str = typer.Option("br", "--cc", help="Country code for storefront"),
    lang: str = typer.Option("portuguese", "--lang", help="Store language"),
) -> None:
    info = AppInfoService()

    try:
        details = info.get_details(appid, cc=cc, lang=lang)
        result = CliResult.success(
            source="steam_storefront",
            official=False,
            auth_type="public",
            data={
                "appid": appid,
                "cc": cc,
                "lang": lang,
                "details": details,
            },
        )
    except SteamCliError as exc:
        result = CliResult.failure(
            source="steam_storefront",
            official=False,
            auth_type="public",
            error_code=exc.code,
            message=exc.message,
        )

    emit_result(ctx, result)


@app.command("info")
def app_info(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Game name query"),
    cc: str = typer.Option("br", "--cc", help="Country code for storefront"),
    lang: str = typer.Option("portuguese", "--lang", help="Store language"),
) -> None:
    resolver = AppResolverService()
    info = AppInfoService()

    try:
        search_payload = resolver.search(query, cc=cc, lang=lang, limit=10)
        matches = search_payload.get("matches", [])
        best = resolver.choose_best(query, matches)

        if not best:
            result = CliResult.failure(
                source="steam_storefront",
                official=False,
                auth_type="public",
                error_code="not_found",
                message=f"No matches found for query: {query}",
            )
            emit_result(ctx, result)
            return

        appid = int(best["appid"])
        details = info.get_details(appid, cc=cc, lang=lang)

        result = CliResult.success(
            source="steam_storefront",
            official=False,
            auth_type="public",
            data={
                "query": query,
                "best_match": best,
                "details": details,
                "other_matches": matches[:5],
            },
        )
    except SteamCliError as exc:
        result = CliResult.failure(
            source="steam_storefront",
            official=False,
            auth_type="public",
            error_code=exc.code,
            message=exc.message,
        )

    emit_result(ctx, result)


@app.callback()
def app_root() -> None:
    """Namespace for app-related commands."""
