from __future__ import annotations

import os


def open_uri(uri: str) -> None:
    os.startfile(uri)
