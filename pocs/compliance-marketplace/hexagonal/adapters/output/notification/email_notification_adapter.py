import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ports.output.notification_port import INotificationPort

logger = logging.getLogger(__name__)


class SMTPNotificationAdapter(INotificationPort):
    """
    Driven adapter de notificação via SMTP.
    Substituível por SES, SendGrid ou qualquer outro provedor
    sem tocar uma linha do domínio ou da camada de aplicação —
    basta implementar INotificationPort e reconectar no main.py.
    """

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 1025,
        from_email: str = "noreply@compliance-marketplace.com",
    ) -> None:
        self._host = smtp_host
        self._port = smtp_port
        self._from = from_email

    def send_welcome_freelancer(self, email: str, name: str) -> None:
        self._send(
            to=email,
            subject="Bem-vindo ao Compliance Marketplace!",
            body=(
                f"Olá {name},\n\n"
                "Seu cadastro de freelancer foi criado com sucesso.\n"
                "Complete seu perfil para começar a receber projetos de compliance.\n\n"
                "Equipe Compliance Marketplace"
            ),
        )

    def send_welcome_client(self, email: str, company_name: str) -> None:
        self._send(
            to=email,
            subject="Bem-vindo ao Compliance Marketplace!",
            body=(
                f"Olá, {company_name},\n\n"
                "Sua conta empresarial foi criada com sucesso.\n"
                "Publique seu primeiro projeto e conecte-se a especialistas certificados.\n\n"
                "Equipe Compliance Marketplace"
            ),
        )

    def notify_new_proposal(
        self, client_email: str, project_title: str, freelancer_name: str
    ) -> None:
        self._send(
            to=client_email,
            subject=f"Nova proposta recebida: {project_title}",
            body=(
                f"O freelancer {freelancer_name} enviou uma proposta para '{project_title}'.\n\n"
                "Acesse a plataforma para revisar e aceitar ou rejeitar a proposta.\n\n"
                "Equipe Compliance Marketplace"
            ),
        )

    def notify_proposal_accepted(self, freelancer_email: str, project_title: str) -> None:
        self._send(
            to=freelancer_email,
            subject=f"Proposta aceita: {project_title}",
            body=(
                f"Parabéns! Sua proposta para '{project_title}' foi aceita.\n\n"
                "Um contrato foi gerado automaticamente. Acesse a plataforma para ver os detalhes.\n\n"
                "Equipe Compliance Marketplace"
            ),
        )

    def notify_proposal_rejected(self, freelancer_email: str, project_title: str) -> None:
        self._send(
            to=freelancer_email,
            subject=f"Atualização da sua proposta: {project_title}",
            body=(
                f"Sua proposta para '{project_title}' não foi selecionada desta vez.\n\n"
                "Continue enviando propostas para outros projetos disponíveis.\n\n"
                "Equipe Compliance Marketplace"
            ),
        )

    def notify_contract_created(
        self, freelancer_email: str, client_email: str, project_title: str
    ) -> None:
        for recipient in (freelancer_email, client_email):
            if recipient:
                self._send(
                    to=recipient,
                    subject=f"Contrato gerado: {project_title}",
                    body=(
                        f"Um contrato foi gerado para o projeto '{project_title}'.\n\n"
                        "Acesse a plataforma para visualizar os termos.\n\n"
                        "Equipe Compliance Marketplace"
                    ),
                )

    def notify_payment_released(self, freelancer_email: str, amount: str) -> None:
        self._send(
            to=freelancer_email,
            subject="Pagamento liberado!",
            body=(
                f"O valor de {amount} foi liberado para sua conta.\n\n"
                "Equipe Compliance Marketplace"
            ),
        )

    def _send(self, to: str, subject: str, body: str) -> None:
        try:
            msg = MIMEMultipart()
            msg["From"] = self._from
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))
            with smtplib.SMTP(self._host, self._port) as server:
                server.sendmail(self._from, [to], msg.as_string())
            logger.info("E-mail enviado para %s: %s", to, subject)
        except Exception as exc:
            logger.warning("Falha ao enviar e-mail para %s: %s", to, exc)