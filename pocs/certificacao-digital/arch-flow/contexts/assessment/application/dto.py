from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class TipoQuestaoDTO(str, Enum):
    MULTIPLA_ESCOLHA = "multipla_escolha"
    VERDADEIRO_FALSO = "verdadeiro_falso"


class AlternativaRequest(BaseModel):
    texto: str
    correta: bool = False


class QuestaoRequest(BaseModel):
    enunciado: str
    tipo: TipoQuestaoDTO = TipoQuestaoDTO.MULTIPLA_ESCOLHA
    alternativas: List[AlternativaRequest]
    peso: float = Field(default=1.0, ge=0.1)


class CriarAvaliacaoRequest(BaseModel):
    curso_id: str
    titulo: str
    nota_minima_aprovacao: float = Field(default=7.0, ge=0.0, le=10.0)
    tentativas_maximas: int = Field(default=3, ge=1)
    questoes: List[QuestaoRequest]


class RespostaQuestaoRequest(BaseModel):
    questao_id: str
    alternativa_id: str


class SubmeterTentativaRequest(BaseModel):
    estudante_id: str
    respostas: List[RespostaQuestaoRequest]


class TentativaResponse(BaseModel):
    id: str
    avaliacao_id: str
    estudante_id: str
    status: str
    nota: float