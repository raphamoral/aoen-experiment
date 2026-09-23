import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from domain.entities.nutrition_plan import NutritionPlan
from domain.entities.patient import Patient
from ports.output.notification_service_port import NotificationServicePort


class SMTPNotificationService(NotificationServicePort):
    """
    Driven adapter for email notifications via SMTP.

    Symmetrically replaceable (e.g., with SendGrid, Resend) without
    touching the domain or any other adapter.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        sender_email: str,
        use_tls: bool = True,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._sender = sender_email
        self._use_tls = use_tls

    async def _send(self, to_email: str, subject: str, body_html: str) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self._sender
        message["To"] = to_email
        message.attach(MIMEText(body_html, "html"))

        await aiosmtplib.send(
            message,
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            use_tls=self._use_tls,
        )

    async def send_welcome(self, patient: Patient) -> None:
        body = f"""
        <h2>Welcome to NutriAI, {patient.name}!</h2>
        <p>Your profile has been created. You can now submit your laboratory results
        to receive a personalized AI-powered nutritional plan.</p>
        <p>Your health goals: <strong>{', '.join(patient.health_goals)}</strong></p>
        """
        await self._send(patient.email, "Welcome to NutriAI", body)

    async def send_plan_ready(
        self, patient: Patient, plan: NutritionPlan
    ) -> None:
        critical_note = ""
        if plan.has_critical_deficiencies:
            critical_note = (
                "<p><strong>⚠️ Critical deficiencies detected. "
                "Please consult your physician urgently.</strong></p>"
            )

        abnormal = ", ".join(plan.abnormal_nutrients) or "none"
        body = f"""
        <h2>Your Nutritional Plan is Ready, {patient.name}!</h2>
        {critical_note}
        <p>We have analyzed your laboratory results from {plan.created_at.strftime('%Y-%m-%d')}.</p>
        <p>Markers requiring attention: <strong>{abnormal}</strong></p>
        <p>Log in to the platform to view your complete personalized nutritional plan
        with AI-powered recommendations.</p>
        <p><em>Remember: always discuss any supplement recommendations with your healthcare provider.</em></p>
        """
        await self._send(patient.email, "Your NutriAI Plan is Ready", body)