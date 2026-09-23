from dataclasses import dataclass
from enum import Enum

from shared.kernel.value_object import ValueObject


class BiologicalSex(str, Enum):
    """Sexo Biológico — relevante para faixas de referência laboratorial."""

    MALE = "masculino"
    FEMALE = "feminino"
    OTHER = "outro"


class HealthGoal(str, Enum):
    """Meta de Saúde — objetivo de saúde declarado pelo usuário.

    Linguagem ubíqua: as metas contextualizam as recomendações da IA
    e permitem personalização além dos biomarcadores.
    """

    WEIGHT_LOSS = "perda_de_peso"
    MUSCLE_GAIN = "ganho_muscular"
    ENERGY_BOOST = "aumento_de_energia"
    DISEASE_PREVENTION = "prevencao_de_doencas"
    IMMUNE_SUPPORT = "fortalecimento_imunologico"
    HORMONAL_BALANCE = "equilibrio_hormonal"
    CARDIOVASCULAR_HEALTH = "saude_cardiovascular"
    GUT_HEALTH = "saude_intestinal"


@dataclass(frozen=True)
class Age(ValueObject):
    """Idade — valor semântico com comportamentos de negócio.

    Não é simples inteiro: encapsula classificações etárias
    relevantes para interpretação laboratorial e nutricional.
    """

    years: int

    def __post_init__(self) -> None:
        if not (0 <= self.years <= 120):
            raise ValueError(f"Idade inválida: {self.years}")

    @property
    def is_adult(self) -> bool:
        return self.years >= 18

    @property
    def age_group(self) -> str:
        if self.years < 18:
            return "juvenil"
        if self.years < 30:
            return "adulto_jovem"
        if self.years < 60:
            return "adulto"
        return "idoso"


@dataclass(frozen=True)
class HealthCondition(ValueObject):
    """Condição de Saúde — diagnóstico ou condição clínica relevante.

    Condições crônicas podem alterar faixas de referência e
    impactar diretamente as recomendações nutricionais da IA.
    """

    name: str
    is_chronic: bool = False
    affects_nutrition: bool = True