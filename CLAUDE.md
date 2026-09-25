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

### As sete regras do projeto

1. Eu sou a arquiteta. A IA digita, explica, revisa e ensina. Não decide arquitetura.
2. Nenhuma linha entra no repositório que eu não consiga explicar em voz alta.
3. Toda decisão relevante vira ADR — escrito **antes** do código.
4. Tento sozinha antes de pedir revisão.
5. Uma etapa por vez, com o critério de pronto atendido.
6. Todo bug ganha primeiro um teste que o reproduz.
7. Ideia nova vai para o backlog, não para a v1.

## Estado atual

- **Etapa 1 (modelagem): concluída** — `docs/modelo.md`, ADRs 0001–0004.
- **Etapa 0 (fundação): concluída** — `docker compose up` sobe `db` e `api`; `/health` responde `200`.
- **Etapa 1 (migrations): concluída em 2026-09-10** — a migration `8cf01df862a4` cria o esquema do
  zero e `docs/prova-invariante.sql` passa nos sete casos contra o banco que o Alembic construiu.
- **Etapa 2 (primeira fatia vertical): concluída em 2026-09-15** — CRUD de `recurso` em camadas e o
  primeiro `pytest`, isolado por transação (ADRs 0010 e 0011).
- **Etapa 3 (autenticação e autorização): concluída em 2026-09-23** — ADRs 0012 e 0013, emendas aos
  0010 e 0011; sete rotas, o comando `criar_admin`, suíte em `22 passed`. A metade IDOR do critério
  de pronto **passou para a Etapa 4**: é critério das rotas de `reserva`, que ainda não existem.
- **Etapa 4 (reservas, concorrência e estados): em andamento** — fase Decidir fechada em
  2026-09-24 (ADRs 0014–0017); fase Desenhar fechada em 2026-09-25 (ADR 0018, esqueleto, 37
  testes com `skip`); fase Tentar em andamento — as três funções puras prontas em 2026-09-25.

O detalhe de cada etapa está no ROADMAP; a história de cada sessão, no `git log`. Esta seção guarda
só o que **não** é derivável de lá nem do código: decisões em vigor que não viraram ADR,
compromissos sobre código que ainda não existe, e armadilhas.

### Decisões em vigor fora dos ADRs

**Ambiente e banco**

- **Toda porta publicada em `127.0.0.1`**, nunca `0.0.0.0`: API em `:8000`, Postgres em `:5432`. O
  Postgres é publicado porque **o Alembic roda do host** — o `--autogenerate` escreve um arquivo que
  precisa cair no repositório para ser revisado. Rever se o bind mount do código entrar no
  compose (adiado: montar `backend/` sobre `/app` cobriria o `.venv` Linux com o de Windows).
- **A URL do banco é derivada, não escrita:** `POSTGRES_USER`/`PASSWORD`/`DB` + **`DB_HOST`
  obrigatório** — `db` no container, `127.0.0.1` no host (**nunca `localhost`**: o Windows resolve
  para `::1` primeiro, o compose publica só IPv4, e o driver pendura em vez de falhar). Sem
  fallback: um padrão silencioso no fim da cadeia é o que torna fallback perigoso. O dono é
  `url_do_ambiente()` em `app/db.py` (`URL.create()` escapa a senha); o `migrations/env.py` a
  importa e só deriva se `sqlalchemy.url` vier `None` — é por onde o `conftest.py` injeta a URL de
  teste. No deploy, aceitar uma `DATABASE_URL` pronta se vier, senão montar dos pedaços.
- **`load_dotenv` mora em `app/__init__.py`**, que roda antes de qualquer `app.x`; toda chave
  obrigatória é `os.environ[...]`, e o app falha no startup se faltar. `alembic.ini` tem
  `sqlalchemy.url` **comentada de propósito** (placeholder num repo público é convite a colar a URL
  real).
- **`docs/esquema-alvo.sql` está congelado** como registro histórico; a verdade é a migration.
  **`docs/prova-invariante.sql` continua vivo** — é o teste de aceitação da Etapa 1, rodado **sem**
  `ON_ERROR_STOP`.
