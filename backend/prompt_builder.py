"""
Dynamic Prompt Builder
Constructs optimized prompts with context injection for the local LLM.
"""

from personality_engine import PersonalityEngine


class PromptBuilder:
    """
    Builds dynamic, context-rich prompts for the LLM.
    Injects relevant context, conversation history, and personality.
    """

    def __init__(self, personality_engine: PersonalityEngine):
        self.personality = personality_engine

    def build_prompt(
        self,
        user_message: str,
        intelligence: dict,
        retrieved_memories: list[dict],
        conversation_history: list[dict],
        user_preferences: dict | None = None,
        language: str = "en",
    ) -> str:
        """
        Build a comprehensive prompt with ChatML formatting.
        """
        system_parts = []

        # 1. System Prompt with Personality
        system_prompt = self.personality.get_system_prompt(
            language=language,
            context={
                "has_documents": len(retrieved_memories) > 0,
                "previous_conversations": len(conversation_history) > 0,
                "user_preferences": user_preferences or {},
            },
        )
        system_parts.append(system_prompt)

        # 2. User Preferences
        if user_preferences:
            pref_text = self._format_preferences(user_preferences)
            system_parts.append(f"\nUser Preferences:\n{pref_text}")

        # 3. Retrieved Memories & Documents
        if retrieved_memories:
            memories_text = self._format_memories(retrieved_memories)
            system_parts.append(
                f"\n--- Relevant Context from Documents & Memories ---\n{memories_text}\n-------------------------------------------------"
            )

        system_content = "\n".join(system_parts)

        # Construct ChatML string
        chat_ml_prompt = f"<|im_start|>system\n{system_content}\n<|im_end|>\n"

        # Add conversation history (up to last 5 turns)
        for turn in conversation_history[-5:]:
            chat_ml_prompt += f"<|im_start|>user\n{turn['question']}\n<|im_end|>\n"
            chat_ml_prompt += f"<|im_start|>assistant\n{turn['answer']}\n<|im_end|>\n"

        # Add current user message
        chat_ml_prompt += f"<|im_start|>user\n{user_message}\n<|im_end|>\n"
        chat_ml_prompt += "<|im_start|>assistant\n"

        return chat_ml_prompt

    def _format_preferences(self, preferences: dict) -> str:
        """Format user preferences."""
        items = []
        for key, value in preferences.items():
            items.append(f"- {key}: {value}")
        return "\n".join(items) if items else "No specific preferences set."

    def _format_memories(self, memories: list[dict]) -> str:
        """Format retrieved memories cleanly for context injection."""
        formatted = []

        for memory in memories:
            source = (
                memory.get("source_file") or memory.get("source_document") or "Personal Knowledge"
            )
            title = memory.get("title", "Untitled")
            content = memory.get("content", "").strip()

            # Clean content prefix metadata if present
            if "Content Preview:" in content:
                content = content.split("Content Preview:")[-1].strip()

            formatted.append(f"[Source: {source} | Title: {title}]\n{content}\n")

        return "\n".join(formatted)

    def build_coding_prompt(
        self,
        user_message: str,
        intelligence: dict,
        conversation_history: list[dict],
        language: str = "en",
    ) -> str:
        """
        Build a specialized coding prompt using ChatML.
        """
        system_prompt = f"""You are Memento, an expert coding assistant. Help the user with programming questions by providing clear explanations and complete, runnable code blocks with syntax highlighting.
Respond in {language.upper()}."""

        chat_ml = f"<|im_start|>system\n{system_prompt}\n<|im_end|>\n"

        for turn in conversation_history[-3:]:
            chat_ml += f"<|im_start|>user\n{turn['question']}\n<|im_end|>\n"
            chat_ml += f"<|im_start|>assistant\n{turn['answer']}\n<|im_end|>\n"

        chat_ml += f"<|im_start|>user\n{user_message}\n<|im_end|>\n"
        chat_ml += "<|im_start|>assistant\n"
        return chat_ml

    def build_summarization_prompt(
        self, user_message: str, content_to_summarize: str, language: str = "en"
    ) -> str:
        """
        Build a specialized summarization prompt using ChatML.
        """
        system_prompt = f"""You are Memento, a skilled summarizer. Create a clear, well-structured summary of the provided text.
Respond in {language.upper()}."""

        chat_ml = f"<|im_start|>system\n{system_prompt}\n<|im_end|>\n"
        chat_ml += f"<|im_start|>user\nContent to Summarize:\n{content_to_summarize}\n\nSpecific Request: {user_message}\n<|im_end|>\n"
        chat_ml += "<|im_start|>assistant\n"
        return chat_ml

    def build_followup_prompt(
        self,
        user_message: str,
        previous_answer: str,
        intelligence: dict,
        language: str = "en",
    ) -> str:
        """
        Build a prompt for follow-up questions using ChatML.
        """
        system_prompt = f"""You are Memento, continuing an ongoing conversation. Maintain consistency with the previous answer.
Respond in {language.upper()}."""

        chat_ml = f"<|im_start|>system\n{system_prompt}\n<|im_end|>\n"
        chat_ml += f"<|im_start|>user\nPrevious Context:\n{previous_answer[:500]}...\n\nFollow-up Question: {user_message}\n<|im_end|>\n"
        chat_ml += "<|im_start|>assistant\n"
        return chat_ml


class ProgressivePromptBuilder:
    """
    Builds prompts progressively for streaming responses.
    Allows for context injection at different stages.
    """

    def __init__(self, base_builder: PromptBuilder):
        self.base_builder = base_builder

    def build_initial_prompt(
        self, user_message: str, intelligence: dict, language: str = "en"
    ) -> str:
        """Build the initial prompt without full context."""
        system_prompt = self.base_builder.personality.get_system_prompt(language=language)
        return f"""{system_prompt}

**User's Question:**
{intelligence["resolved_message"]}

Begin your response naturally and conversationally."""

    def build_context_injection_prompt(self, context: str, sources: list[str]) -> str:
        """Build a prompt for injecting additional context."""
        sources_text = "\n".join(f"- {s}" for s in sources)
        return f"""**Additional Context Retrieved:**
{context}

**Sources:**
{sources_text}

Continue your response incorporating this information naturally."""
