# ADR 0034 — Construir a imagem da raiz do repositório, com o front e a API num Dockerfile só

- **Data:** 2026-10-26
- **Situação:** aceita

## Contexto

O [ADR 0006](./0006-local-dockerfile.md) guardou o `Dockerfile` em `backend/`, ao lado do serviço que ele construía. O argumento era um `Dockerfile` por serviço: front e back partem de bases diferentes (Node e Python) e não compartilham nada. O próprio 0006 deixou escrito o sinal para revisá-lo: algum arquivo fora de `backend/` de que o build precise. Esse sinal apareceu. O [ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md) fez a API servir o front já empacotado, para front e API ficarem no mesmo site e o cookie de refresh continuar funcionando [ADR 0023](./0023-guardar-refresh-em-cookie-httponly.md). Com isso, front e API viraram um serviço só, e a imagem precisa de `backend/` e de `frontend/`. O Docker só deixa o `COPY` alcançar o que está dentro do contexto, a pasta entregue ao construtor. Com o contexto em ``backend/`, o `frontend/` fica de fora.
Restrições: o `.dockerignore` só vale na raiz do contexto. O contexto inteiro é enviado ao construtor, inclusive o `.env` e os `node_modules` e `.venv` do Windows, que não servem no Linux da imagem.

## Decisão

Vou mover o `Dockerfile` e o `.dockerignore` para a raiz do repositório, e o contexto do build passa a ser a raiz. O `Dockerfile` constrói em duas etapas: a primeira, com Node, roda o build do front e gera o `dist/`; a segunda, com Python, é a imagem que roda e copia da primeira só o `dist/`. O `.dockerignore` deixa fora do contexto os segredos (`.env`), as dependências instaladas no Windows (`node_modules/`, `.venv/`), o `.git/` e os artefatos de build e de teste. O [ADR 0006](./0006-local-dockerfile.md) passa a "substituída pelo ADR 0034".

## Alternativas consideradas

- **`Dockerfile` em `backend/`, com contexto na raiz (`context: .` e `dockerfile: backend/Dockerfile`)** — por que descartei: um arquivo dentro de `backend/` mandaria copiar `frontend/`, e todo caminho nele seria relativo a uma psta que não é a dele. O `.dockerignore` iria para a raiz de qualquer jeito, ou viraria um `backend/Dockerfile.dockerignore`, um recurso do BuidKit que pouca gente conhece. São dois lugares para ler um build só.

- **Dois `Dockerfile` (front e API), com o `dist/` passado de uma imagem para a outra** — por que descartei: o front não roda sozinho em lugar nenhum. A imagem dele só existiria par alimentar a da API, e o build passaria a depender da ordem entre duas imagens.

- **Construir o `dist/` fora do Docker e copiar o resultado (no CI ou na máquina)** — por que descartei: a imagem passaria a depender de um passo que acontece fora dela. O Render constrói a partir do ``Dockerfile` ([ADR 0031](./0031-configurar-producao-por-blueprint.md)), e o `dist/` nem está no repositório.

## Consequências

Os ganhos:
- Uma imagem só, construída por um comando só, a partir do repositório limpo.
- Nada do Node vai par aa imagem que roda: só a pasta de arquivos estáticos.
- O `npm run build` roda o `tsc`, então um erro de tipo no front quebra a imagem antes do deploy.
- O `.dockerignore` na raiz cobre os dois lados.

Os custos:
- O compose e o `render.yaml` apontam o contexto para a raiz.
- O contexto enviado é o repositório inteiro, e o `.dockerignore` vira proteção, não só otimização: esquecer uma linha manda o `.env` ao construtor, ou faz o `node_modules` do Windows cobrir o do Linux.
- A construção da imagem fica mais lenta, porque inclui o `npm ci` e o build do front. o cache de camadas compensa quando só o código muda.
- O `Dockerfile` passa a conhecer a estrutura das duas pastas: renomear `frontend/` ou `backend/` quebra o build.

Mudar de ideia é barato: se o front voltar a ser um serviço próprio, a primeira etapa vira o `Dockerfile` dele.

## Como eu saberia que errei

O front volta a precisar de um serviço próprio (num host de estáticos, por exemplo), e a etapa de Node passa a existir só por costume. O build fica lento a ponto de atrasar o deploy, sinal de que o cache não está funcionando. Algo que o `.dockerignore` deveria barrar aparecer dentro da imagem ou no contexto: o `.env`, ou um `node_modules` de Windows.
