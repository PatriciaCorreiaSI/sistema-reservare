# Reservare — instruções para o Claude

Leia este arquivo antes de qualquer coisa. Ele define **como** trabalhar neste
repositório, não só o que ele é.

## O projeto em uma frase

Sistema de reserva de recursos compartilhados (salas, equipamentos, estações),
construído como exercício de engenharia de software. O tema é o veículo; o
conteúdo é modelagem com garantias no banco, concorrência, testes e automação.

**O invariante que dá razão ao projeto:**

> Duas reservas ativas nunca podem se sobrepor no mesmo recurso.

Garantido de forma declarativa no PostgreSQL (`tstzrange` + `EXCLUDE` com
`btree_gist`), não em Python — porque entre verificar disponibilidade e gravar
existe uma janela em que outra transação insere.

Documentação viva: [`docs/ROADMAP.md`](docs/ROADMAP.md) (plano e etapas),
[`docs/modelo.md`](docs/modelo.md) (modelo de dados e regras de negócio),
[`docs/api.md`](docs/api.md) (contrato HTTP: schemas, rotas, códigos e o porquê),
[`docs/adr/`](docs/adr/) (decisões de arquitetura).

## Quem decide

A autora é a arquiteta. Você é tutor e revisor — **não** implementador por
padrão. Esta é a regra mais importante do arquivo, e a que é mais fácil de
violar sem perceber.

O objetivo do projeto não é o código existir: é ela conseguir explicar cada
linha em voz alta. Código que você escreve antes de ela tentar não avança o
projeto — ele o desfaz.

### O protocolo das quatro fases

Antes de escrever implementação, verifique em que fase ela está:

1. **Decidir** — ADR aberto: qual o problema, quais as opções, qual escolho, o
   que custa. Sem código. Se ela pedir código e não houver ADR para uma decisão
   relevante, pergunte pelo ADR primeiro.
2. **Desenhar** — nomes de tabelas e colunas, assinaturas sem corpo, nomes de
   rotas, e o teste que deveria passar.
3. **Tentar sozinha** — a primeira tentativa é dela, mesmo feia, mesmo errada.
   **Não pule esta fase por ela.**
4. **Revisar e ensinar** — aqui você entra de verdade: _o que está frágil
   aqui?_, _que caso não foi considerado?_, _por que isso falha sob
   concorrência?_, _como seria a versão profissional, e por quê?_

### Como se comportar na prática

- Pergunte em que fase estamos quando não estiver claro.
- Explique o porquê antes do como. Conceito primeiro, comando depois.
- Ao revisar, o ciclo é de **uma rodada** (acordado em 2026-09-18): ela tenta uma vez; você
  diz o que está certo e, para o que errou, traz **a resposta certa** com o conceito ao lado —
  nunca uma segunda rodada de dicas sobre o mesmo ponto. Se a primeira tentativa errou, é porque
  ela não sabe o conceito; dica não ensina o que não se sabe, resposta ao lado do erro ensina.
- Quando ela pedir "escreve pra mim", ofereça primeiro: o desenho, as
  assinaturas, ou o teste que deveria passar. Se ela reafirmar o pedido, é
  decisão dela — escreva, e explique cada trecho.
- Escrever _para ela ler e reescrever_ é diferente de escrever no lugar dela.
  Deixe claro qual dos dois está acontecendo.

### As sete regras do projeto

1. Eu sou a arquiteta. A IA digita, explica, revisa e ensina. Não decide arquitetura.
2. Nenhuma linha entra no repositório que eu não consiga explicar em voz alta.
3. Toda decisão relevante vira ADR — escrito **antes** do código.
4. Tento sozinha antes de pedir revisão.
5. Uma etapa por vez, com o critério de pronto atendido.
6. Todo bug ganha primeiro um teste que o reproduz.
7. Ideia nova vai para o backlog, não para a v1.

## Estado atual

- **Etapa 1 (modelagem): concluída** — `docs/modelo.md`, 6 ADRs escritos.
- **Etapa 0 (fundação): concluída** — `docker compose up` sobe `db` e `api`; `/health` responde
  `200` pelo compose.
- **Etapa 1 (migrations): concluída em 2026-09-10** — as três partes fecharam. O esquema existe em
  SQL e a prova por SQL na mão passa nos sete casos; as três tabelas estão traduzidas para
  SQLAlchemy 2.0 tipado; e a migration `8cf01df862a4` cria tudo do zero, com a prova passando
  contra o banco que o Alembic construiu.
- **Etapa 2 (primeira fatia vertical): concluída em 2026-09-15** — CRUD de `recurso` nas quatro
  camadas e o primeiro `pytest`: 11 testes verdes, isolados por transação (ADR 0011), inclusive o
  `409` do `DELETE`. As três pendências pequenas fecharam em 2026-09-16 (ver o fim da seção).
- **Etapa 3 (autenticação e autorização): concluída em 2026-09-23** — ADRs 0012 e 0013, emendas
  aos 0010 e 0011, desenho em `docs/api.md`. Sete rotas, o comando `criar_admin`, e a suíte em
  `22 passed`. A metade IDOR do critério de pronto **passou para a Etapa 4** (decidido em
  2026-09-23): é critério de aceite das rotas de `reserva`, que ainda não existem.
- **Etapa 4 (reservas, concorrência e estados): próxima**, começando pela fase Decidir. Detalhes
  no fim da seção.

### Já feito

- `.gitignore` na raiz, `.env` protegido antes de existir segredo, `.env.example` versionado.
- Python 3.14 fixado (ADR 0005 substitui a escolha de 3.12 do ROADMAP).
- `uv` com `pyproject.toml` + `uv.lock`; ambiente reprodutível via `uv sync`.
- Layout monorepo: `backend/` (Python) e `frontend/` (Etapa 7); documentação na raiz.
- Camadas em `backend/app/`: `routers`, `services`, `repositories`, `models`,
  `schemas` — irmãs, cada uma com `__init__.py`.
- `GET /health` respondendo `200` fora do container.
- `ruff` e `mypy` como dependências de desenvolvimento, configurados em
  `[tool.ruff]` (`line-length = 88`), `[tool.ruff.lint]` (`select = ["E","F","I"]`)
  e `[tool.mypy]` (`python_version = "3.14"`, sem modo estrito). Os três passam
  limpos: `ruff check`, `ruff format --diff`, `mypy app`.
- `pre-commit` instalado e verificado. `.pre-commit-config.yaml` na **raiz**:
  hooks oficiais `ruff-check` (com `--fix`) e `ruff-format`, em `rev: v0.16.5`
  batendo com o `uv.lock`; e um hook `local` de `mypy` com `language: system` e
  `entry: uv run --directory backend mypy app`. O `--directory` é o que resolve o
  descompasso do monorepo — sem ele o mypy roda da raiz e cai em
  `Config File: Default`, aprovando com a configuração errada, em silêncio.
- ADR 0006: `Dockerfile` em `backend/`, ao lado do serviço, com `context` em
  `backend/`. A alternativa (raiz do repo) foi descartada porque back e front
  partem de bases diferentes (`python:3.14-slim` × `node`) e o padrão é um
  `Dockerfile` por serviço.
- `backend/Dockerfile` escrito e funcionando: `python:3.14-slim` (glibc, ao
  contrário da `alpine`/musl, que faria os wheels compilarem do zero); `uv`
  fixado em `0.12.8` via `COPY --from=ghcr.io/astral-sh/uv:0.12.8`, batendo com
  o `uv --version` local; `WORKDIR /app`; manifestos copiados **antes** do
  código, com `uv sync --locked` entre os dois — é o que preserva o cache de
  camadas quando só o código muda; `CMD` em forma exec (o processo recebe o
  sinal de encerramento, em vez de o `sh` engolir) com `--host 0.0.0.0`, sem o
  qual o uvicorn escuta só o loopback do container e o mapeamento de porta não
  alcança ninguém. Sem `--reload`: na imagem o código é cópia congelada.
- `backend/.dockerignore` (mora na raiz do `context`): barra `.venv` — que aqui
  seria um venv de Windows, inútil em Linux —, `.git/`, caches, `*.pyc` e os
  próprios arquivos do Docker.
- `docker build -t reservare-api .` e `docker run --rm -p 8000:8000` verificados:
  `/health` responde `200` **pelo container**, ainda sem compose.
- `docker-compose.yml` na **raiz** (não em `backend/`): o arquivo orquestra `db` e `api`, então
  precisa enxergar os dois — mesmo raciocínio do ADR 0006, aplicado a quem orquestra em vez de a
  quem constrói. `db` vem de `image: postgres:16` (a versão da stack, pinada — nunca `latest`);
  `api` vem de `build: { context: ./backend, dockerfile: Dockerfile }`, porque essa imagem não
  existe pronta em lugar nenhum. `depends_on` da `api` na condição `service_healthy`, e o
  `healthcheck` do `db` roda `pg_isready -h localhost -U ... -d ...`: forçar TCP é o que evita o
  teste passar contra o servidor temporário que o próprio Postgres sobe durante o `initdb`, antes
  do banco aceitar conexão de verdade. Volume nomeado `db_data` persiste os dados entre reinícios
  (não bind mount: permissão Unix da pasta de dados do Postgres é frágil vindo de um path do
  Windows). Toda porta publicada é prefixada com `127.0.0.1:` — sem o prefixo o Docker publica em
  `0.0.0.0` e o serviço fica visível para a rede local inteira. A API sai em `127.0.0.1:8000` e o
  Postgres em `127.0.0.1:5432`. O banco não nasceu publicado — até 2026-09-09 a inspeção era só por
  `docker compose exec db psql` — e passou a ser porque o Alembic roda do host (decisão registrada
  mais abaixo). O princípio que importa não mudou: nada publicado em `0.0.0.0`; em loopback, só quem
  já roda na máquina alcança, e quem já roda na máquina já lê o `.env`. Este compose é de
  desenvolvimento — o deploy (Etapa 9) usa Postgres gerenciado, fora dele. Decidido em 2026-09-11
  que isto é nota, não ADR: a decisão de fundo (`127.0.0.1` em tudo) ficou de pé; o que envelheceu
  foi o fato.
  **`DATABASE_URL` não existe mais em lugar nenhum.** Ela foi substituída por `DB_HOST`: o serviço
  `api` recebe os três `POSTGRES_*` interpolados mais `DB_HOST: db` literal; o `.env` do host tem
  `DB_HOST=127.0.0.1`. A URL é montada em Python, não escrita — o porquê está na decisão abaixo.
  Live-reload via bind mount do código para dentro do container **foi adiado de propósito** para a
  Etapa 2: montar `backend/` sobre `/app` cobriria o `.venv` Linux do `uv sync` com um `.venv` de
  Windows, e hoje não há código suficiente (só `/health`) para validar a técnica de exclusão do
  subcaminho de verdade.
- `docker compose up` confirmado: `db` fica `(healthy)` antes de `api` subir; `GET /health` responde
  `200` **através do compose**.
