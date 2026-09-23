from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Matricula


class RepositorioDeMatricula(ABC):
    @abstractmethod
    def salvar(self, matricula: Matricula) -> Matricula: ...

    @abstractmethod
    def buscar_por_id(self, matricula_id: str) -> Optional[Matricula]: ...

    @abstractmethod
    def buscar_por_estudante_e_curso(self, estudante_id: str, curso_id: str) -> Optional[Matricula]: ...

    @abstractmethod
    def listar_por_estudante(self, estudante_id: str) -> List[Matricula]: ...