from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from shared.kernel.infrastructure.database import get_db
from ..application.dto import VerificacaoResponse
from ..application.use_cases import VerificarCertificado
from ..infrastructure.persistence import RepositorioDeVerificacaoSQLite

router = APIRouter()


def _repo(db: Session = Depends(get_db)):
    return RepositorioDeVerificacaoSQLite(db)


@router.get("/{hash_verificacao}", response_model=VerificacaoResponse)
def verificar_certificado(hash_verificacao: str, request: Request, repo=Depends(_repo)):
    """
    Endpoint publico — sem autenticacao.
    Qualquer pessoa, sistema ou empregador pode verificar a autenticidade de um certificado
    usando apenas o hash impresso no documento ou no QR code.
    """
    ip = request.client.host if request.client else "unknown"
    resultado = VerificarCertificado(repo).executar(hash_verificacao, ip)
    return VerificacaoResponse(
        valido=resultado.valido,
        hash_verificacao=resultado.hash_verificacao,
        nome_estudante=resultado.nome_estudante,
        titulo_curso=resultado.titulo_curso,
        carga_horaria=resultado.carga_horaria,
        nota_final=resultado.nota_final,
        emitido_em=resultado.emitido_em,
        status=resultado.status,
        mensagem=resultado.mensagem,
        verificado_em=resultado.verificado_em,
    )