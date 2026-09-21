# ADR 0010 — Tratar a requisição como a transação

- **Data:** 2026-09-11
- **Situação:** aceita

## Contexto

Definir onde a transação começa e onde ela termina. A `Session` é uma por requisição: dado que ela não é segura entre threads; e a API é síncrona, então cada requisição é uma thread.

## Decisão

Escolhi a opção em que a **dependência comita no fim:** depois do `yield`, `commit()` se o handler voltou sem exceção; `rollback()` se uma exceção passou; `close()` sempre. A fronteira da **"Unidade de trabalho" (*Unit of work*)** é a requisição. Nenhuma camada chama `commit()` (uma exceção: ver Emenda). A etapa 4 vai precisar que *"uma requisição = uma transação"* seja literal. 

## Alternativas consideradas

- **Cada operação comita** — por que descartei: o repository faz `session.add(recurso); session.commit()` no fim de cada operação que escreve. Simples de ler, quem escreve, confirma. Mas custa um *service* que faz duas escritas ter dois `commit`. Se o segundo falhar, o primeiro já entrou. *A Unidade de Trabalho* deixa de ser uma unidade.

## Consequências

O ganho é que um *service* que faz três escritas produz uma transação. O padrão de *Unidade de Trabalho* é mantido. O custo é se ter o erro longe do código, porque ele só aparece no `commit`. Então se faz necessário usar a regra de `flush`: todo repository que escreve faz `session.flush()` antes de devolver. Assim, o erro aparece cedo, pois o `flush` traz o erro no banco para dentro da camada que sabe o que ele significa e a camada imediatamente acima (*service*) o traduz para uma exceção do domínio. Além disso, quem lê o repository não vê onde a transação fecha, pois o `commit` é invisível nas camadas e isso não tem contorno. Quando um *service* precisar de duas transações de propósito, terá que sair da convenção explicitamente.

## Emenda (2026-09-21): a única escrita que sobrevive à exceção

### **Problema:** 
No `POST /auth/refresh`, um refresh já revogado que é apresentado de novo é sinal de reuso (ADR 0012 e `api.md`): o serviço revoga a família inteira e responde `401`. O `401` nasce de `CredenciaisInvalidas`, que atravessa o `yield` do `obter_sessao`. E ele faz `rollback`, desfazendo o `UPDATE` que revogou a família. O cliente recebe `401`, a família continua viva no banco e quem roubou o token tenta de novo com outro da mesma família. A detecção existe no código e não existe no banco.

A regra geral ("exceção desfaz tudo") pressupõe que a escrita é parte do que deu errado. Aqui ela não é: a revogação é a resposta ao erro, e precisa sobreviver a ele.

### **Decisão:** 
O `AuthService` chama `self._sessao.commit()` logo depois de `revogar_familia`, antes de levantar `CredenciaisInvalidas`. Quando o `rollback` do `obter_sessao` chega, a revogação já é definitiva. É o único `commit()` fora do `obter_sessao`, e fica nomeado aqui por isso

### **Alternativa descartada:**
- **Não levantar exceção:** o service devolve `None` e o router responde `401` com JSONResponse; sem exceção, o `obter_sessao` comita normalmente. Custo: o router passa a ter regra ("se veio `None`, é `401`"), o que viola a convenção de camadas.  E o `401` passa a nascer em dois lugares diferentes (handler global para login e router para refresh).

- **Sessão independente** só para o `UPDATE` da família: abre uma segunda `Session` do zero, faz o `UPDATE`, comita e fecha. A da requisição é desfeita pelo `rollback` como sempre. Custo: duas conexões por requisição, código de infraestrutura dentro do service, a fixture de teste não enxerga essa segunda sessão. Ela escreveria de verdade no banco de teste, quebrando o isolamento do [ADR 0011](0011-isolar-teste-em-transacao-desfeita-no-fim.md).

### Consequências
O `create_savepoint` da fixture `sessao` faz esse `commit()` liberar só o *savepoint*; a transação externa da fixture continua de pé e é desfeita no fim do teste. O [ADR 0011](0011-isolar-teste-em-transacao-desfeita-no-fim.md) sobrevive sem ajuste.

### Como eu saberia que errei
Se aparecer um segundo `commit()` fora do `obter_sessao` significa que a exceção virou
regra. Ou se o teste de reuso passar conferindo só o `401`, sem consultar no banco que
a família ficou revogada: com a detecção desfeita ele passaria igual.

## Como eu saberia que errei

Se um `IntegrityError` chegar ao cliente como `500`. É o sinal de um repository sem `flush` ou de que a regra não segurou.
