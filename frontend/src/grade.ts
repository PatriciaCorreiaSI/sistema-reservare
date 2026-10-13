import type { components } from "./api/tipos";

type Lacuna = components["schemas"]["Lacuna"];

// A grade de horários oferecidos para reservar. Os horários nascem dos instantes que a
// API devolveu, somando milissegundos: nenhum instante é construído a partir de uma
// hora local, o que pediria a conversão relógio → instante que o Intl não faz.
export const PASSO_MINUTOS = 30;
const PASSO_MS = PASSO_MINUTOS * 60 * 1000;

// Arredonda para cima até o próximo múltiplo do passo, contado em UTC. Com fusos de hora
// cheia ou meia hora, o múltiplo em UTC cai em :00 ou :30 no relógio local também.
function arredondarParaCima(ms: number): number {
  return Math.ceil(ms / PASSO_MS) * PASSO_MS;
}

// Inícios possíveis: os da grade, dentro da lacuna. A lacuna de hoje começa no "agora"
// (14:37:22); arredondar para 15:00 evita mandar um início que já terá passado.
export function iniciosPossiveis(lacuna: Lacuna): string[] {
  const fim = Date.parse(lacuna.fim);
  const inicios: string[] = [];
  for (
    let t = arredondarParaCima(Date.parse(lacuna.inicio));
    t < fim;
    t += PASSO_MS
  ) {
    inicios.push(new Date(t).toISOString());
  }
  return inicios;
}

// Fins possíveis para um início: de passo em passo até o fim da lacuna, que entra
// sempre, mesmo fora da grade (uma reserva vizinha pode começar às 13:15).
export function finsPossiveis(inicio: string, lacuna: Lacuna): string[] {
  const fim = Date.parse(lacuna.fim);
  const fins: string[] = [];
  for (let t = Date.parse(inicio) + PASSO_MS; t < fim; t += PASSO_MS) {
    fins.push(new Date(t).toISOString());
  }
  fins.push(new Date(fim).toISOString());
  return fins;
}
