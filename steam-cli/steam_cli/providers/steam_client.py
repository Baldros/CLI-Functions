from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ClientUriSpec:
    uri_template: str
    stability: Literal["stable", "experimental", "unsupported"]
    experimental: bool
    needs_appid: bool = False


_URI_SPECS: dict[str, ClientUriSpec] = {
    "open:library": ClientUriSpec("steam://open/games", "stable", False),
    "open:friends": ClientUriSpec("steam://open/friends", "stable", False),
    "open:downloads": ClientUriSpec("steam://open/downloads", "stable", False),
    "open:settings": ClientUriSpec("steam://open/settings", "stable", False),
    "open:store": ClientUriSpec("steam://open/store", "stable", False),
    "open:store-app": ClientUriSpec("steam://store/{appid}", "stable", False, True),
    "open:community-app": ClientUriSpec("steam://url/GameHub/{appid}", "stable", False, True),
    "open:library-app": ClientUriSpec("steam://nav/games/details/{appid}", "experimental", True, True),
    "run": ClientUriSpec("steam://run/{appid}", "stable", False, True),
    "install": ClientUriSpec("steam://install/{appid}", "stable", False, True),
}


class SteamClientProvider:
    source = "steam_client"

    def resolve_uri(self, *, action: str, target: str | None = None, appid: int | None = None) -> tuple[str, ClientUriSpec]:
        key = action if target is None else f"{action}:{target}"
        spec = _URI_SPECS.get(key)
        if not spec:
            raise ValueError(f"Unsupported client action: {key}")

        if spec.needs_appid and appid is None:
            raise ValueError(f"Action '{key}' requires an appid")

        uri = spec.uri_template.format(appid=appid)
        return uri, spec
