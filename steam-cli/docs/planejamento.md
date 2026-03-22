# Planejamento Estrategico e Arquitetural do `steam-cli`

## 1. Objetivo

Depois do `docs/mapeamento_inicial.md`, o proximo passo nao e listar mais endpoints, mas decidir como transformar esse universo num CLI utilizavel por humano e por agente de terminal.

O objetivo do `steam-cli` v1 deve ser:

- expor informacoes relevantes da Steam por comandos simples
- devolver saida previsivel para consumo por Agentes de AI e humanos
- separar claramente o que vem de API oficial, storefront e cliente desktop
- evitar acoplar a arquitetura a partes mais frageis do ecossistema Steam

Neste momento, o escopo estrategico da v1 fica em 3 trilhas:

1. aquisicao de informacoes sobre o proprio usuario
2. informacoes sobre jogos, preco, requisitos e metadados
3. comandos de uso do app da Steam via terminal

## 2. Premissas do produto

O `steam-cli` deve ser pensado como um utilitario local, orientado a automacao.

Isso implica algumas decisoes:

- o CLI precisa funcionar bem tanto em uso manual quanto chamado por outro agente
- cada comando deve ter contrato claro de entrada e saida
- erros devem ser explicitos e classificaveis
- capacidades com menor estabilidade devem ser marcadas como `experimental`
- capacidades que dependem de chave devem ser claramente separadas das publicas

## 3. Tese arquitetural

O projeto deve ser dividido em 3 fronteiras tecnicas, porque elas tem caracteristicas muito diferentes:

### 3.1 Provedor `steam_web_api`

Responsavel por chamadas oficiais do Steamworks Web API.

Uso principal:

- identidade do usuario
- perfil basico
- biblioteca
- jogos recentes
- playtime
- bans
- grupos
- nivel
- badges
- achievements e stats
- noticias
- catalogo de apps

Caracteristicas:

- maior estabilidade contratual
- parte das chamadas exige `user key`
- bom para informacao estruturada

### 3.2 Provedor `steam_storefront`

Responsavel por endpoints da Store e do storefront.

Uso principal:

- preco
- requisitos
- descricao curta e longa
- generos
- publishers
- developers
- plataformas
- screenshots
- videos
- reviews
- recomendacoes
- release date

Caracteristicas:

- muito util na pratica
- parcialmente nao oficial no sentido Steamworks Web API
- precisa de tratamento de HTML e campos inconsistentes

### 3.3 Provedor `steam_client`

Responsavel por interagir com o aplicativo Steam instalado na maquina.

Uso principal:

- abrir Biblioteca
- abrir Friends
- abrir Downloads
- abrir Settings
- abrir Store
- abrir pagina de jogo
- lancar jogo
- instalar jogo

Caracteristicas:

- depende do cliente desktop estar instalado e associado ao protocolo `steam://`
- comportamento pode variar por versao do cliente e sistema operacional
- parte dos comandos e claramente menos confiavel que as APIs HTTP

Essa separacao e a decisao arquitetural mais importante do projeto.

## 4. Recomendacao de stack

Para a primeira implementacao, a stack mais pragmatica e Python.

Motivos:

- otimo para CLIs locais
- simples integracao com `subprocess` e launcher do sistema
- ecossistema bom para HTTP, parsing e serializacao
- facil de integrar com agentes de terminal

Sugestao de stack:

- `Typer` para CLI
- `httpx` para HTTP
- `pydantic` para modelos normalizados
- `selectolax` ou `BeautifulSoup` para limpar HTML de requisitos e descricoes
- `rich` apenas se quisermos tabela/colorizacao no modo humano

Se quisermos manter a porta aberta para outra linguagem depois, o importante e preservar a divisao de camadas, nao a stack em si.

## 5. Estrutura de modulos recomendada

```text
steam_cli/
  cli.py
  config.py
  errors.py
  models/
    user.py
    app.py
    review.py
    result.py
  commands/
    user.py
    app.py
    client.py
  services/
    identity.py
    app_resolver.py
    app_info.py
    client_actions.py
  providers/
    steam_web_api.py
    steam_storefront.py
    steam_client.py
  renderers/
    text.py
    json.py
  launchers/
    windows.py
    posix.py
  cache/
    store.py
```

Leitura da estrutura:

- `commands/`: parseia input do CLI e chama servicos
- `services/`: orquestra resolucao, composicao e fallback
- `providers/`: fala com cada backend externo
- `renderers/`: cuida da saida
- `launchers/`: encapsula abertura de `steam://...` por SO

