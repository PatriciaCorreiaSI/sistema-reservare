import { useTema, type Tema } from "../tema";

const OPCOES: { valor: Tema; rotulo: string }[] = [
  { valor: "claro", rotulo: "Claro" },
  { valor: "escuro", rotulo: "Escuro" },
];

// Dois botões de alternância num grupo com nome: o leitor de tela anuncia "Tema, grupo"
// e, em cada botão, se ele está pressionado. O visual de "escolhido" sai do próprio
// aria-pressed, então a aparência e o que se anuncia nunca discordam.
export function SeletorDeTema({ className = "" }: { className?: string }) {
  const { tema, escolher } = useTema();
  return (
    <div
      role="group"
      aria-label="Tema"
      className={`flex rounded-full border border-borda-forte p-1 ${className}`}
    >
      {OPCOES.map(({ valor, rotulo }) => (
        <button
          key={valor}
          type="button"
          aria-pressed={tema === valor}
          onClick={() => escolher(valor)}
          className="flex-1 cursor-pointer rounded-full px-4 py-2.5 text-sm font-semibold text-texto aria-pressed:bg-texto aria-pressed:text-fundo"
        >
          {rotulo}
        </button>
      ))}
    </div>
  );
}