- **Migrations:** `CREATE EXTENSION IF NOT EXISTS btree_gist` é escrito à mão como primeira
  operação; o `downgrade` **não** derruba a extensão (o `IF NOT EXISTS` admite que ela pode ser
  anterior — desfazer o que talvez não fizemos é o erro). Constraints sempre **nomeadas**; a
  `naming_convention` está em `app/models/base.py`, e só a chave `ck` reescreve nome explícito e
  exige `name=`. Migration não aplicada é só texto (apagar e regenerar); aplicada, corrigir é outra
  migration.
- Driver `psycopg` 3 — escolhido por não fechar a porta síncrono × assíncrono.

**Camadas, erros e transação**

- **ADR 0010:** nenhuma camada chama `commit()`; todo repository que escreve faz `flush()`. Única
  exceção nomeada: o `commit()` logo após `revogar_familia` no `AuthService`. O comando
  `criar_admin` não é exceção — é outro **ponto de entrada**, com a própria unidade de trabalho
  (`with FabricaDeSessao() as sessao, sessao.begin():`).
- **Compromisso do ADR 0009:** repositories usam `selectinload` explícito, para a conversão futura
  a async ser mecânica.
- **Compromissos do ADR 0013:** o token fica só em memória no frontend (Etapa 7), e a extração do
  token está concentrada numa dependência só (`obter_usuario_atual`), para a troca de transporte
  ser localizada.
- **O status HTTP nasce num lugar só:** exceções de domínio em `services/excecoes.py`, traduzidas
  pelos handlers do `main.py` — `404`, `409`, `401` (sempre com `WWW-Authenticate: Bearer`, RFC
  7235/9110) e `403` (sem o cabeçalho). Router sem `try` e sem `JSONResponse` de erro.
- **Ordem real das verificações no FastAPI:** `401` → `403` → `422` → `409` — as dependências rodam
  antes de o erro de validação do corpo ser levantado.
- **Fuso injetado (ADR 0018):** `obter_fuso()` em `dependencies.py` devolve o `ZoneInfo` de
  `FUSO_FUNCIONAMENTO`, e o `ReservaService` o recebe por `Depends`, como o `obter_agora`; a regra
  mora em `cabe_no_horario(inicio, fim, recurso, fuso)`, função pura. Em `test_reserva.py`,
  `agora_fixo` e `fuso_fixo` são `autouse` porque as dependências rodam antes da validação do
  corpo: até o teste de `422` do schema constrói o service. Toda variável nova que o app lê
  entra também no `environment:` do `api` no `docker-compose.yml` — o container não vê o `.env`
  (o `JWT_SEGREDO` faltou lá da Etapa 3 até 2026-09-25).
- **Dívida da Etapa 2:** `criar` e `atualizar` de recurso deixam `IntegrityError` subir → `500`
  (o `TestClient` o mostra como traceback). A Etapa 4 paga pelo ADR 0014: tradução pelo nome da
  constraint, no repository, e `CHECK` que dispara é validação faltando no schema.
- **Validação só na entrada:** `UsuarioCriar` leva `nome_usuario` com `min_length=1`, `EmailStr`
  (exige `email-validator`) e `senha` com `min_length=8`, e `privilegio_usuario:
  Literal["admin", "usuario"]`. `UsuarioResposta` e `UsuarioAtual` não repetem — o que sai do banco
  já foi validado, e o JWT é guardado pela assinatura.
- **`UsuarioAtual` mora em `dependencies.py`**, não em `schemas/`: nunca viaja em JSON.
  `obter_usuario_atual` (`401`) → `exigir_admin` (`403`). Guarda que não entrega valor vai no
  decorador (`dependencies=[Depends(exigir_admin)]`); quando o handler usa quem chamou, vai como
  parâmetro — será o caso de `POST /reservas`. **Autorização pergunta sobre quem chama (o token),
  nunca sobre o corpo.**
