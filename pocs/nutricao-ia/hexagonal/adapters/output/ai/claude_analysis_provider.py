import anthropic

from domain.entities.lab_exam import LabExam
from domain.entities.patient import Patient
from ports.output.ai_analysis_provider_port import AIAnalysisProviderPort


class ClaudeAnalysisProvider(AIAnalysisProviderPort):
    """
    Driven adapter that connects the hexagon to the Anthropic Claude API.

    Symmetrically replaceable with any other AI provider by implementing
    AIAnalysisProviderPort — the domain never knows which model is in use.
    """

    def __init__(self, api_key: str, model: str = "claude-opus-4-6") -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    def _build_prompt(
        self,
        patient: Patient,
        exam: LabExam,
        domain_findings: list[str],
    ) -> str:
        goals = ", ".join(patient.health_goals) if patient.health_goals else "general health improvement"
        findings_text = "\n".join(f"  - {f}" for f in domain_findings)
        results_text = "\n".join(
            f"  - {r.exam_type}: {r.value} {r.unit}"
            + (f" (ref: {r.reference_min}–{r.reference_max})" if r.reference_min or r.reference_max else "")
            for r in exam.results
        )

        return f"""You are a clinical nutritionist with expertise in functional medicine and nutrigenomics.

Analyze the following laboratory results and provide a comprehensive, personalized nutritional plan.

## Patient Profile
- Age: {patient.age} years old
- Gender: {"Male" if patient.gender == "M" else "Female"}
- Health Goals: {goals}
- Exam Date: {exam.exam_date}

## Laboratory Results
{results_text}

## Domain Classification (rule-based analysis)
{findings_text}

## Required Output
Provide a structured nutritional analysis in Markdown with:

1. **Executive Summary** — 2–3 sentence overview of the patient's nutritional status
2. **Priority Issues** — ranked list of the most urgent nutritional concerns with clinical rationale
3. **Personalized Dietary Strategy** — specific dietary pattern recommendation (e.g., Mediterranean, anti-inflammatory) justified by the exam results
4. **Nutrient-Specific Action Plan** — for each abnormal result: food sources, meal timing, synergistic nutrients
5. **7-Day Sample Meal Blueprint** — a conceptual meal framework aligned with the patient's findings and goals
6. **Supplement Protocol** — evidence-based recommendations with dosages and timing (note: requires medical supervision)
7. **Monitoring & Follow-Up** — which markers to retest and when

Be specific, evidence-based, and personalize recommendations to this patient's unique lab profile and goals.
Important: always note that supplementation requires medical supervision."""

    async def analyze(
        self,
        patient: Patient,
        exam: LabExam,
        domain_findings: list[str],
    ) -> str:
        prompt = self._build_prompt(patient, exam, domain_findings)
        message = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text