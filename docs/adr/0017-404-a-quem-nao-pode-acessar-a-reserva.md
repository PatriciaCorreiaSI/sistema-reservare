# ADR 0017 — Responder `404` a quem não pode acessar a reserva

- **Data:** 2026-09-24
- **Situação:** aceita

## Contexto

IDOR (*Insecure Direct Object Reference*), que a OWASP hoje chama de BOLA (*Broken Object Level Authorization*), é a API entregar ou alterar um objeto só porque alguém pediu pelo `id`, sem conferir se ele tem direito ao objeto. É o primeiro risco da OWASP API Top 10 (edição de 2023, a vigente), e a sua família, *Broken Access Control*, segue em primeiro na OWASP Top 10:2025 de aplicações web. É também metade do critério de pronto da Etapa 4. No Reservare, o cenário é este:

```
    Ana (token válido) → GET /reservas/42
    A reserva 42 é do João.
```

O token da Ana responde "quem é você". Ele não responde "esta reserva é sua". Essa segunda pergunta é a autorização por objeto, e é ela que falta decidir. Quem pode o quê já está decidido: o dono e o admin cancelam ([ADR 0002](0002-cancelamento-em-colunas.md)). Pela mesma lógica, os dois leem. O que falta é o que responder a quem não pode, e onde fazer essa verificação. E o cancelamento do [ADR 0016](0016-cancelar-pela-acao-com-update-condicional.md) precisa de uma ordem: o `WHERE` do `UPDATE` confere o estado da reserva, não de quem ela é.


## Decisão

Escolhi responder `404` a quem não pode: para quem pergunta, a reserva alheia e a inexistente são indistinguíveis. A RFC 9110 (especificação do HTTP) prevê isso com todas as letras, dizendo que o servidor que quiser esconder a existência de um recurso proibido pode responder `404`. O `403` continua no projeto para outra pergunta, a da rota (o `exigir_admin`: "você tem o papel para usar isto?"); a pergunta sobre o objeto ("isto é seu?") responde `404`. 

A verificação mora numa função de política no service (ex:`garantir_acesso(reserva, usuario_atual)`), que aceita o dono ou o admin e, para qualquer outro, levanta a mesma exceção de "não encontrada". Assim, "não existe" e "não é sua" saem idênticos, por construção. A leitura e o cancelamento usam a mesma função. A listagem não usa: ela filtra (o usuário recebe as dele, o admin recebe todas).

O cancelamento passa a ser: ler → `garantir_acesso` (se não pode, `404`) → `UPDATE` condicional → 0 linhas = `409`. Ler antes não reabre a janela de corrida que o [ADR 0016](0016-cancelar-pela-acao-com-update-condicional.md) fechou: só se corre risco verificando antes aquilo que pode mudar até a gravação, e o dono de uma reserva nunca muda. O status, que pode mudar, continua no `WHERE` do `UPDATE`.

## Alternativas consideradas

- **Responder `403`** — por que descartei: vaza a existência ("existe, mas não é sua"). Os `id` são sequenciais: quem pergunta testa `/reservas/1`, `/2`, `/3` ... e, pela diferença entre `403` e `404`, descobre quantas reservas existem, ou seja, o volume de uso do sistema. Esse ataque se chama **enumeração**.

- **Verificar na consulta (`WHERE id_reserva = :id AND id_usuario = :quem`)** — por que descartei: a consulta nunca devolve o que não é seu. Mas o admin não tem esse filtro, então o repository passaria a conhecer papéis, que são regra de negócio.

- **Pôr o dono no `WHERE` do `UPDATE` (`AND (id_usuario = :quem OR :eh_admin)`)** — por que descartei: tudo num único comando. Mas é papel dentro da query de novo (a alternativa anterior), e a regra ficaria escrita em dois lugares.


## Consequências

O ganho: não vaza nada. Para quem pergunta, a reserva alheia e a inexistente são indistinguíveis. O custo é o suporte: uma reclamação de "a minha reserva sumiu" exige olhar o log, porque a resposta não diz qual dos dois casos aconteceu. Outro custo é na verificação: uma rota nova precisa lembrar de chamar a função, e o teste de IDOR é quem pega o esquecimento.

## Como eu saberia que errei

Surgir uma regra em que "existe, mas não é sua" seja informação útil ao usuário, como reserva compartilhada ou convidados que precisam ver a reserva. Ou o suporte passar a gastar tempo demais distinguindo, pelo log, reserva inexistente de reserva alheia.
