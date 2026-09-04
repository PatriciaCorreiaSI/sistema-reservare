# ADR 0004 — Reserva passa a Concluída ao término do seu período

- **Data:** 2026-08-31
- **Situação:** aceita

## Contexto

O status da reserva deve passar a 'Concluída' após finalizado o período da reserva.

## Decisão

Quando o fim do período já passou e a reserva não foi cancelada, ela é concluída por dedução do sistema. 

## Alternativas consideradas

- **Uma tarefa agendada** — por que descartei: exigiria um novo processo no sistema rodando em produção, falha segura e monitoramento
 constante. Tornaria o escopo do sistema mais complexo, aumentando o tempo de conclusão do mesmo.

## Consequências

Torna o sistema mais simples. O ganho é evitar a necessidade de monitoramento constante e a necessidade da tarefa falhar de forma segura. O risco é que o recurso de uma reserva cujo usuário não compareceu permanece bloqueado até o final do período da reserva.


## Como eu saberia que errei

Se após o término do período da reserva, a mesma continuar com o status 'confirmada' e o recurso ativo continuar bloqueado para novas reservas.