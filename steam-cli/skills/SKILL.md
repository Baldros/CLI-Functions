---
name: steam-cli
description: Use when Codex needs to operate the local Steam CLI at <COLOQUE_AQUI_O_CAMINHO_DO_STEAM_CLI> to resolve game names to AppIDs, fetch Steam store metadata, inspect Steam profile data, or control the installed Steam desktop client. Use for tasks like finding a game's AppID, opening a Steam store page, triggering install or run, checking Steam CLI config, handling private-profile limits, and recovering from ambiguous, abbreviated, aliased, or misspelled game names.
---

# Steam CLI

## Overview

Use the local `steam-cli` project to interact with Steam through structured terminal commands.

Prefer the CLI over ad hoc browsing when the task is one of these:

- resolve a game name into a Steam `appid`
- fetch current Steam store metadata for a game
- open a Steam page in the desktop client
- trigger install or run in the desktop client
- inspect Steam CLI auth/config state
- inspect limited user/profile data when the API token is available

Treat `appid` as the canonical identifier for game-specific actions.

## Environment

Use the project at:

- `<COLOQUE_AQUI_O_CAMINHO_DO_STEAM_CLI>`

Run commands from that directory with:

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json ...
```

Prefer `--format json` so outputs are easy to parse and reason about.

Configuration comes from the shared env file used by other CLIs:

- `<COLOQUE_AQUI_O_CAMINHO_DO_ARQUIVO_.ENV>`

Important env vars:

- `STEAM_TOKEN`: required for authenticated Steam Web API calls such as `user` and `games`
- `DOMAIN_NAME`: shared setting; the CLI normalizes invalid values to `api.steampowered.com`
- `STEAM_IDENTITY`: optional default `steamid64` or vanity for `games owned`

## Core Rules

- Resolve `appid` first for any action that targets a specific game, unless the `appid` is already known from prior context.
- Never invent or guess an `appid`.
- Prefer `app appid "<name>"` when the user wants a game-specific action.
- Prefer `app info "<name>"` when the user wants general information about a game.
- Prefer `app details <appid>` when the `appid` is already known.
- Treat `client install` and `client run` as handoff commands to Steam. They confirm the URI launch, not the final install/play result.
- Treat `client open library-app <appid>` as experimental. Prefer store/community pages unless the user specifically wants library focus behavior.
- If intent is unclear, use `--dry-run` for client actions before launching GUI side effects.

## Current Commands

Use these commands as implemented today.

### Diagnostics

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json diagnose config
.\.venv\Scripts\python.exe -m steam_cli --format json diagnose client
```

### User and Library

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json user resolve "<vanity>"
.\.venv\Scripts\python.exe -m steam_cli --format json user summary "<steamid-or-vanity>"
.\.venv\Scripts\python.exe -m steam_cli --format json games owned ["<steamid-or-vanity>"]
```

### App and Storefront

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json app appid "<game name>"
.\.venv\Scripts\python.exe -m steam_cli --format json app search "<game name>"
.\.venv\Scripts\python.exe -m steam_cli --format json app info "<game name>"
.\.venv\Scripts\python.exe -m steam_cli --format json app details <appid>
```

### Steam Desktop Client

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json client open library
.\.venv\Scripts\python.exe -m steam_cli --format json client open friends
.\.venv\Scripts\python.exe -m steam_cli --format json client open downloads
.\.venv\Scripts\python.exe -m steam_cli --format json client open settings
.\.venv\Scripts\python.exe -m steam_cli --format json client open store
.\.venv\Scripts\python.exe -m steam_cli --format json client open store-app <appid>
.\.venv\Scripts\python.exe -m steam_cli --format json client open community-app <appid>
.\.venv\Scripts\python.exe -m steam_cli --format json client open library-app <appid> --dry-run
.\.venv\Scripts\python.exe -m steam_cli --format json client run <appid>
.\.venv\Scripts\python.exe -m steam_cli --format json client install <appid>
```

## Standard Workflows

### 1. Resolve a Game Name Before Acting

Use this for install, run, or open-store requests.

1. Run `app appid "<user text>"`.
2. If it returns `ok=true`, use the returned `appid`.
3. If the task is higher risk or user intent is ambiguous, also run `app info "<user text>"` to confirm the title.
4. Only then run `client open store-app <appid>`, `client run <appid>`, or `client install <appid>`.

Example:

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json app appid "Binary Domain"
.\.venv\Scripts\python.exe -m steam_cli --format json client install 203750
```

### 2. Bring Back Information About a Game

