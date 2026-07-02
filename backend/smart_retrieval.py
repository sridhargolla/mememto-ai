"""
Smart Retrieval Module
Enhanced memory retrieval with advanced ranking, context awareness, and document prioritization.
"""

import re
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from embedding_service import EmbeddingService
from models import Memory
from retrieval import MemoryRetriever


class SmartRetriever:
    """
    Advanced retrieval system with intelligent ranking and context awareness.
    Prioritizes uploaded documents and uses multi-factor scoring.
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.base_retriever = MemoryRetriever()
        self.embedding_service = EmbeddingService()

    def retrieve_with_ranking(
        self,
        query: str,
        top_k: int = 5,
        intent: str = "general",
        conversation_context: list[dict] | None = None,
    ) -> list[dict]:
        """
        Retrieve memories with advanced multi-factor ranking.

        Args:
            query: User query
            top_k: Number of results to return
            intent: Detected user intent
            conversation_context: Recent conversation history

        Returns:
            List of ranked memory dictionaries with metadata
        """
        # Get base hybrid results
        base_results = self.base_retriever.retrieve_hybrid(self.db, query, top_k=top_k * 2, user_id=self.user_id)

        if not base_results:
            return []

        # Enhance with additional ranking factors
        ranked_results = []
        for memory, base_score in base_results:
            enhanced_score = self._calculate_enhanced_score(memory, base_score, query, intent, conversation_context)

            ranked_results.append(
                {
                    "memory": memory,
                    "base_score": base_score,
                    "enhanced_score": enhanced_score,
                    "source_file": memory.source_file,
                    "title": memory.title,
                    "content": memory.content,
                    "tags": memory.tags,
                    "created_at": memory.created_at,
                    "metadata": self._parse_metadata(memory.metadata_json),
                }
            )

        # Sort by enhanced score
        ranked_results.sort(key=lambda x: x["enhanced_score"], reverse=True)

        return ranked_results[:top_k]

    def _calculate_enhanced_score(
        self,
        memory: Memory,
        base_score: float,
        query: str,
        intent: str,
        conversation_context: list[dict] | None,
    ) -> float:
        """
        Calculate enhanced score using multiple factors.
        """
        score = base_score

        # Factor 1: Document priority boost (uploaded documents get priority)
        if memory.source_file and "upload" in (memory.tags or ""):
            score *= 1.3  # 30% boost for uploaded documents

        # Factor 2: Recency boost (recent memories slightly preferred)
        memory_age = datetime.now() - memory.created_at
        if memory_age < timedelta(days=30):
            score *= 1.1  # 10% boost for recent memories
        elif memory_age < timedelta(days=90):
            score *= 1.05  # 5% boost for moderately recent

        # Factor 3: Intent-specific weighting
        if intent == "document_query":
            # Prioritize document memories for document queries
            if memory.source_file:
                score *= 1.4
        elif intent == "memory_query":
            # Prioritize personal memories for memory queries
            if not memory.source_file:
                score *= 1.2
        elif intent == "coding":
            # Prioritize code-related memories
            if memory.tags and any(tag in memory.tags for tag in ["code", "programming", "algorithm"]):
                score *= 1.3

        # Factor 4: Conversation context relevance
        if conversation_context:
            context_boost = self._calculate_context_relevance(memory, conversation_context)
            score *= 1.0 + context_boost * 0.2  # Up to 20% boost

        # Factor 5: Query term density in memory
        density_score = self._calculate_term_density(query, memory)
        score *= 1.0 + density_score * 0.15  # Up to 15% boost

        # Factor 6: Memory quality indicators
        quality_boost = self._assess_memory_quality(memory)
        score *= quality_boost

        return min(score, 1.0)  # Cap at 1.0

    def _calculate_context_relevance(self, memory: Memory, context: list[dict]) -> float:
        """
        Calculate how relevant a memory is to the conversation context.
        """
        if not context:
            return 0.0

        relevance = 0.0
        memory_text = (memory.title + " " + memory.content).lower()

        # Check if memory relates to recent topics
        for conv in context[-3:]:  # Last 3 exchanges
            conv_text = (conv.get("question", "") + " " + conv.get("answer", "")).lower()

            # Simple overlap check
            memory_words = set(memory_text.split())
            conv_words = set(conv_text.split())

            if memory_words & conv_words:  # Intersection
                overlap = len(memory_words & conv_words) / len(memory_words | conv_words)
                relevance = max(relevance, overlap)

        return relevance

    def _calculate_term_density(self, query: str, memory: Memory) -> float:
        """
        Calculate how densely query terms appear in the memory.
        """
        query_terms = set(re.findall(r"\b\w+\b", query.lower()))
        memory_text = (memory.title + " " + memory.content).lower()

        if not query_terms:
            return 0.0

        matches = sum(1 for term in query_terms if term in memory_text)
        density = matches / len(query_terms)

        return density

    def _assess_memory_quality(self, memory: Memory) -> float:
        """
        Assess the quality of a memory based on various indicators.
        """
        quality = 1.0

        # Boost for memories with tags (indicates structured data)
        if memory.tags:
            quality *= 1.05

        # Boost for memories with sufficient content
        if len(memory.content) > 100:
            quality *= 1.05

        # Boost for memories with clear titles
        if memory.title and len(memory.title) > 5:
            quality *= 1.03

        # Reduce for very short or empty content
        if len(memory.content) < 20:
            quality *= 0.8

        return quality

    def _parse_metadata(self, metadata_json: str | None) -> dict:
        """Parse metadata JSON if available."""
        if not metadata_json:
            return {}

        try:
            import json

            return json.loads(metadata_json)
        except:
            return {}

    def get_document_summary(self) -> dict:
        """
        Get a summary of all uploaded documents for the user.
        """
        memories = self.db.query(Memory).filter(Memory.user_id == self.user_id, Memory.source_file.isnot(None)).all()

        if not memories:
            return {"total": 0, "documents": []}

        documents = {}
        for memory in memories:
            if memory.source_file not in documents:
                documents[memory.source_file] = {
                    "name": memory.source_file,
                    "memory_count": 0,
                    "tags": set(),
                    "created_at": memory.created_at,
                }
            documents[memory.source_file]["memory_count"] += 1
            if memory.tags:
                documents[memory.source_file]["tags"].update(memory.tags.split(","))

        # Convert sets to lists for JSON serialization
        for doc in documents.values():
            doc["tags"] = list(doc["tags"])

        return {"total": len(documents), "documents": list(documents.values())}

    def search_by_document(self, query: str, document_name: str, top_k: int = 5) -> list[dict]:
        """
        Search within a specific document.
        """
        memories = (
            self.db.query(Memory).filter(Memory.user_id == self.user_id, Memory.source_file == document_name).all()
        )

        if not memories:
            return []

        # Score memories based on query relevance
        scored = []
        for memory in memories:
            score = self._calculate_enhanced_score(memory, 0.5, query, "document_query", None)
            scored.append(
                {
                    "memory": memory,
                    "score": score,
                    "source_file": memory.source_file,
                    "title": memory.title,
                    "content": memory.content,
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def get_related_memories(self, memory_id: int, top_k: int = 3) -> list[dict]:
        """
        Find memories related to a specific memory.
        """
        target_memory = self.db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == self.user_id).first()

        if not target_memory:
            return []

        # Use memory content as query
        query = target_memory.title + " " + target_memory.content

        # Retrieve related memories (excluding the target)
        results = self.retrieve_with_ranking(query, top_k=top_k + 1)

        # Filter out the target memory itself
        related = [r for r in results if r["memory"].id != memory_id]

        return related[:top_k]


class DocumentAwareRetriever:
    """
    Retrieval system that automatically prioritizes document search
    when documents are available.
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.smart_retriever = SmartRetriever(db, user_id)

    def has_documents(self) -> bool:
        """Check if user has uploaded documents."""
        count = self.db.query(Memory).filter(Memory.user_id == self.user_id, Memory.source_file.isnot(None)).count()
        return count > 0

    def retrieve_with_document_priority(
        self,
        query: str,
        top_k: int = 5,
        intent: str = "general",
        conversation_context: list[dict] | None = None,
    ) -> tuple[list[dict], bool]:
        """
        Retrieve memories with automatic document prioritization.

        Returns:
            Tuple of (results, used_documents)
        """
        # Check if user has documents
        has_docs = self.has_documents()

        if has_docs:
            # Prioritize document results
            results = self.smart_retriever.retrieve_with_ranking(
                query, top_k=top_k, intent=intent, conversation_context=conversation_context
            )

            # Ensure at least half of results are from documents if possible
            doc_results = [r for r in results if r["source_file"]]
            non_doc_results = [r for r in results if not r["source_file"]]

            if len(doc_results) < top_k // 2:
                # Need more document results, expand search
                additional = self.smart_retriever.retrieve_with_ranking(
                    query,
                    top_k=top_k * 2,
                    intent="document_query",
                    conversation_context=conversation_context,
                )
                additional_docs = [r for r in additional if r["source_file"]]

                # Add unique document results
                existing_ids = {r["memory"].id for r in doc_results}
                for add_doc in additional_docs:
                    if add_doc["memory"].id not in existing_ids:
                        doc_results.append(add_doc)
                        existing_ids.add(add_doc["memory"].id)
                        if len(doc_results) >= top_k:
                            break

            # Re-sort and combine
            combined = doc_results + non_doc_results
            combined.sort(key=lambda x: x["enhanced_score"], reverse=True)

            return combined[:top_k], True
        else:
            # No documents, use normal retrieval
            results = self.smart_retriever.retrieve_with_ranking(
                query, top_k=top_k, intent=intent, conversation_context=conversation_context
            )
            return results, False
