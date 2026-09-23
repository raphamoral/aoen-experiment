from domain.entities.lab_exam import ExamResult, LabExam
from domain.entities.nutrition_plan import DietaryRecommendation
from domain.entities.patient import Patient
from domain.value_objects.nutrient_level import NutrientLevel

# (level, min_inclusive, max_exclusive) — None means unbounded
_REFERENCE_RANGES: dict[str, list[tuple[NutrientLevel, float | None, float | None]]] = {
    "vitamin_d": [
        (NutrientLevel.DEFICIENT, None, 20.0),
        (NutrientLevel.LOW, 20.0, 30.0),
        (NutrientLevel.NORMAL, 30.0, 100.0),
        (NutrientLevel.HIGH, 100.0, 150.0),
        (NutrientLevel.VERY_HIGH, 150.0, None),
    ],
    "ferritin_male": [
        (NutrientLevel.DEFICIENT, None, 30.0),
        (NutrientLevel.LOW, 30.0, 50.0),
        (NutrientLevel.NORMAL, 50.0, 300.0),
        (NutrientLevel.HIGH, 300.0, 400.0),
        (NutrientLevel.VERY_HIGH, 400.0, None),
    ],
    "ferritin_female": [
        (NutrientLevel.DEFICIENT, None, 12.0),
        (NutrientLevel.LOW, 12.0, 20.0),
        (NutrientLevel.NORMAL, 20.0, 200.0),
        (NutrientLevel.HIGH, 200.0, 300.0),
        (NutrientLevel.VERY_HIGH, 300.0, None),
    ],
    "hemoglobin_male": [
        (NutrientLevel.DEFICIENT, None, 11.0),
        (NutrientLevel.LOW, 11.0, 13.5),
        (NutrientLevel.NORMAL, 13.5, 17.5),
        (NutrientLevel.HIGH, 17.5, 20.0),
        (NutrientLevel.VERY_HIGH, 20.0, None),
    ],
    "hemoglobin_female": [
        (NutrientLevel.DEFICIENT, None, 10.0),
        (NutrientLevel.LOW, 10.0, 12.0),
        (NutrientLevel.NORMAL, 12.0, 16.0),
        (NutrientLevel.HIGH, 16.0, 18.0),
        (NutrientLevel.VERY_HIGH, 18.0, None),
    ],
    "vitamin_b12": [
        (NutrientLevel.DEFICIENT, None, 200.0),
        (NutrientLevel.LOW, 200.0, 300.0),
        (NutrientLevel.NORMAL, 300.0, 900.0),
        (NutrientLevel.HIGH, 900.0, 1200.0),
        (NutrientLevel.VERY_HIGH, 1200.0, None),
    ],
    "folic_acid": [
        (NutrientLevel.DEFICIENT, None, 3.0),
        (NutrientLevel.LOW, 3.0, 5.0),
        (NutrientLevel.NORMAL, 5.0, 20.0),
        (NutrientLevel.HIGH, 20.0, None),
    ],
    "fasting_glucose": [
        (NutrientLevel.LOW, None, 70.0),
        (NutrientLevel.NORMAL, 70.0, 99.0),
        (NutrientLevel.HIGH, 99.0, 126.0),
        (NutrientLevel.VERY_HIGH, 126.0, None),
    ],
    "hba1c": [
        (NutrientLevel.NORMAL, None, 5.7),
        (NutrientLevel.HIGH, 5.7, 6.5),
        (NutrientLevel.VERY_HIGH, 6.5, None),
    ],
    "ldl_cholesterol": [
        (NutrientLevel.NORMAL, None, 130.0),
        (NutrientLevel.HIGH, 130.0, 160.0),
        (NutrientLevel.VERY_HIGH, 160.0, None),
    ],
    "hdl_cholesterol_male": [
        (NutrientLevel.DEFICIENT, None, 40.0),
        (NutrientLevel.LOW, 40.0, 60.0),
        (NutrientLevel.NORMAL, 60.0, None),
    ],
    "hdl_cholesterol_female": [
        (NutrientLevel.DEFICIENT, None, 50.0),
        (NutrientLevel.LOW, 50.0, 60.0),
        (NutrientLevel.NORMAL, 60.0, None),
    ],
    "triglycerides": [
        (NutrientLevel.NORMAL, None, 150.0),
        (NutrientLevel.HIGH, 150.0, 200.0),
        (NutrientLevel.VERY_HIGH, 200.0, None),
    ],
    "tsh": [
        (NutrientLevel.DEFICIENT, None, 0.4),
        (NutrientLevel.NORMAL, 0.4, 4.0),
        (NutrientLevel.HIGH, 4.0, 10.0),
        (NutrientLevel.VERY_HIGH, 10.0, None),
    ],
    "zinc": [
        (NutrientLevel.DEFICIENT, None, 60.0),
        (NutrientLevel.LOW, 60.0, 70.0),
        (NutrientLevel.NORMAL, 70.0, 120.0),
        (NutrientLevel.HIGH, 120.0, None),
    ],
    "magnesium": [
        (NutrientLevel.DEFICIENT, None, 1.5),
        (NutrientLevel.LOW, 1.5, 1.8),
        (NutrientLevel.NORMAL, 1.8, 2.6),
        (NutrientLevel.HIGH, 2.6, None),
    ],
    "calcium": [
        (NutrientLevel.DEFICIENT, None, 8.5),
        (NutrientLevel.NORMAL, 8.5, 10.5),
        (NutrientLevel.HIGH, 10.5, None),
    ],
    "uric_acid_male": [
        (NutrientLevel.NORMAL, None, 7.0),
        (NutrientLevel.HIGH, 7.0, 9.0),
        (NutrientLevel.VERY_HIGH, 9.0, None),
    ],
    "uric_acid_female": [
        (NutrientLevel.NORMAL, None, 6.0),
        (NutrientLevel.HIGH, 6.0, 8.0),
        (NutrientLevel.VERY_HIGH, 8.0, None),
    ],
}