Use `app info` when the user gives a game name. It resolves the best match and fetches current storefront metadata in one step.

Example:

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json app info "Resident Evil Requiem"
```

Use `app details <appid>` only if the `appid` is already known.

### 3. Open a Store Page in Steam

1. Resolve the `appid`.
2. Run `client open store-app <appid>`.
3. Report that Steam accepted the request if `launched=true`.

Example:

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json app appid "Resident Evil Requiem"
.\.venv\Scripts\python.exe -m steam_cli --format json client open store-app 3764200
```

### 4. Trigger an Install

1. Resolve the `appid`.
2. Optionally confirm with `app info` if the name is ambiguous.
3. Run `client install <appid>`.
4. Report that the install request was handed off to Steam. Do not claim the game is already installed.

If the user cares about follow-up, offer to open Downloads:

```powershell
.\.venv\Scripts\python.exe -m steam_cli --format json client open downloads
```

### 5. Handle Private Profile Limitations

If `games owned` returns `game_count: 0` and the profile is private or low-visibility, do not conclude that the user owns no games.

Instead:

- explain that the Steam profile/library visibility can hide owned games from the Web API
- continue to support app/store/client workflows based on `appid`
- do not block install/open-store actions just because library introspection failed

## Name Resolution and Flexibility

Users will often provide shorthand, aliases, abbreviations, bad spacing, or slightly wrong titles. Handle that before giving up.

Try these steps in order:

1. Run `app appid "<user text>"` once as given.
2. If it fails, run `app search "<user text>"` and inspect candidates.
3. Normalize obvious variations:
- franchise initials like `RE`, `FF`, `MGS`, `GTA`
- Arabic vs Roman numerals like `7` vs `VII`
- subtitle omissions like `Resident Evil Requiem` vs deluxe kit variants
- punctuation differences like hyphen, colon, apostrophe, spacing
4. If the user intent is still reasonably obvious, retry with the expanded title.
5. If local lookup still fails, browse the web to confirm the official Steam-facing title, then rerun `app appid` with that title.
6. Only ask the user to clarify if multiple plausible games remain after search and title normalization.

Examples of acceptable normalization:

- `FF7` -> `Final Fantasy VII` or the most likely Steam-specific title after search
- `RE2` -> `Resident Evil 2`
- `MGS V` -> `Metal Gear Solid V`
- typo such as `Binari Domain` -> search, correct to `Binary Domain`, then resolve `appid`

## Error Handling

### `not_found` from `app appid` or `app info`

Interpret this as a name-resolution problem first, not a hard failure.

Do this:

- try `app search`
- normalize the title or abbreviation
- if needed, browse the web to confirm the exact Steam title
- rerun the lookup

Do not claim the game does not exist after a single failed lookup.

### `auth_error`

This usually means `STEAM_TOKEN` is missing or invalid.

Do this:

- run `diagnose config`
- explain that authenticated commands need `STEAM_TOKEN` in `<COLOQUE_AQUI_O_CAMINHO_DO_ARQUIVO_.ENV>`
- avoid `user` and `games` commands until auth is fixed
- continue using public storefront commands when possible

### `config_error`

This usually means a required identity was missing for a user/library command.

Do this:

- ask for `steamid64` or vanity if the user explicitly wants profile/library data
- or suggest setting `STEAM_IDENTITY` in the shared `.env`

### `game_count: 0`

Interpret carefully.

Possible cause:

- private library/profile visibility

Do this:

- explain the limitation
- avoid claiming the library is empty
- keep using `appid`-based workflows

### Client action returns `launched=true`

This only means the URI was handed off to Steam.

Do not overclaim. The final result may still depend on:

- ownership or license status
- age/region restrictions
- disk space
- Steam client prompts
- the client actually being logged in and healthy

Good reporting style:

- say the install/open/run request was sent successfully
- if needed, offer to open Steam Downloads or the Store page next

## Response Style

When you use this skill:

- keep responses concise
- mention the resolved title and `appid` when relevant
- distinguish between store metadata retrieved from the CLI and actions merely handed off to the Steam client
- if you had to normalize or correct a title, say what title you used
- if you had to browse to recover an exact title, say that you verified the name before rerunning the CLI lookup

## Safety and Validation

- Prefer `app appid` before any game-specific GUI action.
- Prefer `--dry-run` when the user is asking what would happen rather than asking you to do it.
- Never claim install success unless there is a separate confirmation path beyond the current `steam-cli` handoff.
- Never claim a user does not own a game solely because `games owned` is empty on a private profile.
