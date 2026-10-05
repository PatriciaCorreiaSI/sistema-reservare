# ADR 0025 — Gerar os tipos do front a partir do OpenAPI

- **Data:** 2026-10-05
- **Situação:** aceita

## Contexto

O front, em TypeScript, precisa conhecer o formato de cada rota da API: caminho, método, corpo, resposta e erros. Sem isso, um campo com nome errado (`reserva.inicoi`) vira `undefined` na tela, e não erro de compilação. O FastAPI já publica esse formato: o OpenAPI (`openapi.json`), gerado dos schemas Pydantic. É o contrato da API, e a fonte da verdade é o backend.
Tipos escritos à mão no front seriam uma cópia do contrato em outra linguagem, que se desalinha calada quando um schema muda. É o mesmo risco das cópias do ciclo do `obter_sessao`. A Etapa 7 tem o TanStack Query como conceito a aprender (cache, revalidação, nova tentativa).

## Decisão

Escolhi gerar só os tipos com o `openapi-typescript` e fazer as chamadas com o `openapi-fetch`, um `fetch` pequeno que confere caminho, corpo e resposta por esses tipos. Os hooks do TanStack Query são escritos à mão, sobre o `openapi-fetch`. O contrato é exportado do próprio app (`app.openapi()`) para um arquivo, sem precisar da API no ar, e o gerador lê esse arquivo. O arquivo de tipos gerado entra no repositório, para o front compilar sem o backend rodando. É o mesmo arranjo do template oficial *full-stack-fastapi-template*, que exporta o `openapi.json` por um script antes de gerar. Nenhum arquivo gerado se edita à mão: mudou a API, gera de novo.

## Alternativas consideradas

- **Tipos escritos à mão** — por que descartei: não acrescenta nenhuma ferramenta, mas cada schema passa a existir duas vezes, em Python e em TypeScript, e nada avisa quando as duas versões divergirem.

- **`@hey-api/openapi-ts`** — por que descartei: gera os tipos, uma função por rota e, opcionalmente, os hooks do TanStack Query. É a escolha do template oficial do FastAPI. Mas gera justamente a camada que a Etapa 7 quer que eu aprenda, e eu não saberia revisar o que ele produz sem antes ter escrito à mão. É a lição do `--autogenerate` do Alembic.

- **Orval** — por que descartei: gera tipos, hooks, schemas `zod` e mocks: faz sentido num front grande, com muitas rotas. Aqui seria mais código gerado do que entendido.

## Consequências

O ganho: um schema mudado no backend vira erro de compilação no front, não `undefined` em produção; o código gerado se lê como uma lista de tipos; a camada de chamadas é minha, e cada linha se explica.
O custo: mais código escrito à mão (um hook por consulta e uma mutação por escrita); um passo a mais quando a API muda (exportar e gerar) e um script para isso; o arquivo gerado no repositório pode ficar velho se alguém esquecer de gerar de novo. A defesa é o CI exportar, gerar e falhar se o resultado diferir do que está no repositório, como já faz o `alembic check`.
O custo de mudar de ideia é localizado. Os tipos ficam, e a troca para o `@hey-api` mudaria só a camada de hooks. No fim da Etapa 7, gerar os hooks com o `@hey-api` num rascunho e comparar com os meus fica como exercício.

## Como eu saberia que errei

Se aparecer um tipo de resposta da API escrito à mão no front, ou um `as` forçando um tipo: o contrato foi contornado. Se o arquivo gerado for editado à mão. Se os hooks escritos à mão começarem a se repetir quase iguais, rota após rota, a ponto de copiar e colar: aí o gerador passa a se pagar.
