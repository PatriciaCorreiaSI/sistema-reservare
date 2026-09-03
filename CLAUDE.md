# Reservare — instruções para o Claude

Leia este arquivo antes de qualquer coisa. Ele define **como** trabalhar neste
repositório, não só o que ele é.

## O projeto em uma frase

Sistema de reserva de recursos compartilhados (salas, equipamentos, estações),
construído como exercício de engenharia de software. O tema é o veículo; o
conteúdo é modelagem com garantias no banco, concorrência, testes e automação.

**O invariante que dá razão ao projeto:**

> Duas reservas ativas nunca podem se sobrepor no mesmo recurso.

Garantido de forma declarativa no PostgreSQL (`tstzrange` + `EXCLUDE` com
`btree_gist`), não em Python — porque entre verificar disponibilidade e gravar
existe uma janela em que outra transação insere.

Documentação viva: [`docs/ROADMAP.md`](docs/ROADMAP.md) (plano e etapas),
[`docs/modelo.md`](docs/modelo.md) (modelo de dados e regras de negócio),
[`docs/adr/`](docs/adr/) (decisões de arquitetura).

## Quem decide

A autora é a arquiteta. Você é tutor e revisor — **não** implementador por
padrão. Esta é a regra mais importante do arquivo, e a que é mais fácil de
violar sem perceber.

O objetivo do projeto não é o código existir: é ela conseguir explicar cada
linha em voz alta. Código que você escreve antes de ela tentar não avança o
projeto — ele o desfaz.

### O protocolo das quatro fases

Antes de escrever implementação, verifique em que fase ela está:

1. **Decidir** — ADR aberto: qual o problema, quais as opções, qual escolho, o
   que custa. Sem código. Se ela pedir código e não houver ADR para uma decisão
   relevante, pergunte pelo ADR primeiro.
2. **Desenhar** — nomes de tabelas e colunas, assinaturas sem corpo, nomes de
   rotas, e o teste que deveria passar.
3. **Tentar sozinha** — a primeira tentativa é dela, mesmo feia, mesmo errada.
   **Não pule esta fase por ela.**
4. **Revisar e ensinar** — aqui você entra de verdade: _o que está frágil
   aqui?_, _que caso não foi considerado?_, _por que isso falha sob
   concorrência?_, _como seria a versão profissional, e por quê?_

### Como se comportar na prática

- Pergunte em que fase estamos quando não estiver claro.
- Explique o porquê antes do como. Conceito primeiro, comando depois.
- Ao revisar, aponte a falha e o raciocínio — não entregue só o código corrigido.
- Quando ela pedir "escreve pra mim", ofereça primeiro: o desenho, as
  assinaturas, ou o teste que deveria passar. Se ela reafirmar o pedido, é
  decisão dela — escreva, e explique cada trecho.
- Escrever _para ela ler e reescrever_ é diferente de escrever no lugar dela.
  Deixe claro qual dos dois está acontecendo.

### As sete regras do projeto

1. Eu sou a arquiteta. A IA digita, explica, revisa e ensina. Não decide arquitetura.
2. Nenhuma linha entra no repositório que eu não consiga explicar em voz alta.
3. Toda decisão relevante vira ADR — escrito **antes** do código.
4. Tento sozinha antes de pedir revisão.
5. Uma etapa por vez, com o critério de pronto atendido.
6. Todo bug ganha primeiro um teste que o reproduz.
7. Ideia nova vai para o backlog, não para a v1.

## Estado atual

- **Etapa 1 (modelagem): concluída** — `docs/modelo.md`, 5 ADRs escritos.
- **Etapa 0 (fundação): concluída** — `docker compose up` sobe `db` e `api`; `/health` responde
  `200` pelo compose.
- **Etapa 1 (migration): em andamento** — é aqui que estamos.

### Já feito

- `.gitignore` na raiz, `.env` protegido antes de existir segredo, `.env.example` versionado.
- Python 3.14 fixado (ADR 0005 substitui a escolha de 3.12 do ROADMAP).
- `uv` com `pyproject.toml` + `uv.lock`; ambiente reprodutível via `uv sync`.
- Layout monorepo: `backend/` (Python) e `frontend/` (Etapa 7); documentação na raiz.
- Camadas em `backend/app/`: `routers`, `services`, `repositories`, `models`,
  `schemas` — irmãs, cada uma com `__init__.py`.
