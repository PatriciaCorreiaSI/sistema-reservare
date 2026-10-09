import { useMutation } from "@tanstack/react-query";
import { cliente } from "./cliente";
import { esquecerAccessToken, guardarAccessToken } from "./sessao";
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

// Uma renovação por vez (single-flight). O backend rotaciona o refresh a cada uso e
// trata um refresh já usado como roubo: revoga a família inteira (ADR 0023). Duas
// renovações simultâneas levariam o mesmo cookie, e a segunda deslogaria a usuária.
let renovacaoEmCurso: Promise<boolean> | null = null;

export function renovarSessao(): Promise<boolean> {
  if (!renovacaoEmCurso) {
    renovacaoEmCurso = (async () => {
      const { data } = await cliente.POST("/api/auth/refresh");
      if (!data) {
        esquecerAccessToken();
        return false;
      }
      guardarAccessToken(data.access_token);
      return true;
    })().finally(() => {
      renovacaoEmCurso = null;
    });
  }
  return renovacaoEmCurso;
}
