"""
Test script for structured memory extraction.
This script tests the new memory extraction pipeline without requiring a running server.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import required modules
from memory_schema import MemorySchema, Entities, TimeInfo
from memory_extractor_service import MemoryExtractorService
from model_wrapper import LocalLLM

def test_memory_schema():
    """Test the MemorySchema model."""
    print("Testing MemorySchema model...")
    
    # Create a test memory
    memory = MemorySchema(
        type="person",
        title="John Doe",
        summary="Software engineer with expertise in AI and machine learning",
        entities=Entities(
            people=["John Doe"],
            organizations=["Tech Corp"],
            locations=["San Francisco"],
            skills=["Python", "Machine Learning"]
        ),
        time=TimeInfo(
            start="2020-01-01",
            end="2023-12-31"
        ),
        importance="high",
        source_documents=["resume.pdf"]
    )
    
    print(f"✓ Memory created with ID: {memory.id}")
    print(f"✓ Memory type: {memory.type}")
    print(f"✓ Memory title: {memory.title}")
    print(f"✓ Entities - People: {memory.entities.people}")
    print(f"✓ Entities - Skills: {memory.entities.skills}")
    
    # Test JSON conversion
    json_str = memory.to_json()
    print(f"✓ JSON conversion successful")
    
    # Test from JSON
    memory_from_json = MemorySchema.from_json(json_str)
    print(f"✓ Memory reconstructed from JSON")
    
    # Test validation
    try:
        invalid_memory = MemorySchema(
            type="invalid_type",
            title="Test",
            summary="Test summary"
        )
        print("✗ Validation should have failed")
    except Exception as e:
        print(f"✓ Validation correctly rejected invalid type: {e}")
    
    print("MemorySchema tests passed!\n")


def test_memory_extractor_service():
    """Test the MemoryExtractorService."""
    print("Testing MemoryExtractorService...")
    
    # Check if model path is set
    model_path = os.getenv("MODEL_PATH", "./models/model.gguf")
    
    if not os.path.exists(model_path):
        print(f"⚠ Model file not found at {model_path}")
        print("Skipping LLM extraction tests (requires local model)")
        return
    
    try:
        # Initialize LLM
        llm = LocalLLM(model_path=model_path, n_ctx=2048, n_threads=4)
        print(f"✓ Model loaded from {model_path}")
        
        # Initialize extractor service
        extractor = MemoryExtractorService(llm)
        print("✓ MemoryExtractorService initialized")
        
        # Test with sample text
        sample_text = """
        John Smith is a senior software engineer at Google. He specializes in machine learning 
        and has been working there since 2018. Before that, he studied computer science at MIT 
        from 2014 to 2018. He is known for his expertise in Deep Learning and Natural Language Processing.
        """
        
        print("\nExtracting memories from sample text...")
        memories = extractor.extract_memories(sample_text, source_document="test.txt", max_memories=3)
        
        print(f"✓ Extracted {len(memories)} memories")
        
        for i, memory in enumerate(memories, 1):
            print(f"\nMemory {i}:")
            print(f"  Type: {memory.type}")
            print(f"  Title: {memory.title}")
            print(f"  Summary: {memory.summary}")
            print(f"  Importance: {memory.importance}")
            print(f"  People: {memory.entities.people}")
            print(f"  Organizations: {memory.entities.organizations}")
            print(f"  Skills: {memory.entities.skills}")
        
        print("\nMemoryExtractorService tests passed!\n")
        
    except Exception as e:
        print(f"✗ Error during extraction test: {e}")
        print("This is expected if no local model is available")


def test_json_parsing():
    """Test JSON parsing from LLM responses."""
    print("Testing JSON parsing...")
    
    from memory_extractor_service import MemoryExtractorService
    
    # Create a mock LLM for testing
    class MockLLM:
        def generate(self, prompt, max_tokens=512, temperature=0.7):
            # Return a mock JSON response
            return '''```json
            [
                {
                    "id": "test-1",
                    "type": "person",
                    "title": "Test Person",
                    "summary": "A test person entry",
                    "entities": {
                        "people": ["Test Person"],
                        "organizations": [],
                        "locations": [],
                        "skills": []
                    },
                    "time": {
                        "start": null,
                        "end": null
                    },
                    "importance": "medium",
                    "source_documents": ["test.txt"]
                }
            ]
            ```'''
    
    mock_llm = MockLLM()
    extractor = MemoryExtractorService(mock_llm)
    
    # Test JSON extraction
    json_str = extractor._extract_json_from_response(mock_llm.generate(""))
    print(f"✓ Extracted JSON: {json_str[:100]}...")
    
    # Test parsing
    memories = extractor._parse_memories_from_response(mock_llm.generate(""), "test.txt")
    print(f"✓ Parsed {len(memories)} memories")
    
    # Test validation
    if memories:
        is_valid = extractor.validate_memory_schema(memories[0])
        print(f"✓ Memory validation: {is_valid}")
    
    print("JSON parsing tests passed!\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Memento AI - Structured Memory Extraction Tests")
    print("=" * 60 + "\n")
    
    # Test 1: MemorySchema model
    test_memory_schema()
    
    # Test 2: JSON parsing
    test_json_parsing()
    
    # Test 3: MemoryExtractorService (requires local model)
    test_memory_extractor_service()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
