from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.kernel.infrastructure.database import get_db
from ..application.dto import CriarAvaliacaoRequest, SubmeterTentativaRequest, TentativaResponse
from ..application.use_cases import CriarAvaliacao, SubmeterTentativa
from ..infrastructure.persistence import RepositorioDeAvaliacaoSQLite, RepositorioDeTentativaSQLite

router = APIRouter()


def _repo_avaliacao(db: Session = Depends(get_db)):
    return RepositorioDeAvaliacaoSQLite(db)


def _repo_tentativa(db: Session = Depends(get_db)):
    return RepositorioDeTentativaSQLite(db)


@router.post("/", status_code=201)
def criar_avaliacao(request: CriarAvaliacaoRequest, repo=Depends(_repo_avaliacao)):
    avaliacao = CriarAvaliacao(repo).executar(request)
    return {"id": avaliacao.id, "curso_id": avaliacao.curso_id, "titulo": avaliacao.titulo}


@router.post("/{avaliacao_id}/tentativas", response_model=TentativaResponse, status_code=201)
async def submeter_tentativa(
    avaliacao_id: str,
    request: SubmeterTentativaRequest,
    repo_av=Depends(_repo_avaliacao),
    repo_tent=Depends(_repo_tentativa),
):
    try:
        return await SubmeterTentativa(repo_av, repo_tent).executar(avaliacao_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))