- **JWT:** PyJWT, `HS256`, `JWT_SEGREDO` obrigatória. Payload `sub` (**`str`** — PyJWT ≥ 2.10
  recusa numérico), `exp`, `privilegio_usuario`. `algorithms=[...]` obrigatório na decodificação
  (defesa contra `alg: none`). `decodificar_access_token` não captura nada; quem traduz é a
  dependência.
- **Refresh em SHA-256, senha em Argon2** — o SHA-256 é determinístico e serve de chave de busca;
  o Argon2 tem salt, então senha nunca se busca por hash (`hasher.verify`). `buscar_por_hash`
  devolve também revogados e expirados, de propósito: a detecção de reuso precisa vê-los; "válido"
  é regra do service.
- **`criar_admin`** (`app/comandos/criar_admin.py`): `uv run python -m app.comandos.criar_admin`,
  com `ADMIN_NOME`/`ADMIN_EMAIL`/`ADMIN_SENHA` obrigatórias; **falha alto** na segunda execução
  (stderr + `sys.exit(1)`). `criar_admin()` é a lógica testável, que delega ao `UsuarioService`;
  `main()` é a casca. O `try` fica em volta do `with`; o `id` é lido dentro do bloco e impresso
  fora. Depois de usada, `ADMIN_SENHA` fica comentada no `.env` — ausente falha na primeira linha.

**Testes**

- **ADR 0011 e emenda:** banco `reservare_test`, criado à mão (o Alembic cria tabelas, não
  bancos); o `conftest.py` aplica `upgrade head` uma vez por rodada; a fixture `sessao` usa
  `join_transaction_mode="create_savepoint"`; a função substituta (`obter_sessao_de_teste`)
  **repete o ciclo do `obter_sessao`** — mudar um exige mudar o outro. Exceção nomeada: o teste de
  concorrência da Etapa 4 comita de verdade, limpa com `TRUNCATE` e leva marcador próprio.
- **Fato que vira o centro da Etapa 4:** quando a transação 2 insere sobre uma linha que a 1 fez
  `flush` mas não comitou, o Postgres **não recusa — espera**. `commit` na 1 → erro da `EXCLUDE` na
  2; `rollback` na 1 → a 2 entra. Por isso o teste de concorrência precisa de `commit` real.
- **Como se escreve um teste aqui:** três atos (preparar, agir, conferir); **prepara pelo caminho
  mais direto** (fixture grava pelo modelo) e **age pela interface testada**; a entrada é válida em
  tudo menos no que se testa (**um teste, um motivo para falhar**); confere comportamento, não
  implementação; depois de verde, o **contra-teste** — estragar o ato e ver falhar com o número
  certo. Teste ainda não escrito leva `@pytest.mark.skip(reason=...)`, nunca `pass` (que é verde).
  Dados do teste ficam no teste, nunca no `.env`.

### Armadilhas que as ferramentas não pegam

`ruff` e `mypy` leem; nenhum dos dois executa. A verificação que falta é importar
(`uv run python -c "from app.x import Y"`) e, para router novo,
`uv run python -c "from app.routers.X import router; [print(r.path) for r in router.routes]"`.

- **Erro dentro de string** não tem quem verifique: status `"arivo"`, `prefix` sem a barra
  (`/authlogin`), `"Barer"`, nome de campo do JSON (`senha` × `senha_usuario_hash`), f-string sem
  `=`. Só o teste, o banco ou quem lê a saída.
- **Expressão solta não faz nada:** `CredenciaisInvalidas` sem `raise`, `Classe.campo == x` fora do
  `where`, argumento nomeado numa linha sozinho, chamada sem guardar o retorno.
- **Classe × objeto:** `Classe.campo` dentro de `where` pergunta ao banco; `objeto.campo = x` ordena
  ao objeto. Num `if`, comparar o campo da classe é sempre falso — foi o que faria todo usuário
  virar admin.
