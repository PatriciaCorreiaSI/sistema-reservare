import { ErroDaApi } from "../api/erro";

// O código que leva do erro na tela à linha certa no log (ADR 0029). Só nos 5xx: um
// 4xx a tela já explica, e não há o que procurar no log. É um <span>, e não um <p>,
// porque algumas mensagens de erro já são um <p>, e <p> dentro de <p> não é HTML válido.
export function CodigoDoErro({ erro }: { erro: Error | null }) {
  if (!(erro instanceof ErroDaApi) || erro.status < 500 || !erro.codigo) {
    return null;
  }
  return (
    <span className="mt-1 block text-sm font-normal text-perigo">
      Código do erro:{" "}
      <code className="break-all select-all">{erro.codigo}</code>
    </span>
  );
}
