import { test as base, expect } from "@playwright/test";
import type { components } from "../src/api/tipos.ts";
import { tokenDoAdmin } from "./api.ts";

type Schemas = components["schemas"];

// Cada teste ganha um recurso novo, com nome único: o retry não zera o banco, e um
// recurso compartilhado faria a segunda tentativa achar a reserva da primeira.
export const test = base.extend<{ recurso: Schemas["RecursoResposta"] }>({
  recurso: async ({ request }, use) => {
    const token = await tokenDoAdmin(request);
    const resposta = await request.post("/api/recursos", {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        nome_recurso: `Sala e2e ${crypto.randomUUID().slice(0, 8)}`,
        ocupacao: 4,
        hora_func_inicio: "08:00:00",
        hora_func_fim: "18:00:00",
      } satisfies Schemas["RecursoCriar"],
    });
    expect(resposta.status()).toBe(201);
    await use(await resposta.json());
  },
});

export { expect };
