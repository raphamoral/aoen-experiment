from dataclasses import dataclass
from enum import Enum

from shared.kernel.value_object import ValueObject


class MeasurementUnit(str, Enum):
    """Unidade de Medida dos biomarcadores laboratoriais.

    Linguagem ubíqua: unidades clínicas padronizadas conforme
    nomenclatura laboratorial brasileira.
    """

    MG_DL = "mg/dL"
    G_DL = "g/dL"
    MEQ_L = "mEq/L"
    UI_L = "UI/L"
    MIU_ML = "mIU/mL"
    NG_ML = "ng/mL"
    PERCENT = "%"
    THOUSAND_PER_MM3 = "mil/mm³"
    PG = "pg"
    FL = "fL"
    NMOL_L = "nmol/L"
    PMOL_L = "pmol/L"
    UMOL_L = "umol/L"
    G_L = "g/L"
    U_L = "U/L"
    MCG_DL = "mcg/dL"
    NG_DL = "ng/dL"


@dataclass(frozen=True)
class ReferenceRange(ValueObject):
    """Faixa de Referência — valores clínicos normais de um biomarcador.

    Representa o intervalo considerado saudável para um biomarcador
    em um determinado contexto clínico. A mesma medição pode ter
    faixas diferentes por sexo, idade ou condição clínica.
    """

    minimum: float
    maximum: float
    unit: MeasurementUnit

    def __post_init__(self) -> None:
        if self.minimum >= self.maximum:
            raise ValueError(
                "Valor mínimo deve ser menor que o máximo da faixa de referência"
            )

    def contains(self, value: float) -> bool:
        return self.minimum <= value <= self.maximum

    def deviation_percentage(self, value: float) -> float:
        midpoint = (self.minimum + self.maximum) / 2
        return ((value - midpoint) / midpoint) * 100


@dataclass(frozen=True)
class BiomarkerValue(ValueObject):
    """Valor de Biomarcador — resultado numérico de um exame específico.

    Conceito central da linguagem ubíqua laboratorial: encapsula
    o valor mensurado com sua unidade de medida, garantindo que
    comparações só ocorram entre unidades compatíveis.
    """

    numeric_value: float
    unit: MeasurementUnit

    def __post_init__(self) -> None:
        if self.numeric_value < 0:
            raise ValueError("Valor do biomarcador não pode ser negativo")

    def is_within_range(self, reference: ReferenceRange) -> bool:
        if self.unit != reference.unit:
            raise ValueError(
                f"Unidades incompatíveis: {self.unit} vs {reference.unit}"
            )
        return reference.contains(self.numeric_value)