from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class MaturidadeCursoDTO(str, Enum):
    GENESIS = "genesis"
    CUSTOM = "custom"
    PRODUTO = "produto"
    COMMODITY = "commodity"


class CriarInstrutorRequest(BaseModel):
    nome: str = Field(..., min_length=3)
    email: str
    especialidade: str


class InstrutorResponse(BaseModel):
    id: str
    nome: str
    email: str
    especialidade: str


class CriarCursoRequest(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200)
    descricao: str = Field(..., min_length=10)
    carga_horaria: int = Field(..., ge=1, le=1000)
    maturidade: MaturidadeCursoDTO = MaturidadeCursoDTO.CUSTOM
    instrutor_id: str
    nota_minima_aprovacao: float = Field(default=7.0, ge=0.0, le=10.0)


class CursoResponse(BaseModel):
    id: str
    titulo: str
    descricao: str
    carga_horaria: int
    maturidade: str
    status: str
    instrutor_id: str
    total_aulas: int
    nota_minima_aprovacao: float