from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

from use_cases.get_patient_report import GetPatientReport, GetPatientReportInput, PatientReport
from use_cases.register_patient import RegisterPatient, RegisterPatientInput


@dataclass
class RegisterPatientRequest:
    name: str
    birth_date: date
    gender: str
    weight_kg: float
    height_cm: float
    email: str


class PatientController:
    def __init__(
        self,
        register_patient: RegisterPatient,
        get_patient_report: GetPatientReport,
    ) -> None:
        self._register_patient = register_patient
        self._get_report = get_patient_report

    def register(self, request: RegisterPatientRequest) -> Dict[str, Any]:
        output = self._register_patient.execute(
            RegisterPatientInput(
                name=request.name,
                birth_date=request.birth_date,
                gender=request.gender,
                weight_kg=request.weight_kg,
                height_cm=request.height_cm,
                email=request.email,
            )
        )
        return self._present_patient(output.patient)

    def get_report(self, patient_id: str) -> Dict[str, Any]:
        report = self._get_report.execute(GetPatientReportInput(patient_id=patient_id))
        return self._present_report(report)

    # --- presenters (Controller + Presenter unificados para REST simples) ---

    def _present_patient(self, patient) -> Dict[str, Any]:
        return {
            "id": patient.id,
            "name": patient.name,
            "email": patient.email,
            "age": patient.age,
            "bmi": patient.bmi,
            "bmi_classification": patient.bmi_classification,
            "gender": patient.gender.value,
        }

    def _present_report(self, report: PatientReport) -> Dict[str, Any]:
        return {
            "patient": self._present_patient(report.patient),
            "total_exams": report.total_exams,
            "has_critical_markers": report.has_critical_markers,
            "latest_nutrition_plan": (
                self._present_plan_summary(report.latest_nutrition_plan)
                if report.latest_nutrition_plan else None
            ),
            "exams": [self._present_exam_summary(e) for e in report.exams],
        }

    def _present_exam_summary(self, exam) -> Dict[str, Any]:
        return {
            "id": exam.id,
            "exam_date": exam.exam_date.isoformat(),
            "lab_name": exam.lab_name,
            "total_markers": len(exam.markers),
            "abnormal_count": len(exam.abnormal_markers),
            "critical_count": len(exam.critical_markers),
        }

    def _present_plan_summary(self, plan) -> Dict[str, Any]:
        return {
            "id": plan.id,
            "generated_at": plan.generated_at.isoformat(),
            "daily_calories_kcal": plan.daily_calories_kcal,
            "meals_count": len(plan.meals),
            "is_calorie_balanced": plan.is_calorie_balanced,
        }