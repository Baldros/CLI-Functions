# Mapeamento Inicial da Steam API para `steam-cli`

## Objetivo

Este documento resume o que da para buscar via Steam para um CLI proprio, separando:

- APIs oficiais do Steamworks Web API
- endpoints oficiais da Store
- endpoints de storefront nao oficiais, mas amplamente usados

Tambem marca o tipo de acesso necessario:

- `public`: sem chave
- `user key`: chave Web API normal de usuario
- `publisher key`: chave de parceiro/publicador do Steamworks

## Leitura rapida

Se a ideia e fazer um CLI pessoal, as interfaces mais uteis sao:

- `IPlayerService`
- `ISteamUser`
- `ISteamUserStats`
- `ISteamNews`
- `IStoreService`
- `ISteamWebAPIUtil`

E para cobrir preco, requisitos de sistema e reviews:

- `store.steampowered.com/appreviews/<appid>?json=1` para reviews
- `store.steampowered.com/api/appdetails?appids=<appid>` para preco e requisitos

Observacao importante:

- `appreviews` tem documentacao oficial da Steam
- `appdetails` nao aparece como Steamworks Web API oficial; e um endpoint de storefront amplamente usado. Vale marcar isso no CLI como `nao oficial`

## 1. Endpoints mais uteis para um CLI pessoal

| Tema | Interface / metodo | Acesso | Oficial | O que retorna | Observacoes |
| --- | --- | --- | --- | --- | --- |
| Resolver perfil customizado | `ISteamUser/ResolveVanityURL` | `user key` | sim | Converte vanity URL em `steamid64` | Excelente para entrada amigavel no CLI |
| Perfil basico | `ISteamUser/GetPlayerSummaries` | `user key` | sim | Nome, avatar, URL do perfil, estado basico | Bom para `steam user summary` |
| Amigos | `ISteamUser/GetFriendList` | `user key` | sim | Lista de amigos | Se a lista for privada pode retornar `401` |
| Banimentos | `ISteamUser/GetPlayerBans` | `user key` | sim | VAC bans, game bans, community ban, economy ban | Bom para auditoria rapida |
| Grupos | `ISteamUser/GetUserGroupList` | `user key` | sim | Lista de grupos do usuario | Util, mas menos prioritaria |
| Biblioteca | `IPlayerService/GetOwnedGames` | `user key` | sim | Jogos possuidos, `appid`, nome, playtime | Core do CLI |
| Jogos recentes | `IPlayerService/GetRecentlyPlayedGames` | `user key` | sim | Jogos recentes e tempo nas ultimas 2 semanas | Core do CLI |
| Tempo em um jogo | `IPlayerService/GetSingleGamePlaytime` | `user key` | sim | Tempo jogado de um app especifico | Bom para consultas pontuais |
| Nivel Steam | `IPlayerService/GetSteamLevel` | `user key` | sim | Nivel da conta | Simples de adicionar |
| Badges | `IPlayerService/GetBadges` | `user key` | sim | Badges e progresso | Pode ser legal para perfil |
| Comunidade | `IPlayerService/GetCommunityBadgeProgress` | `user key` | sim | Progresso do badge da comunidade | Nichado |
| Achievements do usuario | `ISteamUserStats/GetPlayerAchievements` | `user key` | sim | Achievements desbloqueados por usuario em um app | Muito util |
| Stats do usuario | `ISteamUserStats/GetUserStatsForGame` | `user key` | sim | Stats do usuario para um app | Muito util |
| Schema de achievements | `ISteamUserStats/GetSchemaForGame` | `user key` | sim | Lista de achievements/stats de um jogo | Bom para enriquecer saida |
| Percentual global de achievements | `ISteamUserStats/GetGlobalAchievementPercentagesForApp` | `public` | sim | Percentual global por achievement | Bom para comparacoes |
| Jogadores online agora | `ISteamUserStats/GetNumberOfCurrentPlayers` | `public` | sim | Numero atual de jogadores online | Muito bom para consultas rapidas |
| Noticias / patch notes | `ISteamNews/GetNewsForApp` | `public` | sim | Noticias, anuncios e posts por app | Bom para `steam app news` |
| Catalogo de apps | `IStoreService/GetAppList` | `public` ou `user key` | sim | Lista de apps com filtros/paginacao | Base para busca por nome/appid |
| Lista de APIs suportadas | `ISteamWebAPIUtil/GetSupportedAPIList` | `public` | sim | Mapa das APIs/metodos disponiveis | Bom para diagnostico/descoberta |
| Info do servidor da API | `ISteamWebAPIUtil/GetServerInfo` | `public` | sim | Info basica do servidor | Baixa prioridade |

## 2. Preco, requisitos de sistema e reviews

Esta e a parte que faltava no mapeamento anterior.

### 2.1 Reviews de usuarios

Fonte recomendada:

- `GET https://store.steampowered.com/appreviews/<appid>?json=1`

Status:

- `oficial`: sim
- `acesso`: `public`

O que da para buscar:

- score agregado
- descricao do score (`review_score_desc`)
- total de reviews positivas
- total de reviews negativas
- total de reviews da consulta
- texto de cada review
- idioma da review
- tempo total jogado pelo autor
- tempo jogado nas ultimas 2 semanas
- tempo jogado no momento em que a review foi escrita
- data de criacao
- se a compra foi feita na Steam ou fora dela
- paginacao por cursor

Parametros mais uteis:

- `filter=recent|updated|all`
- `language=all`
- `review_type=all|positive|negative`
- `purchase_type=all|steam|non_steam_purchase`
- `num_per_page=1..100`
- `cursor=*`
- `day_range=365`
- `filter_offtopic_activity=0`

Uso no CLI:

- `steam reviews summary <appid>`
- `steam reviews list <appid>`
- `steam reviews negative <appid>`
- `steam reviews recent <appid>`

### 2.2 Preco de jogos

Voce tem dois caminhos.

#### A. Preco oficial de parceiro

Fonte:

- `ISteamUser/GetAppPriceInfo`

Status:

- `oficial`: sim
- `acesso`: `publisher key`

O que retorna:

- `packageid`
- `currency`
- `initial_price`
- `final_price`
- `discount_percent`

Limitacao:

- nao serve para um CLI pessoal comum, porque exige chave de publicador e chamada em servidor seguro

#### B. Preco publico de storefront

Fonte:

- `GET https://store.steampowered.com/api/appdetails?appids=<appid>&cc=<country>&l=<lang>`

Status:

- `oficial`: nao como Steamworks Web API
- `acesso`: `public`

Campos uteis geralmente retornados:

- `price_overview.currency`
- `price_overview.initial`
- `price_overview.final`
- `price_overview.discount_percent`
- `price_overview.initial_formatted`
- `price_overview.final_formatted`
- `packages`
- `package_groups`
- `package_groups[].subs[].price_in_cents_with_discount`

Uso no CLI:

- `steam app price <appid> --cc us`
- `steam app price <appid> --cc br`
- `steam app packages <appid>`

### 2.3 Requisitos de sistema

Melhor fonte pratica:

- `GET https://store.steampowered.com/api/appdetails?appids=<appid>&filters=pc_requirements,mac_requirements,linux_requirements`

Status:

- `oficial`: nao como Steamworks Web API
- `acesso`: `public`

Campos uteis:

- `pc_requirements.minimum`
- `pc_requirements.recommended`
- `mac_requirements.minimum`
- `mac_requirements.recommended`
- `linux_requirements.minimum`
- `linux_requirements.recommended`
- `platforms.windows`
- `platforms.mac`
- `platforms.linux`

Observacao:

- os requisitos costumam vir em HTML; o CLI vai precisar limpar tags para ficar legivel

Uso no CLI:

- `steam app requirements <appid>`
- `steam app requirements <appid> --platform windows`

## 3. Outros dados muito interessantes que o endpoint `appdetails` costuma expor

Mesmo sendo storefront e nao Steamworks Web API oficial, esse endpoint costuma ser extremamente util para enriquecer o CLI.

Campos comuns:

- `type`
- `name`
- `steam_appid`
- `required_age`
- `is_free`
- `dlc`
- `detailed_description`
- `about_the_game`
- `short_description`
- `supported_languages`
- `header_image`
- `website`
- `developers`
- `publishers`
- `packages`
- `package_groups`
- `platforms`
- `metacritic`
- `categories`
- `genres`
- `screenshots`
- `movies`
- `recommendations.total`
- `achievements.total`
- `release_date`
- `support_info`
- `content_descriptors`

Isso abre espaco para comandos como:

- `steam app details <appid>`
- `steam app media <appid>`
- `steam app genres <appid>`
- `steam app metacritic <appid>`
- `steam app release-date <appid>`

## 4. Mapeamento por categoria de informacao

### Usuario e identidade

- nome e avatar
- URL do perfil
- `steamid64`
- vanity URL -> SteamID
- amigos
- grupos
- banimentos
- nivel da conta
- badges

Fontes principais:

- `ISteamUser`
- `IPlayerService`

### Biblioteca e uso

- lista de jogos possuidos
- nome do jogo
- `appid`
- tempo total jogado
- tempo jogado recentemente
- tempo jogado em um jogo especifico

Fontes principais:

- `IPlayerService`

### Achievements e stats

- achievements do usuario
- schema do jogo
- stats do usuario
- percentual global de achievements
- numero atual de jogadores online

Fontes principais:

- `ISteamUserStats`

### Loja, catalogo e metadados do app

- lista de apps
- nome
- descricao curta e longa
- linguas suportadas
- plataformas
- categorias
- generos
- data de lancamento
- screenshots
- videos
- achievements totais
- recomendacoes totais

