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
[`docs/adr/`](docs/adr/) (decisões de arquitetura),
[`docs/aprendizados.md`](docs/aprendizados.md) (glossário de conceitos, escrito pela autora).

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
- **Território novo (acordado em 2026-10-06):** para o que ela nunca fez — cookies no FastAPI,
  todo o front-end — a fase 3 não se aplica: traga o **código pronto no chat, com o conceito ao
  lado de cada trecho**; ela copia para o arquivo, roda e explica em voz alta. Adivinhar o que
  nunca se viu não ensina. A fase 3 continua valendo para o que ela já domina (teste pytest,
  service, repository, ADR), e o contra-teste continua sendo dela. Vale também para o desenho:
  em território novo, o desenho vem pronto, com o porquê — sem perguntas para ela adivinhar.

### As sete regras do projeto

1. Eu sou a arquiteta. A IA digita, explica, revisa e ensina. Não decide arquitetura.
2. Nenhuma linha entra no repositório que eu não consiga explicar em voz alta.
3. Toda decisão relevante vira ADR — escrito **antes** do código.
4. Tento sozinha antes de pedir revisão.
5. Uma etapa por vez, com o critério de pronto atendido.
6. Todo bug ganha primeiro um teste que o reproduz.
7. Ideia nova vai para o backlog, não para a v1.

## Estado atual

| Etapa | Concluída em | Decisões |
|---|---|---|
| 1 — modelagem e migrations | 2026-09-10 | ADRs 0001–0004; migration `8cf01df862a4`; `docs/prova-invariante.sql` passa |
| 0 — fundação | — | `docker compose up` sobe `db` e `api`; `/health` → `200` |
| 2 — primeira fatia vertical | 2026-09-15 | ADRs 0010–0011 |
| 3 — autenticação | 2026-09-23 | ADRs 0012–0013 |
| 4 — reservas e concorrência | 2026-10-01 | ADRs 0014–0020 (pendências em 10-02) |
| 6 — testes e CI | 2026-10-05 | ADRs 0021–0022 |
| 7 — front-end | 2026-10-21 | ADRs 0023–0027, emendas aos 0018 e 0022 |
| 8 — observabilidade e deploy | 2026-10-28 | ADRs 0028–0034, emendas aos 0010 e 0014 |
| **9 — vitrine** | **próxima** | — |

Suíte do back-end em `146 passed`; e2e em `16 passed`. O detalhe de cada etapa está no ROADMAP;
a história de cada sessão, no `git log`. Este arquivo guarda só o que **não** se deriva de lá nem
do código: decisões em vigor fora dos ADRs, compromissos sobre código que ainda não existe, e
armadilhas.

**Início de sessão:** Docker Desktop aberto e **não pausado** (pausado, o `docker compose ps`
responde `Docker Desktop is manually paused` e o `pytest` pendura); da raiz, `docker compose up -d
db` até `(healthy)`; de `backend/`, `uv run pytest` → `146 passed` (e o aviso do `httpx`, backlog)
antes de mexer em qualquer coisa; mexendo no front, também de `frontend/`, `npx playwright test`
→ `16 passed`. Para a API à mão e o front, o banco de desenvolvimento precisa do admin (`criar_admin`; `ADMIN_SENHA` vazia passa pelo `os.environ` e cai no `min_length=8`).

## Próximo passo

**Etapa 9 — vitrine** (ROADMAP): o projeto legível em dois minutos por quem nunca o viu — README
com GIF, diagrama de arquitetura e a seção "Decisões técnicas", `docs/colaboracao-ia.md`, "O que
eu faria diferente", diagrama do modelo em Mermaid, `aprendizados.md` publicado e o post sobre a
corrida de reservas. Critério de pronto: uma pessoa desconhecida entende, abre a demonstração e
roda o projeto localmente sem perguntar nada. Primeiro, ver no ROADMAP o que dela já existe.

Pendência da autora: a **segunda cópia** da chave do backup, fora deste computador.

## Produção (Etapa 8): o que o código não conta

- **Logs (0029):** o `X-Request-ID` só aparece na tela nos 5xx (`CodigoDoErro`, um `<span>` em
  bloco: `<p>` dentro de `<p>` não é HTML válido). O `500` se prova só localmente e, no e2e, por
  `page.route` + `fulfill`: a API não quebra de propósito.
- **Conexão com o Neon (0031):** `sslmode=verify-full&sslrootcert=system&channel_binding=require`
  na URL e `SSL_CERT_FILE` no `Dockerfile`, porque o OpenSSL do `psycopg-binary` não acha as raízes
  do sistema sozinho. Por isso essa URL **não conecta do Windows**: teste contra o Neon roda num
  container (`-e NEON_URL` sem valor) — e a imagem `postgres:16` também não traz `ca-certificates`.
  Render e Neon em `us-east-1`; Neon em Postgres 16 (o `pg_dump` recusa servidor mais novo que
  ele). No `render.yaml`: `plan: free` escrito (sem ele o Render cria pago), `region` imutável,
  `sync: false` só pergunta na criação do Blueprint; o `CMD` escuta a `PORT` (10000 no Render).
- **Front pela API (0028, 0034):** `app.frontend()` decide pelo `Accept` (navegação recebe o
  `index.html`; `fetch` e asset sumido, `404` em JSON). Liga pela `PASTA_DO_FRONT`, **não** pelo
  `FASTAPI_ENV` (sem o `dist/`, toda rota inexistente viraria `500`). O pytest não vê o front; a
  prova é a imagem. O `.dockerignore` protege `.env`, `node_modules` e o `.venv` do Windows.
- **Partida (0030):** `exec uvicorn` no `CMD`, sem `uv run`, para o `uvicorn` ser o PID 1 e receber
  o `SIGTERM` (saída `0`; sem `exec`, `137`). Linha no `CMD`, não `partida.sh`: o VS Code cria o
  arquivo em CRLF, e o `docker build` copia do disco antes de o `.gitattributes` agir.
