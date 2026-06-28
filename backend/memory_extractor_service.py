import json
import re
from typing import List, Optional, Dict, Any
from model_wrapper import LocalLLM
from memory_schema import MemorySchema, Entities, TimeInfo


class MemoryExtractorService:
    """Service for extracting structured memories from document text using local LLM."""
    
    def __init__(self, llm: LocalLLM):
        """
        Initialize the memory extractor service.
        
        Args:
            llm: LocalLLM instance for generating extractions
        """
        self.llm = llm
    
    def extract_memories(
        self, 
        text: str, 
        source_document: str = None,
        max_memories: int = 5
    ) -> List[MemorySchema]:
        """
        Extract structured memories from document text.
        
        Args:
            text: Document text to extract memories from
            source_document: Name of the source document
            max_memories: Maximum number of memories to extract
        
        Returns:
            List of structured MemorySchema objects
        """
        if not text or len(text) < 50:
            return []
        
        # Truncate text if too long to avoid context overflow
        truncated_text = text[:3000]
        
        # Generate structured extraction prompt
        prompt = self._build_extraction_prompt(truncated_text, max_memories)
        
        try:
            # Generate response from local LLM
            response = self.llm.generate(
                prompt, 
                max_tokens=1024, 
                temperature=0.3
            )
            
            # Parse and validate JSON response
            memories = self._parse_memories_from_response(response, source_document)
            
            # Validate each memory schema
            validated_memories = []
            for memory_data in memories[:max_memories]:
                try:
                    memory = MemorySchema(**memory_data)
                    validated_memories.append(memory)
                except Exception as e:
                    print(f"Validation error for memory: {e}")
                    continue
            
            return validated_memories
            
        except Exception as e:
            print(f"Error extracting memories: {e}")
            return []
    
    def _build_extraction_prompt(self, text: str, max_memories: int) -> str:
        """
        Build the structured extraction prompt for the LLM.
        
        Args:
            text: Document text
            max_memories: Maximum number of memories to extract
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a memory extraction system. Extract the most important structured memories from the following text.

Extract at most {max_memories} memories. Each memory must follow this exact JSON schema:

{{
  "id": "unique-identifier",
  "type": "person|event|experience|project|education|skill|document",
  "title": "Brief title",
  "summary": "Detailed summary of the memory",
  "entities": {{
    "people": ["person names"],
    "organizations": ["organization names"],
    "locations": ["location names"],
    "skills": ["skill names"]
  }},
  "time": {{
    "start": "start date or null",
    "end": "end date or null"
  }},
  "importance": "low|medium|high",
  "source_documents": ["document name"]
}}

Memory types:
- person: Information about a specific person
- event: A specific event or occurrence
- experience: A personal experience or activity
- project: A project or work endeavor
- education: Educational background or learning
- skill: A skill or competency
- document: General document information

Text to analyze:
{text}

Return ONLY a valid JSON array of memory objects. Do not include any other text or explanation."""
        
        return prompt
    
    def _parse_memories_from_response(
        self, 
        response: str, 
        source_document: str = None
    ) -> List[Dict[str, Any]]:
        """
        Parse the LLM response into structured memory data.
        
        Args:
            response: LLM response text
            source_document: Source document name
        
        Returns:
            List of memory dictionaries
        """
        try:
            # Extract JSON from response (handle potential markdown code blocks)
            json_str = self._extract_json_from_response(response)
            
            if not json_str:
                return []
            
            # Parse JSON
            memories_data = json.loads(json_str)
            
            # Ensure it's a list
            if not isinstance(memories_data, list):
                memories_data = [memories_data]
            
            # Add source document if provided
            if source_document:
                for memory in memories_data:
                    if isinstance(memory, dict):
                        if 'source_documents' not in memory or not memory['source_documents']:
                            memory['source_documents'] = [source_document]
                        elif source_document not in memory['source_documents']:
                            memory['source_documents'].append(source_document)
            
            return memories_data
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []
        except Exception as e:
            print(f"Error parsing memories: {e}")
            return []
    
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """
        Extract JSON string from LLM response, handling markdown code blocks.
        
        Args:
            response: LLM response text
        
        Returns:
            Clean JSON string or None
        """
        # Try to find JSON array in response
        # First, look for markdown code blocks
        json_pattern = r'```json\s*(\[.*?\])\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            return match.group(1)
        
        # Try without json language identifier
        json_pattern = r'```\s*(\[.*?\])\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            return match.group(1)
        
        # Try to find JSON array directly
        json_pattern = r'\[.*\]'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            return match.group(0)
        
        # If no array found, try to find a single JSON object
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            # Wrap single object in array
            return f"[{match.group(0)}]"
        
        return None
    
    def validate_memory_schema(self, memory_data: Dict[str, Any]) -> bool:
        """
        Validate that memory data conforms to the schema.
        
        Args:
            memory_data: Dictionary containing memory data
        
        Returns:
            True if valid, False otherwise
        """
        try:
            MemorySchema(**memory_data)
            return True
        except Exception:
            return False
    
    def extract_single_memory(
        self, 
        text: str, 
        memory_type: str,
        source_document: str = None
    ) -> Optional[MemorySchema]:
        """
        Extract a single memory of a specific type from text.
        
        Args:
            text: Document text
            memory_type: Type of memory to extract
            source_document: Source document name
        
        Returns:
            Single MemorySchema object or None
        """
        prompt = f"""Extract a single memory of type '{memory_type}' from the following text.

Return the memory in this exact JSON format:
{{
  "id": "unique-identifier",
  "type": "{memory_type}",
  "title": "Brief title",
  "summary": "Detailed summary",
  "entities": {{
    "people": [],
    "organizations": [],
    "locations": [],
    "skills": []
  }},
  "time": {{
    "start": null,
    "end": null
  }},
  "importance": "medium",
  "source_documents": ["{source_document or 'unknown'}"]
}}

Text:
{text}

Return ONLY the JSON object, no other text."""
        
        try:
            response = self.llm.generate(prompt, max_tokens=512, temperature=0.3)
            json_str = self._extract_json_from_response(response)
            
            if json_str:
                # Parse as array and take first element
                data = json.loads(json_str)
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                if data:
                    return MemorySchema(**data)
        
        except Exception as e:
            print(f"Error extracting single memory: {e}")
        
        return None