- ADR 0007: a `EXCLUDE` recebe `WHERE (cancelada_em IS NULL)` — predicado pelo **cancelamento**, não
  pelo status. A escolha é pelo lado seguro da falha: um estado novo que ninguém previu passa a
  bloquear (erro visível, alguém reclama) em vez de liberar (erro silencioso, o invariante quebra
  sem ninguém ver). Depende do `CHECK` do ADR 0002 estar de pé — se aquele CHECK cair, esta
  constraint passa a proteger a coisa errada. `now()` não pode entrar no predicado: índice não
  aceita expressão mutável, então reservas já concluídas continuam ocupando o índice.
- `docs/esquema-alvo.sql`: o DDL alvo das três tabelas, rodando de ponta a ponta no compose. Todas
  as constraints **nomeadas** (inclusive as FKs, via `CONSTRAINT <nome>` antes do `REFERENCES`) —
  o nome aparece na mensagem de erro do usuário e o Alembic precisa dele para o `downgrade`.
  `CREATE EXTENSION btree_gist` na primeira linha, porque GiST não tem `=` para inteiros sem ela.
  `ON DELETE RESTRICT` nas três FKs — daí nasceu `status_usuario`: se o usuário nunca sai do banco,
  precisa de desativação lógica. Índice manual nas três FKs, porque no Postgres FK **não** cria
  índice do lado que aponta.
- `reserva_formato_semiaberto` fecha dois furos que a `EXCLUDE` sozinha não vê: range **vazio**
  (não sobrepõe nada, entraria sem reclamar) e range **infinito** (sobrepõe tudo, travaria o
  recurso para sempre). Cuidado com `upper_inc`: ele já é falso num range sem fim, então não
  distingue "fim exclusivo" de "sem fim" — é `upper_inf` que faz isso.
- `docs/prova-invariante.sql`: sete casos em SQL puro, todos com o resultado esperado escrito
  **antes** de rodar. Cada caso limpa `reserva` antes de começar, para não herdar estado do
  anterior. `TRUNCATE ... RESTART IDENTITY` no topo torna a prova repetível. Rodar **sem**
  `ON_ERROR_STOP`: metade dos casos deve falhar. Rótulos com `\warn`, não `\echo` — o primeiro
  escreve em stderr, o mesmo canal dos erros, e só assim rótulo e resultado saem em ordem.

### Decisões e aprendizados da Etapa 1

O que segue é o registro do que foi decidido e do que custou tempo ao longo da Etapa 1 — a parte
que não é derivável lendo o código. A etapa está fechada: isto fica como memória, não como plano.
O que vem a seguir está em "Próximo passo", no fim desta seção.

**Decisões fechadas — Fase 1 concluída:**

1. **Onde a `EXCLUDE` mora — ADR 0008:** declarada no `__table_args__` do modelo **e** escrita à
   mão na migration. Motivo: legibilidade, não ganho técnico.
2. **`naming_convention` — adotada**, em `app/models/base.py`; nota em `docs/modelo.md`.

**O que o experimento com o Alembic provou** (SQLAlchemy 2.0.52 / Alembic 1.19.2, comparando
contra o banco real e renderizando o `CREATE TABLE`). Isto vale mais que os dois casos acima:

- **O `autogenerate` faz duas coisas diferentes, e a cegueira só existe numa delas.** Quando a
  tabela **não existe** no banco, ele *renderiza* o modelo inteiro em `create_table` — e aí
  `EXCLUDE` e `CHECK` **vêm junto**, porque estão no `__table_args__`. Quando a tabela **já
  existe**, ele *compara* item a item para achar a diferença — e nesse modo é cego para `EXCLUDE`
  (não a cria quando falta no banco, não a derruba quando falta no modelo, não avisa da
  divergência) e para `CHECK`. É o comparador que é cego, não o renderizador.
  **Consequência prática:** a primeira migration vem completa; as *seguintes*, que alteram tabela
  existente, é que vão calar. *(Corrigido em 2026-09-10: a nota anterior dizia "cego para
  `EXCLUDE`" sem ressalva, porque o experimento só exercitou o comparador — o banco tinha as
  tabelas do `esquema-alvo.sql`. A primeira migration real trouxe a `EXCLUDE` completa, com o
  predicado do ADR 0007, e os nove `CHECK`.)*
- **`CREATE EXTENSION` nunca sai do modelo**, em nenhum dos dois modos: `MetaData` não tem o
  conceito. Essa continua sendo escrita à mão.
- Ele **não** propõe `drop_index` espúrio para o índice GiST que sustenta a `EXCLUDE`.
- Ele **compara `COMMENT ON COLUMN`**. Sem `comment=` no modelo, a primeira migration **apaga** o
  comentário que existe no banco.
- A lição de forma permanece: ele compara algumas coisas e cala sobre outras sem dizer quais —
  tratá-lo como completo é o mesmo erro de forma do `if disponivel: criar()`. Só que a fronteira
  do silêncio é **tabela nova × tabela existente**, não "esta constraint × aquela".
- Na convenção, **só a chave `ck` reescreve nome explícito**, por ser a única com
  `%(constraint_name)s`: `name="status"` vira `ck_recurso_status`. `fk`, `uq` e `ix` respeitam o
  nome dado; `pk` só age quando não há nome; `EXCLUDE` não tem chave e fica intacta.
- `mypy app` passou em código que estourava no import, por causa de `ignore_missing_imports`.
  Ferramenta verde não é prova de que executa — cada uma responde a uma pergunta estreita.

**`docs/esquema-alvo.sql` foi congelado como registro histórico** (cabeçalho no próprio arquivo):
a verdade sobre o esquema passa a ser a migration, e ele não deve mais ser sincronizado.
`docs/prova-invariante.sql` **continua vivo** — ele não cria esquema, só pressupõe que existe, então
dá para rodá-lo contra o banco que o Alembic construir. É o teste de aceitação da Etapa 1.

**As dependências não existiam.** `sqlalchemy`, `alembic` e o driver nunca tinham entrado no
`pyproject.toml` — o `import app.models` que parecia funcionar na sessão anterior rodava no venv
solto do experimento com o Alembic, não no projeto. Instalados agora: SQLAlchemy 2.0.52, Alembic
1.19.2 e `psycopg[binary]` 3.3.5. O **driver** foi escolhido pelo critério de não fechar porta: o
`psycopg` 3 traz síncrono e assíncrono no mesmo pacote, então a decisão continua aberta —
`psycopg2` (só síncrono) ou `asyncpg` (só assíncrono) já teriam decidido por baixo do pano.
**Débito: ADR de síncrono × assíncrono**, adiado de propósito para depois do `reserva.py`.

**`app/models/reserva.py` está escrito e o DDL renderizado bate com o alvo** — as três FKs com
`ON DELETE RESTRICT`, os quatro `CHECK`, os três índices e a `EXCLUDE` completa com o predicado do
ADR 0007. O que essa tabela ensinou, e não é derivável do código:

- **Cada `mapped_column` tem duas vagas com vocabulários diferentes.** A anotação descreve o valor
  **Python** (`datetime`, `Range[datetime]`); o argumento descreve o tipo **no banco**
  (`DateTime(timezone=True)`, `TSTZRANGE()`). Repetir o mesmo nome nas duas é o erro natural, e o
  `TSTZRANGE` na anotação estoura com `'SchemaItem' object ... expected`.
- **Tipo explícito ganha da anotação.** `Mapped[int] = mapped_column(String(15))` cria `VARCHAR`.
  Nem `ruff` nem `mypy` veem isso — só o Postgres, na migration, com `incompatible types`.
- **Cada opção pertence a um parêntese.** `ondelete` é do `ForeignKey`; `index=True` é do
  `mapped_column`. Trocar dá `Additional arguments should be named <dialectname>_<argument>`.
- **A `ExcludeConstraint` é a única que não engole SQL cru.** O `CheckConstraint` cola qualquer
  string dentro de `CHECK (...)` sem ler nada; a `ExcludeConstraint` exige tuplas
  `(coluna, operador)` porque precisa saber quais colunas entram no índice GiST. O operador é `=` e
  `&&` — o `WITH` é gerado por ela. O `WHERE` do ADR 0007 é o argumento `where=`, e recebe expressão
  Python (`cancelada_em.is_(None)`), não string.
- **`Index(name, *colunas)`** — o primeiro posicional já é o nome. Optamos por `index=True` nas três
  colunas: a convenção gera `ix_reserva_id_usuario` e irmãos sozinha, sem `__table_args__`.
- **A convenção `ck` exige `name=` explícito** (`InvalidRequestError: ... requires that constraint
  is explicitly named`). Aspas triplas ajudam a quebrar SQL longo, mas fechar depois do `name=`
  engole o argumento e cai nesse erro.
- **As FKs não colidem:** a chave `fk` inclui `%(referred_table_name)s`, então as duas que apontam
  para `usuario` saem `fk_reserva_id_usuario_usuario` e
  `fk_reserva_cancelada_por_id_usuario_usuario`.
- **Só entra no `Base.metadata` o módulo que alguém executa.** Sem `Reserva` no `__init__.py`, o
  `autogenerate` compararia um metadata sem `reserva` contra um banco sem `reserva`, concluiria que
  está tudo em ordem e geraria migration **vazia**, em silêncio.
- **`CREATE EXTENSION btree_gist` não tem como sair do modelo** — `MetaData` não tem conceito de
  extensão. A primeira migration precisa criá-la **à mão, antes** da tabela `reserva`, ou o
  `CREATE TABLE` falha; e o `downgrade` tem de decidir se a derruba (pode quebrar outra coisa no
  mesmo banco).
- O VS Code aponta para o Python global porque o `.venv` mora em `backend/` e o workspace é a raiz —
  **o mesmo descompasso de monorepo** que o `--directory backend` resolveu no `pre-commit`. Corrige
  em *Python: Select Interpreter*.

