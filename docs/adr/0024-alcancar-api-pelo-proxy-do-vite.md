# ADR 0024 — Alcançar a API pelo proxy do Vite, sob o prefixo `/api`

- **Data:** 2026-10-05
- **Situação:** aceita

## Contexto

Em desenvolvimento, o front roda no servidor do Vite (`:5173`) e a API no Uvicorn (`:8000`). São origens diferentes, porque a porta conta. O navegador bloqueia o JavaScript de ler respostas de outra origem, a menos que o servidor autorize. Essa autorização é o CORS. O cookie do refresh ([ADR 0023](0023-guardar-refresh-em-cookie-httponly.md)) olha o site, não a origem: chega à API mesmo de outra porta. O problema a resolver é ler a resposta. Front e API também disputam os mesmos caminhos: a página `/reservas` do front e a rota `/reservas` da API. Num F5, o pedido precisa chegar ao lugar certo.

## Decisão

Escolhi fazer o front chamar a API pela própria origem: o servidor do Vite repassa a outra porta todo pedido que começa com `/api` (`server.proxy`). O navegador só enxerga `:5173`, então não existe CORS. O prefixo mora no backend: todas as rotas da API passam a viver sob `/api` (`/api/auth/login`, `/api/recursos`...). O caminho que o navegador vê é o mesmo que a API conhece, sem reescrita no meio. É o que faz o template oficial *full-stack-fastapi-template*.
O `/health` fica fora do prefixo: quem o consulta é o Docker, não o front. O proxy aponta para `http://127.0.0.1:8000`, nunca `localhost`. É a mesma armadilha do `DB_HOST`: o Node resolve `localhost` para `::1` (IPv6) primeiro, e a API escuta em IPv4. Em produção (Etapa 8), um servidor na frente faz o mesmo papel: `/api` vai para a API, e o resto para os arquivos do front.

## Alternativas consideradas

- **CORS (`CORSMiddleware` com `allow_credentials=True`, e `credentials: "include"` no front)** — por que descartei: funciona, mas acrescenta peças: a lista de origens permitidas por ambiente; o *preflight*, um pedido de verificação que o navegador faz antes; lembrar das credenciais em cada `fetch`. O erro de qualquer uma dessas peças só aparece no navegador, nunca no `pytest`.

- **Prefixo só no proxy, que corta o `/api` antes de repassar** — por que descartei: a API não mudaria, mas o cookie é avaliado pelo caminho que o navegador vê (`/api/auth`), e a API teria de gravar um `Path` que ela não conhece. É uma configuração que se desalinha calada: o cookie simplesmente não é enviado.

- **Sem prefixo, com o proxy repassando rota por rota** — por que descartei: a página `/reservas` e a rota `/reservas` colidiriam: um F5 na página traria JSON.

- **Prefixo com versão (`/api/v1`)** — por que descartei: a versão serve quando clientes antigos precisam continuar funcionando enquanto a API muda. Aqui há um cliente só, que muda junto com a API. Acrescentar a versão depois é localizado.

## Consequências

O ganho: sem CORS, sem preflight e sem credenciais para lembrar em cada chamada; o mesmo caminho em todo lugar: navegador, API, testes e produção; o cookie do [ADR 0023](0023-guardar-refresh-em-cookie-httponly.md) funciona sem configuração extra.
O custo:
- No backend: todos os routers passam a ser incluídos com `prefix="/api"`
- Nos testes: o `TestClient` ganha `base_url` com `/api` no conftest.py. O teste de concorrência tem o próprio cliente e precisa da mesma mudança: são 2 lugares, que precisam andar juntos.
- Nos documentos e clientes: o `docs/api.md`, o `curl` e o `/docs` passam a usar `/api/...`
- Na produção: a Etapa 8 passa a exigir um servidor na frente, ou uma plataforma que roteie por caminho. Front e API soltos, cada um no seu endereço, deixam de ser opção sem reabrir esta decisão.

Custo de mudar de ideia: ir para CORS é localizado, com o middleware no backend e as credenciais no front. O prefixo pode ficar mesmo assim.

## Como eu saberia que errei

Se aparecer erro de CORS no console do navegador: algum código do front está chamando `http://127.0.0.1:8000` direto, em vez de `/api`, e o proxy foi contornado. Se o proxy responder `ECONNREFUSED` ou ficar pendurado: ele está apontando para `localhost`. Se a produção precisar servir front e API em sites diferentes: esta decisão e o `SameSite=Strict` do [ADR 0023](0023-guardar-refresh-em-cookie-httponly.md) caem juntos.
