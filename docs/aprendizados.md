# 👩‍🎓Uma linha por conceito novo aprendido

### 🧱 Etapa 0 — Fundação

| **Conceitos** | **Novo aprendizado** |
|--------------|----------------------|
|🪝**Ancoragem do .gitignore:** | 1. Barra (/) no início ou no meio ancora na raiz; sem barra casa em qualquer profundidade do repo. O .gitignore não protege arquivos pré-existentes já rastreados. 2. Ele decide o que o Git começa a rastrear a partir da criação do .gitignore.|
|💼 **Alterar nome do diretório local:** | 1. A ligação com o GIthub é a URL do remote. Alterar o nome da pasta local não interfere em nada. 2. É uma alteração meramente cosmética. Custa apenas fechar o VS Code e reabrir a pasta renomeada e nada mais. |
|🐍 **Python-version × requires-python** | 1. O arquivo python-version (instrução local) define a versão python utilizada no sistema e está deliberada. 2. O atributo requires-python no arquivo pyproject.toml pode restringir a versão (ex:>=3.14,<3.15) ou deixar aberto para novas atualizações futuras de versões (ex:>=3.14), como está o valor atual. O padrão do uv é deixar aberto. |
|🩺 **/health e Falha em cascata** | O desatre maior que um /health mal projetado causa se chama **Falha em cascata** ou, vulgarmente, *Espiral da Morte*. Acontece quando o /health que existe para verificar a saúde e bom funcionamento do sistema acaba por quebrá-lo, matando todas as instâncias que estavam saudáveis.  |
|✍️ Ferramenta **ruff** | **Pergunta que responde:** "isto está escrito no padrão?" | 
|🆎 Ferramenta **mypy** | **Pergunta que responde:** "estes tipos batem?" | 
|🚪 Ferramenta **pre-commit** | **Pergunta que responde:** "isto pode entrar no repositório?" |
|🤖 **git status --short** | Colunas "AD": "A" entrou no índice; "D" foi removido do disco; Para corrigir esta situação, rodar ```"git restore --staged <caminho do arquivo>"``` | 
|🔕 **Silêncio = sucesso** | Terminal só acusa informação quando dá erro. Esse é o padrão |
|🔍 **Ruff check** |  Encontra problemas (imports não usados, variável morta, ordem de import). A flag```[--fix]``` aqui pede para *também* consertar. |
|🛠️ **Ruff format** |  Reescreve o arquivo formatado. Por isso flag ```[--fix]``` não é necessária, porque o ```ruff format``` já modifica o arquivo. As flags ```[--diff]``` e ```[--check]``` aqui pedem para só relatar. |
