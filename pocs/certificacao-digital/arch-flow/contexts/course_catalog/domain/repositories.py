from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Curso, Instrutor


class RepositorioDeCurso(ABC):
    @abstractmethod
    def salvar(self, curso: Curso) -> Curso: ...

    @abstractmethod
    def buscar_por_id(self, curso_id: str) -> Optional[Curso]: ...

    @abstractmethod
    def listar_publicados(self) -> List[Curso]: ...

    @abstractmethod
    def listar_todos(self) -> List[Curso]: ...


class RepositorioDeInstrutor(ABC):
    @abstractmethod
    def salvar(self, instrutor: Instrutor) -> Instrutor: ...

    @abstractmethod
    def buscar_por_id(self, instrutor_id: str) -> Optional[Instrutor]: ...