import { useQuery } from "@tanstack/react-query";
import { cliente } from "./cliente";

export function useRecursos() {
  return useQuery({
    queryKey: ["recursos"],
    queryFn: async () => {
      const { data, response } = await cliente.GET("/api/recursos");
      if (!data) {
        throw new Error(`Listagem recusada: ${response.status}`);
      }
      return data;
    },
  });
}
