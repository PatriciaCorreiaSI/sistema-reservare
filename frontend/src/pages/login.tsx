import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router";
import { z } from "zod";
import { useLogin } from "../api/auth";
import { ErroDaApi } from "../api/erro";
import type { components } from "../api/tipos";
import { Campo } from "../components/Campo";
import { CodigoDoErro } from "../components/CodigoDoErro";
import { SeletorDeTema } from "../components/SeletorDeTema";

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

// Sem biblioteca de ícones por um desenho só. O currentColor herda a cor do botão, então
// acompanha o tema; o aria-hidden tira o desenho do leitor de tela (quem nomeia é o botão).
function IconeDoOlho({ riscado }: { riscado: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className="size-5"
    >
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
      {riscado && <path d="m4 4 16 16" />}
    </svg>
  );
}

export function TelaLogin() {
  const navegar = useNavigate();
  const local = useLocation();
  const login = useLogin();
  const [senhaVisivel, setSenhaVisivel] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(esquemaLogin) });

  const entrar = handleSubmit((credenciais) => {
    // A senha não fica à mostra depois de enviada, nem se a resposta for um erro.
    setSenhaVisivel(false);
    login.mutate(credenciais, {
      onSuccess: () => navegar(destinoDe(local.state), { replace: true }),
    });
  });

  const credenciaisErradas =
    login.error instanceof ErroDaApi && login.error.status === 401;

  return (
    <div className="flex min-h-svh flex-col md:flex-row">
      <section
        aria-label="Sobre o Reservare"
        className="flex flex-col gap-12 bg-destaque-suave p-8 md:w-1/2 md:p-12"
      >
        <span className="font-titulo text-3xl font-extrabold tracking-tight">
          reservare<span className="text-destaque">.</span>
        </span>
        <div className="md:my-auto">
          <p className="max-w-lg font-titulo text-4xl leading-none font-extrabold tracking-tight lg:text-6xl">
            Salas, equipamentos e estações, sem conflito de horário.
          </p>
          <p className="mt-5 max-w-md text-lg leading-relaxed text-texto-suave">
            Duas reservas ativas nunca se sobrepõem no mesmo recurso: quem
            garante é o banco, não a tela.
          </p>
        </div>
      </section>

      <main className="flex flex-1 flex-col p-8 md:p-12">
        <SeletorDeTema className="self-end" />
        <div className="flex flex-1 items-center justify-center py-8">
          <form
            onSubmit={entrar}
            noValidate
            className="flex w-full max-w-sm flex-col gap-5"
          >
            <h1 className="font-titulo text-4xl font-extrabold tracking-tight">
              Entrar
            </h1>
            <Campo
              id="email"
              rotulo="E-mail"
              erro={errors.email_usuario?.message}
            >
              {(props) => (
                <input
                  type="email"
                  autoComplete="username"
                  {...props}
                  {...register("email_usuario")}
                />
              )}
            </Campo>
            <Campo id="senha" rotulo="Senha" erro={errors.senha?.message}>
              {(props) => (
                <div className="relative">
                  {/* Como type="text", o texto passaria pelo corretor do navegador, que
                      pode mandá-lo a um servidor: o spellCheck fica desligado de vez. */}
                  <input
                    type={senhaVisivel ? "text" : "password"}
                    autoComplete="current-password"
                    autoCapitalize="none"
                    spellCheck={false}
                    {...props}
                    {...register("senha")}
                    className={`${props.className} w-full pr-12 [&::-ms-reveal]:hidden`}
                  />
                  {/* type="button": sem ele, o botão dentro do form enviaria o form. */}
                  <button
                    type="button"
                    aria-label="Mostrar senha"
                    aria-pressed={senhaVisivel}
                    onClick={() => setSenhaVisivel((visivel) => !visivel)}
                    className="absolute top-1/2 right-2 -translate-y-1/2 cursor-pointer rounded-lg p-2 text-texto-suave hover:text-texto"
                  >
                    <IconeDoOlho riscado={senhaVisivel} />
                  </button>
                </div>
              )}
            </Campo>
            {login.isError && (
              <p
                role="alert"
                className="rounded-xl bg-perigo-suave px-4 py-3 font-semibold text-perigo"
              >
                {credenciaisErradas
                  ? "E-mail ou senha incorretos."
                  : "Não foi possível entrar agora. Tente de novo em instantes."}
                <CodigoDoErro erro={login.error} />
              </p>
            )}
            <button
              type="submit"
              disabled={login.isPending}
              className="cursor-pointer rounded-full bg-destaque px-6 py-3.5 font-bold text-sobre-destaque hover:opacity-90 disabled:cursor-wait disabled:opacity-60"
            >
              {login.isPending ? "Entrando…" : "Entrar"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
