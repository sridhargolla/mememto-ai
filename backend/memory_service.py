import json

from embedding_service import EmbeddingService
from language_service import detect_language
from memory_schema import MemorySchema
from sqlalchemy.orm import Session

from models import Conversation, Memory


class MemoryService:
    """Service layer for memory operations."""

    @staticmethod
    def create_memory(
        db: Session,
        title: str,
        content: str,
        tags: str | None = None,
        metadata: str | None = None,
        source_document: str | None = None,
        user_id: int | None = None,
        type: str | None = None,
    ) -> Memory:
        """Create a new memory with optional embedding."""
        embedding_service = EmbeddingService()
        embedding = None

        # Detect language from content
        detected_language = detect_language(content)

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
            type=type,
            embedding=embedding,
            metadata_json=metadata,
            source_file=source_document,
            language=detected_language,
            user_id=user_id,
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def get_memory(db: Session, memory_id: int) -> Memory | None:
        """Get a memory by ID."""
        return db.query(Memory).filter(Memory.id == memory_id).first()

    @staticmethod
    def get_all_memories(
        db: Session, skip: int = 0, limit: int = 100, user_id: int | None = None
    ) -> list[Memory]:
        """Get all memories with pagination."""
        query = db.query(Memory)
        if user_id:
            query = query.filter(Memory.user_id == user_id)
        return query.order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_memories_by_tag(
        db: Session,
        tag: str,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
    ) -> list[Memory]:
        """Get memories by tag."""
        query = db.query(Memory).filter(Memory.tags.like(f"%{tag}%"))
        if user_id:
            query = query.filter(Memory.user_id == user_id)
        return query.order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_memory(
        db: Session,
        memory_id: int,
        title: str | None = None,
        content: str | None = None,
        tags: str | None = None,
        metadata: str | None = None,
        source_document: str | None = None,
    ) -> Memory | None:
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
    def create_structured_memory(
        db: Session, memory_schema: MemorySchema, user_id: int | None = None
    ) -> Memory:
        """
        Create a new memory from a structured MemorySchema.

        Args:
            db: Database session
            memory_schema: MemorySchema object with structured data
            user_id: Optional user ID to associate with the memory

        Returns:
            Created Memory object
        """
        embedding_service = EmbeddingService()
        embedding = None

        # Detect language from summary
        detected_language = detect_language(memory_schema.summary)

        # Generate embedding if model is available
        if embedding_service.is_loaded():
            text_to_embed = f"{memory_schema.title}. {memory_schema.summary}"
            embedding_array = embedding_service.generate_embedding(text_to_embed)
            if embedding_array is not None:
                embedding = embedding_service.serialize_embedding(embedding_array)

        # Merge skills list into entities if present in the schema
        skills_json = None
        if memory_schema.skills:
            skills_json = json.dumps(list(set(memory_schema.skills)))
        elif memory_schema.entities.skills:
            skills_json = json.dumps(memory_schema.entities.skills)

        # Get source document name
        source_doc = memory_schema.source
        if not source_doc and memory_schema.source_documents:
            source_doc = memory_schema.source_documents[0]

        memory = Memory(
            title=memory_schema.title,
            content=memory_schema.summary,
            type=memory_schema.type,
            embedding=embedding,
            metadata_json=memory_schema.to_metadata_json(),
            source_file=source_doc,
            language=detected_language,
            user_id=user_id,
            importance=memory_schema.importance,
            entities_people=(
                json.dumps(memory_schema.entities.people) if memory_schema.entities.people else None
            ),
            entities_organizations=(
                json.dumps(memory_schema.entities.organizations)
                if memory_schema.entities.organizations
                else None
            ),
            entities_locations=(
                json.dumps(memory_schema.entities.locations)
                if memory_schema.entities.locations
                else None
            ),
            entities_skills=skills_json,
            time_start=memory_schema.time.start or memory_schema.duration,
            time_end=memory_schema.time.end,
            source_documents=(
                json.dumps(memory_schema.source_documents)
                if memory_schema.source_documents
                else None
            ),
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def get_memories_by_type(
        db: Session, memory_type: str, skip: int = 0, limit: int = 100
    ) -> list[Memory]:
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
        return (
            db.query(Memory)
            .filter(Memory.memory_type == memory_type)
            .order_by(Memory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_memories_by_importance(
        db: Session, importance: str, skip: int = 0, limit: int = 100
    ) -> list[Memory]:
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
        return (
            db.query(Memory)
            .filter(Memory.importance == importance)
            .order_by(Memory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_memories_by_entity(
        db: Session,
        entity_type: str,
        entity_value: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Memory]:
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
            "people": Memory.entities_people,
            "organizations": Memory.entities_organizations,
            "locations": Memory.entities_locations,
            "skills": Memory.entities_skills,
        }

        column = column_map.get(entity_type)
        if not column:
            return []

        return (
            db.query(Memory)
            .filter(column.like(f"%{entity_value}%"))
            .order_by(Memory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class ConversationService:
    """Service layer for conversation operations."""

    @staticmethod
    def create_conversation(
        db: Session,
        question: str,
        answer: str,
        user_id: int | None = None,
        session_id: str | None = None,
        title: str | None = None,
        is_pinned: int = 0,
    ) -> Conversation:
        """Create a new conversation, auto-generating a title if it's the first message of a session."""
        import re
        import uuid

        if not session_id:
            session_id = str(uuid.uuid4())

        if not title:
            # Check if there is an existing conversation in this session to copy the title
            existing = db.query(Conversation).filter(Conversation.session_id == session_id).first()
            if existing:
                title = existing.title
            else:
                # Auto-generate title from the first question
                clean_q = question.strip()
                # Strip common formatting characters
                clean_q = re.sub(r"[#*`_\-\n\r\t]", " ", clean_q).strip()
                # Extract first 40 characters
                title = clean_q[:40] + ("..." if len(clean_q) > 40 else "")
                if not title:
                    title = "New Chat"

        conversation = Conversation(
            question=question,
            answer=answer,
            user_id=user_id,
            session_id=session_id,
            title=title,
            is_pinned=is_pinned,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(db: Session, conversation_id: int) -> Conversation | None:
        """Get a conversation by ID."""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    @staticmethod
    def get_all_conversations(
        db: Session, skip: int = 0, limit: int = 100, user_id: int | None = None
    ) -> list[Conversation]:
        """Get all conversations with pagination."""
        query = db.query(Conversation)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        return query.order_by(Conversation.timestamp.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int) -> bool:
        """Delete a conversation."""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False
