import { Link } from "react-router";
import { useRecursos } from "../api/recurso";
import type { components } from "../api/tipos";
import { horaCurta } from "../formato";

type RecursoResposta = components["schemas"]["RecursoResposta"];

// O título fica fora dos estados: a página tem nome mesmo carregando ou com erro.
export function TelaRecursos() {
  return (
    <>
      <h1
        id="titulo-recursos"
        className="font-titulo text-5xl leading-none font-extrabold tracking-tight"
      >
        Recursos
      </h1>
      <ListaDeRecursos />
    </>
  );
}

// Os quatro estados de uma tela que busca dados: carrgando, erro, vazio e com dados.
// Cada um tem a sua saída; nenhum cai no outro por acidente.
function ListaDeRecursos() {
  const recursos = useRecursos();

  if (recursos.isPending) {
    return (
      <p role="status" className="mt-4 text-texto-suave">
        Carregando recursos…
      </p>
    );
  }

  if (recursos.isError) {
    return (
      <div
        role="alert"
        className="mt-8 flex max-w-lg flex-col items-start gap-4 rounded-xl bg-perigo-suave p-5"
      >
        <p className="font-semibold text-perigo">
          Não foi possível carregar os recursos.
        </p>
        <button
          type="button"
          onClick={() => recursos.refetch()}
          disabled={recursos.isFetching}
          className="cursor-pointer rounded-lg border border-borda-forte bg-superficie px-3.5 py-3 text-texto hover:bg-sutil disabled:cursor-wait disabled:opacity-60"
        >
          {recursos.isFetching ? "Tentando…" : "Tentar de novo"}
        </button>
      </div>
    );
  }

  if (recursos.data.length === 0) {
    return (
      <p className="mt-4 text-texto-suave">Nenhum recurso cadastrado ainda.</p>
    );
  }

  // O fuso vem da configuração do servidor, um só para todos os recursos (ADR 0018):
  // dizer uma vez no subtítulo basta.
  const fuso = recursos.data[0].fuso;
  const quantos = recursos.data.length;

  return (
    <>
      <p className="mt-3.5 text-texto-suave">
        {quantos} {quantos === 1 ? "recurso" : "recursos"} · horários em {fuso}
      </p>
      <ul
        role="list"
        aria-labelledby="titulo-recursos"
        className="mt-8 grid grid-cols-[repeat(auto-fill,minmax(16rem,1fr))] gap-4"
      >
        {recursos.data.map((recurso) => (
          <CartaoDeRecurso key={recurso.id_recurso} recurso={recurso} />
        ))}
      </ul>
    </>
  );
}

// O inativo continua na lista, apagado: borda tracejada, sem fundo, tudo em texto suave.
function CartaoDeRecurso({ recurso }: { recurso: RecursoResposta }) {
  const ativo = recurso.status_recurso === "ativo";

  return (
    <li
      className={
        ativo
          ? "flex flex-col gap-4.5 rounded-2xl border border-borda bg-superficie p-6"
          : "flex flex-col gap-4.5 rounded-2xl border border-dashed border-borda-forte p-6 text-texto-suave"
      }
    >
      <div className="flex items-start justify-between gap-3">
        <Link
          to={`/recursos/${recurso.id_recurso}`}
          className={
            ativo
              ? "font-titulo text-2xl font-bold tracking-tight underline decoration-destaque underline-offset-6"
              : "font-titulo text-2xl font-bold tracking-tight underline decoration-borda-forte underline-offset-6"
          }
        >
          {recurso.nome_recurso}
        </Link>
        {/* O círculo é efeite: o leitor da tela lê só a palavra. */}
        <span
          className={
            ativo
              ? "shrink-0 text-sm font-bold text-ok"
              : "shrink-0 text-sm font-bold"
          }
        >
          <span aria-hidden="true">{ativo ? "● " : "○ "}</span>
          {ativo ? "Ativo" : "Inativo"}
        </span>
      </div>
      <dl className="grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-sutil p-3">
          <dt className="text-xs font-bold text-texto-suave uppercase">
            Ocupação
          </dt>
          <dd className="text-x1 mt-1 font-titulo font-bold">
            {recurso.ocupacao} {recurso.ocupacao === 1 ? "pessoa" : "pessoas"}
          </dd>
        </div>
        <div className="rounded-xl bg-sutil p-3">
          <dt className="text-xs font-bold text-texto-suave uppercase">
            Funciona
          </dt>
          <dd className="text-x1 mt-1 font-titulo font-bold">
            {horaCurta(recurso.hora_func_inicio)}–
            {horaCurta(recurso.hora_func_fim)}
          </dd>
        </div>
      </dl>
    </li>
  );
}
