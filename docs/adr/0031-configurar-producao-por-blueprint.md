# ADR 0031 — Configurar a produção por Blueprint, com a URL do banco pronta

- **Data:** 2026-10-22
- **Situação:** aceita

## Contexto

Hoje a URL do banco é derivada de `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` e `DB_HOST` por `url_do_ambiente()`, sem fallback. É uma decisão em vigor registrada no CLAUDE.md, sem ADR. O Neon ([ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md)) entrega uma URL pronta e recusa conexão sem TLS. A URL derivada não tem como pedir TLS. O prefixo `postgresql://` da URL do Neon, para o SQLAlchemy, significa o driver `psycopg2`; o projeto usa o `psycopg` 3. O Neon oferece conexão direta e conexão com pool (PgBouncer em modo transação). A própria documentação manda usar a direta para migrations, e pelo [ADR 0030](./0030-migrar-na-partida-do-container.md) as migrations rodam no mesmo container. O ROADMAP aponta como armadilha o "deploy manual e não documentado", e como regra "segredos em produção, jamais no repositório".

## Decisão

**URL do banco:** vou aceitar uma `DATABASE_URL` pronta quando ela existir (produção), trocando o prefixo para `postgresql+psycopg`. Quando não existir (desenvolvimento e CI), continuo derivando como hoje. A conexão é a direta, não a com pool, com TLS obrigatório. O valor exato do `sslmode` fica para o desenho, testado contra o Neon.

**Configuração como código:** vou descrever o serviço num Blueprint do Render (`render.yaml`, no repositório): plano grátis, deploy pelo `Dockerfile`, *health check* em `/health`; `autoDeployTrigger: checksPass`, para o deploy só acontecer com o CI verde.

**Segredos:** declarados no Blueprint só pelo nome, com `sync: false`; o valor é digitado no painel. O `JWT_SEGREDO` de produção é gerado pelo Render (`generateValue: true`, 32 bytes aleatórios) e nunca é o de desenvolvimento.

## Alternativas consideradas

- **Continuar derivando, com `DB_SSLMODE`** — por que descartei: a URL do Neon teria que ser quebrada à mão em cinco variáveis, e cada parte copiada é uma chance de erro.

- **Só `DATABASE_URL`, em todo lugar** — por que descartei: mudaria o compose, o CI, o `conftest.py` e o `.env` sem ganho, e a senha teria que ser escapada à mão dentro da URL, que é o que o `URL.create()` resolve hoje.

- **Conexão com pool do Neon** — por que descartei: as migrations pedem a direta, o SQLALchemy já tem pool próprio, e uma instância só usa poucas conexões.

- **Configuração só no painel do Render** — por que descartei: é o deploy não documentado que o ROADMAP pede para evitar; ninguém saberia recriar o serviço.

- **Terraform** — por que descartei: ferramenta de infraestrutura para muitos serviços e fornecedores; para um serviço só, é desproporcional.

## Consequências

Os ganhos:
- Desenvolvimento e CI não mudam;
- Em produção, a variável faltando continua falhando alto, porque a derivação não acha as outras variáveis;
- O serviço é recriável a partir do repositório;
- O CI vira o portão do deploy;
- Nenhum valor secreto no repositório;
- Trocar o `JWT_SEGREDO` custa pouco: invalida só os *access tokens* de 15 minutos, e o refresh, que é um valor aleatório guardado em hash no banco, renova a sessão.

Os custos:
- Dois caminhos para a URL do banco no código;
- O `sync: false` só pergunta o valor na criação do Blueprint, então um segredo novo depois disso se acrescenta à mão no painel;
- O Blueprint é formato do Render: mudar de hospedagem é reescrever esse arquivo (o resto, container e Postgres comum, continua igual).

## Como eu saberia que errei

Um deploy acontece com o CI vermelho. Um valor secreto aparece no repositório. A API sobe em produção conectada sem TLS, ou pela URL com pool. O desenvolvimento ou o CI passam a precisar da `DATABASE_URL`.
