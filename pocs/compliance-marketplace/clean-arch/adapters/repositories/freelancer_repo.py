from typing import List, Optional
from sqlalchemy.orm import Session

from entities.freelancer import Freelancer, ComplianceArea
from use_cases.ports.repositories import FreelancerRepository
from adapters.repositories.orm_models import FreelancerModel


class SQLAlchemyFreelancerRepository(FreelancerRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, freelancer: Freelancer) -> Freelancer:
        model = FreelancerModel(
            id=freelancer.id,
            name=freelancer.name,
            email=freelancer.email,
            specializations=[s.value for s in freelancer.specializations],
            hourly_rate=freelancer.hourly_rate,
            bio=freelancer.bio,
            rating=freelancer.rating,
            total_reviews=freelancer.total_reviews,
            is_active=freelancer.is_active,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, id: str) -> Optional[Freelancer]:
        model = self.session.query(FreelancerModel).filter_by(id=id).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[Freelancer]:
        model = self.session.query(FreelancerModel).filter_by(email=email).first()
        return self._to_entity(model) if model else None

    def find_all(self, specialization: Optional[ComplianceArea] = None) -> List[Freelancer]:
        models = self.session.query(FreelancerModel).filter_by(is_active=True).all()
        freelancers = [self._to_entity(m) for m in models]
        if specialization:
            freelancers = [f for f in freelancers if specialization in f.specializations]
        return freelancers

    def _to_entity(self, model: FreelancerModel) -> Freelancer:
        return Freelancer(
            id=model.id,
            name=model.name,
            email=model.email,
            specializations=[ComplianceArea(s) for s in model.specializations],
            hourly_rate=model.hourly_rate,
            bio=model.bio,
            rating=model.rating,
            total_reviews=model.total_reviews,
            is_active=model.is_active,
        )