# 📅 Reservare — Roadmap de Estudo e Portfólio

> **Sistema de reserva de recursos compartilhados**
> Projeto-estudo para conquistar autonomia arquitetural: saber qual caminho tomar, por quê, e conseguir ler e defender cada linha do sistema.

---

## 1. O que é este documento

Este **não** é uma lista de funcionalidades. É um **currículo de engenharia de software disfarçado de projeto**.

O sistema é apenas o veículo. O objetivo real não é digitar cada caractere sozinha — é **deixar de ser dependente**: entrar numa decisão técnica sabendo quais são as opções, escolher com critério e conseguir explicar qualquer trecho do sistema para outra pessoa. O que está sendo construído é fluência em:

- modelagem de dados com garantias no próprio banco
- concorrência, transações e o que acontece quando duas pessoas clicam ao mesmo tempo
- separação de camadas e por que ela importa quando o código cresce
- estratégia de testes de verdade — não "escrevi uns testes"
- automação: container, migrations, integração contínua, deploy reprodutível

### Como ler este documento

**Leia apenas a etapa atual.** Isto é um mapa, não uma lista de leitura. Ler as dez etapas de uma vez dá a impressão de que existem quarenta conceitos difíceis pela frente — e não existem.

Conceito abstrato só vira concreto quando você **bate no problema que ele resolve**. Cada etapa foi escrita para ser lida **no momento em que você chega nela**.

### Triagem honesta: nome assustador × dificuldade real

**Nome assustador, dificuldade baixa** — uma tarde cada, e quase tudo é ferramenta, não conceito:
`uv` · `ruff` · `mypy` · Docker Compose · `/health` · Alembic (dois comandos) · Argon2 (duas funções) · paginação · GitHub Actions · log estruturado

**Dificuldade média** — exige prática, mas vira mecânico depois que a ficha cai:
separação em camadas · schemas separados dos modelos · JWT com refresh token · máquina de estados · TanStack Query

**Genuinamente difícil — e são apenas quatro:**

1. Condição de corrida e transações (Etapa 4)
2. Idempotência (bônus)
3. Estratégia de testes: decidir _o que_ testar e em qual nível (Etapa 6)
4. Fusos horários — parece bobagem e derruba profissionais experientes

---

## 2. O sistema em uma frase

> Uma equipe compartilha recursos limitados — salas, equipamentos, estações de trabalho. O Reservare permite reservá-los por uma janela de tempo, **garantindo que nunca haja conflito**.

### Por que este tema

**Tem um invariante difícil.** Um _invariante_ é uma regra que o sistema não pode violar em hipótese alguma, nem quando duas requisições chegam no mesmo milissegundo:

> **Duas reservas ativas nunca podem se sobrepor no mesmo recurso.**

Essa frase é o motor pedagógico do projeto inteiro. Ela força transações, locks, constraints de exclusão no Postgres e testes de concorrência — assuntos que um CRUD nunca obriga a encarar.

**É compreensível em três segundos** por qualquer recrutador, que passa então a avaliar a engenharia, não o domínio.

**É raro em portfólios.** Todo mundo tem app bancário e to-do list. Quase ninguém resolve sobreposição de intervalos com garantia no banco de dados.

---

## 3. Escopo da versão 1

### Dentro

**Recursos** — cadastro com capacidade de pessoas e horário de funcionamento; ativação e desativação sem apagar histórico. **Cada unidade é um recurso próprio** (Projetor 1, Projetor 2), portanto todo recurso é exclusivo no tempo.

**Reservas** — criar para uma janela `[início, fim)`; consultar disponibilidade; cancelar, com registro de quem cancelou e quando; três estados: **confirmada, concluída, cancelada**. Regras: horário de funcionamento, recurso ativo, convidados dentro da capacidade, nada no passado.

**Pessoas** — cadastro, autenticação, dois papéis: `admin` e `colaborador`.

### Fora (backlog, e resistir)

Pagamento · reserva recorrente · multi-tenant · notificação por e-mail · fluxo de aprovação · no-show · recurso com N unidades · histórico completo de eventos · fila de espera · integração com calendário

> Escopo que cresce é a causa número um de projeto de portfólio abandonado. Ideia nova vai para o backlog, não para a v1.

