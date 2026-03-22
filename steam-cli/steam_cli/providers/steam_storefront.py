from __future__ import annotations

import httpx

from steam_cli.config import get_settings
from steam_cli.errors import NotFoundError, UpstreamError


class SteamStorefrontProvider:
    source = "steam_storefront"

    def __init__(self) -> None:
        settings = get_settings()
        self._timeout = settings.timeout_seconds
        self._base_url = "https://store.steampowered.com"

    def _request_json(self, path: str, params: dict[str, str]) -> dict:
        url = f"{self._base_url}/{path.lstrip('/')}"
        try:
            response = httpx.get(url, params=params, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise UpstreamError(f"Steam Store HTTP error: {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise UpstreamError(f"Steam Store request failed: {exc}") from exc
        except ValueError as exc:
            raise UpstreamError("Steam Store returned invalid JSON.") from exc

    def search_apps(self, term: str, *, cc: str = "br", lang: str = "portuguese") -> dict:
        payload = self._request_json(
            "api/storesearch/",
            {
                "term": term,
                "cc": cc,
                "l": lang,
            },
        )

        items = payload.get("items", [])
        if not isinstance(items, list):
            items = []

        total = int(payload.get("total", len(items)) or 0)
        return {"total": total, "items": items}

    def get_app_details(self, appid: int, *, cc: str = "br", lang: str = "portuguese") -> dict:
        payload = self._request_json(
            "api/appdetails",
            {
                "appids": str(appid),
                "cc": cc,
                "l": lang,
            },
        )

        entry = payload.get(str(appid), {})
        if not isinstance(entry, dict) or not entry.get("success"):
            raise NotFoundError(f"App details not found for appid: {appid}")

        data = entry.get("data", {})
        if not isinstance(data, dict):
            raise NotFoundError(f"Invalid app details payload for appid: {appid}")

        return data
