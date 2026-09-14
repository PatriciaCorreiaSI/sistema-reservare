# API - contrato HTTP

## Recurso

### Schemas

```
RecursoCriar
    nome_recurso: str
    ocupacao: int
    hora_func_inicio: time
    hora_func_fim: time
```

```
RecursoAtualizar
    nome_recurso: str | None = None
    ocupacao: int | None = None
    hora_func_inicio: time | None = None
    hora_func_fim: time | None = None
    status_recurso: str | None = None
```

```
RecursoResposta
    id_recurso: int
    nome_recurso: str
    ocupacao: int
    hora_func_inicio: time
    hora_func_fim: time
    status_recurso: str
```


### Rotas

| **Rota**  |  **Sucesso** |  **Erros** | **Porquê** |
|-----------|--------------|------------|------------|
|`POST /recursos`| `201` + `RecursoResposta`|`422` (schema)| `RecursoCriar` não tem `status_recurso` porque por default todo recurso nasce como `ativo`. |
|`GET /recursos?limite=&deslocamento=`| `200` + lista| — | |
|`GET /recursos/{id}`| `200`|`404`| |
|`PATCH /recursos/{id}`| `200`|`404` · `422`| `PUT` obrigaria o usuário a escrever sempre todos os campos, sob risco de reescrever dado velho. `PATCH` garante a inserção apenas dos dados a serem atualizados e mantém os demais como estão. |
|`DELETE /recursos/{id}`| `204`|`404` · `409`|Dá `404` quando o recurso pedido não existe. Dá `409` quando o recurso existe, a requisição está bem formada, mas ela conflita com o estado atual do sistema (o recurso está em uso: existe reserva apontando para ele. A FK é `ON DELETE RESTRICT` e por isso não é possível deletá-lo por causa do que já existe no banco).|