Fontes principais:

- `IStoreService/GetAppList`
- storefront `appdetails`

### Preco e comercial

- preco atual
- preco cheio
- percentual de desconto
- moeda
- pacotes e opcoes de compra

Fontes principais:

- `ISteamUser/GetAppPriceInfo` para parceiros
- storefront `appdetails` para uso publico

### Reviews e reputacao

- score agregado
- descricao do score
- total positivo / negativo
- reviews individuais
- idioma
- playtime do autor
- data de criacao

Fonte principal:

- store `appreviews`

### Noticias e atualizacoes

- posts
- patch notes
- anuncios por app

Fonte principal:

- `ISteamNews/GetNewsForApp`

## 5. APIs oficiais adicionais que existem, mas provavelmente ficam para depois

Estas interfaces existem na documentacao oficial, mas fogem do escopo do CLI pessoal inicial:

- `IBroadcastService`
- `ICheatReportingService`
- `ICloudService`
- `IEconMarketService`
- `IEconService`
- `IGameInventory`
- `IGameNotificationsService`
- `IGameServersService`
- `IInventoryService`
- `ILobbyMatchmakingService`
- `IPartnerFinancialsService`
- `IPublishedFileService`
- `ISiteLicenseService`
- `ISteamApps` em funcoes de parceiro
- `ISteamCommunity`
- `ISteamEconomy`
- `ISteamGameServerStats`
- `ISteamLeaderboards`
- `ISteamMicroTxn`
- `ISteamMicroTxnSandbox`
- `ISteamPublishedItemSearch`
- `ISteamPublishedItemVoting`
- `ISteamRemoteStorage`
- `ISteamUserAuth`
- `IWorkshopService`

Elas podem servir mais tarde para:

- Workshop / UGC
- market / trading / inventory
- lobbies
- microtransacoes
- game servers
- ownership/licencas detalhadas
- financeiro de parceiro

## 6. Recomendacao de escopo para o `steam-cli` v1

Eu comecaria com estes comandos:

- `steam user resolve <vanity>`
- `steam user summary <steamid|vanity>`
- `steam user friends <steamid|vanity>`
- `steam user bans <steamid|vanity>`
- `steam games owned <steamid|vanity>`
- `steam games recent <steamid|vanity>`
- `steam games playtime <steamid|vanity> <appid>`
- `steam app details <appid>`
- `steam app price <appid> [--cc br]`
- `steam app requirements <appid> [--platform windows|mac|linux]`
- `steam app reviews <appid>`
- `steam app reviews-summary <appid>`
- `steam app news <appid>`
- `steam app current-players <appid>`
- `steam app achievements <appid> <steamid|vanity>`

## 7. Notas de arquitetura para o CLI

- Tratar `Steamworks Web API` e `Storefront` como provedores separados
- Marcar cada comando como `official` ou `storefront`
- Marcar cada comando como `public`, `user-key` ou `publisher-key`
- Ter um resolvedor central de `vanity -> steamid64`
- Ter limpeza de HTML para `requirements`, `about_the_game` e `reviews`
- Ter suporte a `--cc` e `--lang` para preco e localizacao
- Ter fallback elegante quando perfil, biblioteca ou amigos forem privados

## 8. Fontes

Fontes oficiais:

- Steamworks Web API overview: `https://partner.steamgames.com/documentation/webapi`
- Steamworks Web API reference: `https://partner.steamgames.com/doc/webapi`
- `IPlayerService`: `https://partner.steamgames.com/doc/webapi/IPlayerService`
- `ISteamUser`: `https://partner.steamgames.com/doc/webapi/ISteamUser`
- `ISteamUserStats`: `https://partner.steamgames.com/doc/webapi/ISteamUserStats`
- `ISteamNews`: `https://partner.steamgames.com/doc/webapi/ISteamNews`
- `ISteamApps`: `https://partner.steamgames.com/doc/webapi/ISteamApps`
- `IStoreService`: `https://partner.steamgames.com/doc/webapi/IStoreService`
- `ISteamWebAPIUtil`: `https://partner.steamgames.com/doc/webapi/ISteamWebAPIUtil`
- Reviews da Store: `https://partner.steamgames.com/doc/store/getreviews`

Fonte complementar para storefront `appdetails`:

- `https://github-wiki-see.page/m/Revadike/InternalSteamWebAPI/wiki/Get-App-Details`

## 9. Decisao pratica

Para o projeto atual, o melhor caminho e:

1. usar API oficial para usuario, biblioteca, achievements, stats, noticias e catalogo
2. usar `appreviews` para reviews
3. usar `appdetails` para preco, requisitos e metadados ricos de store

Isso entrega um CLI muito util sem precisar de MCP e sem entrar nas areas de parceiro da Steam.