- **Semeadura (0033):** a guarda liga só com `"1"` exato (`"false"` é string verdadeira); "cria o
  que faltar" pergunta antes (o `IntegrityError` abortaria a transação); o `DELETE` só alcança a
  lista fixa de e-mails; o histórico passa pelo `ReservaService` com o relógio três dias atrás
  (exemplo que a regra recusaria é demonstração que mente). Se o admin reservar em produção um
  horário de exemplo, a partida para com `HorarioOcupado`, de propósito.
- **Backup (0032):** o `backup_leitura` foi criado **por SQL** (pelo painel do Neon entraria no
  `neon_superuser`, que escreve), com `SELECT` também nas sequências (o dump guarda onde cada
  `Identity` parou) e `ALTER DEFAULT PRIVILEGES` (tabelas de migrations futuras); host sem
  `-pooler`. As contagens do Neon são lidas depois do dump: atividade no meio dá vermelho falso, e
  basta rodar de novo. A chave privada é um **arquivo**, fora do repositório e de pasta
  sincronizada, com segunda cópia fora do computador. Par só por `age-keygen -o`, nunca transcrito
  à mão: o primeiro se perdeu na área de transferência, e só o ensaio de restauração descobriu.
- **A URL do Neon nunca passa pelo chat nem por arquivo:** entra por `Read-Host` (o que se digita
  no comando vai para o histórico do PSReadLine) e sai por `Set-Clipboard` ou `-e VAR` sem valor.
  Se vazar, troca-se a senha do papel (Neon: **Reset password**, ou `ALTER ROLE`) e o destino dela:
  a `DATABASE_URL` no Render (`neondb_owner`) ou o *secret* `NEON_URL_BACKUP` (`backup_leitura`).
- **Os dois bugs de transação** que o e2e instável revelou (emendas aos 0010 e 0014). **Run verde
  com `flaky` é sintoma, não sorte.** Commit antes da resposta: o serviço recebe `sessao: Sessao`
  (`scope="function"`); o `TestClient` sozinho espera a requisição inteira e passa verde com o
  defeito, então o teste espia o `http.response.start`. Deadlock da `EXCLUDE`: o teste monta o
  círculo (A sem commit, B pela API, C pelo teste) e o fecha assim que a `pg_stat_activity` mostra
  a API esperando; o abortado é quem esperou primeiro, e a procura por círculo roda **uma vez por
  espera** (C tem até o `deadlock_timeout`, 1 s). A thread usa `raise_server_exceptions=False`,
  senão o vermelho vira `[] == [409]`.

## Front-end: o que o desenho decidiu e o código não conta

- **Visual (ADR 0027):** Tailwind v4 pelo `@tailwindcss/vite`, variáveis de design no `@theme` do
  `index.css`, `prettier-plugin-tailwindcss`. Tela nova começa num protótipo (artifact) com as
  classes que irão para o código. Layout no limite exato não conta como cabendo: a fonte de reserva
  e o zoom só do texto mudam a largura. Grade de cartões por
  `grid-cols-[repeat(auto-fill,minmax(...))]`, não por `md:`/`lg:` — o prefixo mede a janela, e a
  coluna perde 256px para a barra (`auto-fit` quando o conjunto é fixo).
- **O Tailwind não avisa:** classe errada é ignorada em silêncio (o Prettier põe as desconhecidas no
  começo da lista — sinal que falha quando a errada **já é** a primeira); valor arbitrário com
  unidade errada é gerado e o navegador descarta; borda e grade pedem duas classes (`border` +
  `border-X`, `grid` + `grid-cols-X`); `aria-invalid:` não existe (criado com `@custom-variant`);
  valor de atributo no seletor diferencia maiúscula. O Preflight zera margens (o `<dialog>` leva
  `m-auto`) e marcadores (`<ul>` sem marcador leva `role="list"`, pelo VoiceOver). Contraste AA e
  foco visível são critério, não enfeite.
- **Faixa da semana:** derivada do `?dia=`, sem parâmetro novo; dias e semanas são `<Link
  replace>` (muda a URL → link); dia passado é texto fora do Tab, com `sr-only` "(já passou)";
  "Semana anterior" nunca leva antes de hoje. A `<section>` se nomeia por `aria-label` (o `<h2>` é
  a data, que muda). A lacuna se conta como período ("livre por 8h30").
- **Foco:** abrir o cartão → `autoFocus` no "Início"; cancelar → volta ao "Reservar" da mesma
  lacuna; terminar, ou cancelar uma reserva → a tarja do aviso (`tabIndex={-1}`,
  `ref={focarAoMontar}`). A função do ref mora **fora** do componente: nova a cada desenho, o React
  a chamaria de novo e roubaria o foco; `key` nova na tarja faz o ref agir outra vez. O `Campo`
  liga rótulo, controle e erro por *render prop*; classe a mais vai depois do *spread*.
- **Ambiente do e2e** (sem ADR; o Playwright é de desenho): dentro do front (`frontend/e2e/`,
  `tsconfig.e2e.json`). O `webServer` sobe a API e o Vite em **portas próprias** (`:8001`, `:5174`,
  `reuseExistingServer: false`) e o banco **`reservare_e2e`** (criado à mão), zerado a cada rodada
  por `downgrade base` → `upgrade head`, atrás de uma **guarda** que sai com `1` se o
  `POSTGRES_DB` for outro. O alvo do proxy vem de `ALVO_DA_API` (sem `VITE_`, que exporia ao
  navegador). `... is already used` = `uvicorn` órfão: `Get-NetTCPConnection -State Listen
  -LocalPort 8001,5174` dá o PID. Usuárias no projeto de setup; **recurso novo por teste** (o
  *retry* do CI não zera o banco). Só Chromium. Job `e2e` com `needs: [backend, frontend]`.