**ADR 0009 — a API é síncrona.** A decisão nasceu com o título errado ("qual template do
`alembic init`") e foi reescrita: o template é *consequência*, a decisão é a API. O que pesou não foi
"async é difícil", e sim que o teste de concorrência — o coração do projeto — fica demonstrável com
threads: duas threads, duas conexões, um ponto de sincronização, concorrência visível. Em async num
único event loop, o esforço migra de *provar que o banco está certo* para *provar que o teste está
concorrendo de verdade*. O custo aceito está escrito no ADR: quem revisar isto como portfólio pode
esperar `async` e notar a ausência. **Compromisso que decorre dele:** os repositories usarão
`selectinload` explícito desde o começo, para que a conversão futura seja mecânica — restrição sobre
código que ainda não existe, e que se perde se ninguém a escrever.

Dois fatos aprendidos ao escrever o ADR, ambos invertidos na primeira versão: **carregamento
preguiçoso é comportamento do síncrono** — async o proíbe (`MissingGreenlet`), e é por proibir que
obriga o `selectinload`. E o **threadpool do FastAPI é limitado** (~40 threads): ele não cresce
consumindo RAM, ele **enche e as requisições passam a esperar na fila**. O sintoma é latência
subindo, não memória estourando — muda o que procurar ao medir.

**Decisão 2 — o Alembic roda do host** (opção B), com a porta do Postgres publicada em
`127.0.0.1:5432`. Razão: `alembic revision --autogenerate` **escreve um arquivo**, e ele precisa
aterrissar no repositório para ser revisado, completado à mão e commitado. Rodando dentro do
container, o arquivo nasce numa imagem congelada — o que forçaria agora o bind mount adiado para a
Etapa 2, ou um `docker compose cp` a cada iteração. A porta publicada é consequência desta decisão,
e ficou registrada como nota no trecho do compose, não como ADR. **Esta decisão pode ser revista
quando o bind mount entrar (Etapa 2):** com o código montado dentro do container, o arquivo da
migration aterrissaria no repositório de qualquer forma, e o argumento principal para rodar do host
enfraquece. Se sobrar decisão real nesse momento, aí sim é matéria de ADR.

**A URL do banco é derivada, não escrita.** Havia três formas: escrever a
`DATABASE_URL` inteira nos dois lugares; usar uma variável com *fallback* para `localhost`; ou
derivar de `POSTGRES_USER`/`PASSWORD`/`DB` mais um `DB_HOST` **obrigatório**. Ficou a terceira.

O raciocínio, que vale mais que a escolha: a decisão original — *"`DATABASE_URL` é montada dentro do
compose, por isso não existe como chave solta em `.env`"* — tinha o princípio certo (**derivar em vez
de duplicar**) e uma premissa que venceu. Naquele momento havia **um** consumidor da URL, dentro da
rede do compose. Agora há **dois em contextos de rede diferentes**: o container `api`, que enxerga
`db`, e o Alembic no Windows, que só enxerga `localhost`. A URL deixou de ser derivável de uma
fórmula única — ela depende de onde se está olhando. Só o **host** difere, então só ele é escrito
duas vezes; o resto continua derivado.

O *fallback* foi descartado pelo critério do ADR 0007: se a variável sumisse, ele conectaria em
`localhost` **calado**. O que torna um fallback perigoso não é ter alternativa — é ter um padrão
silencioso no fim da cadeia. Por isso `DB_HOST` é obrigatório e o `env.py` deve estourar sem ele.

Montar a URL em Python com `URL.create()` traz um ganho concreto: a senha é **escapada
corretamente**. Uma URL escrita à mão quebra se a senha tiver `@`, `#` ou `/`, e quebra de um jeito
confuso, porque o parser corta no lugar errado.

**Quando o deploy chegar (Etapa 9):** plataformas gerenciadas entregam uma `DATABASE_URL` pronta,
não os componentes. O padrão maduro é aceitar as duas formas — usa a URL se ela vier, senão monta
dos pedaços. Isso é acrescentar um ramo, não refazer a escolha; e não é o fallback ruim, porque as
duas pontas são fontes explícitas.

**Compose e `.env` já editados e validados** (`docker compose config` passa): `db` publica
`127.0.0.1:5432:5432`; o serviço `api` perdeu a `DATABASE_URL` e ganhou os três `POSTGRES_*`
interpolados mais `DB_HOST: db` literal; `.env` tem `DB_HOST=127.0.0.1` (era `localhost` — ver a
armadilha logo abaixo) e `.env.example` a chave vazia com a nota do porquê. Cuidado ao colar saída
de `docker compose config` em qualquer lugar — ela imprime a senha em texto puro.

**O que a ligação do `env.py` ensinou** (sessão de 2026-09-10):

- **`sqlalchemy.url` do `alembic.ini` ficou comentada, não apagada.** Os dois jeitos falham alto se
  o `env.py` não injetar a URL, então segurança de falha empata. O que decidiu foi que o placeholder
  é um convite: `driver://user:pass@...` num repo público pede para alguém colar a URL real ali.
  Comentar preserva a descoberta — quem procurar onde se configura o banco vê a chave e a nota
  apontando para o `env.py`. O `alembic.ini` **não** interpola variável de ambiente.
- **`target_metadata` recebe `app.models.Base.metadata`, importando o pacote.** O
  `prepend_sys_path = .` do `alembic.ini` é o que faz esse import funcionar: põe `backend/` no
  `sys.path` antes do `env.py` rodar.
- **A URL é injetada uma vez, no nível do módulo**, com `config.set_main_option(...)`. As duas
  funções (`offline` e `online`) leem do mesmo objeto `config`, então não é preciso mexer nelas.
  Cuidado: `set_main_option` **devolve `None`** — reatribuir `config` com o resultado apaga o
  objeto, e o erro (`AttributeError` em `NoneType`) aparece quatro linhas adiante.
- **`str()` numa `URL` mascara a senha com `***`.** A conexão falha por "senha incorreta" e o erro
  aponta para o lugar errado. O método que não mascara é `render_as_string(hide_password=False)`.
- **`load_dotenv` quer o caminho de um arquivo, e falha calado.** Apontado para uma pasta, carrega
  zero chaves — e aí o `os.environ[...]` estoura com `KeyError`, que é o comportamento desejado.
  Apontado para o próprio `env.py`, é pior: ele **lê as linhas `CHAVE=valor` do código Python** e
  popula `os.environ` com o texto literal `os.environ["POSTGRES_USER"]`. A chave passa a existir,
  o `KeyError` não acontece, e o erro só aparece na conexão. O caminho é derivado de `__file__`,
  não do diretório atual — `Path(__file__).parent.parent.parent / ".env"`.
- **`os.environ[...]` protege contra chave ausente, não contra chave presente com lixo dentro.**
  Não é defeito da escolha; é o limite dela.

**`DB_HOST=127.0.0.1`, não `localhost`** — a armadilha que custou a maior parte da sessão; está em
`docs/aprendizados.md`. Em resumo: `localhost` é um nome que o Windows resolve para `::1` antes de
`127.0.0.1`; o compose publica a porta só em IPv4; e o driver não tem limite de espera por padrão,
então ele **pendura em vez de falhar**, de forma intermitente. O `healthcheck` do compose protege o
serviço `api`, que tem `depends_on`; ele não protege quem digita comandos no host.

**A primeira migration — `8cf01df862a4`.** Veio quase completa do `autogenerate`, inclusive a
`EXCLUDE` e os nove `CHECK`, porque as tabelas não existiam (ver renderizar × comparar, mais acima).
Foi completada à mão com três coisas:

1. `op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")` como **primeira** operação do
   `upgrade()`. `op.execute` manda SQL cru — é a saída para o que não tem `op.alguma_coisa`.
2. Os dois `CHECK` longos reescritos com aspas triplas. O `autogenerate` os colapsa numa string de
   390 caracteres com `\n` escapado, o que estoura o `E501` — e o `ruff format` **não** resolve,
   porque ele quebra chamadas de função, não strings. Reformatar não muda nada no banco: o Postgres
   guarda a **árvore** da expressão, não o texto. Os parênteses redundantes somem e `IN (...)` volta
   como `= ANY (ARRAY[...])`.
3. Um comentário no `downgrade()` dizendo que a `btree_gist` **não** é derrubada de propósito —
   ausência não se explica sozinha. O critério: o `IF NOT EXISTS` do `upgrade` admite que a extensão
   pode ser anterior a esta migration, e desfazer o que talvez não tenhamos feito é o erro.
   *(Derrubar não "quebraria o vizinho": o Postgres recusa `DROP EXTENSION` com dependentes. O que
   decide é a propriedade, não o estrago.)*

**Antes de rodar `--autogenerate`, confira o estado do banco.** Se as tabelas já existirem, a
diferença é nenhuma e ele gera migration **vazia**, sem erro nem aviso — e ela passaria no `upgrade`
sem reclamar, porque as tabelas já estavam lá. Foi preciso `docker compose down -v` para apagar o
volume e recriar do zero; sem o `-v`, o `down` preserva os volumes e o banco volta com tudo.

**Critério de pronto da Etapa 1: cumprido em 2026-09-10.** `alembic upgrade head` cria as três
tabelas, a extensão e a `EXCLUDE` num banco vazio; `docs/prova-invariante.sql` passa nos sete casos
contra esse banco; `downgrade base` deixa só a `alembic_version` vazia, com a `btree_gist`
instalada. No caso 7 a prova mostra duas camadas de defesa em profundidades diferentes: o limite
invertido é recusado pelo **tipo** `tstzrange`, antes de existir linha para testar, e a
inclusividade trocada — um range válido — é barrada pelo `ck_reserva_formato_semiaberto`.

### Decisões e aprendizados da Etapa 2

**Etapa 2 — primeira fatia vertical, concluída em 2026-09-15.** Um recurso completo, da requisição
HTTP ao banco e de volta, com teste: CRUD de `recurso` em `routers/` → `services/` →
`repositories/`, schemas Pydantic separados por direção, e o primeiro `pytest` com banco de teste
isolado. O critério de pronto, os conceitos novos e as armadilhas estão na Etapa 2 do
[`docs/ROADMAP.md`](docs/ROADMAP.md). Como na Etapa 1, o que segue é registro do que foi decidido e
do que custou tempo — a parte que não é derivável lendo o código.

**Fase Decidir: fechada em 2026-09-11.** Duas decisões, ambas em ADR, que restringem todo o código
da etapa:

- **ADR 0010 — a requisição é a transação.** Uma `Session` por requisição (ela não é segura entre
  threads; a API é síncrona, então cada requisição é uma thread). A dependência `obter_sessao` faz
  `yield session`; depois do `yield`, `commit()` se o handler voltou sem exceção, `rollback()` se
  uma exceção passou, `close()` sempre. **Nenhuma camada chama `commit()`.** O custo aceito é o
  erro do banco ficar longe do código — por isso a regra: **todo repository que escreve faz
  `session.flush()` antes de devolver.** O fato que sustenta a regra: constraint é verificada no
  fim de cada comando (salvo `DEFERRABLE`, que a nossa não é), e o `INSERT` só viaja no `flush`
  — então o `IntegrityError` aparece no `flush`, dentro do repository, onde o service acima
  consegue traduzi-lo em exceção de domínio. Sinal de erro: `IntegrityError` chegando ao cliente
  como `500`.
- **ADR 0011 — isolar cada teste numa transação desfeita no fim.** Banco `reservare_test`
  separado, no mesmo Postgres; esquema construído por `alembic upgrade head` uma vez por rodada
  (prova a migration junto). Padrão: o teste abre uma transação, `dependency_overrides` troca
  `obter_sessao` por uma que entrega a `Session` presa a essa transação **sem comitar**, e o
  teste faz `rollback` no fim. O ADR 0010 é o que torna isso simples — se algum repository
  comitasse, seria preciso *savepoint*. Exceção **nomeada desde já**, com marcador próprio do
  `pytest`: testes que precisam de transação real (o de concorrência da Etapa 4 é o primeiro)
  comitam de verdade e limpam com `TRUNCATE` depois. Sinal de erro: teste que passa sozinho e
  falha na suíte; teste de concorrência travado esperando.

