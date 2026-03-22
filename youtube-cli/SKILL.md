# YouTube CLI Skill

Use esta ferramenta para interagir com o YouTube via terminal, permitindo buscas, extração de metadados, transcrições e downloads de mídia (vídeo ou áudio).

## ⚠️ Configuração Obrigatória

A ferramenta depende da variável de ambiente `YOUTUBE_API_KEY` configurada no arquivo `.env` localizado na raiz do projeto: `<PROJECT_ROOT>/.env` (substitua pelo caminho do seu projeto).

### Uso do Ambiente Virtual (venv)

Sempre utilize o interpretador Python do ambiente virtual para garantir que as dependências (`google-api-python-client`, `yt-dlp`, `youtube-transcript-api`) estejam disponíveis.

**Comando Base (exemplo):**
```powershell
& "<VENV_PYTHON>" "<PROJECT_ROOT>/youtube-cli/YoutubeCLI.py" <comando> <args>
```

---

## Comandos Disponíveis

| Comando | Descrição | Argumentos Principais |
|---|---|---|
| `search` | Busca vídeos por palavras-chave. | `<query>` `--max <num>` |
| `details` | Obtém metadados (views, likes, descrição) pelo ID. | `<id>` |
| `transcript` | Extrai a transcrição/legenda do vídeo. | `<id>` `--lang <idioma>` |
| `comments` | Lista os comentários mais relevantes. | `<id>` `--max <num>` |
| `download` | Baixa o vídeo ou áudio. | `<url>` `--out <path>` `--audio` `--format <fmt>` |
| `channel` | Obtém informações de um canal pelo ID. | `<id>` |

---

## 📂 DIRETÓRIO DE DOWNLOAD (REGRA CRÍTICA)

> ⚠️ **DIRETRIZ OBRIGATÓRIA:** O destino padrão para **QUALQUER** download é a pasta de Downloads do sistema (`<DOWNLOADS_DIR>` — substitua pelo caminho apropriado no seu sistema).
> 
> *   **PADRÃO:** Sempre adicione `--out "<DOWNLOADS_DIR>"` ao comando de download.
> *   **EXCEÇÃO:** Somente utilize outro caminho se o usuário fornecer um local específico explicitamente.
> *   **PROIBIDO:** Nunca salve arquivos na pasta interna do projeto (`<PROJECT_DOWNLOADS_DIR>` — ex: `./downloads`) por conta própria.

### Exemplos de Download Correto
-   **Comando Sugerido:**
    `download https://... --out "<DOWNLOADS_DIR>"`
-   **Apenas Áudio (MP3):**
    `download https://... --audio --out "<DOWNLOADS_DIR>"`

---

## 🚀 Workflows Sugeridos

### 1. Pesquisa e Resumo (Análise de Conteúdo)
O agente deve buscar um vídeo sobre um tema, obter a transcrição e então gerar um resumo ou responder perguntas:
1. `search "tutorial de python" --max 1` (Extrair o ID do resultado)
2. `transcript <ID> --lang pt`
3. (Analisar o texto retornado)

### 2. Monitoramento de Canais
1. `channel <ChannelID>` (Para verificar estatísticas e descrição do canal)
2. `search "channelId:<ChannelID> <termo>"` (Para buscar vídeos específicos dentro de um canal)

### 3. Extração de Áudio para Estudo/Podcasts
1. `search "podcast inteligência artificial" --max 1`
2. `download <URL> --audio --out "<DOWNLOADS_DIR>"`

---

## Diretrizes de Operação

1. **Idiomas:** Se a transcrição falhar no idioma solicitado (`--lang`), a ferramenta tentará buscar em inglês (`en`) e traduzir automaticamente.
2. **IDs vs URLs:** Comandos de dados (`details`, `transcript`, `comments`) usam **IDs**. O comando `download` usa a **URL**.
3. **Dependência Externa:** O download de formatos específicos ou conversão para MP3 pode requerer `ffmpeg` instalado no sistema. Se falhar, tente o download padrão (sem flags).
4. **Respeito aos Termos:** Use a ferramenta de forma ética, respeitando direitos autorais e limites da API.
