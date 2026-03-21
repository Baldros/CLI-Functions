# Google CLI - Terminal Functions

Este projeto é um utilitário de terminal (CLI) desenvolvido em Python para integração direta com os serviços do **Gmail**, **Google Drive** e **Google Calendar**. Ele foi projetado para ser utilizado por agentes de IA e usuários avançados que precisam de automação de produtividade diretamente do console.

---

## 1. Visão Geral e Estratégia
O **Google CLI** utiliza a **Google API Python Client** e o fluxo de autenticação **OAuth 2.0 (Desktop App)**. 

### Diferenciais Técnicos:
- **Token Consolidado:** Diferente de muitas implementações, este CLI solicita todos os escopos necessários (Gmail, Drive, Calendar) de uma única vez, evitando reautenticações constantes.
- **Segurança:** Credenciais sensíveis e tokens de acesso são armazenados em arquivos locais (`credentials/` e `token/`), fora do código-fonte.
- **Saída Estruturada:** Suporta formatos `text`, `json`, `csv` e `ndjson`, facilitando o processamento por outros scripts ou IAs.

---

## 2. Estrutura de Pastas
Para o funcionamento correto, o projeto segue a seguinte hierarquia:

```text
CLI-Functions/google/
├── credentials/
│   └── client_secret.json    # Suas credenciais do Google Cloud (Obrigatório)
├── token/
│   └── token.json            # Cache de autenticação do usuário (Gerado após o 1º login)
├── .venv/                    # Ambiente virtual Python
├── GoogleCLI.py              # Script principal da aplicação
├── requirements.txt          # Dependências do projeto
└── README.md                 # Este guia
```

---

## 3. Configuração Passo a Passo

### 3.1 Google Cloud Console (Onde tudo começa)
Para usar este CLI, você precisa ser o "dono" de um aplicativo no Google Cloud:

1.  Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2.  **Crie um Novo Projeto:** Clique no seletor de projetos no topo e selecione "Novo Projeto".
3.  **Habilitar APIs:** Vá em "APIs e Serviços" > "Biblioteca" e habilite:
    - `Gmail API`
    - `Google Drive API`
    - `Google Calendar API`
4.  **Configurar Tela de Consentimento (OAuth Consent Screen):**
    - Escolha o tipo **External**.
    - Preencha os dados básicos (Nome do app, seu email).
    - **IMPORTANTE:** Em "Test Users", adicione o seu próprio e-mail do Gmail. Sem isso, o Google não permitirá o login.
5.  **Criar Credenciais:**
    - Vá em "Credenciais" > "Criar Credenciais" > **ID do cliente OAuth**.
    - Selecione o tipo **App de Desktop (Desktop App)**.
    - Baixe o arquivo JSON gerado.
6.  **Instalação Local:**
    - Renomeie o arquivo baixado para `client_secret.json`.
    - Coloque-o na pasta `CLI-Functions/google/credentials/`.

### 3.2 Ambiente Python
Abra o terminal na pasta do projeto e execute:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4. Configuração da Skill (Integração com Agente IA)

Para que o seu Agente de Terminal reconheça esses comandos, você precisa de uma **Skill**. O arquivo de definição da skill (geralmente um `SKILL.md`) deve estar na pasta de configuração do seu agente (ex: `.gemini/skills/google-cli/`).

### Prompt Recomendado para Configuração:
Se você estiver usando um agente como o Gemini CLI, pode simplesmente colar o seguinte prompt:

> "Configure a skill do Google CLI para mim. O script principal está em `C:\Caminho\Para\CLI-Functions\google\GoogleCLI.py`. Certifique-se de que os caminhos para o executável do Python no venv e o arquivo de token estejam corretos para o meu sistema operacional."

O agente irá ler o `GoogleCLI.py`, entender os comandos disponíveis e criar o arquivo de instrução necessário para usá-lo automaticamente.

---

## 5. Exemplos de Uso
```powershell
# Listar 5 emails da Inbox
python GoogleCLI.py gmail list --max-results 5

# Buscar arquivos no Drive
python GoogleCLI.py drive list --max-results 10

# Ver próximos eventos na agenda
python GoogleCLI.py calendar list-upcoming
```

---
*Desenvolvido para máxima eficiência e automação via CLI.*
