from abc import ABC, abstractmethod

from domain.entities.lab_exam import LabExam
from domain.entities.patient import Patient


class AIAnalysisProviderPort(ABC):
    """
    Secondary port (driven) for AI-powered nutritional analysis.

    Treated symmetrically with all other external systems — the domain
    never knows whether the implementation uses Claude, GPT-4, or any other model.
    """

    @abstractmethod
    async def analyze(
        self,
        patient: Patient,
        exam: LabExam,
        domain_findings: list[str],
    ) -> str:
        """
        Returns a comprehensive AI-generated nutritional analysis narrative.

        Args:
            patient: The patient entity with demographic context.
            exam: The lab exam with all results.
            domain_findings: Human-readable strings from domain classification.

        Returns:
            Markdown-formatted nutritional analysis string.
        """
        ...