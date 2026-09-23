from dataclasses import dataclass
from enum import Enum

from shared.kernel.value_object import ValueObject


class NutrientCategory(str, Enum):
    """Categoria de Nutriente na linguagem ubíqua do domínio nutricional."""

    MACRONUTRIENT = "macronutriente"
    VITAMIN = "vitamina"
    MINERAL = "mineral"
    AMINO_ACID = "aminoacido"
    FATTY_ACID = "acido_graxo"
    ANTIOXIDANT = "antioxidante"


class MealDistribution(str, Enum):
    """Distribuição de Macronutrientes — padrão alimentar terapêutico."""

    BALANCED = "balanceada"
    LOW_CARB = "low_carb"
    MEDITERRANEAN = "mediterranea"
    ANTI_INFLAMMATORY = "anti_inflamatorio"
    HIGH_PROTEIN = "hiperproteica"


@dataclass(frozen=True)
class DailyIntakeTarget(ValueObject):
    """Meta de Ingestão Diária — quantidade recomendada de um nutriente.

    Calculada com base nos biomarcadores do paciente e em evidências
    científicas de nutrição clínica. A prioridade reflete a urgência
    terapêutica derivada do exame laboratorial.
    """

    nutrient_name: str
    target_amount: float
    unit: str
    category: NutrientCategory
    priority: str = "normal"

    def __post_init__(self) -> None:
        if self.target_amount < 0:
            raise ValueError("Meta de ingestão não pode ser negativa")


@dataclass(frozen=True)
class FoodRestriction(ValueObject):
    """Restrição Alimentar — limitação clínica ou terapêutica do plano.

    Pode ser derivada de alergia, intolerância, ou de biomarcadores
    alterados que indicam necessidade de restrição terapêutica.
    """

    food_group: str
    reason: str
    is_absolute: bool = True