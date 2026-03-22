from __future__ import annotations


class SteamCliError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class AuthError(SteamCliError):
    def __init__(self, message: str = "Missing or invalid STEAM_TOKEN.") -> None:
        super().__init__("auth_error", message)


class ConfigError(SteamCliError):
    def __init__(self, message: str) -> None:
        super().__init__("config_error", message)


class UpstreamError(SteamCliError):
    def __init__(self, message: str) -> None:
        super().__init__("upstream_error", message)


class NotFoundError(SteamCliError):
    def __init__(self, message: str) -> None:
        super().__init__("not_found", message)
