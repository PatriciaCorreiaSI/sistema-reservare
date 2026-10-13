import { Link } from "react-router";
import { useRecursos } from "../api/recurso";
import { horaCurta } from "../formato";

// O título fica fora dos estados: a página tem nome mesmo carregando ou com erro.
export function TelaRecursos() {
  return (
    <>
      <h1 id="titulo-recursos">Recursos</h1>
      <ListaDeRecursos />
    </>
  );
}

// Os quatro estados de uma tela que busca dados: carrgando, erro, vazio e com dados.
// Cada um tem a sua saída; nenhum cai no outro por acidente.
function ListaDeRecursos() {
  const recursos = useRecursos();

  if (recursos.isPending) {
    return <p role="status">Carregando recursos…</p>;
  }

  if (recursos.isError) {
    return (
      <div role="alert">
        <p>Não foi possível carregar os recursos.</p>
        <button
          type="button"
          onClick={() => recursos.refetch()}
          disabled={recursos.isFetching}
        >
          {recursos.isFetching ? "Tentando…" : "Tentar de novo"}
        </button>
      </div>
    );
  }

  if (recursos.data.length === 0) {
    return <p>Nenhum recurso cadastrado ainda.</p>;
  }

  return (
    <table aria-labelledby="titulo-recursos">
      <thead>
        <tr>
          <th scope="col">Nome</th>
          <th scope="col">Ocupação máxima</th>
          <th scope="col">Funcionamento</th>
          <th scope="col">Situação</th>
        </tr>
      </thead>
      <tbody>
        {recursos.data.map((recurso) => (
          <tr key={recurso.id_recurso}>
            <td>
              <Link to={`/recursos/${recurso.id_recurso}`}>
                {recurso.nome_recurso}
              </Link>
            </td>
            <td>{recurso.ocupacao}</td>
            <td>
              {horaCurta(recurso.hora_func_inicio)}-
              {horaCurta(recurso.hora_func_fim)} ({recurso.fuso})
            </td>
            <td>{recurso.status_recurso === "ativo" ? "ativo" : "Inativo"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
