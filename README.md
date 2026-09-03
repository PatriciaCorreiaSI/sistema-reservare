# 📅 Reservare

Sistema de reserva de recursos compartilhados — salas, equipamentos e estações de trabalho — construído com foco em **integridade de dados sob concorrência**.

> ⚠️ **Em construção.** Este repositório documenta um projeto em andamento, etapa por etapa.
> Fase atual: **Etapa 1 — migrations e constraints**. Fundação do ambiente concluída.

---

## O problema

Uma equipe compartilha recursos limitados e precisa reservá-los por janelas de tempo. O desafio não é o cadastro — é garantir que **duas pessoas nunca reservem o mesmo recurso no mesmo horário**, inclusive quando as duas requisições chegam no mesmo instante.

## A regra que dá razão a este projeto

> **Duas reservas ativas nunca podem se sobrepor no mesmo recurso.**

Verificar disponibilidade antes de inserir **não** resolve isso: entre a verificação e a gravação existe uma janela em que outra transação insere. Por isso a garantia é declarada no próprio PostgreSQL, com uma constraint de exclusão sobre `tstzrange` — de forma que a regra não dependa de o código lembrar de conferir.

Demonstrar isso, com teste de concorrência que prove o comportamento, é o objetivo central do projeto.

---

## Status

| Etapa | Situação |
|---|---|
| Modelagem de dados | ✅ concluída |
| Fundação: ambiente, container, lint | ✅ concluída |
| Migrations e constraints | 🔨 em andamento |
| API em camadas | ⏳ |
| Autenticação e autorização | ⏳ |
| Reservas, concorrência e estados | ⏳ |
| Testes e integração contínua | ⏳ |
| Front-end | ⏳ |
| Deploy | ⏳ |

Nada é listado como pronto antes de estar funcionando.

---

## Stack

**Back-end** — Python 3.14 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · Alembic · PostgreSQL 16
**Front-end** — Vite · React · TypeScript · TanStack Query
**Qualidade** — pytest · Playwright · ruff · GitHub Actions
**Infra** — Docker Compose

As justificativas de cada escolha estão no [roadmap](docs/ROADMAP.md#4-stack-e-por-quê).

---

## Desenvolvimento

Requisito: [uv](https://docs.astral.sh/uv/). Ele lê o `backend/.python-version` e instala o Python 3.14 sozinho — não é preciso ter a versão na máquina.

```bash
git clone https://github.com/PatriciaCorreiaSI/sistema-reservare.git
cd sistema-reservare/backend
uv sync
uv run uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000` — `/health` responde `200`, e `/docs` traz a documentação interativa.

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
| [`docs/adr/`](docs/adr/) | Decisões de arquitetura, com alternativas descartadas e consequências |

---

## Sobre este projeto

É um projeto de estudo, construído deliberadamente como exercício de **engenharia de software** e não como demonstração de framework. O tema é o veículo; o conteúdo é modelagem com garantias no banco, concorrência, estratégia de testes e automação.

Sobre o uso de IA: ela é usada como revisora e tutora — para explicar conceitos, apontar falhas e sugerir alternativas. As decisões de arquitetura são minhas, ficam registradas em ADRs com as opções que descartei, e vale uma regra simples: **nenhuma linha entra neste repositório que eu não consiga explicar em voz alta.**

---

## Autora

**Patricia Correia**
