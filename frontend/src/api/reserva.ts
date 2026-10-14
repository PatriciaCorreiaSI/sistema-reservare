import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cliente } from "./cliente";
import { ErroDaApi } from "./erro";
import type { components } from "./tipos";

type ReservaCriar = components["schemas"]["ReservaCriar"];
type ReservaResposta = components["schemas"]["ReservaResposta"];

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
    // velhas: invalida tudo sob ["recursos", id], o que inclui a disponibilidade. A lista
    // de minhas reservas também mudou. Devolver a promessa mantém a mutation pendente
    // até a lista nova chegar.
    onSettled: (_dados, _erro, reserva) =>
      Promise.all([
        queryClient.invalidateQueries({
          queryKey: ["recursos", reserva.id_recurso],
        }),
        queryClient.invalidateQueries({ queryKey: ["reservas"] }),
      ]),
  });
}

export function useReservas() {
  return useQuery({
    queryKey: ["reservas"],
    queryFn: async () => {
      // 100 é o teto do `limite`. A API ordena por id crescente, então o que passa
      // disso são as reservas mais novas (backlog).
      const { data, response } = await cliente.GET("/api/reservas", {
        params: { query: { limite: 100 } },
      });
      if (!data) {
        throw new ErroDaApi(response.status, "Listagem de reservas recusada");
      }
      return data;
    },
  });
}

// O cancelamento abre uma nova lacuna: invalida a lista de reservas e a disponibilidade do
// recurso. Recebe a reserva inteira, e não só o id, porque precisa do id_recurso.
export function useCancelarReserva(aoRecusar: (erro: Error) => void) {
  const queryClient = useQueryClient();
  const invalidar = (reserva: ReservaResposta) =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: ["reservas"] }),
      queryClient.invalidateQueries({
        queryKey: ["recursos", reserva.id_recurso],
      }),
    ]);
  return useMutation({
    mutationFn: async (reserva: ReservaResposta) => {
      const { data, response } = await cliente.POST(
        "/api/reservas/{id_reserva}/cancelar",
        { params: { path: { id_reserva: reserva.id_reserva } } },
      );
      if (!data) {
        throw new ErroDaApi(response.status, "Cancelamento recusado");
      }
      return data;
    },
    // No sucesso, a promessa devolvida mantém a mutation pendente até a lista nova
    // chegar: a tela continua mostrando "Cancelada" e não pisca de volta a "Confirmada".
    onSuccess: (_dados, reserva) => invalidar(reserva),
    // No erro, a tela tem de voltar já: avisa e busca a lista nova sem esperar por ela.
    // O aviso vai aqui, e não num callback do mutate(): este roda mesmo se o item já
    // tiver saído da tela.
    onError: (erro, reserva) => {
      aoRecusar(erro);
      void invalidar(reserva);
    },
  });
}
