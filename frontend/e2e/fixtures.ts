import { test as base, expect } from "@playwright/test";
import type { components } from "../src/api/tipos.ts";
import { criarRecursoPelaApi } from "./api.ts";

// Cada teste ganha um recurso novo, com nome único: o retry não zera o banco, e um
// recurso compartilhado faria a segunda tentativa achar a reserva da primeira.
export const test = base.extend<{
  recurso: components["schemas"]["RecursoResposta"];
}>({
  recurso: async ({ request }, use) => {
    await use(await criarRecursoPelaApi(request));
  },
});

export { expect };
