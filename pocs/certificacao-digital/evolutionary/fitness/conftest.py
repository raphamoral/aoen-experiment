import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Deve preceder qualquer import de src/ para que os getenv usem o valor de teste
os.environ.setdefault("API_KEY", "test-api-key")
os.environ.setdefault("CERT_SECRET_KEY", "test-secret-key")

from main import app  # noqa: E402
from src.infrastructure.database import Base, get_db  # noqa: E402

_TEST_DB_URL = "sqlite:///./test_fitness.db"
_engine = create_engine(_TEST_DB_URL, connect_args={"check_same_thread": False})
_TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)
    if os.path.exists("./test_fitness.db"):
        os.remove("./test_fitness.db")


@pytest.fixture(scope="session")
def client():
    def _override_db():
        db = _TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def api_headers():
    return {"x-api-key": "test-api-key"}


@pytest.fixture(scope="session")
def sample_course(client, api_headers):
    resp = client.post(
        "/courses/",
        json={
            "name": "Python Avançado",
            "instructor": "Ada Lovelace",
            "description": "Curso completo de Python para ciência de dados",
            "duration_hours": 40,
        },
        headers=api_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture(scope="session")
def sample_certificate(client, api_headers, sample_course):
    resp = client.post(
        "/certificates/",
        json={
            "course_id": sample_course["id"],
            "recipient_name": "João Silva",
            "recipient_email": "joao@example.com",
        },
        headers=api_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()