# ADR 0014 — Traduzir violação da constraint pelo nome

- **Data:** 2026-09-24
- **Situação:** aceita

## Contexto

O `except` de `services/usuario.py` pega qualquer violação de integridade e sempre responde "e-mail já cadastrado". Para a reserva, isso não serve. Um `INSERT` em `reserva` pode esbarrar em pelo menos quatro constraints diferentes, e cada uma significa algo diferente (`ex_reserva_sem_sobreposicao`, `fk_reserva_id_recurso_recurso`, `ck_reserva_convidados_positivos`, `ck_reserva_formato_semiaberto`). Se um `except` genérico fosse copiado para a reserva, um bug de validação viraria um `409` mentiroso. E um erro mal classificado é pior do que um `500`, porque pelo menos `500` avisa que algo quebrou. 

O mesmo problema já existe no recurso (dívida da Etapa 2): `criar` e `atualizar` não capturam nada, e um `ocupacao: 0` esbarra em `ck_recurso_ocupacao_positiva` e vira `500`. Uma restrição torna a tradução possível: pelo ADR 0010, todo repository que escreve faz `flush()`, e as constraints são verificadas no `INSERT`, não no `commit()`. O erro aparece dentro do repository, antes de a requisição terminar.

## Decisão

Escolhi identificar qual constraint falhou pelo nome (`IntegrityError.orig.diag.constraint_name`), comparando com uma constante no código, e não com uma string solta. A tradução deverá morar no `Repository`: o conhecimento do banco fica na camada que já é dona dele, e o service recebe só a exceção de domínio. Cada método do repository traduz as constraints que a sua própria operação violar: a mesma constraint pode significar coisas diferentes em operações diferentes, e o método conhece a operação. Quando houver uma violação que o sistema não reconhece, deixar subir, sem capturar, e ela vira `500`. Nunca engolir o que não se reconhece. O ADR passa a valer como regra geral, pagando também a dívida da Etapa 2. A tradução encerra o uso da sessão, porque depois do erro a transação fica abortada.

Mapeamento inicial:

| Constraint | Exceção de domínio | Status |
|---|---|---|
| `ex_reserva_sem_sobreposicao` | nova, para horário ocupado | `409` |
| `fk_reserva_id_recurso_recurso`, no `INSERT` de reserva | `RecursoNaoEncontrado` | `404` |
| `uq_usuario_email_usuario` | `EmailJaCadastrado` | `409` |
| `fk_reserva_id_recurso_recurso`, no `DELETE` de recurso | `RecursoEmUso` | `409` |
| qualquer `CHECK` | nenhuma: sobe | `500` |

O `CHECK` que dispara é bug de validação na entrada, e o conserto é validar no schema, não traduzir.

## Alternativas consideradas

- **Identificar qual constraint falhou por texto da mensagem** — por que descartei: frágil, a mensagem muda com a versão e o idioma do Postgres. Mercado também descarta.

- **Identificar qual constraint falhou só pelo SQLSTATE** — por que descartei: é robusto, mas não distingue duas constraints do mesmo tipo. As quatro `CHECK` da `reserva` têm todas o código `SQLSTATE` = `23514`.

- **Verificar antes em Python (`SELECT` antes do `INSERT`)**  — por que descartei: não resolve sozinha. É exatamente a janela de corrida que o projeto existe para fechar. Pode servir de complemento, para uma mensagem mais amigável, mas o banco continua sendo o guardião.

- **Traduzir a constraint no `Service`**  — por que descartei: mantém o padrão que já existe. Mas faz o `service` conhecer detalhe de banco (`.orig`, `.diag`, nome de constraint), o que contraria a convenção "`repositories/` conhece o banco".

## Consequências

O ganho é que identificar a constraint pelo nome é preciso e estável. O custo é que renomear uma constraint numa migration exige mudar o código que a reconhece. Um teste que provoca a violação pega essa quebra. Outro custo é mudar o `UsuarioService` e `RecursoService` para o novo padrão, para não ficarem dois padrões convivendo. O repository passa a importar as exceções de `services/excecoes.py`: a camada de baixo passa a importar da camada de cima. Não há import circular, porque o `excecoes.py` não importa nada, mas a dependência fica invertida e isso é um custo a pagar. Mover as exceções para um módulo de domínio seria outra decisão.

## Como eu saberia que errei

Se o mesmo método do repository precisar traduzir a mesma constraint em respostas diferentes, conforme uma regra de negócios que ele não conhece. O repository não conhece o contexto do negócio, então nesse caso a tradução teria de voltar para o service.


## Emenda (2026-10-08): a validação mora onde a regra enxerga os dados

### Problema

O ADR diz que o conserto de uma `CHECK` que dispara é validar no schema. No `PATCH`, a regra `hora_func_inicio < hora_func_fim` depende de um valor que pode estar só no banco. Um pedido com só `hora_func_fim` não leva o início, e o schema não enxerga o banco.

Como apareceu: em 2026-10-08, o exemplo automático do `/docs` mandou `ocupacao` zero e horários iguais, e o `POST /api/recursos` deu `500`. O `ReservaCriar` valida, mas o `RecursoCriar` e o `RecursoAtualizar` não.

### Decisão

A `CHECK` que dispara continua sendo validação faltando. O que muda é onde a validação mora. 
- Se a regra depende só do pedido, ela fica no schema. É o caso da `ocupacao`, do `status_recurso` e dos dois horários no `POST`.
- Se a regra depende também do que está gravado, ela fica no service, depois de aplicar o patch sobre o recurso lido. É o caso dos horários do `PATCH`.

O service lança uma exceção de domínio nova, e um handler a traduz para `422`. A fonte de mercado é a RFC 7396, do *JSON Merge Patch*: aplica-se o patch ao recurso atual e valida-se o resultado. A tabela do ADR continua valendo: nenhuma `CHECK` é traduzida, e a que escapar sobe como `500`.

### Alternativas descartadas

- **Traduzir a `CHECK` para `422` no repository** — por que descartei: é o menor código, mas o banco deixa de ser a última defesa e vira a validação. Contradiz a própria decisão do ADR.

- **Exigir no schema que os dois horários venham juntos** — por que descartei: tudo ficaria no schema, mas o `PATCH` perderia o sentido de mandar só o que muda, que é o porquê registrado no `api.md`.

### Consequências

O ganho: o `PATCH` continua parcial, e o banco continua sendo só a última defesa. O custo: a mesma regra mora em dois lugares, no schema no `POST` e no service do `PATCH`. O projeto ganha mais uma exceção e mais um handler.

### Como eu saberia que errei

Se um `PATCH` voltar a dar `500` por uma `CHECK`, existe uma combinação de campos que o service não confere. Se o `POST` e o `PATCH` divergirem, a duplicação cobrou o seu preço. Exemplo: um aceita horários iguais e o outro recusa.
