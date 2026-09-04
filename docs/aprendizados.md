# 👩‍🎓Uma linha por conceito novo aprendido

### 🧱 Etapa 0 — Fundação

| **Conceitos** | **Novo aprendizado** |
|--------------|----------------------|
|🪝**Ancoragem do .gitignore:** | 1. Barra (/) no início ou no meio ancora na raiz; sem barra casa em qualquer profundidade do repo. O .gitignore não protege arquivos pré-existentes já rastreados. 2. Ele decide o que o Git começa a rastrear a partir da criação do .gitignore.|
|💼 **Alterar nome do diretório local:** | 1. A ligação com o GIthub é a URL do remote. Alterar o nome da pasta local não interfere em nada. 2. É uma alteração meramente cosmética. Custa apenas fechar o VS Code e reabrir a pasta renomeada e nada mais. |
|🐍 **Python-version × requires-python:** | 1. O arquivo python-version (instrução local) define a versão python utilizada no sistema e está deliberada. 2. O atributo requires-python no arquivo pyproject.toml pode restringir a versão (ex:>=3.14,<3.15) ou deixar aberto para novas atualizações futuras de versões (ex:>=3.14), como está o valor atual. O padrão do uv é deixar aberto. |
|🩺 **/health e Falha em cascata:** | O desatre maior que um /health mal projetado causa se chama **Falha em cascata** ou, vulgarmente, *Espiral da Morte*. Acontece quando o /health que existe para verificar a saúde e bom funcionamento do sistema acaba por quebrá-lo, matando todas as instâncias que estavam saudáveis.  |
|✍️ Ferramenta **ruff:** | **Pergunta que responde:** "isto está escrito no padrão?" | 
|🆎 Ferramenta **mypy:** | **Pergunta que responde:** "estes tipos batem?" | 
|🚪 Ferramenta **pre-commit:** | **Pergunta que responde:** "isto pode entrar no repositório?" |
|🤖 **git status --short:** | Colunas "AD": "A" entrou no índice; "D" foi removido do disco; Para corrigir esta situação, rodar ```"git restore --staged <caminho do arquivo>"``` | 
|🔕 **Silêncio = sucesso:** | Terminal só acusa informação quando dá erro. Esse é o padrão. |
|🔍 **Ruff check:** |  Encontra problemas (imports não usados, variável morta, ordem de import). A flag```[--fix]``` aqui pede para *também* consertar. |
|🛠️ **Ruff format:** |  Reescreve o arquivo formatado. Por isso flag ```[--fix]``` não é necessária, porque o ```ruff format``` já modifica o arquivo. As flags ```[--diff]``` e ```[--check]``` aqui pedem para só relatar. |
|🐋 **Dockerfile:** | Mora ao lado do serviço que ele atende. O padrão é um Dockerfile por serviço. |
|🐳 **docker-compose.yml:** | Atende vários serviços e une o que eu crio com o que consumo, exe: API(crio:build) + Postgres(consumo:image). Mora na raiz do repo |
|🥊 **image × build:** no compose | 1. Image é estático e vem de um registro pronto para ser consumido. O container é a instância em execução de uma imagem, exe: Postgres. 2. Build é construído e sobe no container pelo código, exe: API. |
|📥**container começou ≠ container pronto:** | Quando o container começa a rodar ele percorre 5 etapas e somente ao final ele está pronto para que a API consiga encontrar o Postgres disponível |
|🦻 **pg_isready:** | Existe uma armadilha do *pg_isready* no docker-compose.yml. Por padrão o *pg_isready* aponta para o socket local, um arquivo do sistema do servidor temporário que morre ao final das 5 etapas percorridas ao iniciar o container. É preciso indicar ao *pg_isready* o ```-h localhost``` para forçar o protocolo TCP que somente o servidor definitivo escuta. |
|✅ **depends_on** com **condition: service_healthy**: | 1. Faz com que a API espere o container estar na condição **"está saudável"** para começar os testes de conexão com o banco de dados. 2. Garante que a API evite o teste antes, o que tornaria a conexão falha. |
|🗂️ **Volume nomeado × bind mount** | 1. **Volume nomeado:** delega ao docker-compose.yml criar e gerenciar a pasta oculta no sistema operacional do computador para guardar e salvar os dados do banco de dados. 2. **Bind mount:** permite que se escolha um diretório específico criado no computador para servir como essa pasta. Os dois métodos servem para garantir a persistência dos dados. Porém o volume nomeado é mais seguro e padrão de mercado, ao passo que o bind mount é mais suscetível a erros. |
|⚙️ **docker compose config** | Comando que lê o docker-compose.yml e mostra seus dados de saída. Não se deve copiar o conteúdo dele de volta para dentro do arquivo/código.|
|🥊**Banco garante × Serviço garante** | 1. **Banco garante:** regra que o banco de dados sozinho, com sua linguagem SQL, consegue assegurar, exe: constraint ```CHECK``` garante que somente os status ```ativo``` e ```inativo``` sejam possíveis na coluna ```status_recurso```. 2. **Serviço garante:** regra que o banco de dados não possui recurso para assegurar sozinho e precisa que o serviço assegure, exe: o sistema identificar o instante atual para comparar com o período final da reserva no banco de dados e conseguir alterar seu status para "concluída". |