---

## 4. Stack e por quê

| Camada     | Escolha                       | Por que esta                                                                                                                               |
| ---------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| API        | FastAPI                       | Assíncrono, tipado, OpenAPI automático                                                                                                     |
| ORM        | SQLAlchemy 2.0 tipado         | **Não SQLModel:** ele funde modelo de tabela com schema de API, e essa fusão é o caminho mais curto para vazar hash de senha numa resposta |
| Validação  | Pydantic v2                   | Schemas de entrada e saída **separados** dos modelos                                                                                       |
| Banco      | PostgreSQL 16                 | Único com `EXCLUDE` + `tstzrange`, que é o coração do projeto. **Não comece com SQLite**                                                   |
| Migrations | Alembic                       | `create_all()` é marca de projeto de estudante                                                                                             |
| Senhas     | `pwdlib` com Argon2           | **Passlib está sem manutenção desde 2020**                                                                                                 |
| Pacotes    | `uv`                          | Substitui pip + venv; padrão de fato                                                                                                       |
| Lint       | `ruff`                        | Substitui black + flake8 + isort                                                                                                           |
| Testes     | `pytest` + `httpx`            | Contra o Postgres do próprio compose                                                                                                       |
| Container  | Docker Compose                | Ambiente reprodutível                                                                                                                      |
| CI         | GitHub Actions                | Testes verdes a cada push                                                                                                                  |
| Front      | Vite + React + **TypeScript** | TS é o esperado, e reforça o estudo paralelo                                                                                               |
| Estado     | TanStack Query                | `useEffect` + `fetch` na mão é o antipadrão mais comum                                                                                     |
| E2E        | Playwright                    | Um teste do fluxo principal                                                                                                                |

---

## 5. Como estudar com este projeto

### O problema que este método resolve

Escrever código com ajuda de IA não é o problema. O problema é quando a IA passa a tomar as **decisões** e você passa a ser quem **pede**. O sistema funciona, e você não consegue explicar por que ele é assim.

> **Quem digita é detalhe. Quem decide é tudo.**

### O protocolo das quatro fases

**Fase 1 — Decidir, antes de existir código.** Abra um ADR e responda: qual o problema, quais as opções, qual escolho, o que isso custa. Sem código, sem perguntar "como se faz". Esta fase constrói a autonomia; pulá-la invalida o resto.

**Fase 2 — Desenhar antes de implementar.** Nomes de tabelas e colunas, assinaturas de funções sem corpo, nomes de rotas. Depois, o teste que deveria passar.

**Fase 3 — Primeira tentativa sozinha.** Mesmo feia, mesmo errada. Esta fase existe para **descobrir o que você não sabe** — a descoberta mais valiosa que existe.

**Fase 4 — Revisão e ensino.** Agora use a IA, com perguntas de revisora: _"o que está frágil aqui?"_, _"que caso eu não considerei?"_, _"por que isso falha sob concorrência?"_, _"me mostre a versão profissional e explique cada diferença"_.

Reescrever depois de tentar é aprendizado. Receber pronto antes de tentar é dependência.

### Os dois testes de comprovação

**Teste da voz alta.** Nenhuma linha entra no repositório que você não consiga explicar em voz alta: o que faz, por que está aí, o que quebraria se sumisse. Se não consegue: estudar até conseguir, ou apagar.

**Teste do papel em branco.** Ao fim de cada etapa, feche o computador e redesenhe de memória as tabelas, o caminho de uma requisição e onde a transação abre e fecha. O que não sair é a sua lista de estudo.

### Os registros

**ADRs** em `docs/adr/` — contexto, decisão, alternativas, consequências. Em entrevista, é a prova documental de que a decisão foi sua.
**`docs/aprendizados.md`** — uma linha por conceito novo, com suas palavras.
**Commits pequenos, em português, um por sub-etapa.**

---

## 6. Como tomar uma decisão de arquitetura

### As seis perguntas

**1. Qual é a regra que não pode quebrar nunca?** Comece pelo invariante, não pela tecnologia.

**2. Quem precisa conhecer essa regra?** Regra que só existe no Python some quando alguém insere por outro caminho. Regra que só existe no banco produz erro incompreensível. Normalmente: _o banco garante, o serviço traduz, o cliente antecipa_.

