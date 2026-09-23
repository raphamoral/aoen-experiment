from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Course

router = APIRouter(prefix="/courses", tags=["courses"])


class CourseCreateRequest(BaseModel):
    tenant_id: str
    title: str
    description: str | None = None
    workload_hours: int = 0


class CourseResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: str | None
    workload_hours: int
    is_active: bool

    model_config = {"from_attributes": True}


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(body: CourseCreateRequest, db: Session = Depends(get_db)):
    course = Course(**body.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/", response_model=list[CourseResponse])
def list_courses(tenant_id: str, db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.tenant_id == tenant_id).all()


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_course(course_id: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")
    course.is_active = False
    db.commit()