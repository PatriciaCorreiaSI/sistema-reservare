# 0006 — Guardar ```Dockerfile``` em ```backend/```

- **Data:** 2026-09-02
- **Situação:** aceita

## Contexto

Criação de arquivo ```Dockerfile``` exige decisão de arquitetura: definir seu local de origem. Isso terá consequência nas demais etapas, a saber, a Etapa 7 quando for criado o ```frontend``` do projeto. A imagem da API só precisa enxergar o que está no diretório ```backend/```.

## Decisão

Escolhi criar o ```Dockerfile``` no diretório ```backend/``` onde está o serviço que será buildado. 

## Alternativas consideradas

- **```Dockerfile``` na raiz do projeto** — por que descartei: o padrão é um ```Dockerfile``` por serviço, ao lado do serviço. Portanto, dentro do monorepo não faz sentido criá-lo na raiz do repo, uma vez que futuramente teremos o diretório ```frontend```. ```Backend``` e ```frontend``` possuem imagens partindo de bases diferentes (back: ```python 3.14``` e front: ```node```). Desse modo, um único Dockerfile na raiz do repo não serviria aos dois serviços ao mesmo tempo. 

## Consequências

O custo é a criação de dois arquivos ```Dockerfile```, cada um ao lado do serviço que ele atende respectivamente, a saber ```backend``` e ```frontend```. O ganho é seguir o padrão do mercado e criar um ```Dockerfile``` por serviço, uma vez que ```back``` e ```front``` não compartilham nada entre si que justifique um único ```Dockerfile``` para ambos os serviços dentro do monorepo.

## Como eu saberia que errei

Se ao criar o ```Dockerfile``` no diretório ```backend/``` existir algum arquivo na raiz do repo que o build precise ler para rodar o serviço. Consequentemente, ele nunca o encontraria.