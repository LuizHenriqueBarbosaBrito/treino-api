from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db, usuario_atual
from ..models import Usuario
from ..schemas import Token, UsuarioCreate, UsuarioOut
from ..security import criar_token, gerar_hash, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UsuarioOut, status_code=201)
def registrar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Usuario).where(Usuario.username == dados.username)):
        raise HTTPException(409, "Nome de usuário já está em uso.")
    usuario = Usuario(username=dados.username, senha_hash=gerar_hash(dados.password))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.username == form.username))
    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(
            401, "Usuário ou senha incorretos.", headers={"WWW-Authenticate": "Bearer"}
        )
    return Token(access_token=criar_token(usuario.username))


@router.get("/me", response_model=UsuarioOut)
def quem_sou_eu(usuario: Usuario = Depends(usuario_atual)):
    """Endpoint protegido: devolve os dados do usuário dono do token."""
    return usuario
