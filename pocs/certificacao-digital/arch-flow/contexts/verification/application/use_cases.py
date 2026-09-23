from ..domain.models import ResultadoVerificacao
from ..domain.repositories import RepositorioDeVerificacao


class VerificarCertificado:
    """
    Caso de uso público — sem autenticação requerida.
    Qualquer pessoa ou sistema pode confirmar a autenticidade de um certificado.
    Contexto separado de Certificação garante que a API pública evolua independentemente
    do domínio interno (ex: adicionar QR code, badge digital, JSON-LD sem quebrar Certificação).
    """

    def __init__(self, repo: RepositorioDeVerificacao):
        self._repo = repo

    def executar(self, hash_verificacao: str, ip_solicitante: str = "unknown") -> ResultadoVerificacao:
        certificado = self._repo.buscar_por_hash(hash_verificacao)
        valido = certificado is not None and certificado.get("status") == "valido"

        self._repo.registrar_auditoria(
            hash_verificacao=hash_verificacao,
            ip_solicitante=ip_solicitante,
            resultado=valido,
        )

        if not certificado:
            return ResultadoVerificacao(
                valido=False,
                hash_verificacao=hash_verificacao,
                mensagem="Certificado nao encontrado. Verifique o codigo informado.",
            )

        if certificado.get("status") != "valido":
            return ResultadoVerificacao(
                valido=False,
                hash_verificacao=hash_verificacao,
                status=certificado.get("status"),
                mensagem="Este certificado foi revogado e nao e mais valido.",
            )

        return ResultadoVerificacao(
            valido=True,
            hash_verificacao=hash_verificacao,
            nome_estudante=certificado.get("nome_estudante"),
            titulo_curso=certificado.get("titulo_curso"),
            carga_horaria=certificado.get("carga_horaria"),
            nota_final=certificado.get("nota_final"),
            emitido_em=certificado.get("emitido_em"),
            status=certificado.get("status"),
            mensagem="Certificado valido e autentico.",
        )