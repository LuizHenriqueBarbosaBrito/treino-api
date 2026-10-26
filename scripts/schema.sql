-- Script equivalente ao que o ORM (SQLAlchemy) gera automaticamente na inicialização.
-- Útil para criar o banco manualmente (SQLite/PostgreSQL com pequenos ajustes de tipo).

CREATE TABLE usuarios (
    id          INTEGER PRIMARY KEY,
    username    VARCHAR(30)  NOT NULL UNIQUE,
    senha_hash  VARCHAR(100) NOT NULL,
    criado_em   DATETIME     NOT NULL
);

CREATE TABLE grupos_musculares (
    id    INTEGER PRIMARY KEY,
    nome  VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE exercicios (
    id                 INTEGER PRIMARY KEY,
    nome               VARCHAR(100) NOT NULL UNIQUE,
    descricao          TEXT,
    equipamento        VARCHAR(60),
    nivel              VARCHAR(20)  NOT NULL DEFAULT 'iniciante',
    series_padrao      INTEGER      NOT NULL DEFAULT 3,
    repeticoes_padrao  INTEGER      NOT NULL DEFAULT 10,
    criado_em          DATETIME     NOT NULL,
    grupo_muscular_id  INTEGER      NOT NULL REFERENCES grupos_musculares (id)
);

CREATE INDEX ix_exercicios_nome ON exercicios (nome);
