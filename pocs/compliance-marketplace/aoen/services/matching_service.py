"""
AOEN FASE 1+4 — Service Layer que orquestra o core sem expor HTTP.

Conecta ORM → core puro → persistência de resultado + custo.
"""

from sqlalchemy.orm import Session

from config import get_settings, get_tenant_config, PLAN_LIMITS
from core.compliance_scorer import FreelancerProfile, ProjectRequirements
from core.matching_engine import run_matching
from core.cost_tracker import build_cost_event
from models import Freelancer, Match, MatchStatus, Project, ProjectStatus, UsageRecord


def _to_freelancer_profile(f: Freelancer) -> FreelancerProfile:
    return FreelancerProfile(
        domains=f.domains or [],
        certifications=f.certifications or [],
        regulations_experience=f.regulations_experience or {},
        hourly_rate=float(f.hourly_rate),
        rating=float(f.rating),
        portfolio_score=float(f.portfolio_score),
    )


def _to_project_requirements(p: Project) -> ProjectRequirements:
    return ProjectRequirements(
        required_domains=p.required_domains or [],
        required_certifications=p.required_certifications or [],
        budget_max=float(p.budget_max) if p.budget_max else None,
        estimated_hours=p.estimated_hours,
        urgency_level=p.urgency_level or 3,
    )


def run_project_matching(
    db: Session,
    project: Project,
    tenant_config_override: dict,
    plan: str,
) -> list[Match]:
    cfg = get_tenant_config(tenant_config_override)
    settings = get_settings()

    plan_cfg = PLAN_LIMITS.get(plan, PLAN_LIMITS["starter"])
    top_n = min(cfg["max_matches_per_project"], plan_cfg["max_matches_per_project"])

    freelancers_db = (
        db.query(Freelancer)
        .filter(
            Freelancer.tenant_id == project.tenant_id,
            Freelancer.is_active == True,
            Freelancer.rating >= cfg["min_freelancer_rating"],
        )
        .all()
    )

    if cfg["allowed_domains"]:
        freelancers_db = [
            f for f in freelancers_db
            if set(f.domains or []) & set(cfg["allowed_domains"])
        ]

    if cfg["require_certification"] and project.required_certifications:
        freelancers_db = [
            f for f in freelancers_db
            if set(f.certifications or []) & set(project.required_certifications)
        ]

    candidates = run_matching(
        project=_to_project_requirements(project),
        freelancers=[(f.id, _to_freelancer_profile(f)) for f in freelancers_db],
        weights=cfg["match_weights"],
        top_n=top_n,
    )

    # Persiste matches
    existing_ids = {m.freelancer_id for m in db.query(Match).filter(Match.project_id == project.id).all()}
    new_matches: list[Match] = []

    for candidate in candidates:
        if candidate.freelancer_id in existing_ids:
            continue
        match = Match(
            project_id=project.id,
            freelancer_id=candidate.freelancer_id,
            score=candidate.score,
            score_breakdown={
                "domain_overlap": candidate.breakdown.domain_overlap,
                "certification_match": candidate.breakdown.certification_match,
                "experience_years": candidate.breakdown.experience_years,
                "rating": candidate.breakdown.rating,
                "rate_fit": candidate.breakdown.rate_fit,
                "details": candidate.breakdown.details,
            },
            status=MatchStatus.PENDING,
        )
        db.add(match)
        new_matches.append(match)

    # Registra custo (AOEN fase 4)
    rate_map = {
        "match_run": settings.cost_match_run,
        "project_open": settings.cost_project_open,
        "per_hire": settings.cost_per_hire,
    }
    event = build_cost_event(
        tenant_id=project.tenant_id,
        operation="match_run",
        units=len(freelancers_db),
        rate_map=rate_map,
        metadata={"project_id": project.id, "candidates_evaluated": len(freelancers_db)},
    )
    usage = UsageRecord(
        tenant_id=event.tenant_id,
        operation=event.operation,
        units=event.units,
        cost_credits=event.cost_credits,
        metadata=event.metadata,
        recorded_at=event.recorded_at,
    )
    db.add(usage)

    project.status = ProjectStatus.MATCHING
    db.commit()

    for m in new_matches:
        db.refresh(m)

    return new_matches