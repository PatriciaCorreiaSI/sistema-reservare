# API - contrato HTTP

Todas as rotas ficam sob `/api` ([ADR 0024](./adr/0024-alcancar-api-pelo-proxy-do-vite.md)): é o prefixo que o proxy do Vite encaminha ao backend. Fora dele ficam só `/health`, que o ADR nomeia, e `/docs` e `/openapi.json`, que são do FastAPI, não da API.


## Recurso

### Schemas

```
RecursoCriar
    nome_recurso: str
    ocupacao: int = Field(gt=0)
    hora_func_inicio: time
    hora_func_fim: time
    valida: hora_func_inicioo < hora_func_fim (model_validator) → 422
```

```
RecursoAtualizar
    nome_recurso: str | None = None
    ocupacao: int | None = Field(default=None, gt=0)
    hora_func_inicio: time | None = None
    hora_func_fim: time | None = None
    status_recurso: Literal["ativo", "inativo"] | None = None
```

```
RecursoResposta
    id_recurso: int
    nome_recurso: str
    ocupacao: int
    hora_func_inicio: time
    hora_func_fim: time
    status_recurso: str
    fuso: str
```

```
Lacuna
    inicio: datetime
    fim: datetime
```

```
DisponibilidadeResposta
    id_recurso: int
    dia: date
    lacunas: list[Lacuna]
```


- **O `dia` é local; as lacunas, em UTC** ([ADR 0019](./adr/0019-disponibilidade-como-lacunas-livres.md)). A resposta devolve o `dia` junto porque uma lacuna às 23h UTC do dia 2 ainda pertence ao dia 2 em Brasília: sem ele, a lista não diz de que dia fala.

- **`fuso` é o nome IANA do fuso de funcionamento** (emenda ao [ADR 0018](./adr/0018-fuso-unico-do-sistema.md)): `hora_func_inicio` e `hora_func_fim` são horas de relógio nesse fuso, e a tela formata as lacunas nele. Hoje é `FUSO_FUNCIONAMENTO` para todos os recursos; o campo já tem a forma de "um fuso por recurso".

### Rotas de `/api/recursos`

| **Rota**  |  **Sucesso** |  **Erros** | **Porquê** |
|-----------|--------------|------------|------------|
|`POST /api/recursos`| `201` + `RecursoResposta`| `401` · `403` · `422` (schema)| `401` para quem não está logado [ADR 0020](./adr/0020-exigir-token-nas-rotas-de-recurso.md); `403` para usuário comum, só admin escreve em recursos; `RecursoCriar` não tem `status_recurso` porque por default todo recurso nasce como `ativo`.  |
|`GET /api/recursos?limite=&deslocamento=`| `200` + lista| `401` · `422`  | `401` para quem não está logado. Leitura é para quem está logado, de qualquer privilégio [ADR 0020](./adr/0020-exigir-token-nas-rotas-de-recurso.md). `422` para valor que não é inteiro ou fora da faixa: `limite` de 1 a 100 (padrão 20), `deslocamento` a partir de 0 (padrão 0). O teto impede que um pedido leia a tabela inteira de uma vez; `limite=0` seria um pedido que nunca devolve nada. |
|`GET /api/recursos/{id}`| `200`| `401` · `404` | `401` para quem não está logado; dá `404` quando o recurso pedido não existe. |
|`PATCH /api/recursos/{id}`| `200`| `401` · `403` · `404` · `422`| `401` para quem não está logado; `403` para usuário comum; `422` para valor fora da regra do campo (`ocupacao` maior que zero, `status_recurso` só `ativo` ou `inativo`, `hora_func_inicio` antes de `hora_func_fim` depois de aplicado o patch) e para `null` em qualquer campo: campo ausente significa "não mexer", mas nenhum campo de recurso aceita ficar sem valor. As cinco colunas são `NOT NULL`. O contrato gerado ainda diz `string \| null`, porque o validador do Pydantic não aparece no OpenAPI. `PUT` obrigaria o usuário a escrever sempre todos os campos, sob risco de reescrever dado velho. `PATCH` garante a inserção apenas dos dados a serem atualizados e mantém os demais como estão. |
|`DELETE /api/recursos/{id}`| `204`| `401` · `403` · `404` · `409`| `401` para quem não está logado; `403` para usuário comum; dá `404` quando o recurso pedido não existe. Dá `409` quando o recurso existe, a requisição está bem formada, mas ela conflita com o estado atual do sistema (o recurso está em uso: existe reserva apontando para ele. A FK é `ON DELETE RESTRICT` e por isso não é possível deletá-lo por causa do que já existe no banco). |
|`GET /api/recursos/{id}/disponibilidade?dia=2026-10-02`| `200` + `DisponibilidadeResposta`| `401` · `404` · `409` · `422` |`401` para quem não está logado [ADR 0019](./adr/0019-disponibilidade-como-lacunas-livres.md); `404` para recurso inexistente; `409` para recurso inativo; `422` para dia ausente ou mal formado. Um dia no passado ou todo ocupado não dá `422`, e sim `200` com a lista vazia. |


