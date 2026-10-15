import { useState } from "react";
import { Link, useSearchParams } from "react-router";
import { ErroDaApi } from "../api/erro";
import { useDisponibilidade } from "../api/recurso";
import {
  diaDaSemanaCurto,
  diaNoFuso,
  diaPorExtenso,
  diaValido,
  horaNoFuso,
  segundaDaSemana,
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

  // A semana é derivada do dia, não um segundo parâmetro na URL.
  const segunda = segundaDaSemana(dia);
  const semana = [0, 1, 2, 3, 4, 5, 6].map((n) => somarDias(segunda, n));
  // Voltar uma semana a partir de segunda, 19 cairia em segunda, 12, que já passou: o
  // destino nunca fica antes de hoje. Os dias são "AAAA-MM-DD", e texto nesse formato
  // se compara na mesma ordem do calendário.
  const umaSemanaAntes = somarDias(dia, -7);
  const semanaAnterior = umaSemanaAntes < hoje ? hoje : umaSemanaAntes;

  return (
    <section aria-label="Horários livres" className="mt-10">
      <h2 className="font-titulo text-2xl font-bold tracking-tight">
        {diaPorExtenso(dia)}
      </h2>
      <p className="mt-1 text-sm text-texto-suave">horários em {fuso}</p>

      <div className="mt-5 flex flex-wrap items-end gap-3">
        <nav aria-label="Semanas" className="flex gap-2">
          {segunda <= hoje ? (
            <span className="rounded-full border border-borda px-4 py-2.5 text-sm font-semibold text-texto-suave">
              <span aria-hidden="true">‹ </span>Semana anterior
            </span>
          ) : (
            <Link
              to={`?dia=${semanaAnterior}`}
              replace
              className="rounded-full border border-borda-forte px-4 py-2.5 text-sm font-semibold text-texto hover:bg-sutil"
            >
              <span aria-hidden="true">‹ </span>Semana anterior
            </Link>
          )}
          <Link
            to={`?dia=${somarDias(dia, 7)}`}
            replace
            className="rounded-full border border-borda-forte px-4 py-2.5 text-sm font-semibold text-texto hover:bg-sutil"
          >
            Próxima semana<span aria-hidden="true"> ›</span>
          </Link>
        </nav>
        <div className="flex flex-col gap-1.5 sm:ml-auto">
          <label htmlFor="dia" className="text-sm font-bold">
            Ir para a data
          </label>
          {/* O campo não é link: escolher uma data muda a URL pelo código, com o mesmo
              replace dos links. */}
          <input
            id="dia"
            type="date"
            value={dia}
            min={hoje}
            onChange={(evento) => {
              if (diaValido(evento.target.value)) {
                setBusca({ dia: evento.target.value }, { replace: true });
              }
            }}
            className="rounded-xl border border-borda-campo bg-campo px-3.5 py-2.5 text-texto"
          />
        </div>
      </div>

      <nav
        aria-label="Dias da semana"
        className="mt-5 grid grid-cols-7 gap-1.5 sm:gap-2"
      >
        {semana.map((d) => (
          <DiaDaFaixa key={d} dia={d} hoje={hoje} escolhido={d === dia} />
        ))}
      </nav>

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

// O que se vê ("SEG 13") é abreviado e fica escondido do leitor de tela, que lê a data
// inteira. O risco do dia passado é só CSS: o "(já passou)" diz o mesmo em palavras.
function DiaDaFaixa({
  dia,
  hoje,
  escolhido,
}: {
  dia: string;
  hoje: string;
  escolhido: boolean;
}) {
  const passado = dia < hoje;
  const ehHoje = dia === hoje;

  const conteudo = (
    <>
      <span aria-hidden="true" className="flex flex-col items-center">
        <span className="text-xs font-bold uppercase">
          {diaDaSemanaCurto(dia)}
        </span>
        <span
          className={
            passado
              ? "font-titulo text-xl font-bold line-through"
              : "font-titulo text-xl font-bold"
          }
        >
          {dia.slice(8)}
        </span>
        {ehHoje && <span className="text-xs font-bold">hoje</span>}
      </span>
      <span className="sr-only">
        {diaPorExtenso(dia)}
        {ehHoje && " (hoje)"}
        {passado && " (já passou)"}
      </span>
    </>
  );

  if (passado) {
    return (
      <span className="rounded-xl border border-borda py-3 text-center text-texto-suave">
        {conteudo}
      </span>
    );
  }

  return (
    <Link
      to={`?dia=${dia}`}
      replace
      aria-current={escolhido ? "page" : undefined}
      className={
        escolhido
          ? "rounded-xl border border-destaque bg-destaque py-3 text-center text-sobre-destaque"
          : "rounded-xl border border-borda py-3 text-center text-texto hover:bg-sutil"
      }
    >
      {conteudo}
    </Link>
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
