"""Ponto de entrada da API de treinos."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import models  
from .config import CORS_ORIGINS
from .database import Base, engine
from .routers import auth, exercicios, grupos


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # cria as tabelas se não existirem
    yield


app = FastAPI(
    title="Treino API",
    description="API REST para catalogar exercícios físicos por grupo muscular.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: apenas origens explicitamente autorizadas, métodos e cabeçalhos mínimos
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=False,
)


# Formato único de erro: {"erro": "...", "detalhes": [...]}
@app.exception_handler(StarletteHTTPException)
async def erro_http(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        {"erro": exc.detail}, status_code=exc.status_code, headers=getattr(exc, "headers", None)
    )


@app.exception_handler(RequestValidationError)
async def erro_validacao(request: Request, exc: RequestValidationError):
    detalhes = [
        {"campo": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]), "mensagem": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse({"erro": "Dados inválidos.", "detalhes": detalhes}, status_code=400)


app.include_router(auth.router)
app.include_router(grupos.router)
app.include_router(exercicios.router)


@app.get("/", tags=["Status"])
def raiz():
    return {"api": "Treino API", "documentacao": "/docs"}
