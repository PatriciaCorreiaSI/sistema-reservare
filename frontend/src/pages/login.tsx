import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router";
import { z } from "zod";
import { useLogin } from "../api/auth";
import { ErroDaApi } from "../api/erro";
import type { components } from "../api/tipos";

type LoginEntrada = components["schemas"]["LoginEntrada"];

// Validação no navegador é conveniência: quem garante é a API. O satisfies amarra o
// esquema ao contrato gerado: um campo renomeado na API vira erro de tipo aqui.
const esquemaLogin = z.object({
  email_usuario: z.string().min(1, "Informe o e-mail."),
  senha: z.string().min(1, "Informe a senha."),
}) satisfies z.ZodType<LoginEntrada>;

// De onde a pessoa veio, se a guarda disse (state do histórico, não a URL). O state
// chega como qualquer coisa: confere a forma antes de usar, e na dúvida vai à lista.
function destinoDe(estado: unknown): string {
  if (
    typeof estado == "object" &&
    estado !== null &&
    "de" in estado &&
    typeof estado.de === "string"
  ) {
    return estado.de;
  }
  return "/recursos";
}

export function TelaLogin() {
  const navegar = useNavigate();
  const local = useLocation();
  const login = useLogin();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(esquemaLogin) });

  const entrar = handleSubmit((credenciais) => {
    login.mutate(credenciais, {
      onSuccess: () => navegar(destinoDe(local.state), { replace: true }),
    });
  });

  const credenciaisErradas =
    login.error instanceof ErroDaApi && login.error.status === 401;

  return (
    <main>
      <h1>Entrar</h1>
      <form onSubmit={entrar} noValidate>
        <div>
          <label htmlFor="email">E-mail: </label>
          <input
            id="email"
            type="email"
            autoComplete="username"
            aria-invalid={errors.email_usuario ? true : undefined}
            aria-describedby={errors.email_usuario ? "erro-email" : undefined}
            {...register("email_usuario")}
          />
          {errors.email_usuario && (
            <p id="erro-email">{errors.email_usuario.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="senha">Senha: </label>
          <input
            id="senha"
            type="password"
            autoComplete="current-password"
            aria-invalid={errors.senha ? true : undefined}
            aria-describedby={errors.senha ? "erro-senha" : undefined}
            {...register("senha")}
          />
          {errors.senha && <p id="erro-senha">{errors.senha.message}</p>}
        </div>
        {login.isError && (
          <p role="alert">
            {credenciaisErradas
              ? "E-mail ou senha incorretos."
              : "Não foi possível entrar agora. Tente de novo em instantes."}
          </p>
        )}
        <button type="submit" disabled={login.isPending}>
          {login.isPending ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </main>
  );
}
