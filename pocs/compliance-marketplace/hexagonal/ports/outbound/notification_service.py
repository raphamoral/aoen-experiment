from abc import ABC, abstractmethod


class INotificationService(ABC):
    """
    Porta de saída (driven port) para envio de notificações.
    O domínio define o contrato; o adaptador escolhe o canal (SMTP, SMS, push).
    """

    @abstractmethod
    def notify_proposal_received(
        self,
        client_email: str,
        project_title: str,
        freelancer_name: str,
    ) -> None: ...

    @abstractmethod
    def notify_proposal_accepted(
        self,
        freelancer_email: str,
        project_title: str,
    ) -> None: ...

    @abstractmethod
    def notify_proposal_rejected(
        self,
        freelancer_email: str,
        project_title: str,
    ) -> None: ...