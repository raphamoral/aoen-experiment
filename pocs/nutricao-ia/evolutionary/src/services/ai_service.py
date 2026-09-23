"""
AI Service — Abstração reversível de provider de IA (ADR-002).

AIProvider é um Protocol estrutural: qualquer objeto que implemente os métodos
satisfaz o contrato, sem herança obrigatória. Trocar de provider não requer
alteração nos services que o consomem.

Decisão (Last Responsible Moment): integração com provider real só quando o MVP
validar o modelo de negócio e justificar o custo de API.
"""

import json
from typing import Protocol, runtime_checkable

import httpx

from src.config import settings


@runtime_checkable
class AIProvider(Protocol):
    async def generate_nutrition_plan(self, user_data: dict, exam_data: dict) -> dict: ...
    async def analyze_deficiencies(self, exam_data: dict) -> dict: ...


class MockAIProvider:
    """
    Provider determinístico para desenvolvimento e testes.
    Ativado quando AI_PROVIDER=mock ou AI_API_KEY está vazio.
    Garante reprodutibilidade nas fitness functions de performance e segurança.
    """

    async def generate_nutrition_plan(self, user_data: dict, exam_data: dict) -> dict:
        return {
            "deficiencias": ["vitamina_d", "ferro", "b12"],
            "recomendacoes": ["salmão", "espinafre", "ovos", "lentilha", "fígado bovino"],
            "restricoes": ["açúcar refinado", "ultraprocessados", "álcool"],
            "suplementos": [
                {"nome": "Vitamina D3", "dose": "2000 UI", "frequencia": "diária"},
                {"nome": "Ferro quelato", "dose": "30 mg", "frequencia": "em jejum"},
                {"nome": "B12 metilcobalamina", "dose": "1000 mcg", "frequencia": "diária"},
            ],
            "meta_calorica": 2200,
            "macros": {"proteinas": 30, "carboidratos": 40, "gorduras": 30},
        }

    async def analyze_deficiencies(self, exam_data: dict) -> dict:
        return {
            "deficiencias": [
                {
                    "nutriente": "vitamina_d",
                    "severidade": "moderada",
                    "valor_atual": 18,
                    "referencia": "30-100 ng/mL",
                },
                {
                    "nutriente": "ferro",
                    "severidade": "leve",
                    "valor_atual": 55,
                    "referencia": "60-170 µg/dL",
                },
            ],
            "valores_alterados": ["25-OH Vitamina D", "Ferro sérico"],
            "urgencia": "medio",
        }


class OpenAIProvider:
    """Provider OpenAI — ativado via AI_PROVIDER=openai e AI_API_KEY definido."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self._base_url = "https://api.openai.com/v1"

    async def generate_nutrition_plan(self, user_data: dict, exam_data: dict) -> dict:
        prompt = (
            "Analise os dados do usuário e exames laboratoriais abaixo e gere um plano "
            "nutricional personalizado em JSON.\n"
            f"Usuário: {json.dumps(user_data, ensure_ascii=False)}\n"
            f"Exames: {json.dumps(exam_data, ensure_ascii=False)}\n"
            "Retorne JSON com as chaves: deficiencias, recomendacoes, restricoes, "
            "suplementos, meta_calorica, macros."
        )
        return await self._chat(prompt)

    async def analyze_deficiencies(self, exam_data: dict) -> dict:
        prompt = (
            "Analise os exames laboratoriais abaixo e identifique deficiências nutricionais.\n"
            f"Exames: {json.dumps(exam_data, ensure_ascii=False)}\n"
            "Retorne JSON com as chaves: deficiencias, valores_alterados, urgencia."
        )
        return await self._chat(prompt)

    async def _chat(self, prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)


def get_ai_provider() -> AIProvider:
    """
    Factory — único ponto de decisão sobre qual provider usar.
    Services nunca instanciam providers diretamente; sempre chamam esta factory.
    """
    if settings.AI_PROVIDER == "openai" and settings.AI_API_KEY:
        return OpenAIProvider(api_key=settings.AI_API_KEY, model=settings.AI_MODEL)
    return MockAIProvider()