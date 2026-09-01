# ADR 0003 — Três estados ao invés de seis

- **Data:** 2026-08-31
- **Situação:** aceita

## Contexto

O usuário precisa visualizar em qual status sua reserva se encontra. Se está confirmada, cancelada ou concluída. O sistema também precisa dessa informação para liberar ou bloquear os recursos ativos para novas reservas.

## Decisão

Busquei simplificar o projeto para tornar viável sua execução. Por isso optei por diminuir os seis estados para três, eliminando a necessidade de um fluxo de aprovação. A reserva já nasce aprovada.

## Alternativas consideradas

- **Seis estados: lista Solicitada, Confirmada, Em uso, Concluída, Cancelada e Não compareceu.** — por que descartei: exigia a construção de um fluxo de aprovação que tornava o sistema mais complexo, aumentando o número de transições para validar.

## Consequências

Essa escolha torna o sistema mais simples e factível de entrega ao enxugar o escopo de trabalho. Garante maior probabilidade de entrega do sistema em menor tempo.


## Como eu saberia que errei

Se um usuário não comparece para o usufruto da reserva e o recurso continuar bloqueado para novas reservas.