- `GET /health` respondendo `200` fora do container.
- `ruff` e `mypy` como dependências de desenvolvimento, configurados em
  `[tool.ruff]` (`line-length = 88`), `[tool.ruff.lint]` (`select = ["E","F","I"]`)
  e `[tool.mypy]` (`python_version = "3.14"`, sem modo estrito). Os três passam
  limpos: `ruff check`, `ruff format --diff`, `mypy app`.
- `pre-commit` instalado e verificado. `.pre-commit-config.yaml` na **raiz**:
  hooks oficiais `ruff-check` (com `--fix`) e `ruff-format`, em `rev: v0.16.5`
  batendo com o `uv.lock`; e um hook `local` de `mypy` com `language: system` e
  `entry: uv run --directory backend mypy app`. O `--directory` é o que resolve o
  descompasso do monorepo — sem ele o mypy roda da raiz e cai em
  `Config File: Default`, aprovando com a configuração errada, em silêncio.
- ADR 0006: `Dockerfile` em `backend/`, ao lado do serviço, com `context` em
  `backend/`. A alternativa (raiz do repo) foi descartada porque back e front
  partem de bases diferentes (`python:3.14-slim` × `node`) e o padrão é um
  `Dockerfile` por serviço.
- `backend/Dockerfile` escrito e funcionando: `python:3.14-slim` (glibc, ao
  contrário da `alpine`/musl, que faria os wheels compilarem do zero); `uv`
  fixado em `0.12.8` via `COPY --from=ghcr.io/astral-sh/uv:0.12.8`, batendo com
  o `uv --version` local; `WORKDIR /app`; manifestos copiados **antes** do
  código, com `uv sync --locked` entre os dois — é o que preserva o cache de
  camadas quando só o código muda; `CMD` em forma exec (o processo recebe o
  sinal de encerramento, em vez de o `sh` engolir) com `--host 0.0.0.0`, sem o
  qual o uvicorn escuta só o loopback do container e o mapeamento de porta não
  alcança ninguém. Sem `--reload`: na imagem o código é cópia congelada.
- `backend/.dockerignore` (mora na raiz do `context`): barra `.venv` — que aqui
  seria um venv de Windows, inútil em Linux —, `.git/`, caches, `*.pyc` e os
  próprios arquivos do Docker.
- `docker build -t reservare-api .` e `docker run --rm -p 8000:8000` verificados:
  `/health` responde `200` **pelo container**, ainda sem compose.
- `docker-compose.yml` na **raiz** (não em `backend/`): o arquivo orquestra `db` e `api`, então
  precisa enxergar os dois — mesmo raciocínio do ADR 0006, aplicado a quem orquestra em vez de a
  quem constrói. `db` vem de `image: postgres:16` (a versão da stack, pinada — nunca `latest`);
  `api` vem de `build: { context: ./backend, dockerfile: Dockerfile }`, porque essa imagem não
  existe pronta em lugar nenhum. `depends_on` da `api` na condição `service_healthy`, e o
  `healthcheck` do `db` roda `pg_isready -h localhost -U ... -d ...`: forçar TCP é o que evita o
  teste passar contra o servidor temporário que o próprio Postgres sobe durante o `initdb`, antes
  do banco aceitar conexão de verdade. Volume nomeado `db_data` persiste os dados entre reinícios
  (não bind mount: permissão Unix da pasta de dados do Postgres é frágil vindo de um path do
  Windows). Nenhuma porta do Postgres exposta ao host — inspeção via
  `docker compose exec db psql`; porta da API publicada só em `127.0.0.1:8000`.
  `DATABASE_URL` é montada dentro do compose a partir de `POSTGRES_USER`/`PASSWORD`/`DB` (host
  `db`, o nome do serviço) — por isso não existe mais como chave solta em `.env`/`.env.example`.
  Live-reload via bind mount do código para dentro do container **foi adiado de propósito** para a
  Etapa 2: montar `backend/` sobre `/app` cobriria o `.venv` Linux do `uv sync` com um `.venv` de
  Windows, e hoje não há código suficiente (só `/health`) para validar a técnica de exclusão do
  subcaminho de verdade.
- `docker compose up` confirmado: `db` fica `(healthy)` antes de `api` subir; `GET /health` responde
  `200` **através do compose**.

### Próximo passo

Etapa 0 fechada nos quatro pontos do critério de pronto: `docker compose up` sobe API e Postgres;
`GET /health` responde `200`; `ruff` e `mypy` passam limpos; `.env` fora do repositório
(`git check-ignore` confirma).

