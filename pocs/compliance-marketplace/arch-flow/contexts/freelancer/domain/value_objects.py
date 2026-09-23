from dataclasses import dataclass
from shared.kernel.value_object import ValueObject


@dataclass(frozen=True)
class ComplianceSpecialization(ValueObject):
    """
    Especialização em compliance regulatório.

    Linguagem ubíqua central do domínio.
    Exemplos: LGPD, GDPR, SOX, Basel III, BACEN 4658, CVM 598,
              PLD-FT (AML), SUSEP, COAF, IFRS, ESG/S1.
    """
    code: str             # Ex: "LGPD", "BACEN_4658"
    description: str
    regulatory_body: str  # Órgão regulador: BACEN, CVM, SUSEP, ANPD, COAF...


@dataclass(frozen=True)
class Certification(ValueObject):
    """
    Certificação profissional em compliance.

    Exemplos: CCEP (Certified Compliance & Ethics Professional),
              CISA, CRCM, CPC-A, CFE, CIPP/E.
    """
    name: str
    issuer: str
    valid_until: str     # ISO date string (YYYY-MM-DD)
    credential_url: str = ""


@dataclass(frozen=True)
class HourlyRate(ValueObject):
    """Taxa horária do freelancer."""
    amount: float
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("Taxa horária deve ser positiva")


@dataclass(frozen=True)
class Jurisdiction(ValueObject):
    """
    Jurisdição de atuação regulatória.

    Define o âmbito geográfico e normativo em que o freelancer atua.
    Exemplo: Brasil (BR) com especialização estadual em SP.
    """
    country_code: str   # ISO 3166-1 alpha-2
    region: str = ""    # Estado/Província quando aplicável