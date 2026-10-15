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

// A seta é enfeite: o leitor de tela lê só "Recursos".
function VoltarAosRecursos() {
  return (
    <Link
      to="/recursos"
      className="text-sm font-semibold text-destaque-texto hover:underline"
    >
      <span aria-hidden="true">← </span>Recursos
    </Link>
  );
}

function RecursoNaoEncontrado() {
  return (
    <>
      <VoltarAosRecursos />
      <h1 className="mt-3 font-titulo text-5xl leading-none font-extrabold tracking-tight">
        Recurso não encontrado
      </h1>
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
    return (
      <p role="status" className="text-texto-suave">
        Carregando recurso…
      </p>
    );
  }

  if (recurso.isError) {
    if (recurso.error instanceof ErroDaApi && recurso.error.status === 404) {
      return <RecursoNaoEncontrado />;
    }
    return (
      <div
        role="alert"
        className="flex max-w-lg flex-col items-start gap-4 rounded-xl bg-perigo-suave p-5"
      >
        <p className="font-semibold text-perigo">
          Não foi possível carregar o recurso.
        </p>
        <button
          type="button"
          onClick={() => recurso.refetch()}
          disabled={recurso.isFetching}
          className="cursor-pointer rounded-lg border border-borda-forte bg-superficie px-3.5 py-3 text-texto hover:bg-sutil disabled:cursor-wait disabled:opacity-60"
        >
          {recurso.isFetching ? "Tentando…" : "Tentar de novo"}
        </button>
      </div>
    );
  }

  const r = recurso.data;
  const ativo = r.status_recurso === "ativo";
  return (
    <>
      <VoltarAosRecursos />
      <h1 className="mt-3 font-titulo text-5xl leading-none font-extrabold tracking-tight">
        {r.nome_recurso}
      </h1>
      {/* auto-fit, e não auto-fill: com três quadros, as colunas que sobrariam vazias
          somem e os quadros esticam até a borda. */}
      <dl className="mt-7 grid grid-cols-[repeat(auto-fit,minmax(16rem,1fr))] gap-4">
        <div className="rounded-2xl border border-borda bg-sutil p-5">
          <dt className="text-xs font-bold tracking-wide text-texto-suave uppercase">
            Ocupação máxima
          </dt>
          <dd className="mt-2 flex items-baseline gap-2">
            <span className="text-texto-suave">{r.ocupacao}</span>
            <span className="text-texto-suave">
              {r.ocupacao === 1 ? "pessoa" : "pessoas"}
            </span>
          </dd>
        </div>
        <div className="rounded-2xl border border-borda bg-sutil p-5">
          <dt className="text-xs font-bold tracking-wide text-texto-suave uppercase">
            Funcionamento
          </dt>
          <dd className="mt-2">
            <span className="font-titulo text-3xl leading-none font-extrabold">
              {horaCurta(r.hora_func_inicio)}–{horaCurta(r.hora_func_fim)}
            </span>
            <span className="mt-1.5 block text-sm text-texto-suave">
              {r.fuso}
            </span>
          </dd>
        </div>
        <div className="rounded-2xl border border-borda bg-sutil p-5">
          <dt className="text-xs font-bold tracking-wide text-texto-suave uppercase">
            Situação
          </dt>
          <dd className="mt-2 flex items-center gap-2.5">
            <span
              aria-hidden="true"
              className={
                ativo
                  ? "size-3.5 rounded-full bg-ok"
                  : "size-3.5 rounded-full border-2 border-texto-suave"
              }
            />
            <span className="font-titulo text-3xl leading-none font-extrabold">
              {ativo ? "Ativo" : "Inativo"}
            </span>
          </dd>
        </div>
      </dl>
      {ativo ? (
        <Disponibilidade
          idRecurso={r.id_recurso}
          ocupacao={r.ocupacao}
          fuso={r.fuso}
        />
      ) : (
        <p className="mt-10 text-texto-suave">
          Este recurso está inativo e não aceita reservas.
        </p>
      )}
    </>
  );
}
