# ADR 0020 — Exigir token nas rotas de recurso

- **Data:** 2026-10-01
- **Situação:** aceita

## Contexto

As cinco rotas de `/recursos` nasceram na Etapa 2, antes de existir autenticação, e a Etapa 3 protegeu `/reservas` e `/usuarios`, mas não voltou nelas. Hoje, qualquer pessoa, sem token, cria, altera e remove recurso. A única rota do router que exige token é a disponibilidade. Este é o segundo item da OWASP API Top 10 de 2023, *Broken Authentication*. Remover um recurso em uso já devolve `409` pela FK, mas um recurso sem reserva some sem ninguém saber quem apagou.

## Decisão

- *Quem pode ler?* Autenticação: "você está logada?". A dependência é `obter_usuario_atual`, responde `401`.
- *Quem pode escrever?* Autorização por papel: "você é admin?". A dependência é `exigir_admin`, que chama a primeira e depois responde `403`.

Escolhi leitura para quem está logada e escrita só para admin: `GET /recursos` e `GET /recursos/{id}` levam `dependencies=[Depends(obter_usuario_atual)]`; `POST`, `PATCH` e `DELETE` levam `dependencies=[Depends(exigir_admin)]`. A verificação mora no decorador, não no parâmetro, porque nenhum handler de recurso usa quem chamou.

## Alternativas consideradas

- **Deixar tudo aberto (recurso é catálogo público)** — por que descartei: escrever é destrutivo, e a Etapa 7 vai expor a API na internet.

- **Tudo só para admin, leitura inclusive** — por que descartei: a usuária comum não veria a lista de salas, logo não conseguiria reservar.

- **Leitura pública, sem token; escrita admin** — por que descartei: a disponibilidade já exige token ([ADR 0019](0019-disponibilidade-como-lacunas-livres.md), a resposta é para quem está logada), e ter rotas vizinhas com regras diferentes no mesmo router é uma incoerência.

## Consequências

O ganho: toda escrita em recurso passa a ter autor conhecido, pelo token; o front da Etapa 7 nasce sabendo que recurso exige login. Custos: os testes de `test_recurso.py` passam a mandar `cabecalho_de`, e os que escrevem precisam da fixture `admin` em vez de `usuario`; entram testes novos de `401` e `403`; o `api.md` ganha `401` e `403` na coluna de erros das cinco rotas; nenhuma tela do Reservare funciona antes do login, nem a lista de salas. O que ficaria difícil: se um dia a lista de salas tiver de ser pública (uma tela antes do login), é tirar uma dependência de uma rota, e substituir este ADR.

## Como eu saberia que errei

Se alguém sem conta precisar ver as salas, ou uma usuária comum precisar cadastrar recurso: nesse caso, a resposta é um papel novo, não abrir a rota.
