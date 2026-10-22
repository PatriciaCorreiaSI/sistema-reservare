import { expect, test } from "@playwright/test";
import { entrarPelaTela } from "./tela.ts";

// ADR 0029: num 5xx, a tela mostra o X-Request-ID da resposta, o mesmo das linhas de
// log daquele pedido. A API não tem como quebrar de propósito, então o teste segura o
// pedido do login e responde no lugar dela.
const CODIGO = "0123456789abcdef0123456789abcdef";
const PESSOA = { email: "ana@exemplo.com", senha: "qualquer-senha" };

test("num erro do servidor, a tela mostra o código do erro", async ({
  page,
}) => {
  await page.route("**/api/auth/login", (rota) =>
    rota.fulfill({
      status: 500,
      headers: { "X-Request-ID": CODIGO },
      json: { detail: "Erro interno" },
    }),
  );

  await page.goto("/login");
  await entrarPelaTela(page, PESSOA);

  await expect(page.getByRole("alert")).toContainText(
    `Código do erro: ${CODIGO}`,
  );
});

test("num 4xx, a tela explica o erro e não mostra código", async ({ page }) => {
  await page.route("**/api/auth/login", (rota) =>
    rota.fulfill({
      status: 401,
      headers: { "X-Request-ID": CODIGO },
      json: { detail: "Login, refresh ou access inválidos" },
    }),
  );

  await page.goto("/login");
  await entrarPelaTela(page, PESSOA);

  const aviso = page.getByRole("alert");
  await expect(aviso).toContainText("E-mail ou senha incorretos.");
  await expect(aviso).not.toContainText("Código do erro");
});
