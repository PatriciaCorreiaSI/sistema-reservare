import { expect, type APIRequestContext } from "@playwright/test";
import type { components } from "../src/api/tipos.ts";
import { ADMIN } from "./ambiente.ts";

type Schemas = components["schemas"];

// Preparação pela API, como nos testes do backend: o caminho mais direto até o
// estado de que o teste precisa. O teste em si age pela tela.
export async function tokenDoAdmin(
  request: APIRequestContext,
): Promise<string> {
  const resposta = await request.post("/api/auth/login", {
    data: {
      email_usuario: ADMIN.email,
      senha: ADMIN.senha,
    } satisfies Schemas["LoginEntrada"],
  });
  expect(resposta.status()).toBe(200);
  const corpo: Schemas["TokenResposta"] = await resposta.json();
  return corpo.access_token;
}
