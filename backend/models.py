from sqlalchemy import Column, Integer, String, DateTime, Text, LargeBinary, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Memory(Base):
    """Memory model for storing extracted memories and documents."""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(500))  # Comma-separated tags
    embedding = Column(LargeBinary, nullable=True)  # Serialized numpy array
    json_metadata = Column(Text, nullable=True)  # JSON metadata (full structured memory)
    source_document = Column(String(500), nullable=True)  # Original document name
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Relationship
    user = relationship("User", back_populates="memories")
    
    # New structured memory fields
    memory_type = Column(String(50), nullable=True, index=True)  # person, event, experience, etc.
    importance = Column(String(20), nullable=True, index=True)  # low, medium, high
    entities_people = Column(Text, nullable=True)  # JSON array of people
    entities_organizations = Column(Text, nullable=True)  # JSON array of organizations
    entities_locations = Column(Text, nullable=True)  # JSON array of locations
    entities_skills = Column(Text, nullable=True)  # JSON array of skills
    time_start = Column(String(100), nullable=True)  # Start time
    time_end = Column(String(100), nullable=True)  # End time
    source_documents = Column(Text, nullable=True)  # JSON array of source documents

    # Indexes for performance
    __table_args__ = (
        Index('idx_memory_created_at', 'created_at'),
        Index('idx_memory_source_document', 'source_document'),
    )


class Conversation(Base):
    """Conversation model for storing chat history."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Relationship
    user = relationship("User", back_populates="conversations")