## 6. Modelo mental do CLI

O CLI deve ser orientado a recursos, nao a endpoints.

Sugestao de namespaces:

- `steam user ...`
- `steam games ...`
- `steam app ...`
- `steam client ...`
- `steam diagnose ...`

Comandos base de v1:

- `steam user resolve <vanity>`
- `steam user summary <steamid|vanity>`
- `steam user friends <steamid|vanity>`
- `steam user bans <steamid|vanity>`
- `steam user level <steamid|vanity>`
- `steam games owned <steamid|vanity>`
- `steam games recent <steamid|vanity>`
- `steam games playtime <steamid|vanity> <appid>`
- `steam app search <name>`
- `steam app details <appid>`
- `steam app price <appid> [--cc br]`
- `steam app requirements <appid> [--platform windows|mac|linux]`
- `steam app reviews <appid>`
- `steam app reviews-summary <appid>`
- `steam app news <appid>`
- `steam app current-players <appid>`
- `steam client open library`
- `steam client open friends`
- `steam client open downloads`
- `steam client open settings`
- `steam client open store`
- `steam client open store-app <appid>`
- `steam client open community-app <appid>`
- `steam client run <appid>`
- `steam client install <appid>`

## 7. Contrato de saida

Esse ponto e central, porque o usuario quer integrar o script em um agente de terminal.

O CLI deve suportar pelo menos 2 modos:

- `--format text`: saida humana resumida
- `--format json`: saida estruturada e estavel

Idealmente, toda resposta deveria seguir um envelope comum:

```json
{
  "ok": true,
  "source": "steam_web_api",
  "official": true,
  "experimental": false,
  "data": {}
}
```

Para erros:

```json
{
  "ok": false,
  "error_code": "profile_private",
  "message": "Friend list is not visible for this profile.",
  "source": "steam_web_api"
}
```

Campos recomendados no envelope:

- `source`
- `official`
- `auth_type`
- `experimental`
- `warnings`
- `data`

Isso e importante porque o agente chamador pode decidir automaticamente se confia, reexecuta ou tenta fallback.

## 8. Estrategia para o topico 1: informacoes sobre si mesmo

Esse deve ser o primeiro pilar implementado.

Motivo:

- e a parte mais previsivel
- depende mais de API oficial
- gera valor cedo
- ajuda a validar identidade, config e tratamento de privacidade

### 8.1 Escopo do pilar 1

Prioridade alta:

- resolver vanity URL
- resumo do perfil
- perfil URL
- avatar
- steamid64
- bans
- biblioteca
- jogos recentes
- playtime por app
- nivel

Prioridade media:

- amigos
- grupos
- badges

Prioridade depois da base:

- achievements por jogo
- stats por jogo

### 8.2 Arquitetura desse pilar

Criar um `IdentityService` central com responsabilidade por:

- detectar se a entrada e `vanity`, `steamid64` ou talvez URL
- resolver para `steamid64`
- reutilizar esse id em todos os comandos subsequentes

Esse servico evita duplicacao de logica em `summary`, `friends`, `owned`, `recent`, `bans`, etc.

## 9. Estrategia para o topico 2: informacoes sobre jogos

Esse sera o segundo pilar, mas precisa de composicao entre fontes.

Um unico comando `steam app details <appid>` provavelmente vai consolidar dados de mais de um lugar.

### 9.1 Modelo recomendado

Criar um `AppInfoService` que saiba agregar:

- `IStoreService/GetAppList` para busca e resolucao de nome -> `appid`
- `appdetails` para metadados ricos
- `appreviews` para reputacao
- `ISteamNews/GetNewsForApp` para noticias
- `ISteamUserStats/GetNumberOfCurrentPlayers` para jogadores atuais

### 9.2 Separar "detalhe bruto" de "visoes"

Em vez de um comando gigante que sempre faz tudo, e melhor separar:

- `steam app details <appid>`
- `steam app price <appid>`
- `steam app requirements <appid>`
- `steam app media <appid>`
- `steam app reviews-summary <appid>`

Depois, se quisermos, podemos criar um comando agregado:

- `steam app overview <appid>`

### 9.3 Ponto de atencao

`appdetails` sera extremamente importante, mas deve entrar na arquitetura como `storefront`, nao como "oficial Steamworks". Isso precisa aparecer na implementacao e na documentacao do comando.

## 10. Estrategia para o topico 3: uso do app da Steam via terminal

Aqui esta a parte mais sensivel do planejamento.

A conclusao estrategica e:

