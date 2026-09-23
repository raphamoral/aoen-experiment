from typing import List, Optional

from entities.freelancer import Freelancer
from use_cases.freelancer.create_freelancer import CreateFreelancer, CreateFreelancerInput
from use_cases.freelancer.list_freelancers import ListFreelancers
from use_cases.freelancer.get_freelancer import GetFreelancer
from adapters.presenters.schemas import FreelancerCreateRequest, FreelancerResponse


class FreelancerController:
    def __init__(
        self,
        create_uc: CreateFreelancer,
        list_uc: ListFreelancers,
        get_uc: GetFreelancer,
    ):
        self.create_uc = create_uc
        self.list_uc = list_uc
        self.get_uc = get_uc

    def create(self, request: FreelancerCreateRequest) -> FreelancerResponse:
        freelancer = self.create_uc.execute(
            CreateFreelancerInput(
                name=request.name,
                email=request.email,
                specializations=[s.value for s in request.specializations],
                hourly_rate=request.hourly_rate,
                bio=request.bio,
            )
        )
        return self._to_response(freelancer)

    def list_all(self, specialization: Optional[str] = None) -> List[FreelancerResponse]:
        return [self._to_response(f) for f in self.list_uc.execute(specialization)]

    def get(self, freelancer_id: str) -> FreelancerResponse:
        return self._to_response(self.get_uc.execute(freelancer_id))

    def _to_response(self, f: Freelancer) -> FreelancerResponse:
        return FreelancerResponse(
            id=f.id,
            name=f.name,
            email=f.email,
            specializations=[s.value for s in f.specializations],
            hourly_rate=f.hourly_rate,
            bio=f.bio,
            rating=f.rating,
            total_reviews=f.total_reviews,
            is_active=f.is_active,
        )