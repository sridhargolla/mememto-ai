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
        if not text or len(text.strip()) < 20:
            return []
        
        # Truncate text if too long to avoid context overflow (CPU-friendly limit)
        truncated_text = text[:3000]
        
        # Generate structured extraction prompt
        prompt = self._build_extraction_prompt(truncated_text, max_memories)
        
        try:
            # Generate response from local LLM with low temperature for deterministic JSON
            response = self.llm.generate(
                prompt, 
                max_tokens=1024, 
                temperature=0.1
            )
            
            # Parse and validate JSON response
            memories_data = self._parse_memories_from_response(response, source_document)
            
            # Validate each memory schema
            validated_memories = []
            for memory_data in memories_data[:max_memories]:
                try:
                    # Clean up fields to match Pydantic expectations
                    if 'entities' not in memory_data:
                        memory_data['entities'] = {}
                    if 'time' not in memory_data:
                        memory_data['time'] = {}
                        
                    # Map flat fields to nested structures if necessary
                    entities_data = memory_data['entities']
                    if not isinstance(entities_data, dict):
                        entities_data = {}
                    
                    # Merge flat skills into entities.skills
                    flat_skills = memory_data.get('skills', [])
                    if flat_skills and isinstance(flat_skills, list):
                        existing_skills = entities_data.get('skills', [])
                        entities_data['skills'] = list(set(existing_skills + flat_skills))
                    
                    # Merge flat organization into entities.organizations
                    flat_org = memory_data.get('organization')
                    if flat_org and isinstance(flat_org, str):
                        existing_orgs = entities_data.get('organizations', [])
                        if flat_org not in existing_orgs:
                            entities_data['organizations'] = existing_orgs + [flat_org]

                    # Map flat duration to time.start
                    flat_duration = memory_data.get('duration')
                    time_data = memory_data['time']
                    if not isinstance(time_data, dict):
                        time_data = {}
                    if flat_duration and not time_data.get('start'):
                        time_data['start'] = str(flat_duration)

                    memory_data['entities'] = entities_data
                    memory_data['time'] = time_data
                    
                    # Create validated Pydantic model
                    memory = MemorySchema(**memory_data)
                    validated_memories.append(memory)
                except Exception as e:
                    print(f"Validation error for memory item: {e}. Item was: {memory_data}")
                    continue
            
            return validated_memories
            
        except Exception as e:
            print(f"Error extracting memories: {e}")
            return []
            
    def extract_structured_memories(self, text: str, source_document: str = None, max_memories: int = 5) -> List[MemorySchema]:
        """Alias for backward compatibility."""
        return self.extract_memories(text, source_document, max_memories)
    
    def _build_extraction_prompt(self, text: str, max_memories: int) -> str:
        """
        Build the structured extraction prompt for the LLM.
        """
        prompt = f"""You are a senior AI memory extraction engine. Analyze the text below and extract at most {max_memories} key structured memories (such as professional experiences, projects, skills, education, people, organizations, or events).

For each extracted memory, you MUST generate a JSON object matching this exact schema:
{{
  "type": "person|event|experience|project|education|skill|document|organization",
  "title": "A concise, descriptive title of this specific memory",
  "summary": "Detailed summary of the memory content",
  "entities": {{
    "people": ["Names of people mentioned"],
    "organizations": ["Organizations mentioned"],
    "locations": ["Locations mentioned"],
    "skills": ["Skills or technologies mentioned"]
  }},
  "time": {{
    "start": "Start date or year (e.g. 2025) or null",
    "end": "End date or year or null"
  }},
  "importance": "low|medium|high",
  "source_documents": [],
  
  "organization": "Organization name associated with this memory (e.g., company or university) or null",
  "duration": "Duration or year (e.g., '2025' or '3 months') or null",
  "skills": ["Key skills/technologies associated with this specific memory"],
  "projects": ["Projects associated with this specific memory"],
  "source": "Source document name or null"
}}

Rules:
1. Output ONLY a valid JSON array of these objects (wrapped in [ and ]).
2. Do NOT include any conversational text, markdown code blocks, or explanations.
3. Ensure all JSON fields are properly double-quoted.

Text to analyze:
---
{text}
---

JSON Output:"""
        return prompt
    
    def _parse_memories_from_response(
        self, 
        response: str, 
        source_document: str = None
    ) -> List[Dict[str, Any]]:
        """
        Parse the LLM response into structured memory data.
        """
        try:
            # Extract JSON from response (handle potential markdown code blocks)
            json_str = self._extract_json_from_response(response)
            
            if not json_str:
                print("Failed to extract JSON string from response")
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
                        # Set source field
                        if 'source' not in memory or not memory['source']:
                            memory['source'] = source_document
                            
                        # Set source_documents list
                        if 'source_documents' not in memory or not memory['source_documents']:
                            memory['source_documents'] = [source_document]
                        elif source_document not in memory['source_documents']:
                            memory['source_documents'].append(source_document)
            
            return memories_data
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}. Raw response was: {response}")
            # Try a regex-based recovery for common trailing comma issues
            try:
                # Remove trailing commas before closing braces/brackets
                cleaned = re.sub(r',\s*([\]}])', r'\1', json_str)
                memories_data = json.loads(cleaned)
                if not isinstance(memories_data, list):
                    memories_data = [memories_data]
                return memories_data
            except:
                return []
        except Exception as e:
            print(f"Error parsing memories: {e}")
            return []
    
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """
        Extract JSON string from LLM response, handling markdown code blocks and raw bounds.
        """
        if not response:
            return None
            
        response_str = response.strip()
        
        # 1. Try to find json block in markdown code fence
        json_block = re.search(r'```json\s*(.*?)\s*```', response_str, re.DOTALL)
        if json_block:
            return json_block.group(1).strip()
            
        # 2. Try to find generic block in markdown code fence
        code_block = re.search(r'```\s*(.*?)\s*```', response_str, re.DOTALL)
        if code_block:
            return code_block.group(1).strip()
            
        # 3. Look for outer array bounds [ ... ]
        start_array = response_str.find('[')
        end_array = response_str.rfind(']')
        if start_array != -1 and end_array != -1 and end_array > start_array:
            return response_str[start_array:end_array+1]
            
        # 4. Look for outer object bounds { ... }
        start_obj = response_str.find('{')
        end_obj = response_str.rfind('}')
        if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
            # Wrap single object in list
            return f"[{response_str[start_obj:end_obj+1]}]"
            
        return response_str
    
    def validate_memory_schema(self, memory_data: Dict[str, Any]) -> bool:
        """
        Validate that memory data conforms to the schema.
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
        """
        prompt = f"""Extract a single memory of type '{memory_type}' from the following text.
        
Return the memory in this exact JSON format:
{{
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
  "source_documents": ["{source_document or 'unknown'}"],
  "organization": null,
  "duration": null,
  "skills": [],
  "projects": [],
  "source": "{source_document or 'unknown'}"
}}

Text:
{text}

Return ONLY the JSON object, no other text."""
        
        try:
            response = self.llm.generate(prompt, max_tokens=512, temperature=0.1)
            json_str = self._extract_json_from_response(response)
            
            if json_str:
                data = json.loads(json_str)
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                
                if isinstance(data, dict):
                    return MemorySchema(**data)
        except Exception as e:
            print(f"Error extracting single memory: {e}")
        
        return None
