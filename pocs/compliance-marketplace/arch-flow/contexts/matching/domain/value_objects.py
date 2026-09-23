from dataclasses import dataclass
from shared.kernel.value_object import ValueObject


@dataclass(frozen=True)
class MatchScore(ValueObject):
    """
    Score de compatibilidade entre requisito do projeto e perfil do freelancer.

    Maturidade Wardley: GENESIS
    Algoritmo de scoring especializado em compliance é o principal
    diferencial competitivo da plataforma — não terceirizar.

    Dimensões do score refletem o que importa no domínio:
    - framework_alignment: corresponde às normas exigidas?
    - jurisdiction_match: atua na jurisdição do cliente?
    - seniority_fit: nível de experiência é adequado à complexidade?
    - availability_fit: horas disponíveis cobrem a demanda?
    - certification_bonus: possui certificações exigidas?
    """
    value: float                  # Score final ponderado [0.0–1.0]
    framework_alignment: float    # [0.0–1.0]
    jurisdiction_match: float     # [0.0–1.0]
    seniority_fit: float          # [0.0–1.0]
    availability_fit: float       # [0.0–1.0]
    certification_bonus: float    # [0.0–1.0]

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("MatchScore.value deve estar entre 0.0 e 1.0")


@dataclass(frozen=True)
class ProjectRequirement(ValueObject):
    """
    Requisitos do projeto de compliance do cliente.

    Linguagem ubíqua: o que o cliente precisa para o projeto regulatório.
    """
    framework_codes: tuple          # Ex: ("LGPD", "BACEN_4658")
    jurisdiction_codes: tuple       # Ex: ("BR",)
    min_experience_years: int
    weekly_hours_needed: int
    complexity_level: int           # 1–4, conforme escala do catálogo
    required_certifications: tuple = ()