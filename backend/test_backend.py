import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test database path before imports
os.environ["DATABASE_PATH"] = "./test_memento.db"

import contextlib

from database import Base, get_db
from document_ingestion import DocumentExtractor
from main import app
from memory_schema import MemorySchema
from models import Memory, User
from retrieval import MemoryRetriever

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_memento.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables and delete file
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_memento.db"):
        with contextlib.suppress(BaseException):
            os.remove("./test_memento.db")


def test_health_endpoint():
    """Verify that the health check endpoint enforces CPU-only offline status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["ai_runtime"] == "llama.cpp"
    assert data["device"] == "CPU"
    assert data["offline"] is True


def test_text_normalization():
    """Verify text normalization removes extra spaces and cleans control characters."""
    dirty_text = "Hello \t World!\r\n\r\nThis is   a \x00test.\n\n\n\nNew Paragraph."
    clean_text = DocumentExtractor.normalize_text(dirty_text)
    assert clean_text == "Hello World!\n\nThis is a test.\n\nNew Paragraph."


def test_json_validation_valid():
    """Verify that a valid dictionary parses into a MemorySchema."""
    valid_data = {
        "type": "experience",
        "title": "Machine Learning Internship",
        "summary": "Built a local classifier.",
        "entities": {
            "people": ["Alice"],
            "organizations": ["ABC Corp"],
            "locations": ["Hyderabad"],
            "skills": ["Python", "PyTorch"],
        },
        "time": {"start": "2025", "end": None},
        "importance": "high",
        "source_documents": ["resume.pdf"],
        "organization": "ABC Corp",
        "duration": "2025",
        "skills": ["Python", "PyTorch"],
        "projects": ["Classifier"],
        "source": "resume.pdf",
    }
    schema = MemorySchema(**valid_data)
    assert schema.type == "experience"
    assert schema.organization == "ABC Corp"
    assert "Python" in schema.skills


def test_json_validation_invalid():
    """Verify that invalid memory types or importance levels throw validation errors."""
    invalid_data = {"type": "invalid_type_here", "title": "Test Title", "summary": "Test Summary"}
    with pytest.raises(ValueError):
        MemorySchema(**invalid_data)


def test_database_crud():
    """Verify database CRUD operations for memories."""
    db = TestingSessionLocal()

    # Create a test user
    user = User(name="Test User", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create a memory
    memory = Memory(
        type="project",
        title="AI Attendance System",
        content="An OpenCV based face recognition attendance system.",
        source_file="attendance_report.pdf",
        language="en",
        user_id=user.id,
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)

    # Read memory
    db_memory = db.query(Memory).filter(Memory.id == memory.id).first()
    assert db_memory is not None
    assert db_memory.title == "AI Attendance System"
    assert db_memory.source_document == "attendance_report.pdf"  # tests backward compatibility property

    # Update memory
    db_memory.title = "Updated Attendance System"
    db.commit()

    db_memory_updated = db.query(Memory).filter(Memory.id == memory.id).first()
    assert db_memory_updated.title == "Updated Attendance System"

    # Delete memory
    db.delete(db_memory_updated)
    db.commit()

    deleted = db.query(Memory).filter(Memory.id == memory.id).first()
    assert deleted is None
    db.close()


def test_hybrid_retrieval_logic():
    """Verify that keyword extraction and relevance calculations work as expected."""
    db = TestingSessionLocal()

    # Create test memories
    m1 = Memory(
        type="skill",
        title="Python Programming",
        content="Deep expertise in Python scripting and FastAPI development.",
        user_id=1,
    )
    m2 = Memory(
        type="project",
        title="Visual Attendance",
        content="Face detection project using OpenCV and computer vision.",
        user_id=1,
    )

    db.add(m1)
    db.add(m2)
    db.commit()

    # Test keyword extraction
    keywords = MemoryRetriever.extract_keywords("How to build an attendance system in Python?")
    assert "attendance" in keywords
    assert "python" in keywords
    assert "system" in keywords
    assert "build" in keywords
    assert "how" not in keywords  # stop word

    # Test keyword relevance calculation
    score_m1 = MemoryRetriever.calculate_relevance(m1, keywords)
    score_m2 = MemoryRetriever.calculate_relevance(m2, keywords)

    # m1 has "Python" (1 match)
    # m2 has "attendance" (1 match)
    assert score_m1 > 0
    assert score_m2 > 0

    db.close()
