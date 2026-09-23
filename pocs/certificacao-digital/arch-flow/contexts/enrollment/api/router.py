from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.kernel.infrastructure.database import get_db
from ..application.dto import ConcluirAulaRequest, MatricularRequest, MatriculaResponse
from ..application.use_cases import BuscarMatricula, ConcluirAula, ListarMatriculasEstudante, MatricularEstudante
from ..infrastructure.persistence import RepositorioDeMatriculaSQLite

router = APIRouter()


def _repo(db: Session = Depends(get_db)):
    return RepositorioDeMatriculaSQLite(db)


@router.post("/", response_model=MatriculaResponse, status_code=201)
def matricular(request: MatricularRequest, repo=Depends(_repo)):
    try:
        return MatricularEstudante(repo).executar(request)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/estudante/{estudante_id}")
def listar_matriculas(estudante_id: str, repo=Depends(_repo)):
    return ListarMatriculasEstudante(repo).executar(estudante_id)


@router.get("/{matricula_id}", response_model=MatriculaResponse)
def buscar_matricula(matricula_id: str, repo=Depends(_repo)):
    result = BuscarMatricula(repo).executar(matricula_id)
    if not result:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    return result


@router.post("/{matricula_id}/aulas/concluir", response_model=MatriculaResponse)
async def concluir_aula(matricula_id: str, request: ConcluirAulaRequest, repo=Depends(_repo)):
    try:
        return await ConcluirAula(repo).executar(matricula_id, request.aula_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))