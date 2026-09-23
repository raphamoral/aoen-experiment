import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Job, Proposal, User
from app.schemas import JobCreate, JobOut, ProposalCreate, ProposalOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobOut])
def list_jobs(
    regulation: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if regulation:
        query = query.filter(Job.regulation.ilike(f"%{regulation}%"))
    if status:
        query = query.filter(Job.status == status)
    return query.order_by(Job.created_at.desc()).all()


@router.post("/", response_model=JobOut, status_code=201)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can post jobs")
    job = Job(**payload.model_dump(), client_id=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/proposals", response_model=ProposalOut, status_code=201)
def submit_proposal(
    job_id: uuid.UUID,
    payload: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "freelancer":
        raise HTTPException(status_code=403, detail="Only freelancers can submit proposals")

    job = db.get(Job, job_id)
    if not job or job.status != "open":
        raise HTTPException(status_code=404, detail="Job not found or not open")

    existing = (
        db.query(Proposal)
        .filter(Proposal.job_id == job_id, Proposal.freelancer_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Proposal already submitted")

    proposal = Proposal(
        **payload.model_dump(),
        job_id=job_id,
        freelancer_id=current_user.id,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.get("/{job_id}/proposals", response_model=list[ProposalOut])
def list_proposals(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your job")
    return db.query(Proposal).filter(Proposal.job_id == job_id).all()