"""
Follow-up Question Generator
Generates intelligent, context-aware follow-up questions.
"""

from conversation_intelligence import ConversationIntelligence


class FollowupGenerator:
    """
    Generates relevant follow-up questions based on conversation context.
    """

    INTENT_FOLLOWUPS = {
        "coding": [
            "Explain this code in more detail",
            "What are the time and space complexity?",
            "Can you optimize this code further?",
            "Add error handling to this code",
            "Show me a different approach",
            "What are the edge cases?",
        ],
        "document_query": [
            "Summarize this document",
            "Find important skills mentioned",
            "Compare with other documents",
            "Extract key insights",
            "What are the main points?",
            "Search for related information",
        ],
        "memory_query": [
            "What did I learn recently?",
            "Show my top memories",
            "What are my key achievements?",
            "What projects have I worked on?",
            "What skills do I have?",
            "What's my experience with X?",
        ],
        "summarization": [
            "What are the main points?",
            "Create a bullet-point summary",
            "What are the key takeaways?",
            "Explain this in simpler terms",
            "What did I miss?",
            "Summarize in one sentence",
        ],
        "comparison": [
            "What are the key differences?",
            "Which one is better for my use case?",
            "Compare them in a table",
            "What are the pros and cons?",
            "When should I use each?",
        ],
        "general": [
            "Tell me more about this",
            "Give me an example",
            "How does this work?",
            "Why is this important?",
            "What should I do next?",
        ],
    }

    def __init__(self, conversation_intelligence: ConversationIntelligence):
        self.ci = conversation_intelligence

    def generate_followups(
        self,
        user_message: str,
        assistant_response: str,
        intent: str,
        has_documents: bool = False,
        conversation_history: list[dict] | None = None,
    ) -> list[str]:
        """
        Generate relevant follow-up questions dynamically based on message context.
        """
        import re

        followups = []
        user_msg_lower = user_message.lower()
        assistant_response.lower()

        # 1. Extract dynamic keywords/topics from the user query
        keywords = []
        # Find capitalized terms or double quoted strings
        quoted = re.findall(r'"([^"]+)"', user_message)
        if quoted:
            keywords.extend(quoted)

        # Find single word entities/topics
        for word in re.findall(r"\b[A-Z][a-zA-Z0-9_-]+\b", user_message):
            if word.lower() not in [
                "memento",
                "ai",
                "i",
                "hello",
                "hi",
                "how",
                "what",
                "who",
            ]:
                keywords.append(word)

        # Fallback to key nouns in the user message
        if not keywords:
            words = [w.strip("?.!,:;") for w in user_message.split() if len(w) > 4]
            # pick up to 2 words
            keywords.extend(words[:2])

        keywords = list(dict.fromkeys(keywords))[:3]  # unique first 3

        # 2. Generate dynamic questions based on keywords
        for kw in keywords:
            if kw:
                followups.append(f"Tell me more about {kw}")
                if has_documents:
                    followups.append(f"What details do my files have on {kw}?")

        # 3. Add intent-specific dynamic questions
        if intent == "coding" or "```" in assistant_response:
            if "complexity" not in user_msg_lower:
                followups.append("What are the time and space complexity?")
            if "optimize" not in user_msg_lower:
                followups.append("Can you optimize this code further?")
            followups.append("Add error handling and comments to this code")
        elif intent == "document_query" or "document" in user_msg_lower:
            followups.append("Summarize this document")
            followups.append("Extract key insights from this document")
        elif intent == "memory_query" or "memory" in user_msg_lower:
            followups.append("Show my recent memories")
            followups.append("What did I learn this week?")
        elif intent == "summarization" or "summarize" in user_msg_lower:
            followups.append("What are the main points?")
            followups.append("Explain this in simpler terms")

        # 4. Defaults
        followups.extend(
            [
                "Give me a real-world example",
                "Why is this important?",
                "How does this work in detail?",
            ]
        )

        # Deduplicate, keep order, limit to 4
        unique_followups = []
        seen = set()
        for f in followups:
            f_clean = f.strip("?. ").lower()
            if f_clean not in seen and len(unique_followups) < 4:
                seen.add(f_clean)
                unique_followups.append(f)

        return unique_followups

    def _generate_contextual_followups(
        self, conversation_history: list[dict], intent: str
    ) -> list[str]:
        """Generate follow-ups based on conversation context."""
        followups = []

        # Analyze recent conversation for themes
        recent_topics = []
        for conv in conversation_history[-3:]:
            recent_topics.append(conv["question"].lower())

        # Generate based on detected themes
        if any("code" in topic for topic in recent_topics):
            followups.append("Show me more code examples")

        if any("document" in topic or "file" in topic for topic in recent_topics):
            followups.append("What other information is in my documents?")

        if any("skill" in topic or "experience" in topic for topic in recent_topics):
            followups.append("What are my strongest skills?")

        if any("project" in topic for topic in recent_topics):
            followups.append("Tell me about another project")

        return followups

    def _generate_response_followups(self, response: str) -> list[str]:
        """Generate follow-ups based on the response content."""
        followups = []
        response_lower = response.lower()

        # Check for code in response
        if "```" in response or "code" in response_lower:
            followups.append("Explain this code")

        # Check for lists/points
        if "-" in response or "*" in response or "•" in response:
            followups.append("Elaborate on these points")

        # Check for comparisons
        if "vs" in response_lower or "versus" in response_lower or "compare" in response_lower:
            followups.append("Which one should I choose?")

        # Check for explanations
        if "explain" in response_lower or "how" in response_lower:
            followups.append("Show me an example")

        return followups

    def generate_coding_followups(self, code_language: str | None = None) -> list[str]:
        """Generate follow-ups specific to coding questions."""
        base_followups = [
            "Explain this code in detail",
            "What are the time and space complexity?",
            "Can you optimize this further?",
            "Add error handling",
            "Write unit tests for this",
        ]

        if code_language:
            language_specific = {
                "python": [
                    "Use list comprehension instead",
                    "Make it more Pythonic",
                    "Add type hints",
                ],
                "javascript": [
                    "Convert to modern ES6+",
                    "Use async/await",
                    "Add error handling with try/catch",
                ],
                "java": [
                    "Use streams instead of loops",
                    "Add proper exception handling",
                    "Use generics",
                ],
            }
            base_followups.extend(language_specific.get(code_language, []))

        return base_followups[:4]

    def generate_document_followups(self, document_type: str | None = None) -> list[str]:
        """Generate follow-ups specific to document queries."""
        base_followups = [
            "Summarize the key points",
            "Extract important information",
            "Find related sections",
            "What are the main conclusions?",
        ]

        if document_type:
            type_specific = {
                "resume": [
                    "What are my key skills?",
                    "Summarize my experience",
                    "What are my achievements?",
                ],
                "research": [
                    "What are the key findings?",
                    "Summarize the methodology",
                    "What are the limitations?",
                ],
                "report": [
                    "What are the recommendations?",
                    "Summarize the executive summary",
                    "What are the action items?",
                ],
            }
            base_followups.extend(type_specific.get(document_type, []))

        return base_followups[:4]
