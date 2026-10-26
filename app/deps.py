"""Dependências injetadas nas rotas (sessão de banco e usuário autenticado)."""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Usuario
from .security import ler_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def usuario_atual(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    erro = HTTPException(
        status_code=401,
        detail="Token ausente, inválido ou expirado. Faça login em /auth/login.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise erro
    username = ler_token(token)
    if not username:
        raise erro
    usuario = db.scalar(select(Usuario).where(Usuario.username == username))
    if not usuario:
        raise erro
    return usuario
