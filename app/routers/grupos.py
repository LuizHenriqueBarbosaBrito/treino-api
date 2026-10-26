from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db, usuario_atual
from ..models import GrupoMuscular
from ..schemas import GrupoCreate, GrupoOut

router = APIRouter(prefix="/grupos", tags=["Grupos musculares"])


@router.get("", response_model=list[GrupoOut])
def listar_grupos(db: Session = Depends(get_db)):
    return db.scalars(select(GrupoMuscular).order_by(GrupoMuscular.nome)).all()


@router.post("", response_model=GrupoOut, status_code=201, dependencies=[Depends(usuario_atual)])
def criar_grupo(dados: GrupoCreate, db: Session = Depends(get_db)):
    if db.scalar(select(GrupoMuscular).where(GrupoMuscular.nome == dados.nome)):
        raise HTTPException(409, "Já existe um grupo muscular com esse nome.")
    grupo = GrupoMuscular(nome=dados.nome)
    db.add(grupo)
    db.commit()
    db.refresh(grupo)
    return grupo


@router.delete("/{grupo_id}", status_code=204, dependencies=[Depends(usuario_atual)])
def excluir_grupo(grupo_id: int, db: Session = Depends(get_db)):
    grupo = db.get(GrupoMuscular, grupo_id)
    if not grupo:
        raise HTTPException(404, "Grupo muscular não encontrado.")
    if grupo.exercicios:
        raise HTTPException(409, "Não é possível excluir: há exercícios vinculados a este grupo.")
    db.delete(grupo)
    db.commit()
    return Response(status_code=204)
