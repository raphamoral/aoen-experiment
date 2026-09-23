from uuid import UUID


class DomainError(Exception):
    pass


class PatientNotFoundError(DomainError):
    def __init__(self, patient_id: UUID) -> None:
        super().__init__(f"Patient not found: {patient_id}")
        self.patient_id = patient_id


class LabExamNotFoundError(DomainError):
    def __init__(self, exam_id: UUID) -> None:
        super().__init__(f"Lab exam not found: {exam_id}")
        self.exam_id = exam_id


class NutritionPlanNotFoundError(DomainError):
    def __init__(self, plan_id: UUID) -> None:
        super().__init__(f"Nutrition plan not found: {plan_id}")
        self.plan_id = plan_id


class DomainValidationError(DomainError):
    pass


class DuplicateEmailError(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email}")
        self.email = email