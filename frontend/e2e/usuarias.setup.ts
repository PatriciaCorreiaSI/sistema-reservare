import { expect, test as setup } from "@playwright/test";
import type { components } from "../src/api/tipos.ts";
import { USUARIA } from "./ambiente.ts";
import { tokenDoAdmin } from "./api.ts";

setup("cria a usuaria comum", async ({ request }) => {
  const token = await tokenDoAdmin(request);
  const resposta = await request.post("/api/usuarios", {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      nome_usuario: USUARIA.nome,
      email_usuario: USUARIA.email,
      senha: USUARIA.senha,
      privilegio_usuario: "usuario",
    } satisfies components["schemas"]["UsuarioCriar"],
  });
  expect(resposta.status()).toBe(201);
});
