from typing import List, Optional

from shared.kernel.domain.events import CertificadoEmitidoEvento
from shared.kernel.infrastructure.event_bus import BarramentoDeEventos
from .dto import CertificadoResponse, EmitirCertificadoRequest
from ..domain.models import Certificado
from ..domain.repositories import RepositorioDeCertificado


class EmitirCertificado:
    def __init__(self, repo: RepositorioDeCertificado):
        self._repo = repo

    async def executar(self, request: EmitirCertificadoRequest) -> CertificadoResponse:
        certificado = Certificado(
            estudante_id=request.estudante_id,
            curso_id=request.curso_id,
            nome_estudante=request.nome_estudante,
            titulo_curso=request.titulo_curso,
            carga_horaria=request.carga_horaria,
            nota_final=request.nota_final,
        )
        salvo = self._repo.salvar(certificado)
        await BarramentoDeEventos.publicar(
            CertificadoEmitidoEvento(
                estudante_id=salvo.estudante_id,
                curso_id=salvo.curso_id,
                certificado_id=salvo.id,
                hash_verificacao=salvo.hash_verificacao,
            )
        )
        return _para_response(salvo)


class BuscarCertificado:
    def __init__(self, repo: RepositorioDeCertificado):
        self._repo = repo

    def executar(self, certificado_id: str) -> Optional[CertificadoResponse]:
        c = self._repo.buscar_por_id(certificado_id)
        return _para_response(c) if c else None


class ListarCertificadosEstudante:
    def __init__(self, repo: RepositorioDeCertificado):
        self._repo = repo

    def executar(self, estudante_id: str) -> List[CertificadoResponse]:
        return [_para_response(c) for c in self._repo.listar_por_estudante(estudante_id)]


class RevogarCertificado:
    def __init__(self, repo: RepositorioDeCertificado):
        self._repo = repo

    def executar(self, certificado_id: str, motivo: str) -> CertificadoResponse:
        c = self._repo.buscar_por_id(certificado_id)
        if not c:
            raise ValueError(f"Certificado {certificado_id} não encontrado.")
        c.revogar(motivo)
        return _para_response(self._repo.salvar(c))


def _para_response(c: Certificado) -> CertificadoResponse:
    return CertificadoResponse(
        id=c.id,
        estudante_id=c.estudante_id,
        curso_id=c.curso_id,
        nome_estudante=c.nome_estudante,
        titulo_curso=c.titulo_curso,
        carga_horaria=c.carga_horaria,
        nota_final=c.nota_final,
        status=c.status.value,
        emitido_em=c.emitido_em,
        hash_verificacao=c.hash_verificacao,
        url_verificacao=f"/api/v1/verificacao/{c.hash_verificacao}",
    )