from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Certificado


class RepositorioDeCertificado(ABC):
    @abstractmethod
    def salvar(self, certificado: Certificado) -> Certificado: ...

    @abstractmethod
    def buscar_por_id(self, certificado_id: str) -> Optional[Certificado]: ...

    @abstractmethod
    def buscar_por_hash(self, hash_verificacao: str) -> Optional[Certificado]: ...

    @abstractmethod
    def listar_por_estudante(self, estudante_id: str) -> List[Certificado]: ...