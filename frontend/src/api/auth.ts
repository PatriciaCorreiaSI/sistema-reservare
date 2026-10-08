import { useMutation } from "@tanstack/react-query";
import { cliente } from "./cliente";
import { guardarAccessToken } from "./sessao";
import type { components } from "./tipos";

type LoginEntrada = components["schemas"]["LoginEntrada"];

export function useLogin() {
  return useMutation({
    mutationFn: async (credenciais: LoginEntrada) => {
      const { data, response } = await cliente.POST("/api/auth/login", {
        body: credenciais,
      });
      if (!data) {
        throw new Error(`Login recusado: ${response.status}`);
      }
      return data;
    },
    onSuccess: (token) => {
      guardarAccessToken(token.access_token);
    },
  });
}
