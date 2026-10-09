import { useQuery } from "@tanstack/react-query";
import { Navigate, Outlet } from "react-router";
import { renovarSessao } from "../api/auth";
import { obterAccessToken } from "../api/sessao";

// Rota de layout das telas que exigem sessão (ADRs 0023 e 0026). Conveniência, nao
// segurança: quem protege os dados é o 401 da PAI. Ela só evita desenhar uma tela que
// não teria token para buscar o que mostra.
export function RotaProtegida() {
  const temAccess = obterAccessToken() !== null;

  const renovacao = useQuery({
    queryKey: ["sessao"],
    queryFn: renovarSessao,
    enabled: !temAccess,
    retry: false,
    staleTime: Infinity,
  });

  if (temAccess) {
    return <Outlet />;
  }
  if (renovacao.isPending) {
    return <p>Carregando...</p>;
  }
  if (renovacao.isError) {
    return (
      <p>Não foi possível falar com o servidor. Tente de novo em instantes.</p>
    );
  }
  if (!renovacao.data) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}
