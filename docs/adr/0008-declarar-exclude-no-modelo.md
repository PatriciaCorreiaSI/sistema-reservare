# ADR 0008 — Declarar o `EXCLUDE` no modelo

- **Data:** 2026-09-08
- **Situação:** aceita

## Contexto

Definir onde a `EXCLUDE` ficaria declarada. O invariante já está declarado no Banco de Dados. Aqui decide-se onde mais ela deve ser gravada. O autogenerate é cego para `EXCLUDE`. O SQL vai à mão na migration em qualquer decisão.

## Decisão

Escolhi declarar a `EXCLUDE` no `__table_args__` do modelo e também  escrevê-la à mão na migration. O motivo principal da escolhA é **legibilidade** e não ganho técnico. 

## Alternativas consideradas

- **Declarar apenas na migration** — por que descartei: `models/reserva.py` deixaria de mencionar a regra principal do projeto. Além disso, o padrão de mercado escolhe declarar no modelo e esse projeto escolhe seguir as práticas do mercado atual.

## Consequências

O custo é ter duas cópias sem conferência mecânica. O modo de falha é o modelo mentir, não ficar incompleto. O custo de voltar atrás é apagar uma declaração. O ganho é que o leitor ao abrir o modelo encontra a declaração explícita. Mesmo com essa decisão, o modelo nunca descreve o banco por inteiro. ```CREATE EXTENSION btree_gist``` não é constraint e não tem como ser declarada ali.

## Como eu saberia que errei

Se ao implementar um teste que lê `pg_constraint` no banco que compara com o que o modelo declara, o teste ficar vermelho ao identificar uma divergência entre as duas cópias.
