import { useState } from "react";
import { ErroDaApi } from "../api/erro";
import { useCriarReserva } from "../api/reserva";
import type { components } from "../api/tipos";
import { horaNoFuso } from "../formato";
import { finsPossiveis, iniciosPossiveis } from "../grade";

type Lacuna = components["schemas"]["Lacuna"];

// O resultado que o formulário entrega a quem o abriu. O tipo decide a cor do aviso: o
// conflito não é sucesso, e não pode parecer um.
export type Aviso = { tipo: "sucesso" | "conflito"; texto: string };

// Estado de interface (o que está escolhido no formulário) em useState; o estado de
// servidor (a reserva criada) é da mutation. Os selects só oferecem horários válidos,
// então a única entrada livre é o número de convidados.
export function FormularioDeReserva({
  idRecurso,
  ocupacao,
  fuso,
  lacuna,
  aoTerminar,
  aoCancelar,
}: {
  idRecurso: number;
  ocupacao: number;
  fuso: string;
  lacuna: Lacuna;
  aoTerminar: (aviso: Aviso) => void;
  aoCancelar: () => void;
}) {
  const criar = useCriarReserva();
  const inicios = iniciosPossiveis(lacuna);
  const [inicio, setInicio] = useState(inicios[0]);
  const fins = finsPossiveis(inicio, lacuna);
  const [fim, setFim] = useState(fins[0]);
  const [convidados, setConvidados] = useState("1");
  const [erroConvidados, setErroConvidados] = useState<string | null>(null);

  // Trocar o início pode deixar o fim escolhido antes dele: volta ao primeiro fim válido.
  const escolherInicio = (novo: string) => {
    setInicio(novo);
    setFim(finsPossiveis(novo, lacuna)[0]);
  };

  const reservar = (evento: React.SubmitEvent<HTMLFormElement>) => {
    evento.preventDefault();
    const quantos = Number(convidados);
    if (!Number.isInteger(quantos) || quantos < 1 || quantos > ocupacao) {
      setErroConvidados(`Informe de 1 a ${ocupacao} convidados.`);
      return;
    }
    setErroConvidados(null);
    criar.mutate(
      { id_recurso: idRecurso, convidados: quantos, inicio, fim },
      {
        onSuccess: (reserva) => {
          const de = horaNoFuso(reserva.inicio, fuso);
          const ate = horaNoFuso(reserva.fim, fuso);
          aoTerminar({
            tipo: "sucesso",
            texto: `Reserva feita: ${de}–${ate}.`,
          });
        },
        onError: (erro) => {
          if (erro instanceof ErroDaApi && erro.status === 409) {
            aoTerminar({
              tipo: "conflito",
              texto:
                "Esse horário acabou de ser reservado por outra pessoa. Os horários livres foram atualizados.",
            });
          }
        },
      },
    );
  };

  // O 409 fecha o formulário (a lacuna pode nem existir mais); os outros erros ficam aqui.
  const outroErro =
    criar.isError &&
    !(criar.error instanceof ErroDaApi && criar.error.status === 409);

  return (
    <form onSubmit={reservar} noValidate>
      <div>
        <label htmlFor="inicio">Início: </label>
        <select
          id="inicio"
          value={inicio}
          onChange={(evento) => escolherInicio(evento.target.value)}
        >
          {inicios.map((instante) => (
            <option key={instante} value={instante}>
              {horaNoFuso(instante, fuso)}
            </option>
          ))}
        </select>{" "}
        <label htmlFor="fim">Fim: </label>
        <select
          id="fim"
          value={fim}
          onChange={(evento) => setFim(evento.target.value)}
        >
          {fins.map((instante) => (
            <option key={instante} value={instante}>
              {horaNoFuso(instante, fuso)}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="convidados">Convidados: </label>
        <input
          id="convidados"
          type="number"
          min={1}
          max={ocupacao}
          value={convidados}
          onChange={(evento) => setConvidados(evento.target.value)}
          aria-invalid={erroConvidados ? true : undefined}
          aria-describedby={erroConvidados ? "erro-convidados" : undefined}
        />
        {erroConvidados && <p id="erro-convidados">{erroConvidados}</p>}
      </div>
      {outroErro && (
        <p role="alert">
          A reserva foi recusada. O horário pode ter passado enquanto a tela
          estava aberta: escolha outro.
        </p>
      )}
      <button type="submit" disabled={criar.isPending}>
        {criar.isPending ? "Reservando…" : "Confirmar reserva"}
      </button>{" "}
      <button type="button" onClick={aoCancelar} disabled={criar.isPending}>
        Cancelar
      </button>
    </form>
  );
}