**3. Quais são as duas ou três opções reais?** Decisão sem alternativa considerada não é decisão, é reflexo.

**4. Quais critérios?** Nesta ordem: correção sob concorrência → simplicidade → facilidade de testar → desempenho → flexibilidade futura. _A última é última de propósito:_ projetar para requisito imaginário é a forma mais comum de complicar sem necessidade.

**5. O que essa escolha me custa?** Toda decisão fecha portas. Escreva o custo.

**6. Como eu saberia que errei?** Defina o sinal que indicaria revisar.

### A regra estrutural: dependências apontam para dentro

> O **domínio** não conhece FastAPI, não conhece SQLAlchemy, não conhece HTTP.

`routers/` conhece HTTP e chama `services/` · `services/` tem a regra e chama `repositories/` · `repositories/` conhece o banco.

O teste: _se eu trocasse FastAPI por outro framework, quantos arquivos mexeria?_ Se for "quase todos", as camadas existem só no nome das pastas.

### Quando travar

1. Descreva o problema em português, em três frases
2. Liste os substantivos — são suas tabelas
3. Liste os verbos — são suas rotas
4. Escreva as assinaturas, **sem corpo**
5. Escreva o teste que deveria passar
6. Só então implemente

Quatro dos seis degraus não têm código. É por isso que funcionam.

---

## 7. Plano de execução — 2h/dia, segunda a sexta

10 horas por semana. O que decide o resultado não é a quantidade de horas, é **como o bloco de 2h é usado** — porque 2 horas sem alvo definido viram 20 minutos de reorientação e 40 de dispersão.

### O ritmo da semana: 4 dias construindo, 1 consolidando

| Dia                | O que acontece                                                                                                                                                        |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Segunda**        | **Decidir.** Escrever o ADR da semana, desenhar o que será feito, definir as quatro tarefas dos próximos dias. Sem código                                             |
| **Terça a quinta** | **Construir.** Uma tarefa fechável por dia, escolhida na véspera                                                                                                      |
| **Sexta**          | **Consolidar.** Fechar pontas, rodar os testes, atualizar `aprendizados.md` e o README, fazer o teste do papel em branco, planejar a semana seguinte. Sem código novo |

Sexta sem código parece desperdício de 20% do tempo. Não é: é o que impede a documentação de ser eternamente adiada — e a documentação, neste projeto, **é** metade do valor de portfólio. É também o único dia em que você olha o conjunto em vez do detalhe.

### A anatomia do bloco de 2 horas

| Minutos     | Para quê                                                                                                                                                         |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0–10**    | **Reentrada.** Ler a última anotação e o último commit. Não lute contra isso — todo bloco curto tem custo de religar o contexto; aceitá-lo torna ele mais barato |
| **10–105**  | **A tarefa única do dia.** Uma só, definida ontem                                                                                                                |
| **105–120** | **Fechamento.** Commit (mesmo incompleto) e escrever **qual é o próximo passo**                                                                                  |

Os últimos 15 minutos são os mais importantes do dia. Uma frase escrita hoje — _"parei no meio do teste de concorrência; falta fazer as duas requisições dispararem juntas"_ — transforma a reentrada de amanhã de 25 minutos em 5.

### Quatro regras

1. **Uma tarefa fechável por dia, escolhida na véspera.** "Trabalhar no projeto" não é tarefa; "fazer o `/health` responder 200 dentro do container" é
2. **Commit todo dia**, mesmo incompleto, mesmo feio, em branch. Nunca encerrar com trabalho existindo só na sua cabeça
3. **Nunca encerrar sem escrever o próximo passo**
4. **Sexta não tem código novo**

### Cronograma

Sem datas de propósito — as semanas avançam quando o critério de pronto é atendido.

