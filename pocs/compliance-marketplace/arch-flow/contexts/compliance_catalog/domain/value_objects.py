from dataclasses import dataclass
from shared.kernel.value_object import ValueObject


@dataclass(frozen=True)
class RegulatoryBody(ValueObject):
    """
    Órgão regulador responsável pela norma.

    Linguagem ubíqua: BACEN, CVM, SUSEP, ANPD, COAF, TCU, AGU...
    """
    code: str        # Ex: "BACEN", "CVM", "ANPD"
    country: str     # ISO 3166-1 alpha-2
    full_name: str


@dataclass(frozen=True)
class ComplianceCategory(ValueObject):
    """
    Categoria do framework regulatório.

    Taxonomia proprietária — diferencial do catálogo da plataforma.
    """
    code: str
    # Exemplos de códigos:
    # FINANCIAL_REGULATION, DATA_PROTECTION, ANTI_MONEY_LAUNDERING,
    # CORPORATE_GOVERNANCE, CYBERSECURITY, ENVIRONMENTAL_ESG,
    # CONSUMER_PROTECTION, CAPITAL_MARKETS, INSURANCE


@dataclass(frozen=True)
class RegulatoryRequirement(ValueObject):
    """Requisito normativo específico dentro de um framework."""
    article: str
    description: str
    mandatory: bool = True