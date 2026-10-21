import { expect, test as setup } from "@playwright/test";
import type { components } from "../src/api/tipos.ts";
import { OUTRA_USUARIA, USUARIA } from "./ambiente.ts";
import { tokenDoAdmin } from "./api.ts";

setup("cria as usuárias comuns", async ({ request }) => {
  const token = await tokenDoAdmin(request);
  for (const pessoa of [USUARIA, OUTRA_USUARIA]) {
    const resposta = await request.post("/api/usuarios", {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        nome_usuario: pessoa.nome,
        email_usuario: pessoa.email,
        senha: pessoa.senha,
        privilegio_usuario: "usuario",
      } satisfies components["schemas"]["UsuarioCriar"],
    });
    expect(resposta.status()).toBe(201);
  }
});
