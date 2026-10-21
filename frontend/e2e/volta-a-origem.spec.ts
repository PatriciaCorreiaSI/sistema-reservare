import { USUARIA } from "./ambiente.ts";
import { amanhaNoFuso } from "./datas.ts";
import { expect, test } from "./fixtures.ts";
import { entrarPelaTela } from "./tela.ts";

// Sem sessão (o F5 de quem não entrou, ou um link recebido), a guarda manda ao /login
// guardando de onde a pessoa veio; depois de entrar, ela volta à mesma tela, com o
// ?dia= junto.

test("sem sessão, a guarda manda ao login e o login volta à tela de origem", async ({
  page,
  recurso,
}) => {
  const origem = `/recursos/${recurso.id_recurso}?dia=${amanhaNoFuso(recurso.fuso)}`;
  await page.goto(origem);
  await expect(page).toHaveURL("/login");

  await entrarPelaTela(page, USUARIA);

  await expect(page).toHaveURL(origem);
  await expect(
    page.getByRole("heading", { name: recurso.nome_recurso }),
  ).toBeVisible();
});
