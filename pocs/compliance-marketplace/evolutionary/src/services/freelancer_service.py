from uuid import UUID, uuid4

from src.domain.models import ComplianceArea, Freelancer
from src.infrastructure.repositories import AuditRepository, FreelancerRepository
from src.domain.models import AuditEvent


class FreelancerService:
    def __init__(self, repo: FreelancerRepository, audit: AuditRepository):
        self.repo = repo
        self.audit = audit

    async def register(
        self,
        name: str,
        email: str,
        bio: str,
        areas: list[ComplianceArea],
        hourly_rate_brl: float,
        actor_id: UUID,
    ) -> Freelancer:
        freelancer = Freelancer(
            id=uuid4(),
            name=name,
            email=email,
            bio=bio,
            areas=areas,
            hourly_rate_brl=hourly_rate_brl,
        )
        await self.repo.save(freelancer)
        await self.audit.record(
            AuditEvent(
                entity_type="freelancer",
                entity_id=freelancer.id,
                action="registered",
                actor_id=actor_id,
                payload={"name": name, "email": email, "areas": [a.value for a in areas]},
            )
        )
        return freelancer

    async def find_by_area(self, area: ComplianceArea) -> list[Freelancer]:
        return await self.repo.find_by_area(area)

    async def get(self, freelancer_id: UUID) -> Freelancer | None:
        return await self.repo.find_by_id(freelancer_id)

    async def list_all(self) -> list[Freelancer]:
        return await self.repo.list_all()