from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Database file path
DATABASE_PATH = os.getenv("DATABASE_PATH", "./memento.db")

# Create SQLite engine
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)

# Create session factory
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
