from __future__ import annotations

from steam_cli.launchers import open_steam_uri
from steam_cli.providers.steam_client import SteamClientProvider


class ClientActionsService:
    def __init__(self, provider: SteamClientProvider | None = None) -> None:
        self.provider = provider or SteamClientProvider()

    def execute(
        self,
        *,
        action: str,
        target: str | None = None,
        appid: int | None = None,
        dry_run: bool = False,
    ) -> dict:
        uri, spec = self.provider.resolve_uri(action=action, target=target, appid=appid)

        if not dry_run:
            open_steam_uri(uri)

        return {
            "action": action,
            "target": target,
            "appid": appid,
            "uri": uri,
            "stability": spec.stability,
            "launched": not dry_run,
            "dry_run": dry_run,
        }, spec
