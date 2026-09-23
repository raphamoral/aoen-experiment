from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from shared.kernel.aggregate import AggregateRoot
from .value_objects import ComplianceCategory, RegulatoryBody, RegulatoryRequirement


@dataclass
class RegulatoryFramework(AggregateRoot):
    """
    RegulatoryFramework — Aggregate Root do Catálogo de Compliance.

    Maturidade Wardley: CUSTOM → PRODUCT
    O catálogo de frameworks regulatórios é diferencial competitivo hoje,
    mas tende a ser commoditizado por players RegTech (Bloomberg Law, etc.).
    Decisão arquitetural: manter como Custom agora, planejar extração futura.

    Ubiquitous Language:
    - Framework      = conjunto normativo (lei, resolução, circular, norma)
    - Requisito      = obrigação específica dentro do framework
    - Complexidade   = nível de especialização exigida (1=básico → 4=especialista)
    - Vigência       = período de eficácia da norma
    """
    code: str = ""         # Ex: "LGPD", "BACEN_4658", "CVM_598"
    name: str = ""
    description: str = ""
    regulatory_body: Optional[RegulatoryBody] = None
    category: Optional[ComplianceCategory] = None
    effective_date: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    requirements: List[RegulatoryRequirement] = field(default_factory=list)
    related_frameworks: List[str] = field(default_factory=list)  # codes
    complexity_level: int = 1   # 1=básico, 2=intermediário, 3=avançado, 4=especialista
    is_active: bool = True

    def add_requirement(self, requirement: RegulatoryRequirement) -> None:
        """Adiciona requisito normativo ao framework."""
        if requirement not in self.requirements:
            self.requirements.append(requirement)

    def relate_to(self, framework_code: str) -> None:
        """Associa framework relacionado (ex: LGPD ↔ GDPR)."""
        if framework_code not in self.related_frameworks:
            self.related_frameworks.append(framework_code)

    def update_description(self, description: str) -> None:
        self.description = description
        self.last_updated = datetime.utcnow()

    def deactivate(self) -> None:
        """Marca framework como revogado/substituído."""
        self.is_active = False