Fato aprendido ao decidir, que vira o centro da Etapa 4: quando a transação 2 tenta inserir sobre
uma linha que a 1 fez `flush` mas não comitou, o Postgres **não recusa — espera**. A 2 fica
bloqueada até a 1 decidir: `commit` na 1 dá erro da `EXCLUDE` na 2; `rollback` na 1 deixa a 2
entrar. É por isso que o teste de concorrência precisa de `commit` real, e não cabe na transação
desfeita.

**Fase Desenhar: fechada em 2026-09-14** em `docs/api.md` — os três schemas, a tabela de rotas
com códigos e o porquê de cada escolha. Três convenções da fatia, registradas lá e não em ADR:
recurso nasce `ativo` (o service atribui, não o cliente); `PATCH` parcial e não `PUT`
(`exclude_unset=True`; o caso real é desativar, um campo só); `DELETE` apaga de verdade e devolve
`409` quando a FK `ON DELETE RESTRICT` de `reserva` recusa. `nome_recurso` **não** é único, então o
`POST` não tem caso de `409`.

**Fase Tentar sozinha: código pronto, sem teste (2026-09-14).** Escrito pela autora, um método por
vez, com `ruff` + `mypy` limpos e o caminho feliz verificado à mão pelo `/docs`:

- `app/db.py` — `url_do_ambiente()` (devolve `URL`, não string), `engine`, `FabricaDeSessao` e
  `obter_sessao` (ADR 0010 linha a linha). O `migrations/env.py` **importa** `url_do_ambiente` de
  lá — a URL tem um dono só; o `render_as_string(hide_password=False)` ficou no `env.py`, que é
  quem precisa da string. Provado com `alembic current` → `8cf01df862a4 (head)`.
- `app/repositories/recurso.py` — `RecursoRepository(sessao)`, cinco métodos, nenhum `if`.
  Leitura: montar (`select`) → executar (`scalar`/`scalars`). Escrita: `add`/`delete`/alterar o
  objeto → `flush`; nunca `commit`. `listar` devolve `Sequence[Recurso]` (o que `.all()` promete),
  com `order_by` obrigatório para a paginação ser estável.
- `app/services/excecoes.py` — `ErroDominio` (base), `RecursoNaoEncontrado`, `RecursoEmUso`.
- `app/services/recurso.py` — `RecursoService(sessao: Session = Depends(obter_sessao))` constrói o
  repository no `__init__`. É a única camada com `if`/`for`/`try`: `None` vira
  `RecursoNaoEncontrado`; `criar` faz `Recurso(**dados.model_dump(), status_recurso="ativo")`;
  `atualizar` aplica `model_dump(exclude_unset=True)` com `setattr`; `remover` traduz
  `IntegrityError` em `RecursoEmUso` com `raise ... from erro`.
- `app/schemas/recurso.py` — `RecursoCriar`, `RecursoAtualizar` (tudo `| None = None`),
  `RecursoResposta` (`from_attributes=True`, a única linha que liga schema a modelo).
- `app/routers/recurso.py` — `APIRouter(prefix="/recursos")`, cinco handlers, cada um recebe
  `service: RecursoService = Depends()` e devolve `RecursoResposta.model_validate(...)`. Sem `try`.
- `app/main.py` — dois `@app.exception_handler`: `RecursoNaoEncontrado` → `404`, `RecursoEmUso` →
  `409`, ambos com `{"detail": ...}` (o formato que o `422` do FastAPI já usa).

Verificado à mão: `GET` por id `200`/`404`, `POST` `201` com `status_recurso: "ativo"`, `GET` lista,
`PATCH` `404`, `DELETE` `204`. **O `409` do `DELETE` nunca foi exercitado** — não há `reserva` no
banco de desenvolvimento (a prova da Etapa 1 limpa `reserva` ao fim de cada caso), então a FK não
tinha o que proteger. Provocá-lo exige `usuario` + `reserva`; é trabalho das fixtures do `pytest`.

Dois aprendizados desta sessão que as ferramentas não pegam: `status_recurso="arivo"` (typo numa
string) passou por `ruff` e `mypy` — só o `CHECK` do banco, no `flush`, pegaria, como `500`; e uma
chamada sem `=` (`self.buscar_por_id(id)` sem guardar o retorno) só apareceu como "nome não
definido" duas linhas abaixo. Os dois são o argumento do `pytest`.

**Dívida conhecida da fatia:** `criar` e `atualizar` deixam `IntegrityError` (um `CHECK` de
ocupação ou de horário) subir cru → `500`. Só `remover` traduz. A Etapa 4 trata isso distinguindo
*qual* constraint falhou; por ora fica registrado, não escondido.

**O primeiro `pytest` — feito em 2026-09-15.** Onze testes verdes em `backend/tests/`: `test_health`,
caminho feliz das cinco rotas, os três `404`, o `422` e o `409` do `DELETE` — o único caso que nunca
tinha sido exercitado, agora provado de ponta a ponta (FK `ON DELETE RESTRICT` recusa →
`IntegrityError` no `flush` → `RecursoEmUso` → `409`). O que a sessão ensinou e não está no código:

- **A URL de teste é derivada, não escrita** — `url_do_ambiente().set(database="reservare_test")`.
  Para o Alembic mirar nesse banco, o `env.py` ganhou uma condição (opção 2, escolhida entre três:
  `subprocess` com `POSTGRES_DB` trocado, esta, ou `-x` do Alembic): só deriva a URL do `.env` se
  `config.get_main_option("sqlalchemy.url")` for `None`. Quem chama (o `conftest.py`) injeta a URL
  com `set_main_option` e roda `command.upgrade(config, "head")` como biblioteca, no mesmo
  processo. Custo registrado: se alguém descomentar o placeholder do `alembic.ini`, o `env.py`
  passa a respeitá-lo em vez de derivar. É o ramo "aceita a URL se vier, senão monta dos pedaços"
  previsto para a Etapa 9 — antecipado por um motivo real.
- **O `env.py` é o chamado, não o chamador.** A primeira tentativa colocou
  `alembic.command.upgrade(...)` dentro dele — recursão infinita, porque é o `upgrade` que carrega
  o `env.py`. A chamada programática pertence a quem manda rodar.
- **O banco `reservare_test` foi criado à mão** (`CREATE DATABASE` no psql); o Alembic cria
  tabelas, não bancos. `CREATE DATABASE` copia `template1`, então o banco novo nasce **sem**
  `btree_gist` — o `CREATE EXTENSION IF NOT EXISTS` da migration foi exercitado de verdade pela
  segunda vez.
- **Fixture não é `Depends()`.** A analogia "injeção de dependência" levou a `self`, `Depends(...)`
  e anotação de tipo como forma de pedir uma fixture. No pytest só o **nome do parâmetro** importa;
  o decorador `@pytest.fixture` é o que torna a função fixture; `test_` no nome a transforma em
  teste. Escopo `session` para o engine e o `upgrade` (uma vez por rodada); `function`, o padrão,
  para a transação e o `TestClient` (uma vez por teste). Escopo estreito pode depender do largo,
  nunca o contrário.
- **A cadeia do `conftest.py`:** `url_de_teste` → `engine_de_teste` (upgrade + engine, `dispose`
  depois do `yield`) → `sessao` (`connect` → `begin` → `Session(bind=conexao)`; depois `close`,
  `rollback`, `close`) → `client` (uma função interna que faz só `yield sessao` entra em
  `app.dependency_overrides[obter_sessao]` — **a função, sem parênteses**, não a `Session`;
  `clear()` depois do `yield`). A substituta não faz `commit`/`rollback`: a transação é da fixture.
  O `engine` do `app/db.py` fica criado e ocioso — ninguém pede conexão a ele.
- **Um teste pode pedir `client` e `sessao` juntos** e recebe a *mesma* sessão, porque o pytest
  cria cada fixture uma vez por teste. É o que permite montar o cenário do `409` gravando `Usuario`
  e `Reserva` direto pelos modelos (`add` + `flush`, sem `commit`) e agir por HTTP. Regra que
  ficou: **prepara pelo caminho mais direto, age pela interface que está sendo testada** — montar
  por `POST /reservas` faria o teste do `DELETE /recursos` depender de rotas que não são as dele.
  Um teste é três atos: preparar, agir, conferir.
- **O `TestClient` relança exceção não tratada** em vez de devolver `500`. Um `IntegrityError` cru
  aparece como traceback no teste, não como número — a dívida de `criar`/`atualizar` vai se
  manifestar assim.
- **`Range(inicio, fim, bounds="[)")` com `tzinfo=UTC`** é a primeira `reserva` gravada por
  Python; passou pelos `CHECK` sem ajuste. `time` viaja como `"08:00:00"` no JSON, nos dois
  sentidos.
- **Dois *warnings* ficaram, de propósito.** `StarletteDeprecationWarning` pedindo `httpx2` no
  lugar de `httpx` (a stack mudou depois do ROADMAP; trocar é `uv remove httpx` +
  `uv add --dev httpx2` e rodar a suíte — backlog). E `SAWarning: transaction already deassociated
  from connection`, só no teste do `409`: o `IntegrityError` no `flush` faz a `Session` desfazer
  sozinha a transação externa, e o `rollback()` da fixture chega tarde. A resposta é a que o ADR
  0011 já antecipou: `Session(bind=conexao, join_transaction_mode="create_savepoint")` — a sessão
  desfaz só o *savepoint* e a transação da fixture segue de pé.
- Miudezas que custaram tempo: `\c` e `\dt` são do psql, não do PowerShell; `git status` com
  `MM` depois de o pre-commit corrigir um arquivo é o ciclo normal (`git add` de novo e repetir o
  commit — rodar `ruff format` antes do `add` evita a dupla); de dentro de `backend/` o caminho é
  `migrations/env.py`, sem o prefixo.

### Próximo passo

**As três pendências da Etapa 2 fecharam em 2026-09-16** (savepoint na fixture `sessao`, fixture
`recurso_criado`, vocabulário do pytest no `aprendizados.md`): `11 passed`, e o `SAWarning` do teste
do `409` sumiu — só resta o warning do `httpx2`, que é backlog. O que a sessão ensinou:

- **Argumento nomeado não é variável.** `join_transaction_mode="create_savepoint"` numa linha solta
  é Python válido que cria uma variável local que ninguém lê; a `Session` da linha seguinte não
  sabe que ela existe. O lugar é dentro do parêntese, ao lado do `bind=`. Nem `ruff` nem `pytest`
  apontam — o warning só continua lá.
- **Fixture não se chama, se recebe** — dos dois lados. Na definição, `recurso_criado(client)` pede
  o `client` pelo parâmetro (sem isso, o nome `client` dentro da função é a *função* `def client`,
  que não tem `.post`). No uso, `recurso_criado` entra no parâmetro do teste, sem parênteses e sem
  `import` do `conftest.py`. Um teste pode pedir `client` e `recurso_criado` juntos: é o mesmo
  `client` por baixo, porque o pytest cria cada fixture uma vez por teste.
- **A fixture devolve o `dict` do recurso, não a resposta HTTP** — é o que cinco dos seis testes
  querem. O `test_criar_recurso` **não** usa a fixture: nele o `POST` é o ato, não a preparação,
  e o `assert 201` precisa da resposta inteira. Se o formato do `POST` mudar, ele é o único que
  quebra *por causa do `POST`*; os outros quebram pela fixture, o que é sinal diferente.
