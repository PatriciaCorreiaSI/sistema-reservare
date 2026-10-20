// O dia seguinte no fuso dado, como AAAA-MM-DD (o formato do campo de data e do
// ?dia= da API). O en-CA é o locale que escreve a data nessa ordem.
export function amanhaNoFuso(fuso: string): string {
  const daqui24h = new Date(Date.now() + 24 * 60 * 60 * 1000);
  return daqui24h.toLocaleDateString("en-CA", { timeZone: fuso });
}
