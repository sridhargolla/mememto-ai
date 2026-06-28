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
    """Initialize the database, create tables, and handle schema migrations."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Run lightweight column migrations if tables already exist
    from sqlalchemy import text
    with engine.connect() as conn:
        # Check existing columns in memories table
        result = conn.execute(text("PRAGMA table_info(memories)"))
        columns = [row[1] for row in result.fetchall()]
        
        # Add columns if they don't exist
        if "type" not in columns:
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN type VARCHAR(50)"))
                print("Migration: Added 'type' column to memories table")
            except Exception as e:
                print(f"Migration warning (type): {e}")
                
        if "metadata" not in columns:
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN metadata TEXT"))
                print("Migration: Added 'metadata' column to memories table")
            except Exception as e:
                print(f"Migration warning (metadata): {e}")
                
        if "source_file" not in columns:
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN source_file VARCHAR(500)"))
                print("Migration: Added 'source_file' column to memories table")
            except Exception as e:
                print(f"Migration warning (source_file): {e}")
                
        if "language" not in columns:
            try:
                conn.execute(text("ALTER TABLE memories ADD COLUMN language VARCHAR(50)"))
                print("Migration: Added 'language' column to memories table")
            except Exception as e:
                print(f"Migration warning (language): {e}")
        
        # Check if performance_metrics table exists
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='performance_metrics'"))
        perf_table_exists = result.fetchone() is not None
        
        if not perf_table_exists:
            print("Migration: Creating performance_metrics table")
            # Base.metadata.create_all will handle this, but we log it
        else:
            print("Migration: performance_metrics table already exists")
        
        # Commit changes (SQLAlchemy engine connection handles this, but commit is good practice)
        conn.commit()



def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
