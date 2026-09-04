# ADR 0002 — Cancelamento em colunas ao invés de tabela

- **Data:** 2026-08-31
- **Situação:** aceita

## Contexto

Um usuário ou admin pode precisar cancelar uma reserva feita. Essa informação precisa ser associada ao registro da reserva feita para liberar o recurso reservado. 

## Decisão

Escolhi manter cancelamento como colunas da tabela reserva para impedir que falhas de integração entre as tabelas gere informação dúbia ou defasada.

## Alternativas consideradas

- **Criar nova tabela 'cancelamento'** — por que descartei: se a integração entre as tabelas falhar, uma reserva na tabela 'reserva' poderia continuar ativa enquanto que a mesma reserva na tabela 'cancelamento' poderia estar cancelada. 

## Consequências

A escolha custa inserir uma nova coluna de identificador de quem cancelou a reserva na tabela reserva (uma vez que tanto o próprio usuário quanto o admin podem cancelar a reserva feita) como chave estrangeira. Implica também identificar o instante com fuso de quando o cancelamento foi feito, utilizando o tipo 'TIMESTAMPTZ'. O ganho é ter a informação em lugar único associado ao registro da reserva, o que evita duplicidades. O risco será eliminado ao garantir, pela constraint CHECK nas 3 colunas, que ao preencher as colunas cancelada_por_id_usuario e cancelada_em preenchidas a coluna status_reserva sempre seja alterada para o valor de 'cancelada' e vice e versa. Caso contrário, a gravação deverá falhar.


## Como eu saberia que errei

Se uma reserva cancelada precisar ser reativada pelo usuário e o sistema barrar porque as colunas cancelada_por_id_usuario e cancelada_em preenchidas estão preenchidas