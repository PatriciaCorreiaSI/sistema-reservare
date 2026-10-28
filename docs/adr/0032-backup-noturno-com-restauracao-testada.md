# ADR 0032 — Fazer backup noturno pelo GitHub Actions, restaurando cada um antes de guardar

- **Data:** 2026-10-22
- **Situação:** aceita

## Contexto

O ROADMAP pede "backup e restauração testada, não só backup". O Neon Free ([ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md)) guarda 6 horas de histórico e 1 snapshot manual, sem agendamento. Isso não cobre um erro descoberto no dia seguinte, nem um problema com a própria conta do Neon: backup no mesmo fornecedor cai junto com ele. O plano grátis do Render não tem cron job. Um backup nunca restaurado pode estar vazio, truncado, ou sem a extensão de que o esquema precisa. No nosso caso, sem o `btree_gist` a `EXCLUDE` não é recriada, e o invariante some sem aviso. O repositório é público: os *artifacts* do GitHub Actions podem ser baixados por qualquer pessoa com acesso de leitura, e o banco tem e-mails (dado pessoal, LGPD) e hashes de senha. O [ADR 0031](./0031-configurar-producao-por-blueprint.md) evitou pôr a URL do banco que escreve nos *secrets* do GitHub.

## Decisão

Vou fazer o backup por um workflow agendado no GitHub Actions, uma vez por noite:
1. `pg_dump` do Neon, com um papel do Postgres só de leitura, criado só para isso;
2. restauração do dump num Postgres 16 descartável, dentro do próprio job;
3. conferência da restauração: as tabelas, a `EXCLUDE`, o `alembic current` em `head` e as contagens iguais às do Neon;
4. só então, o dump é criptografado e guardado como *artifact*.

Se a restauração ou a conferência falhar, o wokrflow fica vermelho e nada é guardado. O snapshot e o histórico do Neon ficam como complemento, para desfazer um erro recente, e não como backup. O horário, a ferramenta de criptografia, a criação do papel e o que exatamente se confere ficam para o desenho.

## Alternativas consideradas

- **Só o snapshot e o histórico do Neon** — por que descartei: ficam no mesmo fornecedor do banco, cobrem só 6 horas e 1 cópia manual, e ninguém testa a restauração.

- **Cron job do Render** — por que descartei: não existe no plano grátis ([ADR 0028](./0028-hospedar-api-no-render-e-banco-no-neon.md)).

- **`pg_dump` à mão, do meu computador** — por que descartei: depende de lembrar, e a restauração não é testada. É a mesma armadilha do deploy manual.

- **Workflow que guarda num armazenamento externo (Cloudflare R2, Backblaze B2)** — por que descartei: mais um fornecedor, mais uma conta e mais uma credencial para manter, para ganhar retenção maior que uma demonstração não precisa.

## Consequências

Os ganhos:
- Todo backup é restaurado no momento em que nasce: um backup guardado é um backup que já funcionou;
- A cópia fica fora do Neon;
- O segredo no GitHub só lê, não altera nem apaga;
- A falha avisa sozinha, por e-mail do GitHub;
- Reaproveita o *service container* do Postgres que o CI já usa.

Os custos:
- O dump precisa ser criptografado, e a chave privada que o abre fica fora do GitHub; perdê-la é perder todos os backups;
- Os artifacts duram no máximo 90 dias em repositório público;
- O GitHub desliga o agendamento depois de 60 dias sem atividade no repositório, e o backup para em silêncio;
- Entre um backup e o seguinte, até um dia de dados pode se perder (o histórico de 6 horas do Neon cobre só parte disso).

## Como eu saberia que errei

O workflow fica vermelho e a causa está no procedimento, não no banco. Uma restauração de verdade, feita a partir de um artifact, não reproduz o que a conferência do workflow disse. O backup parou porque o agendamento foi desligado e ninguém percebeu. Um dump aparece sem criptografia em qualquer lugar. A demonstração passa a ter dados que não podem se perder em um dia.
