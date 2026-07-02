"""
Unit tests for MemoryExtractorService.

Tests JSON extraction, validation, and error handling without requiring actual LLM.
"""

import pytest

from memory_extractor_service import MemoryExtractorService
from memory_schema import MemorySchema


class MockLLM:
    """Mock LLM for testing without actual model."""

    def __init__(self, response: str):
        self.response = response

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.1) -> str:
        return self.response


class TestMemoryExtractorService:
    """Test suite for MemoryExtractorService."""

    def test_extract_json_from_response_with_code_block(self):
        """Test JSON extraction from markdown code block."""
        service = MemoryExtractorService(MockLLM(""))
        response = '```json\n[{"type": "experience", "title": "Test"}]\n```'
        result = service._extract_json_from_response(response)
        assert result == '[{"type": "experience", "title": "Test"}]'

    def test_extract_json_from_response_with_generic_code_block(self):
        """Test JSON extraction from generic code block."""
        service = MemoryExtractorService(MockLLM(""))
        response = '```\n[{"type": "experience", "title": "Test"}]\n```'
        result = service._extract_json_from_response(response)
        assert result == '[{"type": "experience", "title": "Test"}]'

    def test_extract_json_from_response_with_array_bounds(self):
        """Test JSON extraction using array bounds."""
        service = MemoryExtractorService(MockLLM(""))
        response = 'Here is the JSON: [{"type": "experience", "title": "Test"}]'
        result = service._extract_json_from_response(response)
        assert result == '[{"type": "experience", "title": "Test"}]'

    def test_extract_json_from_response_with_object_bounds(self):
        """Test JSON extraction using object bounds (wraps in array)."""
        service = MemoryExtractorService(MockLLM(""))
        response = '{"type": "experience", "title": "Test"}'
        result = service._extract_json_from_response(response)
        assert result == '[{"type": "experience", "title": "Test"}]'

    def test_extract_json_from_response_with_conversational_prefix(self):
        """Test JSON extraction with conversational prefix."""
        service = MemoryExtractorService(MockLLM(""))
        response = 'Here is the JSON: [{"type": "experience", "title": "Test"}]'
        result = service._extract_json_from_response(response)
        assert result == '[{"type": "experience", "title": "Test"}]'

    def test_extract_json_from_response_with_conversational_suffix(self):
        """Test JSON extraction with conversational suffix."""
        service = MemoryExtractorService(MockLLM(""))
        response = '[{"type": "experience", "title": "Test"}] I hope this helps.'
        result = service._extract_json_from_response(response)
        assert result == '[{"type": "experience", "title": "Test"}]'

    def test_extract_json_from_response_invalid(self):
        """Test JSON extraction with invalid response."""
        service = MemoryExtractorService(MockLLM(""))
        response = "This is not JSON at all"
        result = service._extract_json_from_response(response)
        assert result is None

    def test_looks_like_json_valid_array(self):
        """Test JSON validation heuristic with valid array."""
        service = MemoryExtractorService(MockLLM(""))
        assert service._looks_like_json("[]")
        assert service._looks_like_json('[{"test": "value"}]')

    def test_looks_like_json_valid_object(self):
        """Test JSON validation heuristic with valid object."""
        service = MemoryExtractorService(MockLLM(""))
        assert service._looks_like_json("{}")
        assert service._looks_like_json('{"test": "value"}')

    def test_looks_like_json_invalid_start(self):
        """Test JSON validation heuristic with invalid start."""
        service = MemoryExtractorService(MockLLM(""))
        assert not service._looks_like_json("not json")
        assert not service._looks_like_json("test []")

    def test_looks_like_json_invalid_end(self):
        """Test JSON validation heuristic with invalid end."""
        service = MemoryExtractorService(MockLLM(""))
        assert not service._looks_like_json("[test")
        assert not service._looks_like_json("{test")

    def test_looks_like_json_unbalanced(self):
        """Test JSON validation heuristic with unbalanced brackets."""
        service = MemoryExtractorService(MockLLM(""))
        assert not service._looks_like_json("[{test}]")
        assert not service._looks_like_json('{"test": [}')

    def test_clean_json_response_removes_prefix(self):
        """Test cleaning conversational prefixes."""
        service = MemoryExtractorService(MockLLM(""))
        response = 'Here is the JSON: [{"test": "value"}]'
        result = service._clean_json_response(response)
        assert result == '[{"test": "value"}]'

    def test_clean_json_response_removes_suffix(self):
        """Test cleaning conversational suffixes."""
        service = MemoryExtractorService(MockLLM(""))
        response = '[{"test": "value"}] I hope this helps.'
        result = service._clean_json_response(response)
        assert result == '[{"test": "value"}]'

    def test_parse_memories_from_response_valid(self):
        """Test parsing valid memory response."""
        service = MemoryExtractorService(MockLLM(""))
        response = '[{"type": "experience", "title": "Test Job", "summary": "A job"}]'
        result = service._parse_memories_from_response(response, "test.pdf")
        assert len(result) == 1
        assert result[0]["type"] == "experience"
        assert result[0]["title"] == "Test Job"
        assert result[0]["source"] == "test.pdf"

    def test_parse_memories_from_response_single_object(self):
        """Test parsing single object (not array)."""
        service = MemoryExtractorService(MockLLM(""))
        response = '{"type": "experience", "title": "Test Job"}'
        result = service._parse_memories_from_response(response)
        assert len(result) == 1
        assert result[0]["type"] == "experience"

    def test_parse_memories_from_response_missing_fields(self):
        """Test parsing with missing required fields (adds defaults)."""
        service = MemoryExtractorService(MockLLM(""))
        response = '[{"title": "Test"}]'
        result = service._parse_memories_from_response(response)
        assert len(result) == 1
        assert result[0]["type"] == "document"  # Default
        assert result[0]["title"] == "Test"
        assert result[0]["importance"] == "medium"  # Default

    def test_parse_memories_from_response_invalid_json(self):
        """Test parsing with invalid JSON."""
        service = MemoryExtractorService(MockLLM(""))
        response = "not valid json"
        result = service._parse_memories_from_response(response)
        assert result == []

    def test_parse_memories_from_response_trailing_comma(self):
        """Test parsing with trailing comma (recovery)."""
        service = MemoryExtractorService(MockLLM(""))
        response = '[{"type": "experience", "title": "Test",},]'
        result = service._parse_memories_from_response(response)
        # Should recover or fail gracefully
        assert isinstance(result, list)

    def test_validate_memory_schema_valid(self):
        """Test validation of valid memory schema."""
        service = MemoryExtractorService(MockLLM(""))
        memory_data = {
            "type": "experience",
            "title": "Test",
            "summary": "A test memory",
            "entities": {
                "people": [],
                "organizations": [],
                "locations": [],
                "skills": [],
            },
            "time": {"start": None, "end": None},
            "importance": "medium",
            "source_documents": [],
        }
        assert service.validate_memory_schema(memory_data) is True

    def test_validate_memory_schema_invalid_type(self):
        """Test validation with invalid memory type."""
        service = MemoryExtractorService(MockLLM(""))
        memory_data = {
            "type": "invalid_type",
            "title": "Test",
            "summary": "A test memory",
            "entities": {
                "people": [],
                "organizations": [],
                "locations": [],
                "skills": [],
            },
            "time": {"start": None, "end": None},
            "importance": "medium",
            "source_documents": [],
        }
        assert service.validate_memory_schema(memory_data) is False

    def test_extract_memories_short_text(self):
        """Test extraction with text too short."""
        llm = MockLLM('[{"type": "experience", "title": "Test"}]')
        service = MemoryExtractorService(llm)
        result = service.extract_memories("short")
        assert result == []

    def test_extract_memories_valid_response(self):
        """Test full extraction with valid LLM response."""
        llm = MockLLM(
            '[{"type": "experience", "title": "ML Internship", "summary": "Worked at ABC", "entities": {"organizations": ["ABC"], "skills": ["Python"]}, "time": {"start": "2025"}, "importance": "high"}]'
        )
        service = MemoryExtractorService(llm)
        result = service.extract_memories("I worked as an ML intern at ABC in 2025.", "resume.pdf")
        assert len(result) == 1
        assert isinstance(result[0], MemorySchema)
        assert result[0].type == "experience"
        assert result[0].title == "ML Internship"
        assert result[0].source == "resume.pdf"

    def test_extract_memories_invalid_json_response(self):
        """Test extraction with invalid LLM JSON response."""
        llm = MockLLM("This is not JSON")
        service = MemoryExtractorService(llm)
        result = service.extract_memories("Some text about work experience.")
        assert result == []

    def test_extract_memories_empty_array(self):
        """Test extraction when LLM returns empty array."""
        llm = MockLLM("[]")
        service = MemoryExtractorService(llm)
        result = service.extract_memories("Some text.")
        assert result == []

    def test_extract_single_memory_valid(self):
        """Test extracting single memory of specific type."""
        llm = MockLLM('{"type": "skill", "title": "Python", "summary": "Programming language"}')
        service = MemoryExtractorService(llm)
        result = service.extract_single_memory("I know Python", "skill", "resume.pdf")
        assert result is not None
        assert isinstance(result, MemorySchema)
        assert result.type == "skill"

    def test_extract_single_memory_invalid(self):
        """Test extracting single memory with invalid response."""
        llm = MockLLM("Not JSON")
        service = MemoryExtractorService(llm)
        result = service.extract_single_memory("Some text", "skill")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