| Semana | Etapa               | Entrega                                                                   |
| ------ | ------------------- | ------------------------------------------------------------------------- |
| —      | Etapa 1 (modelagem) | ✅ **concluída** — `docs/modelo.md`                                       |
| 1      | Etapa 0             | ✅ **concluída** — `docker compose up` sobe API e Postgres; `/health` responde 200 |
| 2      | Etapa 1 (migration) | 🔨 prova em SQL puro ✅ feita; falta `alembic upgrade head` criar tudo |
| 3–4    | Etapa 2             | CRUD de recursos em camadas, com testes                                   |
| 5–6    | Etapa 3             | Cadastro, login, logout que invalida de verdade, autorização por papel    |
| 7–8    | **Etapa 4**         | O invariante sob concorrência + o teste que prova                         |
| 9      | Etapa 6             | Suíte de testes e CI verde                                                |
| 10–12  | Etapa 7             | Front-end consumindo a API real                                           |
| 13     | Etapa 8             | **URL pública funcionando — projeto completo**                            |
| 14     | Etapa 9             | README, ADRs consolidados, diagrama, post                                 |

**Total: 14 semanas de trabalho.** Com uma semana de folga a cada quatro — e vai precisar —, dá **cerca de 4 meses**.

Não é pouco, e é honesto: estimativa menor que essa estaria mentindo. A boa notícia é que na **semana 13** o projeto já é completo e publicável. A semana 14 é acabamento.

### Onde o plano vai furar

**A Etapa 4 é a que mais sofre com blocos de 2h**, porque exige segurar muito contexto na cabeça. Duas defesas: use a sexta daquelas semanas como quinto dia de construção, e aceite que ela pode levar três semanas em vez de duas. É a etapa mais importante do projeto — não vale correr.

**A semana em que você não conseguir cumprir nada vai acontecer.** Quando acontecer, não tente compensar dobrando o ritmo: retome de onde parou. Projeto de portfólio não morre por lentidão, morre por abandono depois de uma tentativa de compensar.

### Ponto de publicação mínima

Ao final da **Etapa 8** o projeto já é publicável: back-end completo, invariante garantido, testes em CI, front funcional e URL pública. Se a energia acabar ali, você tem um projeto **completo**, não um pela metade.

---

## 8. As etapas

### 🧱 Etapa 0 — Fundação

> **Concluída:**✅ `docker compose up` sobe API e Postgres; `/health` responde `200` pelo compose.

**Objetivo:** o projeto nasce com o ambiente que uma equipe profissional usaria, antes de existir regra de negócio.

**Conceitos novos**

- Dependências reprodutíveis com `uv` e `pyproject.toml`
- Lint e formatação (`ruff`); verificação de tipos (`mypy`, sem modo estrito)
- `pre-commit`: impedir que código fora do padrão seja commitado
- Containerização: imagem, container, volume, rede
- Docker Compose orquestrando API + Postgres
- Configuração por variáveis de ambiente com `pydantic-settings` — nunca segredo no código
- Arquitetura em camadas: por que `routers/`, `services/`, `repositories/`, `models/`, `schemas/`
- `/health` e por que todo sistema em produção tem um

**Critério de pronto**
`docker compose up` sobe API e Postgres; `GET /health` responde `200`; `ruff` e `mypy` passam limpos; `.env` está no `.gitignore`.

**Armadilhas**0

- Commitar `.env` — o `.gitignore` precisa existir **antes** do primeiro commit. Em repositório público, segredo commitado é segredo **rotacionado**, não apagado
- Criar as pastas de camadas e escrever tudo dentro do router assim mesmo

**Perguntas de entrevista** — _"Por que Docker se o projeto roda na sua máquina?"_ · _"Onde ficam os segredos?"_

---

### 🗄️ Etapa 1 — Modelagem e migrations

> **Modelagem: ✅ concluída** — `docs/modelo.md`.
>
> **Esquema e prova em SQL: ✅ concluídos** — `docs/esquema-alvo.sql` roda do zero no compose, e
> `docs/prova-invariante.sql` demonstra o invariante em sete casos, sem uma linha de Python.
>
> **Falta a migration:** traduzir para SQLAlchemy tipado e gerar o Alembic.

**Objetivo:** o banco deve **impedir** dado inválido, não confiar que o Python vai validar.

**Conceitos novos**

