# ADR 0011 — Isolar teste em uma transação desfeita no fim

- **Data:** 2026-09-11
- **Situação:** aceita

## Contexto

Testes que compartilham estado ficam dependentes da ordem e intermitentes. O banco de teste não pode ser o de desenvolvimento. E o projeto tem um teste: o de **concorrência da etapa 4** que exige duas transações reais. Isso restringe as opções desde já.

## Decisão

A decisão tem 4 partes:
1. Banco separado `reservare_test`, no mesmo Postgres do compose;
2. Esquema construído por `alembic upgrade head` a cada rodada (uma vez por rodada, não por teste) provando a migration junto;
3. Padrão: cada teste roda dentro de uma transação aberta pelo teste e desfeita no fim. A dependência `obter_sessao` é substituída por uma que entrega a `Session` presa a essa transação e não comita (ver Emenda: passa a comitar e desfazer o *savepoint*).
4. Exceção nomeada desde já: testes que precisam de transação real usam `commit` de verdade e `TRUNCATE` depois, marcados com um marcador próprio do `pytest`. A etapa 4 é o primeiro uso.

## Alternativas consideradas

- **Limpar entre testes:`TRUNCATE` para tudo:** — por que descartei: usaria uma única mecânica para tudo, mais simples de explicar. Antes de cada teste, `TRUNCATE` em todas as tabelas. Porém é mais lenta e `id` não reinicia.
- **Só transação, sem exceção nomeada:** — por que descartei: só faz transação por teste, sem exceção, o que não atende o teste que roda no coração do projeto, na etapa 4.
- **Um banco novo por teste** — por que descartei: cria, migra, testa, derruba, com isolamento perfeito. Mas leva segundos por teste; em uma suíte com 200 testes, levaria minutos.

## Consequências

O custo é ter duas mecânicas de teste ao invés de uma e quem escreve um teste precisa saber em qual está. Além disso, os testes comuns não comitam nunca, então um bug que só aparece no `commit` não é pego por eles. O ganho é que a dependência do [ADR 0010](0010-requisicao-e-transacao.md) torna essa decisão simples (sem *savepoint*; ver Emenda).

## Emenda (2026-09-23): a função substituta imita o ciclo do `obter_sessao`

### **Problema:**
O teste de reuso passava mesmo com o `commit()` da emenda ao ADR 0010 apagado, e isso foi provado por experimento. É o custo que o item `Consequências` previa ("um bug que só aparece no `commit()` não é pego"). A função substituta (`obter_sessao_de_teste` no `conftest.py`) não repetia o que o `obter_sessao` faz depois do `yield`. Sem `rollback()` no teste, o `commit()` da emenda não tinha de que sobreviver.

### **Decisão**
- A sessão se une à transação da fixture por **savepoint**, o que já existe desde **2026-09-16** e agora fica registrado;
- A substituta imita o `obter_sessao`: `commit()` depois do `yield`, `rollback()` + `raise` na exceção, sem `close()`. Com savepoint, esses `commit()` e `rollback()` são do savepoint, e a transação externa continua sendo da fixture e desfeita no fim.

### **Alternativas descartadas:**
- **Testes separados com transação real**: prova o `commit()` sem mexer na fixture, mas antecipa a infraestrutura da etapa 4 para um único teste.

- **Aceitar e registrar o limite**: o mais barato, mas deixa de pé o sinal de erro da emenda ao ADR 0010.

### Consequências
Nada chega ao disco, então outra conexão nunca enxerga o que o teste gravou. A concorrência da etapa 4 continua dependendo da exceção do item 4. O ganho: o caminho do `rollback()` passa a ser exercitado nos testes, e cada requisição dentro de um teste se comporta como uma transação, como em produção. O custo: o ciclo existe em dois lugares, que precisam andar juntos.

### Como eu saberia que errei
A substituta divergir do `obter_sessao`: se alguém muda o `obter_sessao` e não muda o `conftest.py`. Os testes passam a verificar um ciclo de transação que não é o de produção.

## Como eu saberia que errei

Se um teste que falha na suíte inteira passa sozinho, com estado vazando, mostrando que o isolamento não segurou. Ou um teste de concorrência travar esperando (rodando da forma errada dentro de uma transação só). Ou a suíte lenta para rodar a cada commit.
