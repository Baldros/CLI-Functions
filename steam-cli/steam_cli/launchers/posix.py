from __future__ import annotations

import platform
import subprocess


def open_uri(uri: str) -> None:
    system = platform.system().lower()
    if system == "darwin":
        subprocess.run(["open", uri], check=True)
        return
    subprocess.run(["xdg-open", uri], check=True)
