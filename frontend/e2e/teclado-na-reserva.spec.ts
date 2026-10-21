import type { Page } from "@playwright/test";
import type { components } from "../src/api/tipos.ts";
import { USUARIA } from "./ambiente.ts";
import { entrarPelaApi, reservarAmanhaPelaApi } from "./api.ts";
import { amanhaNoFuso } from "./datas.ts";
import { expect, test } from "./fixtures.ts";
import { entrarPelaTela } from "./tela.ts";

// No cartão de uma lacuna, o foco acompanha quem usa só o teclado.
// Cada ação é disparada no próprio botão; o que se confere é onde o foco para depois.

type Recurso = components["schemas"]["RecursoResposta"];

async function entrarEAbrirAmanha(page: Page, recurso: Recurso) {
  await page.goto("/login");
  await entrarPelaTela(page, USUARIA);
  await expect(page).toHaveURL("/recursos");
  await page.goto(
    `/recursos/${recurso.id_recurso}?dia=${amanhaNoFuso(recurso.fuso)}`,
  );
}

function cartoes(page: Page) {
  return page
    .getByRole("region", { name: "Horários livres" })
    .getByRole("listitem");
}

test("abrir o cartão põe o foco no início", async ({ page, recurso }) => {
  await entrarEAbrirAmanha(page, recurso);

  await cartoes(page).getByRole("button", { name: "Reservar" }).press("Enter");

  await expect(page.getByLabel("Início")).toBeFocused();
});

test("cancelar devolve o foco ao reservar do mesmo cartão", async ({
  page,
  request,
  recurso,
}) => {
  // Uma reserva uma hora depois da abertura parte o dia em dois cartões; o teste usa
  // o segundo, para só passar se o foco voltar ao cartão certo, e não ao primeiro.
  const token = await entrarPelaApi(request, USUARIA);
  await reservarAmanhaPelaApi(request, recurso, token, 60);
  await entrarEAbrirAmanha(page, recurso);
  await expect(cartoes(page)).toHaveCount(2);
  await cartoes(page)
    .last()
    .getByRole("button", { name: "Reservar" })
    .press("Enter");

  await cartoes(page).getByRole("button", { name: "Cancelar" }).press("Enter");

  const reservarDoSegundo = cartoes(page)
    .last()
    .getByRole("button", { name: "Reservar" });
  await expect(reservarDoSegundo).toBeFocused();
  // O foco devolvido serve para seguir: o Enter vai para onde o foco está e abre o
  // cartão de novo. Visível, e não focado: o foco no início é o primeiro teste.
  await page.keyboard.press("Enter");
  await expect(page.getByLabel("Início")).toBeVisible();
});

test("confirmar leva o foco à tarja do aviso", async ({ page, recurso }) => {
  await entrarEAbrirAmanha(page, recurso);
  await cartoes(page).getByRole("button", { name: "Reservar" }).press("Enter");

  await cartoes(page)
    .getByRole("button", { name: "Confirmar reserva" })
    .press("Enter");

  await expect(
    page.getByRole("status").filter({ hasText: "Reserva feita" }),
  ).toBeFocused();
});
