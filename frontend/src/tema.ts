import { useState } from "react";

export type Tema = "claro" | "escuro";

// O tema inicial já foi decidido pelo script do index.html, antes de o React existir:
// o hook só lê o que está no <html>. Cada troca escreve nos dois lugares, o atributo
// (que o CSS olha) e o localStorage (que o próximo carregamento lê).
function temaDoDocumento(): Tema {
  return document.documentElement.dataset.tema === "escuro"
    ? "escuro"
    : "claro";
}

export function useTema() {
  const [tema, setTema] = useState<Tema>(temaDoDocumento);

  const escolher = (novo: Tema) => {
    document.documentElement.dataset.tema = novo;
    try {
      localStorage.setItem("tema", novo);
    } catch {
      // Sem armazenamento (aba privada): a escolha vale só até fechar a aba.
    }
    setTema(novo);
  };

  return { tema, escolher };
}
