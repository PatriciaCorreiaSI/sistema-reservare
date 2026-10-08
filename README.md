# 📅 Reservare

[![CI](https://github.com/PatriciaCorreiaSI/sistema-reservare/actions/workflows/ci.yml/badge.svg)](https://github.com/PatriciaCorreiaSI/sistema-reservare/actions/workflows/ci.yml)

Sistema de reserva de recursos compartilhados — salas, equipamentos e estações de trabalho — construído com foco em **integridade de dados sob concorrência**.

> ⚠️ **Em construção.** Este repositório documenta um projeto em andamento, etapa por etapa.
> Fase atual: **Etapa 7 — front-end**, back-end adaptado (rotas sob `/api`, refresh em cookie `httpOnly`), `frontend/` criado com Vite, proxy e tipos gerados do OpenAPI; CI conferindo os dois lados. As reservas funcionam pela
> API, o teste de concorrência está verde e a consulta de horários livres devolve as lacunas do
> dia. No front, o login e a listagem de recursos já falam com a API, com o token em memória. O CI do
> GitHub Actions roda lint, tipos, os 117 testes e as migrations a cada push, contra um Postgres
> próprio.

---

## O problema

Uma equipe compartilha recursos limitados e precisa reservá-los por janelas de tempo. O desafio não é o cadastro — é garantir que **duas pessoas nunca reservem o mesmo recurso no mesmo horário**, inclusive quando as duas requisições chegam no mesmo instante.

## A regra que dá razão a este projeto

> **Duas reservas ativas nunca podem se sobrepor no mesmo recurso.**

Verificar disponibilidade antes de inserir **não** resolve isso: entre a verificação e a gravação existe uma janela em que outra transação insere. Por isso a garantia é declarada no próprio PostgreSQL, com uma constraint de exclusão sobre `tstzrange` — de forma que a regra não dependa de o código lembrar de conferir.

```sql
CONSTRAINT ex_reserva_sem_sobreposicao
    EXCLUDE USING gist (id_recurso WITH =, periodo WITH &&)
    WHERE (cancelada_em IS NULL)
```

Lê-se: *para qualquer par de linhas, se o recurso é o mesmo **e** os períodos se sobrepõem, recuse* — considerando apenas as reservas que não foram canceladas. O porquê desse `WHERE`, e das duas alternativas descartadas, está no [ADR 0007](docs/adr/0007-predicado-pelo-cancelamento.md).

Demonstrar isso, com teste de concorrência que prove o comportamento, é o objetivo central do projeto.

### Verificando o invariante

O esquema é criado pela migration, e a prova roda contra o banco que ela construiu — em SQL puro,
sem nenhuma linha de Python:

```bash
docker compose up -d db                        # espere ficar (healthy)
cd backend && uv run alembic upgrade head      # cria as tabelas, a extensão e a EXCLUDE
cd ..

docker compose cp docs/prova-invariante.sql db:/tmp/prova.sql
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /tmp/prova.sql'
```

[`docs/prova-invariante.sql`](docs/prova-invariante.sql) percorre sete casos, cada um com o resultado esperado escrito antes de rodar — entre eles: reservas sobrepostas são recusadas; reservas que apenas se encostam (`[14h,16h)` e `[16h,18h)`) são as duas aceitas; e cancelar uma reserva devolve o horário para quem vier depois.

---

## Status

| Etapa | Situação |
|---|---|
| Modelagem de dados | ✅ concluída |
| Fundação: ambiente, container, lint | ✅ concluída |
| Migrations e constraints | ✅ concluída — `alembic upgrade head` cria as três tabelas, a extensão e a `EXCLUDE` num banco vazio; `downgrade base` desfaz |
| API em camadas | ✅ concluída — CRUD de `recurso` em router → service → repository, com testes isolados por transação num banco próprio |
| Autenticação e autorização | ✅ concluída — login, refresh com rotação e detecção de reuso, logout que revoga de verdade, cadastro de usuário só para admin ([ADR 0012](docs/adr/0012-jwt-curto-com-refresh-no-banco.md), [ADR 0013](docs/adr/0013-transportar-token-no-cabecalho-authorization.md)) |
| Reservas, concorrência e estados | ✅ concluída — criar, listar, consultar e cancelar reservas, consulta de horários livres, sobreposição recusada pelo banco e traduzida em `409`; testes de IDOR e de concorrência verdes ([ADR 0014](docs/adr/0014-traduzir-violacao-da-constraint-pelo-nome.md) a [0019](docs/adr/0019-disponibilidade-como-lacunas-livres.md)) |
| Testes e integração contínua | ✅ concluída — CI verde a cada push: lint, tipos, a suíte de testes com relatório de cobertura e vaivém das migrations contra Postgres de serviço ([ADR 0021](docs/adr/0021-testar-pelo-que-a-coisa-testada-depende.md), [ADR 0022](docs/adr/0022-container-de-servico-e-variaveis-no-workflow.md)); cobertura lida como alarme, e cada linha sem teste tem o porquê no ROADMAP |
| Front-end | 🔨 em andamento — refresh em cookie `httpOnly`, proxy do Vite sob `/api`, tipos gerados do OpenAPI, React Router declarativo ([ADR 0023](docs/adr/0023-guardar-refresh-em-cookie-httponly.md) a [0026](docs/adr/0026-rotear-com-react-router-declarativo.md)) e fuso do recurso na tela (emenda ao [ADR 0018](docs/adr/0018-fuso-unico-do-sistema.md)); back-end pronto; `frontend/` com Vite + React + TS, proxy, ESLint + Prettier e tipos gerados, conferidos pelo CI em dois jobs (emenda ao [ADR 0022](docs/adr/0022-container-de-servico-e-variaveis-no-workflow.md)); cliente `openapi-fetch` tipado e TanStack Query ligado; sessão com o token em memória e os primeiros hooks (login e listagem de recursos); faltam roteador, renovação do token no F5 e telas |
| Deploy | ⏳ |

Nada é listado como pronto antes de estar funcionando.

---

## Stack

**Back-end** — Python 3.14 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · Alembic · PostgreSQL 16 · `pwdlib` (Argon2) · PyJWT
**Front-end** — Vite · React · TypeScript · TanStack Query
**Qualidade** — pytest · Playwright · ruff · mypy · GitHub Actions
**Infra** — Docker Compose

As justificativas de cada escolha estão no [roadmap](docs/ROADMAP.md#4-stack-e-por-quê).

---

## Desenvolvimento

Requisito: [uv](https://docs.astral.sh/uv/). Ele lê o `backend/.python-version` e instala o Python 3.14 sozinho — não é preciso ter a versão na máquina.

```bash
git clone https://github.com/PatriciaCorreiaSI/sistema-reservare.git
cd sistema-reservare
cp .env.example .env            # preencha as chaves; DB_HOST=127.0.0.1 no host
docker compose up -d db         # espere ficar (healthy) em `docker compose ps`

cd backend
uv sync
uv run alembic upgrade head     # cria as tabelas no banco do compose
uv run uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000` — `/health` responde `200`, e `/docs` traz a documentação interativa. O `.env` é obrigatório: a URL do banco é montada a partir dele na importação, sem valor padrão — a ausência de uma chave falha alto, de propósito.

### Testes

Precisam do `db` no ar e de um banco `reservare_test` criado uma vez à mão (`CREATE DATABASE reservare_test;` no psql do container). O `conftest.py` aplica as migrations nele a cada rodada; cada teste roda numa transação desfeita no fim ([ADR 0011](docs/adr/0011-isolar-teste-em-transacao-desfeita-no-fim.md)).

```bash
cd backend && uv run pytest
```

No CI, o mesmo `pytest` roda com `--cov=app --cov-report=term-missing`: o relatório lista as linhas
que nenhum teste executou e nunca reprova o push — cobertura é alarme, não meta
([ADR 0021](docs/adr/0021-testar-pelo-que-a-coisa-testada-depende.md)).

### Verificação antes do commit

O repositório usa `pre-commit` para rodar `ruff` e `mypy` a cada `git commit`. **Depois de clonar, o hook precisa ser instalado uma vez:**

```bash
cd backend && uv run pre-commit install
```

Esse passo não é automático, e a razão importa: o hook do Git vive em `.git/hooks/`, que **não é versionado** e portanto não vem junto no clone. Sem o comando acima, os commits passam sem verificação nenhuma — e nada na tela avisa que a proteção não está ali.

Para rodar as verificações à mão, sem commitar:

```bash
cd backend && uv run pre-commit run --all-files
```

---

## Documentação

| Documento | O que contém |
|---|---|
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Escopo, plano de execução e o que cada etapa ensina |
| [`docs/modelo.md`](docs/modelo.md) | Modelo de dados, restrições e regras de negócio |
| [`docs/api.md`](docs/api.md) | Contrato HTTP: schemas por direção, rotas, códigos de resposta e o porquê de cada escolha |
| [`docs/esquema-alvo.sql`](docs/esquema-alvo.sql) | O DDL escrito à mão na Etapa 1 — congelado como registro histórico; a partir da migration, a verdade sobre o esquema é o Alembic |
| [`docs/prova-invariante.sql`](docs/prova-invariante.sql) | Sete casos que demonstram, em SQL puro, o que o banco aceita e o que recusa |
| [`docs/adr/`](docs/adr/) | Decisões de arquitetura, com alternativas descartadas e consequências |
| [`docs/aprendizados.md`](docs/aprendizados.md) | Um conceito por linha — o que cada etapa ensinou na prática |

---

## Sobre este projeto

É um projeto de estudo, construído deliberadamente como exercício de **engenharia de software** e não como demonstração de framework. O tema é o veículo; o conteúdo é modelagem com garantias no banco, concorrência, estratégia de testes e automação.

Sobre o uso de IA: ela é usada como revisora e tutora — para explicar conceitos, apontar falhas e sugerir alternativas. As decisões de arquitetura são minhas, ficam registradas em ADRs com as opções que descartei, e vale uma regra simples: **nenhuma linha entra neste repositório que eu não consiga explicar em voz alta.**

---

## Autora

**Patricia Correia**