- **Como se escreve um e2e:** prepara pela API (`e2e/api.ts`), age pela tela (`e2e/tela.ts`);
  instante da API + milissegundos, nunca hora local montada. Antes da conferência, a **condição**
  (`toHaveCount(2)`, item fora da tela) — sem ela o teste passa verde com o defeito. Um
  `toBeVisible()` antes de mexer pela API é sincronização. Botão repetido se acha pelo escopo do
  item; texto procurado é copiado da tela, nunca redigitado (localizador errado não dá erro: espera
  30 s, e o `waiting for` cita a string). Nenhum `page.goto` no meio quando o cache importa
  (recarregar zera a memória). Para ver um estado que dura milissegundos, **segurar** o pedido
  (`page.route` sem resposta); para um erro que a API não produz de propósito, responder no lugar
  dela (`rota.fulfill`). Nome de cabeçalho no `fulfill` é string: `X-Request_ID` faz o teste de
  ausência passar verde pelo motivo errado. Arquivo sem `.spec.ts` no nome é ignorado em silêncio (`npx
  playwright test --list`).
- **Como trabalhar no front:** território novo — código pronto no chat, **testado antes numa cópia
  fora do repositório** (`tsc`, ESLint, Prettier, e o e2e quando couber; para instalar pacote, a
  cópia leva `node_modules` próprio), conceito ao lado; ela digita, roda e explica. Os conceitos
  já dados estão no `docs/aprendizados.md` e no histórico: não reexplicar o básico.

## Decisões em vigor fora dos ADRs

### Ambiente e banco

- **Toda porta publicada em `127.0.0.1`**, nunca `0.0.0.0`: API em `:8000`, Postgres em `:5432`.
  O Postgres é publicado porque **o Alembic roda do host** (o `--autogenerate` escreve um arquivo
  que precisa cair no repositório). Bind mount do código adiado: cobriria o `.venv` Linux com o de
  Windows.
- **A URL do banco é derivada, não escrita:** `POSTGRES_USER`/`PASSWORD`/`DB` + **`DB_HOST`
  obrigatório** — `db` no container, `127.0.0.1` no host (**nunca `localhost`**: o Windows resolve
  para `::1`, o compose publica só IPv4, e o driver pendura). Sem fallback. O dono é
  `url_do_ambiente()` em `app/db.py` (`URL.create()` escapa a senha); o `migrations/env.py` só
  deriva se `sqlalchemy.url` vier `None` — é por onde o `conftest.py` injeta a URL de teste. No
  deploy, aceitar uma `DATABASE_URL` pronta se vier.
- **`load_dotenv` mora em `app/__init__.py`**; toda chave obrigatória é `os.environ[...]`, e o app
  falha no startup se faltar. `alembic.ini` tem `sqlalchemy.url` **comentada de propósito**. Toda
  variável nova também entra no `environment:` do `api` no `docker-compose.yml` — o container não
  vê o `.env`. Exceção: variável que descreve a própria imagem nasce no `ENV` do `Dockerfile`
  (`PASTA_DO_FRONT`, o `PATH` do `.venv`), não no compose.
- **`docs/esquema-alvo.sql` está congelado**; a verdade é a migration. **`docs/prova-invariante.sql`
  continua vivo**, rodado **sem** `ON_ERROR_STOP`.
- **Migrations:** `CREATE EXTENSION IF NOT EXISTS btree_gist` escrito à mão como primeira
  operação; o `downgrade` **não** derruba a extensão. Constraints sempre **nomeadas** (a
  `naming_convention` está em `app/models/base.py`; só a chave `ck` exige `name=`). Migration não
  aplicada é só texto (apagar e regenerar); aplicada, corrigir é outra migration.
- Driver `psycopg` 3, por não fechar a porta síncrono × assíncrono.

### Camadas, erros e regras

- **ADR 0010:** nenhuma camada chama `commit()`; repository que escreve faz `flush()`. Serviço
  recebe a sessão por `sessao: Sessao` (`app/db.py`), **nunca** `Depends(obter_sessao)` direto: o
  `Sessao` leva o `scope="function"`, que comita antes de a resposta sair (emenda de 2026-10-27). Única
  exceção: o `commit()` logo após `revogar_familia` no `AuthService`. O `criar_admin` é outro
  **ponto de entrada**, com a própria unidade de trabalho (`with FabricaDeSessao() as sessao,
  sessao.begin():`).
- **ADR 0009:** repositories usam `selectinload` explícito, para a conversão a async ser mecânica.
- **O status HTTP nasce num lugar só:** exceções de domínio em `services/excecoes.py`, traduzidas
  pelos handlers do `main.py` — `404`, `409`, `422`, `401` (sempre com `WWW-Authenticate:
  Bearer`) e `403` (sem o cabeçalho). Router sem `try` e sem `JSONResponse` de erro. Ordem real no
  FastAPI: `401` → `403` → `422` → `409` (as dependências rodam antes da validação do corpo).
- **Onde mora a validação (emenda ao ADR 0014):** regra que depende só do pedido vai no schema
  (`Field(gt=0)`, `Literal`, `model_validator`); regra que depende do gravado vai no service,
  **antes** do `flush` onde a `CHECK` dispararia — o `atualizar` de recurso aplica o patch e
  confere `hora_func_inicio >= hora_func_fim` (`HorarioDeFuncionamentoInvalido` → `422`). **A regra
  dos horários mora em dois lugares** (schema do `POST`, service do `PATCH`), com a mesma mensagem.
  No service se lança exceção de domínio; `ValueError` só dentro de validador do Pydantic.
- **`null` explícito no `PATCH`:** `X | None = None` aceita `null`, e o `exclude_unset` só descarta
  o que **não veio**. O `field_validator` `recusar_nulo[T]` do `RecursoAtualizar` lista os cinco
  campos — **campo novo no schema entra na lista**, senão volta o `500`. Funciona porque valor
  padrão não passa por validação. O contrato ainda diz `string | null` (o validador não aparece no
  OpenAPI); a sentinela `MISSING` do Pydantic corrigiria, mas ainda é experimental (backlog).
- **Validação só na entrada:** `UsuarioCriar` com `min_length=1`, `EmailStr`, senha
  `min_length=8`, `Literal["admin", "usuario"]`; `UsuarioResposta` e `UsuarioAtual` não repetem.
