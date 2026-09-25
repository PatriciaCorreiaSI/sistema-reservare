# ADR 0018 — Ler o horário de funcionamento num fuso único do sistema

- **Data:** 2026-09-25
- **Situação:** aceita

## Contexto

A reserva é um instante (`TIMESTAMPTZ`, sempre em UTC). O horário de funcionamento é uma hora de relógio (`TIME`), sem fuso. Sem um fuso definido, não dá para comparar os dois: "8h" não corresponde a nenhum instante. Já está decidido, no `modelo.md`, que o recurso não atravessa a meia-noite. Por isso, uma reserva de mais de um dia cai sozinha em `ForaDoHorario`. O que falta decidir é de qual relógio é esse 8h.

## Decisão

Escolhi criar a variável obrigatória `FUSO_FUNCIONAMENTO`, com um nome da IANA (ex. `America/Sao_Paulo`). Pela regra do projeto, se ela faltar, o app falha no startup. O service converte `inicio` e `fim` para esse fuso e compara as horas locais com o horário do recurso. O banco não muda: continua guardando instantes em UTC.

## Alternativas consideradas

- **Um fuso por recurso** — por que descartei: uma coluna nova, `fuso`, em `recurso`, com um nome como `America/Sao_Paulo`. Mas exige migration, mudança nos schemas e validação do nome do fuso. Só vale a pena se houver salas em cidades diferentes, o que ninguém pediu (regra 7: vai para o backlog).

- **Tratar o `TIME` como UTC** — por que descartei: compara direto, sem conversão. Mas é uma mentira na interface: para dizer "8h às 18h", o admin teria que cadastrar "11h às 21h". Se o fuso tiver horário de verão, o valor certo muda duas vezes por ano.

- **Usar o fuso de quem fez o pedido** — por que descartei: usa o deslocamento que veio no `inicio` (o `-03:00`). Mas a regra passa a depender de quem pergunta. O mesmo instante seria aceito ou recusado conforme o fuso enviado. Quem manda `+00:00` consegue reservar a sala às 3h da manhã de Brasília. O horário de funcionamento pertence ao lugar, não a quem reserva.


## Consequências

O ganho: o admin cadastra a hora que vê no relógio da sala. Custos: todos os recursos ficam no mesmo fuso; a dependência `tzdata` entra no projeto, porque o Windows não traz a base de fusos da IANA; e exige uma variável obrigatória a mais no ambiente.

## Como eu saberia que errei

Se aparecer um recurso em outra cidade ou outro fuso. Esse é o sinal para migrar para um fuso por recurso.
