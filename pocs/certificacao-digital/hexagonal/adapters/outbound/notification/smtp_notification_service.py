import logging
import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ports.outbound.notification_service_port import (
    CertificateIssuedNotification,
    NotificationServicePort,
)

logger = logging.getLogger(__name__)


@dataclass
class SmtpConfig:
    host: str
    port: int
    username: str
    password: str
    sender_email: str
    use_tls: bool = True


class SmtpNotificationService(NotificationServicePort):
    """
    Driven adapter: delivers transactional emails via SMTP.

    Falls back to structured logging when SMTP credentials are absent
    (useful in development / CI without a mail server).
    """

    def __init__(self, config: SmtpConfig) -> None:
        self._config = config

    def notify_certificate_issued(self, notification: CertificateIssuedNotification) -> None:
        subject = f"Certificado digital emitido: {notification.course_name}"
        body = (
            f"Parabéns, {notification.recipient_name}!\n\n"
            f"Seu certificado para o curso \"{notification.course_name}\" foi emitido.\n\n"
            f"ID do certificado : {notification.certificate_id}\n"
            f"Hash de verificação: {notification.certificate_hash}\n\n"
            f"Verifique a autenticidade em:\n{notification.verification_url}\n\n"
            "Este certificado possui verificação pública disponível 24 h por dia."
        )
        self._dispatch(notification.recipient_email, subject, body)

    def notify_certificate_revoked(
        self,
        recipient_email: str,
        recipient_name: str,
        certificate_id: str,
        reason: str,
    ) -> None:
        subject = "Seu certificado foi revogado"
        body = (
            f"Olá, {recipient_name}.\n\n"
            f"O certificado {certificate_id} foi revogado.\n"
            f"Motivo: {reason}\n\n"
            "Entre em contato conosco para mais informações."
        )
        self._dispatch(recipient_email, subject, body)

    def _dispatch(self, recipient: str, subject: str, body: str) -> None:
        if not self._config.username:
            logger.info(
                "[EMAIL — no SMTP configured] to=%s subject=%r\n%s",
                recipient,
                subject,
                body,
            )
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = self._config.sender_email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            with smtplib.SMTP(self._config.host, self._config.port) as server:
                if self._config.use_tls:
                    server.starttls()
                server.login(self._config.username, self._config.password)
                server.sendmail(self._config.sender_email, recipient, msg.as_string())

            logger.info("Email sent to %s: %s", recipient, subject)
        except Exception:
            logger.exception("Failed to send email to %s", recipient)