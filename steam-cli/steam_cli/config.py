from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

STEAM_CLI_ROOT = Path(__file__).resolve().parent.parent
CLI_FUNCTIONS_ROOT = STEAM_CLI_ROOT.parent
DEFAULT_DOTENV_PATH = CLI_FUNCTIONS_ROOT / ".env"
LOCAL_DOTENV_PATH = STEAM_CLI_ROOT / ".env"
DEFAULT_STEAM_DOMAIN = "api.steampowered.com"


@dataclass(frozen=True)
class Settings:
    steam_token: str
    raw_domain_name: str
    domain_name: str
    steam_identity: str
    output_format: str
    timeout_seconds: float


def _load_env() -> None:
    # Keep parity with google-cli env model: shared .env at CLI-Functions root.
    load_dotenv(dotenv_path=DEFAULT_DOTENV_PATH, override=False)
    # Optional local fallback for isolated usage of steam-cli.
    load_dotenv(dotenv_path=LOCAL_DOTENV_PATH, override=False)


def _normalize_domain_name(raw_domain: str) -> str:
    candidate = raw_domain.strip().replace("https://", "").replace("http://", "").strip("/")
    if not candidate:
        return DEFAULT_STEAM_DOMAIN
    if candidate == "localhost" or "." in candidate:
        return candidate
    return DEFAULT_STEAM_DOMAIN


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_env()
    raw_domain = os.getenv("DOMAIN_NAME", "").strip()
    return Settings(
        steam_token=os.getenv("STEAM_TOKEN", "").strip(),
        raw_domain_name=raw_domain,
        domain_name=_normalize_domain_name(raw_domain),
        steam_identity=os.getenv("STEAM_IDENTITY", "").strip(),
        output_format=os.getenv("STEAM_OUTPUT_FORMAT", "text").strip().lower(),
        timeout_seconds=float(os.getenv("STEAM_TIMEOUT_SECONDS", "15") or 15),
    )
