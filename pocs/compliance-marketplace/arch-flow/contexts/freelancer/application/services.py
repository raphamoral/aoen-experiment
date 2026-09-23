from typing import List, Optional

from shared.events.bus import event_bus
from ..domain.entities import FreelancerProfile
from ..domain.value_objects import (
    Certification,
    ComplianceSpecialization,
    HourlyRate,
    Jurisdiction,
)
from ..infrastructure.repository import FreelancerRepository
from .commands import (
    AddCertificationCommand,
    AddSpecializationCommand,
    ApproveFreelancerCommand,
    RegisterFreelancerCommand,
)


class FreelancerService:
    """
    Application Service do contexto Freelancer.

    Orquestra casos de uso: registro, aprovação editorial,
    enriquecimento de perfil com especializações e certificações.
    Publica Domain Events após persistência bem-sucedida.
    """

    def __init__(self, repository: FreelancerRepository) -> None:
        self._repository = repository

    async def register_freelancer(
        self, cmd: RegisterFreelancerCommand
    ) -> FreelancerProfile:
        profile = FreelancerProfile.register(
            user_id=cmd.user_id,
            full_name=cmd.full_name,
            headline=cmd.headline,
            bio=cmd.bio,
            hourly_rate=HourlyRate(amount=cmd.hourly_rate_brl),
            years_of_experience=cmd.years_of_experience,
            availability_hours_per_week=cmd.availability_hours_per_week,
            max_complexity_level=cmd.max_complexity_level,
        )
        await self._repository.save(profile)
        for event in profile.collect_domain_events():
            await event_bus.publish(event)
        return profile

    async def approve_freelancer(
        self, cmd: ApproveFreelancerCommand
    ) -> FreelancerProfile:
        profile = await self._get_or_raise(cmd.freelancer_id)
        profile.approve(cmd.reviewer_id)
        await self._repository.save(profile)
        for event in profile.collect_domain_events():
            await event_bus.publish(event)
        return profile

    async def add_specialization(
        self, cmd: AddSpecializationCommand
    ) -> FreelancerProfile:
        profile = await self._get_or_raise(cmd.freelancer_id)
        specialization = ComplianceSpecialization(
            code=cmd.specialization_code,
            description=cmd.specialization_description,
            regulatory_body=cmd.regulatory_body,
        )
        profile.add_specialization(specialization)
        await self._repository.save(profile)
        for event in profile.collect_domain_events():
            await event_bus.publish(event)
        return profile

    async def add_certification(
        self, cmd: AddCertificationCommand
    ) -> FreelancerProfile:
        profile = await self._get_or_raise(cmd.freelancer_id)
        certification = Certification(
            name=cmd.name,
            issuer=cmd.issuer,
            valid_until=cmd.valid_until,
            credential_url=cmd.credential_url,
        )
        profile.add_certification(certification)
        await self._repository.save(profile)
        return profile

    async def find_by_id(self, freelancer_id: str) -> Optional[FreelancerProfile]:
        return await self._repository.find_by_id(freelancer_id)

    async def find_active_freelancers(self) -> List[FreelancerProfile]:
        return await self._repository.find_by_status("active")

    async def _get_or_raise(self, freelancer_id: str) -> FreelancerProfile:
        profile = await self._repository.find_by_id(freelancer_id)
        if not profile:
            raise ValueError(f"Freelancer '{freelancer_id}' não encontrado")
        return profile