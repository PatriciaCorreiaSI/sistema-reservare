# ADR 0013 — Transportar o token no cabeçalho `Authorization: Bearer <token>`

- **Data:** 2026-09-17
- **Situação:** aceita

## Contexto

O HTTP é sem estado. Não lembra a identidade de quem fez login de uma vez só. O cliente precisa provar sua identidade em cada requisição. O login recebe usuário e senha, autentica a identidade do cliente e gera um token. Esse token que será utilizado para autenticar o cliente nas próximas requisições. Então, o cliente precisa guardar esse token em algum lugar e saber como transportá-lo para entrar em cada requisição. Há tipos diferentes de transporte para o token. Cada transporte é forte contra um ataque e fraco contra outro. Este projeto possui algumas restrições: o frontend tem origem diferente da API (`:5173 × :8000`), `/docs` do FastAPI, suíte de testes com `TestClient`, API síncrona que outros clientes (`curl`, scripts) vão consumir.

## Decisão

Escolhi usar o transporte pelo cabeçalho `Authorization: Bearer <token>`. O JavaScript do frontend recebe o token no login, guarda em uma variável na memória e o anexa à mão em cada requisição.

## Alternativas consideradas

- **cookie `httpOnly`** — por que descartei: este projeto possui origens diferentes em desenvolvimento. `localhost:5173` e `localhost:8000` são sites diferentes para o navegador, e cookie entre sites exige CORS com credenciais, `SameSite=None` e `Secure` (que exige HTTPS). Além disso, em testes, exige que o `TestClient` guarde cookies como um navegador, mas o teste do CSRF/`SameSite` não é exercitável nele. É forte diante de um ataque XSS, porque mesmo que um script malicioso dispare requisições enquanto o usuário estiver com a aba aberta, ele não consegue levar o token embora, pois `httpOnly` impede a leitura do cookie. Mas sozinho é frágil diante de um ataque CSRF. Precisa de um atributo a mais, o `SameSite`: `Strict` ou `Lax`, que faz o navegador não anexar o cookie em requisições que partem de outro site. Mesmo essa força contra ataques XSS não foi suficiente para escolhê-lo devido ao custo das origens diferentes.

- **híbrido** — por que descartei: com access no cabeçalho (guardado só em memória, some ao fechar a aba) e refresh num cookie `httpOnly` restrito ao caminho `/auth/refresh`. Protege o token de vida longa contra ataques XSS e limita ataques CSRF a uma rota só. Porém são mais peças para implementar.

## Consequências

O ganho é usar o padrão de APIs do mercado que funciona para navegador, `curl`, scripts, app mobile. O `/docs` do FastAPI já vem com o botão *Authorize* para `Bearer`; os testes já o suportam de graça. Além disso, é um transporte imune a ataques CSRF, pois o site malicioso não tem o token para colocar no cabeçalho. E quem não tem o token não consegue mandá-lo. O custo é que o transporte pelo cabeçalho deixa o token visível ao JavaScript e, assim, vulnerável a ataques XSS. Um script malicioso lê o token no lugar onde o JS o guardou e o envia ao atacante. O token roubado vale por 15 minutos, mesmo longe da sua página. Mas o refresh também vive na memória do JavaScript e vale dias, podendo-se renovar o access indefinidamente até a expiração do refresh. Isso exigiria uma decisão sobre rotacionar o refresh a cada uso. Assim, se um refresh antigo for reapresentado, o servidor detecta o roubo e invalida a família toda. A defesa contra XSS vira responsabilidade explícita do frontend: guardar só em memória, nunca em `localStorage`. Mudar de ideia exigiria uma alteração localizada no backend e espalhada nos consumidores.

## Como eu saberia que errei

Se ao revisar o código do frontend, encontrasse o token em `localStorage`, mostrando que o frontend não cumpriu o compromisso da Decisão. Ou um requisito novo de sessão compartilhada entre subdomínios ou de renderização no servidor, onde o cookie é o transporte natural.

