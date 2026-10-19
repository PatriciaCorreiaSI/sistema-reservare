import { useState } from "react";
import { Link } from "react-router";
import { useRecursos } from "../api/recurso";
import { useReservas } from "../api/reserva";
import type { components } from "../api/tipos";
import {
  ItemDeReserva,
  type AvisoDeCancelamento,
} from "../components/ItemDeReserva";
import { LinhaDeReserva } from "../components/LinhaDeReserva";

type ReservaResposta = components["schemas"]["ReservaResposta"];
type RecursoResposta = components["schemas"]["RecursoResposta"];

// A segunda cópia da função do Disponibilidade: fora do componente, para ser sempre a
// mesma, e o React só a chamar quando a tarja monta. Na terceira, vira módulo.
function focarAoMontar(elemento: HTMLElement | null) {
  elemento?.focus();
}

// O aviso mora na tela, e não no item: o item pode mudar de seção (e ser desmontado)
// quando a lista nova chega.
export function TelaReservas() {
  const [aviso, setAviso] = useState<AvisoDeCancelamento | null>(null);
  return (
    <>
      <h1 className="font-titulo text-5xl leading-none font-extrabold tracking-tight">
        Minhas reservas
      </h1>
      {/* A key faz de cada aviso uma tarja nova, que monta e recebe o foco; trocar só o
          texto reaproveitaria o <p>, e o ref não seria chamado. O id basta: depois de um
          aviso, a reserva muda de seção e não gera outro. */}
      {aviso && (
        <p
          key={aviso.id_reserva}
          role="status"
          ref={focarAoMontar}
          tabIndex={-1}
          className={
            aviso.tipo === "sucesso"
              ? "mt-6 rounded-xl border border-ok bg-ok-suave px-4 py-3 font-semibold text-ok"
              : "mt-6 rounded-xl border border-destaque bg-destaque-suave px-4 py-3 font-semibold text-destaque-texto"
          }
        >
          <span aria-hidden="true">
            {aviso.tipo === "sucesso" ? "✓ " : "! "}
          </span>
          {aviso.texto}
        </p>
      )}
      <ListaDeReservas aoAvisar={setAviso} />
    </>
  );
}

// Duas consultas, uma junção no cliente. Os dados vêm antes do erro: se uma busca em
// segundo plano falhar (a API caiu depois do cancelamento), a lista que já estava na
// tela continua lá, em vez de ser trocada pela mensagem de erro.
function ListaDeReservas({
  aoAvisar,
}: {
  aoAvisar: (aviso: AvisoDeCancelamento) => void;
}) {
  const reservas = useReservas();
  const recursos = useRecursos();

  if (reservas.data && recursos.data) {
    return (
      <Secoes
        reservas={reservas.data}
        recursos={recursos.data}
        aoAvisar={aoAvisar}
      />
    );
  }

  if (reservas.isError || recursos.isError) {
    const tentando = reservas.isFetching || recursos.isFetching;
    return (
      <div
        role="alert"
        className="mt-8 flex max-w-lg flex-col items-start gap-4 rounded-xl bg-perigo-suave p-5"
      >
        <p className="font-semibold text-perigo">
          Não foi possível carregar as reservas.
        </p>
        <button
          type="button"
          onClick={() => {
            void reservas.refetch();
            void recursos.refetch();
          }}
          disabled={tentando}
          className="cursor-pointer rounded-lg border border-borda-forte bg-superficie px-3.5 py-3 text-texto hover:bg-sutil disabled:cursor-wait disabled:opacity-60"
        >
          {tentando ? "Tentando…" : "Tentar de novo"}
        </button>
      </div>
    );
  }

  return (
    <p role="status" className="mt-4 text-texto-suave">
      Carregando reservas…
    </p>
  );
}

const instante = (texto: string) => Date.parse(texto);

function Secoes({
  reservas,
  recursos,
  aoAvisar,
}: {
  reservas: ReservaResposta[];
  recursos: RecursoResposta[];
  aoAvisar: (aviso: AvisoDeCancelamento) => void;
}) {
  if (reservas.length === 0) {
    return (
      <p className="mt-4 text-texto-suave">
        Você ainda não tem reservas.{" "}
        <Link
          to="/recursos"
          className="font-semibold text-destaque-texto underline underline-offset-4"
        >
          Escolha um recurso
        </Link>{" "}
        para reservar.
      </p>
    );
  }

  const porId = new Map(recursos.map((r) => [r.id_recurso, r]));
  // O status vem calculado do servidor; a tela só agrupa e ordena.
  const proximas = reservas
    .filter((r) => r.status_reserva === "confirmada")
    .toSorted((a, b) => instante(a.inicio) - instante(b.inicio));
  const anteriores = reservas
    .filter((r) => r.status_reserva !== "confirmada")
    .toSorted((a, b) => instante(b.inicio) - instante(a.inicio));

  return (
    <>
      <section aria-labelledby="titulo-proximas" className="mt-9">
        <h2
          id="titulo-proximas"
          className="mb-4 font-titulo text-2xl font-bold tracking-tight"
        >
          Próximas
        </h2>
        {proximas.length === 0 ? (
          <p className="text-texto-suave">Nenhuma reserva por vir.</p>
        ) : (
          <ul role="list" className="flex flex-col gap-3.5">
            {proximas.map((reserva) => (
              <ItemDeReserva
                key={reserva.id_reserva}
                reserva={reserva}
                recurso={porId.get(reserva.id_recurso)}
                aoAvisar={aoAvisar}
              />
            ))}
          </ul>
        )}
      </section>
      <section aria-labelledby="titulo-anteriores" className="mt-10">
        <h2
          id="titulo-anteriores"
          className="mb-4 font-titulo text-2xl font-bold tracking-tight"
        >
          Anteriores
        </h2>
        {anteriores.length === 0 ? (
          <p className="text-texto-suave">Nenhuma reserva anterior.</p>
        ) : (
          <ul role="list" className="border-t border-borda">
            {anteriores.map((reserva) => (
              <LinhaDeReserva
                key={reserva.id_reserva}
                reserva={reserva}
                recurso={porId.get(reserva.id_recurso)}
              />
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