Abrir a **Etapa 1 (migration)**: SQLAlchemy 2.0 tipado (`Mapped`, `mapped_column`) para as três
tabelas de `docs/modelo.md`, depois Alembic. Uma decisão pendente antes de gerar a migration: uma
`EXCLUDE` simples sobre `periodo` bloquearia reserva nova mesmo contra uma reserva já **cancelada**
— o invariante fala só de reservas *ativas*. Existe uma cláusula que resolve isso na própria
constraint; decidir e registrar (ADR) antes do código.

Critério de pronto da Etapa 1: `alembic upgrade head` cria tudo do zero e `downgrade base` desfaz;
prova por SQL na mão, sem nenhuma linha de Python, de que o banco recusa duas reservas ativas
sobrepostas.

> Atualize esta seção ao fechar cada etapa. O README tem a tabela de status
> completa e não deve listar nada como pronto antes de estar funcionando.

## Stack decidida

Python 3.14 · FastAPI · SQLAlchemy 2.0 tipado · Pydantic v2 · Alembic ·
PostgreSQL 16 · `uv` · `ruff` · `mypy` · `pwdlib` (Argon2) · pytest + httpx ·
Docker Compose · GitHub Actions · Vite + React + TypeScript + TanStack Query ·
Playwright.

As escolhas já foram decididas com critério em
[`docs/ROADMAP.md`](docs/ROADMAP.md#4-stack-e-por-quê) — não as reabra sem
motivo novo. Em particular: **não** SQLModel (funde modelo e schema), **não**
`create_all()` (Alembic), **não** SQLite (o `EXCLUDE` é o coração do projeto),
**não** Passlib (sem manutenção desde 2020).

## Convenções

- **Commits** pequenos, em português, um por sub-etapa. Commit todo dia, mesmo
  incompleto.
- **ADRs** em `docs/adr/NNNN-titulo-curto.md`, seguindo
  [`docs/adr/TEMPLATE.md`](docs/adr/TEMPLATE.md). Toda seção importa — inclusive
  "Alternativas consideradas" e "Como eu saberia que errei".
- **Camadas:** `routers/` conhece HTTP e chama `services/`; `services/` tem a
  regra e chama `repositories/`; `repositories/` conhece o banco. O domínio não
  conhece FastAPI nem SQLAlchemy. Router não contém regra de negócio.
- **Schemas Pydantic separados dos modelos** e separados por direção
  (`RecursoCriar`, `RecursoAtualizar`, `RecursoResposta`). Nunca devolver o
  modelo de tabela na resposta.
- **Todo timestamp em UTC.** Fuso é assunto de apresentação, não de armazenamento.
- **Intervalo semiaberto `[início, fim)`:** reserva que termina às 10h **não**
  conflita com a que começa às 10h. "Não sobrepõe" ≠ "não encosta".
- **Segredos nunca no repositório.** `.env` no `.gitignore` antes do primeiro
  commit que o criaria. Em repo público, segredo commitado é segredo
  _rotacionado_, não apagado.
- Ao fim de cada sessão de trabalho, registrar **qual é o próximo passo**.

## Comandos

Rodar de dentro de `backend/`, onde está o `pyproject.toml`:

- `uv sync` — recria o `.venv/` a partir do `uv.lock`
- `uv run uvicorn app.main:app --reload` — sobe a API local (`/health` e `/docs`)
- `uv add <pacote>` / `uv add --dev <pacote>` — produção / desenvolvimento
- `uv run ruff check .` — lint; `uv run ruff format .` — formatação
- `uv run mypy app` — verificação de tipos

Da **raiz** do repositório, porque o `pre-commit` não está no `PATH` (ele vive
em `backend/.venv/`):

- `backend/.venv/Scripts/pre-commit run --all-files` — roda os hooks à mão
- `backend/.venv/Scripts/pre-commit install` — escreve o hook em `.git/hooks/`;
  **necessário após clonar**, porque `.git/` não é versionado

A preencher conforme forem criados: `docker compose up`,
`alembic upgrade head`, `pytest`.

## Git

Repositório público em `github.com/PatriciaCorreiaSI/sistema-reservare`, via SSH
com chave pessoal. Os commits usam o e-mail privado do GitHub
(`...@users.noreply.github.com`) — não altere `user.email` local.
