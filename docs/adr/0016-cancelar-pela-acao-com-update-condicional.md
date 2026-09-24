# ADR 0016 — Cancelar pela ação, com `UPDATE` condicional, enquanto a reserva não terminou

- **Data:** 2026-09-24
- **Situação:** aceita

## Contexto

Três decisões anteriores já desenharam a máquina de estados da reserva. O [ADR 0003](0003-tres-estados.md) fixou três estados, com a reserva nascendo confirmada, sem fluxo de aprovação. O [ADR 0004](0004-status-reserva-concluida.md) fez de "concluída" um estado deduzido, nunca gravado: é a reserva confirmada cujo fim já passou. O [ADR 0002](0002-cancelamento-em-colunas.md) grava o cancelamento em três colunas amarradas por um `CHECK`: o status, quem cancelou e quando. 

 ```
    confirmada ── o fim do período passa ──► concluída   (deduzida)
         └──────── alguém cancela ─────────► cancelada   (gravada)
 ```

Concluída e cancelada são finais. Com isso, só sobra uma transição que alguém executa (confirmada → cancelada). Quatro perguntas precisam ser respondidas:

- Até quando se cancela? 
- Onde "concluída" é calculada?
- Qual a rota e o erro?
- O que acontece com dois cancelamentos simultâneos da mesma reserva?

## Decisão

Cancela-se enquanto a reserva ainda não terminou, ou seja, ela ainda é "confirmada". "Concluída" sai de uma função de domínio no service, que recebe o agora como parâmetro, para ser testável com um horário fixo. A rota é `POST /reservas/{id}/cancelar`, com `409` para a transição inválida: o pedido conflita com o estado atual da reserva.

O cancelamento é um `UPDATE` condicional que verifica e grava no mesmo comando: `WHERE id_reserva = :id AND cancelada_em IS NULL AND upper(periodo) > :agora`, com o mesmo agora recebido pelo service. Antes dele, o service lê a reserva e confere o acesso ([ADR 0017](0017-404-a-quem-nao-pode-acessar-a-reserva.md)): se ela não existe ou não é de quem pede, `404`. Por isso, se o `UPDATE` afetar 0 linhas, a reserva já foi cancelada ou já terminou, e a resposta é `409`.

## Alternativas consideradas

- **Cancelar só antes de a reserva começar** — por que descartei: quem sai mais cedo não consegue liberar a sala para o resto do horário.

- **Encerrar mais cedo, encurtando o período** — por que descartei: é o que sistemas comerciais de sala fazem (o "check-out"). Mas é uma transição nova, que muda o `periodo`. Isso é escopo novo, então vai para backlog.

- **Calcular "concluída" no SQL da consulta `(CASE WHEN upper(periodo) <= now() ...)`** — por que descartei: filtra no banco, mas a regra fica escrita dentro de uma query, e o `now()` do Postgres é difícil de controlar em testes.

- **Calcular "concluída" num campo calculado do schema Pydantic** — por que descartei: cômodo, mas põe regra de negócio no schema, que é camada de transporte. Contraria a convenção das camadas.

- **Cancelar por `DELETE /reservas/{id}`** — por que descartei: mente. "Delete" promete apagar, e a linha fica no banco como histórico.

- **Cancelar por `PATCH /reservas/{id}` com `{"status_reserva": "cancelada"}`** — por que descartei: deixa o cliente escrever o status. Seria preciso, então, recusar todos os outros valores, e o PATCH ainda não carregaria quem cancelou nem quando.

- **Ler, verificar em Python e depois gravar** — por que descartei: tem a janela de corrida. Dois cancelamentos simultâneos leem "confirmada", os dois passam, e o segundo sobrescreve quem cancelou e quando (atualização perdida). É o `if disponivel: criar()` do ROADMAP com outra roupa.

- **Bloqueio pessimista (`SELECT ... FOR UPDATE`)** — por que descartei: a primeira transação trava a linha, e a segunda espera. Funciona, mas é um passo a mais e segura o lock.


## Consequências

O ganho: nenhuma regra nova além da máquina, e nenhuma janela de corrida no cancelamento. Os custos: a reserva usada pela metade fica como "cancelada", filtrar por "concluída" exigiria levar a regra para o SQL. 

## Como eu saberia que errei

Pedirem com frequência para liberar só o resto do horário, o que indica que a opção de "Encerrar mais cedo", encurtando o período faz falta, ou precisarem filtrar reservas por status, o que puxa a regra para o SQL.
