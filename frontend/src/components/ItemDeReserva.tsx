import { useRef } from "react";
import { ErroDaApi } from "../api/erro";
import { useCancelarReserva } from "../api/reserva";
import type { components } from "../api/tipos";
import { dataNoFuso, horaNoFuso } from "../formato";

type ReservaResposta = components["schemas"]["ReservaResposta"];
type RecursoResposta = components["schemas"]["RecursoResposta"];

const SITUACAO: Record<string, string> = {
  confirmada: "Confirmada",
  concluida: "Concluída",
  cancelada: "Cancelada",
};

const NAO_CANCELAVEL =
  "Esta reserva não pode mais ser cancelada: ela já terminou ou foi cancelada por outra pessoa.";

function ehConflito(erro: Error): boolean {
  return erro instanceof ErroDaApi && erro.status === 409;
}

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
  aoAvisar: (aviso: string) => void;
}) {
  // O 409 vai para a tela, e não para o item: a lista nova pode mudar a reserva de
  // seção, e o item que guardasse a mensagem seria desmontado junto com ela.
  const cancelar = useCancelarReserva((erro) => {
    if (ehConflito(erro)) {
      aoAvisar(NAO_CANCELAVEL);
    }
  });
  const modal = useRef<HTMLDialogElement>(null);
  const situacao = useRef<HTMLParagraphElement>(null);

  // Sem o recurso (fora dos 100 primeiros da lista), o fuso do navegador, com a
  // etiqueta visível: a hora nunca fica ambígua.
  const fuso =
    recurso?.fuso ?? Intl.DateTimeFormat().resolvedOptions().timeZone;
  const nome = recurso?.nome_recurso ?? `Recurso nº ${reserva.id_recurso}`;
  const quando = `${dataNoFuso(reserva.inicio, fuso)}, ${horaNoFuso(reserva.inicio, fuso)}–${horaNoFuso(reserva.fim, fuso)} (${fuso})`;
  const convidados = `${reserva.convidados} ${reserva.convidados === 1 ? "convidado" : "convidados"}`;

  const cancelavel = reserva.status_reserva === "confirmada";
  const texto = cancelar.isPending
    ? "Cancelada"
    : (SITUACAO[reserva.status_reserva] ?? reserva.status_reserva);
  const erroDeServidor = cancelar.isError && !ehConflito(cancelar.error);

  const confirmar = () => {
    // O close() devolve o foco ao botão que abriu o modal, mas ele vai sumir: o foco
    // vai para a situação, que continua na tela.
    modal.current?.close();
    situacao.current?.focus();
    cancelar.mutate(reserva);
  };

  return (
    <li className={cancelar.isPending ? "esmaecido" : undefined}>
      <p>
        <strong>{nome}</strong>
        <br />
        {quando} · {convidados}
      </p>
      {/* O foco chega aqui um instante antes do texto mudar: o aria-live anuncia a
                mudança ("Cancelada", ou a volta a "Confirmada") a quem usa leitor de tela. */}
      <p ref={situacao} tabIndex={-1} aria-live="polite">
        Situação: {texto}
      </p>
      {cancelavel && !cancelar.isPending && (
        <button type="button" onClick={() => modal.current?.showModal()}>
          Cancelar reserva
        </button>
      )}
      {erroDeServidor && (
        <p role="alert">Não foi possível cancelar agora. Tente de novo.</p>
      )}
      {cancelavel && (
        // showModal() prende o foco aqui dentro, fecha com Esc e torna inerte o resto
        // da página. Ao abrir, o foco vai ao primeiro botão: "Manter reserva" vem
        // primeiro de propósito, para que um Enter distraído não cancele nada.
        <dialog
          ref={modal}
          aria-labelledby={`titulo-cancelar-${reserva.id_reserva}`}
          aria-describedby={`texto-cancelar-${reserva.id_reserva}`}
        >
          <h2 id={`titulo-cancelar-${reserva.id_reserva}`}>Cancelar reserva</h2>
          <p id={`texto-cancelar-${reserva.id_reserva}`}>
            Cancelar a reserva de {nome} em {quando}? Não é possível desfazer.
          </p>
          <button type="button" onClick={() => modal.current?.close()}>
            Manter reserva
          </button>{" "}
          <button type="button" onClick={confirmar}>
            Confirmar cancelamento
          </button>
        </dialog>
      )}
    </li>
  );
}