- **Bug antigo corrigido de carona:** a fixture `client` fazia `return TestClient(app)` seguido de
  `app.dependency_overrides.clear()` — código morto, o `clear()` nunca rodava. Virou `yield`. Os
  11 testes já passavam antes: verde nunca provou que o `clear()` executava.

**Etapa 3 — autenticação e autorização: fase Decidir aberta em 2026-09-16.** O ADR 0012 está escrito
e aceito: **JWT curto (access, 15 min) + refresh token opaco no banco**, que é o que o logout apaga.
O critério, escrito no ADR, é exercitar o padrão do mercado — com a admissão, na seção de
alternativas, de que a sessão opaca seria a escolha tecnicamente mais simples e com garantia mais
forte para um serviço só, síncrono, já dentro de uma transação por requisição (ADR 0010). A
admissão aparece **uma vez**, no lugar dela; repetida na Decisão e nas Consequências fazia o ADR
soar como pedido de desculpas — foi a lição de forma da sessão. Sinal de erro registrado: admin
desativa um usuário e ele continua operando por até 15 min com o access que já tem.

**Fase Decidir fechada em 2026-09-17 com o ADR 0013: o token viaja no cabeçalho
`Authorization: Bearer`**, guardado pelo frontend só em memória — nunca em `localStorage`. O que
pesou não foi só XSS × CSRF: foi que, na Etapa 7, Vite (`:5173`) e API (`:8000`) são origens
diferentes para o navegador, e cookie entre origens exige CORS com credenciais, `SameSite=None` e
`Secure` (HTTPS). O híbrido (access no cabeçalho, refresh em cookie restrito a `/auth/refresh`) ficou
registrado como evolução natural, não como v1. **Dois compromissos sobre código que ainda não
existe**, do mesmo tipo do `selectinload` do ADR 0009: o token só em memória (Etapa 7), e a
extração do token concentrada numa dependência só, para que a troca de transporte seja localizada
no backend. **Pergunta que o ADR empurra para a fase Desenhar:** com o refresh na memória do JS, ele
é a exposição real (vale dias, não 15 min) — rotacionar a cada uso permite detectar reuso de um
refresh antigo e invalidar a família toda.

O que a revisão do ADR ensinou, e vale para os próximos: **consequência não é sinal** — o refresh
exposto é o que a escolha custa; o sinal de erro é o que se observa *antes* do estrago (token em
`localStorage` numa revisão, requisito de sessão entre subdomínios). **XSS rouba, CSRF usa sem
ver** — a primeira versão falava em "vazamento" do cookie, e o atacante de CSRF nunca vê o cookie.
E o `docs/aprendizados.md` registra o conceito **inteiro e universal**; o que o projeto decidiu
sobre ele fica no ADR — não alinhar um ao outro.

**Fase Desenhar da Etapa 3 — item 1 fechado em 2026-09-17.** A tabela `refresh_token` está em
`docs/modelo.md`, com as regras de negócio dela. O que ficou decidido lá, e o raciocínio que não
está no documento: **hash SHA-256, não Argon2** — não por velocidade, mas porque (a) a lentidão do
Argon2 só compra algo contra dicionário, e token de 32 bytes aleatórios não tem dicionário; (b) o
salt do Argon2 torna o hash não determinístico, e o servidor precisa de `WHERE hash_token = ...`.
**Marcar `revogado_em`, não apagar** — a detecção de reuso exige que o token usado continue
existindo; apagado, ele fica indistinguível de um token inventado (mesmo critério do ADR 0007:
falha visível). **Rotação com `familia_token` UUID** — reuso de um refresh revogado revoga a
família inteira. **`ON DELETE CASCADE`** na FK — token não é histórico; convive com o `RESTRICT`
da reserva porque só dispara para usuário sem reserva. Critério que custou uma rodada: "banco
garante" = uma constraint recusa a linha gravada direto pelo psql; "serviço garante" = Python
decide. Ao virar modelo SQLAlchemy: índice em `familia_token` e em `id_usuario`.

**Fase Desenhar da Etapa 3 — fechada em 2026-09-18**, itens 2 a 4 em `docs/api.md`, nas seções
`## Autenticação` (schemas, dependências, rotas de `/auth`) e `## Usuário` (schemas, `POST
/usuarios`). O que ficou decidido lá, e o raciocínio que não está no documento:

- **Cadastro mora em `/usuarios`, não em `/auth`.** `/auth` é o conjunto de rotas sobre a sessão
  de quem chama (*eu* entro, renovo, saio); cadastrar outra pessoa é CRUD de `usuario`. Só admin
  cadastra (`403`); o **primeiro admin** nasce fora da API, por um comando `criar_admin` com senha
  de variável de ambiente — a escrever na implementação. Nos testes a fixture grava o admin pelo
  modelo.
- **`refresh` e `logout` são `POST`** (escrevem `revogado_em`; `GET` promete não alterar e poria o
  token na URL, que vai para log). O refresh viaja **no corpo**, nunca no `Authorization` — quando
  `/auth/refresh` é chamado o access já expirou, então ele não autentica nada ali. Rotação: access
  e refresh novos a cada uso; reuso de revogado → `401` e família inteira revogada, e o cliente
  legítimo também cai (custo aceito: o servidor não sabe qual dos dois é o ladrão).
- **Logout é idempotente**: refresh já revogado ou inexistente também devolve `204`.
- **Login devolve uma resposta só** (`401`, mesmo texto) para e-mail inexistente, senha errada e
  usuário inativo — para a API não servir de lista de quem está cadastrado.
- **Payload do JWT: `sub`, `exp`, `privilegio`.** O `privilegio` entra para a dependência
  autorizar sem ir ao banco; o custo (rebaixado segue admin por 15 min) é o mesmo já aceito no
  ADR 0012. Não entra e-mail, nome, senha, hash.
- **Duas dependências encadeadas**: `obter_usuario_atual` (lê `HTTPBearer`, valida assinatura e
  `exp`, devolve `UsuarioAtual` com `id_usuario` + `privilegio`, `401`) e `exigir_admin` (depende
  da primeira, `403`). `/auth/*` não declara nenhuma.

Conceitos que custaram rodadas, agora no `aprendizados.md` ou aprendidos na sessão: **schema não
é tabela** (o schema descreve o que viaja no JSON; `hash_token`, `expira_em`, `revogado_em` são
calculados ou consultados pelo servidor e nunca entram numa entrada — tudo que o cliente manda ele
pode mentir; `UsuarioCriar` leva `senha` em texto, o Argon2 é do servidor); os códigos `4xx` como
perguntas distintas (`401` quem é? → `403` pode? → `422` bem formada? → `409` conflita?) —
*(corrigido em 2026-09-23: a primeira versão punha o `422` na frente; o teste do `403` provou o
contrário — corpo inválido com token de não-admin devolve `403`. No FastAPI as dependências rodam
antes de o erro de validação do corpo ser levantado, e identidade antes de conteúdo é o lado
seguro: quem não pode entrar não descobre o formato esperado)*; **dependência como guarda**; e o
que é uma **assinatura**.

**Item 5 foi rebaixado de propósito**: o teste do critério de pronto não vai em prosa no
`api.md` — o mercado escreve o teste direto em Python, e ela já tem onze. Ele vira o primeiro
passo da fase Tentar.

**Metodologia acordada em 2026-09-18** (vale para as próximas revisões): ela tenta **uma** vez; eu
digo o que está certo e trago a **resposta certa** para o que errou, com o conceito ao lado.
Rodadas sucessivas de dicas sobre o mesmo ponto atrapalham em vez de ensinar.

**Fase Tentar da Etapa 3 — aberta em 2026-09-18, dois passos fechados no mesmo dia:**

1. **`backend/tests/test_auth.py`** — `test_refresh_apos_logout_devolve_401`, escrito antes das
   rotas. Fixture `usuario` no `conftest.py` grava pelo modelo, com `SENHA_HASH` (Argon2 de
   `"senha123"` via `pwdlib`, calculado uma vez no nível do módulo — Argon2 é lento de
   propósito). Login e logout por HTTP são preparação; `POST /auth/refresh` é o ato. Estado
   atual e correto: `1 failed, 11 passed`, com `KeyError: 'refresh_token'` — o login ainda não
   existe. Erro pego na revisão: o ato chamava `/auth/logout` de novo, o que provaria o
   *contrário* do decidido (logout é idempotente). Quando comentário e código discordam, um mente.
2. **Modelo `RefreshToken` + migration `de451a039a1a`**, aplicada nos dois bancos. Veio completa
   do `autogenerate` (tabela nova → renderiza). O que custou tempo, e as ferramentas não pegam:
   - **`NOT NULL` vem da anotação.** `Mapped[datetime]` gera `NOT NULL`; `Mapped[datetime | None]`
     permite nulo. A primeira versão inverteu os três instantes — `revogado_em NOT NULL` tornaria
     impossível gravar um token vivo, e o comentário da coluna contradizia o tipo ao lado.
   - **Vírgula faz tupla, parêntese não.** `__table_args__ = (CheckConstraint(...))` sem a vírgula
     final é o próprio `CheckConstraint`, e o SQLAlchemy recusa. Com um item só, a vírgula é tudo.
   - **`ndex=True`** (typo) passou por `ruff` e `mypy` — `mapped_column` recebe `**kw` — e só
     estourou no import: `Additional arguments should be named <dialectname>_<argument>`. A
     verificação que falta às ferramentas é `uv run python -c "import app.models"`.
   - **Erros de digitação nos `comment=` viajam para o `COMMENT ON COLUMN`** da migration. Como
     ela ainda não tinha sido aplicada, o caminho foi corrigir o modelo, apagar o arquivo e
     regenerar — migration não aplicada é só texto; depois de aplicada, renomear é outra migration.
   - `ruff --fix` e `ruff format` não quebram **strings**; comentário de coluna longo se quebra à
     mão em duas literais adjacentes (com espaço no fim da primeira).
   - `esquema-alvo.sql` **não** ganha a tabela nova — congelado desde 2026-09-10; a verdade é a
     migration.

**Biblioteca de JWT: `PyJWT`, decidida e instalada em 2026-09-18** (nota, não ADR). Escolhida
contra `python-jose` pelo critério que descartou o Passlib: mantida, escopo só JWT, e é o que o
tutorial do FastAPI usa desde 2024 — `python-jose` está parado e teve CVEs em 2024. A chave
`JWT_SEGREDO` já está no `.env` (`secrets.token_urlsafe(48)`) e vazia com nota no `.env.example`.
No código ela será `os.environ["JWT_SEGREDO"]`, **obrigatória, sem fallback** — critério do
`DB_HOST`.

**Sessão de 2026-09-21 — os dois repositories, os schemas de `/auth` e o `security.py` fecharam**
(`RefreshTokenRepository`, commit `21032a9`; `UsuarioRepository`, `be33f5b`; `security.py` +
`load_dotenv` no pacote + `buscar_por_id` + schemas, `e9f4929`). Suíte em `1 failed, 11 passed`,
o estado correto. O que a sessão ensinou, e não está no código:

