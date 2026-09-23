from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from adapters.controllers.freelancer_controller import FreelancerController, RegisterFreelancerRequest
from frameworks.http.dependencies import get_freelancer_controller

router = APIRouter(prefix="/freelancers", tags=["Freelancers"])

FreelancerDep = Annotated[FreelancerController, Depends(get_freelancer_controller)]


class RegisterFreelancerBody(BaseModel):
    name: str
    email: str
    specialties: List[str]
    hourly_rate_amount: str
    bio: str
    years_of_experience: int
    certifications: Optional[List[str]] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
def register_freelancer(body: RegisterFreelancerBody, controller: FreelancerDep) -> dict:
    try:
        return controller.register(
            RegisterFreelancerRequest(
                name=body.name,
                email=body.email,
                specialties=body.specialties,
                hourly_rate_amount=body.hourly_rate_amount,
                bio=body.bio,
                years_of_experience=body.years_of_experience,
                certifications=body.certifications,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))