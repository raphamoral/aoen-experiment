from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from shared.kernel.domain.base_entity import Entity


class StatusMatricula(str, Enum):
    ATIVA = "ativa"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    SUSPENSA = "suspensa"


@dataclass
class RegistroDeProgresso(Entity):
    """
    Rastreia o avanço real do estudante em uma aula específica.
    Linguagem ubíqua: 'Progresso' representa conclusão confirmada, não apenas acesso.
    """
    aula_id: str = ""
    concluida: bool = False
    percentual_assistido: float = 0.0
    concluida_em: Optional[datetime] = None

    def concluir(self) -> None:
        self.concluida = True
        self.percentual_assistido = 100.0
        self.concluida_em = datetime.now(timezone.utc)


@dataclass
class Matricula(Entity):
    """
    Agregado raiz do contexto Matrícula.
    Representa o vínculo formal entre estudante e curso.
    Invariante: matrícula concluída não pode ser cancelada.
    """
    estudante_id: str = ""
    curso_id: str = ""
    status: StatusMatricula = StatusMatricula.ATIVA
    matriculado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    concluido_em: Optional[datetime] = None
    registros_de_progresso: List[RegistroDeProgresso] = field(default_factory=list)

    @property
    def percentual_conclusao(self) -> float:
        if not self.registros_de_progresso:
            return 0.0
        concluidas = sum(1 for r in self.registros_de_progresso if r.concluida)
        return (concluidas / len(self.registros_de_progresso)) * 100

    def concluir_aula(self, aula_id: str) -> None:
        existente = next((r for r in self.registros_de_progresso if r.aula_id == aula_id), None)
        if not existente:
            existente = RegistroDeProgresso(aula_id=aula_id)
            self.registros_de_progresso.append(existente)
        existente.concluir()
        self.tocar()

    def concluir_curso(self) -> None:
        self.status = StatusMatricula.CONCLUIDA
        self.concluido_em = datetime.now(timezone.utc)
        self.tocar()

    def cancelar(self) -> None:
        if self.status == StatusMatricula.CONCLUIDA:
            raise ValueError("Matrícula concluída não pode ser cancelada.")
        self.status = StatusMatricula.CANCELADA
        self.tocar()