- **Nome que resolve para outra coisa:** um nome local que some faz o Python achar a fixture ou a
  função de mesmo nome no módulo (`sessao.add(usuario)` dentro da fixture `admin`). Renomear com
  `F2`, em todas as ocorrências.
- **`F401` pode ser o defeito**, não o ruído (import sem o `include_router`, sem o
  `pytest.raises`). Não rodar `ruff check --fix` em arquivo pela metade: ele apaga a pista.
- **`os.environ[...]` protege contra chave ausente, não contra chave vazia.** `load_dotenv` com
  caminho errado falha calado — o caminho vem de `__file__`.
- **Sem o banco no ar, o `pytest` pendura** em vez de falhar (sem `connect_timeout`). Primeiro
  lugar a olhar: `docker compose ps`.
- **`autogenerate`:** conferir o estado do banco antes (tabela já existente → migration **vazia**,
  sem aviso); em tabela existente é cego para `EXCLUDE` e `CHECK`; `CREATE EXTENSION` nunca sai do
  modelo; sem `comment=` ele apaga o `COMMENT ON COLUMN`; modelo que não está no
  `app/models/__init__.py` não entra no `Base.metadata`.
- **`mapped_column`:** a anotação descreve o valor Python e dá o `NOT NULL` (`X | None` permite
  nulo); o argumento descreve o tipo no banco e ganha da anotação. Cada opção no seu parêntese
  (`ondelete` no `ForeignKey`, `index=True` no `mapped_column`). `__table_args__` com um item só
  precisa da vírgula final — a vírgula faz a tupla.
- `str(URL)` mascara a senha (`render_as_string(hide_password=False)` não); `set_main_option`
  devolve `None`; `docker compose config` imprime a senha em texto puro.
- **Sequência do Postgres nunca volta atrás**, nem com `rollback` — buraco em `id` não é erro.
- Pre-commit que corrige um arquivo interrompe o commit (`MM`/`AM`): `git add` de novo e repetir.
  Rodar `ruff format` antes do `add` evita.

### Próximo passo

**A fase Tentar da Etapa 4.** O critério de pronto tem duas partes: o teste de concorrência (duas
requisições simultâneas para o mesmo recurso e horário → exatamente um `201` e um `409`) e o de IDOR
herdado da Etapa 3. As decisões estão nos ADRs 0014–0018. O esqueleto está em código, com corpos em
`raise NotImplementedError` (corpo vazio `...` o `mypy` recusa como `empty-body`): `obter_agora` e
`obter_fuso` em `dependencies.py`; as exceções novas em `excecoes.py` (os três `422` como filhas de
`RegraDeReservaViolada`, que carregam a mensagem em `detalhe` — um handler só, para a mãe);
`schemas/reserva.py`; `repositories/reserva.py` (`cancelar` devolve `bool`; sem `atualizar` nem
`remover`: reserva é histórico); e `services/reserva.py` (`status_efetivo`, `garantir_acesso` e
`cabe_no_horario` como funções puras fora da classe; `_para_resposta` monta a resposta, porque o
status efetivo e o `periodo` → `inicio`/`fim` impedem o `from_attributes`).

**Feito na fase Tentar (2026-09-25):** as três funções puras, com 13 testes em
`test_reserva_regras.py`, que rodam sem o banco — `status_efetivo` (a cancelada é conferida antes
do fim; `fim <= agora` é concluída; `assert fim is not None` estreita o `Range.upper`, que o `CHECK
formato_semiaberto` garante), `garantir_acesso` (uma condição e um `raise` só, com `reserva is None`
primeiro pelo curto-circuito) e `cabe_no_horario` (converte `inicio` e `fim` para o fuso uma vez e
tira deles a data e a hora; `mesmo_dia` resolve a meia-noite; devolve `bool` — quem levanta
`ForaDoHorario` é o `criar`). Nos testes: instantes de entrada sempre em UTC, para pegar a função
que esquece de converter; cada fronteira com a dupla "em cima" e "um minuto fora" (valor-limite).

