"""
Handlers de eventos para o contexto Certificação.

Anticorruption Layer (ACL): traduz eventos de outros contextos
para operações do domínio de Certificação sem criar acoplamento direto.

Limitação MVP: handlers in-memory não têm sessão de banco injetada.
Evolução: usar worker assíncrono (ARQ/Celery) com sessão própria por mensagem.
"""
import logging

from shared.kernel.domain.events import AvaliacaoAprovadaEvento
from shared.kernel.infrastructure.event_bus import BarramentoDeEventos

logger = logging.getLogger(__name__)


def configurar_handlers() -> None:
    """Registra todos os handlers de eventos do contexto Certificação no barramento."""
    BarramentoDeEventos.assinar(AvaliacaoAprovadaEvento, _ao_aprovar_avaliacao)


async def _ao_aprovar_avaliacao(evento: AvaliacaoAprovadaEvento) -> None:
    """
    Reage a AvaliacaoAprovadaEvento disparando emissão de certificado.

    Tradução ACL:
      Avaliação.estudante_id  → Certificado.estudante_id
      Avaliação.curso_id      → Certificado.curso_id
      Avaliação.nota          → Certificado.nota_final

    Em produção: instanciar SessionLocal() aqui e chamar EmitirCertificado.
    Os dados nome_estudante e titulo_curso viriam de chamadas aos contextos
    Identidade e Catálogo via API interna (customer/supplier relationship).
    """
    logger.info(
        "ACL Certificação ← AvaliacaoAprovada: "
        f"estudante={evento.estudante_id} curso={evento.curso_id} nota={evento.nota:.1f}"
    )
    # TODO (produção):
    # db = SessionLocal()
    # repo = RepositorioDeCertificadoSQLite(db)
    # nome_estudante = IdentidadeClient.buscar_nome(evento.estudante_id)
    # titulo_curso = CatalogoClient.buscar_titulo(evento.curso_id)
    # await EmitirCertificado(repo).executar(EmitirCertificadoRequest(...))
    # db.close()