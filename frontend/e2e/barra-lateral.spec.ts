import type { Page } from "@playwright/test";
import { USUARIA } from "./ambiente.ts";
import { entrarPelaApi, reservarAmanhaPelaApi } from "./api.ts";
import { expect, test } from "./fixtures.ts";

// Numa página mais alta que a tela, o tema e o "Sair"
// continuam à vista. Sem a correção de 2026-10-14 (md:sticky md:top-0 md:h-svh), a
// barra esticava com a página e o md:mt-auto os empurrava para o fim dela.

const RESERVAS = 8;

async function conferirBarraAVista(page: Page) {
  await expect(page.getByRole("group", { name: "Tema" })).toBeInViewport();
  await expect(page.getByRole("button", { name: "Sair" })).toBeInViewport();
}

test("numa página mais alta que a tela, o tema e o sair continuam à vista", async ({
  page,
  request,
  recurso,
}) => {
  // 'Meias horas' seguidas: a primeira lacuna começa onde a reserva anterior termina.
  const token = await entrarPelaApi(request, USUARIA);
  for (let i = 0; i < RESERVAS; i++) {
    await reservarAmanhaPelaApi(request, recurso, token);
  }
  await page.goto("/login");
  await page.getByLabel("E-mail").fill(USUARIA.email);
  await page.getByLabel("Senha").fill(USUARIA.senha);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page
    .getByRole("navigation", { name: "Principal" })
    .getByRole("link", { name: "Minhas reservas" })
    .click();
  const itens = page
    .getByRole("region", { name: "Próximas" })
    .getByRole("listitem")
    .filter({ hasText: recurso.nome_recurso });
  await expect(itens).toHaveCount(RESERVAS);
  // A condição: a página passa da tela. Sem ela, o teste passaria verde com o defeito.
  await expect(itens.last()).not.toBeInViewport();

  // No topo: a barra não pode ter esticado com a página.
  await conferirBarraAVista(page);

  // No fim: a barra não pode ter rolado junto com a página.
  await itens.last().scrollIntoViewIfNeeded();
  await conferirBarraAVista(page);
});
