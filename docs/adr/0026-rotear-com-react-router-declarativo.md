# ADR 0026 — Rotear com React Router declarativo

- **Data:** 2026-10-06
- **Situação:** aceita

## Contexto

O front é um SPA (single-page application): um HTML só, e o JavaScript troca a tela sem pedir página nova. Sem roteador, a URL não acompanha a tela. F5 e "voltar" perdem o lugar, e não há link para "a disponibilidade da sala 3 no dia 10". E a guarda das rotas protegidas depois do F5 (memória vazia, cookie do [ADR 0023](0023-guardar-refresh-em-cookie-httponly.md) cheio) precisa de um lugar para morar: o access token vive só na memória [ADR 0013](0013-transportar-token-no-cabecalho-authorization.md) e some no F5; o refresh sobrevive no cookie ([ADR 0023](0023-guardar-refresh-em-cookie-httponly.md)). Antes de renderizar qualquer tela protegida, o front chama o refresh e só então decide entre a tela e o `/login`. Isso é uma rota de layout, que embrulha as protegidas e faz a guarda uma vez, como o `obter_usuario_atual` no backend.

## Decisão

Escolhi usar o React Router v8, modo declarativo: URL → componente, URL como estado, navegação; nenhum *loader*. Estado de servidor fica inteiro no TanStack Query (hooks à mão, [ADR 0025](0025-gerar-tipos-do-front-pelo-openapi.md)).

## Alternativas consideradas

- **React Router modo *framework*** — por que descartei: assume build e servidor; o [ADR 0024](0024-alcancar-api-pelo-proxy-do-vite.md) já decidiu SPA atrás do proxy.

- **React Router modo *data*** — por que descartei: loaders disputam com o TanStack Query a pergunta "de onde vem o dado".

- **TanStack Router** — por que descartei: URL tipada de ponta a ponta, coerente com o [ADR 0025](0025-gerar-tipos-do-front-pelo-openapi.md), mas 2,5-5× menos mercado e mais conceitos. E o padrão canônico também empurra o carregamento para o roteador.

## Consequências

O ganho: é a biblioteca padrão do mercado. Uma ferramenta, um papel: o roteador mapeia URL; o TanStack Query é dono do estado de servidor. O conceito central da etapa no ROADMAP (estado de servidor × estado de interface) fica nítido, sem *loader* nenhum disputando com os hooks que serão escritos.
O custo: `useParams()` devolve `string | undefined`, link digitado errado só quebra ao clicar, `?dia=` chega como texto. Interpretação de `id` e `dia` na borda, à mão. A URL é entrada do usuário, como o `Query(ge=1, le=100)` do `limite`.
O custo de mudar de ideia é baixo. São quatro ou cinco rotas e dois parâmetros; portar para o TanStack é reescrever a árvore de rotas, não as telas nem os hooks.

## Como eu saberia que errei

Se as rotas se multiplicarem e aparecerem bugs de link digitado errado, ou se a interpretação de parâmetros se repetir em 3 lugares: aí a tipagem da URL vale o preço, e o TanStack Router é a resposta (exercício no fim da etapa, como o do `@hey-api` no [ADR 0025](0025-gerar-tipos-do-front-pelo-openapi.md)).
