# YouTube CLI

Uma interface de linha de comando poderosa para interagir com o YouTube, permitindo buscas, extração de metadados, transcrições e downloads de mídia diretamente do seu terminal.

## 🚀 Como Usar

Para utilizar a ferramenta, você deve executar o script `YoutubeCLI.py` utilizando o ambiente virtual configurado no diretório.

**Exemplo de comando:**
```powershell
& "C:\Users\amori\Documents\CLI-Functions\youtube-cli\.venv\Scripts\python.exe" "C:\Users\amori\Documents\CLI-Functions\youtube-cli\YoutubeCLI.py" search "Python Tutorial"
```

### Comandos Principais:
- `search <termo>`: Busca vídeos no YouTube.
- `details <video_id>`: Obtém estatísticas e descrição de um vídeo.
- `transcript <video_id>`: Extrai a transcrição (legenda) do vídeo.
- `download <url>`: Baixa o vídeo ou áudio (padrão para a pasta Downloads do sistema).
- `comments <video_id>`: Lista comentários relevantes.
- `channel <channel_id>`: Obtém informações de um canal.

---

## 🔑 Configuração da API do YouTube (Obrigatório)

Esta ferramenta requer uma **YouTube Data API v3 Key** para realizar buscas e obter metadados. Sem ela, apenas o comando de download funcionará limitadamente.

### Passo a Passo para Obter sua API Key:

1.  **Google Cloud Console:**
    - Acesse o [Google Cloud Console](https://console.cloud.google.com/).
    - Se for seu primeiro acesso, aceite os termos de serviço.
    - No topo da página, clique em **"Selecionar um projeto"** (ou no nome do projeto atual) e clique em **"Novo Projeto"**. Dê um nome como "Meu-YouTube-CLI" e clique em **Criar**.

2.  **Ativar a API do YouTube:**
    - No menu lateral esquerdo, vá em **APIs e Serviços** > **Biblioteca**.
    - Na barra de pesquisa, digite **"YouTube Data API v3"**.
    - Clique no resultado e depois no botão **Ativar**.

3.  **Criar Credenciais (API Key):**
    - Após ativar, você será levado para a página da API. Clique no botão **Criar Credenciais** no topo (ou vá em APIs e Serviços > Credenciais).
    - Selecione **Chave de API (API Key)**.
    - Uma janela aparecerá com sua chave (ex: `AIzaSy...`). **Copie e guarde esta chave com segurança.**

---

## ⚙️ Configuração do Ambiente (.env)

A ferramenta busca a chave de API em um arquivo `.env` localizado na raiz da pasta de funções (`C:\Users\amori\Documents\CLI-Functions\.env`).

1.  Vá até a pasta raiz: `C:\Users\amori\Documents\CLI-Functions\`.
2.  Crie ou edite o arquivo chamado `.env`.
3.  Adicione a seguinte linha, substituindo pelo valor que você copiou:
    ```env
    YOUTUBE_API_KEY=SUA_CHAVE_AQUI
    ```

---

## 📂 Downloads

Por padrão, todos os vídeos são baixados para a pasta de Downloads do seu Windows: `C:\Users\amori\Downloads`.

- Para baixar apenas o áudio: `download <url> --audio`
- Para especificar outro local: `download <url> --out "D:/MeusVideos"`

---

## 🛠️ Requisitos Técnicos
- **Python 3.10+**
- **FFmpeg** (Opcional, mas altamente recomendado para conversões de áudio e downloads em alta qualidade).
- Dependências listadas em `requirements.txt` (já instaladas no `.venv`).
