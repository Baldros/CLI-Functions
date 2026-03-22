# steam-cli

Scaffold inicial do `steam-cli` com arquitetura orientada a provedores e comandos de terminal para integracao com agentes.

## Requisitos

- Python 3.11+
- `.venv` local no root do projeto

## Instalar dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configurar ambiente

O `steam-cli` usa o mesmo `.env` do diretorio `CLI-Functions` (mesmo padrao do `google-cli`).

Variaveis necessarias:

- `STEAM_TOKEN`
- `DOMAIN_NAME` (opcional, default: `api.steampowered.com`)

Opcional para comandos de biblioteca sem argumento:

- `STEAM_IDENTITY` (steamid64 ou vanity)

## Rodar

```powershell
.\.venv\Scripts\python.exe -m steam_cli --help
```

ou, apos instalar em editable:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
steam --help
```

## Comandos iniciais

- `steam diagnose config`
- `steam diagnose client`
- `steam user resolve <vanity>`
- `steam user summary <steamid|vanity>`
- `steam games owned [steamid|vanity]`
- `steam client open <library|friends|downloads|settings|store|store-app|community-app|library-app> [appid] [--dry-run]`
- `steam client run <appid> [--dry-run]`
- `steam client install <appid> [--dry-run]`
