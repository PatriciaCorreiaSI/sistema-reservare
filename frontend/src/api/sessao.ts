let accessToken: string | null = null;

export function obterAccessToken(): string | null {
  return accessToken;
}

export function guardarAccessToken(token: string): void {
  accessToken = token;
}

export function esquecerAccessToken(): void {
  accessToken = null;
}
