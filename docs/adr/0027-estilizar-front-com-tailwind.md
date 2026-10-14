# ADR 0027 — Estilizar o frontend com Tailwind

- **Data:** 2026-10-14
- **Situação:** aceita

## Contexto

As telas funcionam, mas o visual é o CSS que veio no modelo do Vite, com a cor roxa e classes que nem usamos (`.counter`). Num portfólio, isso esconde o trabalho que está por trás. As restrições do projeto são:
- **Regra 2**: nenhuma linha entra sem que eu consiga explicar;
- **Acessibilidade**: contraste, foco visível, e manter o `<dialog>`, os rótulos e as regiões vivas que já existem;
- **Ferramentas do repositório**: o `tsc`, o ESLint, o Prettier e o `pre-commit` precisam continuar passando;
- **Playwright**: ele vem depois e procura os elementos por papel e por nome, nunca por classe.

## Decisão

Escolhi usar o Tailwind CSS v4, pelo plugin `@tailwindcss/vite`, com as variáveis de design (cores, fontes, espaços) num bloco `@theme` do `index.css`, e o `prettier-plugin-tailwindcss` para ordenar as classes. Esse plugin é o oficial, da própria Tailwind Labs. Sem ele, cada pessoa escreve as classes numa ordem, e o `git diff` fica cheio de mudanças que não mudam nada.

## Alternativas consideradas

- **CSS puro** — por que descartei: as classes valem para a página inteira, sem escopo, e o arquivo cresce sem estrutura.
- **CSS Modules** — por que descartei: resolveria o escopo, mas todo o trabalho de desenho continua do zero, e o mercado está migrando para longe dele.
- **Tailwind com shadcn/ui** — por que descartei: copia para o repositório dezenas de arquivos que não escrevi (regra 2) e trocaria o `<dialog>` nativo pelo do Radix.
- **MUI ou Mantine** — por que descartei: visual com cara de biblioteca e pacote pesado, e o portfólio mostraria a biblioteca, não meu projeto.

## Consequências

O ganho: é o padrão do mercado, não roda nada no navegador (gera um CSS estático no build), o estilo fica junto da marcação, e a escala de espaços e cores já vem pronta. O custo: o acoplamento é alto: as classes ficam espalhadas pela marcação de todos os componentes, e sair do Tailwind significa reescrever a marcação inteira; as listas de classes ficam longas; o Preflight (o *reset* do Tailwind) zera os estilos do navegador, então as telas ficam mais cruas até receberem as classes: o `<h1>` passa a ter o tamanho do texto normal, os botões perdem a borda, as listas perdem os marcadores.
Uma armadilha de acessibilidade que vem com o Preflight: o Safari, com o VoiceOver, deixa de anunciar como lista um `<ul>` sem marcador. A documentação do Tailwind recomenda acrescentar `role="list"` nesses casos. Isso afeta as duas listas de minhas reservas.

## Como eu saberia que errei

- A mesma combinação longa de classes aparece copiada em vários componentes. Esse é o sinal para extrair um componente React, e não para espalhar `@apply`;
- Muitos valores arbitrários (`w-[437px]`, `text-[#3a7]`) furando a escala do `@theme`, o que mostra que a escala não serve;
- Uma troca de versão principal que exige reescrever a configuração, como já aconteceu da v3 para a v4, quando a configuração saiu do JavaScript e foi para CSS.
