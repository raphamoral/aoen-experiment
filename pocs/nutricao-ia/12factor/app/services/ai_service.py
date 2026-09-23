"""
Factor IV: Anthropic Claude tratado como backing service.
A URL/chave vem de env vars; pode ser trocado (outro provider, mock) sem alterar lógica.
Factor VI: Stateless — nenhuma conversa é mantida em memória entre requests.
"""
import json
import structlog
from anthropic import AsyncAnthropic
from app.config import settings

log = structlog.get_logger()

_client: AsyncAnthropic | None = None


def get_anthropic_client() -> AsyncAnthropic:
    """Singleton lazy — conecta ao backing service na primeira chamada."""
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


SYSTEM_PROMPT = """Você é um nutricionista clínico especializado em análise de exames laboratoriais.
Sua função é analisar marcadores bioquímicos e gerar recomendações nutricionais personalizadas,
baseadas em evidências científicas.

REGRAS:
- Sempre mencione que as recomendações não substituem consulta médica/nutricional presencial.
- Baseie as recomendações nos valores de referência fornecidos.
- Seja específico: cite alimentos, quantidades e frequências quando possível.
- Identifique deficiências, excessos e marcadores limítrofes.
- Responda SEMPRE em JSON estruturado conforme o schema solicitado."""


async def analyze_exam_with_ai(
    user_profile: dict,
    exam_markers: dict,
) -> dict:
    """
    Envia exame para Claude e retorna recomendações estruturadas.
    Stateless: cada chamada é independente, sem histórico de conversa.
    """
    client = get_anthropic_client()

    user_context = (
        f"Perfil do paciente: {json.dumps(user_profile, ensure_ascii=False)}\n"
        f"Marcadores laboratoriais: {json.dumps(exam_markers, ensure_ascii=False)}"
    )

    schema = {
        "summary": "resumo executivo em 2-3 frases",
        "deficiencies": [{"marker": "nome", "value": 0.0, "recommendation": "ação nutricional"}],
        "excesses": [{"marker": "nome", "value": 0.0, "recommendation": "ação nutricional"}],
        "borderline": [{"marker": "nome", "value": 0.0, "recommendation": "ação nutricional"}],
        "meal_plan_adjustments": ["ajuste 1", "ajuste 2"],
        "foods_to_increase": [{"food": "nome", "reason": "justificativa", "frequency": "frequência sugerida"}],
        "foods_to_reduce": [{"food": "nome", "reason": "justificativa"}],
        "supplements_to_consider": [{"supplement": "nome", "reason": "justificativa", "note": "consultar profissional"}],
        "disclaimer": "string obrigatória de aviso legal",
    }

    prompt = (
        f"{user_context}\n\n"
        f"Gere recomendações nutricionais personalizadas no seguinte JSON schema:\n"
        f"{json.dumps(schema, indent=2, ensure_ascii=False)}"
    )

    log.info("ai_request", model=settings.ANTHROPIC_MODEL, markers_count=len(exam_markers))

    response = await client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=settings.ANTHROPIC_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text

    # Extrai JSON da resposta
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    parsed = json.loads(raw_text[start:end])

    log.info("ai_response", input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens)

    return parsed