- **`UsuarioAtual` mora em `dependencies.py`** (nunca viaja em JSON). `obter_usuario_atual`
  (`401`) → `exigir_admin` (`403`). Guarda que não entrega valor vai no decorador; quando o
  handler usa quem chamou, vai como parâmetro. **Autorização pergunta sobre quem chama (o token),
  nunca sobre o corpo.** Leitura de `/recursos` para quem está logada, escrita só admin (ADR 0020).
  A extração do token mora só em `obter_usuario_atual` (ADR 0013), para a troca de transporte ser
  localizada.
- **JWT:** PyJWT, `HS256`, `JWT_SEGREDO` obrigatória e validada por `validar_segredo()` (32+ bytes,
  `len(segredo.encode())`, chamada na importação). `sub` é **`str`** (PyJWT ≥ 2.10 recusa
  numérico); `algorithms=[...]` obrigatório na decodificação. Access de 15 minutos
  (`ACCESS_MINUTOS`), refresh de 7 dias (`REFRESH_DIAS`).
- **Refresh em SHA-256, senha em Argon2** — o SHA-256 é determinístico e serve de chave de busca;
  senha nunca se busca por hash (`hasher.verify`). `buscar_por_hash` devolve também revogados e
  expirados, de propósito: a detecção de reuso precisa vê-los.
- **Refresh em cookie (ADR 0023):** o service devolve `ParDeTokens` (`dataclass` em
  `services/auth.py`; em `schemas/` viraria tipo TypeScript) e recebe o refresh como `str | None`;
  o router grava o cookie e devolve só o access. `COOKIE_REFRESH` e `CAMINHO_DO_COOKIE` são
  constantes do router: o `delete_cookie` só apaga com o **mesmo `path`** do `set_cookie`.
  `Cookie(default=None, alias=...)`: ausente não é `422`; refresh → `401`, logout → `204`.
- **Prefixo `/api` (ADR 0024):** um `APIRouter(prefix="/api")` pai no `main.py` inclui os quatro
  routers; `/health`, `/docs` e `/openapi.json` ficam na raiz. Origem inclui a porta (o que o CORS
  olha); site ignora porta (o que o `SameSite` olha).
- **Fuso (ADR 0018 e emenda):** `obter_fuso()` em `dependencies.py` devolve o `ZoneInfo` de
  `FUSO_FUNCIONAMENTO`, injetado como o `obter_agora`; a regra mora em `cabe_no_horario(inicio,
  fim, recurso, fuso)`, função pura. O router de recurso compõe `RecursoResposta` em
  `_resposta(recurso, fuso)` — o schema não lê ambiente, o modelo não tem a coluna. O
  `AuthService` lê `datetime.now(UTC)` direto, não o `obter_agora` (teste de refresh vencido usa
  um instante real no passado, 2020).
- **`criar_admin`** (`app/comandos/criar_admin.py`): **falha alto** na segunda execução (stderr +
  `sys.exit(1)`); `criar_admin()` é a lógica testável, `main()` a casca. Depois de usada,
  `ADMIN_SENHA` fica comentada no `.env`.
- **`FastAPI(title="Reservare")`**: o título vai para o contrato, o `/docs` e o cabeçalho do
  `tipos.ts`.

### Código da Etapa 4 que não se lê de primeira

- **`criar`**: recurso primeiro (`404`, depois `409` inativo), então as três regras de `422`
  (passado, `cabe_no_horario`, `convidados > ocupacao`), filhas de `RegraDeReservaViolada`, com
  **um handler só**. A sobreposição não é checada no Python: o repository traduz a `EXCLUDE` por
  constantes (`SEM_SOBREPOSICAO`, `FK_RECURSO`); o resto sobe (`500`).
- **`listar`**: o service decide o filtro (admin → `None`; usuária → o `id` do token); ordena por
  `id_reserva` (paginação estável). `limite` em `Query(20, ge=1, le=100)`, `deslocamento` em
  `Query(0, ge=0)`.
- **`cancelar`**: ler → `garantir_acesso` (`404`) → `update()` condicional do ADR 0016 →
  `rowcount == 1`, senão `ReservaNaoCancelavel` (`409`). O `synchronize_session` padrão atualiza o
  objeto lido antes.
- **`disponibilidade`** mora no `ReservaService` (ADR 0019), mas a rota fica em
  `routers/recurso.py`: o router é escolhido pela **URL**, o service pela **regra**.
  `listar_ativas_na_janela` filtra por `cancelada_em.is_(None)`, **o mesmo predicado do `where=` da
  `EXCLUDE`**. `calcular_lacunas` **assume `ocupados` ordenado por início** (o `order_by` do
  repository é parte do contrato). Dia no passado → `200` vazio sem consultar o banco.
- **Fato central da Etapa 4:** quando a transação 2 insere sobre uma linha que a 1 fez `flush` mas
  não comitou, o Postgres **não recusa — espera**. `commit` na 1 → erro da `EXCLUDE` na 2;
  `rollback` → a 2 entra. Por isso o teste de concorrência precisa de `commit` real.

### Front-end

- **TypeScript fixado em `~5.9`**: o `openapi-typescript` declara `peer typescript ^5.x`
  (`ERESOLVE`; issue `openapi-ts/openapi-typescript#2723`). Soltar quando ela fechar;
  `--legacy-peer-deps` descartado.
- **`"strict": true` nos três `tsconfig`** (desde 2026-10-21): o template do Vite não escreve a
  linha, e o 5.9 deixa o modo estrito desligado por padrão — por cinco subpassos, `null` cabia em
  qualquer tipo sem aviso. `tsconfig` novo leva a linha; `tsc --showConfig -p <arquivo>` mostra o
  que vale de fato.
- **Arquivos gerados** (`frontend/openapi.json`, `src/api/tipos.ts`) ficam fora do Prettier e do
  ESLint, dentro do `tsc`. Nunca se editam; o `pre-commit` os regenera quando `backend/app/` muda.
- **Abrir sempre `http://localhost:5173`**, nunca `127.0.0.1:5173`: o cookie é `Secure`, e só
  `localhost` é contexto seguro em `http://`. O alvo do proxy continua `127.0.0.1:8000`. Cookie
  ignora porta: o login pelo `/docs` em `localhost:8000` vale para o front.
