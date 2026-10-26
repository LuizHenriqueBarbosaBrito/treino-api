"""Schemas Pydantic: definem e validam o formato de entrada e saída (JSON)."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Nivel = Literal["iniciante", "intermediario", "avancado"]


class Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


# ---------- Autenticação ----------
class UsuarioCreate(Base):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")
    # bcrypt considera no máximo 72 bytes da senha
    password: str = Field(min_length=8, max_length=72)


class UsuarioOut(Base):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    criado_em: datetime


class Token(Base):
    access_token: str
    token_type: str = "bearer"


# ---------- Grupo muscular ----------
class GrupoCreate(Base):
    nome: str = Field(min_length=2, max_length=60)


class GrupoOut(Base):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str


# ---------- Exercício ----------
class ExercicioCreate(Base):
    nome: str = Field(min_length=2, max_length=100)
    descricao: str | None = Field(default=None, max_length=500)
    equipamento: str | None = Field(default=None, max_length=60)
    nivel: Nivel = "iniciante"
    series_padrao: int = Field(default=3, ge=1, le=10)
    repeticoes_padrao: int = Field(default=10, ge=1, le=100)
    grupo_muscular_id: int = Field(ge=1)


class ExercicioUpdate(Base):
    """Todos os campos são opcionais: é uma atualização parcial (PATCH)."""

    nome: str | None = Field(default=None, min_length=2, max_length=100)
    descricao: str | None = Field(default=None, max_length=500)
    equipamento: str | None = Field(default=None, max_length=60)
    nivel: Nivel | None = None
    series_padrao: int | None = Field(default=None, ge=1, le=10)
    repeticoes_padrao: int | None = Field(default=None, ge=1, le=100)
    grupo_muscular_id: int | None = Field(default=None, ge=1)


class ExercicioOut(Base):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    descricao: str | None
    equipamento: str | None
    nivel: Nivel
    series_padrao: int
    repeticoes_padrao: int
    grupo: GrupoOut
    criado_em: datetime
