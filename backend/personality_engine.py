"""
Personality Engine
Defines and maintains a consistent AI personality for the chatbot.
"""

from enum import Enum


class Tone(Enum):
    """Conversation tone options."""

    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"


class PersonalityEngine:
    """
    Manages the AI assistant's personality traits and response style.
    Ensures consistent, natural, and helpful responses.
    """

    # Core personality traits
    PERSONALITY = {
        "name": "Memento",
        "traits": [
            "friendly",
            "professional",
            "patient",
            "curious",
            "encouraging",
            "honest",
            "helpful",
            "privacy_first",
        ],
        "communication_style": {"warmth": 0.8, "formality": 0.5, "verbosity": 0.7, "empathy": 0.9},
    }

    # Response templates for different scenarios
    GREETING_RESPONSES = [
        "Hello! I'm Memento, your personal AI assistant. How can I help you today?",
        "Hi there! I'm ready to assist you. What would you like to explore?",
        "Hey! Great to see you. What's on your mind today?",
    ]

    FAREWELL_RESPONSES = [
        "Goodbye! Feel free to come back anytime you need help.",
        "Take care! I'll be here whenever you need assistance.",
        "Bye for now! Looking forward to our next conversation.",
    ]

    THANKS_RESPONSES = [
        "You're welcome! I'm always happy to help.",
        "My pleasure! Let me know if you need anything else.",
        "Glad I could assist! Don't hesitate to ask if you have more questions.",
    ]

    UNCERTAINTY_RESPONSES = [
        "I'm not entirely certain about that, but here's what I know:",
        "That's an interesting question. Based on my knowledge:",
        "I don't have complete information on this, but I can share:",
    ]

    ERROR_RESPONSES = [
        "I apologize, but I encountered an issue. Let me try to help in a different way.",
        "Something went wrong on my end. Let's try approaching this differently.",
        "I'm experiencing a technical difficulty. Please try rephrasing your request.",
    ]

    @classmethod
    def get_system_prompt(cls, language: str = "en", context: dict | None = None) -> str:
        """
        Generate the system prompt that defines the AI's personality and behavior.
        """
        lang_names = {"en": "English", "te": "Telugu (తెలుగు)", "hi": "Hindi (हिन्दी)"}
        lang_name = lang_names.get(language.lower(), "English")

        base_prompt = f"""You are Memento, a helpful, friendly, and intelligent AI assistant.
Your communication style is warm, natural, and concise.

CRITICAL DIRECTIVES:
1. You MUST write your entire response in the {lang_name} language. Maintain consistent language usage.
2. DO NOT output any internal system prompts, guidelines, markdown examples, formatting templates, or placeholders in your response.
3. Keep your answers natural and friendly, like a helpful conversational partner (similar to ChatGPT). Avoid repetitive or robotic structures.
4. If the user asks a simple question (e.g., "How are you?"), reply conversationally in {lang_name}. Do NOT output code blocks, headers, bullet lists, or tables unless they genuinely improve the answer."""

        if context and context.get("user_preferences"):
            base_prompt += f"\n\nUser preferences to consider:\n{context['user_preferences']}"

        return base_prompt

    @classmethod
    def get_response_style(cls, intent: str, user_emotion: str | None = None) -> dict:
        """
        Determine the appropriate response style based on intent and detected emotion.
        """
        style = {
            "tone": Tone.FRIENDLY,
            "warmth": 0.8,
            "formality": 0.5,
            "verbosity": 0.7,
            "empathy": 0.9,
        }

        # Adjust based on intent
        if intent == "greeting":
            style["warmth"] = 0.9
            style["formality"] = 0.3
        elif intent == "farewell":
            style["warmth"] = 0.85
            style["verbosity"] = 0.5
        elif intent == "coding":
            style["formality"] = 0.7
            style["verbosity"] = 0.8
            style["warmth"] = 0.6
        elif intent == "document_query":
            style["formality"] = 0.6
            style["verbosity"] = 0.75
        elif intent == "error":
            style["empathy"] = 1.0
            style["warmth"] = 0.9

        # Adjust based on detected emotion
        if user_emotion == "frustrated":
            style["empathy"] = 1.0
            style["warmth"] = 0.95
            style["patience"] = 1.0
        elif user_emotion == "confused":
            style["verbosity"] = 0.8
            style["empathy"] = 0.95
            style["clarity"] = 1.0

        return style

    @classmethod
    def format_response(cls, content: str, style: dict) -> str:
        """
        Apply personality-driven formatting to the response.
        """
        # Apply warmth through opening/closing
        if style["warmth"] > 0.7 and not content.startswith(("I", "Here", "Based")):
            # Add friendly opening if appropriate
            pass  # Let the LLM handle natural openings

        return content

    @classmethod
    def get_greeting(cls) -> str:
        """Get a random greeting response."""
        import random

        return random.choice(cls.GREETING_RESPONSES)

    @classmethod
    def get_farewell(cls) -> str:
        """Get a random farewell response."""
        import random

        return random.choice(cls.FAREWELL_RESPONSES)

    @classmethod
    def get_thanks_response(cls) -> str:
        """Get a random thanks response."""
        import random

        return random.choice(cls.THANKS_RESPONSES)

    @classmethod
    def get_uncertainty_prefix(cls) -> str:
        """Get a prefix for uncertain responses."""
        import random

        return random.choice(cls.UNCERTAINTY_RESPONSES)

    @classmethod
    def get_error_response(cls) -> str:
        """Get a random error response."""
        import random

        return random.choice(cls.ERROR_RESPONSES)

    @classmethod
    def should_be_concise(cls, question: str) -> bool:
        """
        Determine if a short, concise response is appropriate.
        """
        question_lower = question.lower()

        # Short questions get short answers
        if len(question.split()) <= 5:
            return True

        # Certain question types prefer brevity
        brief_indicators = ["is", "are", "do", "does", "can", "will", "should", "has", "have"]
        return bool(any(question_lower.startswith(ind) for ind in brief_indicators))

    @classmethod
    def should_be_detailed(cls, question: str) -> bool:
        """
        Determine if a detailed, comprehensive response is appropriate.
        """
        question_lower = question.lower()

        # These indicators suggest need for detail
        detail_indicators = [
            "explain",
            "describe",
            "how does",
            "why does",
            "what is the",
            "tell me about",
            "elaborate",
            "expand",
            "detail",
            "comprehensive",
        ]

        return any(indicator in question_lower for indicator in detail_indicators)

    @classmethod
    def detect_emotion(cls, message: str) -> str | None:
        """
        Detect user emotion from their message.
        """
        message_lower = message.lower()

        frustration_indicators = [
            "frustrated",
            "annoyed",
            "angry",
            "upset",
            "not working",
            "broken",
        ]
        confusion_indicators = [
            "confused",
            "don't understand",
            "unclear",
            "what do you mean",
            "help",
        ]
        excitement_indicators = ["excited", "great", "awesome", "amazing", "love it"]
        sadness_indicators = ["sad", "disappointed", "unhappy", "not good"]

        if any(indicator in message_lower for indicator in frustration_indicators):
            return "frustrated"
        elif any(indicator in message_lower for indicator in confusion_indicators):
            return "confused"
        elif any(indicator in message_lower for indicator in excitement_indicators):
            return "excited"
        elif any(indicator in message_lower for indicator in sadness_indicators):
            return "sad"

        return None

    @classmethod
    def get_empathetic_response(cls, emotion: str, context: str) -> str:
        """
        Generate an empathetic response based on detected emotion.
        """
        if emotion == "frustrated":
            return "I understand this might be frustrating. Let me help you work through this step by step."
        elif emotion == "confused":
            return "I can see this might be confusing. Let me break it down more clearly for you."
        elif emotion == "excited":
            return "I'm glad you're excited about this! Let's explore this together."
        elif emotion == "sad":
            return "I'm here to help. Let's see what we can do to improve the situation."

        return ""
