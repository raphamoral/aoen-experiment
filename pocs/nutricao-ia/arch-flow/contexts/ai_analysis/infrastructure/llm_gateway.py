import json
import logging
import re
from typing import Any, Dict, List

import anthropic

logger = logging.getLogger(__name__)

ANALYSIS_SYSTEM_PROMPT = """Você é um especialista em medicina laboratorial e nutrição clínica.
Analise os biomarcadores fornecidos e gere insights clínicos personalizados.

Responda SEMPRE em JSON válido com exatamente esta estrutura:
{
  "summary": "Resumo executivo da análise em 2-3 frases claras para o paciente",
  "insights": [
    {
      "title": "Título conciso do insight",
      "description": "Descrição detalhada da correlação clínica identificada",
      "risk_level": "critico|alto|moderado|baixo|informativo",
      "category": "cardiovascular|metabolico|hormonal|nutricional|inflamatorio|renal|hepatico|imune",
      "biomarkers_involved": ["nome_biomarcador_1", "nome_biomarcador_2"],
      "recommendation": "Recomendação nutricional específica e acionável",
      "evidence_basis": "Base científica resumida (ex: estudos, guidelines)"
    }
  ]
}

Diretrizes:
- Priorize correlações clínicas entre múltiplos biomarcadores
- Foque em recomendações nutricionais baseadas em evidências
- Use linguagem clara para o paciente, sem jargão excessivo
- Para risco "critico": oriente a buscar avaliação médica urgente
- Gere entre 2 e 6 insights por análise"""


class AnthropicLLMGateway:
    """Gateway para o modelo Claude (Anthropic) — Anti-Corruption Layer.

    Isola o domínio de negócio dos detalhes da API do LLM.
    O domínio recebe HealthInsight (conceito do domínio),
    não respostas brutas do modelo de linguagem.

    Wardley: este gateway em si é Commodity — a IA subjacente
    pode ser substituída sem impactar o modelo de domínio.
    O valor diferencial está nos prompts e no modelo de domínio,
    não na integração com o LLM específico.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-6",
    ) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def analyze_biomarkers(
        self,
        biomarkers: List[Dict[str, Any]],
        user_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analisa biomarcadores e retorna insights clínicos estruturados."""
        prompt = self._build_prompt(biomarkers, user_context)

        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_response = message.content[0].text
        logger.debug("LLM response: %d chars, model: %s", len(raw_response), self._model)

        return self._parse_response(raw_response)

    def _build_prompt(
        self,
        biomarkers: List[Dict[str, Any]],
        user_context: Dict[str, Any],
    ) -> str:
        biomarkers_text = "\n".join(
            f"- {b['name']}: {b['value']} {b['unit']} "
            f"(ref: {b.get('ref_min', '?')}-{b.get('ref_max', '?')} {b['unit']}) "
            f"[{b.get('status', 'desconhecido')}]"
            for b in biomarkers
        )

        context_lines = []
        if user_context:
            if age := user_context.get("age"):
                context_lines.append(f"- Idade: {age} anos")
            if sex := user_context.get("biological_sex"):
                context_lines.append(f"- Sexo biológico: {sex}")
            if goals := user_context.get("health_goals"):
                context_lines.append(f"- Objetivos: {', '.join(goals)}")
            if conditions := user_context.get("health_conditions"):
                context_lines.append(f"- Condições de saúde: {', '.join(conditions)}")

        context_text = (
            "\nPerfil do Paciente:\n" + "\n".join(context_lines)
            if context_lines
            else ""
        )

        return (
            f"Analise os seguintes biomarcadores laboratoriais:\n\n"
            f"{biomarkers_text}\n"
            f"{context_text}\n\n"
            f"Identifique correlações clínicas e gere insights nutricionais personalizados."
        )

    def _parse_response(self, raw_response: str) -> Dict[str, Any]:
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(
                f"LLM não retornou JSON válido: {raw_response[:300]}"
            )