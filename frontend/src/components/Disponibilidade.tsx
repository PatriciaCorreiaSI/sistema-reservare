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

// O dia mora na URL (?dia=2026-10-13): sobrevive ao F5 e o link pode ser enviado. Sem
// ele, ou com lixo, vale hoje, contado no fuso do recurso, não no do navegador.
export function Disponibilidade({
  idRecurso,
  fuso,
}: {
  idRecurso: number;
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
      <Lacunas idRecurso={idRecurso} dia={dia} fuso={fuso} />
    </section>
  );
}

function Lacunas({
  idRecurso,
  dia,
  fuso,
}: {
  idRecurso: number;
  dia: string;
  fuso: string;
}) {
  const disponibilidade = useDisponibilidade(idRecurso, dia);

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

  const { lacunas } = disponibilidade.data;
  if (lacunas.length === 0) {
    return <p>Nenhum horário livre neste dia.</p>;
  }

  return (
    <ul>
      {lacunas.map((lacuna) => (
        <li key={lacuna.inicio}>
          {horaNoFuso(lacuna.inicio, fuso)}-{horaNoFuso(lacuna.fim, fuso)}
        </li>
      ))}
    </ul>
  );
}
