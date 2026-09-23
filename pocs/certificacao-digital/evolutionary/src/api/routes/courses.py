import os
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.domain.models import Course
from src.domain.schemas import CourseCreate, CourseResponse
from src.infrastructure.database import get_db

router = APIRouter()

_DEFAULT_API_KEY = "dev-api-key-change-in-production"


def _require_api_key(x_api_key: str = Header(...)):
    valid = os.getenv("API_KEY", _DEFAULT_API_KEY)
    if x_api_key != valid:
        raise HTTPException(status_code=401, detail="API key inválida")


@router.post("/", response_model=CourseResponse, status_code=201, dependencies=[Depends(_require_api_key)])
def create_course(data: CourseCreate, db: Session = Depends(get_db)):
    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/", response_model=List[CourseResponse])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.active.is_(True)).all()


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return course