import json
import re
from typing import List, Optional
from memory_schema import MemorySchema
from model_wrapper import LocalLLM


class MemoryExtractorService:
    """Service for extracting structured memories from text using local LLM."""
    
    def __init__(self, llm: LocalLLM):
        """
        Initialize the memory extractor service.
        
        Args:
            llm: LocalLLM instance for text generation
        """
        self.llm = llm
    
    def extract_structured_memories(self, text: str, source_document: str = None, max_memories: int = 5) -> List[MemorySchema]:
        """
        Extract structured memories from document text.
        
        Args:
            text: Document text to extract memories from
            source_document: Name of the source document
            max_memories: Maximum number of memories to extract
        
        Returns:
            List of MemorySchema objects
        """
        if not text or len(text) < 50:
            return []
        
        prompt = self._build_extraction_prompt(text, max_memories)
        
        try:
            response = self.llm.generate(prompt, max_tokens=1024, temperature=0.5)
            memories = self._parse_structured_response(response, source_document)
            return memories[:max_memories]
        except Exception as e:
            print(f"Error extracting structured memories: {e}")
            return []
    
    def _build_extraction_prompt(self, text: str, max_memories: int) -> str:
        """
        Build the extraction prompt for the LLM.
        
        Args:
            text: Document text
            max_memories: Maximum number of memories to extract
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""Extract the most important memories, facts, or information from the following text. 
For each memory, provide a structured JSON object with the following schema:

{{
    "type": "person|event|experience|project|education|skill|document",
    "title": "Brief title",
    "summary": "Detailed summary",
    "entities": {{
        "people": ["person1", "person2"],
        "organizations": ["org1", "org2"],
        "locations": ["location1", "location2"],
        "skills": ["skill1", "skill2"]
    }},
    "time": {{
        "start": "start time or date",
        "end": "end time or date"
    }},
    "importance": "low|medium|high",
    "source_documents": []
}}

Memory types:
- person: Information about a person
- event: Specific event or occurrence
- experience: Personal experience or achievement
- project: Project or work item
- education: Educational background
- skill: Skill or competency
- document: General document information

Extract at most {max_memories} memories. Return ONLY valid JSON array. No markdown, no code blocks.

Text to analyze:
{text[:3000]}

Response:"""
        return prompt
    
    def _parse_structured_response(self, response: str, source_document: str = None) -> List[MemorySchema]:
        """
        Parse the LLM response into structured MemorySchema objects.
        
        Args:
            response: LLM response text
            source_document: Source document name
        
        Returns:
            List of MemorySchema objects
        """
        memories = []
        
        # Try to extract JSON from response
        json_str = self._extract_json(response)
        
        if not json_str:
            print("No valid JSON found in response")
            return memories
        
        try:
            data = json.loads(json_str)
            
            # Handle both array and single object
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                print("Response is not a valid JSON array or object")
                return memories
            
            for item in data:
                try:
                    # Add source document if provided
                    if source_document:
                        if 'source_documents' not in item:
                            item['source_documents'] = []
                        if source_document not in item['source_documents']:
                            item['source_documents'].append(source_document)
                    
                    # Validate and create MemorySchema
                    memory = MemorySchema(**item)
                    memories.append(memory)
                except Exception as e:
                    print(f"Error parsing memory item: {e}")
                    continue
        
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        
        return memories
    
    def _extract_json(self, text: str) -> Optional[str]:
        """
        Extract JSON string from text, handling various formats.
        
        Args:
            text: Text containing JSON
        
        Returns:
            Extracted JSON string or None
        """
        # Try to find JSON array
        patterns = [
            r'\[.*\]',  # JSON array
            r'\{.*\}',  # JSON object
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue
        
        # Try to find content between ```json and ```
        json_block = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_block:
            try:
                json_str = json_block.group(1)
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                pass
        
        # Try to find content between ``` and ```
        code_block = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if code_block:
            try:
                json_str = code_block.group(1)
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                pass
        
        return None
    
    def validate_memory_schema(self, memory_data: dict) -> bool:
        """
        Validate a memory dictionary against the schema.
        
        Args:
            memory_data: Dictionary to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            MemorySchema(**memory_data)
            return True
        except Exception:
            return False