# Maps generic exam_type to gender-specific reference key
_GENDER_SPECIFIC: dict[str, dict[str, str]] = {
    "ferritin": {"M": "ferritin_male", "F": "ferritin_female"},
    "hemoglobin": {"M": "hemoglobin_male", "F": "hemoglobin_female"},
    "hdl_cholesterol": {"M": "hdl_cholesterol_male", "F": "hdl_cholesterol_female"},
    "uric_acid": {"M": "uric_acid_male", "F": "uric_acid_female"},
}

_NUTRITIONAL_GUIDANCE: dict[str, dict[NutrientLevel, dict]] = {
    "vitamin_d": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["sardines", "salmon", "tuna", "egg yolks", "fortified milk"],
            "foods_to_avoid": ["processed foods high in phosphate additives"],
            "supplements": ["Vitamin D3 4000–6000 IU/day — requires medical supervision"],
            "notes": "Critical deficiency. Sunlight exposure 15–20 min/day (arms and legs, no sunscreen). Urgent medical evaluation recommended.",
        },
        NutrientLevel.LOW: {
            "foods_to_increase": ["fatty fish", "eggs", "fortified dairy products"],
            "foods_to_avoid": [],
            "supplements": ["Vitamin D3 2000 IU/day"],
            "notes": "Supplementation and moderate sun exposure recommended. Reassess in 3 months.",
        },
        NutrientLevel.HIGH: {
            "foods_to_increase": [],
            "foods_to_avoid": ["excess fortified foods"],
            "supplements": ["Suspend supplementation"],
            "notes": "High vitamin D. Avoid additional supplementation. Monitor calcium levels.",
        },
        NutrientLevel.VERY_HIGH: {
            "foods_to_increase": [],
            "foods_to_avoid": ["all vitamin D-fortified foods", "fatty fish in excess"],
            "supplements": ["Discontinue all supplementation immediately"],
            "notes": "Toxicity risk. Hypercalcemia possible. Seek immediate medical evaluation.",
        },
    },
    "ferritin": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["red meat", "liver", "oysters", "dark leafy greens", "lentils", "pumpkin seeds"],
            "foods_to_avoid": ["tea/coffee with iron-rich meals", "calcium supplements alongside iron sources"],
            "supplements": ["Ferrous bisglycinate 25–50 mg/day — medical supervision required"],
            "notes": "Iron deficiency. Pair iron foods with vitamin C sources. Risk of anemia. Medical evaluation required.",
        },
        NutrientLevel.LOW: {
            "foods_to_increase": ["lean red meat", "spinach", "tofu", "fortified cereals", "legumes"],
            "foods_to_avoid": ["tea/coffee immediately before or after iron-rich meals"],
            "supplements": ["Ferrous bisglycinate 14–25 mg/day"],
            "notes": "Increase dietary iron with vitamin C. Monitor in 3 months.",
        },
        NutrientLevel.HIGH: {
            "foods_to_increase": ["plant-based foods", "antioxidant-rich foods"],
            "foods_to_avoid": ["red meat in excess", "iron-fortified cereals", "vitamin C with iron-rich meals"],
            "supplements": ["Avoid iron supplements"],
            "notes": "Elevated ferritin may indicate inflammation. Avoid iron supplementation.",
        },
        NutrientLevel.VERY_HIGH: {
            "foods_to_increase": [],
            "foods_to_avoid": ["all iron-rich foods", "alcohol", "red meat", "liver"],
            "supplements": ["Avoid all iron supplements"],
            "notes": "Very high ferritin. May indicate hemochromatosis or inflammatory process. Urgent medical evaluation.",
        },
    },
    "vitamin_b12": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["liver", "beef", "clams", "sardines", "eggs", "dairy"],
            "foods_to_avoid": ["excessive alcohol"],
            "supplements": ["Methylcobalamin 1000 mcg/day sublingual or IM injection — medical evaluation required"],
            "notes": "B12 deficiency may cause irreversible neurological damage. Urgent evaluation especially for vegans/vegetarians.",
        },
        NutrientLevel.LOW: {
            "foods_to_increase": ["meat", "fish", "eggs", "dairy", "fortified nutritional yeast"],
            "foods_to_avoid": ["excessive alcohol"],
            "supplements": ["Methylcobalamin 500 mcg/day"],
            "notes": "Monitor with repeat exam in 3 months. Vegetarians/vegans should supplement consistently.",
        },
    },
    "folic_acid": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["dark leafy greens", "lentils", "black beans", "avocado", "broccoli", "asparagus"],
            "foods_to_avoid": ["excessive alcohol", "processed foods"],
            "supplements": ["Folic acid 400–800 mcg/day (methylfolate preferred for MTHFR variants)"],
            "notes": "Critical in women of childbearing age. Associated with neural tube defects and cardiovascular risk.",
        },
        NutrientLevel.LOW: {
            "foods_to_increase": ["leafy greens", "legumes", "fortified cereals"],
            "foods_to_avoid": ["excessive alcohol"],
            "supplements": ["Methylfolate 400 mcg/day"],
            "notes": "Increase dietary folate. Consider MTHFR genetic testing.",
        },
    },
    "fasting_glucose": {
        NutrientLevel.LOW: {
            "foods_to_increase": ["complex carbohydrates", "protein-rich foods", "healthy fats"],
            "foods_to_avoid": ["long fasting periods", "alcohol on empty stomach"],
            "supplements": [],
            "notes": "Hypoglycemia. Eat regular small meals. Avoid prolonged fasting.",
        },
        NutrientLevel.HIGH: {
            "foods_to_increase": ["non-starchy vegetables", "legumes", "whole grains", "nuts", "seeds"],
            "foods_to_avoid": ["refined sugars", "white bread", "white rice", "sugary beverages", "processed snacks"],
            "supplements": ["Chromium picolinate 200 mcg/day", "Berberine 500 mg 3x/day — medical guidance"],
            "notes": "Pre-diabetic range. Low-glycemic Mediterranean diet. 150 min/week aerobic exercise.",
        },
        NutrientLevel.VERY_HIGH: {
            "foods_to_increase": ["non-starchy vegetables", "lean proteins", "healthy fats"],
            "foods_to_avoid": ["all simple sugars", "refined carbohydrates", "fruit juices", "alcohol"],
            "supplements": [],
            "notes": "Diabetic range (≥126 mg/dL). URGENT medical evaluation. Do not self-manage.",
        },
    },
    "hba1c": {
        NutrientLevel.HIGH: {
            "foods_to_increase": ["fiber-rich vegetables", "legumes", "whole oats", "berries"],
            "foods_to_avoid": ["refined carbohydrates", "sugary drinks", "ultra-processed foods"],
            "supplements": ["Berberine", "Magnesium glycinate", "Chromium"],
            "notes": "Pre-diabetes (5.7–6.4%). Lifestyle intervention can reverse progression.",
        },
        NutrientLevel.VERY_HIGH: {
            "foods_to_increase": ["low-glycemic vegetables", "lean proteins"],
            "foods_to_avoid": ["all high-glycemic foods"],
            "supplements": [],
            "notes": "Diabetic range (≥6.5%). Requires immediate medical management.",
        },
    },
    "ldl_cholesterol": {
        NutrientLevel.HIGH: {
            "foods_to_increase": ["oats", "flaxseed", "avocado", "olive oil", "walnuts", "legumes", "berries"],
            "foods_to_avoid": ["saturated fats", "trans fats", "processed red meats", "full-fat dairy excess"],
            "supplements": ["Omega-3 EPA+DHA 2–4 g/day", "Psyllium husk 10–20 g/day", "Red yeast rice — medical guidance"],
            "notes": "Adopt Mediterranean diet. Regular aerobic exercise reduces LDL 5–10%.",
        },
        NutrientLevel.VERY_HIGH: {
            "foods_to_increase": ["plant sterols/stanols", "soluble fiber foods"],
            "foods_to_avoid": ["all saturated and trans fats", "fried foods", "coconut oil in excess"],
            "supplements": ["Omega-3 EPA+DHA 4 g/day"],
            "notes": "High cardiovascular risk. Medical evaluation for statin therapy urgently needed.",
        },
    },
    "hdl_cholesterol": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["olive oil", "avocado", "fatty fish", "nuts", "purple/red berries"],
            "foods_to_avoid": ["trans fats", "refined carbohydrates", "sedentary habits"],
            "supplements": ["Omega-3 EPA+DHA 2 g/day", "Niacin — medical supervision only"],
            "notes": "Low HDL is a cardiovascular risk factor. Exercise raises HDL most effectively.",
        },
        NutrientLevel.LOW: {
            "foods_to_increase": ["olive oil", "fatty fish", "nuts", "legumes"],
            "foods_to_avoid": ["trans fats"],
            "supplements": ["Omega-3 EPA+DHA 1–2 g/day"],
            "notes": "Increase aerobic exercise frequency and intensity.",
        },
    },
    "triglycerides": {
        NutrientLevel.HIGH: {
            "foods_to_increase": ["fatty fish", "flaxseed", "chia seeds", "walnuts", "avocado"],
            "foods_to_avoid": ["alcohol", "refined carbohydrates", "sugary foods", "fruit juices", "honey"],
            "supplements": ["Omega-3 EPA+DHA 2–4 g/day"],
            "notes": "Reduce refined carbs and alcohol. These are the primary dietary drivers of elevated triglycerides.",
        },
        NutrientLevel.VERY_HIGH: {
            "foods_to_increase": ["lean proteins", "non-starchy vegetables", "omega-3 sources"],
            "foods_to_avoid": ["all alcohol", "all added sugars", "all refined carbohydrates", "fruit in excess"],
            "supplements": ["Omega-3 EPA+DHA 4 g/day — medical guidance required"],
            "notes": "Very high triglycerides (≥200 mg/dL). Risk of pancreatitis. Urgent medical attention.",
        },
    },
    "tsh": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["iodine-rich foods (seaweed, fish)", "selenium-rich foods (Brazil nuts)"],
            "foods_to_avoid": ["raw cruciferous vegetables in excess", "soy in excess"],
            "supplements": [],
            "notes": "Suppressed TSH (hyperthyroidism). Medical evaluation required. Avoid stimulants.",
        },
        NutrientLevel.HIGH: {
            "foods_to_increase": ["Brazil nuts (selenium)", "seafood (iodine)", "pumpkin seeds (zinc)"],
            "foods_to_avoid": ["raw kale/broccoli/cauliflower in excess", "soy products", "gluten (if Hashimoto's suspected)"],
            "supplements": ["Selenium 200 mcg/day", "Zinc 15 mg/day", "Vitamin D (if deficient)"],
            "notes": "Elevated TSH suggests hypothyroidism. Medical evaluation for levothyroxine therapy.",
        },
        NutrientLevel.VERY_HIGH: {
            "foods_to_increase": ["anti-inflammatory diet"],
            "foods_to_avoid": ["goitrogenic foods (raw)", "soy", "gluten if autoimmune"],
            "supplements": ["Selenium 200 mcg/day"],
            "notes": "Severe hypothyroidism. Urgent thyroid hormone replacement required.",
        },
    },
    "magnesium": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["pumpkin seeds", "dark chocolate (>70%)", "spinach", "almonds", "black beans", "avocado"],
            "foods_to_avoid": ["excessive alcohol", "high-sugar foods", "excessive caffeine"],
            "supplements": ["Magnesium glycinate or malate 300–400 mg/day"],
            "notes": "Magnesium is cofactor for 300+ enzymatic reactions. Deficiency linked to anxiety, cramps, and poor sleep.",
        },
        NutrientLevel.LOW: {
            "foods_to_increase": ["nuts", "seeds", "leafy greens", "legumes", "whole grains"],
            "foods_to_avoid": ["excessive alcohol"],
            "supplements": ["Magnesium glycinate 200 mg/day before bed"],
            "notes": "Prioritize dietary sources. Supplementation well-tolerated.",
        },
    },
    "zinc": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["oysters", "beef", "pumpkin seeds", "hemp seeds", "cashews", "lentils (soaked)"],
            "foods_to_avoid": ["raw legumes without soaking (phytates block absorption)", "excess calcium"],
            "supplements": ["Zinc picolinate or bisglycinate 15–30 mg/day with food"],
            "notes": "Zinc deficiency affects immunity, wound healing, taste, and reproductive health. Soak/sprout legumes to reduce phytates.",
        },
        NutrientLevel.LOW: {
            "foods_to_increase": ["meat", "pumpkin seeds", "shellfish", "cashews"],
            "foods_to_avoid": [],
            "supplements": ["Zinc picolinate 10–15 mg/day"],
            "notes": "Take zinc away from iron supplements to avoid competition.",
        },
    },
    "calcium": {
        NutrientLevel.DEFICIENT: {
            "foods_to_increase": ["dairy", "fortified plant milks", "canned sardines with bones", "kale", "broccoli", "tofu (calcium-set)"],
            "foods_to_avoid": ["excess sodium", "excess caffeine", "oxalate-rich foods with calcium sources"],
            "supplements": ["Calcium citrate 500 mg 2x/day (citrate preferred — better absorbed)"],
            "notes": "Ensure adequate Vitamin D for calcium absorption. High-dose calcium supplements linked to cardiovascular risk — prefer food sources.",
        },
        NutrientLevel.HIGH: {
            "foods_to_increase": ["water intake"],
            "foods_to_avoid": ["calcium supplements", "fortified foods", "excessive dairy"],
            "supplements": ["Discontinue calcium supplementation"],
            "notes": "Hypercalcemia. Rule out hyperparathyroidism or excess vitamin D. Medical evaluation required.",
        },
    },
    "uric_acid": {
        NutrientLevel.HIGH: {
            "foods_to_increase": ["water (2–3 L/day)", "cherries", "low-fat dairy", "vegetables", "coffee (moderate)"],
            "foods_to_avoid": ["organ meats", "red meat excess", "shellfish", "beer", "fructose-sweetened beverages", "spirits"],
            "supplements": ["Cherry extract", "Vitamin C 500 mg/day"],
            "notes": "Elevated uric acid. Risk of gout and kidney stones. Hydration is key.",
        },
        NutrientLevel.VERY_HIGH: {
            "foods_to_increase": ["water 3+ L/day", "alkalizing foods"],
            "foods_to_avoid": ["all high-purine foods", "all alcohol", "fructose"],
            "supplements": [],
            "notes": "Very high uric acid. High gout risk. Medical management with urate-lowering therapy may be required.",
        },
    },
}


