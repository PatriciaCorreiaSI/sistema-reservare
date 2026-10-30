# Colaboração com IA

Este projeto foi feito com a ajuda de uma IA: o Claude, da Anthropic, pelo Claude Code, dentro do
editor. Este documento conta como ela foi usada, o que ela não fez, e como cada coisa que ela
sugeriu foi conferida antes de entrar no repositório.

O projeto existe para que eu consiga explicar cada linha em voz alta. Uma IA que decide e escreve
por mim desfaria esse objetivo, mesmo que o sistema funcionasse. Por isso o uso dela seguiu
regras escritas desde o primeiro dia — e as regras mudaram, por decisão minha, quando a prática
mostrou que precisavam mudar.

## O protocolo

Toda tarefa passou por quatro fases ([ROADMAP](ROADMAP.md#5-como-estudar-com-este-projeto)):

1. **Decidir.** Um ADR com o problema, as opções, a escolha e o custo — escrito por mim, antes de
   qualquer código. A IA trazia os conceitos e a prática de mercado, com a fonte; a escolha e o
   texto eram meus.
2. **Desenhar.** Nomes de tabelas e colunas, assinaturas sem corpo, rotas, e o teste que deveria
   passar.
3. **Tentar sozinha.** A primeira versão era minha, mesmo errada.
4. **Revisar e aprender.** Só aqui a IA revisava: o que está frágil, que caso faltou, por que
   aquilo falharia sob concorrência.

Duas emendas ao protocolo, cada uma com data e motivo:

- **Revisão em uma rodada (2026-09-18).** No começo, a IA respondia a um erro com uma dica, e eu
  tentava de novo; o mesmo ponto chegava a três ou quatro rodadas. Mudei: eu tento uma vez, e para
  o que errei a IA traz a resposta certa com o conceito ao lado. Se a primeira tentativa errou, é
  porque eu não sabia o conceito — e dica não ensina o que não se sabe.
- **Código sugerido no front (2026-10-06).** Para os cookies no FastAPI e todo o front-end, a fase
  3 deixou de existir. No front, não por ser novo: eu já tinha entregado projetos com React, Vite,
  HTML e CSS, e repetir sintaxe que eu já sabia não ensinava. O novo ali era a arquitetura e a
  segurança. A IA passou a sugerir o código completo no chat, com o
  conceito ao lado de cada trecho, e testado antes numa cópia fora do repositório (TypeScript,
  ESLint, Prettier e, quando cabia, o teste de ponta a ponta). Eu digitava, rodava e explicava em
  voz alta, e parte desse código mudou na conversa antes de entrar. Para o que eu já dominava —
  testes, services, repositories, ADRs — a fase 3 continuou valendo.

## O que a IA fez, e o que não fez

| A IA fez | A IA não fez |
|---|---|
| Explicou conceitos, sempre antes do comando | Decidir arquitetura |
| Revisou o que eu escrevi: código, testes e ADRs | Escrever ADR ou o [glossário](aprendizados.md) |
| Sugeriu código para os cookies e o front-end, no chat | Escrever em arquivo de código: todo código foi digitado por mim |
| Trouxe a prática de mercado, com a fonte, quando eu não tinha base para decidir | Fazer commit: todos são meus |
| Escreveu e manteve atualizados o README, o ROADMAP e o arquivo de instruções dela, o [`CLAUDE.md`](../CLAUDE.md), revisados por mim | |

O `CLAUDE.md` é o arquivo que a IA lê no começo de cada sessão. Ele guarda as regras deste
protocolo, as decisões em vigor que não couberam num ADR e as armadilhas que já custaram tempo —
para que cada sessão comece de onde a anterior parou, sem que eu repita tudo.

## Como cada sugestão foi conferida

Nenhuma sugestão entrou por confiança. Cada uma passou por estas camadas, nesta ordem:

1. **O ADR veio antes.** A IA sugeria dentro de uma decisão já tomada e escrita; sugestão que
   contrariava um ADR era recusada ou virava uma emenda, escrita por mim.
2. **Digitar é ler.** Como todo código passou pelas minhas mãos, cada linha foi lida pelo menos uma
   vez por quem teria de explicá-la.
3. **Teste e contra-teste.** Cada regra ganhou um teste, e o teste verde foi posto à prova: estraguei
   a regra de propósito — não a preparação, e de um jeito plausível (`>` virando `>=`) — para ver
   que ele fica vermelho pelo motivo certo. Teste que não falha quando devia não prova nada.
4. **Todo bug ganha primeiro um teste que o reproduz.** Só depois o conserto.
5. **As ferramentas.** `ruff` e `mypy` no back-end, Prettier e ESLint no front, a cada commit; e o
   CI, a cada push, com a suíte inteira, as migrations de ida e volta e os testes de ponta a ponta.

## Sugestões que recusei

**Um ambiente local maior que o problema (2026-10-29).** Para que quem clona o projeto o rode sem
perguntar nada, a IA propôs que o ambiente local subisse o sistema inteiro com os dados de
demonstração, e uma guarda no código contra o segredo de exemplo. Perguntei o que isso
acrescentava, se a demonstração já está no ar com as contas de teste. Não acrescentava: o que só se
faz na própria máquina é rodar os testes. Ficou só um `.env.example` com os valores que o CI já
publica, e o critério da etapa passou a dizer "roda os testes localmente". A guarda foi para o
backlog.

**Uma regra do projeto no glossário (2026-09-17).** A IA sugeriu anotar, no verbete sobre onde
guardar tokens, que o `localStorage` é proibido pelo ADR 0013. Recusei: o
[glossário](aprendizados.md) registra o conceito como ele é no mundo, e a regra do projeto mora no
ADR. Se os dois disserem a mesma coisa, não há por que existirem os dois.

**A IA escrevendo no arquivo (2026-09-21).** Ao sugerir uma exceção de domínio, a IA a escreveu
direto no `excecoes.py`. Recusei e virou regra: código vem no chat, eu leio a explicação e digito.
O ato de digitar é parte de conseguir explicar.

## Erros que a verificação pegou

Nem tudo o que passou pela revisão estava certo. Três defeitos, e o que os pegou:

**A sessão que acabava quando a API caía (2026-10-09).** O `renovarSessao`, no front, foi código
sugerido pela IA. Com a API desligada, o proxy responde `502`, e a função tratava isso como "sem
sessão", mandando a pessoa para o login. Eu peguei à mão, no mesmo dia, desligando a API; o
conserto foi fazer só o `401` significar "sem sessão". O teste que reproduz o defeito chegou doze
dias depois, quando o Playwright entrou no projeto:
[`servidor-fora.spec.ts`](../frontend/e2e/servidor-fora.spec.ts). Foi a lição mais concreta sobre
a regra 6: verificar à mão pega o defeito uma vez; o teste pega toda vez.

**O `201` antes do commit (2026-10-27).** O desenho da transação por requisição
([ADR 0010](adr/0010-requisicao-e-transacao.md)) foi revisado na conversa com a IA, e o defeito passou: a
resposta saía antes do commit. Um teste de ponta a ponta que falhava de vez em quando, escondido
pelo *retry* do CI, o revelou. O teste que prova a correção espia o instante em que a resposta
começa a sair e confere que a reserva já está no banco:
`test_a_reserva_ja_esta_gravada_quando_o_201_sai`.

**O deadlock da `EXCLUDE` (2026-10-27).** Ninguém o previu no desenho. O teste de concorrência
falhou uma vez em cerca de 25 rodadas: dois pedidos no mesmo horário esperavam um pelo outro, e o
Postgres abortava um deles com um erro que chegava ao cliente como `500`. Hoje um teste monta esse
círculo de propósito e confere o `409`: `test_deadlock_na_exclude_devolve_409`
([ADR 0014](adr/0014-traduzir-violacao-da-constraint-pelo-nome.md)).

Os dois últimos não são erros da IA: são erros que a revisão com IA deixou passar, e que só um
teste rodado muitas vezes encontrou.

## O que eu tiraria disso

- **A regra que mais importou foi decidir antes.** Com o ADR escrito, a IA sugere dentro de uma
  decisão minha; sem ele, a sugestão vira a decisão.
- **Gastar a fase 3 onde ela ensina.** Tentar sozinha vale para o que estou aprendendo a fazer.
  Onde a sintaxe eu já sabia e o novo era o conceito, o código sugerido com o conceito ao lado de
  cada trecho ensinou mais, e em menos tempo, do que tentar sozinha.
- **Teste verde por sorte é sintoma.** Os dois piores defeitos do projeto apareceram como
  instabilidade, não como erro. Investigar o que falha "de vez em quando" valeu mais do que
  qualquer revisão.
