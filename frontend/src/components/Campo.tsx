import type { ReactNode } from "react";

// O que o Campo calcula e entrega ao controle: o id para onde o rótulo aponta, os dois
// aria-* que ligam a mensagem de erro ao campo, e a aparência.
type PropsDoControle = {
  id: string;
  "aria-invalid": true | undefined;
  "aria-describedby": string | undefined;
  className: string;
};

// Rótulo, controle e erro andam juntos: o htmlFor, o id e o aria-describedby precisam
// combinar, e errar um deles não dá erro nenhum, só cala o leitor de tela. O controle
// (input ou select) vem de quem usa, como uma função que recebe as props prontas.
export function Campo({
  id,
  rotulo,
  erro,
  children,
}: {
  id: string;
  rotulo: string;
  erro?: string | null;
  children: (props: PropsDoControle) => ReactNode;
}) {
  const idDoErro = `${id}-erro`;

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-sm font-bold">
        {rotulo}
      </label>
      {children({
        id,
        "aria-invalid": erro ? true : undefined,
        "aria-describedby": erro ? idDoErro : undefined,
        className:
          "rounded-xl border border-borda-campo bg-campo px-4 py-3.5 text-texto aria-invalid:border-2 aria-invalid:border-perigo",
      })}
      {erro && (
        <p id={idDoErro} className="text-sm font-semibold text-perigo">
          {erro}
        </p>
      )}
    </div>
  );
}