class NutritionAnalysisService:
    """
    Pure domain service containing all business rules for interpreting
    laboratory exam results and generating nutritional recommendations.

    Zero external dependencies — only imports from domain layer.
    """

    def _resolve_reference_key(self, exam_type: str, gender: str) -> str:
        if exam_type in _GENDER_SPECIFIC:
            return _GENDER_SPECIFIC[exam_type][gender]
        return exam_type

    def classify_result(self, result: ExamResult, patient: Patient) -> NutrientLevel:
        key = self._resolve_reference_key(result.exam_type, patient.gender)
        thresholds = _REFERENCE_RANGES.get(key)
        if not thresholds:
            if result.reference_min is not None and result.value < result.reference_min:
                return NutrientLevel.LOW
            if result.reference_max is not None and result.value > result.reference_max:
                return NutrientLevel.HIGH
            return NutrientLevel.NORMAL

        for level, min_val, max_val in thresholds:
            if min_val is None and max_val is not None and result.value < max_val:
                return level
            if max_val is None and min_val is not None and result.value >= min_val:
                return level
            if (
                min_val is not None
                and max_val is not None
                and min_val <= result.value < max_val
            ):
                return level

        return NutrientLevel.NORMAL

    def _get_guidance(
        self, exam_type: str, level: NutrientLevel
    ) -> dict | None:
        base_type = exam_type
        for generic, _ in _GENDER_SPECIFIC.items():
            if exam_type.startswith(generic):
                base_type = generic
                break
        guidance_map = _NUTRITIONAL_GUIDANCE.get(base_type, {})
        return guidance_map.get(level)

    def build_recommendation(
        self, result: ExamResult, level: NutrientLevel
    ) -> DietaryRecommendation | None:
        if level == NutrientLevel.NORMAL:
            return None
        guidance = self._get_guidance(result.exam_type, level)
        if not guidance:
            return None
        return DietaryRecommendation(
            nutrient=result.exam_type,
            level=level,
            foods_to_increase=guidance.get("foods_to_increase", []),
            foods_to_avoid=guidance.get("foods_to_avoid", []),
            supplements=guidance.get("supplements", []),
            clinical_notes=guidance.get("notes", ""),
        )

    def analyze_exam(
        self, exam: LabExam, patient: Patient
    ) -> tuple[list[DietaryRecommendation], list[str]]:
        """
        Classifies all exam results and generates rule-based recommendations.

        Returns:
            - List of DietaryRecommendation for abnormal values
            - List of human-readable finding strings (used as AI context)
        """
        recommendations: list[DietaryRecommendation] = []
        findings: list[str] = []

        for result in exam.results:
            level = self.classify_result(result, patient)
            finding = (
                f"{result.exam_type}: {result.value} {result.unit} "
                f"[{level.value.upper()}]"
            )
            if result.reference_min or result.reference_max:
                finding += f" (ref: {result.reference_min}–{result.reference_max})"
            findings.append(finding)

            recommendation = self.build_recommendation(result, level)
            if recommendation:
                recommendations.append(recommendation)

        return recommendations, findings