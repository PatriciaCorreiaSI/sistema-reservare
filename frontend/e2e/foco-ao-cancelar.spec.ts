import type { Page } from "@playwright/test";
import { USUARIA } from "./ambiente.ts";
import {
  cancelarPelaApi,
  criarRecursoPelaApi,
  entrarPelaApi,
  reservarAmanhaPelaApi,
} from "./api.ts";
import { expect, test } from "./fixtures.ts";
import { entrarPelaTela } from "./tela.ts";

// Compromisso (g), regra 6: o item cancelado muda de seção e desmonta; sem a
// correção de 2026-10-19, o foco caía no <body>.

async function entrarEAbrirMinhasReservas(page: Page) {
  await page.goto("/login");
  await entrarPelaTela(page, USUARIA);
  await page
    .getByRole("navigation", { name: "Principal" })
    .getByRole("link", { name: "Minhas reservas" })
    .click();
}

function proximaDe(page: Page, nomeDoRecurso: string) {
  return page
    .getByRole("region", { name: "Próximas" })
    .getByRole("listitem")
    .filter({ hasText: nomeDoRecurso });
}

async function cancelarNaTela(page: Page, nomeDoRecurso: string) {
  await proximaDe(page, nomeDoRecurso)
    .getByRole("button", { name: "Cancelar reserva" })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Confirmar cancelamento" })
    .click();
}

function tarjaDeSucesso(page: Page, nomeDoRecurso: string) {
  return page
    .getByRole("status")
    .filter({ hasText: `Reserva de ${nomeDoRecurso}` });
}

test("depois de cancelar, o foco vai à tarja do aviso", async ({
  page,
  request,
  recurso,
}) => {
  const token = await entrarPelaApi(request, USUARIA);
  await reservarAmanhaPelaApi(request, recurso, token);

  await entrarEAbrirMinhasReservas(page);
  await cancelarNaTela(page, recurso.nome_recurso);

  await expect(tarjaDeSucesso(page, recurso.nome_recurso)).toBeFocused();
});

test("cancelar o que já foi cancelado leva o foco à tarja do 409", async ({
  page,
  request,
  recurso,
}) => {
  const token = await entrarPelaApi(request, USUARIA);
  const reserva = await reservarAmanhaPelaApi(request, recurso, token);
  await entrarEAbrirMinhasReservas(page);
  await expect(proximaDe(page, recurso.nome_recurso)).toBeVisible();
  // Outra pessoa cancela pelas costas da tela, que ainda mostra a reserva ativa.
  await cancelarPelaApi(request, reserva, token);

  await cancelarNaTela(page, recurso.nome_recurso);

  await expect(
    page
      .getByRole("status")
      .filter({ hasText: "Esta reserva não pode mais ser cancelada" }),
  ).toBeFocused();
});

test("um segundo cancelamento leva o foco à tarja nova", async ({
  page,
  request,
  recurso,
}) => {
  // Recursos diferentes, para cada tarja ter um nome próprio.
  const outroRecurso = await criarRecursoPelaApi(request);
  const token = await entrarPelaApi(request, USUARIA);
  await reservarAmanhaPelaApi(request, recurso, token);
  await reservarAmanhaPelaApi(request, outroRecurso, token);
  await entrarEAbrirMinhasReservas(page);
  await cancelarNaTela(page, recurso.nome_recurso);
  await expect(tarjaDeSucesso(page, recurso.nome_recurso)).toBeVisible();

  await cancelarNaTela(page, outroRecurso.nome_recurso);

  await expect(tarjaDeSucesso(page, outroRecurso.nome_recurso)).toBeFocused();
});
