import { expect, test } from "@playwright/test";
import { entrarPelaTela } from "./tela.ts";

const PESSOA = { email: "ana@exemplo.com", senha: "qualquer-senha" };

test("o botão alterna a senha entre oculta e visível", async ({ page }) => {
  await page.goto("/login");
  const campo = page.getByLabel("Senha", { exact: true });
  const botao = page.getByRole("button", { name: "Mostrar senha" });

  // Com os dois campos válidos: um botão que enviasse o form esconderia a senha.
  await page.getByLabel("E-mail").fill(PESSOA.email);
  await campo.fill(PESSOA.senha);
  await expect(campo).toHaveAttribute("type", "password");

  await botao.click();
  await expect(campo).toHaveAttribute("type", "text");
  await expect(botao).toHaveAttribute("aria-pressed", "true");
  await expect(campo).toHaveValue(PESSOA.senha);

  await botao.click();
  await expect(campo).toHaveAttribute("type", "password");
  await expect(botao).toHaveAttribute("aria-pressed", "false");
});

test("ao enviar, a senha visível volta a ficar oculta", async ({ page }) => {
  await page.route("**/api/auth/login", (rota) =>
    rota.fulfill({
      status: 401,
      json: { detail: "Login, refresh ou access inválidos" },
    }),
  );

  await page.goto("/login");
  await page.getByRole("button", { name: "Mostrar senha" }).click();
  await entrarPelaTela(page, PESSOA);

  await expect(page.getByRole("alert")).toContainText(
    "E-mail ou senha incorretos.",
  );
  await expect(page.getByLabel("Senha", { exact: true })).toHaveAttribute(
    "type",
    "password",
  );
});
