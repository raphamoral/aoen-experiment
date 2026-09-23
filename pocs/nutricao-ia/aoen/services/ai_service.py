"""
Wrapper do Anthropic SDK — único ponto de contato com IA externa.
Isolado do core/ para que o núcleo permaneça sem dependências.
"""

import json

import anthropic

from config import get_settings
from core.analyzer import AnalysisResult
from core.nutrition_engine import NutritionPlanData


class AIService:
    def __init__(self):
        settings = get_settings()
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate_nutrition_narrative(
        self,
        analysis_result: AnalysisResult,
        plan_data: NutritionPlanData,
        language: str = "pt-BR",
        model: str = "claude-sonnet-4-6",
    ) -> str:
        """Narrativa humanizada do plano nutricional gerada por IA."""

        deficiencies_txt = "\n".join(
            f"- {d.biomarker}: {d.value} {d.unit} "
            f"(ref: {d.reference_min}–{d.reference_max}, déficit {d.deviation_percent:.1f}%, {d.severity.value})"
            for d in analysis_result.deficiencies
        ) or "Nenhuma deficiência identificada"

        excesses_txt = "\n".join(
            f"- {d.biomarker}: {d.value} {d.unit} "
            f"(ref: {d.reference_min}–{d.reference_max}, excesso {d.deviation_percent:.1f}%, {d.severity.value})"
            for d in analysis_result.excesses
        ) or "Nenhum excesso identificado"

        top_recs_txt = "\n".join(
            f"- [{r.category.value.upper()}] {r.recommendation}"
            for r in plan_data.recommendations[:6]
        )

        key_findings_txt = "\n".join(f"- {f}" for f in plan_data.key_findings)

        prompt = f"""Você é um nutricionista clínico especializado em nutrição funcional baseada em evidências.

Com base na análise laboratorial abaixo, gere um relatório nutricional personalizado em {language}.

SCORE GERAL DE SAÚDE: {analysis_result.overall_score}/100
SCORES DE RISCO POR CATEGORIA: {json.dumps(analysis_result.risk_scores, ensure_ascii=False)}

DEFICIÊNCIAS IDENTIFICADAS:
{deficiencies_txt}

EXCESSOS IDENTIFICADOS:
{excesses_txt}

FLAGS CLÍNICOS: {', '.join(analysis_result.flags) if analysis_result.flags else 'Nenhum'}

PRINCIPAIS ACHADOS:
{key_findings_txt}

PRINCIPAIS RECOMENDAÇÕES:
{top_recs_txt}

INSTRUÇÕES:
1. Avaliação geral do perfil nutricional em 2–3 parágrafos acessíveis
2. Explique o impacto das principais deficiências na energia, imunidade e metabolismo
3. Destaque os pontos de atenção mais urgentes com linguagem motivadora
4. Apresente a estratégia prioritária de intervenção nutricional
5. Finalize com aviso de que o plano deve ser acompanhado por profissional de saúde habilitado
6. Linguagem empática, direta e baseada em evidências. Máximo 500 palavras.

Gere apenas o texto do relatório, sem títulos markdown."""

        message = await self.client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    async def interpret_biomarker(
        self,
        biomarker: str,
        value: float,
        unit: str,
        language: str = "pt-BR",
        model: str = "claude-haiku-4-5-20251001",
    ) -> str:
        """Interpretação rápida de um único biomarcador — modelo mais leve por custo."""
        message = await self.client.messages.create(
            model=model,
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Em {language}, explique em 2–3 frases o que significa "
                        f"{biomarker} = {value} {unit} para a saúde de forma acessível."
                    ),
                }
            ],
        )
        return message.content[0].text