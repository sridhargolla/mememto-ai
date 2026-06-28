import re
from typing import Optional


class PromptSanitizer:
    """Sanitize user input to prevent prompt injection attacks."""
    
    # Patterns that may indicate prompt injection attempts
    INJECTION_PATTERNS = [
        r'ignore\s+(all\s+)?(previous|above)\s+instructions',
        r'disregard\s+(all\s+)?(previous|above)\s+instructions',
        r'forget\s+(all\s+)?(previous|above)\s+instructions',
        r'override\s+(all\s+)?(previous|above)\s+instructions',
        r'new\s+(role|persona|character)',
        r'act\s+as\s+(a|an)',
        r'pretend\s+(to\s+be|you\s+are)',
        r'you\s+are\s+now',
        r'switch\s+to\s+(role|mode)',
        r'change\s+your\s+(behavior|instructions)',
        r'system:\s*',
        r'assistant:\s*',
        r'<\|.*?\|>',  # Special tokens that might be used for injection
    ]
    
    @staticmethod
    def sanitize_input(user_input: str, max_length: int = 5000) -> str:
        """
        Sanitize user input for LLM prompts.
        
        Args:
            user_input: Raw user input
            max_length: Maximum allowed length
        
        Returns:
            Sanitized input
        """
        if not user_input:
            return ""
        
        # Truncate if too long
        if len(user_input) > max_length:
            user_input = user_input[:max_length]
        
        # Remove null bytes and other control characters
        user_input = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', user_input)
        
        # Normalize whitespace
        user_input = re.sub(r'\s+', ' ', user_input).strip()
        
        return user_input
    
    @staticmethod
    def detect_injection_attempt(user_input: str) -> tuple[bool, Optional[str]]:
        """
        Detect potential prompt injection attempts.
        
        Args:
            user_input: User input to check
        
        Returns:
            Tuple of (is_injection, matched_pattern)
        """
        user_input_lower = user_input.lower()
        
        for pattern in PromptSanitizer.INJECTION_PATTERNS:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                return True, pattern
        
        return False, None
    
    @staticmethod
    def sanitize_for_context(user_input: str) -> str:
        """
        Sanitize input that will be used in context/retrieval.
        More aggressive sanitization for context building.
        
        Args:
            user_input: User input
        
        Returns:
            Sanitized input
        """
        # Basic sanitization
        sanitized = PromptSanitizer.sanitize_input(user_input)
        
        # Remove any markdown code blocks that might be used for injection
        sanitized = re.sub(r'```[\s\S]*?```', '', sanitized)
        
        # Remove any XML-like tags that might be used for structured injection
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        return sanitized
    
    @staticmethod
    def is_safe(user_input: str) -> bool:
        """
        Check if input is safe for LLM processing.
        
        Args:
            user_input: User input to check
        
        Returns:
            True if safe, False otherwise
        """
        is_injection, _ = PromptSanitizer.detect_injection_attempt(user_input)
        return not is_injection