- **Repository deriva do uso, e o uso tem de ser listado inteiro.** Os métodos saíram de passar
  rota a rota do `api.md` marcando cada ida ao banco. `buscar_por_id` de `usuario` foi esquecido na
  primeira lista porque o **refresh** não foi percorrido: o JWT novo precisa de `privilegio_usuario`,
  e a linha de `refresh_token` só tem `id_usuario`. A mesma busca é o que faz o usuário desativado
  cair no próximo refresh (sinal de erro do ADR 0012).
- **`buscar_por_hash` devolve também revogados e expirados**, de propósito: a detecção de reuso
  exige enxergar o token revogado. "Válido" é regra do service (`modelo.md`: serviço garante).
- **`revogar_familia` é o primeiro método fora do molde**: `update(...).where(...).values(...)` +
  `execute`, um comando para N linhas, sem objeto. O segundo `where` (`revogado_em.is_(None)`)
  preserva o instante original — timestamp de evento se escreve uma vez.
- **Senha não se busca por hash.** Argon2 tem salt: mesma senha → hashes diferentes, o `WHERE`
  nunca bate. O salt vai dentro do hash guardado; `hasher.verify(senha, hash)` refaz com ele. Por
  isso `UsuarioRepository.buscar_por_email` recebe só o e-mail, e a verificação é do service. É o
  contrário do refresh, cujo SHA-256 é determinístico e por isso serve de chave de busca.
- **Classe × objeto**: `Classe.campo == x` dentro do `where` é pergunta ao banco; `objeto.campo = x`
  fora dele é ordem ao objeto. `add`, `return` e atribuição recebem o objeto (o parâmetro), nunca a
  classe. Uma linha solta com `==` é Python válido que não faz nada — nenhuma ferramenta reclama.
- **`import` é a quarta verificação**: `ruff` e `mypy` leem, o `import` executa. Typo em nome que
  ninguém importa ainda (`Repositoriy`, `criar_acess_token`) passa pelos dois e só estoura no
  `from ... import` de quem usar. `uv run python -c "from app.x import Y"` antecipa isso.
- **Nomes de módulo**: convenção registrada em Convenções (infra em inglês, domínio em português).
  O `privilegio` do `api.md`/`modelo.md` virou `privilegio_usuario` em tudo (commit `bd5859e`) — um
  nome só de ponta a ponta, inclusive no payload do JWT e no `UsuarioAtual`.

**Item 2 (`AuthService`) desenhado, em andamento.** O que já existe e o que ficou decidido:

- `app/security.py` — **pronto e provado** (assina e decodifica no mesmo comando:
  `{'sub': '1', 'exp': 17..., 'privilegio_usuario': 'admin'}`). Funções puras, sem sessão,
  compartilhadas por service e dependência (a dependência do item 4 não vai ao banco e não pode
  carregar um service): constantes `ACCESS_MINUTOS = 15`, `REFRESH_DIAS = 7`,
  `JWT_ALGORITMO = "HS256"`, `JWT_SEGREDO = os.environ[...]` (obrigatória, sem fallback),
  `hasher`; `criar_access_token(id_usuario: int, privilegio_usuario: str, agora: datetime) -> str`,
  `gerar_refresh_token() -> str`, `hash_refresh_token(refresh_token: str) -> str`. Fatos que não
  são deriváveis: `sub` **tem de ser `str`** (PyJWT ≥ 2.10 recusa numérico na decodificação, longe
  do lugar do erro); `exp` aceita `datetime` desde que consciente de fuso — o `agora` de quem chama
  garante; `secrets`, não `random`; `.encode()` porque hash é de bytes. A `decodificar_access_token`
  entra aqui no item 4.
- **`load_dotenv` mora em `app/__init__.py`**, não mais em `db.py`. O `__init__` do pacote roda
  antes de qualquer `app.x`, então `security.py` e `db.py` leem `os.environ` no nível do módulo e
  falham no **startup** se a chave faltar (critério do `DB_HOST`). Custou duas rodadas: primeiro
  só a metade "tirar do `db.py`" foi feita (ninguém carregava o `.env`, o `app` inteiro quebrado);
  depois as linhas foram para `app/repositories/__init__.py` — que só roda quando alguém importa
  `app.repositories`, e de onde os três `.parent` param em `backend/`, não na raiz (`load_dotenv`
  apontado para arquivo inexistente falha calado). O `__init__` que dá a garantia é o do **`app`**.
- `app/schemas/auth.py` — `LoginEntrada`, `RefreshEntrada`, `TokenResposta`, prontos.
- `CredenciaisInvalidas(ErroDeDominio)` → `401`, para login e refresh — a escrever em `excecoes.py`.
- `AuthService(sessao)` com dois repositories: `login(LoginEntrada) -> TokenResposta`,
  `renovar(RefreshEntrada) -> TokenResposta`, `logout(RefreshEntrada) -> None`,
  `_emitir_tokens(usuario, familia_token, agora) -> TokenResposta`. Os corpos em palavras foram
  dados na sessão (login: e-mail → inativo/None/`verify` falso = uma resposta só; renovar: hash →
  None / revogado = reuso → expirado → usuário inativo, depois `revogar` + emitir com a **mesma**
  família; logout: nunca levanta).
- **Decisão do ramo de reuso — fechada em 2026-09-21, emenda ao ADR 0010** (commit `c27dc69`):
  o `UPDATE` da família seria desfeito pelo `rollback` do `obter_sessao` quando
  `CredenciaisInvalidas` atravessa o `yield` — a detecção viraria teatro. A revogação não é parte
  do que deu errado, é a *resposta* a ele, e precisa sobreviver. Decisão: `self._sessao.commit()`
  logo após `revogar_familia`, antes do `raise` — **o único `commit()` fora do `obter_sessao`**,
  nomeado na emenda e apontado na Decisão original. O `create_savepoint` da fixture faz esse
  commit liberar só o savepoint — o ADR 0011 sobrevive. Descartadas: `JSONResponse(401)` no
  router (regra no router; `401` nascendo em dois lugares); sessão independente (a fixture não a
  enxerga, escreveria de verdade no banco de teste). Sinais de erro: um segundo `commit()` fora
  do `obter_sessao`; teste de reuso que confere só o `401` sem olhar o banco.
- **`excecoes.py` ganhou `CredenciaisInvalidas` (`401`, login e refresh — uma exceção só para os
  cinco casos, docstring explica o porquê) e `EmailJaCadastrado` (`409`, `POST /usuarios`)**, no
  mesmo commit.
- **`app/services/auth.py` — `login` e `renovar` prontos e revisados** (2026-09-21); `logout` e
  `_emitir_tokens` são *stubs* (`...` / `raise NotImplementedError`) para o `pre-commit` passar.
  O hook `ruff --fix` apaga os imports ainda não usados (`timedelta`, `RefreshToken`,
  `REFRESH_DIAS`, `criar_access_token`, `gerar_refresh_token`) — recolocar ao escrever o
  `_emitir_tokens`. O que a revisão dos dois métodos ensinou, e as ferramentas não pegam:
  - **`CredenciaisInvalidas` sozinha numa linha não faz nada** — sem `raise`, é uma expressão que
    o Python avalia e descarta; nenhuma ferramenta reclama, e o refresh inválido *passaria*. Mesmo
    fenômeno do `Classe.campo == x` solto. É `raise Classe()`, sempre com `()`.
  - **`!= "ativo"`, não `== "inativo"`** — estado desconhecido bloqueia (critério do ADR 0007),
    nos dois métodos.
  - `||` não existe (`or`); `->` só existe no `def`; `if` sem parênteses salvo para quebrar linha;
    `=` atribui, `==` compara; o `return` do caminho feliz fica **depois** do `if`, não dentro.
  - O `mypy` faz *narrowing*: depois de `if usuario is None: raise`, ele sabe que `usuario` não é
    `None` — por isso o `is None` precisa estar no mesmo `if` do `raise`.
  - Padrão do método: *guard clauses* — cada pergunta do `api.md` é um `if` que sai cedo; quem
    chega ao `return` passou por todas. `agora = datetime.now(UTC)` uma vez por método público.
  - Import "não usado" e variável "não usada" no meio da escrita são promessa, não erro — as
    ferramentas veem o arquivo como está. **Não** rodar `ruff --fix` num arquivo pela metade.

**Sessão de 2026-09-22 — a cadeia da Etapa 3 fechou até as dependências.** Três commits:
`AuthService` completo (`logout` e `_emitir_tokens`), schemas e service de `usuario`, e as duas
dependências. Suíte em `1 failed, 11 passed`, o estado correto — o `test_auth.py` só fecha com os
routers. O que a sessão ensinou, e não está no código:

- **Decisão: o `401` e o `403` nascem como exceção de domínio, tratadas no `main.py`** (opção B,
  contra levantar `HTTPException` na própria dependência). Critério: o mesmo que descartou o
  `JSONResponse(401)` no router na emenda ao ADR 0010 — código de status nascendo em dois lugares
  é um lugar a mais para esquecer. Consequência: o `WWW-Authenticate: Bearer` que a RFC 7235 exige
  em todo `401` passa a ser responsabilidade do handler, e de carona corrige os `401` de login e
  refresh. Nasceu `PrivilegioInsuficiente` (`403`); a docstring de `CredenciaisInvalidas` cresceu
  para admitir o access ausente, malformado ou expirado. Nota, não ADR.
- **O `HTTPBearer` do FastAPI 0.141.1 devolve `401`**, com `WWW-Authenticate` junto, quando o
  cabeçalho falta ou não é `Bearer`. Muito tutorial ainda diz `403` — era verdade em versões
  antigas. Não é preciso `auto_error=False`.
- **`UsuarioAtual` mora em `dependencies.py`, não em `schemas/`**: ele nunca viaja em JSON, é valor
  interno que uma dependência entrega à outra. Manter `schemas/` só com contratos de fio preserva o
  significado da pasta. Módulo em inglês pela convenção (infra), como `security.py` e `db.py`.
- **`Literal` só na entrada.** `UsuarioCriar.privilegio_usuario` leva `Literal["admin", "usuario"]`
  (opção A, escolhida contra deixar cair no `IntegrityError`): sem ele, `"chefe"` morreria no
  `CHECK` e sairia como `409 e-mail duplicado`, mentindo. Custo aceito: a lista existe em dois
  lugares. **Não** leva na `UsuarioResposta` nem no `UsuarioAtual` — guarda-se o que atravessa a
  fronteira vindo de fora, e a assinatura do JWT já é essa guarda; além disso o `!= "admin"` do
  `exigir_admin` já falha do lado seguro (ADR 0007).
- **A divergência `senha` × `senha_usuario_hash` é proteção, não atrito.** Se os nomes batessem,
  `Usuario(**dados.model_dump())` funcionaria e gravaria a senha em texto puro, em silêncio. O
  `TypeError: 'senha' is an invalid keyword argument` é a única barreira automática entre o texto
  da senha e o disco — nenhuma ferramenta do projeto pega isso. Nomes batem quando os **valores**
  são os mesmos; é por isso que em `recurso` o `**model_dump()` cabe e aqui não.
