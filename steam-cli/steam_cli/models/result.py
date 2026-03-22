from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CliResult(BaseModel):
    ok: bool
    source: str
    official: bool = True
    experimental: bool = False
    auth_type: Literal["public", "token", "none"] = "public"
    warnings: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    message: str | None = None

    @classmethod
    def success(
        cls,
        *,
        source: str,
        data: dict[str, Any],
        official: bool = True,
        experimental: bool = False,
        auth_type: Literal["public", "token", "none"] = "public",
        warnings: list[str] | None = None,
    ) -> "CliResult":
        return cls(
            ok=True,
            source=source,
            official=official,
            experimental=experimental,
            auth_type=auth_type,
            warnings=warnings or [],
            data=data,
        )

    @classmethod
    def failure(
        cls,
        *,
        source: str,
        error_code: str,
        message: str,
        official: bool = True,
        experimental: bool = False,
        auth_type: Literal["public", "token", "none"] = "public",
    ) -> "CliResult":
        return cls(
            ok=False,
            source=source,
            official=official,
            experimental=experimental,
            auth_type=auth_type,
            error_code=error_code,
            message=message,
            data={},
        )
