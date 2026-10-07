# ADR 0022 — Usar container de serviço no CI e variáveis de ambiente no workflow

- **Data:** 2026-10-02
- **Situação:** aceita

## Contexto

O pré-commit roda o `ruff` e o `mypy` na máquina local, mas dá para pulá-lo. Ele não roda num clone novo sem o `pre-commit install`, e um `--no-verify` o desliga. O CI é a verificação que ninguém consegue pular, e é a única que roda os testes. A Etapa 6 tem como critério de pronto que o CI rode tudo a cada push e o badge esteja verde. 
O CI do GitHub Actions roda num runner: uma máquina Linux temporária que nasce vazia e é apagada no fim. Ela não tem o `.env`, nem o Docker Desktop, nem o banco `reservare_test`. Pelo [ADR 0021](0021-testar-pelo-que-a-coisa-testada-depende.md), quase todo teste precisa do postgres real, e os testes exigem seis variáveis de ambiente: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DB_HOST`, `JWT_SEGREDO` e `FUSO_FUNCIONAMENTO`. Hoje nada verifica se os modelos e as migrations estão de acordo, nem se os `downgrade` funcionam. É preciso decidir de onde vem o Postgres do CI, de onde vêm as variáveis de ambiente e o que roda e o que reprova o push.

## Decisão

Escolhi usar "Container de serviço do Actions" para o Postgres. O workflow declara o banco na seção chamada `services`, com a mesma imagem do compose, `postgres:16`. O Actions sobe o banco antes dos passos e espera ele ficar saudável. A variável `POSTGRES_DB=reservare_test` faz o banco de teste nascer junto, sem o passo manual que o [ADR 0011](0011-isolar-teste-em-transacao-desfeita-no-fim.md) exige na máquina local.
Os valores das seis variáveis de ambiente serão escritos no próprio **workflow**. São valores de teste, visíveis no repositório público, com nomes que deixam isso claro, como `JWT_SEGREDO: segredo-do-ci-de-32-bytes-testes`. Nenhum valor de produção entra ali. Quando a Etapa 8 chegar, os segredos reais vão para o cofre do GitHub. 
O push fica vermelho se qualquer um destes passos falhar, nesta ordem: `uv sync --locked`, que falha se o `uv.lock` estiver desatualizado; `ruff check` e `ruff format --check`; `mypy app`; `pytest`; e, nas migrations, `alembic check` e um vaivém de `downgrade base` seguido de `upgrade head`. O `upgrade head` a partir do banco vazio já acontece no `conftest.py`. O relatório de cobertura do `pytest-cov` aparece na saída e nunca reprova ([ADR 0021](0021-testar-pelo-que-a-coisa-testada-depende.md)). 

## Alternativas consideradas

- **Rodar `docker compose up -d db` no runner** — por que descartei: usa o mesmo arquivo da máquina local. Mas o compose lê as credenciais do `.env`, que não existe no runner. Também seria preciso esperar o `(healthy)` à mão e criar o `reservare_test` com um passo a mais.

- **Variáveis de ambiente no GitHub Secrets** — por que descartei: ele protegeria algo que não precisa de proteção. O banco do CI só existe durante a execução e ninguém de fora o alcança. O `JWT_SEGREDO` de teste só assina tokens de teste. Há também um custo prático: o GitHub não entrega os Secrets a *pull requests* vindos de forks, então o CI de quem contribuísse falharia.

- **Só o `upgrade head` nas migrations** — por que descartei: prova que as migrations sobem do zero, mas não pega um modelo alterado sem a migration correspondente, nem um `downgrade` quebrado. 

- **`upgrade head` e `alembic check`, sem o vaivém** — por que descartei: pega o modelo sem migration, mas um `downgrade` quebrado continuaria invisível até o dia em que se precisasse dele.

## Consequências

O ganho: o Actions resolve sozinho a espera e a criação do banco, no padrão do mercado, e cada passo das migrations pega um erro diferente por alguns segundos a mais. O custo: a versão da imagem passa a morar em dois lugares, o compose e o workflow, e quem atualiza um precisa atualizar o outro. Os valores no workflow exigem a disciplina de que nenhum valor de produção entre ali. O `alembic check` herda a cegueira do autogenerate: não enxerga `EXCLUDE` nem `CHECK` em tabela existente, então uma constraint esquecida passa por ele. E o vaivém vira compromisso: toda migration nova precisa de um `downgrade` que funcione, ou o CI fica vermelho.

## Como eu saberia que errei

Se o CI ficar verde e a máquina local vermelha, ou o contrário, por diferença entre as versões da imagem. Se uma constraint faltar no banco com o `alembic check` passando. Se um valor de produção aparecer no workflow. Ou se o CI demorar a ponto de eu precisar fazer push sem esperar o resultado.


## Emenda (2026-10-07): o CI passa a conferir o frontend

### Problema

O ADR decidiu um job só, com `working-directory: backend`. A Etapa 7 traz uma segunda cadeia de ferramentas (Node, `npm`, `tsc`, ESLint), o compromisso do [ADR 0025](0025-gerar-tipos-do-front-pelo-openapi.md) (gerar e comparar os tipos no CI) e, no fim, um teste Playwright que precisa de banco, API, front e navegador juntos.

### Decisão

- Dois jobs no mesmo `ci.yml`, `backend` e `frontend`, em paralelo: o `backend` fica como está.
- O que reprova no `frontend`, na ordem: `npm ci`, `eslint`, `prettier --check`, `npm run build`:

| Backend hoje | Front | O que pega |
|--------------|-------|------------|
| `uv sync --locked` | `npm ci` | lock desatualizado ou ausente (o ci recusa instalar sem o package-lock.json bater) |
| `ruff check` | `npx eslint .` | lint (o `create-vite` oferece o ESLint na criação, pela flag `--eslint`) |
| `ruff format --check` | `npx prettier --check .` | formatação. O ESLint deixou de formatar; o par ESLint + Prettier é o padrão do mercado |
| `mypy app` | `npm run build` | tipos e empacotamento: o script do template é tsc -b && vite build, então um passo cobre os dois. Na Etapa 8 o deploy vai precisar do build de qualquer jeito |

- Dois arquivos gerados no repositório, cada job confere o seu com `git diff --exit-code`: o `backend` exporta `app.openapi()` e compara o `openapi.json`; o `frontend` gera os tipos desse JSON e compara. O porquê da divisão: exportar exige importar o app, e o app exige as seis variáveis, que só o `backend` tem. Arquivo gerado fica fora do lint e do formatador.
- Terceiro job, `e2e`, independente e paralelo, com os passos do workflow oficial do Playwright, entrando no commit do primeiro teste. Node fixado em `frontend/.nvmrc` (`24`), lido pelo `setup-node` com cache do `npm`.

### Alternativas descartadas

- **Filtro por caminho (`paths:`)** — por que descartei: job pulado não fica verde, e a suíte é curta demais para compensar.

- **Um script só que exporta e gera, como o `generate-client.sh` do template, com o CI comitando a correção** — por que descartei: exige token de escrita e esconde de quem fez o push que esqueceu de gerar. Aqui o CI fica vermelho e a pessoa gera na máquina, como com as migrations.

- **Oxlint + oxfmt (o padrão novo do `create-vite`) Biome no lugar de ESLint + Prettier** — por que descartei: ferramentas em Rust, um binário só e mais rápidas; o Biome é a escolha do template oficial do FastAPI, e o Oxlint virou o padrão do `create-vite`. Mas ESLint + Prettier continua sendo o par que o mercado usa, e o `oxfmt` ainda está em versão 0.x.

### Consequências

O ganho: cada camada reprova pelo seu próprio motivo, em paralelo, e um contrato desatualizado fica vermelho antes de virar `undefined` na tela. O custo: dois arquivos gerados que precisam ser regerados a cada mudança de schema (um passo a mais no fluxo, como o `autogenerate`); a versão do Node passa a morar num arquivo a mais para manter; o `e2e` será o job mais lento e mais frágil do workflow.
Mudar de ideia custa pouco: trocar ESLint + Prettier por Biome muda dois passos e um arquivo de configuração; juntar os jobs de volta é mover passos de lugar. O que não volta atrás sem dor é o `openapi.json` no repositório; quem o remover precisa achar outro jeito de o job `frontend` conhecer o contrato sem importar.

### Como eu saberia que errei

O job `frontend` vermelho por mudança só no backend sem o `openapi.json` ter mudado. Alguém editando o `tipos.ts` à mão para calar o diff. O `e2e` virando o job que todo mundo espera e ninguém olha.