## Autenticação

### Schemas

- Schema descreve o que viaja no JSON, não o que fica na tabela. Regra de entrada o cliente só manda o que ele sabe e tem direito de dizer; o que o servidor calcula (hash) ou consulta (`espira_em`, `revogado_em`) nunca entra, porque tudo o que o cliente manda ele pode mentir.

```
LoginEntrada
    email_usuario: str
    senha: str
```

```
TokenResposta
    access_token: str
    token_type: str = "bearer"
```


- **O refresh viaja num cookie, nunca no JSON ([ADR 0023](./adr/0023-guardar-refresh-em-cookie-httponly.md)):** `refresh_token`, com `HttpOnly`; `Secure`; `SameSite=Strict`; `Path=/api/auth`; `Max-Age=` igual a `REFRESH_DIAS` em segundos. O login e o refresh o gravam pelo `Set-Cookie`; o refresh e o logout o leem do cabeçalho `Cookie`, que o navegador manda sozinho; o logout o apaga com `Max-Age=0`, no mesmo `Path`. Sem o cookie, o refresh responde `401` e o logout `204`. Clientes fora do navegador precisam guardar cookies (`curl -c / -b`).

- **Payload do JWT:** só entra no payload o que se mostraria ao próprio usuário na tela. O padrão tem dois obrigatórios: 
    - `sub` (*subject*, quem é: `id_usuario`): para identifica a quem pertence;
    - `exp`(*expiration*, instante em que este access deixa de valer, em UTC). O refresh não é JWT; o vencimento dele é `espira_em` no banco.
    - `privilegio_usuario`: entra, para a dependência autorizar (`403`) validando só a assinatura, sem ir ao banco. O custo: rebaixado continua admin por até 15 minutos. É o mesmo aceito no ADR 0012 para desativação.
    - Não entra: senha, hash, e-mail (o `sub` já identifica), nome.


### Rotas de `/api/auth`

| **Rota**  |  **Sucesso** |  **Erros** | **Porquê** |
|-----------|--------------|------------|------------|
|`POST /api/auth/login`| `200` + `TokenResposta` + cookie `refresh_token` | `401` | Única rota que não recebe token: ela que os cria. O access vai no corpo; o refresh vai no `Set-Cookie`. `status_usuario = inativo`, `email_inexistente` e senha errada recebem a mesma resposta `401`: mesmo código e texto idêntico para API não servir de lista de quem está cadastrado. |
|`POST /api/auth/refresh`| `200` + `TokenResposta` + cookie novo | `401` | Cliente chama `/api/auth/refresh` quando o access expira para continuar logado. Sem corpo: o refresh vem no cookie, e sem cookie é `401`. Servidor procura o SHA-256 dele em `hash_token` e confere `expira_em` e `revogado_em`. Rotação devolve access novo no corpo e refresh novo no `Set-Cookie`, e marca o antigo `revogado_em`. Refresh revogado reapresentado devolve `401` e revoga a família toda. Cliente legítimo cai e precisa fazer login de novo. Custo aceito porque o servidor não sabe qual dos dois é o ladrão. | 
|`POST /api/auth/logout`| `204` + cookie apagado | — | Lê o refresh do cookie, marca `revogado_em` e manda `Max-Age=0`. Idempotente: refresh já revogado, desconhecido ou cookie ausente devolvem `204` também. O objetivo já está atingido: este refresh não funciona mais. |


### Dependências

```
UsuarioAtual
    id_usuario: int
    privilegio_usuario: str
```

```
obter_usuario_atual(credenciais=Depends(HTTPBearer())) → UsuarioAtual
levanta: 401 quando o cabeçalho falta, não é `Bearer`, a assinatura não confere ou `exp` passou.
```

```
exigir_admin(usuario:UsuarioAtual=Depends(obter_usuario_atual)) → UsuarioAtual
levanta: 403 quando `usuario.privilegio_usuario != "admin"`
```


## Usuário

### Schemas

```
UsuarioCriar
    nome_usuario: str = Field(min_length=1)
    email_usuario: EmailStr
    senha: str = Field(min_length=8)
    privilegio_usuario: Literal["admin", "usuario"]
```

```
UsuarioResposta
    id_usuario: int
    nome_usuario: str
    email_usuario: str
    privilegio_usuario: str
    status_usuario: str
```


- O cliente manda a senha em texto (por HTTPS); o Argon2 é calculado no servidor. Sem `status_usuario`: o serviço atribui `ativo`, como em recurso.


### Rotas de `/api/usuarios`

