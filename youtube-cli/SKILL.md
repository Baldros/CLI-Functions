---
name: youtube-cli
description: Use the local YouTube terminal CLI at C:\Users\amori\Documents\CLI-Functions\youtube-cli\YoutubeCLI.py for everything related to YouTube: search, metadata lookup, transcript extraction, channel inspection, comment retrieval, and media downloads.
---

# YouTube CLI Skill

Use esta ferramenta para interagir com o YouTube via terminal, permitindo buscas, extração de metadados, transcrições e downloads de mídia (vídeo ou áudio).

## ⚠️ Configuração Obrigatória

A ferramenta depende da variável de ambiente `YOUTUBE_API_KEY` configurada no arquivo `.env` localizado na raiz do projeto: `C:\Users\amori\Documents\CLI-Functions\.env`.

### Uso do Ambiente Virtual (venv)

Sempre utilize o interpretador Python do ambiente virtual para garantir que as dependências (`google-api-python-client`, `yt-dlp`, `youtube-transcript-api`) estejam disponíveis.

**Comando Base (Windows):**
```powershell
& "C:\Users\amori\Documents\CLI-Functions\youtube-cli\.venv\Scripts\python.exe" C:\Users\amori\Documents\CLI-Functions\youtube-cli\YoutubeCLI.py <comando> <args>
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

> ⚠️ **DIRETRIZ OBRIGATÓRIA:** O destino padrão para **QUALQUER** download é a pasta **Downloads do sistema** (`C:\Users\amori\Downloads`). 
> 
> *   **PADRÃO:** Sempre adicione `--out "C:\Users\amori\Downloads"` ao comando de download.
> *   **EXCEÇÃO:** Somente utilize outro caminho se o usuário fornecer um local específico explicitamente.
> *   **PROIBIDO:** Nunca salve arquivos na pasta interna do projeto (`./downloads`) por conta própria.

### Exemplos de Download Correto
*   **Comando Sugerido:**
    `download https://... --out "C:\Users\amori\Downloads"`
*   **Apenas Áudio (MP3):**
    `download https://... --audio --out "C:\Users\amori\Downloads"`

---

## 🚀 Diretrizes Estratégicas

### 1. Refinamento Prévio da Demanda Antes da Busca no YouTube
Quando o pedido do usuário for vago, amplo, ambíguo ou exigir curadoria, não dependa apenas da primeira busca no YouTube. Antes de usar o `youtube-cli`, faça uma investigação breve na internet para refinar a intenção real do pedido.

Use essa investigação prévia para identificar, conforme o caso:
- nomes de canais relevantes e confiáveis;
- títulos ou formatos de vídeos que costumam responder bem ao problema;
- termos técnicos, nomes de produtos, erros, siglas ou palavras-chave mais precisas;
- subtemas ou abordagens que o usuário provavelmente quis dizer, mas ainda não formulou direito.

Depois disso, use o `youtube-cli` com consultas mais específicas e informativas. Priorize buscas em texto natural com combinações como:
- `<tema específico> <nome do canal>`
- `<erro/problema exato> tutorial`
- `<ferramenta/tecnologia> <caso de uso>`

Se a pesquisa externa trouxer bons sinais, converta isso em 1 a 3 buscas mais focadas no YouTube, em vez de insistir em uma consulta genérica.

Regras obrigatórias:
- não cite nem dependa do nome de uma ferramenta externa específica nesta estratégia;
- não invente filtros, operadores ou sintaxes que o `youtube-cli` não suporta;
- trate essa etapa como estratégia de refinamento de demanda, não como substituição do `youtube-cli`.

### 2. Análise e Resumo de Conteúdo
1. `search "tutorial de python" --max 1` (Extrair o ID do resultado)
2. `transcript <ID> --lang pt`
3. (Analisar o texto retornado e responder ao usuário)

### 3. Extração de Áudio para Estudo/Podcasts
1. `search "podcast inteligência artificial" --max 1`
2. `download <URL> --audio --out "C:\Users\amori\Downloads"`

---

## Diretrizes de Operação

1. **Idiomas:** Se a transcrição falhar no idioma solicitado (`--lang`), a ferramenta tentará buscar em inglês (`en`) e traduzir automaticamente.
2. **IDs vs URLs:** Comandos de dados (`details`, `transcript`, `comments`) usam **IDs**. O comando `download` usa a **URL**.
3. **Dependência Externa:** O download de formatos específicos ou conversão para MP3 pode requerer `ffmpeg` instalado no sistema. Se falhar, tente o download padrão (sem flags).
4. **Respeito aos Termos:** Use a ferramenta de forma ética, respeitando direitos autorais e limites da API.
