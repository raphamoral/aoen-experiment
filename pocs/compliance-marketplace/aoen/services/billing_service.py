from sqlalchemy.orm import Session
from sqlalchemy import func

from models import UsageRecord


def get_tenant_usage_summary(db: Session, tenant_id: str) -> dict:
    rows = (
        db.query(
            UsageRecord.operation,
            func.sum(UsageRecord.units).label("total_units"),
            func.sum(UsageRecord.cost_credits).label("total_credits"),
        )
        .filter(UsageRecord.tenant_id == tenant_id)
        .group_by(UsageRecord.operation)
        .all()
    )
    return {
        row.operation: {
            "total_units": int(row.total_units),
            "total_credits": float(row.total_credits),
        }
        for row in rows
    }


def get_tenant_credit_balance(db: Session, tenant_id: str) -> float:
    total = (
        db.query(func.sum(UsageRecord.cost_credits))
        .filter(UsageRecord.tenant_id == tenant_id)
        .scalar()
    )
    return float(total or 0.0)