"""
FASE 1 — NÚCLEO ISOLADO: Engine de Recomendações Nutricionais

Mapeia desvios de biomarcadores em recomendações estruturadas.
Sem dependências externas — mesma política de isolamento do analyzer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from core.analyzer import AnalysisResult, BiomarkerDeviation, Severity


class RecCategory(str, Enum):
    FOOD = "food"
    SUPPLEMENT = "supplement"
    LIFESTYLE = "lifestyle"


@dataclass
class RecommendationData:
    category: RecCategory
    priority: int
    target_biomarker: str
    recommendation: str
    rationale: str


@dataclass
class NutritionPlanData:
    recommendations: List[RecommendationData] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)


# ── Base de conhecimento nutricional: deficiências ────────────────────────────
_DEFICIENCY_MAP: Dict[str, List[Dict]] = {
    "vitamin_d": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Aumentar peixes gordurosos (salmão, sardinha, atum) 3×/semana, gema de ovo e cogumelos expostos ao sol",
            "rationale": "Vitamina D3 biodisponível em peixes gordurosos e gema; cogumelos geram D2 por exposição UV",
        },
        {
            "category": RecCategory.SUPPLEMENT,
            "recommendation": "Vitamina D3 2.000–4.000 UI/dia com vitamina K2-MK7 100 µg/dia, tomada com refeição gordurosa",
            "rationale": "K2 direciona cálcio mobilizado para ossos e evita deposição vascular; D3 é a forma bioativa",
        },
        {
            "category": RecCategory.LIFESTYLE,
            "recommendation": "Exposição solar 15–20 min/dia entre 10h–14h em braços e pernas sem protetor solar",
            "rationale": "UVB converte 7-dihidrocolesterol em D3 na pele; vidro e protetor bloqueiam UVB",
        },
    ],
    "ferritin": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Carnes vermelhas magras 3×/semana, fígado 1×/semana, feijão e lentilha diariamente com fonte de vitamina C",
            "rationale": "Ferro heme (carnes): absorção 15–35%. Ferro não-heme: absorção 2–20%, potencializada 3× por vitamina C",
        },
        {
            "category": RecCategory.FOOD,
            "recommendation": "Evitar chá, café e laticínios nas 2 horas adjacentes às refeições ricas em ferro",
            "rationale": "Taninos (chá/café) e cálcio competem diretamente com absorção de ferro não-heme",
        },
        {
            "category": RecCategory.SUPPLEMENT,
            "recommendation": "Bisglicinato ferroso 30 mg/dia em jejum ou com vitamina C; suplementar cobre 1 mg se uso >8 semanas",
            "rationale": "Bisglicinato: menor irritação gástrica e maior biodisponibilidade que sulfato ferroso. Ferro alto depleta cobre",
        },
    ],
    "vitamin_b12": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Consumo diário de carnes, ovos, laticínios; veganos: levedura nutricional + alimentos B12-fortificados",
            "rationale": "B12 existe naturalmente apenas em alimentos animais; deficiência em veganos sem suplementação é universal",
        },
        {
            "category": RecCategory.SUPPLEMENT,
            "recommendation": "Metilcobalamina 1.000 µg sublingual 3×/semana (ou 2.500 µg/dia se B12 < 200 pg/mL)",
            "rationale": "Metilcobalamina é a forma bioativa; via sublingual contorna má absorção gástrica, comum após 50 anos",
        },
    ],
    "magnesium": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Nozes, sementes de abóbora, chocolate amargo >70%, vegetais folhosos verdes, leguminosas e grãos integrais",
            "rationale": "Sementes de abóbora: 592 mg Mg/100 g. Clorofila tem Mg no centro da molécula (folhosos escuros)",
        },
        {
            "category": RecCategory.SUPPLEMENT,
            "recommendation": "Glicinato de magnésio 300–400 mg/dia em 2 doses; 1 dose à noite (melhora qualidade do sono)",
            "rationale": "Glicinato: alta biodisponibilidade, sem efeito laxante. Magnésio noturno reduz cortisol e melhora sono",
        },
        {
            "category": RecCategory.LIFESTYLE,
            "recommendation": "Reduzir álcool e cafeína excessivos; técnicas de manejo do estresse (cortisol alto depleta magnésio)",
            "rationale": "Álcool aumenta excreção urinária de Mg. Cortisol crônico cria ciclo vicioso de depleção de magnésio",
        },
    ],
    "zinc": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Ostras (maior concentração), carnes vermelhas, sementes de abóbora e castanha de caju diariamente",
            "rationale": "Ostras: 74 mg Zn/100 g. Zinco heme de carnes tem absorção superior ao de cereais (fitato inibe absorção)",
        },
        {
            "category": RecCategory.SUPPLEMENT,
            "recommendation": "Zinco bisglicinato 15–30 mg/dia com refeição; suplementar cobre 2 mg se uso > 8 semanas",
            "rationale": "Altas doses de zinco deslocam cobre por competição. Necessário monitorar razão Cu/Zn",
        },
    ],
    "glucose": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Sequência alimentar: fibras e proteínas ANTES dos carboidratos em toda refeição; priorizar carboidratos complexos de baixo IG",
            "rationale": "Sequência alimentar reduz pico glicêmico pós-prandial em até 73% (Shukla et al., Cell Metabolism 2015)",
        },
        {
            "category": RecCategory.LIFESTYLE,
            "recommendation": "Caminhada leve 10–15 min após as principais refeições; evitar sedentarismo pós-prandial",
            "rationale": "Contração muscular pós-prandial aumenta captação de glicose via GLUT4 independente de insulina",
        },
    ],
    "tsh": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Garantir iodo (sal iodado, algas com moderação) e selênio (2 castanhas-do-pará/dia)",
            "rationale": "Iodo é substrato para T3/T4. Selênio é cofator das deiodinases que convertem T4 inativo em T3 ativo",
        },
        {
            "category": RecCategory.FOOD,
            "recommendation": "Consumir brócolis, couve e soja apenas cozidos; evitar crus em grandes quantidades",
            "rationale": "Goitrogênios em crucíferas interferem na síntese de hormônios tireoidianos; cozimento os inativa",
        },
    ],
    "selenium": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "2–3 castanhas-do-pará/dia (não mais: risco de selenose), frutos do mar, carnes e ovos",
            "rationale": "1 castanha-do-pará = ~100 µg selênio (necessidade diária ~55 µg). Selênio é antioxidante e cofator tireoidiano",
        },
    ],
}

# ── Base de conhecimento nutricional: excessos ────────────────────────────────
_EXCESS_MAP: Dict[str, List[Dict]] = {
    "glucose": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Eliminar açúcares adicionados e bebidas açucaradas; limitar carboidratos simples a <25% das calorias totais",
            "rationale": "Glicose em jejum >99 mg/dL indica pré-diabetes. Redução de simples é intervenção de primeira linha",
        },
        {
            "category": RecCategory.SUPPLEMENT,
            "recommendation": "Berberina 500 mg 3×/dia com refeições (consultar médico — interage com metformina e anticoagulantes)",
            "rationale": "Berberina ativa AMPK com eficácia comparável à metformina; evidências robustas para redução de HbA1c",
        },
    ],
    "ferritin": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Reduzir carnes vermelhas a máx 2×/semana; consumir chá verde ou preto com refeições ricas em ferro",
            "rationale": "Ferritina elevada pode indicar inflamação crônica ou hemocromatose. Excesso de ferro catalisa radicais livres",
        },
        {
            "category": RecCategory.LIFESTYLE,
            "recommendation": "Investigar doação de sangue regular com médico; avaliar marcadores inflamatórios (PCR, VHS, IL-6)",
            "rationale": "Doação de sangue é a forma mais efetiva de reduzir estoques de ferro. Ferritina alta frequentemente acompanha inflamação",
        },
    ],
    "crp": [
        {
            "category": RecCategory.FOOD,
            "recommendation": "Dieta mediterrânea ou anti-inflamatória: aumentar ômega-3 (salmão, sardinha, linhaça), cúrcuma com pimenta-preta, gengibre",
            "rationale": "Curcumina inibe NF-κB. Ômega-3 produz resolvinas e protectinas. Evidências para redução de PCR em 4–12 semanas",
        },
        {
            "category": RecCategory.LIFESTYLE,
            "recommendation": "Priorizar sono 7–9 h/noite; reduzir álcool; cessação tabágica; meditação ou exercício regular",
            "rationale": "Privação de sono aumenta IL-6 e TNF-α. Álcool e tabaco são promotores potentes de inflamação sistêmica",
        },
    ],
    "cortisol": [
        {
            "category": RecCategory.LIFESTYLE,
            "recommendation": "Técnicas de regulação do sistema nervoso: respiração 4-7-8, meditação mindfulness 10 min/dia, limite de cafeína após 14h",
            "rationale": "Cortisol crônico alto promove resistência insulínica, perda muscular e imunossupressão",
        },
        {
            "category": RecCategory.SUPPLEMENT,
            "recommendation": "Ashwagandha (KSM-66) 300–600 mg/dia; fosfatidilserina 400 mg/dia antes de exercício de alta intensidade",
            "rationale": "Ashwagandha reduz cortisol sérico em 27% em 8 semanas (Chandrasekhar et al., IJHS 2012)",
        },
    ],
}


def _base_priority(deviation: BiomarkerDeviation) -> int:
    return {Severity.CRITICAL: 1, Severity.HIGH: 2, Severity.MODERATE: 3, Severity.MILD: 4}[
        deviation.severity
    ]


def generate_plan(
    analysis: AnalysisResult,
    include_supplements: bool = True,
    include_lifestyle: bool = True,
) -> NutritionPlanData:
    """
    Gera plano nutricional estruturado a partir da análise de biomarcadores.

    Args:
        analysis: Resultado do core.analyzer.analyze()
        include_supplements: Configurável por tenant (planos básicos excluem)
        include_lifestyle: Configurável por tenant

    Returns:
        NutritionPlanData com recomendações ordenadas por prioridade clínica
    """
    plan = NutritionPlanData()
    all_deviations = sorted(
        analysis.deficiencies + analysis.excesses, key=_base_priority
    )

    priority_counter = 1
    seen: set = set()

    for deviation in all_deviations:
        if deviation.deviation_type == "deficiency":
            recs = _DEFICIENCY_MAP.get(deviation.biomarker, [])
        else:
            recs = _EXCESS_MAP.get(deviation.biomarker, [])

        for rec in recs:
            category: RecCategory = rec["category"]

            if category == RecCategory.SUPPLEMENT and not include_supplements:
                continue
            if category == RecCategory.LIFESTYLE and not include_lifestyle:
                continue

            dedup_key = (deviation.biomarker, rec["recommendation"][:60])
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            plan.recommendations.append(
                RecommendationData(
                    category=category,
                    priority=priority_counter,
                    target_biomarker=deviation.biomarker,
                    recommendation=rec["recommendation"],
                    rationale=rec["rationale"],
                )
            )
            priority_counter += 1

    # ── Key findings ─────────────────────────────────────────────────────────
    score = analysis.overall_score
    if score >= 80:
        plan.key_findings.append(f"Perfil laboratorial geral adequado (score {score}/100)")
    elif score >= 60:
        plan.key_findings.append(
            f"Perfil com alterações moderadas (score {score}/100) — acompanhamento recomendado"
        )
    else:
        plan.key_findings.append(
            f"Perfil com alterações significativas (score {score}/100) — avaliação médica prioritária"
        )

    flag_messages = {
        "CRITICAL_VALUES_PRESENT": "Valores críticos detectados — avaliação médica imediata recomendada",
        "INSULIN_RESISTANCE": "Resistência insulínica suspeita — protocolo de controle glicêmico prioritário",
        "IRON_DEFICIENCY_ANEMIA": "Anemia ferropriva suspeita — reposição direcionada e investigação da causa",
        "SEVERE_VITAMIN_D_DEFICIENCY": "Deficiência grave de vitamina D — suplementação de alta dose recomendada",
        "HYPOTHYROIDISM_SUSPECTED": "Hipotireoidismo suspeito — avaliação endocrinológica recomendada",
        "CHRONIC_INFLAMMATION": "Marcador de inflamação crônica elevado — protocolo anti-inflamatório prioritário",
    }
    for flag in analysis.flags:
        for key, message in flag_messages.items():
            if key in flag:
                plan.key_findings.append(message)
                break

    # ── Contraindications ────────────────────────────────────────────────────
    if "IRON_DEFICIENCY_ANEMIA_SUSPECTED" in analysis.flags:
        plan.contraindications.append(
            "Evitar doação de sangue até normalização dos estoques de ferro"
        )

    has_excess_ferritin = any(
        d.biomarker == "ferritin" and d.deviation_type == "excess" for d in analysis.excesses
    )
    if has_excess_ferritin:
        plan.contraindications.append(
            "Evitar suplementos de ferro e multivitamínicos com ferro sem orientação médica"
        )

    return plan