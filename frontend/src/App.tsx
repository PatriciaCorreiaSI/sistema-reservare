import { Navigate, Route, Routes } from "react-router";

function TelaLogin() {
  return <h1>Login</h1>;
}

function TelaRecursos() {
  return <h1>Recursos</h1>;
}

function TelaNaoEncontrada() {
  return <h1>Página não encontrada</h1>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<TelaLogin />} />
      <Route path="/recursos" element={<TelaRecursos />} />
      <Route path="/" element={<Navigate to="/recursos" replace />} />
      <Route path="*" element={<TelaNaoEncontrada />} />
    </Routes>
  );
}