- **`decodificar_access_token` não captura nada** — devolve o payload e deixa o
  `jwt.InvalidTokenError` subir; quem traduz erro em resposta é a dependência. O `algorithms=[...]`
  é obrigatório e é lista: sem ele o PyJWT aceitaria o algoritmo que o próprio token declara
  (`alg: none`). O `sub` volta `str` e a conversão para `int` é de quem monta o `UsuarioAtual`.
- **Classe × objeto reapareceu no `raise` e no `return`.** `UsuarioAtual.privilegio_usuario` dentro
  do `if` compara o campo da **classe**: o `mypy` pega o `return` (`got "type[UsuarioAtual]"`) mas
  **não** pega o `if`, porque o plugin do Pydantic o resolve como `str`. A comparação seria sempre
  falsa e **todo usuário viraria admin**. Mesmo fenômeno do `Classe.campo == x` nos repositories.
- **`raise X from Y` só dentro de um `except`**, e só sobre a variável capturada ali. Fora disso
  inventa uma causa que nunca aconteceu.
- **O `try` tem o tamanho do risco:** envolve a chamada que fala com o banco ou decodifica, nunca a
  construção do objeto nem o `return`.
- **Pytest que não imprime veredito é infraestrutura, não teste.** `collected N items` seguido de
  silêncio = o driver pendurado esperando um Postgres que não responde (aqui, Docker Desktop
  pausado). Sem `connect_timeout` o `psycopg` espera para sempre. Primeiro lugar a olhar:
  `docker compose ps`.
- Miudezas: a **vírgula mágica** no fim de parâmetro quebrado em linhas é lida pelo `ruff format`
  como ordem de manter explodido, além de deixar o diff limpo — diferente da vírgula do
  `__table_args__`, que **cria** a tupla; importar `jwt` de `app.security` funciona e é armadilha
  (some quando aquele módulo parar de usá-lo); e nome de módulo com typo (`depedencies.py`) não dá
  erro, só falha longe.

**Sessão de 2026-09-22 (segunda do dia) — a fatia de autenticação atravessa de ponta a ponta.**
Dois commits: `routers/auth.py` + `routers/usuario.py`, e o `main.py` ligando tudo. A suíte foi de
`1 failed, 11 passed` para **`12 passed`** — o `test_refresh_apos_logout_devolve_401`, escrito em
2026-09-18 antes das rotas, ficou verde sem ser tocado. As sete rotas registradas: `/health`,
`/recursos` (4), `/auth/login`, `/auth/refresh`, `/auth/logout`, `POST /usuarios`. O que a sessão
ensinou, e não é derivável do código:

- **O `prefix` do `APIRouter` é concatenado cru.** `"/auth" + "login"` (sem a barra) é
  `"/authlogin"` — rota que existe, aparece no `/docs` e nunca é chamada. `ruff`, `mypy` e o
  import passam; o sintoma seria `404` em `POST /auth/login`, longe da causa. Mesma família do
  `ndex=True` e do `Repositoriy`: **erro dentro de string não tem quem verifique**. A verificação
  que falta virou rotina para todo router novo:
  `uv run python -c "from app.routers.X import router; [print(r.path) for r in router.routes]"`.
  No `app` inteiro esse truque **não** funciona: o FastAPI 0.141 guarda `_IncludedRouter` preguiçoso
  em `app.routes`, e os caminhos só aparecem em `app.openapi()["paths"]`.
- **O FastAPI decide de onde vem cada parâmetro pela anotação**: nome que está entre chaves no
  caminho → path; tipo simples (`str`, `int`) → **query string**; modelo Pydantic → **corpo JSON**;
  `Depends(...)` → dependências. Escrever `email_usuario: str` num `POST` põe o dado na URL — que
  vai para log de servidor, de proxy e histórico do navegador. É `dados: LoginEntrada`, e o `422`
  vem de graça.
- **`model_validate` só onde há fronteira.** A regra é olhar o que o service devolve: `AuthService`
  devolve `TokenResposta`, que já é schema → o handler devolve direto; `UsuarioService.criar`
  devolve `Usuario`, modelo SQLAlchemy → `UsuarioResposta.model_validate(...)`, senão o hash da
  senha viajaria na resposta. O `mypy` pega este caso (`got "Usuario", expected "UsuarioResposta"`),
  e é a única das quatro ferramentas que pega.
- **Autorização pergunta sobre quem chama, nunca sobre o corpo.** A primeira versão do
  `POST /usuarios` tinha `if dados.privilegio_usuario != "admin": raise CredenciaisInvalidas` —
  isso lê o privilégio do usuário **sendo criado**, então proibia cadastrar usuário comum e liberava
  criar admin para qualquer um, sem token. Quem chama vem do JWT no cabeçalho, que o cliente não
  consegue forjar. São dois campos de mesmo nome na mesma rota: o do corpo é guardado pelo
  `Literal` (`422`); o do token, pelo `exigir_admin` (`403`).
- **Guarda que não entrega valor vai no decorador.** `dependencies=[Depends(exigir_admin)]` em vez
  de um parâmetro que ninguém lê — o `ruff` com `select = ["E","F","I"]` não avisa sobre argumento
  não usado, e a guarda fica visível na linha da rota. A forma com parâmetro
  (`admin: UsuarioAtual = Depends(exigir_admin)`) é para quando o handler **usa** quem chamou —
  será o caso de `POST /reservas` na Etapa 4.
- **`WWW-Authenticate: Bearer` é obrigatório em todo `401`** (RFC 7235): o `401` não diz "vá
  embora", diz "autentique-se, e o esquema é este". O `403` **não** leva o cabeçalho — ali o
  servidor já sabe quem é quem chama e não há nada a negociar. Nada no projeto verifica isso; entra
  no `JSONResponse` pelo argumento `headers=`. Como só o handler produz `401`, os de login e refresh
  ganharam o cabeçalho de carona — era o critério da emenda ao ADR 0010.
- **`F401` pode ser o defeito, não o ruído.** `from app.routers import auth, usuario` sem os
  `include_router` correspondentes é "importado e não usado" — e aqui importar e usar são a mesma
  tarefa em duas linhas. **Não rodar `ruff check --fix`**: ele apagaria os imports, o erro sumiria
  do terminal e o defeito ficaria sem pista. A ferramenta sabe que há inconsistência, nunca qual
  dos dois lados consertar.
- Miudezas: `ruff format` junta parâmetros quebrados quando cabem em 88 — a **vírgula mágica**
  depois do último é o que manda manter explodido (diferente da vírgula do `__table_args__`, que
  *cria* a tupla); `ruff format` não quebra **import** longo, que se quebra com parênteses, como os
  `CHECK` longos da migration se quebraram com aspas triplas; arquivo sem `\n` final faz o git
  marcar a última linha como alterada no próximo diff; e `git commit -a` não pega arquivo novo,
  só o que já é rastreado (`??` × `M`).

**Sessão de 2026-09-23 — a Etapa 3 fechou.** Testes do `403`, do `409`, do login, da rotação e do
reuso; a função substituta corrigida; o comando `criar_admin`; e um bug achado de passagem,
reproduzido por teste e corrigido. Suíte de `12 passed` para **`22 passed`**. O que a sessão
ensinou, e não está no código:

- **No FastAPI as dependências rodam antes do `422` do corpo.** Um corpo inválido com token de
  não-admin devolveu `403`, não `422` — a ordem real é `401` → `403` → `422` → `409` (a nota da
  fase Desenhar, mais acima, foi corrigida). Consequência para teste: **a entrada precisa passar em
  todas as verificações menos a testada**, ou o resultado depende da ordem interna do servidor e o
  teste passa pelo motivo errado. Mais tarde no mesmo dia, um `"Barer"` digitado errado fez os três
  casos do `422` voltarem `401` — a mesma lição vista do outro lado.
- **O teste de reuso confere que o R2 morreu, pela interface.** A preparação deixa o R2 **vivo**
  (login → um refresh); o ato é reapresentar o R1; o conferir é `401` no R1 **e** `401` no R2. A
  primeira versão gastava o R2 na preparação, e aí a morte dele não provaria nada. Pela interface,
  não pela coluna `revogado_em`: testar comportamento, não implementação.
- **Emenda ao ADR 0011 — a função substituta repete o ciclo do `obter_sessao`.** Provado por
  experimento (plugin no scratchpad que anula só o `commit()` do `AuthService`): com a substituta
  antiga, que só fazia `yield sessao`, o teste de reuso passava **sem** o `commit()` da emenda ao
  0010 — nada desfazia o `UPDATE`. Agora ela faz `commit()` depois do `yield` e `rollback()` +
  `raise` na exceção, sem `close()`; com o `create_savepoint`, os dois agem só sobre o savepoint. O
  mesmo experimento agora falha com `200` no R2. Primeira versão do experimento anulou **todos** os
  `commit()` e passou pelo motivo errado — um teste, um motivo, vale para experimento também.
- **Contra-teste virou rotina:** depois de cada teste verde, estragar o ato (tirar o `headers=`,
  comentar a linha do reuso, trocar o e-mail repetido por um novo) e ver o teste falhar com o
  número certo. Teste que continua verde sem o ato não prova nada.
- **Teste com `pass` é verde.** Enquanto um teste não está escrito, `@pytest.mark.skip(reason=...)`;
  o `s` aparece em toda rodada.
- **`criar_admin` — três decisões (nota, não ADR):** módulo Python em `app/comandos/criar_admin.py`,
  rodado com `uv run python -m app.comandos.criar_admin` (o `-m` garante que o `app/__init__.py`
  roda e carrega o `.env`); nome, e-mail e senha por `ADMIN_NOME`/`ADMIN_EMAIL`/`ADMIN_SENHA`,
  obrigatórias; e **falhar alto** na segunda execução — stderr e `sys.exit(1)`. Duas funções:
  `criar_admin(sessao, nome, email, senha)` é a lógica, testável com a sessão da fixture, e
  delega ao `UsuarioService` (o `Depends` do `__init__` é só valor padrão; fora do FastAPI basta
  `UsuarioService(sessao)`); `main()` é a casca que toca o mundo. O comando é **ponto de entrada**
  com a própria unidade de trabalho — `with FabricaDeSessao() as sessao, sessao.begin():` — não
  uma camada chamando `commit()`. O `try` fica **em volta** do `with`, para a exceção atravessar o
  `begin()` (rollback) antes de ser tratada; o `id` é lido dentro do bloco (depois do `close()` o
  objeto está desligado da sessão) e impresso fora (só depois do `commit()` é verdade que existe).
