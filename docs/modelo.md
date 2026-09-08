# 🛅 Modelo de Dados Conceitual para Banco de Dados PostgreSQL

## 🔖RESERVA
| coluna         | tipo | restrições | descrição | 
|----------------|------|------------| ----------|
| id_reserva     | INT  | PRIMARY KEY,  NOT NULL, GENERATED ALWAYS AS IDENTITY  | Identificador |
| id_usuario     | INT  | FOREIGN KEY,  NOT NULL   | Qual usuário realizou a reserva   |
| id_recurso     | INT  | FOREIGN KEY,  NOT NULL   | Qual recurso está sendo utilizado |
| convidados     | INT  | NOT NULL   | quantidade de ocupantes do recurso simultaneamente |
| periodo        | tstzrange   | NOT NULL   | Ocupa um trecho de tempo com início e fim |
| status | VARCHAR(30) | NOT NULL, CHECK  | confirmada, cancelada |
| cancelada_por_id_usuario  | INT | FOREIGN KEY, CHECK  | Identificador de quem cancelou a reserva |
| cancelada_em   | TIMESTAMPTZ   | CHECK  | Tipo de instante com fuso |


## 🗄️RECURSO
| coluna         | tipo | restrições | descrição | 
|----------------|------|------------| ----------|
| id_recurso   | INT  | PRIMARY KEY,  NOT NULL, GENERATED ALWAYS AS IDENTITY  | Identificador |
| nome_recurso | VARCHAR(30)  | NOT NULL   | Nome de exibição |
| ocupacao_positiva     | INT  | NOT NULL   | Quantas pessoas podem usar o espaço simultaneamente|
| hora_func_inicio  | TIME  | NOT NULL  | Hora de funcionamento inicial |
| hora_func_fim     | TIME  | NOT NULL  | Hora de funcionamento final |
| status    | VARCHAR(30)  | NOT NULL, CHECK  | ativo, inativo |


## 👤USUARIO
| coluna       | tipo | restrições | descrição |
|--------------|------|------------| ----------|
| id_usuario   | INT  | PRIMARY KEY,  NOT NULL,  GENERATED ALWAYS AS IDENTITY | Identificador |
| privilegio | VARCHAR(15)  | NOT NULL, CHECK | admin, usuario|
| nome_usuario | VARCHAR(30)  | NOT NULL | Nome de exibição |
| email_usuario | VARCHAR(50)  | NOT NULL, UNIQUE | login |
| senha_usuario_hash | VARCHAR(100)  | HASH,  NOT NULL | Hash Argon 2 |
| status | VARCHAR(30)  | NOT NULL, CHECK  | ativo, inativo |



## ✍️ REGRAS DE NEGÓCIO

| regra | Como será garantida? |
|-------|----------------------|
| Duas reservas **ativas** não podem se sobrepor no mesmo recurso. | Banco garante |
| A reserva deve caber no horário de funcionamento do recurso. | Serviço garante |
| Não se reserva recurso inativo. | Serviço garante |
| Convidados <= Ocupação | Serviço garante |
| Reservas só podem ser feitas do período presente em diante, jamais no passado | Serviço garante |
| Status "Concluída" não é escrita na coluna porque é deduzida pelo sistema ao fim do período da reserva | Serviço garante |
| Recurso funciona dentro de um mesmo dia e não atravessa a meia-noite | Banco garante |
| Usuário com reserva pode ser inativado, jamais deletado | Banco garante |
| Recurso com reserva pode ser inativado, jamais deletado | Banco garante |



## 🔑 CONVENÇÃO DE NOMES

* `naming_convention` mora no `MetaData` e padroniza nomes de constraint e índice. Adotado o dicionário de cinco chaves (`ix`, `uq`, `ck`, `fk`, `pk`). Vale desde a primeira migration: mudar depois exige migration de renomeação.
* **Nome explícito nem sempre ganha** — só a chave `ck` reescreve. Ela é a única que usa `%(constraint_name)s`, então o nome que você escreveu vira ingrediente e a convenção monta outro em cima: `name="status"` sai como `ck_recurso_status` no banco. `fk`, `uq` e `ix` não têm esse token e respeitam o nome explícito; `pk` só age quando não há nome. (Verificado em SQLAlchemy 2.0.52.)
* Consequência prática: nomeie o `CHECK` pela parte semântica, **sem repetir o nome da tabela** — `name="recurso_status"` viraria `ck_recurso_recurso_status`.
* Não há chave para `EXCLUDE`: ela mantém o nome explícito, então `reserva_sem_sobreposicao` chega intacto na mensagem de erro. Para cobri-la, a chave seria a própria classe da constraint.


