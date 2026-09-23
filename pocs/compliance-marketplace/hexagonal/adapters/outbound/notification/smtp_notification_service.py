import logging

from ports.outbound.notification_service import INotificationService

logger = logging.getLogger(__name__)


class SMTPNotificationService(INotificationService):
    """
    Adaptador de saída: direciona notificações via SMTP.

    Em produção, injete host/port/credenciais por variáveis de ambiente
    e substitua os `logger.info` por envios reais com `smtplib` ou
    uma biblioteca como `fastapi-mail`.

    O domínio nunca sabe que existe SMTP — ele apenas chama INotificationService.
    """

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 587,
        sender: str = "noreply@marketplace-compliance.com.br",
    ) -> None:
        self._host = smtp_host
        self._port = smtp_port
        self._sender = sender

    def notify_proposal_received(
        self,
        client_email: str,
        project_title: str,
        freelancer_name: str,
    ) -> None:
        logger.info(
            "[SMTP] %s → %s | Nova proposta para '%s' de %s",
            self._sender,
            client_email,
            project_title,
            freelancer_name,
        )

    def notify_proposal_accepted(
        self,
        freelancer_email: str,
        project_title: str,
    ) -> None:
        logger.info(
            "[SMTP] %s → %s | Sua proposta para '%s' foi ACEITA",
            self._sender,
            freelancer_email,
            project_title,
        )

    def notify_proposal_rejected(
        self,
        freelancer_email: str,
        project_title: str,
    ) -> None:
        logger.info(
            "[SMTP] %s → %s | Sua proposta para '%s' foi REJEITADA",
            self._sender,
            freelancer_email,
            project_title,
        )