- **Bug achado rodando o comando: admin com nome, e-mail e senha vazios.** As três chaves estavam
  no `.env` sem valor — `os.environ[...]` protege contra chave ausente, não contra chave vazia (o
  limite registrado em 2026-09-10, visto acontecer pela primeira vez). E o furo não era do comando:
  `POST /usuarios` também aceitava. Correção **no schema**, a porta comum às duas entradas:
  `nome_usuario: str = Field(min_length=1)`, `email_usuario: EmailStr` (dependência nova,
  `email-validator` — o Pydantic a chama por baixo, sem `import` no projeto), `senha:
  str = Field(min_length=8)` (piso do NIST). Teste primeiro, com `@pytest.mark.parametrize` — um
  campo estragado por rodada, o resto válido; foi ele que apontou o `nome_usuario` esquecido na
  primeira versão do schema. Banco de desenvolvimento limpo à mão; `ADMIN_SENHA` fica comentada no
  `.env` depois de usada — ausente, ela falha na primeira linha com `KeyError`; vazia, só no schema.
- **Uma sequência do Postgres nunca volta atrás**, nem com `rollback`: o admin nasceu com `id=5`
  porque tentativas anteriores gastaram 3 e 4. Buraco na numeração não é sinal de erro.
- Miudezas: argumento **posicional** preenche parâmetros na ordem da assinatura — com vários `str`
  seguidos, nomeados (`email=...`); `for` sobre uma `str` percorre letras; `resposta = corpo[campo]
  = valor` é atribuição encadeada; `with` é gerenciador de contexto (entrada, bloco, saída
  garantida — a mesma ideia do `yield` da fixture); `pytest.raises` engole só o tipo pedido e deve
  envolver só a chamada que deve falhar; código de saída `0` = sucesso, `≠ 0` = falha, e
  `$LASTEXITCODE` o mostra no PowerShell; `MAIÚSCULAS` é para constante de módulo, não variável
  local.

**Próximo passo: a fase Decidir da Etapa 4.** O critério de pronto tem agora duas partes: o teste
de concorrência (duas requisições simultâneas para o mesmo recurso e horário → exatamente um `201` e
um `409`) e o de IDOR herdado da Etapa 3. Decisões que a fase precisa abrir, antes de qualquer
código: como o teste de concorrência roda de verdade (a exceção nomeada no ADR 0011 — transação
real, `TRUNCATE` depois, marcador próprio do `pytest`); como traduzir a violação da `EXCLUDE` em
`409` distinguindo **qual** constraint falhou (a dívida de `criar`/`atualizar` da Etapa 2); a
máquina de estados da reserva; e `403` × `404` para a reserva de outra pessoa (o mercado tende ao
`404`, para não revelar que existe). Backlog pequeno: `str_strip_whitespace` para o nome feito só de
espaços; `httpx2` no lugar de `httpx`.

**Backlog da comparação com o mercado ao fechar a Etapa 3 (2026-09-23)** — nenhum é v1; ficam
registrados para decisão futura:

- **Limite de tentativas no `/auth/login`** (*rate limiting*) — o furo mais concreto: nada impede
  mil tentativas de senha por minuto, e o Argon2, caro de propósito, vira também vetor de negação
  de serviço. O mercado limita por IP e por conta, com bloqueio progressivo.
- **Mínimo de senha: 8 × 15.** O `min_length=8` saiu da revisão de 2017 do NIST SP 800-63B; a
  revisão 4 (2025) exige **15** quando a senha é o único fator — o caso do Reservare — e 8 só com
  segundo fator. Pede também recusar senhas de listas vazadas, e desaconselha regras de composição
  e troca periódica forçada. Mudar para 15 exige trocar `"senha456"` nos testes e a senha do admin
  de desenvolvimento.
- **Padrão BFF com cookie `httpOnly`** — a recomendação atual do IETF para aplicações de navegador
  (*OAuth 2.0 for Browser-Based Applications*); já previsto como evolução no ADR 0013. Rever na
  Etapa 7.

Subir o Docker Desktop antes de começar (`docker compose up -d db` da raiz, esperar `(healthy)` no
`docker compose ps`); `uv run pytest` de dentro de `backend/` deve dar `22 passed` antes de mexer em
qualquer coisa. Sem o banco no ar o `pytest` **pendura** em vez de falhar.

> Atualize esta seção ao fechar cada etapa. O README tem a tabela de status
> completa e não deve listar nada como pronto antes de estar funcionando.

## Stack decidida

Python 3.14 · FastAPI · SQLAlchemy 2.0 tipado · Pydantic v2 · Alembic ·
PostgreSQL 16 · `uv` · `ruff` · `mypy` · `pwdlib` (Argon2) · `PyJWT` · pytest + httpx ·
Docker Compose · GitHub Actions · Vite + React + TypeScript + TanStack Query ·
Playwright.

As escolhas já foram decididas com critério em
[`docs/ROADMAP.md`](docs/ROADMAP.md#4-stack-e-por-quê) — não as reabra sem
motivo novo. Em particular: **não** SQLModel (funde modelo e schema), **não**
`create_all()` (Alembic), **não** SQLite (o `EXCLUDE` é o coração do projeto),
**não** Passlib (sem manutenção desde 2020).

## Convenções

- **Commits** pequenos, em português, um por sub-etapa. Commit todo dia, mesmo
  incompleto.
- **ADRs** em `docs/adr/NNNN-titulo-curto.md`, seguindo
  [`docs/adr/TEMPLATE.md`](docs/adr/TEMPLATE.md). Toda seção importa — inclusive
  "Alternativas consideradas" e "Como eu saberia que errei".
- **Camadas:** `routers/` conhece HTTP e chama `services/`; `services/` tem a
  regra e chama `repositories/`; `repositories/` conhece o banco. O domínio não
  conhece FastAPI nem SQLAlchemy. Router não contém regra de negócio.
- **Schemas Pydantic separados dos modelos** e separados por direção
  (`RecursoCriar`, `RecursoAtualizar`, `RecursoResposta`). Nunca devolver o
  modelo de tabela na resposta.
- **Nomes de módulo (decidido em 2026-09-21):** infraestrutura — o que existiria em qualquer
  projeto FastAPI — em inglês, com o nome que o ecossistema usa (`main.py`, `db.py`, `base.py`,
  `health.py`, `security.py`); domínio — o que é do Reservare — em português (`recurso.py`,
  `usuario.py`, `reserva.py`, `refresh_token.py`). Identificadores dentro de qualquer módulo são em
  português (`obter_sessao`, `criar_access_token`). `excecoes.py` é a exceção histórica; não renomear.
- **Todo timestamp em UTC.** Fuso é assunto de apresentação, não de armazenamento.
- **Intervalo semiaberto `[início, fim)`:** reserva que termina às 10h **não**
  conflita com a que começa às 10h. "Não sobrepõe" ≠ "não encosta".
- **Segredos nunca no repositório.** `.env` no `.gitignore` antes do primeiro
  commit que o criaria. Em repo público, segredo commitado é segredo
  _rotacionado_, não apagado.
- Ao fim de cada sessão de trabalho, registrar **qual é o próximo passo**.

## Comandos

Rodar de dentro de `backend/`, onde está o `pyproject.toml`:

- `uv sync` — recria o `.venv/` a partir do `uv.lock`
- `uv run uvicorn app.main:app --reload` — sobe a API local (`/health` e `/docs`)
- `uv add <pacote>` / `uv add --dev <pacote>` — produção / desenvolvimento
- `uv run ruff check .` — lint; `uv run ruff format .` — formatação
- `uv run mypy app` — verificação de tipos

Da **raiz** do repositório, porque o `pre-commit` não está no `PATH` (ele vive
em `backend/.venv/`):

- `backend/.venv/Scripts/pre-commit run --all-files` — roda os hooks à mão
- `backend/.venv/Scripts/pre-commit install` — escreve o hook em `.git/hooks/`;
  **necessário após clonar**, porque `.git/` não é versionado

Banco, da raiz. As credenciais vêm das variáveis que já existem **dentro** do container — por isso
as aspas simples, que impedem o PowerShell de expandir `$POSTGRES_USER` antes da hora:

- `docker compose up -d db` — sobe só o banco; `docker compose ps` mostra quando fica `(healthy)`.
  `Started` significa apenas que o container subiu, não que o Postgres aceita conexão
- `docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'` — psql interativo.
  Dentro dele: `\dt` lista tabelas, `\d reserva` mostra colunas, índices e constraints, `\q` sai
- `Get-Content docs/prova-invariante.sql | docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'`
  — roda um `.sql`. O `-T` é obrigatório: sem ele o `exec` tenta alocar terminal e ignora o pipe.
  Acrescentar `-v ON_ERROR_STOP=1` **só** para o esquema, onde erro significa consertar; nunca para
  a prova, onde metade dos casos deve falhar
- Plano B quando o pipe travar: `docker compose cp <arquivo>.sql db:/tmp/x.sql` e depois
  `docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /tmp/x.sql'`

O PowerShell 5.1 come aspas duplas ao chamar executável nativo, então `psql -c "SELECT ..."` numa
linha só chega truncado ao container. Use o psql interativo ou `-f`.

O Postgres também é alcançável direto do Windows em `127.0.0.1:5432`, desde que `docker compose up
-d db` esteja no ar — é assim que o Alembic conecta.

Alembic, de dentro de `backend/`. O `alembic.ini` mora lá e a ferramenta o procura no **diretório
atual**, então rodar da raiz falha:

- `uv run alembic revision --autogenerate -m "<mensagem>"` — gera a migration comparando
  `Base.metadata` com o banco. **Nunca confie no resultado sem ler.** `CREATE EXTENSION` nunca sai
  do modelo; e em tabela que **já existe** ele também cala sobre `EXCLUDE` e `CHECK` (em tabela
  nova os dois vêm junto). Confira também o **estado do banco antes de rodar**: se as tabelas já
  existirem, a diferença é nenhuma e ele gera uma migration **vazia**, sem erro nem aviso
- `uv run alembic upgrade head` — aplica; `uv run alembic downgrade base` desfaz tudo
- `uv run alembic current` — mostra em que revisão o banco está; `uv run alembic history` lista a
  cadeia
- `uv run alembic upgrade head --sql` — imprime o SQL sem conectar (modo *offline*), útil para
  revisar antes de aplicar

Testes, de dentro de `backend/`. Precisam do `db` no ar (`docker compose up -d db`, da raiz) e do
banco `reservare_test` já criado — o `conftest.py` aplica `alembic upgrade head` nele uma vez por
rodada, mas não o cria:

- `uv run pytest` — a suíte inteira; `-q` resume, `-v` lista cada teste com `PASSED`/`FAILED`
- `uv run pytest -k em_uso` — só os testes cujo nome contém o trecho; ou o caminho completo,
  `uv run pytest tests/test_recurso.py::test_remover_recurso_em_uso`
- `uv run pytest -s` — libera a saída de `print()` (sem o `-s` o pytest a engole). Para investigar;
  o `print` não commita
- O pytest só mostra valores quando o `assert` **falha** (`assert 404 == 409`) — leia esse número
  antes de qualquer outra coisa

## Git

Repositório público em `github.com/PatriciaCorreiaSI/sistema-reservare`, via SSH
com chave pessoal. Os commits usam o e-mail privado do GitHub
(`...@users.noreply.github.com`) — não altere `user.email` local.
