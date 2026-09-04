CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE usuario(
    id_usuario INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    privilegio_usuario VARCHAR(15) NOT NULL,
    nome_usuario VARCHAR(30) NOT NULL,
    email_usuario VARCHAR(50) NOT NULL UNIQUE,
    senha_usuario_hash VARCHAR(100) NOT NULL,
    status_usuario VARCHAR(30) NOT NULL,
    CONSTRAINT usuario_status CHECK (status_usuario IN ('ativo', 'inativo')),
    CONSTRAINT usuario_privilegio CHECK (privilegio_usuario IN ('admin', 'usuario'))
);

COMMENT ON COLUMN usuario.senha_usuario_hash IS 'Hash da senha do usuário, gerada com Argon 2';

CREATE TABLE recurso(
    id_recurso INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nome_recurso VARCHAR(30) NOT NULL,
    ocupacao INT NOT NULL,
    hora_func_inicio TIME NOT NULL,
    hora_func_fim TIME NOT NULL,
    status_recurso VARCHAR(30) NOT NULL,
    CONSTRAINT recurso_status CHECK (status_recurso IN ('ativo', 'inativo')),
    CONSTRAINT recurso_horario_dentro_do_dia CHECK (hora_func_fim > hora_func_inicio),
    CONSTRAINT recurso_ocupacao_positiva CHECK (ocupacao > 0)
);

CREATE TABLE reserva(
    id_reserva INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_usuario INT NOT NULL CONSTRAINT fk_reserva_id_usuario REFERENCES usuario(id_usuario) ON DELETE RESTRICT,
    id_recurso INT NOT NULL CONSTRAINT fk_reserva_id_recurso REFERENCES recurso(id_recurso) ON DELETE RESTRICT,
    convidados INT NOT NULL,
    periodo tstzrange NOT NULL,
    status_reserva VARCHAR(30) NOT NULL,
    cancelada_por_id_usuario INT CONSTRAINT fk_reserva_cancelada_por_id_usuario REFERENCES usuario(id_usuario) ON DELETE RESTRICT,
    cancelada_em TIMESTAMPTZ,
    CONSTRAINT reserva_sem_sobreposicao EXCLUDE USING gist (id_recurso WITH =,  periodo WITH &&) WHERE (cancelada_em IS NULL),
    CONSTRAINT reserva_formato_semiaberto CHECK (
        NOT isempty(periodo) AND lower_inc(periodo) AND NOT upper_inc(periodo) 
        AND NOT upper_inf(periodo) AND NOT lower_inf(periodo)
    ),
    CONSTRAINT reserva_convidados_positivos CHECK (convidados > 0),
    CONSTRAINT reserva_status CHECK (status_reserva IN ('confirmada', 'cancelada')),
    CONSTRAINT reserva_cancelamento CHECK (
        (status_reserva = 'cancelada' AND cancelada_em IS NOT NULL AND cancelada_por_id_usuario IS NOT NULL) OR 
        (status_reserva = 'confirmada' AND cancelada_em IS NULL AND cancelada_por_id_usuario IS NULL)
    )
);

CREATE INDEX ix_reserva_id_usuario ON reserva(id_usuario);
CREATE INDEX ix_reserva_id_recurso ON reserva(id_recurso);
CREATE INDEX ix_reserva_cancelada_por_id_usuario ON reserva(cancelada_por_id_usuario);