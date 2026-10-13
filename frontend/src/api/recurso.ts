import { useQuery } from "@tanstack/react-query";
import { cliente } from "./cliente";

export function useRecursos() {
  return useQuery({
    queryKey: ["recursos"],
    queryFn: async () => {
      // 100 é o teto do `limite` na API; o padrão (20) cortaria a lista em silêncio.
      const { data, response } = await cliente.GET("/api/recursos", {
        params: { query: { limite: 100 } },
      });
      if (!data) {
        throw new Error(`Listagem recusada: ${response.status}`);
      }
      return data;
    },
  });
}
