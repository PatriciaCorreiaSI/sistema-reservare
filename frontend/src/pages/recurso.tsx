import { Link, useParams } from "react-router";
import { useRecurso } from "../api/recurso";
import { ErroDaApi } from "../api/erro";
import { horaCurta } from "../formato";
import { Disponibilidade } from "../components/Disponibilidade";

// A URL é entrada: chega como texto, ou nem chega. Só um inteiro positivo vira id;
// "abc", "1.5" e "-3" param aqui, sem pedido à API.
function idDaUrl(texto: string | undefined): number | null {
  if (texto === undefined || !/^\d+$/.test(texto)) {
    return null;
  }
  const id = Number(texto);
  return id > 0 ? id : null;
}

function RecursoNaoEncontrado() {
  return (
    <>
      <h1>Recurso não encontrado</h1>
      <p>
        <Link to="/recursos">Voltar à lista de recursos</Link>
      </p>
    </>
  );
}

// Quem lê a URL decide se há id; só então o componente com o hook aparece. O hook não
// pode ficar depois de um return condicional (regra dos hooks), por isso são dois.
export function TelaRecurso() {
  const { idRecurso } = useParams();
  const id = idDaUrl(idRecurso);
  if (id === null) {
    return <RecursoNaoEncontrado />;
  }
  return <DetalheDoRecurso idRecurso={id} />;
}

function DetalheDoRecurso({ idRecurso }: { idRecurso: number }) {
  const recurso = useRecurso(idRecurso);

  if (recurso.isPending) {
    return <p role="status">Carregando recurso…</p>;
  }

  if (recurso.isError) {
    if (recurso.error instanceof ErroDaApi && recurso.error.status === 404) {
      return <RecursoNaoEncontrado />;
    }
    return (
      <div role="alert">
        <p>Não foi possível carregar o recurso.</p>
        <button
          type="button"
          onClick={() => recurso.refetch()}
          disabled={recurso.isFetching}
        >
          {recurso.isFetching ? "Tentando…" : "Tentar de novo"}
        </button>
      </div>
    );
  }

  const r = recurso.data;
  return (
    <>
      <p>
        <Link to="/recursos">← Recursos</Link>
      </p>
      <h1>{r.nome_recurso}</h1>
      <dl>
        <dt>Ocupação máxima</dt>
        <dd>{r.ocupacao}</dd>
        <dt>Funcionamento</dt>
        <dd>
          {`${horaCurta(r.hora_func_inicio)}-${horaCurta(r.hora_func_fim)} (${r.fuso})`}
        </dd>
        <dt>Situação</dt>
        <dd>{r.status_recurso === "ativo" ? "Ativo" : "Inativo"}</dd>
      </dl>
      {r.status_recurso === "ativo" ? (
        <Disponibilidade idRecurso={r.id_recurso} fuso={r.fuso} />
      ) : (
        <p>Este recurso está inativo e não aceita reservas.</p>
      )}
    </>
  );
}