- SQLAlchemy 2.0 tipado (`Mapped`, `mapped_column`)
- Alembic: migração versionada, `upgrade` e `downgrade`
- Constraints como contrato: `NOT NULL`, `CHECK`, `UNIQUE`, FK, `ON DELETE`
- `tstzrange`: intervalo com fuso, tratado como valor único
- Extensão `btree_gist` e a constraint `EXCLUDE` — a peça central
- Índices: varredura sequencial e quando um índice ajuda
- **Todo timestamp em UTC.** Fuso é assunto de apresentação, não de armazenamento
- Intervalo semiaberto `[início, fim)`: reserva que termina às 10h não conflita com a que começa às 10h

**Critério de pronto**
`alembic upgrade head` cria tudo do zero; `downgrade base` desfaz. Você prova, **inserindo SQL na mão**, que o banco recusa duas reservas sobrepostas — sem nenhuma linha de Python.

**Armadilhas** — editar migration já aplicada em vez de gerar nova · `timestamp` sem fuso

**Perguntas de entrevista** — _"Onde garantir uma regra: aplicação ou banco?"_ · _"O que é migration e por que não `create_all`?"_

---

### 🚶 Etapa 2 — Primeira fatia vertical

**Objetivo:** um recurso completo, da requisição HTTP ao banco e de volta, com teste. Fino, mas inteiro.

**Conceitos novos**

- Schemas Pydantic separados por direção: `RecursoCriar`, `RecursoAtualizar`, `RecursoResposta`
- Fluxo em camadas: router → service → repository
- Injeção de dependência do FastAPI e ciclo de vida da sessão
- Erros como contrato: exceptions de domínio traduzidas em respostas HTTP consistentes
- Códigos corretos: `201`, `204`, `404`, `409`, `422`
- Paginação com `LIMIT`/`OFFSET`
- Primeiro `pytest`: banco de teste isolado, fixtures, transação revertida entre testes

**Critério de pronto**
CRUD de `recurso` funcionando, documentado no `/docs`, com testes de caminho feliz e erros. O router não contém regra de negócio nem importa SQLAlchemy.

**Armadilhas** — devolver o modelo de tabela na resposta (é assim que campo interno vaza) · testes que compartilham estado

**Perguntas de entrevista** — _"Por que separar schema de API do modelo de banco?"_ · _"Quando 404 e quando 409?"_

---

### 🔐 Etapa 3 — Autenticação e autorização

**Objetivo:** entender a diferença entre _quem você é_ e _o que você pode fazer_ — e por que logout com JWT é um problema.

**Conceitos novos**

- Hash com Argon2 (`pwdlib`): por que hash não é criptografia, e o que é _salt_
- JWT: cabeçalho, payload, assinatura — e por que **o payload é legível por qualquer pessoa**
- O problema: JWT é _stateless_, logo **não dá para invalidá-lo**
- A solução: **access token curto (~15 min) + refresh token guardado no banco e revogável**. Logout apaga o refresh token — aí a invalidação é verdadeira
- Cookie `httpOnly` + `Secure` + `SameSite` vs. `localStorage`, e por que `localStorage` é vulnerável a XSS
- CSRF: o risco que aparece quando você adota cookie
- Autorização por papel via dependências do FastAPI
- **IDOR**: o usuário 5 pedindo `/reservas/9`, que é de outra pessoa. Autorização é por **objeto**, não só por rota

**Critério de pronto**
Existe teste provando que **após o logout o refresh token não funciona mais**, e teste provando que um usuário não lê nem cancela a reserva de outro.

**Armadilhas** — dado sensível no payload do JWT · mensagem de erro que revela se o e-mail existe

**Perguntas de entrevista** — _"Como você faz logout com JWT?"_ — a pergunta que elimina a maioria dos candidatos.

---

### ⚙️ Etapa 4 — O coração: reservas, concorrência e estados

**Objetivo:** a etapa mais importante. Aqui você aprende o que acontece quando duas pessoas clicam ao mesmo tempo.

**Conceitos novos**

- Transações e **ACID** na prática, não na definição decorada
- Isolamento: `READ COMMITTED` (padrão) vs. `SERIALIZABLE`
- **Condição de corrida:** por que `if disponivel: criar()` está errado, mesmo parecendo certo
- Três soluções, e quando usar cada uma:
  1. bloqueio pessimista — `SELECT ... FOR UPDATE`
  2. bloqueio otimista — coluna de versão e nova tentativa
  3. **garantia declarativa** — a constraint `EXCLUDE`, que não depende de o código lembrar de checar
