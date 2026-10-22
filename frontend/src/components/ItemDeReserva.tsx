import { useRef } from "react";
import { ErroDaApi } from "../api/erro";
import { useCancelarReserva } from "../api/reserva";
import type { components } from "../api/tipos";
import {
  dataNoFuso,
  descreverReserva,
  diaDaSemanaCurto,
  diaNoFuso,
  mesCurto,
} from "../formato";
import { CodigoDoErro } from "./CodigoDoErro";
import type { Aviso } from "./FormularioDeReserva";

type ReservaResposta = components["schemas"]["ReservaResposta"];
type RecursoResposta = components["schemas"]["RecursoResposta"];

// O aviso de um cancelamento leva a reserva de que fala: a tela o usa como key da tarja.
export type AvisoDeCancelamento = Aviso & { id_reserva: number };

const NAO_CANCELAVEL =
  "Esta reserva não pode mais ser cancelada: ela já terminou ou foi cancelada por outra pessoa.";

function ehConflito(erro: Error): boolean {
  return erro instanceof ErroDaApi && erro.status === 409;
}

// Uma reserva por vir, em cartão. Só as confirmadas chegam aqui: as anteriores são a
// LinhaDeReserva, que não cancela e por isso não tem hook nenhum.
// Uma mutation por item: cada reserva tem o seu isPending e o seu erro. O "Cancelada"
// enquanto o pedido viaja é derivado do isPending (atualização otimista pela UI): o
// cache nunca é alterado, então, se o servidor recusar, não há nada a desfazer.
export function ItemDeReserva({
  reserva,
  recurso,
  aoAvisar,
}: {
  reserva: ReservaResposta;
  recurso: RecursoResposta | undefined;
  aoAvisar: (aviso: AvisoDeCancelamento) => void;
}) {
  const { fuso, nome, horario, convidados } = descreverReserva(
    reserva,
    recurso,
  );
  const data = dataNoFuso(reserva.inicio, fuso);
  // Os avisos vão para a tela, e não para o item: a lista nova muda a reserva de
  // seção, e o item que guardasse a mensagem seria desmontado junto com ela.
  const cancelar = useCancelarReserva({
    aoCancelar: () =>
      aoAvisar({
        tipo: "sucesso",
        texto: `Reserva de ${nome} em ${data}, ${horario}, cancelada.`,
        id_reserva: reserva.id_reserva,
      }),
    aoRecusar: (erro) => {
      if (ehConflito(erro)) {
        aoAvisar({
          tipo: "conflito",
          texto: NAO_CANCELAVEL,
          id_reserva: reserva.id_reserva,
        });
      }
    },
  });
  const modal = useRef<HTMLDialogElement>(null);
  const situacao = useRef<HTMLParagraphElement>(null);

  // O dia do calendário no fuso do recurso: é dele que saem as três partes do selo.
  const dia = diaNoFuso(new Date(reserva.inicio), fuso);
  const pendente = cancelar.isPending;
  const erroDeServidor = cancelar.isError && !ehConflito(cancelar.error);

  const confirmar = () => {
    // O close() devolve o foco ao botão que abriu o modal, mas ele some enquanto o
    // pedido viaja: o foco espera na situação. Se o cancelamento terminar num aviso,
    // a tarja o recebe antes de a lista nova desmontar o item; no erro de servidor, o
    // item fica, e o foco com ele.
    modal.current?.close();
    situacao.current?.focus();
    cancelar.mutate(reserva);
  };

  return (
    <li
      className={`flex flex-wrap items-center gap-x-6 gap-y-4 rounded-2xl border border-borda bg-superficie p-5 ${pendente ? "opacity-60" : ""}`}
    >
      {/* O selo é enfeite: o leitor de tela lê a data por extenso, no sr-only abaixo. */}
      <div
        aria-hidden="true"
        className={`w-19 shrink-0 rounded-xl py-2.5 text-center ${pendente ? "bg-sutil text-texto-suave" : "bg-destaque text-sobre-destaque"}`}
      >
        <div className="text-xs font-bold uppercase">{mesCurto(dia)}</div>
        <div className="font-titulo text-3xl leading-none font-extrabold">
          {Number(dia.slice(8))}
        </div>
        <div className="text-xs font-semibold">{diaDaSemanaCurto(dia)}</div>
      </div>
      <div className="min-w-0 flex-[1_1_16rem]">
        <p className="font-titulo text-xl font-bold">{nome}</p>
        <p className="mt-1 text-texto-suave">
          <span className="sr-only">{data}, </span>
          {horario} · {convidados}
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-3.5">
        {/* O foco chega aqui um instante antes do texto mudar: o aria-live anuncia a 
              mudança ("Cancelada", ou a volta a "Confirmada") a quem usa leitor de tela. */}
        <p
          ref={situacao}
          tabIndex={-1}
          aria-live="polite"
          className={`text-sm font-bold ${pendente ? "text-texto-suave" : "text-ok"}`}
        >
          <span className="sr-only">Situação: </span>
          {pendente ? (
            "Cancelada"
          ) : (
            <>
              <span aria-hidden="true">● </span>Confirmada
            </>
          )}
        </p>
        {!pendente && (
          <button
            type="button"
            onClick={() => modal.current?.showModal()}
            className="cursor-pointer rounded-full border border-borda-forte px-4.5 py-2.5 font-semibold text-texto hover:bg-sutil"
          >
            Cancelar reserva
          </button>
        )}
      </div>
      {erroDeServidor && (
        <p
          role="alert"
          className="basis-full rounded-xl bg-perigo-suave px-4 py-3 font-semibold text-perigo"
        >
          Não foi possível cancelar agora. Tente de novo.
          <CodigoDoErro erro={cancelar.error} />
        </p>
      )}
      {/* showModal() prende o foco aqui dentro, fecha com Esc e torna inerte o resto
          da página. Ao abrir, o foco vai ao primeiro botão: "Manter reserva" vem
          primeiro de propósito, para que um Enter distraído não cancele nada.
          O m-auto devolve a centralização que o Preflight tirou. */}
      <dialog
        ref={modal}
        aria-labelledby={`titulo-cancelar-${reserva.id_reserva}`}
        aria-describedby={`texto-cancelar-${reserva.id_reserva}`}
        className="m-auto w-[calc(100%-2rem)] max-w-lg rounded-2xl border border-borda bg-superficie p-8 text-texto shadow-2xl backdrop:bg-veu"
      >
        <h2
          id={`titulo-cancelar-${reserva.id_reserva}`}
          className="font-titulo text-3xl font-extrabold tracking-tight"
        >
          Cancelar reserva
        </h2>
        <p
          id={`texto-cancelar-${reserva.id_reserva}`}
          className="mt-3 leading-relaxed text-texto-suave"
        >
          Cancelar a reserva de <strong className="text-texto">{nome}</strong>{" "}
          em {data}, {horario}? Não é possível desfazer.
        </p>
        <div className="mt-7 flex flex-wrap justify-end gap-2.5">
          <button
            type="button"
            onClick={() => modal.current?.close()}
            className="cursor-pointer rounded-full border border-texto bg-texto px-5.5 py-3 font-bold text-fundo"
          >
            Manter reserva
          </button>
          <button
            type="button"
            onClick={confirmar}
            className="cursor-pointer rounded-full border border-perigo px-5.5 py-3 font-bold text-perigo hover:bg-perigo-suave"
          >
            Confirmar cancelamento
          </button>
        </div>
      </dialog>
    </li>
  );
}
