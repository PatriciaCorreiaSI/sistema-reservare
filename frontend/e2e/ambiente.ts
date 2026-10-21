// O que o config e os testes precisam saber igual, escrito num lugar só.
// O fuso da API (FUSO_FUNCIONAMENTO) e o do navegador (timezoneId): o runner do CI
// é UTC, e a tela calcularia "hoje" num fuso e a API em outro.
export const FUSO = "America/Sao_Paulo";

// O primeiro admin do banco do e2e, criado pelo criar_admin a cada rodada. Dado de
// teste, não segredo: o banco é zerado antes de cada rodada.
export const ADMIN = {
  nome: "Admin do e2e",
  email: "admin@teste.com",
  senha: "senha-do-admin-e2e",
};

// Portas próprias: a :8000 e a :5173 são as de desenvolvimento.
export const URL_DA_API = "http://127.0.0.1:8001";
export const URL_DO_FRONT = "http://localhost:5174";

// A usuária comum dos testes, criada pelo projeto de setup.
export const USUARIA = {
  nome: "Ana do e2e",
  email: "ana@teste.com",
  senha: "senha-da-ana-e2e",
};

// A segunda usuária comum: quem entra depois da primeira, na mesma aba.
export const OUTRA_USUARIA = {
  nome: "Bia do e2e",
  email: "bia@teste.com",
  senha: "senha-da-bia-e2e",
};
