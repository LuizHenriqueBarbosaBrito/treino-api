import os

# Configuração de teste: deve vir ANTES de importar a aplicação
os.environ["SECRET_KEY"] = "chave-apenas-para-testes"
os.environ["DATABASE_URL"] = "sqlite:///./test_treino.db"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as c:  # o lifespan recria as tabelas
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth(client):
    """Registra um usuário, faz login e devolve o cabeçalho Authorization."""
    client.post("/auth/register", json={"username": "luiz", "password": "senha12345"})
    r = client.post("/auth/login", data={"username": "luiz", "password": "senha12345"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def grupo(client, auth):
    return client.post("/grupos", json={"nome": "Peitoral"}, headers=auth).json()


def novo_exercicio(grupo_id, **extra):
    return {"nome": "Supino reto", "grupo_muscular_id": grupo_id, **extra}