- Capturar a violação e traduzir em `409 Conflict` legível
- Máquina de estados: `confirmada → concluída`, com `cancelada`. Transição inválida é recusada explicitamente
- Fusos e a diferença entre o horário que o usuário pensa e o instante que o sistema grava
- Consulta de disponibilidade: calcular as lacunas livres de um recurso num dia

**Critério de pronto**
Existe teste que dispara **duas requisições concorrentes para o mesmo recurso no mesmo horário** e comprova que exatamente uma retorna `201` e a outra `409`.

> Esse teste é, sozinho, o item de maior valor do seu portfólio inteiro.

**Armadilhas** — validar disponibilidade no Python e achar que resolveu · testar concorrência em série (dois `requests` seguidos não é concorrência) · confundir "não sobrepõe" com "não encosta": `[9h,10h)` e `[10h,11h)` **não** conflitam

**Perguntas de entrevista** — _"Como você garante que dois usuários não reservem a mesma sala ao mesmo tempo?"_ · _"Bloqueio otimista ou pessimista?"_

---

### 🧪 Etapa 6 — QA/QC: estratégia de testes e CI

**Objetivo:** parar de "escrever uns testes" e passar a ter uma **estratégia** de qualidade.

**Conceitos novos**

- **Pirâmide de testes:** muitos unitários, alguns de integração, poucos de ponta a ponta — e por que a proporção inversa deixa a suíte lenta e instável
- Unitário: isola a regra, sem banco. Integração: API + Postgres real do compose
- Dublês: _stub_, _mock_, _fake_, _spy_ — e por que mockar demais faz o teste testar o mock
- Fixtures e factories
- Cobertura: útil como alarme, enganosa como meta. 100% com zero asserção útil é possível
- Escrever o teste **antes** da correção do bug
- CI no GitHub Actions: lint, tipos, testes e migrations a cada push; badge no README

**Critério de pronto**
`pytest` roda contra Postgres em container. O CI roda tudo a cada push e o badge está verde.

**Armadilhas** — testar implementação em vez de comportamento · testes que dependem da ordem ou do relógio real · perseguir percentual de cobertura

**Perguntas de entrevista** — _"Como você decide o que testar?"_ · _"Qual sua meta de cobertura?"_ — a resposta certa **não** é um número.

---

### 🖥️ Etapa 7 — Front-end

**Objetivo:** interface que consome a API real e trata o que existe além do caminho feliz.

**Conceitos novos**

- Vite + React + TypeScript; tipos gerados a partir do OpenAPI
- **Estado de servidor vs. estado de interface** — a distinção que organiza um front inteiro
- TanStack Query: cache, revalidação, nova tentativa
- Os quatro estados de toda tela: carregando, vazio, erro, sucesso
- Formulários com react-hook-form + zod, exibindo os erros vindos do back
- Rotas protegidas e renovação silenciosa de token
- Calendário no fuso do usuário
- **Atualização otimista** e como desfazer quando o servidor recusa
- Acessibilidade básica: rótulos, foco, teclado, contraste
- Um teste Playwright de ponta a ponta

**Critério de pronto**
Login, listagem, calendário de disponibilidade e criar/cancelar reserva funcionando contra a API real. Um teste Playwright percorre "logar → reservar → ver na agenda → cancelar". Reservar horário ocupado mostra mensagem clara, vinda do `409`.

**Armadilhas** — `useEffect` + `fetch` na mão para tudo · formatar data sem cuidar de fuso · ignorar o estado de erro

---

### 📡 Etapa 8 — Observabilidade e deploy

**Objetivo:** existir uma URL pública — e você conseguir descobrir o que aconteceu quando algo quebra.

**Conceitos novos**

- Log estruturado em JSON, sem dado sensível
- **ID de correlação:** um identificador que atravessa requisição, log e resposta
- `Dockerfile` simples e imagem enxuta
- Migrations no deploy: rodar antes de subir a versão nova; toda migration retrocompatível
- Deploy em Fly.io ou Render, com Postgres gerenciado
- Segredos em produção, jamais no repositório
- Backup e **restauração testada**, não só backup

