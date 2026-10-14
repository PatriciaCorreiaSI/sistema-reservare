// "08:00:00" → "08:00". A hora de funcionamento é hora de relógio no fuso do recurso,
// não um instante: não passa pelo Intl, só se cortar.
export function horaCurta(hora: string): string {
  return hora.slice(0, 5);
}

// O dia do calendário ("2026-10-13") em que um instante cai, no fuso dado. O mesmo
// instante pode ser dia 13 em São Paulo e dia 14 em Tóquio. Por partes, e não pelo texto
// formatado, para não depender do jeito como cada idioma escreve datas.
export function diaNoFuso(instante: Date, fuso: string): string {
  const partes = new Intl.DateTimeFormat("en-US", {
    timeZone: fuso,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(instante);
  const parte = (tipo: string) => partes.find((p) => p.type === tipo)?.value;
  return `${parte("year")}-${parte("month")}-${parte("day")}`;
}

// Um dia do calendário não é um instante: a conta é feita em UTC, onde todo dia tem 24
// horas, e só a data volta. Assim a troca de horário de verão não pula nem repete dia.
function diaComoUtc(dia: string): Date {
  const [ano, mes, d] = dia.split("-").map(Number);
  return new Date(Date.UTC(ano, mes - 1, d));
}

// "2026-02-30" passa no formato, mas não existe: o Date o empurraria para 2 de março.
// Ida e volta pelo Date confere que o dia é de verdade.
export function diaValido(texto: string | null): texto is string {
  if (texto === null || !/^\d{4}-\d{2}-\d{2}$/.test(texto)) {
    return false;
  }
  return diaComoUtc(texto).toISOString().slice(0, 10) === texto;
}

export function somarDias(dia: string, quantos: number): string {
  const data = diaComoUtc(dia);
  data.setUTCDate(data.getUTCDate() + quantos);
  return data.toISOString().slice(0, 10);
}

// "terça-feira, 13 de outubro de 2026". Formatado em UTC de propósito: diaComoUtc pôs a
// meia-noite em UTC, e qualquer outro fuso poderia mostrar o dia anterior.
export function diaPorExtenso(dia: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: "UTC",
    dateStyle: "full",
  }).format(diaComoUtc(dia));
}

// Um instante da API ("2026-10-13T14:00:00Z") como hora de relógio no fuso do recurso.
// A API manda UTC; o fuso é assunto de apresentação, e só aqui ele entra.
export function horaNoFuso(instante: string, fuso: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: fuso,
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(instante));
}

// "quarta-feira, 15 de outubro de 2026": o dia do calendário em que o instante cai, no
// fuso do recurso.
export function dataNoFuso(instante: string, fuso: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: fuso,
    dateStyle: "full",
  }).format(new Date(instante));
}
