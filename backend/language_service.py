"""
Language service for detecting language and providing language-specific instructions.
This service works completely offline using Unicode range heuristics.
"""


def detect_language(text: str) -> str:
    """
    Detect the language of the given text using Unicode range heuristics.
    Supports English (en), Telugu (te), and Hindi (hi).

    Args:
        text: The input text to analyze

    Returns:
        Language code ('en', 'te', or 'hi')
    """
    if not text:
        return "en"

    # Count characters in each language's Unicode range
    telugu_count = 0
    hindi_count = 0
    english_count = 0

    for char in text:
        code_point = ord(char)

        # Telugu Unicode range: U+0C00 to U+0C7F
        if 0x0C00 <= code_point <= 0x0C7F:
            telugu_count += 1
        # Devanagari (Hindi) Unicode range: U+0900 to U+097F
        elif 0x0900 <= code_point <= 0x097F:
            hindi_count += 1
        # Basic Latin (English) range: U+0020 to U+007F (excluding punctuation)
        elif 0x0041 <= code_point <= 0x005A or 0x0061 <= code_point <= 0x007A:
            english_count += 1

    # Determine language based on character counts
    if telugu_count > 0:
        return "te"
    elif hindi_count > 0:
        return "hi"
    else:
        return "en"


def get_language_instruction(language: str) -> str:
    """
    Get language-specific instruction for the local LLM.
    This instruction tells the LLM to respond in the specified language.

    Args:
        language: Language code ('en', 'te', or 'hi')

    Returns:
        Instruction string for the LLM
    """
    instructions = {
        "en": "Respond in English. Use clear and concise language.",
        "te": "Respond in Telugu (తెలుగు). Use clear and natural Telugu language.",
        "hi": "Respond in Hindi (हिंदी). Use clear and natural Hindi language.",
    }

    return instructions.get(language, instructions["en"])
