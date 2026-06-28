from pydantic import BaseModel, Field, validator
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
    type: str = Field(..., description="Type of memory: person, event, experience, project, education, skill, document")
    title: str = Field(..., description="Brief title of the memory")
    summary: str = Field(..., description="Detailed summary of the memory content")
    entities: Entities = Field(default_factory=Entities, description="Extracted entities")
    time: TimeInfo = Field(default_factory=TimeInfo, description="Time information")
    importance: str = Field(default="medium", description="Importance level: low, medium, high")
    source_documents: List[str] = Field(default_factory=list, description="Source document names or IDs")
    
    @validator('type')
    def validate_type(cls, v):
        """Validate memory type."""
        valid_types = ['person', 'event', 'experience', 'project', 'education', 'skill', 'document']
        if v not in valid_types:
            raise ValueError(f"Invalid memory type. Must be one of: {', '.join(valid_types)}")
        return v
    
    @validator('importance')
    def validate_importance(cls, v):
        """Validate importance level."""
        valid_levels = ['low', 'medium', 'high']
        if v not in valid_levels:
            raise ValueError(f"Invalid importance level. Must be one of: {', '.join(valid_levels)}")
        return v
    
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