Os demais testes esperados, com `@pendente` (o `skip`) e a docstring dizendo o que conferem:
`test_reserva.py` (API) e
`test_reserva_concorrencia.py` (marcador `concorrencia`, registrado no `pyproject.toml`). As
fixtures novas (`outra_usuaria` e `cabecalho_de` no `conftest.py`; `agora_fixo`, `fuso_fixo` e
`reserva_da_ana` no `test_reserva.py`) levam `raise NotImplementedError`: tirar o `skip` de um teste
sem escrever a fixture dá `ERROR`, não `FAILED`. As fixtures que comitam de verdade para o teste de
concorrência ainda não estão desenhadas.

**Retomar por:** os testes pela API, começando por `test_buscar_reserva_da_dona_devolve_200` — o
caminho mais curto (router → service → repository, cujo `buscar_por_id` já existe), que pede de uma
vez as peças novas: o corpo do `obter_fuso`; as fixtures `agora_fixo`, `fuso_fixo`,
`reserva_da_ana` e `cabecalho_de`; o router `routers/reserva.py` e o `include_router` no `main.py`;
e `_para_resposta` e `buscar_por_id` no service. Depois `criar`, `listar` e `cancelar`, com o que
cada teste pedir. O mesmo ciclo: tirar o `@pendente`, ver falhar, escrever, ver passar,
contra-teste. Armadilha já anunciada: após o `UPDATE`
do `cancelar`, o objeto lido antes segue com o status antigo na sessão (identity map) —
`test_cancelar_reserva_da_dona_devolve_200_cancelada` é quem pega.

Subir o Docker Desktop antes de começar (`docker compose up -d db` da raiz, esperar `(healthy)` no
`docker compose ps`); `uv run pytest` de dentro de `backend/` deve dar `35 passed, 25 skipped` (e o
aviso do `httpx`, que é backlog) antes de mexer em qualquer coisa.

**Backlog** (regra 7 — nenhum é v1):

- **Limite de tentativas no `/auth/login`** — nada impede mil tentativas por minuto, e o Argon2,
  caro de propósito, vira vetor de negação de serviço. O mercado limita por IP e por conta.
- **Mínimo de senha 8 × 15** — o `min_length=8` vem da revisão de 2017 do NIST SP 800-63B; a
  revisão 4 (2025) exige 15 quando a senha é o único fator, o caso daqui, e pede recusar senhas de
  listas vazadas. Mudar exige trocar `"senha456"` nos testes e a senha do admin de desenvolvimento.
- **Padrão BFF com cookie `httpOnly`** — recomendação atual do IETF para aplicações de navegador;
  já previsto no ADR 0013. Rever na Etapa 7.
- **Teste de concorrência determinístico, direto no banco** (ADR 0015) — duas conexões sem HTTP: a 1
  insere sem comitar, a 2 fica bloqueada, a 1 comita, a 2 recebe `23P01`. Prova a espera toda vez;
  adiado porque testa comportamento do Postgres, e o teste pela API já exercita o que é do projeto.
- **Encerrar a reserva mais cedo** (ADR 0016) — o "check-out" dos sistemas comerciais: encurta o
  `periodo` e libera só o resto do horário. Na v1, cancelar em andamento libera o período inteiro e
  a reserva usada pela metade fica como "cancelada".
- `str_strip_whitespace` para o nome feito só de espaços; `httpx2` no lugar de `httpx`
  (`uv remove httpx` + `uv add --dev httpx2`).

> Atualize esta seção ao fechar cada etapa. O README tem a tabela de status
> completa e não deve listar nada como pronto antes de estar funcionando.

## Stack decidida

Python 3.14 · FastAPI · SQLAlchemy 2.0 tipado · Pydantic v2 (+ `email-validator`) · Alembic ·
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
- `uv run python -m app.comandos.criar_admin` — cria o primeiro admin a partir de `ADMIN_NOME`,
  `ADMIN_EMAIL` e `ADMIN_SENHA` do `.env`; sai com código `1` se o e-mail já existir

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
