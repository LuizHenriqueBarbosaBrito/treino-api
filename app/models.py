"""Modelos ORM: cada classe é mapeada para uma tabela do banco."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(100))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class GrupoMuscular(Base):
    __tablename__ = "grupos_musculares"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(60), unique=True)

    # Relação 1:N -> um grupo possui vários exercícios
    exercicios: Mapped[list["Exercicio"]] = relationship(back_populates="grupo")


class Exercicio(Base):
    __tablename__ = "exercicios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    equipamento: Mapped[str | None] = mapped_column(String(60), nullable=True)
    nivel: Mapped[str] = mapped_column(String(20), default="iniciante")
    series_padrao: Mapped[int] = mapped_column(Integer, default=3)
    repeticoes_padrao: Mapped[int] = mapped_column(Integer, default=10)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    grupo_muscular_id: Mapped[int] = mapped_column(ForeignKey("grupos_musculares.id"))
    grupo: Mapped[GrupoMuscular] = relationship(back_populates="exercicios")
