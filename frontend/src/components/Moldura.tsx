import { Link, NavLink, Outlet, useNavigate } from "react-router";
import { useLogout } from "../api/auth";
import { SeletorDeTema } from "./SeletorDeTema";

// O NavLink chama esta função com isActive e põe aria-current="page" sozinho no link da
// tela atual. Sem o `end`, /recursos fica ativo também em /recursos/7.
function itemDoMenu({ isActive }: { isActive: boolean }) {
  return isActive
    ? "rounded-lg bg-destaque-suave px-3.5 py-3 font-bold text-destaque-texto"
    : "rounded-lg px-3.5 py-3 font-medium text-texto-suave hover:bg-sutil hover:text-texto";
}

// Rota de layout dentro da guarda: o que toda tela protegida tem em volta. A guarda
// decide SE a tela aparece; a moldura decide COMO. No celular a barra fica em cima; a
// partir de md (768px) vira a coluna da esquerda.
export function Moldura() {
  const navegar = useNavigate();
  const logout = useLogout();

  const sair = () => {
    logout.mutate(undefined, {
      onSettled: () => navegar("/login", { replace: true }),
    });
  };

  // md:h-svh: a altura da barra passa a ser a da tela, e não a da página.
  // É isso que traz o tema e o "Sair" para o pé da tela.
  return (
    <div className="flex min-h-svh flex-col md:flex-row">
      <header className="flex shrink-0 flex-col gap-6 border-b border-borda p-6 md:sticky md:top-0 md:h-svh md:w-64 md:overflow-y-auto md:border-r md:border-b-0 md:py-8">
        <Link
          to="/recursos"
          className="font-titulo text-2xl font-extrabold tracking-tight text-texto"
        >
          reservare<span className="text-destaque">.</span>
        </Link>
        <nav aria-label="Principal" className="flex gap-1 md:flex-col">
          <NavLink to="/recursos" className={itemDoMenu}>
            Recursos
          </NavLink>
          <NavLink to="/reservas" className={itemDoMenu}>
            Minhas reservas
          </NavLink>
        </nav>
        <div className="flex flex-col gap-3 md:mt-auto">
          <SeletorDeTema />
          <button
            type="button"
            onClick={sair}
            disabled={logout.isPending}
            className="cursor-pointer rounded-lg border border-borda-forte px-3.5 py-3 text-left text-texto hover:bg-sutil disabled:cursor-wait disabled:opacity-60"
          >
            {logout.isPending ? "Saindo…" : "Sair"}
          </button>
        </div>
      </header>
      <main className="min-w-0 flex-1 px-6 py-10 md:px-12">
        <Outlet />
      </main>
    </div>
  );
}
