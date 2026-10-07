import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // ADR 0024: o navegador só fala com o Vite (:5173). Tudo que começa com /api
    // o Vite repassa à API, sem reescrever o caminho: por isso o cookie do
    // ADR 0023, com Path=/api/auth, chega inteiro. 127.0.0.1, nunca localhost:
    // o Windows resolve localhost para ::1 e o uvicorn escuta só IPv4.
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
