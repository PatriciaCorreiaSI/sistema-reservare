import { QueryClient } from "@tanstack/react-query";

// O QueryClient é o cache do estado de servidor: um só para o app inteiro.
// Mora num módulo próprio, e não no main.tsx, para que o código fora de componente
// (o middleware do auth.ts) também o alcance. Dentro de componente, continua
// chegando pelo provider (useQueryClient).
export const queryClient = new QueryClient();
