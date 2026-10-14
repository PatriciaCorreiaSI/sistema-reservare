import { Navigate, Route, Routes } from "react-router";
import { Moldura } from "./components/Moldura";
import { RotaProtegida } from "./components/RotaProtegida";
import { TelaLogin } from "./pages/login";
import { TelaRecurso } from "./pages/recurso";
import { TelaRecursos } from "./pages/recursos";
import { TelaReservas } from "./pages/reservas";

function TelaNaoEncontrada() {
  return <h1>Página não encontrada</h1>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<TelaLogin />} />
      <Route element={<RotaProtegida />}>
        <Route element={<Moldura />}>
          <Route path="/recursos" element={<TelaRecursos />} />
          <Route path="/recursos/:idRecurso" element={<TelaRecurso />} />
          <Route path="/reservas" element={<TelaReservas />} />
        </Route>
      </Route>
      <Route path="/" element={<Navigate to="/recursos" replace />} />
      <Route path="*" element={<TelaNaoEncontrada />} />
    </Routes>
  );
}