- **O Vite responde `index.html` a toda URL que não conhece** — é o que faz o F5 numa rota do front
  funcionar. API parada = `502` do proxy (resposta, não falha de rede).
- **`createClient<paths>()` sem `baseUrl`** (as chaves de `paths` já começam com `/api`).
  `import type` é obrigatório (`verbatimModuleSyntax`). O `openapi-fetch` devolve `{ data, error,
  response }`: `data` só em 2xx. O `QueryClient` é um por app; o `Provider` o entrega por contexto.
- **Pastas do `src/` em inglês, com o nome do ecossistema** (`api/`, `pages/`, `components/`);
  arquivo de domínio e identificador em português (`pages/login.tsx`, `TelaLogin`). Hooks em
  `src/api/<módulo>.ts`, com o nome do router do back-end; tipos de entrada de
  `components["schemas"][...]`, nunca reescritos.
- **Toda `queryFn`/`mutationFn` lança quando `data` falta**: o `openapi-fetch` devolve `401`/`422`
  em `error` sem lançar, e sem o `throw` o Query trata o erro como sucesso. Quando a tela precisa
  do número, lança `ErroDaApi` (`src/api/erro.ts`, com `status`; campo declarado à parte porque o
  `erasableSyntaxOnly` proíbe *parameter properties*). Exceção: `204` não tem `data` — olhar
  `response.ok`.
- **Sessão:** o access fica numa variável do `sessao.ts`, sem `export`, lida por
  `obterAccessToken()` a cada chamada — nem `localStorage` (XSS lê) nem `useState`. O hook cuida da
  sessão, a tela navega.
- **`renovarSessao`** (`src/api/auth.ts`) é *single-flight*: o back-end trata refresh reapresentado
  como roubo e revoga a família, e duas renovações simultâneas levariam o mesmo cookie. Devolve
  `false` **só no `401`** e lança no resto ("sem sessão" ≠ "não deu para saber").
- **`renovaNo401`** (middleware registrado no `auth.ts`, não no `cliente.ts`, para não haver ciclo
  de import): copia o pedido no `onRequest` (o `fetch` consome o corpo), indexado pelo `id` do
  `openapi-fetch`; no `401`, renova e repete com `options.fetch` (sem passar pelos middlewares de
  novo); ignora `/api/auth/` (o `401` do login é senha errada; o do refresh seria laço);
  `onError` apaga a cópia.
- **Rotas:** duas rotas de layout aninhadas — `RotaProtegida` decide **se** a tela aparece (já há
  access → `<Outlet />`; senão `useQuery(["sessao"], renovarSessao)` com `retry: false` e
  `staleTime: Infinity`; `false` → `<Navigate to="/login" replace state={{ de }} />`), `Moldura`
  decide **como** (cabeçalho, `<Link>`, "Sair"). A guarda é conveniência; quem protege é o `401`.
- **Login** (`pages/login.tsx`): esquema zod com `satisfies z.ZodType<LoginEntrada>` (campo
  renomeado na API vira erro de tipo); só "obrigatório" — não inventar regra que a API não tem;
  `noValidate`. Volta à origem pelo `state` do histórico, conferido por `destinoDe(estado:
  unknown)` — no `state`, e não em `?proximo=`, para não haver redirecionamento aberto.
- **Logout** limpa no `onSettled` (mesmo com a API fora): access e `queryClient.clear()` — o cache
  inteiro, não só o `["sessao"]`. Com a API fora, o cookie sobrevive e o próximo F5 renova.
  **Login** faz `removeQueries()` no `onSuccess` (decidido em 2026-10-14): quem entra começa
  limpo, também depois de uma sessão que venceu com a tela aberta. O `renovaNo401` continua só com
  o `setQueryData(["sessao"], false)` — limpar ali exigiria contornar a guarda montada; no
  `/login` ela não está. `removeQueries`, não `clear()`: o `clear()` apagaria a mutation que roda.
- **Minhas reservas** (decidido em 2026-10-14): otimista **pela UI** (o "Cancelada" deriva do
  `isPending`; o cache não muda), porque só uma tela mostra reservas. **Uma mutation por item**,
  confirmação num `<dialog>` com `showModal()` ("Manter reserva" primeiro). No sucesso o hook avisa
  **antes** de devolver a invalidação (a tarja pega o foco enquanto o item existe; a mutation fica
  pendente até a lista nova, sem piscar); no erro, invalida sem esperar. Os avisos sobem por
  `aoAvisar`, nos callbacks **do hook** (o do `mutate()` não roda depois que o item desmonta).
  Nome e fuso do recurso pela junção com o `useRecursos`; ausente → "Recurso nº X". A tela
  pergunta `data` antes de `isError`.
- **Fuso na tela:** o do recurso (`RecursoResposta.fuso`), formatado com `Intl` (`timeZone:`), sem
  biblioteca, com a etiqueta do fuso visível; o `dia` se calcula nesse fuso. `useParams()` é
  `string | undefined` e `?dia=` chega como texto: a URL é entrada e se interpreta na borda.
- **Reservar clicando numa lacuna:** início e fim numa grade de 30 minutos (`src/grade.ts`),
  somando milissegundos aos instantes da API — nunca instante montado de hora local. A lacuna
  aberta se identifica pelo **fim** (o início da de hoje é o "agora", que muda a cada busca).
- **Tela em branco (preta no tema escuro) = erro lançado durante o desenho**: sem *error
  boundary*, o React desmonta a árvore inteira. A causa está no Console do DevTools, não na
  Network. **`npm run build` antes do navegador.**
- **O `npm run dev` não confere tipos**: código com o `tsc` vermelho roda no navegador. Quem
  confere é o editor, o `npm run build` e o CI. O `StrictMode` monta tudo duas vezes em
  desenvolvimento.

### CI e `pre-commit`

