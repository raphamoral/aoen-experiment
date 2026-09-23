from typing import List, Optional

from shared.kernel.domain.events import MatriculaConcluidaEvento
from shared.kernel.infrastructure.event_bus import BarramentoDeEventos
from .dto import MatricularRequest, MatriculaResponse
from ..domain.models import Matricula
from ..domain.repositories import RepositorioDeMatricula


class MatricularEstudante:
    def __init__(self, repo: RepositorioDeMatricula):
        self._repo = repo

    def executar(self, request: MatricularRequest) -> MatriculaResponse:
        existente = self._repo.buscar_por_estudante_e_curso(request.estudante_id, request.curso_id)
        if existente and existente.status.value != "cancelada":
            raise ValueError("Estudante já matriculado neste curso.")
        matricula = Matricula(estudante_id=request.estudante_id, curso_id=request.curso_id)
        return _para_response(self._repo.salvar(matricula))


class ConcluirAula:
    def __init__(self, repo: RepositorioDeMatricula):
        self._repo = repo

    async def executar(self, matricula_id: str, aula_id: str) -> MatriculaResponse:
        matricula = self._repo.buscar_por_id(matricula_id)
        if not matricula:
            raise ValueError(f"Matrícula {matricula_id} não encontrada.")
        matricula.concluir_aula(aula_id)
        if matricula.percentual_conclusao >= 100.0:
            matricula.concluir_curso()
            await BarramentoDeEventos.publicar(
                MatriculaConcluidaEvento(
                    estudante_id=matricula.estudante_id,
                    curso_id=matricula.curso_id,
                    matricula_id=matricula.id,
                )
            )
        return _para_response(self._repo.salvar(matricula))


class BuscarMatricula:
    def __init__(self, repo: RepositorioDeMatricula):
        self._repo = repo

    def executar(self, matricula_id: str) -> Optional[MatriculaResponse]:
        m = self._repo.buscar_por_id(matricula_id)
        return _para_response(m) if m else None


class ListarMatriculasEstudante:
    def __init__(self, repo: RepositorioDeMatricula):
        self._repo = repo

    def executar(self, estudante_id: str) -> List[MatriculaResponse]:
        return [_para_response(m) for m in self._repo.listar_por_estudante(estudante_id)]


def _para_response(m: Matricula) -> MatriculaResponse:
    return MatriculaResponse(
        id=m.id,
        estudante_id=m.estudante_id,
        curso_id=m.curso_id,
        status=m.status.value,
        percentual_conclusao=m.percentual_conclusao,
    )