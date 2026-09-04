# ADR 0007 — Usar 'predicado pelo cancelamento' para listar o estado que libera nova reserva

- **Data:** 2026-09-04
- **Situação:** aceita

## Contexto

O invariante do projeto diz que **duas reservas ativas** nunca podem se sobrepor. A constraint precisa saber o que é **"ativa"** e desconsiderar reservas **"canceladas"**. A constraint não precisa liberar reservas passadas, porque a regra **"não se reserva no passado"** torna o caso de sobrepor novas reservas a reservas passadas inalcançável na prática. Mesmo que quisesse, não seria possível. A constraint de exclusão aceita uma cláusula ```WHERE``` que é apoiada num índice parcial que precisa ser fixo. ```WHERE upper(periodo) > now()``` é recusado pelo Postgres.  ```now()``` não é imutável, e um índice que muda com o passar do tempo passaria a apontar linhas erradas.

## Decisão

Escolhi a opção do **predicado pelo cancelamento**. A constraint seria ```EXCLUDE USING gist (id_recurso WITH =,  periodo WITH &&) WHERE (cancelada_em IS NULL)```. Isso lista o estado que *libera*. Pelo predicado ```WHERE (cancelada_em IS NULL)``` o sistema ignora ```status_reserva = 'Cancelada'```, mas o [ADR 0002](0002-cancelamento-em-colunas.md) amarra as 3 colunas de cancelamento. Enquanto este ```CHECK``` existir, o sistema jamais terá uma coluna ```status_reserva = 'Cancelada'``` e ```cancelada_em``` vazia. Se, futuramente, surgir um novo estado no sistema, qualquer nova reserva com esse novo status sobreposta à outra existente 'Confirmada' será explicitamente bloqueada, já que o default é liberar *apenas* se a coluna cancelada_em estiver preenchida. E qualquer outro status diferente de 'Cancelada' trará, por default, essa coluna vazia. Isso avisaria explicitamente que o sistema precisa ser atualizado para incluir o novo status, não passando despercebido silenciosamente em produção. 

## Alternativas consideradas

- **Predicado pelo status** — por que descartei: ```WHERE (status_reserva = 'Confirmada')```. Funciona listando o estado que *bloqueia*. Contudo, se futuramente surgir um novo status, o default é liberar qualquer status diferente de 'Confirmada'. Assim, uma reserva ativa marcada com o novo status não bloqueia outra nova reserva solicitada com período sobreposto ao seu. O sistema libera a nova reserva, quebra o invariante do projeto e ninguém percebe o erro que passa silenciosamente em produção.

- **Coluna derivada** — por que descartei:```(ativa BOOLEAN GENERATED ALWAYS AS (...) STORED)``` e predicado sobre ela. O predicado da cláusula ```WHERE``` passaria a apontar uma coluna derivada (calculada pelo sistema). É uma indireção a mais: exigiria dois saltos a mais para se chegar a um lugar que poderia ser alcançado de forma direta. Torna o sistema mais complexo. A opção adotada é mais simples e direta. 

## Consequências

O custo é: sempre que alguém adicionar um novo status no serviço, deve obrigatoriamente adicionar o novo status no banco de dados. Caso contrário, o sistema bloqueará reservas que supostamente poderiam ser liberadas. O ganho é: se alguém esquecer de adicionar o novo status no banco de dados, o invariante do sistema não será quebrado e a condição de duas reservas ativas nunca se sobreporem continuará resguardada. Mudar de ideia custaria derrubar a constraint e recriá-la exigiria uma manutenção cara, bloqueando a tabela do banco de dados para novas leituras ou escritas e segurando locks importantes por muito tempo. Além disso, se os dados existentes já violarem o predicado novo, a recriação falha, exigindo a limpeza dos dados manualmente enquanto a tabela em produção fica sem constraint nenhuma.

## Como eu saberia que errei

Se forem inseridos no sistema novos status que deveriam liberar novas reservas ao invés de bloquear, como por exemplo, 'Pendente'. Nesse caso, o sistema bloquearia, uma vez que a coluna ```cancelada_em``` de qualquer reserva com status diferente de 'Cancelada' estará sempre vazia por default. A regra escolhida não seria suficiente para atender este cenário. Ou se o ```CHECK``` do ADR 0002 que amarra as 3 colunas de cancelamento for retirado e passar a existir uma reserva com a coluna ```status_reserva = 'Cancelada'``` e a coluna ```cancelada_em``` vazia. Isso faria o sistema continuar bloqueando um recurso que deveria estar liberado para novas reservas.
