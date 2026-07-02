"""
Conversation Intelligence Module
Handles intent detection, context awareness, multi-turn conversations,
context compression, and pronoun resolution.
"""

import re

from sqlalchemy.orm import Session

from models import Conversation


class IntentDetector:
    """Detects user intent from messages."""

    INTENTS = {
        "question": [
            "what",
            "how",
            "why",
            "when",
            "where",
            "which",
            "who",
            "can you",
            "could you",
        ],
        "command": ["tell me", "show me", "list", "find", "search", "get", "retrieve"],
        "greeting": [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        ],
        "farewell": ["bye", "goodbye", "see you", "farewell"],
        "thanks": ["thank", "thanks", "appreciate"],
        "coding": [
            "code",
            "function",
            "class",
            "algorithm",
            "implement",
            "debug",
            "fix",
            "programming",
        ],
        "document_query": ["document", "file", "resume", "paper", "report", "upload"],
        "memory_query": ["remember", "memory", "recall", "what did i", "my"],
        "summarization": ["summarize", "summary", "overview", "recap"],
        "comparison": ["compare", "difference", "vs", "versus", "better"],
    }

    @classmethod
    def detect_intent(cls, message: str) -> str:
        """Detect the primary intent of a user message."""
        message_lower = message.lower()

        # Check for greetings and farewells first
        for intent, keywords in cls.INTENTS.items():
            if intent in ["greeting", "farewell", "thanks"]:
                for keyword in keywords:
                    if keyword in message_lower:
                        return intent

        # Check for other intents
        intent_scores = {}
        for intent, keywords in cls.INTENTS.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score

        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]

        return "general"

    @classmethod
    def detect_follow_up(cls, message: str) -> bool:
        """Check if this is a follow-up question."""
        follow_up_indicators = [
            "what about",
            "and",
            "also",
            "what else",
            "more about",
            "tell me more",
            "why",
            "how",
            "explain",
            "clarify",
        ]
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in follow_up_indicators)

    @classmethod
    def detect_pronoun_references(cls, message: str) -> list[str]:
        """Detect pronoun references that need resolution."""
        pronouns = [
            "it",
            "they",
            "them",
            "this",
            "that",
            "these",
            "those",
            "he",
            "she",
            "his",
            "her",
        ]
        found = []
        for word in message.split():
            word_lower = word.lower().strip(".,!?;:")
            if word_lower in pronouns:
                found.append(word_lower)
        return found


class ContextManager:
    """Manages conversation context and history."""

    def __init__(self, db: Session, user_id: int, max_history: int = 10):
        self.db = db
        self.user_id = user_id
        self.max_history = max_history
        self.conversation_history: list[dict] = []
        self.context_window: list[str] = []
        self.entity_memory: dict[str, str] = {}

    def load_recent_history(self, limit: int = 10, session_id: str | None = None) -> list[dict]:
        """Load recent conversation history."""
        query = self.db.query(Conversation).filter(Conversation.user_id == self.user_id)
        if session_id:
            query = query.filter(Conversation.session_id == session_id)

        recent_convs = query.order_by(Conversation.timestamp.desc()).limit(limit).all()

        self.conversation_history = [
            {
                "question": conv.question,
                "answer": conv.answer,
                "timestamp": conv.timestamp.isoformat(),
            }
            for conv in reversed(recent_convs)
        ]

        return self.conversation_history

    def extract_entities(self, message: str) -> dict[str, str]:
        """Extract and remember entities from user messages."""
        # Simple entity extraction patterns
        patterns = {
            "name": r"(?:my name is|i am|i\'m|i am called)\s+([A-Z][a-z]+)",
            "email": r"[\w\.-]+@[\w\.-]+\.\w+",
            "phone": r"\b\d{10}\b|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "date": r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b",
        }

        entities = {}
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches[0]
                self.entity_memory[entity_type] = matches[0]

        # Merge with existing entity memory
        entities.update(self.entity_memory)
        return entities

    def resolve_pronouns(self, message: str) -> str:
        """Resolve pronoun references using conversation history."""
        pronouns = IntentDetector.detect_pronoun_references(message)

        if not pronouns:
            return message

        resolved = message
        recent_entities = self._get_recent_entities()

        for pronoun in pronouns:
            if pronoun in ["it", "this", "that"]:
                # Try to resolve to the most recently mentioned noun
                if "last_subject" in recent_entities:
                    resolved = resolved.replace(
                        f" {pronoun}", f" {recent_entities['last_subject']}", 1
                    )
            elif pronoun in ["they", "them"] and "last_plural" in recent_entities:
                resolved = resolved.replace(f" {pronoun}", f" {recent_entities['last_plural']}", 1)

        return resolved

    def _get_recent_entities(self) -> dict[str, str]:
        """Get recently mentioned entities from conversation history."""
        entities = {}

        for conv in self.conversation_history[-3:]:
            # Extract nouns from the last user question
            words = re.findall(r"\b[A-Z][a-z]+\b", conv["question"])
            if words:
                entities["last_subject"] = words[-1]
                if len(words) > 1:
                    entities["last_plural"] = ", ".join(words[-2:])

        return entities

    def compress_context(self, messages: list[dict], max_tokens: int = 1000) -> str:
        """Compress conversation context to fit within token limits."""
        if not messages:
            return ""

        # Simple compression: keep recent messages, summarize older ones
        if len(messages) <= 3:
            return self._format_messages(messages)

        recent = messages[-2:]
        older = messages[:-2]

        summary = f"[Previous conversation: {len(older)} exchanges about various topics]"
        recent_text = self._format_messages(recent)

        return f"{summary}\n{recent_text}"

    def _format_messages(self, messages: list[dict]) -> str:
        """Format messages for context."""
        formatted = []
        for msg in messages:
            formatted.append(f"User: {msg['question']}")
            formatted.append(f"Assistant: {msg['answer']}")
        return "\n".join(formatted)

    def update_context_window(self, new_message: str, response: str):
        """Update the context window with new conversation."""
        self.context_window.append(f"User: {new_message}")
        self.context_window.append(f"Assistant: {response}")

        # Keep context window manageable
        if len(self.context_window) > 20:  # 10 turns
            self.context_window = self.context_window[-20:]


class ConversationIntelligence:
    """Main conversation intelligence orchestrator."""

    def __init__(self, db: Session, user_id: int, session_id: str | None = None):
        self.user_id = user_id
        self.session_id = session_id
        self.intent_detector = IntentDetector()
        self.context_manager = ContextManager(db, user_id)

    def process_message(self, message: str) -> dict:
        """Process a user message and extract intelligence."""
        # Detect intent
        intent = self.intent_detector.detect_intent(message)

        # Check if follow-up
        is_follow_up = self.intent_detector.detect_follow_up(message)

        # Load conversation history
        history = self.context_manager.load_recent_history(session_id=self.session_id)

        # Extract entities
        entities = self.context_manager.extract_entities(message)

        # Resolve pronouns
        resolved_message = self.context_manager.resolve_pronouns(message)

        # Compress context if needed
        compressed_context = self.context_manager.compress_context(history)

        return {
            "intent": intent,
            "is_follow_up": is_follow_up,
            "entities": entities,
            "resolved_message": resolved_message,
            "context": compressed_context,
            "history": history,
        }

    def should_use_coding_mode(self, message: str) -> bool:
        """Determine if the user is asking a coding question."""
        intent = self.intent_detector.detect_intent(message)
        return intent == "coding" or "code" in message.lower()

    def should_summarize(self, message: str) -> bool:
        """Determine if the user wants a summary."""
        intent = self.intent_detector.detect_intent(message)
        return intent == "summarization"
