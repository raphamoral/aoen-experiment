from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class RepositorioDeVerificacao(ABC):
    @abstractmethod
    def buscar_por_hash(self, hash_verificacao: str) -> Optional[Dict[str, Any]]:
        """
        Retorna um dicionário simples (read model projetado).
        Verificação é leitura otimizada — não manipula agregados de domínio.
        Em arquitetura distribuída: substituir por chamada HTTP ao contexto Certificação.
        """
        ...

    @abstractmethod
    def registrar_auditoria(self, hash_verificacao: str, ip_solicitante: str, resultado: bool) -> None:
        ...