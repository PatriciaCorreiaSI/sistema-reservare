import { useQuery } from "@tanstack/react-query";
import { cliente } from "./cliente";
import { ErroDaApi } from "./erro";

export function useRecursos() {
  return useQuery({
    queryKey: ["recursos"],
    queryFn: async () => {
      // 100 é o teto do `limite` na API; o padrão (20) cortaria a lista em silêncio.
      const { data, response } = await cliente.GET("/api/recursos", {
        params: { query: { limite: 100 } },
      });
      if (!data) {
        throw new ErroDaApi(response, "Listagem recusada");
      }
      return data;
    },
  });
}

// Repetir só o que pode dar certo na segunda vez: falha de servidor ou de rede. Um 4xx
// é resposta definitiva (o recurso não existe), e repetir só atrasa a mensagem.
function repetirSeServidor(falhas: number, erro: Error): boolean {
  if (erro instanceof ErroDaApi && erro.status < 500) {
    return false;
  }
  return falhas < 3;
}

export function useRecurso(idRecurso: number) {
  return useQuery({
    queryKey: ["recursos", idRecurso],
    queryFn: async () => {
      const { data, response } = await cliente.GET(
        "/api/recursos/{id_recurso}",
        { params: { path: { id_recurso: idRecurso } } },
      );
      if (!data) {
        throw new ErroDaApi(response, "Recurso recusado");
      }
      return data;
    },
    retry: repetirSeServidor,
  });
}

// A chave começa por ["recursos", id]: invalidar o recurso leva a disponibilidade junto.
export function useDisponibilidade(idRecurso: number, dia: string) {
  return useQuery({
    queryKey: ["recursos", idRecurso, "disponibilidade", dia],
    queryFn: async () => {
      const { data, response } = await cliente.GET(
        "/api/recursos/{id_recurso}/disponibilidade",
        { params: { path: { id_recurso: idRecurso }, query: { dia } } },
      );
      if (!data) {
        throw new ErroDaApi(response, "Disponibilidade recusada");
      }
      return data;
    },
    retry: repetirSeServidor,
  });
}
