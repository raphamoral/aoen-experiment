import json
import uuid
from datetime import datetime

import anthropic

from entities.exam import Exam
from entities.nutrient import Nutrient, NutrientCategory
from entities.nutrition_plan import Meal, NutritionPlan
from entities.patient import Patient
from use_cases.ports.ai_nutrition_service_port import AiNutritionServicePort

_SYSTEM_PROMPT = """Você é um nutricionista clínico especialista em nutrição baseada em evidências laboratoriais.
Analise os dados do paciente e os marcadores laboratoriais para criar um plano nutricional personalizado.
Responda APENAS com JSON válido, sem markdown, sem texto adicional fora do JSON."""

_RESPONSE_SCHEMA = {
    "daily_calories_kcal": "number",
    "ai_rationale": "string — explicação clínica baseada nos marcadores alterados",
    "restrictions": ["alimentos/grupos a evitar e por quê"],
    "meals": [
        {
            "name": "string (ex: Café da Manhã)",
            "time_suggestion": "HH:MM",
            "foods": ["alimento com quantidade aproximada"],
            "calories_kcal": "number",
            "notes": "string",
        }
    ],
    "nutrients": [
        {
            "name": "string",
            "category": "macronutrient | vitamin | mineral | fatty_acid",
            "daily_target_g": "number",
            "unit": "g | mg | mcg",
            "reason": "string — motivo clínico baseado nos exames",
        }
    ],
}


class AnthropicNutritionService(AiNutritionServicePort):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6") -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def generate_plan(self, patient: Patient, exam: Exam) -> NutritionPlan:
        prompt = self._build_prompt(patient, exam)
        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(response.content[0].text)
        return self._to_entity(data, patient_id=patient.id, exam_id=exam.id)

    def _build_prompt(self, patient: Patient, exam: Exam) -> str:
        markers_lines = "\n".join(
            f"  • {m.name}: {m.value} {m.unit} "
            f"(ref: {m.reference_min}–{m.reference_max}) [{m.status.value.upper()}]"
            for m in exam.markers
        )
        abnormal_lines = (
            "\n".join(
                f"  ⚠ {m.name}: {m.value} {m.unit} [{m.status.value}]"
                for m in exam.abnormal_markers
            )
            or "  Nenhum marcador alterado"
        )
        return f"""PACIENTE:
- Nome: {patient.name}
- Idade: {patient.age} anos | Gênero: {patient.gender.value}
- Peso: {patient.weight_kg} kg | Altura: {patient.height_cm} cm
- IMC: {patient.bmi} ({patient.bmi_classification})

EXAME LABORATORIAL — {exam.lab_name} ({exam.exam_date.strftime("%d/%m/%Y")}):
{markers_lines}

MARCADORES ALTERADOS:
{abnormal_lines}

Gere o plano nutricional personalizado seguindo exatamente este schema JSON:
{json.dumps(_RESPONSE_SCHEMA, indent=2, ensure_ascii=False)}"""

    def _to_entity(self, data: dict, patient_id: str, exam_id: str) -> NutritionPlan:
        meals = [
            Meal(
                name=m["name"],
                time_suggestion=m["time_suggestion"],
                foods=m["foods"],
                calories_kcal=float(m["calories_kcal"]),
                notes=m.get("notes", ""),
            )
            for m in data["meals"]
        ]
        nutrients = [
            Nutrient(
                name=n["name"],
                category=NutrientCategory(n["category"]),
                daily_target_g=float(n["daily_target_g"]),
                unit=n["unit"],
                reason=n["reason"],
            )
            for n in data["nutrients"]
        ]
        return NutritionPlan(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            exam_id=exam_id,
            generated_at=datetime.now(),
            daily_calories_kcal=float(data["daily_calories_kcal"]),
            meals=meals,
            nutrients=nutrients,
            restrictions=data.get("restrictions", []),
            ai_rationale=data["ai_rationale"],
        )