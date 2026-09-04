-- ----cenário base-------------------------
TRUNCATE reserva, recurso, usuario RESTART IDENTITY CASCADE;
INSERT INTO usuario (privilegio_usuario, nome_usuario, email_usuario, senha_usuario_hash, status_usuario) VALUES
('usuario', 'Maria Silva', 'maria.silva@example.com', 'hashed_ficticio1', 'ativo') RETURNING id_usuario;
INSERT INTO recurso (nome_recurso, ocupacao, hora_func_inicio, hora_func_fim, status_recurso) VALUES
('Sala de Reunião A', 10, '08:00:00', '18:00:00', 'ativo') RETURNING id_recurso;

\warn
\warn '=== Caso 1: sobreposição no mesmo recurso ==='  
\warn '=== esperado:a segunda reserva é RECUSADA (reserva_sem_sobreposicao) ==='
DELETE FROM reserva;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '[2026-09-04 10:00:00+00, 2026-09-04 12:00:00+00)', 'confirmada');
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 3, '[2026-09-04 11:00:00+00, 2026-09-04 13:00:00+00)', 'confirmada');

\warn
\warn '=== Caso 2: reservas enconstadas, no mesmo recurso [10h,12h) e [12h,13h) ==='
\warn '=== esperado: ambas reservas são ACEITAS ==='
DELETE FROM reserva;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '[2026-09-04 10:00:00+00, 2026-09-04 12:00:00+00)', 'confirmada');
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 3, '[2026-09-04 12:00:00+00, 2026-09-04 13:00:00+00)', 'confirmada');

\warn
\warn '=== Caso 3: reservas no mesmo horário, mas em recursos diferentes ==='
\warn '=== esperado: ambas reservas são ACEITAS ==='
DELETE FROM reserva;
INSERT INTO recurso (nome_recurso, ocupacao, hora_func_inicio, hora_func_fim, status_recurso) VALUES
('Sala de Reunião B', 8, '08:00:00', '18:00:00', 'ativo') RETURNING id_recurso;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '[2026-09-04 10:00:00+00, 2026-09-04 12:00:00+00)', 'confirmada');
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 2, 3, '[2026-09-04 10:00:00+00, 2026-09-04 12:00:00+00)', 'confirmada');

\warn
\warn '=== Caso 4: reserva cancelada, seguida de nova reserva no mesmo horário e recurso ==='
\warn '=== esperado: a segunda reserva é ACEITA ==='
DELETE FROM reserva;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '[2026-09-04 10:00:00+00, 2026-09-04 12:00:00+00)', 'confirmada');
UPDATE reserva SET status_reserva = 'cancelada', cancelada_por_id_usuario = 1, cancelada_em = '2026-09-04 09:00:00+00' WHERE id_recurso = 1;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 3, '[2026-09-04 10:00:00+00, 2026-09-04 12:00:00+00)', 'confirmada');

\warn
\warn '=== Caso 5: reserva com período vazio ou sem fim ==='
\warn '=== esperado: a reserva é RECUSADA (reserva_formato_semiaberto) ==='
DELETE FROM reserva;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '[2026-09-04 10:00:00+00,)', 'confirmada');
DELETE FROM reserva;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '[2026-09-04 10:00:00+00, 2026-09-04 10:00:00+00)', 'confirmada');

\warn
\warn '=== Caso 6: reserva com status = "cancelada" sem cancelada_em ==='
\warn '=== esperado: a reserva é RECUSADA (reserva_cancelamento) ==='
DELETE FROM reserva;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '[2026-09-04 10:00:00+00, 2026-09-04 12:00:00+00)', 'cancelada');

\warn
\warn '=== Caso 7: reserva com limites invertidos ou com inclusividade trocada ==='
\warn '=== esperado: a reserva é RECUSADA pelo tipo tstzrange ou (reserva_formato_semiaberto) ==='
DELETE FROM reserva;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '[2026-09-04 12:00:00+00, 2026-09-04 10:00:00+00)', 'confirmada');
DELETE FROM reserva;
INSERT INTO reserva (id_usuario, id_recurso, convidados, periodo, status_reserva) VALUES
(1, 1, 5, '(2026-09-04 10:00:00+00, 2026-09-04 12:00:00+00]', 'confirmada');
