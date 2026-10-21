import type { APIRequestContext, Page } from "@playwright/test";
import type { components } from "../src/api/tipos.ts";
import { OUTRA_USUARIA, USUARIA } from "./ambiente.ts";
import { entrarPelaApi, reservarAmanhaPelaApi } from "./api.ts";
import { expect, test } from "./fixtures.ts";
import { entrarPelaTela } from "./tela.ts";

// Quem entra depois de outra pessoa, na mesma aba, não vê os dados
// dela. O cache do TanStack query vive na memória da página; por isso os dois testes
// nunca recarregam: só uma página que continua aberta guarda o que a anterior viu.

type Recurso = components["schemas"]["RecursoResposta"];

function menu(page: Page) {
  return page.getByRole("navigation", { name: "Principal" });
}

// A primeira pessoa vê a reserva dela em minhas reservas: a lista entra no cache.
async function anaVeAReservaDela(
  page: Page,
  request: APIRequestContext,
  recurso: Recurso,
) {
  const token = await entrarPelaApi(request, USUARIA);
  await reservarAmanhaPelaApi(request, recurso, token);
  await page.goto("/login");
  await entrarPelaTela(page, USUARIA);
  await menu(page).getByRole("link", { name: "Minhas reservas" }).click();
  await expect(
    page
      .getByRole("region", { name: "Próximas" })
      .getByRole("listitem")
      .filter({ hasText: recurso.nome_recurso }),
  ).toBeVisible();
}

// A segunda pessoa abre minhas reservas com a lista segurada no caminho: o handler
// nunca responde. Enquanto a lista não chega, a tela só pode mostrar o que já
// estava no cache; sem o cache, o que aparece é o "Carregando". Sem segurar, a lista
// nova trocaria a velha em milissegundos, e o teste passaria sem ver o defeito.
async function biaAbreMinhasReservasComAListaSegurada(page: Page) {
  await page.route(
    (url) => url.pathname === "/api/reservas",
    () => {},
  );
  await menu(page).getByRole("link", { name: "Minhas reservas" }).click();
}

function carregando(page: Page) {
  return page.getByRole("status").filter({ hasText: "Carregando reservas" });
}

test("depois de sair, quem entra não vê as reservas de quem saiu", async ({
  page,
  request,
  recurso,
}) => {
  await anaVeAReservaDela(page, request, recurso);
  await page.getByRole("button", { name: "Sair" }).click();
  await expect(page).toHaveURL("/login");
  await entrarPelaTela(page, OUTRA_USUARIA);
  await expect(page).toHaveURL("/recursos");

  await biaAbreMinhasReservasComAListaSegurada(page);

  await expect(carregando(page)).toBeVisible();
});

test("depois de a sessão vencer com a tela aberta, quem entra não vê as reservas da anterior", async ({
  page,
  context,
  request,
  recurso,
}) => {
  await anaVeAReservaDela(page, request, recurso);
  // A sessão acaba sem recarregar a página. Sem o cookie, o refresh dá 401 de
  // verdade; o access ainda valeria 15 minutos, então o próximo pedido leva o 401 que
  // o servidor daria a um access vencido. Ir a recursos monta a lista, que é velha
  // (staleTime = 0) e se busca de novo: é esse pedido.
  await context.clearCookies();
  await page.route(
    (url) => url.pathname === "/api/recursos",
    (rota) => rota.fulfill({ status: 401 }),
    { times: 1 },
  );
  await menu(page).getByRole("link", { name: "Recursos" }).click();
  await expect(page).toHaveURL("/login");
  await entrarPelaTela(page, OUTRA_USUARIA);
  await expect(page).toHaveURL("/recursos");

  await biaAbreMinhasReservasComAListaSegurada(page);

  await expect(carregando(page)).toBeVisible();
});
