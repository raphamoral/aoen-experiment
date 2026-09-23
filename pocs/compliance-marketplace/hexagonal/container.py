"""
Raiz de composição (Composition Root).

Este é o único lugar onde adaptadores concretos são instanciados e
injetados nas portas. Nenhum outro módulo da aplicação conhece as
implementações concretas — todos dependem das interfaces (ports/).

Para trocar de in-memory para SQLAlchemy, altere apenas este arquivo.
"""

from adapters.inbound.http import freelancer_router, project_router, proposal_router
from adapters.outbound.notification.smtp_notification_service import SMTPNotificationService
from adapters.outbound.payment.stripe_payment_service import StripePaymentService
from adapters.outbound.persistence.in_memory_freelancer_repository import (
    InMemoryFreelancerRepository,
)
from adapters.outbound.persistence.in_memory_project_repository import InMemoryProjectRepository
from adapters.outbound.persistence.in_memory_proposal_repository import InMemoryProposalRepository
from application.freelancer_service import FreelancerApplicationService
from application.project_service import ProjectApplicationService
from application.proposal_service import ProposalApplicationService
from domain.services.matching_service import FreelancerMatchingService
from domain.services.proposal_service import ProposalDomainService

# --- Adaptadores de saída (driven) ---
_freelancer_repo = InMemoryFreelancerRepository()
_project_repo = InMemoryProjectRepository()
_proposal_repo = InMemoryProposalRepository()
_notification_svc = SMTPNotificationService()
_payment_svc = StripePaymentService()

# --- Serviços de domínio (stateless) ---
_matching_svc = FreelancerMatchingService()
_proposal_domain_svc = ProposalDomainService()

# --- Serviços de aplicação (implementam as portas de entrada) ---
_freelancer_app_svc = FreelancerApplicationService(
    freelancer_repo=_freelancer_repo,
    project_repo=_project_repo,
    matching_service=_matching_svc,
)

_project_app_svc = ProjectApplicationService(project_repo=_project_repo)

_proposal_app_svc = ProposalApplicationService(
    proposal_repo=_proposal_repo,
    project_repo=_project_repo,
    freelancer_repo=_freelancer_repo,
    notification_service=_notification_svc,
    matching_service=_matching_svc,
    proposal_domain_service=_proposal_domain_svc,
)


# --- Factories para FastAPI Depends ---
def get_freelancer_use_case() -> FreelancerApplicationService:
    return _freelancer_app_svc


def get_project_use_case() -> ProjectApplicationService:
    return _project_app_svc


def get_proposal_use_case() -> ProposalApplicationService:
    return _proposal_app_svc


def wire_dependencies(app) -> None:
    """
    Substitui os placeholders de dependência dos routers pelas
    implementações concretas via app.dependency_overrides.
    """
    app.dependency_overrides[freelancer_router.get_use_case] = get_freelancer_use_case
    app.dependency_overrides[project_router.get_project_use_case] = get_project_use_case
    app.dependency_overrides[project_router.get_freelancer_use_case] = get_freelancer_use_case
    app.dependency_overrides[proposal_router.get_use_case] = get_proposal_use_case