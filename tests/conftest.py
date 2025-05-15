from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from main import app  
from database import Base, get_db  

# Use SQLite in-memory database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database schema
Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inject override
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        for tbl in reversed(Base.metadata.sorted_tables):
            db.execute(tbl.delete())
        db.commit()
        db.close()

# Fixture for FastAPI test client
@pytest.fixture()
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c