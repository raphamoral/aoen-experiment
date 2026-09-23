from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class MarkerStatus(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    HIGH = "high"
    CRITICAL_LOW = "critical_low"
    CRITICAL_HIGH = "critical_high"


@dataclass
class ExamMarker:
    name: str
    value: float
    unit: str
    reference_min: float
    reference_max: float

    @property
    def status(self) -> MarkerStatus:
        if self.value < self.reference_min * 0.7:
            return MarkerStatus.CRITICAL_LOW
        if self.value < self.reference_min:
            return MarkerStatus.LOW
        if self.value > self.reference_max * 1.3:
            return MarkerStatus.CRITICAL_HIGH
        if self.value > self.reference_max:
            return MarkerStatus.HIGH
        return MarkerStatus.NORMAL

    @property
    def deviation_percentage(self) -> float:
        mid = (self.reference_min + self.reference_max) / 2
        return round(((self.value - mid) / mid) * 100, 2)


@dataclass
class Exam:
    id: str
    patient_id: str
    exam_date: datetime
    lab_name: str
    markers: List[ExamMarker] = field(default_factory=list)

    @property
    def abnormal_markers(self) -> List[ExamMarker]:
        return [m for m in self.markers if m.status != MarkerStatus.NORMAL]

    @property
    def critical_markers(self) -> List[ExamMarker]:
        return [
            m for m in self.markers
            if m.status in (MarkerStatus.CRITICAL_LOW, MarkerStatus.CRITICAL_HIGH)
        ]

    def validate(self) -> None:
        if not self.markers:
            raise ValueError("Exame deve ter pelo menos um marcador")
        if not self.lab_name.strip():
            raise ValueError("Nome do laboratório não pode ser vazio")
        if self.exam_date > datetime.now():
            raise ValueError("Data do exame não pode ser no futuro")