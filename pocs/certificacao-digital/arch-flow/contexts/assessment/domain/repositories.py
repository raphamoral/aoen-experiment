from abc import ABC, abstractmethod
from typing import Optional

from .models import Avaliacao, Tentativa


class RepositorioDeAvaliacao(ABC):
    @abstractmethod
    def salvar(self, avaliacao: Avaliacao) -> Avaliacao: ...

    @abstractmethod
    def buscar_por_id(self, avaliacao_id: str) -> Optional[Avaliacao]: ...

    @abstractmethod
    def buscar_por_curso(self, curso_id: str) -> Optional[Avaliacao]: ...


class RepositorioDeTentativa(ABC):
    @abstractmethod
    def salvar(self, tentativa: Tentativa) -> Tentativa: ...

    @abstractmethod
    def buscar_por_id(self, tentativa_id: str) -> Optional[Tentativa]: ...

    @abstractmethod
    def contar_tentativas(self, estudante_id: str, avaliacao_id: str) -> int: ...