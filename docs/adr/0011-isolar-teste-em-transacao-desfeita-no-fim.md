# ADR 0011 — Isolar teste em uma transação desfeita no fim

- **Data:** 2026-09-11
- **Situação:** aceita

## Contexto

Testes que compartilham estado ficam dependentes da ordem e intermitentes. O banco de teste não pode ser o de desenvolvimento. E o projeto tem um teste: o de **concorrência da etapa 4** que exige duas transações reais. Isso restringe as opções desde já.

## Decisão

A decisão tem 4 partes: 
1. Banco separado `reservare_test`, no mesmo Postgres do compose;
2. Esquema construído por `alembic upgrade head` a cada rodada (uma vez por rodada, não por teste) provando a migration junto;
3. Padrão: cada teste roda dentro de uma transação aberta pelo teste e desfeita no fim. A dependência `obter_sessao` é substituída por uma que entrega a `Session` presa a essa transação e não comita.
4. Exceção nomeada desde já: testes que precisam de transação real usam `commit` de verdade e `TRUNCATE` depois, marcados com um marcador próprio do `pytest`. A etapa 4 é o primeiro uso.

## Alternativas consideradas

- **Limpar entre testes:`TRUNCATE` para tudo:** — por que descartei: usaria uma única mecânica para tudo, mais simples de explicar. Antes de cada teste, `TRUNCATE` em todas as tabelas. Porém é mais lenta e `id` não reinicia.
- **Só transação, sem exceção nomeada:** — por que descartei: só faz transação por teste, sem exceção, o que não atende o teste que roda no coração do projeto, na etapa 4.
- **Um banco novo por teste** — por que descartei: cria, migra, testa, derruba, com isolamento perfeito. Mas leva segundos por teste; em uma suíte com 200 testes, levaria minutos.

## Consequências

O custo é ter duas mecânicas de teste ao invés de uma e quem escreve um teste precisa saber em qual está. Além disso, os testes comuns não comitam nunca, então um bug que só aparece no `commit` não é pego por eles. O ganho é que a dependência do [ADR 0010](0010-requisicao-e-transacao.md) torna essa decisão simples (sem *savepoint*).

## Como eu saberia que errei

Se um teste que falha na suíte inteira passa sozinho, com estado vazando, mostrando que o isolamento não segurou. Ou um teste de concorrência travar esperando (rodando da forma errada dentro de uma transação só). Ou a suíte lenta para rodar a cada commit.
