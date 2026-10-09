// Falha de uma chamada à API, com o status HTTP. A tela decide a mensagem pelo número
// (401 = credenciais, o resto = servidor), nunca pelo texto.
export class ErroDaApi extends Error {
  readonly status: number;

  constructor(status: number, mensagem: string) {
    super(`${mensagem}: ${status}`);
    this.name = "ErroDaApi";
    this.status = status;
  }
}
