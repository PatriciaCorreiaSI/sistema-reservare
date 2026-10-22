# ADR 0028 — Hospedar a API no Render e o banco no Neon, com a API servindo o front

- **Data:** 2026-10-22
- **Situação:** aceita

## Contexto

A Etapa 8 pede uma URL pública com dados de demonstração. É um portfólio, então o custo precisa ser zero e a demonstração precisa ficar no ar por tempo indeterminado. Restrição dura: o banco precisa do `btree_gist`, porque sem ele não existe o `EXCLUDE`, que é o invariante do projeto. Restrição do [ADR 0023](./0023-guardar-refresh-em-cookie-httponly.md): o cookie de refresh exige que front e API estejam no mesmo site. O ROADMAP citava "Fly.io ou Render"; o Fly.io deixou de ter plano grátis para conta nova.

## Decisão

Escolhi hospedar a API num serviço web Free do Render, construída a partir do `Dockerfile`. O banco será no Neon Free, com Postgres 16, a mesma versão do desenvolvimento. A própria API serve o front já empacotado (`dist/`), com as rotas do front devolvendo o `index.html`, como o Vite faz hoje. O "como" exato disso fica para a fase de desenho.

## Alternativas consideradas

- **Banco no Render Free** — por que descartei: expira em 30 dias e é apagado 14 dias depois.

- **Fly.io** — por que descartei: sem plano grátis para conta nova; cobrança por uso com cartão e sem teto de gasto por padrão.

- **Render pago** — por que descartei: resolve o sono e dá o pre-deploy, mas tem mensalidade, e para uma demonstração o custo não se justifica.

- **Front num serviço separado (static site do Render, ou outro host de estáticos)** — por que descartei: os dois ficariam em sites diferentes pela Public Suffix List, e o cookie de refresh deixaria de ir junto.

## Consequências

Os ganhos: entrega o que pede a Etapa 8 sem custos financeiros e com projeto público permanente. Um serviço só, numa origem só, e o cookie funciona sem mudar nada do [ADR 0023](./0023-guardar-refresh-em-cookie-httponly.md). Os custos:
- A API dorme depois de 15 minutos sem acesso, e o primeiro acesso espera cerca de 1 minuto (avisar no README). O Neon também dorme, depois de 5 minutos, mas acorda em menos de um segundo.
- Sem pre-deploy no Free, a migration roda no comando de partida do container, antes do `uvicorn` (decisão do ADR de migrations no deploy).
- O backup do Neon Free cobre 6 horas de histórico e 1 snapshot manual. O backup com restauração testada vai ser nosso.
- O Free do Render não tem shell, então o `criar_admin` e os dados de demonstração precisam de outro caminho.
- Os limites do Free (1GB, 100 horas de computação, 750 horas de instância) sobram para uma demonstração. Ao estourar, o Neon bloqueia ou suspende, mas não apaga dado.

Se precisar mudar de ideia, é barato: um container e um Postgres comum, sem nada específico de um fornecedor, salvo a configuração do painel. 

## Como eu saberia que errei

O Neon ou o Render mudam o plano grátis (fim do plano, expiração, perda do `btree_gist`). A espera de 1 minuto faz quem visita desistir da demonstração. Os limites de horas ou de espaço são atingidos.