- **Dois jobs** (`backend`, `frontend`, emenda ao ADR 0022); cada um regenera o seu arquivo gerado
  e compara com `git diff --exit-code`, que só vê arquivo **rastreado**. O contra-teste estraga a
  **origem** (um schema, o `title`), não o gerado. No CI, `POSTGRES_DB=reservare_test` e
  `DB_HOST=127.0.0.1`; as migrations vêm **depois** dos testes (o `alembic check` precisa do banco
  em `head`, e quem o leva até lá é o `conftest.py`).
- **O `pre-commit` cobre os dois lados:** `ruff`, `mypy`, e hooks `local` que rodam Prettier e
  ESLint quando `frontend/` muda, e `exportar_openapi` + `gerar-tipos` quando `backend/app/` muda.
  Os dois do contrato têm o **mesmo gatilho** de propósito: o `files:` é decidido uma vez, sobre o
  que estava *staged* no início. Hook que reescreve arquivo interrompe o commit: `git add` e
  repetir.
- **`.gitattributes`** (`* text=auto eol=lf`) ganha do `core.autocrlf` e entrega LF no disco; o VS
  Code ainda cria arquivo novo em CRLF e com quatro espaços, e o hook do Prettier conserta.
- **O CI roda uma vez por push, sobre o último commit**: commit do meio de uma pilha não é
  conferido lá.
- **Tag de action nem sempre é móvel:** `setup-uv` não publica a tag curta desde a v8 (fixado em
  `@v10.2.0`). Conferir com `gh api repos/<dono>/<action>/tags`; fixar pelo hash do commit é a
  prática mais forte.
- **Runner fixado em `ubuntu-24.04`** (decidido em 2026-10-19, o dia em que o `ubuntu-latest`
  virou Ubuntu 26): o sistema do CI só muda por commit, pelo mesmo motivo da tag de action fixa.
  Migrar para o `ubuntu-26.04` quando o Playwright declarar suporte a ele (o `--with-deps`
  instala bibliotecas do sistema, e cada versão do Playwright aceita uma lista fechada de
  Ubuntus), num commit próprio, com o CI verde como prova.

## Testes

- **ADR 0011 e emendas:** banco `reservare_test`, criado à mão; o `conftest.py` aplica `upgrade
  head` uma vez por rodada; a fixture `sessao` usa `join_transaction_mode="create_savepoint"`; a
  `obter_sessao_de_teste` **repete o ciclo do `obter_sessao`** — mudar um exige mudar o outro.
  **Fixture que grava pelo modelo termina em `sessao.commit()`, nunca `flush()`**: sem ele, o
  `rollback` de uma requisição que falha desfaz a preparação junto (sintoma: `404` ao ler depois de
  um erro).
- **O teste de concorrência** (`test_reserva_concorrencia.py`, marcador `concorrencia`) comita de
  verdade e limpa com `TRUNCATE`; suas fixtures moram no próprio arquivo. A `api_com_sessao_real` é
  a terceira cópia do ciclo do `obter_sessao`. As que gravam dependem de `banco_limpo` pela
  **ordem** e devolvem o **`id`**, lido dentro do `with` (depois, `DetachedInstanceError`).
- **Como se escreve um teste:** três atos (preparar, agir, conferir); prepara pelo caminho mais
  direto (fixture grava pelo modelo) e age pela interface testada; a entrada é válida em tudo menos
  no que se testa (**um teste, um motivo para falhar**); confere comportamento, não implementação.
  Teste ainda não escrito leva `@pytest.mark.skip(reason=...)` + docstring com o esperado — nunca
  `pass` (verde) nem `raise NotImplementedError` (vermelho, reservado ao corpo da *função*
  desenhada). Dados do teste ficam no teste, nunca no `.env`.
- **O contra-teste:** depois de verde, estragar a **regra** (no service), não a preparação, de um
  jeito **plausível** (`>` → `>=`, id errado mas existente) e ver falhar com o número certo.
  `git add` antes, para o `git restore` voltar à versão certa; desfazer com `git restore`, nunca à
  mão. Teste que copia outro herda o motivo dele. **Um estrago por vez:** `git diff` antes de cada
  contra-teste mostra só o dele — um estrago esquecido faz o seguinte derrubar "um teste a mais".
  Teste a peça **e** quem a usa: testar `demonstracao_ligada()` não prova que o `main` a chama.
- **Variável de ambiente no teste:** `monkeypatch.setenv`/`delenv(..., raising=False)`; ele
  restaura o valor anterior no fim (não apaga). Teste sem `assert` vale: exceção que escapa é
  `FAILED` (o do `main` apaga as `ADMIN_*` e só chama; sem a guarda, `KeyError` antes da sessão).
- **Teste pela API:** o teste é o cliente — manda **dicionário** em `json=` (instantes ISO 8601
  com fuso, `None` para `null`) e lê `resposta.json()`. Parâmetro de URL vai em `params=`. No
  `POST`, o corpo de referência é o do teste do `201` (copiar de um teste de erro traz o defeito
  junto, e o sintoma é `422` onde se esperava `404`/`409`). **Preparação pela API leva um `assert`
  do status**, só ele. **Teste de `404` confere o `detail`** (`"Not Found"` = a rota nem existe).
  Ausência de cabeçalho: `not in resposta.headers`. Lista se confere por `id in [...]`. Instante
  por `datetime.fromisoformat(...) == datetime(..., tzinfo=UTC)`, nunca pela string.
- **Cookies no teste:** os `TestClient` usam `base_url="https://testserver/api"` (o pote do `httpx`
  não envia cookie `Secure` em `http://`; o `test_health` usa a URL absoluta). O pote manda e
  substitui o cookie sozinho; `usar_refresh(client, valor)` faz `cookies.clear()` + `set()` para
  reapresentar um valor (o atacante com a cópia). `Max-Age=0` apaga do pote.
- **Fixtures:** `AGORA` = 1/10 12h UTC; `recurso_criado` (dicionário, `["campo"]`, vem da API)
  funciona 8h–18h local = **11h–21h UTC**; `reserva_da_ana` (objeto, `.campo`, gravada pelo
  modelo) = 2/10, 13h–14h UTC. `agora_fixo` e `fuso_fixo` são `autouse` em `test_reserva.py`
  porque as dependências rodam antes da validação. Trocar o relógio dentro de um teste: só a
  atribuição no `dependency_overrides`.
