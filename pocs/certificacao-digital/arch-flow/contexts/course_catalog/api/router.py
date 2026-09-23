from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.kernel.infrastructure.database import get_db
from ..application.dto import CriarCursoRequest, CriarInstrutorRequest, CursoResponse, InstrutorResponse
from ..application.use_cases import BuscarCurso, CriarCurso, CriarInstrutor, ListarCursosPublicados, PublicarCurso
from ..infrastructure.persistence import RepositorioDeCursoSQLite, RepositorioDeInstrutorSQLite

router = APIRouter()


def _repo_curso(db: Session = Depends(get_db)):
    return RepositorioDeCursoSQLite(db)


def _repo_instrutor(db: Session = Depends(get_db)):
    return RepositorioDeInstrutorSQLite(db)


@router.post("/instrutores", response_model=InstrutorResponse, status_code=201)
def criar_instrutor(request: CriarInstrutorRequest, repo=Depends(_repo_instrutor)):
    return CriarInstrutor(repo).executar(request)


@router.post("/cursos", response_model=CursoResponse, status_code=201)
def criar_curso(request: CriarCursoRequest, repo=Depends(_repo_curso)):
    return CriarCurso(repo).executar(request)


@router.get("/cursos", response_model=List[CursoResponse])
def listar_cursos(repo=Depends(_repo_curso)):
    return ListarCursosPublicados(repo).executar()


@router.get("/cursos/{curso_id}", response_model=CursoResponse)
def buscar_curso(curso_id: str, repo=Depends(_repo_curso)):
    resultado = BuscarCurso(repo).executar(curso_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return resultado


@router.post("/cursos/{curso_id}/publicar", response_model=CursoResponse)
def publicar_curso(curso_id: str, repo=Depends(_repo_curso)):
    try:
        return PublicarCurso(repo).executar(curso_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))