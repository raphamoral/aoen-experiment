from pydantic import BaseModel


class MatricularRequest(BaseModel):
    estudante_id: str
    curso_id: str


class ConcluirAulaRequest(BaseModel):
    aula_id: str


class MatriculaResponse(BaseModel):
    id: str
    estudante_id: str
    curso_id: str
    status: str
    percentual_conclusao: float