- **`ERROR` ≠ `FAILED`:** `ERROR` é a preparação que quebrou (o teste nem rodou); `FAILED` é o ato.
  `ruff check` **antes** de dar o teste por pronto (um `"Bearer {token}"` sem o `f` deixou um teste
  verde sem mandar o token). O `mypy` roda em `app`, não em `tests`: prefira argumento nomeado.
  Os `401` de `test_recurso.py` saem no `HTTPBearer` (pedido sem token); quem prova assinatura e
  `exp` são os testes de access em `test_auth.py`. `test_reserva_repository.py` é o único que
  chama um repository direto.

## Armadilhas que as ferramentas não pegam

`ruff` e `mypy` leem; nenhum dos dois executa. A verificação que falta é importar
(`uv run python -c "from app.x import Y"`) e, para router novo,
`uv run python -c "from app.routers.X import router; [print(r.path) for r in router.routes]"`.

- **Erro dentro de string** não tem quem verifique: status `"arivo"`, `prefix` sem a barra,
  `"Barer"`, nome de campo do JSON, nome de constraint, URL com `{...}` sem o `f`, `"null"` em vez
  de `None`. Só o teste, o banco ou quem lê a saída.
- **Expressão solta não faz nada:** exceção sem `raise`, `Classe.campo == x` fora do `where`,
  chamada sem guardar o retorno, `consulta.where(...)` sem reatribuir (o `select` é imutável),
  comparação guardada numa variável em vez de `assert` (o `F841` é o defeito).
- **Classe × objeto:** `Classe.campo` dentro de `where` pergunta ao banco; num `if`, comparar o
  campo da classe é sempre falso. `Coluna == lista` não é `IN` (é `.in_(...)`); `scalar` devolve um
  valor, `scalars(...).all()` a lista; função sem `()` é a própria função (`url.drivername` →
  `AttributeError`). Nenhum dos três o `mypy` pega.
- **`return 0` não é código de saída:** o Python sai com `0` ao terminar, `1` com exceção não
  pegada, `n` com `sys.exit(n)`.
- **`mypy` e o SQLAlchemy:** `IntegrityError.orig` é `BaseException | None` (`.diag` só depois de
  `isinstance(erro.orig, psycopg.Error)`); o `rowcount` só existe no `CursorResult`. Função sem
  anotação não é conferida: o verde do `mypy` não prova nada nela.
- **Parâmetro de handler sem `Depends`:** um `BaseModel` sem `= Depends(...)` vira **corpo JSON**
  (rota sem `401` e com `422`). No `/docs`, rota protegida tem cadeado e GET não tem
  `requestBody`. `prefix` do `APIRouter` se soma à rota.
- **Exceção de domínio sem handler:** o `TestClient` **relança** a exceção no teste (aparece o
  nome em vez de um número); em produção seria `500`. Para ver o `500` de propósito:
  `TestClient(..., raise_server_exceptions=False)` (a `client_sem_relancar` do `test_logs.py`).
- **O Alembic reconfigura o log do processo:** o `fileConfig` do `migrations/env.py` troca os
  handlers da raiz pelos do `alembic.ini`. Em produção não importa (a migration é outro processo,
  ADR 0030); no pytest, o `conftest.py` migra no mesmo processo e apaga o handler JSON — teste de
  log chama `configurar_logs()` antes (ela limpa e repõe; chamar de novo não duplica).
- **`**kwargs` esconde nome errado:** `JsonFormatter(reservrd_attrs=...)` passa no `mypy` e só
  falha ao importar. Mesma cura: `uv run python -c "import app.main"`.
- **Log:** nunca `logging.py` como nome de módulo; campos do JSON em inglês (`level` é o que o
  Render lê); o handler do `500` não loga — o `ServerErrorMiddleware` relança e o `uvicorn`
  registra o traceback com o `request_id`. `contextvar` mudada em teste volta com `reset(token)`.
- **`env:` do GitHub Actions não expande `$VAR`** (o Compose expande): no CI, o valor vai escrito.
- **Schema copiado para um segundo módulo** vira **outro tipo** (tipagem nominal). Um schema mora
  num módulo só.
- **O Pydantic ignora chave desconhecida em silêncio:** `PATCH` com nome de campo errado responde
  `200` sem mudar nada.
- **Restrição nova num schema muda o contrato** (`gt=0` → `exclusiveMinimum`, `Literal` → `enum`);
  o `pre-commit` regenera, e os gerados vão no mesmo commit.
- **Nome que resolve para outra coisa:** nome local que some faz o Python achar a fixture ou função
  de mesmo nome; no front, `location` esconderia o `window.location` (usar `local`). Renomear com
  `F2`.
- **Import que você não digitou:** o VS Code auto-importa o primeiro módulo homônimo (`from
  backend.app...`, `from xmlrpc import client`), mesmo com `autoImportCompletions` desligado.
  Sintoma: `ModuleNotFoundError: No module named 'backend'` ou `F811`. Fixture do `conftest.py`
  nunca se importa. Conferir o topo do arquivo no `git diff`.
- **Ciclo de import no front** às vezes funciona e às vezes entrega `undefined`: a seta entre
  módulos vai num sentido só.
- **`fabrica()` × `fabrica.begin()`:** a mistura com `sessao.begin()` dá `InvalidRequestError`.
- **Thread engole o que acontece nela:** o resultado vai numa lista que o teste lê; `join(timeout)`
  não falha ao vencer o prazo (quem diz é `is_alive()`); o valor do `for` precisa chegar ao `args`.
- **Traceback:** a linha que importa é a do arquivo do projeto e a que começa com `E`.
  `ERROR collecting` = o arquivo nem carregou.
- **`F401` pode ser o defeito** (import sem o `include_router`). Não rodar `ruff check --fix` em
  arquivo pela metade.