- sim, vale a pena suportar interacao com o cliente Steam
- mas isso deve nascer como um subsistema separado
- e a v1 deve focar em acoes com maior previsibilidade

### 10.1 O que a pesquisa indica

Pelos materiais da Valve Developer Community, o protocolo `steam://` continua sendo o mecanismo central para abrir e acionar o cliente Steam. A propria documentacao alerta que alguns comandos nao sao mais funcionais e que a lista pode estar incompleta.

O que parece mais confiavel para v1:

- `steam://open/games`
- `steam://open/friends`
- `steam://open/downloads`
- `steam://open/news`
- `steam://open/settings`
- `steam://store/<appid>`
- `steam://run/<appid>`
- `steam://install/<appid>`
- `steam://url/GameHub/<appid>`
- `steam://url/StoreAppPage/<appid>`

O que deve entrar como `experimental`:

- `steam://nav/games/details/<appid>`
- `steam://open/games/details`
- comandos de navegacao finos dentro da Biblioteca

Motivo:

- a documentacao oficial diz que parte dos comandos deixou de funcionar
- ha relato documentado no Steam Client Beta, em 26 de maio de 2023, de `steam://nav/games/details/<appid>` nao estar funcionando como esperado

### 10.2 Leitura arquitetural disso

Nao devemos modelar `steam client` como "garantia de navegacao". Devemos modelar como "executor de intents".

Exemplo:

- intent: `open library`
- intent: `open store app 620`
- intent: `open community app 620`
- intent: `run game 620`

O `ClientActionService` traduz a intent para a melhor URI conhecida para aquele caso.

### 10.3 Tabela de estabilidade recomendada

Cada acao do cliente deve carregar um nivel:

- `stable`
- `experimental`
- `unsupported`

Exemplo inicial:

| Intent | URI sugerida | Nivel |
| --- | --- | --- |
| abrir Biblioteca | `steam://open/games` | `stable` |
| abrir Friends | `steam://open/friends` | `stable` |
| abrir Downloads | `steam://open/downloads` | `stable` |
| abrir Settings | `steam://open/settings` | `stable` |
| abrir pagina da Store de um app | `steam://store/<appid>` | `stable` |
| abrir pagina da Comunidade de um app | `steam://url/GameHub/<appid>` | `stable` |
| abrir pagina interna de store do app | `steam://url/StoreAppPage/<appid>` | `stable` |
| lancar jogo | `steam://run/<appid>` | `stable` |
| instalar jogo | `steam://install/<appid>` | `stable` |
| focar Biblioteca no jogo | `steam://nav/games/details/<appid>` | `experimental` |

### 10.4 Como expor isso no CLI

Namespace recomendado:

- `steam client open library`
- `steam client open friends`
- `steam client open downloads`
- `steam client open settings`
- `steam client open store`
- `steam client open store-app <appid>`
- `steam client open community-app <appid>`
- `steam client open library-app <appid>`
- `steam client run <appid>`
- `steam client install <appid>`

O comportamento de `open library-app` deve ser:

1. tentar a URI experimental conhecida
2. devolver no resultado que a capacidade e experimental
3. se falhar, orientar fallback para `store-app` ou `run`

### 10.5 Implementacao por SO

Precisamos encapsular a abertura do protocolo por sistema:

- Windows: `Start-Process "steam://..."`
- macOS: `open "steam://..."`
- Linux: `xdg-open "steam://..."`

Nao vale espalhar isso pelo codigo. Isso deve ficar em `launchers/`.

### 10.6 Recomendacao de postura de produto

Esse pilar nao deve ser descrito como automacao completa da interface da Steam.

A mensagem correta e:

- o CLI suporta `deep links` e `client intents`
- alguns sao estaveis
- alguns sao best effort

Isso evita prometer navegacao precisa onde a plataforma nao oferece contrato forte.

## 11. Cache, resiliencia e fallback

Mesmo na v1, vale prever um cache simples em disco para consultas de leitura.

Candidatos ideais:

- resolucao de vanity -> steamid64
- busca de app por nome
- `appdetails` por `appid` + `cc` + `lang`
- `GetAppList`

Estrutura simples ja resolve:

- cache por arquivo JSON
- TTL por tipo de recurso

Sugestao de TTL:

- `GetAppList`: longo
- perfil e owned games: medio
- preco e current players: curto

## 12. Configuracao e segredos

Recomendacao:

- `STEAM_API_KEY` por variavel de ambiente
- `STEAM_DEFAULT_CC`
- `STEAM_DEFAULT_LANG`
- `STEAM_OUTPUT_FORMAT`

