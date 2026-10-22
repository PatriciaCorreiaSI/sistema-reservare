# ADR 0033 — Semear a demonstração na partida do container, reiniciando as reservas de quem a visita

- **Data:** 2026-10-22
- **Situação:** aceita

## Contexto

O critério de pronto da Etapa 8 pede "dados de demonstração e credenciais de teste no README". Não há cadastro público: só o admin cria usuários. Sem admin, ninguém entra. O `criar_admin` falha de propósito na segunda execução, e o Render grátis não tem shell para rodá-lo ([ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md)). O README é público. Com a senha do admin publicada, um visitante pode apagar recursos e criar usuários. Com a de um usuário comum, pode criar e cancelar só as próprias reservas, e o pior que faz é lotar a agenda. A partida do container já roda a migration ([ADR 0030](./0030-migrar-na-partida-do-container.md)) e acontece num deploy ou quando a API acorda, depois de 15 minutos sem acesso.

## Decisão

**Semeadura:** vou escrever um comando de semeadura idempotente, rodando na partida do container, depois da migration e antes do `uvicorn`. Ele cria o que faltar: o admin, os usuários de demonstração e os recursos de exemplo.

**Reinício:** a cada partida, ele apaga as reservas dos usuários de demonstração e recria um conjunto conhecido, com datas relativas a hoje no fuso do sistema.

**Guarda:** a semeadura só age com uma variável explícita ligada (algo como `DEMONSTRACAO=1`); sem ela, não faz nada.

**Credenciais:** o README publica só as credenciais dos usuários comuns, e a senha do admin fica num segredo do Render (`sync: false`, [ADR 0031](./0031-configurar-producao-por-blueprint.md)). O `criar_admin` continua como está, para o desenvolvimento local. 

Os nomes, as quantidades e as reservas de exemplo ficam para o desenho.

## Alternativas consideradas

- **O `criar_admin` na partida, ignorando o erro** — por que descartei: ignorar o código de saída esconde todo erro, não só o "já existe". Uma falha de conexão também passaria em silêncio.

- **Semear do meu computador, uma vez, contra o Neon** — por que descartei: manual, exige a URL do banco que escreve fora do Render, e os dados não se renovam.

- **Dados dentro de uma migration** — por que descartei: mistura a forma do banco com o conteúdo, e a senha do admin iria para o repositório.

- **Publicar também a credencial do admin** — por que descartei: qualquer visitante poderia apagar recursos e criar usuários, e o front nem tem tela de admin para mostrar.

- **Não reiniciar a demonstração** — por que descartei: as reservas dos visitantes se acumulam até lotar a agenda, e quem chega depois encontra uma demonstração quebrada.

## Consequências

Os ganhos:
- A demonstração nasce sozinha no primeiro deploy;
- Quem chega depois de um tempo parado encontra os dados limpos, porque a partida acontece depois de 15 minutos sem ninguém;
- O pior que um visitante faz dura até a próxima partida;
- A senha do admin nunca vai para o repositório nem para o README;
- O "falha alto" do `criar_admin` continua valendo.

Os custos:
- Mais um passo na partida, que soma tempo à espera de cerca de 1 minuto;
- Um comando que apaga dados roda em produção, e a guarda é a única proteção;
- O Render pode reiniciar a instância grátis a qualquer momento, e um deploy no meio de uma visita também reinicia: nesses casos, o visitante perde as reservas que acabou de fazer;
- O visitante vê as reservas de outros visitantes que usam a mesma conta de demonstração;
- Duas lógicas de criar admin no código (o `criar_admin` e a semeadura).

## Como eu saberia que errei

Uma reserva de quem não é usuário de demonstração some. A demonstração aparece lotada ou sem dados, sinal de que a semeadura não rodou ou a guarda a bloqueou. Visitantes relatam perder reservas no meio da visita com frequência. A senha do admin aparece em qualquer lugar fora do painel do Render.
