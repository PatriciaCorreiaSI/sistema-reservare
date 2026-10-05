# ADR 0023 — Guardar refresh token num cookie httpOnly

- **Data:** 2026-10-05
- **Situação:** aceita

## Contexto

O [ADR 0013](0013-transportar-token-no-cabecalho-authorization.md) decidiu que os dois tokens viajam fora de cookie: o access no cabeçalho `Authorization`, o refresh no corpo, e o front guarda os dois só em memória, nunca em `localStorage`. A memória não sobrevive ao recarregar a página: o navegador descarta todo o JavaScript e suas variáveis. Com isso, F5, uma aba nova ou fechar e reabrir o navegador obrigam a fazer o login de novo. Só ficou visível agora, porque é na Etapa 7 que o front existe. Os dois tokens têm riscos diferentes: o access vale 15 minutos, e o refreh vale 7 dias e renova o access; Um XSS que roube o refreh leva dias de acesso, não minutos. As restrições são as de antes:

- front e API em origens diferentes em desenvolvimento (`:5173` × `:8000`);
- os testes usam o `TestClient`;
- outros clientes, como `curl` e scripts, também consomem a API.

## Decisão

Escolhi guardar o refresh num cookie `HttpOnly; Secure; SameSite=Strict; Path=/api/auth`, com `Max-Age` igual ao `REFRESH_DIAS`. O access continua como no [ADR 0013](0013-transportar-token-no-cabecalho-authorization.md): no corpo da resposta, na memória do front, enviado pelo cabeçalho `Authorization`.
O ciclo de vida:

- o login grava o cookie;
- o refresh lê o cookie, rotaciona e grava um cookie novo;
- o logout lê o cookie, revoga no banco e apaga o cookie (`Max-Age=0`).

O refresh deixa de aparecer no corpo das respostas e das requisições. Se aparecesse, o JavaScript o leria e o ganho acabaria. No F5, o front chama `/auth/refresh` ao carregar; o navegador manda o cookie sozinho, e a sessão volta sem pedir a senha. O porquê de cada atributo, em uma linha cada:
- `HttpOnly`: o JavaScript não lê o cookie;
- `Secure`: só trafega por HTTPS; o `localhost` é exceção dos navegadores;
- `SameSite=Strict`: o cookie nunca vai em pedido que parte de outro site, que é a defesa contra CSRF;
- `Path=/api/auth`: o cookie só vai às rotas de autenticação. Não pode ser `/api/auth/refresh`, porque o logout precisa ler o cookie. O prefixo `/api` vem do [ADR 0024](0024-alcancar-api-pelo-proxy-do-vite.md).

## Alternativas consideradas

- **Aceitar o logout no F5** — por que descartei: nada muda no back-end, mas recarregar a página pede a senha de novo. É uma experiência que só se justifica em sistemas de alto risco, como bancos, e não é o caso de um sistema de reservas.

- **Refresh em `localStorage`** — por que descartei: sobrevive ao F5 e é o mais simples, mas qualquer script da página o lê. É exatamente o risco que o [ADR 0013](0013-transportar-token-no-cabecalho-authorization.md) proibiu, e com o token de vida longa.

- **BFF *(Backend for Frontend)*** — por que descartei: é o topo da recomendação do IETF para aplicações de navegador *(OAuth 2.0 for Browser-Based Applications)*: nenhum token chega ao navegador. só um cookie de sessão. Mas é uma peça de infraestrutura a mais para construir, testar e publicar, e o ganho sobre a escolha é pequeno neste projeto. Fica no backlog.


## Consequências

O ganho: a sessão sobrevive ao F5, e o token de vida longa fica fora do alcance do JavaScript; um XSS ainda pode usar o access enquanto a aba está aberta, mas não consegue levar o refreh embora. Fica fechado o risco que o [ADR 0013](0013-transportar-token-no-cabecalho-authorization.md) tinha deixado aberto.
O custo: 
- No backend: as 3 rotas de `/auth` mudam; o schema de refresh e de logout perde o campo do corpo; a extração do refresh passa a ler cookie;
- Nos testes: os de `test_auth.py` que leem `resposta.json()["refresh_token"]` mudam. O `TestClient` guarda cookies como um navegador.
- Nos outros clientes: o `curl` e os scripts continuam funcionando, mas precisam guardar cookies (`curl -c` e `-b`). Antes era só copiar um campo do JSON.
- Na arquitetura: com `SameSite=Strict`, front e API precisam estar no mesmo site - mesmo domínio, mesmo que em portas ou subdomínios diferentes. `localhost:5173` e `localhost:8000` já são o mesmo site, então o cookie chega à API em desenvolvimento. Como o front alcança a API (proxy ou CORS) fica para o próximo ADR. Em produção, os dois (front e API) precisam ficar sob o mesmo domínio (Etapa 8).

O custo de mudar de ideia: voltar ao refresh no corpo é localizado, as mesmas 3 rotas. Ir para o BFF reaproveitaria tudo isto, porque o cookie passaria a ser de sessão e os tokens morariam no servidor intermediário.

## Como eu saberia que errei

Se o refresh aparecer em algum JSON, no `localStorage` ou em alguma variável do front: o compromisso da Decisão foi quebrado. Se o front e a API precisarem ficar em sites diferentes em produção, como `reservare.com` e `reservare-api.com`: o `SameSite=Strict` deixaria de enviar o cookie, e a escolha teria de ser revista: CORS com credenciais e `SameSite=None`, ou o BFF. Se o F5 continuar pedindo login: o cookie não está chegando, exigindo olhar primeiro o `Path` e o site.
