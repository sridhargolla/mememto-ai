from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import uuid


class Entities(BaseModel):
    """Extracted entities from memory."""
    people: List[str] = Field(default_factory=list, description="People mentioned in the memory")
    organizations: List[str] = Field(default_factory=list, description="Organizations mentioned")
    locations: List[str] = Field(default_factory=list, description="Locations mentioned")
    skills: List[str] = Field(default_factory=list, description="Skills or competencies mentioned")


class TimeInfo(BaseModel):
    """Time information for the memory."""
    start: Optional[str] = Field(None, description="Start time or date (ISO format or natural language)")
    end: Optional[str] = Field(None, description="End time or date (ISO format or natural language)")


class MemorySchema(BaseModel):
    """Structured memory schema for intelligent memory extraction."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the memory")
    type: str = Field(..., description="Type of memory: person, event, experience, project, education, skill, document, organization")
    title: str = Field(..., description="Brief title of the memory")
    summary: str = Field(..., description="Detailed summary of the memory content")
    entities: Entities = Field(default_factory=Entities, description="Extracted entities")
    time: TimeInfo = Field(default_factory=TimeInfo, description="Time information")
    importance: str = Field(default="medium", description="Importance level: low, medium, high")
    source_documents: List[str] = Field(default_factory=list, description="Source document names or IDs")
    
    # Phase 2 MVP Specific Fields
    organization: Optional[str] = Field(None, description="Organization name (for experience, project, education, etc.)")
    duration: Optional[str] = Field(None, description="Duration or date range")
    skills: Optional[List[str]] = Field(default_factory=list, description="List of skills associated")
    projects: Optional[List[str]] = Field(default_factory=list, description="List of projects associated")
    source: Optional[str] = Field(None, description="Source file name")
    
    @field_validator('type', mode='before')
    @classmethod
    def validate_type(cls, v):
        """Validate memory type."""
        valid_types = ['person', 'event', 'experience', 'project', 'education', 'skill', 'document', 'organization']
        if str(v).lower() not in valid_types:
            raise ValueError(f"Invalid memory type. Must be one of: {', '.join(valid_types)}")
        return str(v).lower()
    
    @field_validator('importance', mode='before')
    @classmethod
    def validate_importance(cls, v):
        """Validate importance level."""
        valid_levels = ['low', 'medium', 'high']
        if str(v).lower() not in valid_levels:
            return 'medium'  # Default to medium instead of raising, for LLM output tolerance
        return str(v).lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemorySchema':
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MemorySchema':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_metadata_json(self) -> str:
        """Convert to JSON for storage in metadata field (legacy compatibility)."""
        return self.json()

