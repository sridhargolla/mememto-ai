from embedding_service import EmbeddingService
from sqlalchemy.orm import Session

from models import Memory


class MemoryRetriever:
    """Retrieve relevant memories using semantic search and keyword matching."""

    @staticmethod
    def extract_keywords(query: str) -> list[str]:
        """
        Extract keywords from a query.

        Args:
            query: User query string

        Returns:
            List of keywords
        """
        # Simple keyword extraction - split by common delimiters
        import re

        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "need",
            "dare",
            "how",
            "what",
            "when",
            "where",
            "why",
            "who",
            "which",
            "that",
            "this",
            "these",
            "those",
            "am",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "its",
            "our",
            "their",
            "mine",
            "yours",
            "hers",
            "ours",
            "theirs",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "and",
            "but",
            "if",
            "or",
            "because",
            "until",
            "while",
            "about",
        }

        # Split query into words and filter stop words
        words = re.findall(r"\b\w+\b", query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return keywords

    @staticmethod
    def calculate_relevance(memory: Memory, keywords: list[str]) -> float:
        """
        Calculate relevance score of a memory based on keyword matching.

        Args:
            memory: Memory object
            keywords: List of keywords to search for

        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not keywords:
            return 0.0

        memory_text = (memory.title + " " + memory.content + " " + (memory.tags or "")).lower()

        matches = 0
        for keyword in keywords:
            if keyword in memory_text:
                matches += 1

        # Score is ratio of matched keywords
        score = matches / len(keywords)
        return score

    @staticmethod
    def retrieve_memories(
        db: Session,
        query: str,
        top_k: int = 3,
        min_score: float = 0.2,
        user_id: int | None = None,
    ) -> list[tuple[Memory, float]]:
        """
        Retrieve most relevant memories for a query.

        Args:
            db: Database session
            query: User query
            top_k: Number of top memories to retrieve
            min_score: Minimum relevance score threshold
            user_id: Optional user ID to filter memories

        Returns:
            List of (memory, score) tuples sorted by relevance
        """
        # Get all memories (filtered by user if provided)
        if user_id:
            memories = db.query(Memory).filter(Memory.user_id == user_id).all()
        else:
            memories = db.query(Memory).all()

        if not memories:
            return []

        # Extract keywords from query
        keywords = MemoryRetriever.extract_keywords(query)

        if not keywords:
            return []

        # Calculate relevance scores
        scored_memories = []
        for memory in memories:
            score = MemoryRetriever.calculate_relevance(memory, keywords)
            if score >= min_score:
                scored_memories.append((memory, score))

        # Sort by score descending and return top_k
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return scored_memories[:top_k]

    @staticmethod
    def format_context(memories: list[tuple[Memory, float]]) -> str:
        """
        Format retrieved memories into context string.

        Args:
            memories: List of (memory, score) tuples

        Returns:
            Formatted context string
        """
        if not memories:
            return ""

        context_parts = []
        for memory, score in memories:
            context_parts.append(f"- {memory.title}: {memory.content}")

        return "\n".join(context_parts)

    @staticmethod
    def retrieve_semantically(
        db: Session,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.3,
        user_id: int | None = None,
    ) -> list[tuple[Memory, float]]:
        """
        Retrieve most relevant memories using semantic search.

        Args:
            db: Database session
            query: User query
            top_k: Number of top memories to retrieve
            min_similarity: Minimum similarity score threshold
            user_id: Optional user ID to filter memories

        Returns:
            List of (memory, similarity) tuples sorted by similarity
        """
        embedding_service = EmbeddingService()

        if not embedding_service.is_loaded():
            # Fallback to keyword search if embedding model not loaded
            return MemoryRetriever.retrieve_memories(db, query, top_k, min_similarity, user_id)

        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)
        if query_embedding is None:
            return []

        # Get all memories with embeddings (filtered by user if provided)
        if user_id:
            memories = (
                db.query(Memory)
                .filter(Memory.embedding.isnot(None), Memory.user_id == user_id)
                .all()
            )
        else:
            memories = db.query(Memory).filter(Memory.embedding.isnot(None)).all()

        if not memories:
            # Fallback to keyword search if no embeddings exist
            return MemoryRetriever.retrieve_memories(db, query, top_k, min_similarity, user_id)

        # Calculate similarity scores
        scored_memories = []
        for memory in memories:
            if memory.embedding:
                try:
                    memory_embedding = embedding_service.deserialize_embedding(memory.embedding)
                    similarity = embedding_service.calculate_similarity(
                        query_embedding, memory_embedding
                    )
                    if similarity >= min_similarity:
                        scored_memories.append((memory, similarity))
                except Exception as e:
                    print(f"Error calculating similarity for memory {memory.id}: {e}")
                    continue

        # Sort by similarity descending and return top_k
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return scored_memories[:top_k]

    @staticmethod
    def retrieve_hybrid(
        db: Session, query: str, top_k: int = 3, user_id: int | None = None
    ) -> list[tuple[Memory, float]]:
        """
        Retrieve memories using a hybrid approach combining semantic and keyword search.

        Args:
            db: Database session
            query: User query
            top_k: Number of top memories to retrieve
            user_id: Optional user ID to filter memories

        Returns:
            List of (memory, hybrid_score) tuples sorted by score
        """
        # Get semantic results (wider net)
        semantic_results = []
        try:
            semantic_results = MemoryRetriever.retrieve_semantically(
                db, query, top_k=top_k * 3, min_similarity=0.15, user_id=user_id
            )
        except Exception as e:
            print(f"Semantic retrieval failed: {e}")

        # Get keyword results (wider net)
        keyword_results = []
        try:
            keyword_results = MemoryRetriever.retrieve_memories(
                db, query, top_k=top_k * 3, min_score=0.05, user_id=user_id
            )
        except Exception as e:
            print(f"Keyword retrieval failed: {e}")

        # Combine scores
        scores = {}

        for memory, score in semantic_results:
            scores[memory.id] = {"memory": memory, "semantic": score, "keyword": 0.0}

        for memory, score in keyword_results:
            if memory.id in scores:
                scores[memory.id]["keyword"] = score
            else:
                scores[memory.id] = {
                    "memory": memory,
                    "semantic": 0.0,
                    "keyword": score,
                }

        # Calculate weighted sum (70% semantic, 30% keyword)
        scored_memories = []
        for memory_id, data in scores.items():
            hybrid_score = 0.7 * data["semantic"] + 0.3 * data["keyword"]
            scored_memories.append((data["memory"], hybrid_score))

        # Sort by score descending and return top_k
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return scored_memories[:top_k]
