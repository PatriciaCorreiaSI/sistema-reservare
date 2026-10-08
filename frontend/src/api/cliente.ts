import createClient, { type Middleware } from "openapi-fetch";
import { obterAccessToken } from "./sessao";
import type { paths } from "./tipos";

// ADR 0025: um cliente só, tipado pelo contrato gerado. Sem baseUrl porque as
// chaves de `paths` já começam com /api  (o prefixo é do back-end, ADR 0024), e
// a URL relativa resolve na origem da página: o Vite encaminha para a API.
export const cliente = createClient<paths>();

const comToken: Middleware = {
  onRequest({ request }) {
    const token = obterAccessToken();
    if (token) {
      request.headers.set("Authorization", `Bearer ${token}`);
    }
    return request;
  },
};

cliente.use(comToken);
