from __future__ import annotations

import httpx

from steam_cli.config import get_settings
from steam_cli.errors import AuthError, NotFoundError, UpstreamError


class SteamWebApiProvider:
    source = "steam_web_api"

    def __init__(self) -> None:
        settings = get_settings()
        self._token = settings.steam_token
        self._base_url = f"https://{settings.domain_name.strip('/')}"
        self._timeout = settings.timeout_seconds

    def _request(self, path: str, params: dict[str, str], *, requires_auth: bool) -> dict:
        if requires_auth:
            if not self._token:
                raise AuthError("STEAM_TOKEN is required for this command.")
            params = {**params, "key": self._token}

        url = f"{self._base_url}/{path.lstrip('/')}"
        try:
            response = httpx.get(url, params=params, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise UpstreamError(f"Steam API HTTP error: {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise UpstreamError(f"Steam API request failed: {exc}") from exc

    def resolve_vanity_url(self, vanity: str) -> str:
        payload = self._request(
            "ISteamUser/ResolveVanityURL/v1/",
            {"vanityurl": vanity},
            requires_auth=True,
        )
        response = payload.get("response", {})
        if response.get("success") != 1:
            raise NotFoundError(f"Could not resolve vanity URL: {vanity}")

        steamid = str(response.get("steamid", "")).strip()
        if not steamid:
            raise NotFoundError(f"No steamid returned for vanity URL: {vanity}")
        return steamid

    def get_player_summary(self, steamid: str) -> dict:
        payload = self._request(
            "ISteamUser/GetPlayerSummaries/v2/",
            {"steamids": steamid},
            requires_auth=True,
        )
        players = payload.get("response", {}).get("players", [])
        if not players:
            raise NotFoundError(f"No player found for steamid: {steamid}")
        return players[0]

    def get_owned_games(self, steamid: str) -> dict:
        payload = self._request(
            "IPlayerService/GetOwnedGames/v1/",
            {
                "steamid": steamid,
                "include_appinfo": "1",
                "include_played_free_games": "1",
            },
            requires_auth=True,
        )
        response = payload.get("response", {})
        games = response.get("games", [])
        if not isinstance(games, list):
            games = []

        game_count = int(response.get("game_count", len(games)) or 0)
        return {"game_count": game_count, "games": games}
