import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_reference_range, get_tenant_config
from core.analyzer import AnalysisResult, analyze
from models import ExamAnalysis, ExamStatus, LabExam


class ExamService:
    """
    FASE 2 — SERVICE LAYER: orquestra exames sem saber qual interface chamou.
    Toda lógica clínica é delegada ao core/ isolado.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_exam(
        self,
        patient_id: str,
        tenant_id: str,
        exam_date: str,
        biomarkers: dict,
        lab_name: Optional[str] = None,
    ) -> LabExam:
        exam = LabExam(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            tenant_id=tenant_id,
            exam_date=exam_date,
            lab_name=lab_name,
            biomarkers=biomarkers,
            status=ExamStatus.PENDING,
        )
        self.db.add(exam)
        await self.db.flush()
        return exam

    async def analyze_exam(self, exam_id: str, tenant_id: str) -> ExamAnalysis:
        result = await self.db.execute(
            select(LabExam).where(LabExam.id == exam_id, LabExam.tenant_id == tenant_id)
        )
        exam = result.scalar_one_or_none()
        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        # FASE 3 — CONFIG-DRIVEN: faixas de referência específicas por tenant
        reference_ranges = {}
        for biomarker in exam.biomarkers:
            ref = get_reference_range(biomarker, tenant_id)
            if ref:
                reference_ranges[biomarker] = (ref.min_normal, ref.max_normal, ref.unit)

        # FASE 4 — ISOLAMENTO: toda análise clínica fica no core/ sem deps externas
        analysis_result: AnalysisResult = analyze(
            exam_id=exam_id,
            biomarkers={k: float(v) for k, v in exam.biomarkers.items()},
            reference_ranges=reference_ranges,
        )

        exam_analysis = ExamAnalysis(
            id=str(uuid.uuid4()),
            exam_id=exam_id,
            deficiencies=[
                {
                    "biomarker": d.biomarker,
                    "value": d.value,
                    "unit": d.unit,
                    "reference_min": d.reference_min,
                    "reference_max": d.reference_max,
                    "deviation_percent": d.deviation_percent,
                    "severity": d.severity.value,
                }
                for d in analysis_result.deficiencies
            ],
            excesses=[
                {
                    "biomarker": d.biomarker,
                    "value": d.value,
                    "unit": d.unit,
                    "reference_min": d.reference_min,
                    "reference_max": d.reference_max,
                    "deviation_percent": d.deviation_percent,
                    "severity": d.severity.value,
                }
                for d in analysis_result.excesses
            ],
            risk_scores=analysis_result.risk_scores,
            overall_score=analysis_result.overall_score,
            flags=analysis_result.flags,
        )

        exam.status = ExamStatus.ANALYZED
        self.db.add(exam_analysis)
        await self.db.flush()
        return exam_analysis

    async def get_exam_by_id(self, exam_id: str, tenant_id: str) -> Optional[LabExam]:
        result = await self.db.execute(
            select(LabExam).where(LabExam.id == exam_id, LabExam.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_patient_exams(self, patient_id: str, tenant_id: str) -> list[LabExam]:
        result = await self.db.execute(
            select(LabExam)
            .where(LabExam.patient_id == patient_id, LabExam.tenant_id == tenant_id)
            .order_by(LabExam.exam_date.desc())
        )
        return list(result.scalars().all())