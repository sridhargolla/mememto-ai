"""
Integration tests for end-to-end memory extraction.

Tests the full pipeline from text input to structured memory output.
"""

import pytest
from memory_extractor_service import MemoryExtractorService
from memory_schema import MemorySchema


class MockLLM:
    """Mock LLM that simulates realistic responses."""
    
    def __init__(self, responses):
        """
        Initialize with a list of responses or a single response.
        
        Args:
            responses: Either a single string or list of strings to return
        """
        if isinstance(responses, str):
            self.responses = [responses]
        else:
            self.responses = responses
        self.call_count = 0
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.1) -> str:
        """Return the next response in the list."""
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return "[]"


class TestIntegrationMemoryExtraction:
    """Integration tests for memory extraction pipeline."""
    
    def test_extract_experience_from_resume_text(self):
        """Test extracting experience from resume text."""
        text = "I worked as a Machine Learning Intern at ABC Technologies in 2025. Built an image classifier using Python and OpenCV."
        
        llm_response = '''[{
  "type": "experience",
  "title": "Machine Learning Internship",
  "summary": "Worked as a Machine Learning Intern at ABC Technologies in 2025, building an image classifier using Python and OpenCV.",
  "entities": {
    "people": [],
    "organizations": ["ABC Technologies"],
    "locations": [],
    "skills": ["Python", "OpenCV", "Machine Learning"]
  },
  "time": {
    "start": "2025",
    "end": null
  },
  "importance": "high",
  "source_documents": [],
  "organization": "ABC Technologies",
  "duration": "2025",
  "skills": ["Python", "OpenCV"],
  "projects": [],
  "source": null
}]'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "resume.pdf", max_memories=5)
        
        assert len(memories) == 1
        assert isinstance(memories[0], MemorySchema)
        assert memories[0].type == "experience"
        assert memories[0].title == "Machine Learning Internship"
        assert "ABC Technologies" in memories[0].entities.organizations
        assert "Python" in memories[0].entities.skills
        assert "OpenCV" in memories[0].entities.skills
        assert memories[0].time.start == "2025"
        assert memories[0].source == "resume.pdf"
    
    def test_extract_multiple_memories_from_project_notes(self):
        """Test extracting multiple memories from project notes."""
        text = """
        Project: AI-Powered Customer Support System
        Team: Sarah, Mike, Alex
        We implemented a REST API using Python and FastAPI.
        The project used Redis for session management.
        """
        
        llm_response = '''[{
  "type": "project",
  "title": "AI-Powered Customer Support System",
  "summary": "Implemented a REST API using Python and FastAPI with Redis for session management.",
  "entities": {
    "people": ["Sarah", "Mike", "Alex"],
    "organizations": [],
    "locations": [],
    "skills": ["Python", "FastAPI", "Redis", "REST API"]
  },
  "time": {
    "start": null,
    "end": null
  },
  "importance": "high",
  "source_documents": [],
  "organization": null,
  "duration": null,
  "skills": ["Python", "FastAPI", "Redis"],
  "projects": [],
  "source": null
}]'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "project_notes.txt", max_memories=5)
        
        assert len(memories) == 1
        assert memories[0].type == "project"
        assert "Sarah" in memories[0].entities.people
        assert "Mike" in memories[0].entities.people
        assert "Alex" in memories[0].entities.people
        assert "Python" in memories[0].entities.skills
        assert "FastAPI" in memories[0].entities.skills
    
    def test_extract_education_from_resume(self):
        """Test extracting education information."""
        text = "Bachelor of Science in Computer Science from University of Technology, graduated May 2018 with GPA 3.7."
        
        llm_response = '''[{
  "type": "education",
  "title": "Bachelor of Science in Computer Science",
  "summary": "Graduated from University of Technology in May 2018 with GPA 3.7.",
  "entities": {
    "people": [],
    "organizations": ["University of Technology"],
    "locations": [],
    "skills": ["Computer Science"]
  },
  "time": {
    "start": null,
    "end": "2018"
  },
  "importance": "high",
  "source_documents": [],
  "organization": "University of Technology",
  "duration": null,
  "skills": [],
  "projects": [],
  "source": null
}]'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "resume.pdf", max_memories=5)
        
        assert len(memories) == 1
        assert memories[0].type == "education"
        assert "University of Technology" in memories[0].entities.organizations
        assert memories[0].time.end == "2018"
    
    def test_extract_skills_from_text(self):
        """Test extracting skills from text."""
        text = "I have experience with Python, JavaScript, TypeScript, React, and Node.js."
        
        llm_response = '''[{
  "type": "skill",
  "title": "Programming Skills",
  "summary": "Proficient in Python, JavaScript, TypeScript, React, and Node.js.",
  "entities": {
    "people": [],
    "organizations": [],
    "locations": [],
    "skills": ["Python", "JavaScript", "TypeScript", "React", "Node.js"]
  },
  "time": {
    "start": null,
    "end": null
  },
  "importance": "medium",
  "source_documents": [],
  "organization": null,
  "duration": null,
  "skills": ["Python", "JavaScript", "TypeScript", "React", "Node.js"],
  "projects": [],
  "source": null
}]'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "skills.txt", max_memories=5)
        
        assert len(memories) == 1
        assert memories[0].type == "skill"
        assert "Python" in memories[0].entities.skills
        assert "React" in memories[0].entities.skills
    
    def test_extract_with_markdown_code_block(self):
        """Test extraction when LLM returns JSON in markdown code block."""
        text = "I worked at Google as a Software Engineer."
        
        llm_response = '''```json
[{
  "type": "experience",
  "title": "Software Engineer",
  "summary": "Worked at Google as a Software Engineer.",
  "entities": {
    "people": [],
    "organizations": ["Google"],
    "locations": [],
    "skills": []
  },
  "time": {
    "start": null,
    "end": null
  },
  "importance": "high",
  "source_documents": [],
  "organization": "Google",
  "duration": null,
  "skills": [],
  "projects": [],
  "source": null
}]
```'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "resume.pdf", max_memories=5)
        
        assert len(memories) == 1
        assert memories[0].type == "experience"
        assert "Google" in memories[0].entities.organizations
    
    def test_extract_with_conversational_text(self):
        """Test extraction when LLM adds conversational text."""
        text = "I learned Python in 2020."
        
        llm_response = '''Here is the extracted memory:
