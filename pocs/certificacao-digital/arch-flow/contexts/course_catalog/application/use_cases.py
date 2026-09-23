from typing import List, Optional

from .dto import CriarCursoRequest, CriarInstrutorRequest, CursoResponse, InstrutorResponse
from ..domain.models import Curso, Instrutor, MaturidadeCurso
from ..domain.repositories import RepositorioDeCurso, RepositorioDeInstrutor


class CriarInstrutor:
    def __init__(self, repo: RepositorioDeInstrutor):
        self._repo = repo

    def executar(self, request: CriarInstrutorRequest) -> InstrutorResponse:
        instrutor = Instrutor(nome=request.nome, email=request.email, especialidade=request.especialidade)
        salvo = self._repo.salvar(instrutor)
        return InstrutorResponse(id=salvo.id, nome=salvo.nome, email=salvo.email, especialidade=salvo.especialidade)


class CriarCurso:
    def __init__(self, repo: RepositorioDeCurso):
        self._repo = repo

    def executar(self, request: CriarCursoRequest) -> CursoResponse:
        curso = Curso(
            titulo=request.titulo,
            descricao=request.descricao,
            carga_horaria=request.carga_horaria,
            maturidade=MaturidadeCurso(request.maturidade),
            instrutor_id=request.instrutor_id,
            nota_minima_aprovacao=request.nota_minima_aprovacao,
        )
        return _para_response(self._repo.salvar(curso))


class PublicarCurso:
    def __init__(self, repo: RepositorioDeCurso):
        self._repo = repo

    def executar(self, curso_id: str) -> CursoResponse:
        curso = self._repo.buscar_por_id(curso_id)
        if not curso:
            raise ValueError(f"Curso {curso_id} não encontrado.")
        curso.publicar()
        return _para_response(self._repo.salvar(curso))


class BuscarCurso:
    def __init__(self, repo: RepositorioDeCurso):
        self._repo = repo

    def executar(self, curso_id: str) -> Optional[CursoResponse]:
        curso = self._repo.buscar_por_id(curso_id)
        return _para_response(curso) if curso else None


class ListarCursosPublicados:
    def __init__(self, repo: RepositorioDeCurso):
        self._repo = repo

    def executar(self) -> List[CursoResponse]:
        return [_para_response(c) for c in self._repo.listar_publicados()]


def _para_response(curso: Curso) -> CursoResponse:
    return CursoResponse(
        id=curso.id,
        titulo=curso.titulo,
        descricao=curso.descricao,
        carga_horaria=curso.carga_horaria,
        maturidade=curso.maturidade.value,
        status=curso.status.value,
        instrutor_id=curso.instrutor_id,
        total_aulas=curso.total_aulas,
        nota_minima_aprovacao=curso.nota_minima_aprovacao,
    )