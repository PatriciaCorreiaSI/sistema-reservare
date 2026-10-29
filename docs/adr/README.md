# Decisões de arquitetura

Cada ADR (*Architecture Decision Record*) registra uma decisão relevante do Reservare, escrita
**antes** do código: o contexto, a escolha, as alternativas descartadas e por quê, as
consequências, e o sinal de que a decisão estaria errada. Todos seguem o mesmo
[modelo](TEMPLATE.md).

Um ADR aceito não se reescreve. Quando a prática mostra que ele estava incompleto, ganha uma
**emenda** datada, no fim do próprio arquivo; quando a decisão muda de sentido, nasce um ADR novo
que o **substitui**.

As sete decisões que mais dizem sobre o projeto estão resumidas no
[README](../../README.md#decisões-técnicas).

## Modelo de dados

| ADR | Decisão | Observação |
|---|---|---|
| [0001](0001-periodo-como-valor-unico.md) | Guardar o período como um valor único (`tstzrange`) | |
| [0002](0002-cancelamento-em-colunas.md) | Cancelamento em colunas, e não em tabela | |
| [0003](0003-tres-estados.md) | Três estados de reserva, e não seis | |
| [0004](0004-status-reserva-concluida.md) | "Concluída" deduzida do fim do período, sem gravar | |
| [0007](0007-predicado-pelo-cancelamento.md) | A `EXCLUDE` ignora só as reservas canceladas (`WHERE cancelada_em IS NULL`) | |
| [0008](0008-declarar-exclude-no-modelo.md) | Declarar a `EXCLUDE` no modelo, além da migration | |

## Ambiente

| ADR | Decisão | Observação |
|---|---|---|
| [0005](0005-versao-python-3-14.md) | Python 3.14 | |
| [0006](0006-local-dockerfile.md) | `Dockerfile` em `backend/` | substituído pelo [0034](0034-construir-imagem-da-raiz-do-repositorio.md) |

## API, transações e regras

| ADR | Decisão | Observação |
|---|---|---|
| [0009](0009-api-sincrona.md) | API síncrona | |
| [0010](0010-requisicao-e-transacao.md) | Uma requisição é uma transação | 2 emendas |
| [0014](0014-traduzir-violacao-da-constraint-pelo-nome.md) | Traduzir a violação da constraint pelo nome, no repository | 2 emendas |
| [0016](0016-cancelar-pela-acao-com-update-condicional.md) | Cancelar com um `UPDATE` condicional, enquanto a reserva não terminou | |
| [0017](0017-404-a-quem-nao-pode-acessar-a-reserva.md) | Responder `404` a quem não pode acessar a reserva | |
| [0018](0018-fuso-unico-do-sistema.md) | Ler o horário de funcionamento num fuso único do sistema | 1 emenda |
| [0019](0019-disponibilidade-como-lacunas-livres.md) | Devolver a disponibilidade como lacunas livres, calculadas em Python | |
| [0020](0020-exigir-token-nas-rotas-de-recurso.md) | Leitura de recursos para quem está logada, escrita só para admin | |

## Autenticação

| ADR | Decisão | Observação |
|---|---|---|
| [0012](0012-jwt-curto-com-refresh-no-banco.md) | JWT curto, com refresh guardado no banco | 1 emenda |
| [0013](0013-transportar-token-no-cabecalho-authorization.md) | Transportar o token no cabeçalho `Authorization: Bearer` | o refresh passou ao [0023](0023-guardar-refresh-em-cookie-httponly.md) |
| [0023](0023-guardar-refresh-em-cookie-httponly.md) | Guardar o refresh num cookie `HttpOnly` | |

## Testes e CI

| ADR | Decisão | Observação |
|---|---|---|
| [0011](0011-isolar-teste-em-transacao-desfeita-no-fim.md) | Isolar cada teste numa transação desfeita no fim | 2 emendas |
| [0015](0015-concorrencia-com-threads-e-barreira-pela-api.md) | Provocar a concorrência com threads e barreira, pela API | |
| [0021](0021-testar-pelo-que-a-coisa-testada-depende.md) | Escolher o tipo de teste pelo que a coisa testada depende | |
| [0022](0022-container-de-servico-e-variaveis-no-workflow.md) | Postgres como container de serviço no CI, variáveis no workflow | 1 emenda |

## Front-end

| ADR | Decisão | Observação |
|---|---|---|
| [0024](0024-alcancar-api-pelo-proxy-do-vite.md) | Alcançar a API pelo proxy do Vite, sob o prefixo `/api` | |
| [0025](0025-gerar-tipos-do-front-pelo-openapi.md) | Gerar os tipos do front a partir do OpenAPI | |
| [0026](0026-rotear-com-react-router-declarativo.md) | Rotear com o React Router declarativo | |
| [0027](0027-estilizar-front-com-tailwind.md) | Estilizar com Tailwind | |

## Produção

| ADR | Decisão | Observação |
|---|---|---|
| [0028](0028-hospedar-api-no-render-e-banco-no-neon.md) | API no Render e banco no Neon, com a API servindo o front | 1 emenda |
| [0029](0029-logs-em-json-com-id-de-correlacao.md) | Logs em JSON, com um ID de correlação por pedido | |
| [0030](0030-migrar-na-partida-do-container.md) | Migrar o banco na partida do container, com migrations retrocompatíveis | |
| [0031](0031-configurar-producao-por-blueprint.md) | Configurar a produção por Blueprint, com a URL do banco pronta | 1 emenda |
| [0032](0032-backup-noturno-com-restauracao-testada.md) | Backup noturno, restaurado e conferido antes de ser guardado | |
| [0033](0033-semear-demonstracao-na-partida.md) | Semear a demonstração na partida do container | |
| [0034](0034-construir-imagem-da-raiz-do-repositorio.md) | Uma imagem só, construída da raiz, com o front e a API | |