Depois podemos adicionar arquivo local de config, mas variavel de ambiente basta para a v1.

## 13. Observabilidade e diagnostico

Vale prever desde cedo:

- `steam diagnose config`
- `steam diagnose auth`
- `steam diagnose client`

Esses comandos ajudam muito o usuario e o agente quando algo nao funciona.

Especialmente para o cliente desktop:

- verificar se o protocolo `steam://` esta associado
- verificar se o executavel parece instalado
- testar uma URI simples em modo `--dry-run`

## 14. Testes recomendados

O projeto vai precisar de 3 tipos de teste:

### 14.1 Testes unitarios

Para:

- resolucao de identidade
- composicao de servicos
- normalizacao de payload
- parsing e limpeza de HTML

### 14.2 Testes de contrato

Com fixtures de respostas reais ou anonimizada para:

- `GetPlayerSummaries`
- `GetOwnedGames`
- `appdetails`
- `appreviews`

### 14.3 Testes de cliente

Para `steam client`, o ideal e nao depender de abrir a GUI em teste automatizado.

Entao o teste principal deve validar:

- qual URI foi gerada
- qual launcher foi chamado
- qual nivel de estabilidade foi marcado

## 15. Roadmap de implementacao

### Fase 0: fundacao

- scaffold do projeto
- parser de CLI
- config
- envelope padrao de resultado
- tratamento de erros
- launcher por SO

### Fase 1: pilar usuario

- `resolve`
- `summary`
- `bans`
- `owned`
- `recent`
- `playtime`
- `level`

Essa fase valida identidade, auth, renderizacao e privacidade.

### Fase 2: pilar app/store

- `app search`
- `app details`
- `app price`
- `app requirements`
- `app reviews-summary`
- `app news`
- `app current-players`

Essa fase valida agregacao de fontes.

### Fase 3: pilar cliente desktop

- `open library`
- `open friends`
- `open downloads`
- `open settings`
- `open store-app`
- `open community-app`
- `run`
- `install`

`open library-app` entra apenas como `experimental`.

### Fase 4: refinamento

- cache
- `--format json` mais rico
- `diagnose`
- melhorias de busca por nome
- achievements/stats

## 16. Decisoes recomendadas agora

As decisoes mais importantes para travar antes de codar sao:

1. tratar `steam_web_api`, `steam_storefront` e `steam_client` como subsistemas separados
2. assumir Python como stack inicial
3. projetar o CLI com saida `json` estavel desde o inicio
4. tratar automacao do cliente Steam como `intent-based`, nao como controle fino de UI
5. marcar deep links de Biblioteca por app como `experimental`

## 17. Proposta objetiva de escopo v1

Se a ideia e maximizar valor com risco controlado, eu faria a v1 assim:

### Entram

- identidade e dados do usuario
- biblioteca e uso
- detalhes de app
- preco
- requisitos
- reviews agregadas
- current players
- noticias
- abrir Biblioteca
- abrir Friends
- abrir Downloads
- abrir Settings
- abrir Store/App
- abrir Community/App
- run/install

### Nao entram ainda

- automacao detalhada de Biblioteca por aba interna
- workflow complexo de login
- scraping visual da UI do cliente
- interacao com Workshop/market/inventory
- publisher-only APIs

## 18. Fontes de pesquisa para o topico do cliente Steam

Pesquisa consolidada em 21 de marco de 2026.

Fontes principais:

- Valve Developer Community, `Steam browser protocol`: `https://developer.valvesoftware.com/wiki/Steam_browser_protocol`
- Valve Developer Community, `Template:Steam/doc`: `https://developer.valvesoftware.com/wiki/Template:Steam/doc`
- Exemplo de `steam.desktop` com actions para Store, Community e Library: `https://gist.github.com/mdeguzis/68fad717a06625df4da0a9dd2d952bca`
- Discussao Steam Client Beta sobre `steam://nav/games/details/<appid>` quebrado em 2023-05-26: `https://steamcommunity.com/groups/SteamClientBeta/discussions/3/3842178984950303395/`

## 19. Conclusao

O projeto ja tem mapeamento suficiente para sair da fase de descoberta e entrar em implementacao.

Arquiteturalmente, a jogada correta e:

- construir primeiro as capacidades HTTP estaveis
- tratar a Steam desktop integration como um modulo separado
- suportar o cliente por intents e deep links, com niveis de estabilidade

Isso entrega valor rapido, preserva clareza para o agente chamador e evita que a parte mais fragil da plataforma contamine o resto da arquitetura.
