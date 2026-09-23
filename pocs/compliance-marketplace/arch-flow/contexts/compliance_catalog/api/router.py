from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from ..application.services import ComplianceCatalogService
from ..infrastructure.repository import RegulatoryFrameworkRepository

router = APIRouter(prefix="/compliance-catalog", tags=["Compliance Catalog (Custom)"])

_repository = RegulatoryFrameworkRepository()
_service = ComplianceCatalogService(_repository)


class CreateFrameworkRequest(BaseModel):
    code: str
    name: str
    description: str
    regulatory_body_code: str
    regulatory_body_name: str
    country: str
    category_code: str
    complexity_level: int = 1


class FrameworkResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    regulatory_body_code: Optional[str]
    category_code: Optional[str]
    complexity_level: int
    requirements_count: int
    related_frameworks: List[str]
    is_active: bool


@router.post("/frameworks", status_code=status.HTTP_201_CREATED)
async def create_framework(request: CreateFrameworkRequest):
    """Cadastra novo framework regulatório no catálogo."""
    framework = await _service.create_framework(**request.model_dump())
    return _to_response(framework)


@router.get("/frameworks", response_model=List[FrameworkResponse])
async def list_frameworks(category: Optional[str] = None):
    """Lista frameworks regulatórios. Filtra por categoria se fornecida."""
    if category:
        frameworks = await _service.find_by_category(category)
    else:
        frameworks = await _service.find_all_active()
    return [_to_response(f) for f in frameworks]


@router.get("/frameworks/{code}", response_model=FrameworkResponse)
async def get_framework(code: str):
    """Retorna detalhes de um framework regulatório pelo código."""
    framework = await _service.find_by_code(code)
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework '{code}' não encontrado",
        )
    return _to_response(framework)


def _to_response(framework) -> dict:
    return {
        "id": framework.id,
        "code": framework.code,
        "name": framework.name,
        "description": framework.description,
        "regulatory_body_code": (
            framework.regulatory_body.code if framework.regulatory_body else None
        ),
        "category_code": framework.category.code if framework.category else None,
        "complexity_level": framework.complexity_level,
        "requirements_count": len(framework.requirements),
        "related_frameworks": framework.related_frameworks,
        "is_active": framework.is_active,
    }