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

## Emenda (2026-10-06): o fuso vale também para a tela, e a API o publica

### Problema:
O banco guarda instantes (`TIMESTAMPTZ`, UTC): "2026-10-02T13:00Z" é um ponto da linha do tempo, igual para o mundo inteiro. A tela mostra horas de relógio: "10h". Entre um e outro há sempre uma conversão, e a pergunta é: o relógio é de quem? O navegador tem uma resposta pronta: ele sabe o fuso do sistema operacional e, por padrão, todo `Date` se formata nele. O problema é que o Reservare já tem um terceiro relógio: o do recurso. Este ADR decidiu que `hora_func_inicio = 08:00` é 8h em `FUSO_FUNCIONAMENTO`, porque "o horário de funcionamento pertence ao lugar, não a quem reserva". E o `dia` da disponibilidade também é local a esse fuso ([api.md](../api.md)). Para alguém com navegador em Lisboa (UTC+1), a tela do recurso mostraria "funciona das 8h às 18h (o `time`, como veio) e, logo abaixo, as lacunas formatadas pelo navegador: "livre das 12h às 22h". Duas verdades incompatíveis na mesma tela. E o `dia`: às 21h de Brasília do dia 2 já é dia 3 em Lisboa. Se o front calcular "hoje" pelo navegador, pede a disponibilidade do dia errado. Isso acontece sem ninguém viajar: o Playwright roda no fuso da máquina, e o runner do CI é UTC.

### Decisão:
O front formata todo instante nesse fuso e calcula o `dia` nele. O fuso único vale também para a apresentação, e a API o publica para o front não precisar adivinhar. Onde a API publica: um campo `fuso: str` (nome IANA, `"America/Sao_Paulo"`) em `RecursoResposta`. Três motivos: é ao lado de `hora_func_inicio` que ele dá sentido. Um `time` sem fuso é a metade de uma informação; a tela do recurso é onde os dois relógios se encontram; e o contrato já fica com a forma do backlog "um fuso por recurso". Hoje o valor vem de `FUSO_FUNCIONAMENTO` para todos, amanhã viria de uma coluna, sem mudar o front.

### Alternativas descartadas

- **Fuso do navegador** — por que descartei: nenhuma mudança na API, mas é a tela de Lisboa acima: `hora_func` e lacunas em relógios diferentes, `dia` errado na virada, e o Playwright precisando de `timezoneId` fixado. O que é escolher o fuso do recurso dentro do teste e o do navegador fora.

- **Fuso do recurso por padrão com troca pelo usuário** — por que descartei: é o que o Google Calendar e o Microsoft Bookings fazem para reuniões. Mas é um estado de interface a mais, e o `hora_func` continuaria sem conversão (é `time`, não instante). Faz sentido para recurso remoto, que ninguém pediu (regra 7: backlog).

- **Uma rota `/api/config`** — por que descartei: uma rota para um valor só.

- **O campo em `DisponibilidadeResposta`** — por que descartei: resolve o `dia`, mas não o `hora_func`, que mora em `RecursoResposta`.


### Consequências

O ganho: tudo na tela fala o mesmo relógio: `hora_func`, lacunas e `dia`, e o Playwright passa a ser determinístico com o `timezoneId` fixado no fuso do recurso. O custo: `RecursoResposta` deixa de ser espelho do modelo (`from_attributes`), e quem monta a resposta precisa compor o campo; e quem acessa de outro fuso vê horário de Brasília, não o seu. Aceitável porque o recurso é físico, e só usa o horário estando lá. A tela dizer isso: a etiqueta "horários em America/Sao_Paulo" é desenho, não decisão.

### Como eu saberia que errei
Se aparecer recurso remoto (reunião online, licença de software). O fuso do navegador passa a fazer sentido e a opção do fuso do recurso por padrão, com troca do usuário sai do backlog.
