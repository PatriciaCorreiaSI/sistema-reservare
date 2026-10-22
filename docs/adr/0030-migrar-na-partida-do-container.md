# ADR 0030 — Migrar o banco na partida do container, com migrations retrocompatíveis

- **Data:** 2026-10-22
- **Situação:** aceita

## Contexto

O ROADMAP pede que a migration rode antes da versão nova subir e que toda migration seja retrocompatível. As armadilhas citadas são "deploy manual e não documentado" e "migration destrutiva antes do código novo". O lugar natural seria *pre-deploy command* do Render, mas ele só existe nos planos pagos ([ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md)). No deploy, o Render mantém a instância velha atendendo enquanto a nova sobe, e só troca o tráfego quando a nova passa no *health check*. Nesse intervalo, código velho roda sobre esquema novo. No Postgres, a mudança de esquema é transacional: o Alembic desfaz inteira a migration que falha. Hoje a imagem leva só `app/`, sem `migrations/` nem `alembic.ini`.

## Decisão

Vou rodar o `alembic upgrade head` no comando de partida do container, e o `uvicorn` só sobe se a migration terminar sem erro. A imagem passa a levar `migrations/` e `alembic.ini`. **Regra para toda migration daqui em diante (*expand/contract*):** uma migration nunca quebra o código que está em produção. Mudança destrutiva (apagar ou renomear coluna ou tabela, tornar uma coluna obrigatória) se divide em dois deploys:

1. **expandir**: só acrescenta, e o código novo passa a usar o que é novo;
1. **contrair**: num deploy seguinte, remove o que nenhum código em produção usa mais.

O formato exato do comando fica para o desenho.

## Alternativas consideradas

- **Job no GitHub Actions antes d deploy** — por que descartei: a URL do banco de produção passaria a morar também nos *secrets* do GitHub, mais um lugar com o segredo mais valioso do sistema; e o deploy deixaria de ser automático, porque o CI teria que migrar e depois acionar o Render.

- **À mão, do computador** — por que descartei: é o deploy manual e não documentado que o ROADMAP aponta como armadilha. Depende de lembrar, e ninguém confere.

- **No `lifespan` do FastAPI** — por que descartei: mistura servir pedidos com mudar o esquema, e com vários *workers* cada um tentaria migrar.

- **Pre-deploy do Render** — por que descartei: disponível apenas nos planos pagos ([ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md)).

## Consequências

Os ganhos:
- Versão e esquema viajam juntos: a imagem leva as migrations que combinam com o código dela;
- Falha segura: a migration falha, o container não sobe, o Render cancela o deploy e a versão velha continua no ar com o banco intacto;
- O segredo do banco fica num lugar só, o Render;
- O `docker compose up` local também passa a migrar sozinho.

Os custos:
- A migration roda a cada partida, e no plano grátis a API acorda várias vezes por dia. Já em `head`, não faz nada, mas soma alguns segundos à espera de cerca de 1 minuto;
- O *expand/contract* transforma toda mudança destrutiva em dois deploys e exige lembrar do segundo;
- A regra não tem verificação automática: depende de revisão.

## Como eu saberia que errei

O serviço passa a ter mais de uma instância: várias partidas rodariam a migration ao mesmo tempo, e a decisão precisa ser revista (job no CI, ou pre-deploy pago). Uma migration demorada faz a partida passar dos 15 minutos que o Render espera, ou torna a espera para acordar perceptivelmente maior. Um deploy quebra a versão velha durante a troca, sinal de que uma migration fugiu da regra.
