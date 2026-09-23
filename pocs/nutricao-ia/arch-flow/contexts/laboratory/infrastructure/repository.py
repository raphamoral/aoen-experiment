from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, Column, Date, JSON, String
from sqlalchemy.orm import Session

from shared.infra.database import Base
from contexts.laboratory.domain.entities import Biomarker, LabResult
from contexts.laboratory.domain.value_objects import (
    BiomarkerValue,
    MeasurementUnit,
    ReferenceRange,
)


class LabResultModel(Base):
    __tablename__ = "lab_results"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    collection_date = Column(Date, nullable=False)
    laboratory_name = Column(String(255), nullable=False)
    biomarkers_json = Column(JSON, nullable=False, default=list)
    is_processed = Column(Boolean, default=False)


class LabResultRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, lab_result: LabResult) -> None:
        model = LabResultModel(
            id=str(lab_result.id),
            user_id=str(lab_result.user_id),
            collection_date=lab_result.collection_date,
            laboratory_name=lab_result.laboratory_name,
            biomarkers_json=[
                {
                    "id": str(b.id),
                    "name": b.name,
                    "value": b.value.numeric_value,
                    "unit": b.value.unit.value,
                    "ref_min": b.reference_range.minimum,
                    "ref_max": b.reference_range.maximum,
                    "is_critical": b.is_critical,
                }
                for b in lab_result.biomarkers
            ],
            is_processed=lab_result.is_processed,
        )
        self._session.merge(model)
        self._session.commit()

    def find_by_id(self, lab_result_id: UUID) -> Optional[LabResult]:
        model = (
            self._session.query(LabResultModel)
            .filter_by(id=str(lab_result_id))
            .first()
        )
        return self._to_domain(model) if model else None

    def find_by_user(self, user_id: UUID) -> List[LabResult]:
        models = (
            self._session.query(LabResultModel)
            .filter_by(user_id=str(user_id))
            .all()
        )
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: LabResultModel) -> LabResult:
        from uuid import UUID as _UUID

        lab_result = LabResult(
            id=_UUID(model.id),
            user_id=_UUID(model.user_id),
            collection_date=model.collection_date,
            laboratory_name=model.laboratory_name,
            is_processed=model.is_processed,
        )
        for b_data in model.biomarkers_json or []:
            unit = MeasurementUnit(b_data["unit"])
            lab_result.biomarkers.append(
                Biomarker(
                    id=_UUID(b_data["id"]),
                    name=b_data["name"],
                    value=BiomarkerValue(numeric_value=b_data["value"], unit=unit),
                    reference_range=ReferenceRange(
                        minimum=b_data["ref_min"],
                        maximum=b_data["ref_max"],
                        unit=unit,
                    ),
                    is_critical=b_data.get("is_critical", False),
                )
            )
        return lab_result