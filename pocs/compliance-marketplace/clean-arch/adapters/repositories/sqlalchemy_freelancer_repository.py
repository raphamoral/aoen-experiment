from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.freelancer import Freelancer
from entities.value_objects import ComplianceSpecialty, Email, Money
from frameworks.database.models import FreelancerModel
from use_cases.ports import FreelancerRepository


class SQLAlchemyFreelancerRepository(FreelancerRepository):
    """
    Gateway: implements the port defined in use_cases/ports.py.
    Knows about SQLAlchemy (infrastructure), but the use cases
    only depend on the abstract FreelancerRepository interface.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, freelancer: Freelancer) -> Freelancer:
        model = self._session.get(FreelancerModel, str(freelancer.id))
        if model:
            self._update_model(model, freelancer)
        else:
            model = self._to_model(freelancer)
            self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, freelancer_id: UUID) -> Optional[Freelancer]:
        model = self._session.get(FreelancerModel, str(freelancer_id))
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[Freelancer]:
        model = (
            self._session.query(FreelancerModel)
            .filter(FreelancerModel.email == email.lower())
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_specialty(self, specialty: ComplianceSpecialty) -> List[Freelancer]:
        models = (
            self._session.query(FreelancerModel)
            .filter(FreelancerModel.specialties.contains(specialty.value))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def list_all(self, skip: int = 0, limit: int = 20) -> List[Freelancer]:
        models = self._session.query(FreelancerModel).offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_model(freelancer: Freelancer) -> FreelancerModel:
        return FreelancerModel(
            id=str(freelancer.id),
            name=freelancer.name,
            email=freelancer.email.value,
            specialties=",".join(s.value for s in freelancer.specialties),
            hourly_rate_amount=str(freelancer.hourly_rate.amount),
            hourly_rate_currency=freelancer.hourly_rate.currency,
            bio=freelancer.bio,
            years_of_experience=freelancer.years_of_experience,
            certifications=",".join(freelancer.certifications),
            average_rating=freelancer.average_rating,
            total_reviews=freelancer.total_reviews,
            is_available=freelancer.is_available,
        )

    @staticmethod
    def _update_model(model: FreelancerModel, freelancer: Freelancer) -> None:
        model.name = freelancer.name
        model.specialties = ",".join(s.value for s in freelancer.specialties)
        model.hourly_rate_amount = str(freelancer.hourly_rate.amount)
        model.bio = freelancer.bio
        model.years_of_experience = freelancer.years_of_experience
        model.certifications = ",".join(freelancer.certifications)
        model.average_rating = freelancer.average_rating
        model.total_reviews = freelancer.total_reviews
        model.is_available = freelancer.is_available

    @staticmethod
    def _to_entity(model: FreelancerModel) -> Freelancer:
        specialties = [ComplianceSpecialty(s) for s in model.specialties.split(",") if s]
        certifications = [c for c in model.certifications.split(",") if c]
        return Freelancer(
            id=UUID(model.id),
            name=model.name,
            email=Email(model.email),
            specialties=specialties,
            hourly_rate=Money(Decimal(model.hourly_rate_amount), model.hourly_rate_currency),
            bio=model.bio,
            years_of_experience=model.years_of_experience,
            certifications=certifications,
            average_rating=model.average_rating,
            total_reviews=model.total_reviews,
            is_available=model.is_available,
        )