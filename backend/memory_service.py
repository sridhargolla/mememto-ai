from sqlalchemy.orm import Session
from models import Memory, Conversation
from typing import List, Optional
from embedding_service import EmbeddingService
from memory_schema import MemorySchema
import json


class MemoryService:
    """Service layer for memory operations."""
    
    @staticmethod
    def create_memory(db: Session, title: str, content: str, tags: Optional[str] = None, 
                     metadata: Optional[str] = None, source_document: Optional[str] = None, user_id: Optional[int] = None) -> Memory:
        """Create a new memory with optional embedding."""
        embedding_service = EmbeddingService()
        embedding = None
        
        # Generate embedding if model is available
        if embedding_service.is_loaded():
            text_to_embed = f"{title}. {content}"
            embedding_array = embedding_service.generate_embedding(text_to_embed)
            if embedding_array is not None:
                embedding = embedding_service.serialize_embedding(embedding_array)
        
        memory = Memory(
            title=title,
            content=content,
            tags=tags,
            embedding=embedding,
            json_metadata=metadata,
            source_document=source_document,
            user_id=user_id
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def get_memory(db: Session, memory_id: int) -> Optional[Memory]:
        """Get a memory by ID."""
        return db.query(Memory).filter(Memory.id == memory_id).first()

    @staticmethod
    def get_all_memories(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Memory]:
        """Get all memories with pagination."""
        query = db.query(Memory)
        if user_id:
            query = query.filter(Memory.user_id == user_id)
        return query.order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_memories_by_tag(db: Session, tag: str, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Memory]:
        """Get memories by tag."""
        query = db.query(Memory).filter(Memory.tags.like(f"%{tag}%"))
        if user_id:
            query = query.filter(Memory.user_id == user_id)
        return query.order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_memory(db: Session, memory_id: int, title: Optional[str] = None, content: Optional[str] = None, 
                     tags: Optional[str] = None, metadata: Optional[str] = None, source_document: Optional[str] = None) -> Optional[Memory]:
        """Update a memory and regenerate embedding if content changes."""
        memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if memory:
            if title is not None:
                memory.title = title
            if content is not None:
                memory.content = content
            if tags is not None:
                memory.tags = tags
            if metadata is not None:
                memory.json_metadata = metadata
            if source_document is not None:
                memory.source_document = source_document
            
            # Regenerate embedding if title or content changed
            if title is not None or content is not None:
                embedding_service = EmbeddingService()
                if embedding_service.is_loaded():
                    text_to_embed = f"{memory.title}. {memory.content}"
                    embedding_array = embedding_service.generate_embedding(text_to_embed)
                    if embedding_array is not None:
                        memory.embedding = embedding_service.serialize_embedding(embedding_array)
            
            db.commit()
            db.refresh(memory)
        return memory

    @staticmethod
    def delete_memory(db: Session, memory_id: int) -> bool:
        """Delete a memory."""
        memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if memory:
            db.delete(memory)
            db.commit()
            return True
        return False

    @staticmethod
    def create_structured_memory(db: Session, memory_schema: MemorySchema) -> Memory:
        """
        Create a new memory from a structured MemorySchema.
        
        Args:
            db: Database session
            memory_schema: MemorySchema object with structured data
        
        Returns:
            Created Memory object
        """
        embedding_service = EmbeddingService()
        embedding = None
        
        # Generate embedding if model is available
        if embedding_service.is_loaded():
            text_to_embed = f"{memory_schema.title}. {memory_schema.summary}"
            embedding_array = embedding_service.generate_embedding(text_to_embed)
            if embedding_array is not None:
                embedding = embedding_service.serialize_embedding(embedding_array)
        
        memory = Memory(
            title=memory_schema.title,
            content=memory_schema.summary,
            tags=memory_schema.type,
            embedding=embedding,
            metadata=memory_schema.to_metadata_json(),
            source_document=memory_schema.source_documents[0] if memory_schema.source_documents else None,
            memory_type=memory_schema.type,
            importance=memory_schema.importance,
            entities_people=json.dumps(memory_schema.entities.people) if memory_schema.entities.people else None,
            entities_organizations=json.dumps(memory_schema.entities.organizations) if memory_schema.entities.organizations else None,
            entities_locations=json.dumps(memory_schema.entities.locations) if memory_schema.entities.locations else None,
            entities_skills=json.dumps(memory_schema.entities.skills) if memory_schema.entities.skills else None,
            time_start=memory_schema.time.start,
            time_end=memory_schema.time.end,
            source_documents=json.dumps(memory_schema.source_documents) if memory_schema.source_documents else None
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def get_memories_by_type(db: Session, memory_type: str, skip: int = 0, limit: int = 100) -> List[Memory]:
        """
        Get memories by type.
        
        Args:
            db: Database session
            memory_type: Type of memory (person, event, experience, etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Memory objects
        """
        return db.query(Memory).filter(
            Memory.memory_type == memory_type
        ).order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_memories_by_importance(db: Session, importance: str, skip: int = 0, limit: int = 100) -> List[Memory]:
        """
        Get memories by importance level.
        
        Args:
            db: Database session
            importance: Importance level (low, medium, high)
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Memory objects
        """
        return db.query(Memory).filter(
            Memory.importance == importance
        ).order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_memories_by_entity(db: Session, entity_type: str, entity_value: str, skip: int = 0, limit: int = 100) -> List[Memory]:
        """
        Get memories containing a specific entity.
        
        Args:
            db: Database session
            entity_type: Type of entity (people, organizations, locations, skills)
            entity_value: Value to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Memory objects
        """
        column_map = {
            'people': Memory.entities_people,
            'organizations': Memory.entities_organizations,
            'locations': Memory.entities_locations,
            'skills': Memory.entities_skills
        }
        
        column = column_map.get(entity_type)
        if not column:
            return []
        
        return db.query(Memory).filter(
            column.like(f"%{entity_value}%")
        ).order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()


class ConversationService:
    """Service layer for conversation operations."""
    
    @staticmethod
    def create_conversation(db: Session, question: str, answer: str) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            question=question,
            answer=answer
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(db: Session, conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    @staticmethod
    def get_all_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """Get all conversations with pagination."""
        return db.query(Conversation).order_by(Conversation.timestamp.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int) -> bool:
        """Delete a conversation."""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False
