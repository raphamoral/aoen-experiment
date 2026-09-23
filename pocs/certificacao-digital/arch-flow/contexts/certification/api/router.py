from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.kernel.infrastructure.database import get_db
from ..application.dto import CertificadoResponse, EmitirCertificadoRequest
from ..application.use_cases import (
    BuscarCertificado, EmitirCertificado, ListarCertificadosEstudante, RevogarCertificado,
)
from ..infrastructure.persistence import RepositorioDeCertificadoSQLite

router = APIRouter()


def _repo(db: Session = Depends(get_db)):
    return RepositorioDeCertificadoSQLite(db)


@router.post("/", response_model=CertificadoResponse, status_code=201)
async def emitir_certificado(request: EmitirCertificadoRequest, repo=Depends(_repo)):
    return await EmitirCertificado(repo).executar(request)


@router.get("/estudante/{estudante_id}", response_model=List[CertificadoResponse])
def listar_certificados(estudante_id: str, repo=Depends(_repo)):
    return ListarCertificadosEstudante(repo).executar(estudante_id)


@router.get("/{certificado_id}", response_model=CertificadoResponse)
def buscar_certificado(certificado_id: str, repo=Depends(_repo)):
    result = BuscarCertificado(repo).executar(certificado_id)
    if not result:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return result


@router.post("/{certificado_id}/revogar", response_model=CertificadoResponse)
def revogar_certificado(certificado_id: str, motivo: str, repo=Depends(_repo)):
    try:
        return RevogarCertificado(repo).executar(certificado_id, motivo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))