**Critério de pronto**
URL pública funcionando, com dados de demonstração e credenciais de teste no README. Um erro em produção é rastreável pelo ID de correlação.

**Armadilhas** — deploy manual e não documentado · migration destrutiva antes do código novo · `DEBUG=True` em produção

**Perguntas de entrevista** — _"Como você investiga um erro que só acontece em produção?"_

---

### 📖 Etapa 9 — Vitrine

**Objetivo:** o trabalho está feito; agora precisa ser **legível em dois minutos** por quem nunca te viu.

**O que produzir**

- README com: o problema, um GIF de 20 segundos, link da demonstração, credenciais de teste, diagrama de arquitetura, como rodar localmente em um comando
- **Seção "Decisões técnicas"** com 5 a 7 escolhas e o porquê — a parte que recrutador técnico realmente lê
- **`docs/colaboracao-ia.md`** — como a IA foi usada e como cada saída foi validada. Em 2026 isso é requisito, não confissão: mostre o protocolo, dois ou três exemplos de sugestão que você **recusou** e por quê, e o teste que provou a correção
- **Seção "O que eu faria diferente"** — três decisões que revisitaria. Quase ninguém escreve
- ADRs consolidados e diagrama do modelo em Mermaid, que o GitHub renderiza nativamente
- `docs/aprendizados.md` publicado, honesto sobre o que foi difícil
- Post no LinkedIn sobre **um problema técnico** (a corrida de reservas), não sobre "terminei meu projeto"

**Critério de pronto**
Uma pessoa desconhecida entende o que o sistema faz, abre a demonstração e roda o projeto localmente — sem te perguntar nada.

---

## 9. Bônus — só depois do deploy

**Idempotência é o primeiro a fazer.** O usuário clica "Reservar", a conexão engasga, ele clica de novo. Sem tratamento: duas reservas. O padrão `Idempotency-Key` — o cliente manda um identificador único, o servidor guarda pedido e resposta, e repetições devolvem o resultado original sem executar nada. É como todo gateway de pagamento funciona, é o assunto de maior retorno em entrevista, e fica barato depois que a Etapa 4 já ensinou o raciocínio.

Depois dele: recursos com N unidades · histórico completo de eventos · testes de propriedade com `hypothesis` · fuzzing de contrato com `schemathesis` · teste de carga · rate limiting · reserva por linguagem natural com LLM (onde o modelo **interpreta** e nunca **decide**).

---

## 10. Glossário

| Termo                            | Em uma frase                                                               |
| -------------------------------- | -------------------------------------------------------------------------- |
| **Invariante**                   | Regra que o sistema nunca pode violar                                      |
| **ACID**                         | Garantias de transação: atômica, consistente, isolada, durável             |
| **Condição de corrida**          | Duas operações simultâneas erram por causa do tempo entre verificar e agir |
| **Bloqueio pessimista**          | Travar a linha antes de mexer                                              |
| **Bloqueio otimista**            | Deixar acontecer e detectar conflito na gravação, via versão               |
| **Idempotência**                 | Repetir a operação produz o mesmo resultado, sem efeito extra              |
| **Migration**                    | Alteração versionada do esquema, aplicável e reversível                    |
| **ADR**                          | Registro curto de uma decisão de arquitetura e do seu porquê               |
| **IDOR**                         | Falha em que o usuário acessa objeto de outro trocando o ID                |
| **Esqueleto que anda**           | Fatia fina funcionando de ponta a ponta desde cedo                         |
| **Instante / período / duração** | Um ponto no tempo · de X até Y · quanto tempo dura. Três tipos diferentes  |

---

## 11. Regras deste projeto

1. **Eu sou a arquiteta.** A IA digita, explica, revisa e ensina. Não decide arquitetura por mim.
2. **Nenhuma linha entra no repositório que eu não consiga explicar em voz alta.**
3. **Toda decisão relevante vira ADR — escrito antes do código.**
4. **Tento sozinha antes de pedir revisão.**
5. **Uma etapa por vez**, com o critério de pronto atendido.
6. **Todo bug ganha primeiro um teste que o reproduz.**
7. **Ideia nova vai para o backlog**, não para a v1.

---

_Documento vivo. Atualize-o conforme o entendimento evoluir — inclusive corrigindo o que aqui está._
