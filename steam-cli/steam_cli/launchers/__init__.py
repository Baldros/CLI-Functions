from __future__ import annotations

import platform

from steam_cli.launchers.posix import open_uri as open_uri_posix
from steam_cli.launchers.windows import open_uri as open_uri_windows


def open_steam_uri(uri: str) -> None:
    system = platform.system().lower()
    if system.startswith("win"):
        open_uri_windows(uri)
        return
    open_uri_posix(uri)
