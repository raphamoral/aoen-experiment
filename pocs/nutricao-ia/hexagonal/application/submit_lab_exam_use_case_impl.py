from domain.entities.lab_exam import ExamResult, LabExam
from domain.exceptions import PatientNotFoundError
from ports.input.submit_lab_exam_use_case import (
    SubmitLabExamCommand,
    SubmitLabExamUseCasePort,
)
from ports.output.lab_exam_repository_port import LabExamRepositoryPort
from ports.output.patient_repository_port import PatientRepositoryPort


class SubmitLabExamUseCaseImpl(SubmitLabExamUseCasePort):
    def __init__(
        self,
        patient_repo: PatientRepositoryPort,
        lab_exam_repo: LabExamRepositoryPort,
    ) -> None:
        self._patient_repo = patient_repo
        self._lab_exam_repo = lab_exam_repo

    async def execute(self, command: SubmitLabExamCommand) -> LabExam:
        patient = await self._patient_repo.find_by_id(command.patient_id)
        if not patient:
            raise PatientNotFoundError(command.patient_id)

        results = [
            ExamResult(
                exam_type=r.exam_type,
                value=r.value,
                unit=r.unit,
                reference_min=r.reference_min,
                reference_max=r.reference_max,
            )
            for r in command.results
        ]

        exam = LabExam(
            patient_id=command.patient_id,
            exam_date=command.exam_date,
            results=results,
        )
        return await self._lab_exam_repo.save(exam)