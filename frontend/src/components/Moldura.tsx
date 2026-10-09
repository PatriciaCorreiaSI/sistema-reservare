import { Link, Outlet, useNavigate } from "react-router";
import { useLogout } from "../api/auth";

// Rota de layout dentro da guarda: o que toda tela protegida tem em volta. A guarda
// decide SE a tela aparece; a moldura decide COMO.
export function Moldura() {
  const navegar = useNavigate();
  const logout = useLogout();

  const sair = () => {
    logout.mutate(undefined, {
      onSettled: () => navegar("/login", { replace: true }),
    });
  };

  return (
    <>
      <header>
        <nav aria-label="Principal">
          <Link to="/recursos">Recursos</Link>
        </nav>
        <button type="button" onClick={sair} disabled={logout.isPending}>
          {logout.isPending ? "Saindo…" : "Sair"}
        </button>
      </header>
      <main>
        <Outlet />
      </main>
    </>
  );
}
