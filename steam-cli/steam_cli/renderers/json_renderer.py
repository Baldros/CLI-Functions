from __future__ import annotations

import json

from steam_cli.models.result import CliResult


def render_json(result: CliResult) -> str:
    return json.dumps(result.model_dump(exclude_none=True), indent=2, ensure_ascii=True)
