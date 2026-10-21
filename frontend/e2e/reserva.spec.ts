import { USUARIA } from "./ambiente.ts";
import { amanhaNoFuso } from "./datas.ts";
import { expect, test } from "./fixtures.ts";
import { entrarPelaTela } from "./tela.ts";

test("logar, reservar, ver em minhas reservas e cancelar", async ({
  page,
  recurso,
}) => {
  // Logar
  await page.goto("/login");
  await entrarPelaTela(page, USUARIA);
  await expect(page).toHaveURL("/recursos");

  // Escolher o recurso e o dia: amanhã é sempre futuro e, com o recurso novo, vazio.
  await page.getByRole("link", { name: recurso.nome_recurso }).click();
  const horariosLivres = page.getByRole("region", { name: "Horários livres" });
  await expect(horariosLivres).toBeVisible();
  await page.getByLabel("Ir para a data").fill(amanhaNoFuso(recurso.fuso));

  // Reservar: a primeira lacuna que tem o botão serve.
  const botaoReservar = page.getByRole("button", {
    name: "Reservar",
    exact: true,
  });
  const lacuna = horariosLivres
    .getByRole("listitem")
    .filter({ has: botaoReservar })
    .first();
  await lacuna.getByRole("button", { name: "Reservar", exact: true }).click();
  await page.getByRole("button", { name: "Confirmar reserva" }).click();
  await expect(
    page.getByRole("status").filter({ hasText: "Reserva feita" }),
  ).toBeVisible();

  // Ver em minhas reservas
  await page
    .getByRole("navigation", { name: "Principal" })
    .getByRole("link", { name: "Minhas reservas" })
    .click();
  const proximas = page.getByRole("region", { name: "Próximas" });
  const reserva = proximas
    .getByRole("listitem")
    .filter({ hasText: recurso.nome_recurso });
  await expect(reserva).toBeVisible();

  // Cancelar
  await reserva.getByRole("button", { name: "Cancelar reserva" }).click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Confirmar cancelamento" })
    .click();
  await expect(
    page
      .getByRole("status")
      .filter({ hasText: `Reserva de ${recurso.nome_recurso}` }),
  ).toBeVisible();
  await expect(
    page
      .getByRole("region", { name: "Anteriores" })
      .getByRole("listitem")
      .filter({ hasText: recurso.nome_recurso }),
  ).toBeVisible();
  await expect(reserva).toHaveCount(0);
});
