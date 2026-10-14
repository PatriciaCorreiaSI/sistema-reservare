import { useState } from "react";
import { Link } from "react-router";
import { useRecursos } from "../api/recurso";
import { useReservas } from "../api/reserva";
import type { components } from "../api/tipos";
import { ItemDeReserva } from "../components/ItemDeReserva";

type ReservaResposta = components["schemas"]["ReservaResposta"];
type RecursoResposta = components["schemas"]["RecursoResposta"];

// O aviso mora na tela, e não no item: o item pode mudar de seção (e ser desmontado)
// quando a lista nova chega.
export function TelaReservas() {
  const [aviso, setAviso] = useState<string | null>(null);
  return (
    <>
      <h1>Minhas reservas</h1>
      {aviso && <p role="alert">{aviso}</p>}
      <ListaDeReservas aoAvisar={setAviso} />
    </>
  );
}

// Duas consultas, uma junção no cliente. Os dados vêm antes do erro: se uma busca em
// segundo plano falhar (a API caiu depois do cancelamento), a lista que já estava na
// tela continua lá, em vez de ser trocada pela mensagem de erro.
function ListaDeReservas({ aoAvisar }: { aoAvisar: (aviso: string) => void }) {
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
      <div role="alert">
        <p>Não foi possível carregar as reservas.</p>
        <button
          type="button"
          onClick={() => {
            void reservas.refetch();
            void recursos.refetch();
          }}
          disabled={tentando}
        >
          {tentando ? "Tentando…" : "Tentar de novo"}
        </button>
      </div>
    );
  }

  return <p role="status">Carregando reservas…</p>;
}

const instante = (texto: string) => Date.parse(texto);

function Secoes({
  reservas,
  recursos,
  aoAvisar,
}: {
  reservas: ReservaResposta[];
  recursos: RecursoResposta[];
  aoAvisar: (aviso: string) => void;
}) {
  if (reservas.length === 0) {
    return (
      <p>
        Você ainda não tem reservas.{" "}
        <Link to="/recursos">Escolha um recurso</Link> para reservar.
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

  const item = (reserva: ReservaResposta) => (
    <ItemDeReserva
      key={reserva.id_reserva}
      reserva={reserva}
      recurso={porId.get(reserva.id_recurso)}
      aoAvisar={aoAvisar}
    />
  );

  return (
    <>
      <section aria-labelledby="titulo-proximas">
        <h2 id="titulo-proximas">Próximas</h2>
        {proximas.length === 0 ? (
          <p>Nenhuma reserva por vir.</p>
        ) : (
          <ul>{proximas.map(item)}</ul>
        )}
      </section>
      <section aria-labelledby="titulo-anteriores">
        <h2 id="titulo-anteriores">Anteriores</h2>
        {anteriores.length === 0 ? (
          <p>Nenhuma reserva anterior.</p>
        ) : (
          <ul>{anteriores.map(item)}</ul>
        )}
      </section>
    </>
  );
}
