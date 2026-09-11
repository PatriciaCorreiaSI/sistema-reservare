# ADR 0010 — Tratar a requisição como a transação

- **Data:** 2026-09-11
- **Situação:** aceita

## Contexto

Definir onde a transação começa e onde ela termina. A `Session` é uma por requisição: dado que ela não é segura entre threads; e a API é síncrona, então cada requisição é uma thread.

## Decisão

Escolhi a opção em que a **dependência comita no fim:** depois do `yield`, `commit()` se o handler voltou sem exceção; `rollback()` se uma exceção passou; `close()` sempre. A fronteira da **"Unidade de trabalho" (*Unit of work*)** é a requisição. Nenhuma camada chama `commit()`. A etapa 4 vai precisar que *"uma requisição = uma transação"* seja literal. 

## Alternativas consideradas

- **Cada operação comita** — por que descartei: o repository faz `session.add(recurso); session.commit()` no fim de cada operação que escreve. Simples de ler, quem escreve, confirma. Mas custa um *service* que faz duas escritas ter dois `commit`. Se o segundo falhar, o primeiro já entrou. *A Unidade de Trabalho* deixa de ser uma unidade.

## Consequências

O ganho é que um *service* que faz três escritas produz uma transação. O padrão de *Unidade de Trabalho* é mantido. O custo é se ter o erro longe do código, porque ele só aparece no `commit`. Então se faz necessário usar a regra de `flush`: todo repository que escreve faz `session.flush()` antes de devolver. Assim, o erro aparece cedo, pois o `flush` traz o erro no banco para dentro da camada que sabe o que ele significa e a camada imediatamente acima (*service*) o traduz para uma exceção do domínio. Além disso, quem lê o repository não vê onde a transação fecha, pois o `commit` é invisível nas camadas e isso não tem contorno. Quando um *service* precisar de duas transações de propósito, terá que sair da convenção explicitamente.

## Como eu saberia que errei

Se um `IntegrityError` chegar ao cliente como `500`. É o sinal de um repository sem `flush` ou de que a regra não segurou.
