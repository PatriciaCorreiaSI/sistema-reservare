# ADR 0015 — Provocar concorrência com threads e barreira, pela API

- **Data:** 2026-09-24
- **Situação:** aceita

## Contexto

O critério de pronto da Etapa 4 pede que duas requisições simultâneas para o mesmo recurso e horário resultem em exatamente um `201` e um `409`. Para isso, é preciso haver duas transações abertas ao mesmo tempo, em duas conexões diferentes: só assim a segunda espera a primeira, como o Postgres faz em produção. O item 4 do [ADR 0011](0011-isolar-teste-em-transacao-desfeita-no-fim.md) já decidiu que esse teste comita de verdade, limpa com `TRUNCATE` e leva marcador próprio. Falta decidir como provocar a concorrência.

A infraestrutura atual não serve por 3 motivos:

- O `TestClient` é sequencial. `client.post()` só devolve quando a requisição inteira terminou. Duas chamadas seguidas nunca se sobrepõem. A segunda encontra a primeira já comitada e recebe `409`.

- A fixture `client` entrega a mesma sessão para todas as requisições. Tudo roda numa conexão só e numa transação só. Não existe "outra transação" para esperar;

- Os dados preparados pelas fixtures são invisíveis para outras conexões. A Emenda do [ADR 0011](0011-isolar-teste-em-transacao-desfeita-no-fim.md) já registrou isso: "nada chega ao disco, então outra conexão nunca enxerga o que o teste gravou". O `usuario` e o `recurso_criado` de hoje vivem numa transação que nunca comita. Uma requisição com sessão própria procuraria o recurso, não o encontraria e responderia `404`.

E uma armadilha: o `engine` de `app/db.py` aponta para o banco de desenvolvimento. Tirar a substituição do `obter_sessao` gravaria e comitaria no banco errado.

## Decisão

Escolhi provocar a concorrência pela API, com duas threads liberadas juntas por uma barreira (`threading.Barrier`), cada uma com o seu `TestClient`. A substituta do `obter_sessao` entrega a cada requisição uma sessão nova e real, ligada ao `reservare_test`, que comita de verdade. Fixtures próprias comitam usuário e recurso. O teste confere o conjunto de status, `{201, 409}`, sem depender de qual thread vence. A desmontagem da fixture faz o `TRUNCATE` e roda mesmo se o teste falhar. Cada thread tem prazo máximo para responder, para o teste falhar em vez de pendurar. O marcador é `concorrencia`, e o teste roda por padrão.

## Alternativas consideradas

- **Cliente assíncrono (`httpx.AsyncClient` + `asyncio.gather`)** — por que descartei: duas requisições disparadas num laço assíncrono. Traz para os testes a maquinaria assíncrona (`pytest-asyncio` ou `anyio`) num projeto que o [ADR 0009](0009-api-sincrona.md) decidiu síncrono, e tem o mesmo limite da opção escolhida: não garante que as transações se sobreponham.

- **Duas conexões direto no banco, sem HTTP** — por que descartei: a conexão 1 insere e não comita. Numa thread, a conexão 2 insere e fica bloqueada. O teste confirma o bloqueio, comita a 1 e vê a 2 falhar com `23P01`. Prova a espera toda vez, de forma determinística. Contudo, por ora, a espera e o `23P01` são comportamento do Postgres, testado pelo próprio fornecedor. O que é meu (declarar a `EXCLUDE`, a fronteira da transação e a tradução do erro) o teste pela API já exercita. Vai para backlog.

- **Servidor real (`uvicorn`) + HTTP de verdade** — por que descartei: sobe a API num processo e dispara requisições reais. É a mais parecida com a produção, porém é a mais pesada: processo para subir e derrubar, porta, tempo de espera. Esse papel é do Playwright, na Etapa 7.

## Consequências

O ganho é que o teste prova o que o critério de pronto pede: pela API, o resultado é sempre um `201` e um `409`, em qualquer ordem. O custo é que ele não prova, a cada execução, que as transações se sobrepuseram: a barreira aproxima a largada, não a garante. Outro custo é um segundo conjunto de fixtures, que precisa andar junto com o primeiro.

## Como eu saberia que errei

O teste passar sempre, mas um bug de concorrência aparecer em produção, ou o teste ficar intermitente.
