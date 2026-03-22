from __future__ import annotations

from typing import Any

from steam_cli.providers.steam_storefront import SteamStorefrontProvider


class AppResolverService:
    def __init__(self, provider: SteamStorefrontProvider | None = None) -> None:
        self.provider = provider or SteamStorefrontProvider()

    def search(self, query: str, *, cc: str = "br", lang: str = "portuguese", limit: int = 10) -> dict:
        payload = self.provider.search_apps(query, cc=cc, lang=lang)
        items = payload.get("items", [])[: max(limit, 1)]
        return {
            "query": query,
            "total": payload.get("total", len(items)),
            "matches": [self._normalize_item(item) for item in items],
        }

    def choose_best(self, query: str, matches: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not matches:
            return None

        q = query.strip().lower()

        def score(item: dict[str, Any]) -> tuple[int, int]:
            name = str(item.get("name") or "").strip().lower()
            if not name:
                return (3, 999999)
            if name == q:
                return (0, len(name))
            if name.startswith(q):
                return (1, len(name))
            if q in name:
                return (2, len(name))
            return (3, len(name))

        return sorted(matches, key=score)[0]

    @staticmethod
    def _normalize_item(item: dict[str, Any]) -> dict[str, Any]:
        appid = item.get("id")
        name = str(item.get("name") or "").strip()
        price = item.get("price")
        return {
            "appid": appid,
            "name": name,
            "price": price,
        }
