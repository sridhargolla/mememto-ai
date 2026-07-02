"""
Response Formatter Module
Handles ChatGPT-style response formatting with Markdown, tables, code blocks, etc.
"""

import re


class ResponseFormatter:
    """
    Formats AI responses with ChatGPT-style markdown and structure.
    """

    @staticmethod
    def format_markdown(text: str) -> str:
        """
        Ensure proper Markdown formatting in the response.
        """
        # Ensure code blocks have language specification
        text = re.sub(r"```(?!\w)", "```text", text)

        # Ensure proper heading spacing
        text = re.sub(r"([^\n])#", r"\1\n#", text)

        # Ensure list items are properly formatted
        text = re.sub(r"(?<!\n)-", "\n-", text)

        # Ensure numbered lists have proper spacing
        text = re.sub(r"(?<!\n)\d+\.", "\n\\0", text)

        return text

    @staticmethod
    def add_structure(text: str, intent: str) -> str:
        """
        Add structural elements based on intent (simplified to let the LLM generate natural layouts).
        """
        return text

    @staticmethod
    def _add_coding_structure(text: str) -> str:
        return text

    @staticmethod
    def _add_summary_structure(text: str) -> str:
        return text

    @staticmethod
    def _add_comparison_structure(text: str) -> str:
        return text

    @staticmethod
    def add_source_attribution(text: str, sources: list[dict]) -> str:
        """
        Avoid appending raw text source citations; the frontend will render them from the sources JSON array.
        """
        return text

    @staticmethod
    def add_followup_suggestions(text: str, suggestions: list[str]) -> str:
        """
        Avoid appending raw text follow-up lists; the frontend will render suggestion buttons.
        """
        return text

    @staticmethod
    def ensure_readability(text: str) -> str:
        """
        Ensure the response is readable and well-formatted.
        """
        return text

    @staticmethod
    def add_key_takeaways(text: str) -> str:
        """
        Avoid adding hardcoded placeholder key takeaways.
        """
        return text


class FollowupGenerator:
    """
    Generates intelligent follow-up questions based on context.
    """

    @staticmethod
    def generate_followups(
        user_message: str, assistant_response: str, intent: str, has_documents: bool
    ) -> list[str]:
        """
        Generate relevant follow-up questions.
        """
        followups = []

        # Intent-specific follow-ups
        if intent == "coding":
            followups.extend(
                [
                    "Explain this code in more detail",
                    "What are the time and space complexity?",
                    "Can you optimize this code further?",
                    "Add error handling to this code",
                ]
            )
        elif intent == "document_query":
            followups.extend(
                [
                    "Summarize this document",
                    "Find important skills mentioned",
                    "Compare with other documents",
                    "Extract key insights",
                ]
            )
        elif intent == "memory_query":
            followups.extend(
                [
                    "What did I learn recently?",
                    "Show my top memories",
                    "What are my key achievements?",
                    "What projects have I worked on?",
                ]
            )
        elif intent == "summarization":
            followups.extend(
                [
                    "What are the main points?",
                    "Create a bullet-point summary",
                    "What are the key takeaways?",
                    "Explain this in simpler terms",
                ]
            )

        # Context-aware follow-ups
        if has_documents:
            followups.extend(
                [
                    "Search for related information",
                    "Find more details in my documents",
                    "What else do my documents say about this?",
                ]
            )

        # Generic follow-ups
        followups.extend(["Tell me more about this", "Give me an example", "How does this work?"])

        # Return top 3-4 most relevant
        return followups[:4]

    @staticmethod
    def generate_contextual_followups(
        conversation_history: list[dict], current_topic: str
    ) -> list[str]:
        """
        Generate follow-ups based on conversation context.
        """
        followups = []

        # Analyze recent conversation for themes
        recent_topics = []
        for conv in conversation_history[-3:]:
            recent_topics.append(conv["question"].lower())

        # Generate follow-ups based on detected themes
        if any("code" in topic for topic in recent_topics):
            followups.append("Show me more code examples")

        if any("document" in topic or "file" in topic for topic in recent_topics):
            followups.append("What other information is in my documents?")

        if any("skill" in topic or "experience" in topic for topic in recent_topics):
            followups.append("What are my strongest skills?")

        return followups[:3]
