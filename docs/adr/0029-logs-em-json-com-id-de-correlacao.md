# ADR 0029 — Registrar logs em JSON com um ID de correlação por pedido

- **Data:** 2026-10-22
- **Situação:** aceita

## Contexto

O critério de pronto da Etapa 8 diz: *"um erro em produção é rastreável pelo ID de correlação"*. Hoje o back-end não tem log próprio: só o que o `uvicorn` imprime, em texto. Em produção ([ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md)), quem guarda os logs é o Render. Ele captura a saída do processo, guarda por 7 dias no plano da conta grátis e permite buscar por texto e filtrar por nível, rota e status. Restrições:
- Nada sensível no log: senha, access token, refresh token, URL do banco; e o e-mail, que é dado pessoal sob a LGPD;
- O log de texto puro é sujeito a *log injection*, a linha forjada por uma quebra de linha num campo (OWASP);
- Pedidos simultâneos não podem misturar seus IDs;
- Cada linha precisa ser explicável.

## Decisão

Escolhi usar o `logging` da biblioteca padrão com o formatador do `python-json-logger`: um objeto JSON por linha na saída padrão, valendo também para os logs do `uvicorn` e do SQLAlchemy. Usarei o middleware do `asgi-correlation-id`: aproveita o `X-Request-ID` que chega, se for válido, ou gera um novo; guarda o ID numa `contextvar`; põe o ID em toda linha de log do pedido; devolve o ID no cabeçalho `X-Request-ID` da resposta, inclusive no `500`. O usuário é identificado no log pelo id, nunca pelo e-mail. Os nomes dos campos, o nível de log e a forma como o front mostra o código ficam para a fase de desenho.

## Alternativas consideradas

- **`structlog`** — por que descartei: o código passaria a ter duas formas de registrar log (a do `structlog` no nosso código, a do `logging` no `uvicorn` e no SQLAlchemy), e a ponte entre elas, para tudo sair no mesmo JSON, é configuração a mais para manter.

- **Formatador escrito à mão** — por que descartei: os casos de canto (traceback, campos extras) ficariam por minha conta, para resolver algo que um pacote pequeno já resolve.

- **Middleware de correlação escrito à mão** — por que descartei: a validação do cabeçalho de entrada e o caso do `500` ficariam por minha conta.

- **OpenTelemetry** — por que descartei: é o padrão para rastrear um pedido entre vários serviços e precisa de um coletor e de um serviço para ver os rastros. Para uma API só, é desproporcional (vai para o backlog).

## Consequências

Os ganhos:
- Busca por campo no Render;
- Todas as linhas de um pedido reunidas pelo ID;
- Quem relata um erro manda o código e eu acho o pedido;
- O JSON escapa a quebra de linha, o que fecha a *log injection*;
- Front e API na mesma origem ([ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md)), então o front lê o `X-Request-ID` sem configurar CORS.

Os custos:
- Duas dependências novas;
- O middleware não põe o cabeçalho no `500` não tratado, e é preciso um handler de exceção para isso: é exatamente o caso que o critério da etapa pede;
- O ID que chega no cabeçalho é aceito se tiver o formato válido, então quem chama pode escolher o próprio ID (não serve como prova de nada, só como rastro);
- Log lido no terminal fica menos legível que o texto de hoje;
- Os logs duram 7 dias no Render: um erro mais antigo que isso não é mais rastreável.

## Como eu saberia que errei

Um erro relatado com o código não aparece na busca: o ID não chegou à linha, ou o cabeçalho não saiu no `500`. Aparece um dado sensível numa linha de log. Os 7 dias se mostram pouco, e os logs precisam ir para um serviço externo. O `python-json-logger` ou o `asgi-correlation-id` param de ser mantidos ou não suportam a próxima versão do Python.
