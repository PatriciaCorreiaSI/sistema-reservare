# ADR 0021 — Testar pelo que a coisa testada depende

- **Data:** 2026-10-02
- **Situação:** aceita

## Contexto

Um teste pode testar um pedaço maior ou menor do sistema. A suíte de testes do Reservare já tem dois níveis, mas nenhuma regra escrita sobre quando usar cada um: o arquivo `test_reserva_regras.py` tem 20 testes unitários das funções puras; os outros arquivos têm cerca de 70 testes de integração pela API, e há um teste de concorrência. Cada teste novo é uma escolha feita na hora. Na Etapa 6, o CI vai rodar essa suíte a cada push, e o que ela cobre ou deixa de cobrir passa a valer como garantia.

A pirâmide de testes recomenda muitos testes unitários, alguns de integração e poucos de ponta a ponta. A razão é a velocidade e a precisão do diagnóstico. A restrição que pesa contra ela aqui: o invariante do projeto não mora no Python, mora no banco, na `EXCLUDE`. E os testes de reserva já dependem de duas coisas que não são determinísticas: o relógio e o fuso, que o `agora_fixo` e o `fuso_fixo` substituem. A cobertura nunca foi medida.

## Decisão

Escolhi a regra pelo que a coisa testada depende. Uma regra pura de Python, sem banco, ganha testes unitários. Qualquer coisa que depende do banco, como constraint, FK, `EXCLUDE`, transação ou tradução de erro, ganha teste de integração com o Postgres real. Utilizar dublê só para o que não é determinístico, como relógio e o fuso, e nunca para o banco. Medir a cobertura de testes e mostrar as linhas não cobertas, sem número mínimo. O CI imprime o relatório que pode ser usado para achar regra sem teste. A ferramenta é o `pytest-cov`, uma dependência de desenvolvimento. A cobertura serve como um alarme e nunca como meta.

## Alternativas consideradas

- **Pirâmide estrita** — por que descartei: testa o service com unitários, trocando o repository por um dublê que finge ser o banco. Mas o custo é alto. O invariante do projeto mora no banco, na `EXCLUDE`. Um service testado com banco falso nunca encontra a `EXCLUDE`, então o teste prova que o dublê funciona, não o sistema.

- **Não medir a cobertura de testes** — por que descartei: não custa nada, mas perde-se o alarme. Um handler de exceção que nenhum teste exercita fica invisível.

- **Na cobertura, exigir um mínimo que reprove o push** — por que descartei: a cobertura vira meta, e a meta convida a escrever teste para subir o número.

## Consequências

O ganho: os testes exercitam o que o sistema garante de verdade, a `EXCLUDE`, as FKs e a tradução de erro, e não um dublê. É o formato que o mercado chama de "troféu de testes", com o meio largo de integração, viável quando o banco real cabe num container. O custo: quase todo teste precisa do Postgres no ar, então nada roda sem o `docker compose`, e o CI precisa de um Postgres próprio. A suíte também é mais lenta que uma pirâmide pura. Hoje ela roda em cerca de 3 segundos, então esse custo ainda não pesa. A cobertura sem mínimo nunca reprova nada: o alarme só toca se alguém lê o relatório.

## Como eu saberia que errei

Se a suíte passar de um minuto, a ponto de eu evitar rodá-la antes de cada commit. Se um teste passar ou falhar conforme a hora em que roda: é o relógio real vazando, e um dublê faltou. Se um bug chegar ao CI verde numa linha que o relatório de cobertura já mostrava como não executada: o alarme existia e ninguém olhou. Ou se aparecer uma meta de cobertura a cumprir.
