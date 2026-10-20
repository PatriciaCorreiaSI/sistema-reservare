import { expect, type APIRequestContext } from "@playwright/test";
import type { components } from "../src/api/tipos.ts";
import { ADMIN } from "./ambiente.ts";
import { amanhaNoFuso } from "./datas.ts";

type Schemas = components["schemas"];

const MINUTO_MS = 60 * 1000;
const MEIA_HORA_MS = 30 * MINUTO_MS;

// Preparação pela API, como nos testes do backend: o caminho mais direto até o
// estado de que o teste precisa. O teste em si age pela tela.
export async function entrarPelaApi(
  request: APIRequestContext,
  pessoa: { email: string; senha: string },
): Promise<string> {
  const resposta = await request.post("/api/auth/login", {
    data: {
      email_usuario: pessoa.email,
      senha: pessoa.senha,
    } satisfies Schemas["LoginEntrada"],
  });
  expect(resposta.status()).toBe(200);
  const corpo: Schemas["TokenResposta"] = await resposta.json();
  return corpo.access_token;
}

export async function tokenDoAdmin(
  request: APIRequestContext,
): Promise<string> {
  return entrarPelaApi(request, ADMIN);
}

// Nome único: o retry não zera o banco, e cada teste precisa do seu recurso.
export async function criarRecursoPelaApi(
  request: APIRequestContext,
): Promise<Schemas["RecursoResposta"]> {
  const token = await tokenDoAdmin(request);
  const resposta = await request.post("/api/recursos", {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      nome_recurso: `Sala e2e ${crypto.randomUUID().slice(0, 8)}`,
      ocupacao: 4,
      hora_func_inicio: "08:00:00",
      hora_func_fim: "18:00:00",
    } satisfies Schemas["RecursoCriar"],
  });
  expect(resposta.status()).toBe(201);
  return resposta.json();
}

// Meia hora na primeira lacuna de amanhã, no começo dela ou alguns minutos depois
// (para deixar um cartão livre antes). O início vem da API, como instante: somar
// milissegundos a ele evita montar instante a partir de hora local.
export async function reservarAmanhaPelaApi(
  request: APIRequestContext,
  recurso: Schemas["RecursoResposta"],
  token: string,
  minutosDepoisDoInicio = 0,
): Promise<Schemas["ReservaResposta"]> {
  const autorizacao = { Authorization: `Bearer ${token}` };
  const livres = await request.get(
    `/api/recursos/${recurso.id_recurso}/disponibilidade`,
    {
      headers: autorizacao,
      params: { dia: amanhaNoFuso(recurso.fuso) },
    },
  );
  expect(livres.status()).toBe(200);
  const { lacunas }: Schemas["DisponibilidadeResposta"] = await livres.json();
  const inicio = new Date(
    Date.parse(lacunas[0].inicio) + minutosDepoisDoInicio * MINUTO_MS,
  ).toISOString();
  const fim = new Date(Date.parse(inicio) + MEIA_HORA_MS).toISOString();
  const resposta = await request.post("/api/reservas", {
    headers: autorizacao,
    data: {
      id_recurso: recurso.id_recurso,
      convidados: 1,
      inicio,
      fim,
    } satisfies Schemas["ReservaCriar"],
  });
  expect(resposta.status()).toBe(201);
  return resposta.json();
}

export async function cancelarPelaApi(
  request: APIRequestContext,
  reserva: Schemas["ReservaResposta"],
  token: string,
): Promise<void> {
  const resposta = await request.post(
    `/api/reservas/${reserva.id_reserva}/cancelar`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  expect(resposta.status()).toBe(200);
}
