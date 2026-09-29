# ADR 0019 — Devolver a disponibilidade como lacunas livres, calculadas em Python

- **Data:** 2026-09-29
- **Situação:** aceita

## Contexto

A consulta de disponibilidade está no escopo da v1 e é o que a Etapa 7 consome. Hoje, a única forma de saber se um horário está livre é tentar reservar. As restrições que qualquer solução precisa respeitar: o dia e o horário de funcionamento são lidos no fuso do sistema [ADR 0018](0018-fuso-unico-do-sistema.md) enquanto as reservas estão em UTC; só as reservas ativas ocupam; o intervalo é semiaberto; e a resposta não pode revelar reservas de outras pessoas [ADR 0017](0017-404-a-quem-nao-pode-acessar-a-reserva.md).

## Decisão

Escolhi utilizar a rota em `GET /recursos/{id}/disponibilidade?dia=2026-10-02`, devolvendo as lacunas livres em UTC calculadas por uma função pura em Python, só para quem está logado. Para recurso inativo ou inexistente, seguiremos o `POST /reservas` com `404` para o inexistente e `409` para o inativo. Os horários que já passaram serão cortados no `agora` (o `obter_agora` já injetado): uma lacuna livre deve significar reservável, e o `POST` recusa o passado com `422`. Para um dia inteiro no passado, a resposta é uma lista vazia, e não um erro. O `dia` é uma data local, lida no fuso do sistema [ADR 0018](0018-fuso-unico-do-sistema.md); as lacunas saem em UTC, como todo instante do projeto.

## Alternativas consideradas

- **Rota por `GET /reservas?id_recurso=...&dia=...`** — por que descartei: devolve as reservas do dia para o cliente calcular os buracos. Mas devolve as reservas dos outros, com dono e convidados. É vazamento, o mesmo problema que o [ADR 0017](0017-404-a-quem-nao-pode-acessar-a-reserva.md) fechou com o `404`. E joga a regra (fuso, horário de funcionamento) para o front.

- **Calcular lacunas por SQL, com *multirange* (Postgres 14+)** — por que descartei: o Postgres faz a subtração sozinho: `tstzmultirange(janela) - range_agg(periodo)` devolve os buracos numa consulta só. Mas a regra fica escondida numa linha SQL. Só se testa com banco. Essa opção por SQL se justificaria apenas num sistema com muito volume. A garantia continua no banco, na `EXCLUDE`; esta consulta só mostra, então vale o que é mais fácil de testar e explicar.

## Consequências

O ganho: a função pura se testa sem banco; a resposta não mostra o dono. O custo: é uma busca a mais e um laço no Python, desprezível nesta escala; a resposta envelhece no instante seguinte, e "livre" não é promessa, porque quem garante continua sendo a `EXCLUDE` no banco.

## Como eu saberia que errei

A consulta dizer "livre" e o `POST` responder `422` ou `409` para o mesmo horário, sem ninguém ter reservado nesse meio-tempo. Esse sinal quer dizer que a regra do horário ou do fuso foi calculada diferente nos dois lugares.
