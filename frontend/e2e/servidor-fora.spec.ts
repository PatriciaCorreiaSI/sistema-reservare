import { expect, test } from "@playwright/test";

// Com a API parada, o proxy do Vite responde 502 a todo
// pedido. A guarda precisa dizer que o servidor não respondeu, e não mandar ao
// /login: 502 não é "sem sessão", é "não deu para saber". Sem a correção de
// 2026-10-09, o renovarSessao tratava qualquer recusa como sessão acabada.

test("com a API parada, a guarda avisa do servidor em vez de mandar ao login", async ({
  page,
}) => {
  await page.route(
    (url) => url.pathname.startsWith("/api/"),
    (rota) => rota.fulfill({ status: 502 }),
  );

  await page.goto("/reservas");

  await expect(
    page.getByText("Não foi possível falar com o servidor"),
  ).toBeVisible();
});
