# ADR 0005 — Usar versão Python 3.14 ao invés da versão Python 3.12

- **Data:** 2026-09-01
- **Situação:** aceita

## Contexto

A arquitetura inicial do projeto sugeriu o uso da versão python 3.12. Porém já temos a versão 3.14 disponível e estável.

## Decisão

Eu, como autora do projeto, optei por escolher usar a versão Python 3.14 por ser a mais atual e já estar acostumada a utilizá-la em outros projetos. E porque agora é o momento mais barato de errar, por não existir nenhuma linha de código ainda escrita.

## Alternativas consideradas

- **Python 3.12 com maturidade máxima do ecossistema** — por que descartei: pelo custo comsético de estar atrás da versão mais atual. A versão 3.14 já é estável.
- **Python 3.13** — por que descartei: é o meio termo do caminho. Estaria menos maturada do que a versão 3.12 e ainda não seria a versão mais atual.

## Consequências

O risco é algum pacote com extensão em C ainda não publicar _wheel_ para a versão Python 3.14. Isso pode fazer com que o Windows tente compilar do zero e eu precise de um compilador C. Porém é um risco baixo, embora não ausente. O ganho é ter no projeto uma versão mais atual que já tem quase 1 ano de uso no mercado e já se mostrar estável.

## Como eu saberia que errei

Se o Roadmap e o Dockerfile divergirem da versão utilizada ou se um pacote da stack não tiver _wheel_ para 3.14 e exigir compilação. Então terei que voltar ao custo de _uv python pin 3.12_ e trocar uma linha do _Dockerfile_.