| **Rota**  |  **Sucesso** |  **Erros** | **Porquê** |
|-----------|--------------|------------|------------|
|`POST /api/usuarios`| `201` + `UsuarioResposta` | `401` · `403` · `422` · `409`  | Sem acesso válido devolve `401`. Se um usuário comum tentar cadastrar sem privilégio de admin recebe `403`: só admin pode cadastrar. Recusa nome vazio, e-mail inválido e senha curta devolvendo `422`. Devolve `409` em tentativa de cadastrar e-mail duplicado: e-mail é `UNIQUE`. `UsuarioResposta` nunca inclui senha nem hash. |


- **Primeiro admin** é criado fora da API por um comando (`criar_admin`, senha vinda de variável de ambiente), porque o banco nasce vazio e só admin cadastra. Rodar com `uv run python -m app.comandos.criar_admin` de dentro de `backend/`, lendo `ADMIN_NOME`, `ADMIN_EMAIL` e `ADMIN_SENHA` do `.env` e saindo com código `1` se o e-mail já existir. Nos testes, a fixture grava o admin direto pelo modelo.


## Reserva

### Schemas

```
ReservaCriar
    id_recurso: int
    convidados: int = Field(gt=0)
    inicio: AwareDatetime
    fim: AwareDatetime
    valida: inicio < fim (model_validator) → 422
```

```
ReservaResposta
    id_reserva: int
    id_usuario: int
    id_recurso: int
    convidados: int
    inicio: datetime
    fim: datetime
    status_reserva: str         confirmada | cancelada | concluida
    cancelada_por_id_usuario: int | None
    cancelada_em: datetime | None
```


- **O `periodo` não viaja no JSON.** O `tstzrange` é um tipo do Postgres, e o JSON não tem nada parecido. O cliente manda `inicio` e `fim`, e o service monta o intervalo semiaberto `[inicio, fim)`. A resposta devolve os dois de volta.

- **Horário sem fuso é recusado.** `AwareDatetime` exige o deslocamento (`2026-10-01T09:00-03:00`); sem ele (`2026-10-01T09:00`), o horário é ambíguo e a resposta é `422`. O banco guarda o instante, e fuso é assunto de apresentação.

- **O cliente não manda quem reserva, nem o status.** `id_usuario` vem do token: quem reserva é quem chama, e aceitar do corpo deixaria reservar em nome de outra pessoa. A reserva nasce `confirmada`, e as colunas de cancelamento só mudam pela rota de cancelar.

- **O schema valida só o que o JSON sabe sozinho** (`convidados > 0`, `inicio < fim`). O que depende do relógio (não reservar no passado) ou do recurso no banco (ativo, horário de funcionamento, `convidados <= ocupacao`) é regra do service.

- **`status_reserva` na resposta é o status efetivo**, não a coluna: uma reserva confirmada cujo fim já passou aparece como `concluida` ([ADR 0004](./adr/0004-status-reserva-concluida.md)). Por isso, e porque `inicio` e `fim` não existem na tabela, `ReservaResposta` não é montada direto do modelo com `from_attributes`.


### Rotas de `/api/reservas`

| **Rota**  |  **Sucesso** |  **Erros** | **Porquê** |
|-----------|--------------|------------|------------|
|`POST /api/reservas` | `201` + `ReservaResposta` | `401` · `422` · `404` · `409`  | `401`: sem token válido. `422`: quando o conteúdo viola uma regra, e quem pede precisa mudar o pedido: no schema (horário sem fuso, `inicio >= fim`, `convidados <= 0`) ou no service (no passado, fora do horário de funcionamento, mais convidados que a ocupação). `404`: quando o recurso não existe. `409`: quando o pedido está certo, mas conflita com o estado atual: o horário já está ocupado por outra reserva (a `EXCLUDE`) ou o recurso está inativo. `id_usuario` vem do token.  |
|`GET /api/reservas?limite=&deslocamento=` | `200` + lista de `ReservaResposta` | `401` · `422` | `401`: sem token válido. `422`: limite ou deslocamento fora da faixa, a mesma de `GET /api/recursos`. Filtra em vez de recusar: o usuário comum recebe só as suas reservas, o admin recebe todas. |
|`GET /api/reservas/{id}`| `200` + `ReservaResposta`  | `401` · `404` | `401`: sem token válido. `404`: tanto para a reseva que não existe quanto para a de outra pessoa: a resposta não revela que ela existe ([ADR 0017](./adr/0017-404-a-quem-nao-pode-acessar-a-reserva.md)). O admin lê qualquer uma. |
|`POST /api/reservas/{id}/cancelar` | `200` + `ReservaResposta` | `401` · `404` · `409` |`401`: sem token válido. `404`: para a reserva inexistente ou de outra pessoa, como na leitura. `409`: quando a reserva já foi cancelada ou já terminou ([ADR 0016](./adr/0016-cancelar-pela-acao-com-update-condicional.md)). Devolve a reserva, e não `204`, porque ela continua existindo, agora cancelada, e o cliente vê o resultado sem outro `GET`.|
