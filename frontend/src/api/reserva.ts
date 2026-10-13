import { useMutation, useQueryClient } from "@tanstack/react-query";
import { cliente } from "./cliente";
import { ErroDaApi } from "./erro";
import type { components } from "./tipos";

type ReservaCriar = components["schemas"]["ReservaCriar"];

export function useCriarReserva() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (reserva: ReservaCriar) => {
      const { data, response } = await cliente.POST("/api/reservas", {
        body: reserva,
      });
      if (!data) {
        throw new ErroDaApi(response.status, "Reserva recusada");
      }
      return data;
    },
    // Com sucesso, ou com 409 (outra pessoa reservou antes), as lacunas na tela ficaram
    // velhas: invalida tudo sob ["recursos", id], o que inclui a disponibilidade. Devolver
    // a promessa mantém a mutation pendente até a lista nova chegar.
    onSettled: (_dados, _erro, reserva) =>
      queryClient.invalidateQueries({
        queryKey: ["recursos", reserva.id_recurso],
      }),
  });
}
