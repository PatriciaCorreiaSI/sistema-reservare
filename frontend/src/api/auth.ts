import { useMutation } from "@tanstack/react-query";
import type { Middleware } from "openapi-fetch";
import { cliente } from "./cliente";
import {
  esquecerAccessToken,
  guardarAccessToken,
  obterAccessToken,
} from "./sessao";
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
      const { data, response } = await cliente.POST("/api/auth/refresh");
      if (response.status === 401) {
        esquecerAccessToken();
        return false;
      }
      if (!data) {
        throw new Error(`Renovação recusada: ${response.status}`);
      }
      guardarAccessToken(data.access_token);
      return true;
    })().finally(() => {
      renovacaoEmCurso = null;
    });
  }
  return renovacaoEmCurso;
}

// Cópia de cada pedido, feita antes do envio: o fetch consome o corpo do original, e um
// POST repetido sem a cópia sairia vazio. A chave é o id que o openapi-fetch dá a cada
// pedido, o mesmo no onRequest e no onResponse.
const copias = new Map<string, Request>();

// 401 com access vencido → renova (uma vez só, pelo single-flight) → repete o pedido.
// Rotas de /api/auth ficam de fora: o 401 do login é senha errada, e do refresh é
// sessão acabada: renovar dentro dele seria um laço.
const renovaNo401: Middleware = {
  onRequest({ request, id }) {
    copias.set(id, request.clone());
    return undefined;
  },
  async onResponse({ response, schemaPath, id, options }) {
    const copia = copias.get(id);
    copias.delete(id);
    if (
      response.status !== 401 ||
      schemaPath.startsWith("/api/auth/") ||
      !copia
    ) {
      return response;
    }
    const renovou = await renovarSessao();
    if (!renovou) {
      return response;
    }
    copia.headers.set("Authorization", `Bearer ${obterAccessToken()}`);
    return options.fetch(copia);
  },
  onError({ id }) {
    copias.delete(id);
    return undefined;
  },
};

cliente.use(renovaNo401);
