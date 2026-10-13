import { useState } from "react";
import { useSearchParams } from "react-router";
import { ErroDaApi } from "../api/erro";
import { useDisponibilidade } from "../api/recurso";
import {
  diaNoFuso,
  diaPorExtenso,
  diaValido,
  horaNoFuso,
  somarDias,
} from "../formato";
import { iniciosPossiveis } from "../grade";
import { FormularioDeReserva } from "./FormularioDeReserva";

// O dia mora na URL (?dia=2026-10-13): sobrevive ao F5 e o link pode ser enviado. Sem
// ele, ou com lixo, vale hoje, contado no fuso do recurso, não no do navegador.
export function Disponibilidade({
  idRecurso,
  ocupacao,
  fuso,
}: {
  idRecurso: number;
  ocupacao: number;
  fuso: string;
}) {
  const [busca, setBusca] = useSearchParams();
  const hoje = diaNoFuso(new Date(), fuso);
  const daUrl = busca.get("dia");
  const dia = diaValido(daUrl) ? daUrl : hoje;

  // replace: trocar de dia não empilha histórico; o "voltar" leva à lista.
  const irPara = (novo: string) => setBusca({ dia: novo }, { replace: true });

  return (
    <section aria-labelledby="titulo-disponibilidade">
      <h2 id="titulo-disponibilidade">Horários livres</h2>
      <p>
        <button
          type="button"
          onClick={() => irPara(somarDias(dia, -1))}
          disabled={dia <= hoje}
        >
          ← Dia anterior
        </button>{" "}
        <label htmlFor="dia">Dia: </label>
        <input
          id="dia"
          type="date"
          value={dia}
          min={hoje}
          onChange={(evento) => {
            if (diaValido(evento.target.value)) {
              irPara(evento.target.value);
            }
          }}
        />{" "}
        <button type="button" onClick={() => irPara(somarDias(dia, 1))}>
          Próximo dia →
        </button>
      </p>
      <p>
        {diaPorExtenso(dia)} · horários em {fuso}
      </p>
      {/* key: trocar de dia monta um Lacunas novo, sem formulário aberto nem aviso. */}
      <Lacunas
        key={dia}
        idRecurso={idRecurso}
        ocupacao={ocupacao}
        dia={dia}
        fuso={fuso}
      />
    </section>
  );
}

function Lacunas({
  idRecurso,
  ocupacao,
  dia,
  fuso,
}: {
  idRecurso: number;
  ocupacao: number;
  dia: string;
  fuso: string;
}) {
  const disponibilidade = useDisponibilidade(idRecurso, dia);
  // A lacuna com o formulário aberto e o aviso do último resultado: estado de interface.
  // A lacuna se identifica pelo fim: o início da de hoje é o "agora", que muda a cada
  // busca nova (ao voltar à aba, por exemplo), e fecharia o formulário no meio.

  const [aberta, setAberta] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);

  if (disponibilidade.isPending) {
    return <p role="status">Carregando horários…</p>;
  }

  if (disponibilidade.isError) {
    const erro = disponibilidade.error;
    if (erro instanceof ErroDaApi && erro.status === 409) {
      return <p>Este recurso está inativo e não aceita reservas.</p>;
    }
    return (
      <div role="alert">
        <p>Não foi possível carregar os horários.</p>
        <button
          type="button"
          onClick={() => disponibilidade.refetch()}
          disabled={disponibilidade.isFetching}
        >
          {disponibilidade.isFetching ? "Tentando…" : "Tentar de novo"}
        </button>
      </div>
    );
  }

  const terminar = (texto: string) => {
    setAberta(null);
    setAviso(texto);
  };

  const { lacunas } = disponibilidade.data;

  return (
    <>
      {aviso && <p role="status">{aviso}</p>}
      {lacunas.length === 0 ? (
        <p>Nenhum horário livre neste dia.</p>
      ) : (
        <ul>
          {lacunas.map((lacuna) => {
            const estaAberta = aberta === lacuna.fim;
            // Lacuna curta demais para a grade (14:37-14:50) aparece, mas não se reserva.
            const reservavel = iniciosPossiveis(lacuna).length > 0;
            return (
              <li key={lacuna.fim}>
                {horaNoFuso(lacuna.inicio, fuso)}-{horaNoFuso(lacuna.fim, fuso)}{" "}
                {reservavel && !estaAberta && (
                  <button
                    type="button"
                    onClick={() => {
                      setAberta(lacuna.fim);
                      setAviso(null);
                    }}
                  >
                    Reservar
                  </button>
                )}
                {estaAberta && (
                  <FormularioDeReserva
                    idRecurso={idRecurso}
                    ocupacao={ocupacao}
                    fuso={fuso}
                    lacuna={lacuna}
                    aoTerminar={terminar}
                    aoCancelar={() => setAberta(null)}
                  />
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
