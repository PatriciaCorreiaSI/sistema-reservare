// "08:00:00" → "08:00". A hora de funcionamento é hora de relógio no fuso do recurso,
// não um instante: não passa pelo Intl, só se cortar.
export function horaCurta(hora: string): string {
  return hora.slice(0, 5);
}
