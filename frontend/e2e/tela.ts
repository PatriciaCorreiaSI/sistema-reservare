import type { Page } from "@playwright/test";

// O login pela tela, como a pessoa faz. Sem o goto: quem chama decide se abre o
// /login pela URL ou se chegou lá levada pelo app (recarregar zeraria o cache).
export async function entrarPelaTela(
  page: Page,
  pessoa: { email: string; senha: string },
) {
  await page.getByLabel("E-mail").fill(pessoa.email);
  await page.getByLabel("Senha").fill(pessoa.senha);
  await page.getByRole("button", { name: "Entrar" }).click();
}
