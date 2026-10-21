import { USUARIA } from "./ambiente.ts";
import { entrarPelaApi, reservarAmanhaPelaApi } from "./api.ts";
import { amanhaNoFuso } from "./datas.ts";
import { expect, test } from "./fixtures.ts";
import { entrarPelaTela } from "./tela.ts";

// Critério de pronto da Etapa 7: reservar um horário que outra pessoa acabou de pegar
// mostra uma mensagem clara, vinda do 409 da EXCLUDE.

test("reservar um horário que outra pessoa acabou de pegar mostra o aviso do conflito", async ({
  page,
  request,
  recurso,
}) => {
  await page.goto("/login");
  await entrarPelaTela(page, USUARIA);
  await expect(page).toHaveURL("/recursos");
  await page.goto(
    `/recursos/${recurso.id_recurso}?dia=${amanhaNoFuso(recurso.fuso)}`,
  );
  const cartao = page
    .getByRole("region", { name: "Horários livres" })
    .getByRole("listitem");
  await cartao.getByRole("button", { name: "Reservar" }).click();
  // O formulário aberto antes da outra reserva: a tela ainda mostra a lacuna inteira.
  await expect(page.getByLabel("Início")).toBeVisible();
  const token = await entrarPelaApi(request, USUARIA);
  await reservarAmanhaPelaApi(request, recurso, token);

  await cartao.getByRole("button", { name: "Confirmar reserva" }).click();

  await expect(
    page
      .getByRole("status")
      .filter({ hasText: "Esse horário acabou de ser reservado" }),
  ).toBeVisible();
});