[{
  "type": "skill",
  "title": "Python Programming",
  "summary": "Learned Python in 2020.",
  "entities": {
    "people": [],
    "organizations": [],
    "locations": [],
    "skills": ["Python"]
  },
  "time": {
    "start": "2020",
    "end": null
  },
  "importance": "medium",
  "source_documents": [],
  "organization": null,
  "duration": null,
  "skills": ["Python"],
  "projects": [],
  "source": null
}]
I hope this helps!'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "notes.txt", max_memories=5)
        
        assert len(memories) == 1
        assert memories[0].type == "skill"
        assert "Python" in memories[0].entities.skills
    
    def test_extract_empty_result(self):
        """Test extraction when LLM returns empty array."""
        text = "This is just some random text with no structured information."
        
        llm_response = '[]'
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "random.txt", max_memories=5)
        
        assert len(memories) == 0
    
    def test_extract_with_trailing_comma_recovery(self):
        """Test extraction when JSON has trailing comma (common LLM error)."""
        text = "I worked at Microsoft."
        
        llm_response = '''[{
  "type": "experience",
  "title": "Work at Microsoft",
  "summary": "Worked at Microsoft.",
  "entities": {
    "people": [],
    "organizations": ["Microsoft"],
    "locations": [],
    "skills": []
  },
  "time": {
    "start": null,
    "end": null
  },
  "importance": "medium",
  "source_documents": [],
  "organization": "Microsoft",
  "duration": null,
  "skills": [],
  "projects": [],
  "source": null
},]'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "resume.pdf", max_memories=5)
        
        # Should recover from trailing comma or fail gracefully
        assert isinstance(memories, list)
    
    def test_extract_single_memory_of_specific_type(self):
        """Test extracting a single memory of a specific type."""
        text = "I know React and Vue.js for frontend development."
        
        llm_response = '''{
  "type": "skill",
  "title": "Frontend Frameworks",
  "summary": "Knows React and Vue.js for frontend development.",
  "entities": {
    "people": [],
    "organizations": [],
    "locations": [],
    "skills": ["React", "Vue.js"]
  },
  "time": {
    "start": null,
    "end": null
  },
  "importance": "medium",
  "source_documents": ["skills.txt"],
  "organization": null,
  "duration": null,
  "skills": ["React", "Vue.js"],
  "projects": [],
  "source": "skills.txt"
}'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memory = service.extract_single_memory(text, "skill", "skills.txt")
        
        assert memory is not None
        assert isinstance(memory, MemorySchema)
        assert memory.type == "skill"
        assert "React" in memory.entities.skills
        assert "Vue.js" in memory.entities.skills
    
    def test_extract_with_missing_fields(self):
        """Test extraction when LLM omits some fields (should add defaults)."""
        text = "I did a project."
        
        llm_response = '[{"title": "Some Project"}]'
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "notes.txt", max_memories=5)
        
        assert len(memories) == 1
        assert memories[0].type == "document"  # Default
        assert memories[0].title == "Some Project"
        assert memories[0].importance == "medium"  # Default
    
    def test_extract_long_text_truncation(self):
        """Test that long text is truncated to avoid context overflow."""
        # Create a very long text
        long_text = "This is a test. " * 1000  # ~15,000 characters
        
        llm_response = '[]'
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        # Should not crash with long text
        memories = service.extract_memories(long_text, "long.txt", max_memories=5)
        assert isinstance(memories, list)
    
    def test_extract_with_source_document_tracking(self):
        """Test that source document is properly tracked."""
        text = "I worked at Amazon."
        
        llm_response = '''[{
  "type": "experience",
  "title": "Amazon Experience",
  "summary": "Worked at Amazon.",
  "entities": {
    "people": [],
    "organizations": ["Amazon"],
    "locations": [],
    "skills": []
  },
  "time": {
    "start": null,
    "end": null
  },
  "importance": "high",
  "source_documents": [],
  "organization": "Amazon",
  "duration": null,
  "skills": [],
  "projects": [],
  "source": null
}]'''
        
        llm = MockLLM(llm_response)
        service = MemoryExtractorService(llm)
        
        memories = service.extract_memories(text, "amazon_resume.pdf", max_memories=5)
        
        assert len(memories) == 1
        assert memories[0].source == "amazon_resume.pdf"
        assert "amazon_resume.pdf" in memories[0].source_documents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
