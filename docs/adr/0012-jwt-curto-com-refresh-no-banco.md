# ADR 0012 — Usar token JWT curto com refresh no banco

- **Data:** 2026-09-16
- **Situação:** aceita

## Contexto

O HTTP não tem memória. Após efetuar login, o cliente precisa provar quem é ao servidor em cada nova requisição que realiza. Então o servidor entrega ao cliente um *token* para ele apresentar nas novas requisições para provar sua identidade. O logout precisa invalidar essa prova. Existem duas famílias de token a serem utilizadas para essa autenticação: token opaco e token autocontido (JWT).

## Decisão

Escolhi utilizar **token autocontido JSON Web Token (JWT)** pelo desafio do exercício e o aprendizado. Ele é o padrão que o mercado atual adota para resolver desafios de **escalabilidade** e **desacoplamento**. Com JWT, o servidor escreve os dados dentro do próprio token `{"sub": 42, "papel": "admin", "exp": 1758000000}` e assina com chave secreta, o que impede do cliente editar seu conteúdo. Com JWT quem verifica só precisa da chave secreta para conferir a assinatura; verifica localmente, em microssegundos, sem rede. O *access token* é o JWT, de vida curta (15 minutos); o refresh token é opaco, guardado no banco, e é ele que o logout apaga.

## Alternativas consideradas

- **Token opaco (sessão no servidor)** — por que descartei: com essa opção, o servidor gera uma chave de busca composta por uma sequência aleatória longa, guarda no banco numa tabela (`token → id_usuario, criado_em, expira_em`) e entrega a sequência ao cliente. No logout essa linha é deletada da tabela. Na requisição seguinte, a busca não encontra nada. O token morre de verdade no mesmo instante. Porém isso custa uma consulta a mais em toda requisição autenticada. A cada requisição, o servidor consulta a tabela para ver se o token existe, se está válido e a quem pertence. A API deste projeto é síncrona. Nesse sentido, optar pelo token opaco seria a escolha técnica mais simples e com garantia mais forte. Escolho JWT para exercitar o padrão que o mercado usa e ser capaz de explicar quando ele é e quando não é a resposta.

- **JWT + lista de revogados** — por que descartei: o servidor guarda no banco os tokens que fizeram logout e consulta a lista a cada requisição. Garante invalidação instantânea. Mas ao custo de exigir consulta ao banco a cada requisição + a complexidade da assinatura e verificação JWT perdendo o único ganho do JWT que é eliminar esta consulta ao banco.


## Consequências

O ganho é que o servidor verifica o token sem consultar nada. Libera essa consulta ao banco a cada nova requisição.  Confere a assinatura com a chave, lê o `exp` (tempo de expiração) e pronto. Sem consultas à tabela e nenhuma busca.
O custo é que o JWT é *stateless*. Portanto, o servidor não guarda estado sobre quem está logado e assim não há o que apagar no logout. O token continua válido até a sua expiração, esteja o usuário deslogado ou não. Custará a este projeto duas rotas a mais (`/auth/refresh`, `/auth/logout`); dois formatos de token e o cliente precisará saber renovar o token; **access curto + refresh no banco**, com uma janela de 15 minutos para obter logout seguro. O *refresh token* é opaco, guardado no banco, de vida longa (dias). Quando o *access* expira, o cliente apresenta o *refresh* numa rota `/auth/refresh` e recebe um *access* novo. Logout apaga o *refresh* e o usuário não consegue mais obter um *access* novo. Porém o *access* que ele já possuía continua válido até expirar. Garantir um access curto fará com que este token fique válido pelo menor tempo possível após logout.

## Como eu saberia que errei

Se o admin desativa um usuário e ele continua operando no sistema por até 15 minutos com o access que já tem. Se algum dia a exigência virar "desativação no instante", **token opaco** ou **lista de revogados** se tornam a solução melhor. Se eu mudar de ideia, alterar para a escolha de **token opaco** custa pouco. A tabela de refresh já é uma tabela de sessão; bastaria abandonar o *access* e consultá-la a cada requisição.
