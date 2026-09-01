# ADR 0001 — Guardar o período como um valor único

- **Data:** 2026-08-31
- **Situação:** aceita

## Contexto

Ao solicitar reserva, usuário deve informar início e fim de uso do recurso. Este período deve ser guardado como valor único para que o banco não sobreponha reservas.

## Decisão

Usarei o tipo de dado *'tstzrange'* no campo 'período', com constraint NOT NULL para que o período ocupe um trecho de tempo com início e fim.

## Alternativas consideradas

- **DATE + TIME + TIME** — por que descartei: não consegui garantir que o banco de dados não sobreporia duas reservas num mesmo período, além de gerar campos a mais no banco de dados.
- **timestamptz: início e fim** — por que descartei: o tstzrange garante, por si só, que o período seja um só e o fim seja depois do início. Com timestamptz eu teria que reconstruir o período em toda consulta, além de contar com duas colunas a mais, exigindo um CHECK a mais.

## Consequências

O tstzrange é um tipo de dado exclusivo do banco de dados Postgre. O risco de usá-lo é a falta de conhecimento de sua sintaxe por parte de muitos devs. Além disso, o ORM e o Pydantic precisam serializar esse dado range vindo do banco PostgreSQL para que o python consiga entendê-lo, já que ele não é nativo do python. O ganho é que o 'tstzrange' torna possível a constraint de exclusão que garante que duas ou mais reservas não se sobreponham no mesmo período. E isso sem depender do código.

## Como eu saberia que errei

Se um usuário no Brasil reservar uma sala para as 17h e ao tentar acessar o recurso, perceber que a reserva foi feita as 17h do fuso de Londres e o recurso não estar disponível para o usuário na hora necessária.