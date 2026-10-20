import { defineConfig, devices } from "@playwright/test";
import { ADMIN, FUSO, URL_DA_API, URL_DO_FRONT } from "./e2e/ambiente.ts";

// A guarda: sai com 1 se o banco não for o do e2e. Sem ela, este comando copiado
// para um terminal leria o POSTGRES_DB do .env e zeraria o de desenvolvimento.
const GUARDA =
  "uv run python -c \"import os, sys; os.environ.get('POSTGRES_DB') == 'reservare_e2e' or sys.exit('Guarda: POSTGRES_DB precisa ser reservare_e2e')\"";

export default defineConfig({
  testDir: "./e2e",
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: URL_DO_FRONT,
    timezoneId: FUSO,
    trace: "on-first-retry",
  },
  projects: [
    // Roda antes de todos: cria pela API o que todo teste espera encontrar.
    { name: "setup", testMatch: /.*\.setup\.ts/ },
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      dependencies: ["setup"],
    },
  ],
  webServer: [
    {
      command: [
        GUARDA,
        "uv run alembic downgrade base",
        "uv run alembic upgrade head",
        "uv run python -m app.comandos.criar_admin",
        "uv run uvicorn app.main:app --port 8001",
      ].join(" && "),
      cwd: "../backend",
      url: `${URL_DA_API}/health`,
      reuseExistingServer: false,
      env: {
        POSTGRES_DB: "reservare_e2e",
        DB_HOST: "127.0.0.1",
        FUSO_FUNCIONAMENTO: FUSO,
        ADMIN_NOME: ADMIN.nome,
        ADMIN_EMAIL: ADMIN.email,
        ADMIN_SENHA: ADMIN.senha,
      },
    },
    {
      command: "npm run dev -- --port 5174 --strictPort",
      url: URL_DO_FRONT,
      reuseExistingServer: false,
      env: { ALVO_DA_API: URL_DA_API },
    },
  ],
});