- **`os.environ[...]` protege contra chave ausente, não contra chave vazia.**
- **Sem o banco no ar, o `pytest` pendura** em vez de falhar: `docker compose ps` primeiro.
- **`autogenerate`:** tabela já existente → migration **vazia**, sem aviso; em tabela existente é
  cego para `EXCLUDE` e `CHECK`; `CREATE EXTENSION` nunca sai do modelo; sem `comment=` ele apaga o
  `COMMENT ON COLUMN`; modelo fora do `app/models/__init__.py` não entra no `Base.metadata`.
- **`mapped_column`:** a anotação dá o `NOT NULL` (`X | None` permite nulo); o argumento descreve o
  tipo no banco e ganha. `__table_args__` com um item precisa da vírgula final.
- `str(URL)` mascara a senha; `docker compose config` imprime a senha em texto puro. **Sequência do
  Postgres nunca volta atrás** — buraco em `id` não é erro.
- **Commit que já subiu não se reescreve** — nem `amend`, nem `reset`: dá `non-fast-forward` no
  push. Corrige-se com um commit **por cima**; `amend` e `reset --soft` são para o que não saiu da
  máquina. `git reset --hard` descarta tudo o que não foi commitado: `git status` antes, sempre.
- **No workflow, os `with:` das actions não respeitam `defaults.run.working-directory`**
  (`node-version-file` e `cache-dependency-path` levam `frontend/` na frente).
- **PowerShell não tem `head`** (`Select-Object -First 40`). O `npm` recusa conflito de *peer
  dependency* (`ERESOLVE`): é erro, não aviso.
- **O pipe do PowerShell 5.1 para executável nativo põe BOM no começo** (`set: not found` com um
  caractere invisível na frente, `unknown identity type`): passar por arquivo, ou
  `[Console]::InputEncoding` e `$OutputEncoding` em UTF-8 sem BOM antes do pipe.
- **Em tabela Markdown, todo `|` separa coluna**, mesmo dentro de *backticks*: escapar com `\|`.

## Backlog (regra 7 — nenhum é v1)

- **Segurança:** limite de tentativas no `/auth/login` (o Argon2 caro vira negação de serviço);
  login em tempo constante (hash falso quando o e-mail não existe); senha mínima de 15 (NIST
  SP 800-63B rev. 4; muda `"senha456"` nos testes); padrão BFF (IETF); janela de tolerância no
  reuso do refresh (duas abas com F5 revogam a família; muda o ADR 0023).
- **Testes:** mutação (`mutmut`); propriedades (`Hypothesis`, para `calcular_lacunas` e
  `cabe_no_horario`); concorrência direto no banco, sem HTTP (ADR 0015); e2e no Firefox e no
  WebKit (o Safari não passa por botões com o Tab por padrão); e2e da imagem Docker da API;
  testes de componente e verificação automática de acessibilidade (axe).
- **Contrato:** chave desconhecida vira `422` (`extra="forbid"`); sentinela `MISSING` no
  `RecursoAtualizar` quando sair do experimental; junção no servidor (nome e fuso do recurso no
  `ReservaResposta`); minhas reservas além de 100 (a API ordena por `id` crescente e corta as mais
  novas: pede ordenação decrescente ou filtro por status).
- **Telas:** admin de recursos; paginar recursos (`?pagina=`, hoje o 101º some); dados antes do
  erro em `recursos.tsx` e `recurso.tsx` (regra 6 quando reproduzido); nome acessível com contexto
  nos botões repetidos (`sr-only`, como o GOV.UK); *error boundary*; encerrar a reserva mais cedo
  (ADR 0016).
- **Observabilidade:** OpenTelemetry (`traceparent`), se um dia houver mais de um serviço (ADR 0029).
- `str_strip_whitespace` para nome só de espaços; `httpx2` no lugar de `httpx`.

> Atualize "Estado atual" e "Próximo passo" ao fechar cada etapa. O README tem a tabela de status
> completa e não deve listar nada como pronto antes de estar funcionando.

## Stack decidida

Python 3.14 · FastAPI · SQLAlchemy 2.0 tipado · Pydantic v2 (+ `email-validator`) · Alembic ·
PostgreSQL 16 · `uv` · `ruff` · `mypy` · `pwdlib` (Argon2) · `PyJWT` · pytest + httpx ·
Docker Compose · GitHub Actions · Vite + React + TypeScript + TanStack Query + React Router v8
(declarativo) · Tailwind CSS v4 · `openapi-typescript` + `openapi-fetch` · Playwright.

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
  "Alternativas consideradas" e "Como eu saberia que errei". Alternativa se descarta por um custo
  **da opção**, nunca por "exigiria estudar mais" (decidido em 2026-10-22).
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
- `uv run python -m app.comandos.criar_admin` — cria o primeiro admin a partir de `ADMIN_NOME`,
  `ADMIN_EMAIL` e `ADMIN_SENHA` do `.env`; sai com código `1` se o e-mail já existir
- `uv run python -m app.comandos.exportar_openapi` — grava `app.openapi()` em
  `frontend/openapi.json` (JSON com `indent=2`, UTF-8, LF); importa o app, logo precisa do `.env`

Front, de dentro de `frontend/` (Node 24, versão em `.nvmrc`):

- `npm install` — instala o `package-lock.json`; `npm ci` é a forma do CI, que recusa lock
  desatualizado. `npm install -D <pacote>` é o `uv add --dev`
- `npm run dev` — sobe o Vite em `http://localhost:5173`, com o proxy de `/api` para a API, que
  precisa estar no ar (`uvicorn`, em outro terminal)
- `npm run lint` — ESLint; `npm run format` — Prettier reescreve; `npm run format:check` — só
  confere (o do CI)
- `npm run build` — `tsc -b && vite build`: tipos e empacotamento em `dist/` (ignorado)
- `npm run gerar-tipos` — `openapi-typescript openapi.json -o src/api/tipos.ts`; rodar depois do
  `exportar_openapi`

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
  `Base.metadata` com o banco. **Nunca confie no resultado sem ler** (ver as armadilhas do
  `autogenerate`)
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
