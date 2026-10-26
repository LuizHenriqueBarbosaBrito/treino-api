from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..deps import get_db, usuario_atual
from ..models import Exercicio, GrupoMuscular
from ..schemas import ExercicioCreate, ExercicioOut, ExercicioUpdate, Nivel

router = APIRouter(prefix="/exercicios", tags=["Exercícios"])

# Campos que não aceitam valor nulo em atualizações
CAMPOS_OBRIGATORIOS = {"nome", "nivel", "series_padrao", "repeticoes_padrao", "grupo_muscular_id"}


def _buscar_ou_404(db: Session, exercicio_id: int) -> Exercicio:
    exercicio = db.get(Exercicio, exercicio_id)
    if not exercicio:
        raise HTTPException(404, "Exercício não encontrado.")
    return exercicio


def _garantir_grupo(db: Session, grupo_id: int) -> None:
    if not db.get(GrupoMuscular, grupo_id):
        raise HTTPException(400, f"Grupo muscular {grupo_id} não existe.")


def _garantir_nome_livre(db: Session, nome: str, ignorar_id: int | None = None) -> None:
    existente = db.scalar(select(Exercicio).where(Exercicio.nome == nome))
    if existente and existente.id != ignorar_id:
        raise HTTPException(409, "Já existe um exercício com esse nome.")


@router.get("", response_model=list[ExercicioOut])
def listar_exercicios(
    grupo_id: int | None = Query(None, description="Filtra por grupo muscular"),
    nivel: Nivel | None = Query(None, description="Filtra por nível"),
    busca: str | None = Query(None, min_length=1, description="Trecho do nome"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    consulta = select(Exercicio).options(joinedload(Exercicio.grupo)).order_by(Exercicio.id)
    if grupo_id is not None:
        consulta = consulta.where(Exercicio.grupo_muscular_id == grupo_id)
    if nivel is not None:
        consulta = consulta.where(Exercicio.nivel == nivel)
    if busca:
        consulta = consulta.where(Exercicio.nome.ilike(f"%{busca}%"))
    return db.scalars(consulta.offset(skip).limit(limit)).all()


@router.get("/{exercicio_id}", response_model=ExercicioOut)
def consultar_exercicio(exercicio_id: int, db: Session = Depends(get_db)):
    return _buscar_ou_404(db, exercicio_id)


@router.post("", response_model=ExercicioOut, status_code=201, dependencies=[Depends(usuario_atual)])
def criar_exercicio(dados: ExercicioCreate, db: Session = Depends(get_db)):
    _garantir_grupo(db, dados.grupo_muscular_id)
    _garantir_nome_livre(db, dados.nome)
    exercicio = Exercicio(**dados.model_dump())
    db.add(exercicio)
    db.commit()
    db.refresh(exercicio)
    return exercicio


@router.patch("/{exercicio_id}", response_model=ExercicioOut, dependencies=[Depends(usuario_atual)])
def atualizar_exercicio(exercicio_id: int, dados: ExercicioUpdate, db: Session = Depends(get_db)):
    exercicio = _buscar_ou_404(db, exercicio_id)
    mudancas = dados.model_dump(exclude_unset=True)  # só o que o cliente enviou
    if not mudancas:
        raise HTTPException(400, "Envie ao menos um campo para atualizar.")
    nulos = [c for c in mudancas if c in CAMPOS_OBRIGATORIOS and mudancas[c] is None]
    if nulos:
        raise HTTPException(400, f"Campos não aceitam valor nulo: {', '.join(nulos)}.")
    if "grupo_muscular_id" in mudancas:
        _garantir_grupo(db, mudancas["grupo_muscular_id"])
    if "nome" in mudancas:
        _garantir_nome_livre(db, mudancas["nome"], ignorar_id=exercicio.id)
    for campo, valor in mudancas.items():
        setattr(exercicio, campo, valor)
    db.commit()
    db.refresh(exercicio)
    return exercicio


@router.delete("/{exercicio_id}", status_code=204, dependencies=[Depends(usuario_atual)])
def excluir_exercicio(exercicio_id: int, db: Session = Depends(get_db)):
    exercicio = _buscar_ou_404(db, exercicio_id)
    db.delete(exercicio)
    db.commit()
    return Response(status_code=204)