### 🗄️ Etapa 1 — Modelagem e migrations

| **Conceitos** | **Novo aprendizado** |
|--------------|----------------------|
| **Constraint de coluna × constraint de tabela:** | 1. Cada vírgula dentro do ```CREATE TABLE``` cria uma nova coluna. Desse modo, **constraint de coluna** deve ficar na linha da coluna sem vírgula. Não precisa repetir o nome da coluna. 2. Já a **constraint de tabela** deve ser construída após a vírgula em linha própria. Já nomear a **constraint** é opcional nas duas formas. |
| ```PRIMARY KEY × FOREIGN KEY``` e **nulidade:** | 1. **PK** já traz implícito o fato de ser NOT NULL. Por isso não precisa declará-lo explícitamente e fazê-lo seria redundante. 2. **FK** não possui esse atributo, então precisa que a nulidade (```NOT NULL```) seja explicitada, se for o caso, na sua declaração. |
| **Cláusula × predicado:** | 12.**Cláusula** é uma estrutura sintática de um comando ```SQL``` que funciona como um recipiente, exe: ```WHERE```. Já **predicado** é uma condição lógica que avalia valores como ```V```, ```F``` ou ```desconhecido```, funcionando como o conteúdo desse recipiente, exe: ```cancelada_em IS NULL```. Uma mesma cláusula pode ter diferentes predicados que alteram seu comportamente.  |
| **```upper_inc``` × ```upper_inf```:** | 1. ```upper_inc(intervalo)``` é uma função nativa no SQL, especialmente no Postgres, que retorna ```TRUE``` se o valor limite superior do intervalo for inclusivo, exe: ```]``` 2. Já ```upper_inf(intervalo)``` retorna ```TRUE``` se o valor superior do intervalo superior for infinito, ilimitado. |
| **```lower_inc``` × ```lower_inf```:** | 1. ```lower_inc(intervalo)``` é uma função nativa no SQL, especialmente no Postgres, que retorna ```TRUE``` se o valor limite inferior do intervalo for inclusivo, exe: ```[``` 2. Já ```lower_inf(intervalo)``` retorna ```TRUE``` se o valor inferior do intervalo inferior for infinito, ilimitado. |
| **Tipo ````tstzrange```` recusa limites invertidos:** | O tipo ````tstzrange```` já atua como uma constraint que recusa a escrita de valores limites invertidos, como ```[12h, 10h)```. Não precisa, portanto, do uso de ```CHECK``` para garantir essa recusa. |
| **```ON DELETE```:** | Instrução SQL usada em chaves estrangeiras para decidir o que acontece com os registros filhos quando o pai é deletado. Pode receber como comportamento ```CASCADE```, ```RESTRICT``` e outros valores. Sobre esse dois, ```CASCADE``` apaga por cascata todos os registros filhos automaticamente. ```RESTRICT``` bloqueia a exclusão do registro pai se existir algum filho conectado a ele. |
| **```\echo``` × ```\warn```:** | São comandos internos (metacomandos) do **psql** (o cliente). São usados para exibir mensagens na tela. Cada um envia a informação para um fluxo de dados distinto: 1. ```\echo```: ```stdount``` que é a saída padrão, recomendado para mensagens informativas normais, lgos e resultados esperados. 2. ````\warn```: ```stderr``` que é a saída de erro, recomendado para avisos, alertas e mensagens de erro. |
| **Indireção:** | É falar com algo que aponta para a coisa em vez da coisa. Exe: quando se faz uso de uma coluna calculada para se chegar a um valor. |
| **--amend:** | Renomeia um commit sem apagar o original. |
| **--force-with-lease:** | Reescreve a história publicada por cima do commit original, conferindo se algo mudou desde o último ```fetch```. Usar com cuidado quando outras pessoas fazem uso do repo. |
| **--force:** | Reescreve a história publicada por cima do commit original, sem conferir se algo mudou desde o último ```fetch```. Usar com cuidado quando outras pessoas fazem uso do repo. |