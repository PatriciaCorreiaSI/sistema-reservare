# ADR 0009 — Usar API síncrona

- **Data:** 2026-09-09
- **Situação:** aceita

## Contexto

Precisamos definir qual tipo de API usar: síncrona ou assíncrona. O FastAPI aceita `def` e `async def`. Numa rota `def` ele roda a função num *threadpool*: o SQLAlchemy síncrono funciona e o servidor continua atendendo outras requisições. Numa rota `async def`, não se pode bloquear: toda chamada ao banco precisa de um `await`, com engine e sessão assíncronas.

## Decisão

Escolhi usar a API síncrona com rota `def`. Na migração utilizarei o template `alembic init migrations` que gera um `env.py` síncrono. 

## Alternativas consideradas

- **API assíncrona com rota `async def`** — por que descartei: quem revisar este repositório pode esperar `async` e notará sua ausência. Embora a API assíncrona seja muito utilizada no mercado e traga o ganho de não gastar uma thread por requisição parada, não o adotamos porque o coração do projeto **Reservare** é provar que o banco recusa duas reservas sobrepostas sob concorrência real. O teste precisa de duas transações ao mesmo tempo e duas conexões diferentes. Com threads isso é explícito e verificável: duas threads, duas conexões, um ponto de sincronização entre elas. Além disso, o Alembic executa migration sempre de forma síncrona. Escolher `async def` adicionaria um invólucro a mais. Uma decisão pesada por escrito lê melhor que um async por inércia.

## Consequências

O ganho com a API síncrona é que o teste de concorrência fica mais direto e demonstrável. Além disso, ela usa menos peças móveis no projeto. A perda é não utilizar o `async` que resolve exatamente a limitação do threadpool que o FastAPI possui. Com a API síncrona, cada requisição que chega trava uma thread inteira do servidor. Caso existam muitas conexões simultâneas esperando I/O, o threadpool enche. As requisições passam a esperar na fila. O custo de mudar de ideia depois é reescrever services e repositories inteiros. Decidimos que os repositories usarão `selectinload` explícito desde o começo para que a conversão futura para async seja mecânica.


## Como eu saberia que errei

Se houver muitas requisições simultâneas atingindo rapidamente o teto de threads do FastAPI e a latência subir. A medição de carga mostrará o threadpool saturado e o gargalo serão threads paradas esperando o banco de dados responder.