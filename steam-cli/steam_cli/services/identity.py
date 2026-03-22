from __future__ import annotations

from steam_cli.errors import NotFoundError
from steam_cli.providers.steam_web_api import SteamWebApiProvider


class IdentityService:
    def __init__(self, provider: SteamWebApiProvider | None = None) -> None:
        self.provider = provider or SteamWebApiProvider()

    def resolve_input(self, identity: str) -> str:
        raw = identity.strip()
        if raw.isdigit() and len(raw) >= 16:
            return raw
        if not raw:
            raise NotFoundError("Identity cannot be empty.")
        return self.provider.resolve_vanity_url(raw)
