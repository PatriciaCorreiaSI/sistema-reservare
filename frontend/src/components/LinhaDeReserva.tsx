import type { components } from "../api/tipos";
import { dataCurtaNoFuso, descreverReserva } from "../formato";

type ReservaResposta = components["schemas"]["ReservaResposta"];
type RecursoResposta = components["schemas"]["RecursoResposta"];

const SITUACAO: Record<string, string> = {
  concluida: "Concluída",
  cancelada: "Cancelada",
};

// Uma reserva que já terminou ou foi cancelada, numa linha. Só apresentação: nada aqui
// muda, então não há hook, ref nem estado.
export function LinhaDeReserva({
  reserva,
  recurso,
}: {
  reserva: ReservaResposta;
  recurso: RecursoResposta | undefined;
}) {
  const { fuso, nome, horario, convidados } = descreverReserva(
    reserva,
    recurso,
  );
  const cancelada = reserva.status_reserva === "cancelada";

  return (
    <li className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 border-b border-borda px-1 py-4">
      <p className="min-w-0">
        <span className="font-bold">{nome}</span>
        <span className="text-texto-suave">
          {" "}
          · {dataCurtaNoFuso(reserva.inicio, fuso)} · {horario} · {convidados}
        </span>
      </p>
      <p
        className={`text-sm font-bold ${cancelada ? "text-destaque-texto" : "text-texto-suave"}`}
      >
        <span className="sr-only">Situação: </span>
        {SITUACAO[reserva.status_reserva] ?? reserva.status_reserva}
      </p>
    </li>
  );
}
