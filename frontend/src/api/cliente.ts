import createClient from "openapi-fetch";
import type { paths } from "./tipos";

// ADR 0025: um cliente só, tipado pelo contrato gerado. Sem baseUrl porque as
// chaves de `paths` já começam com /api  (o prefixo é do back-end, ADR 0024), e
// a URL relativa resolve na origem da página: o Vite encaminha para a API.
export const cliente = createClient<paths>();
