// Falha de uma chamada à API, com o status HTTP. A tela decide a mensagem pelo número
// (401 = credenciais, o resto = servidor), nunca pelo texto.
export class ErroDaApi extends Error {
  readonly status: number;
  // O X-Request-ID da resposta (ADR 0029): o mesmo valor das linhas de log daquele
  // pedido. null quando a resposta não passou pela API (o 502 do proxy, por exemplo).
  readonly codigo: string | null;

  constructor(response: Response, mensagem: string) {
    super(`${mensagem}: ${response.status}`);
    this.name = "ErroDaApi";
    this.status = response.status;
    this.codigo = response.headers.get("X-Request-ID");
  }
}
