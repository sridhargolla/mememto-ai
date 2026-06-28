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
        Build the structured extraction prompt for the LLM with strong JSON forcing.
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

CRITICAL RULES:
1. Output ONLY a valid JSON array of these objects (wrapped in [ and ]).
2. Do NOT include any conversational text, markdown code blocks (```json), or explanations.
3. Do NOT add any text before or after the JSON array.
4. Ensure all JSON fields are properly double-quoted.
5. Use null for missing values, not empty strings.
6. If no memories can be extracted, return an empty array: []
7. The output must start with [ and end with ]

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
        Parse the LLM response into structured memory data with enhanced error handling.
        """
        try:
            # Extract JSON from response (handle potential markdown code blocks)
            json_str = self._extract_json_from_response(response)
            
            if not json_str:
                print("Failed to extract JSON string from response")
                print(f"Raw response: {response[:500]}...")
                return []
            
            # Parse JSON
            memories_data = json.loads(json_str)
            
            # Ensure it's a list
            if not isinstance(memories_data, list):
                memories_data = [memories_data]
            
            # Validate each memory has required fields
            validated_memories = []
            for memory in memories_data:
                if not isinstance(memory, dict):
                    print(f"Skipping non-dict memory item: {memory}")
                    continue
                
                # Ensure required fields exist
                if 'type' not in memory:
                    memory['type'] = 'document'
                if 'title' not in memory:
                    memory['title'] = 'Untitled Memory'
                if 'summary' not in memory:
                    memory['summary'] = memory.get('title', '')
                if 'importance' not in memory:
                    memory['importance'] = 'medium'
                
                # Ensure nested structures exist
                if 'entities' not in memory or not isinstance(memory['entities'], dict):
                    memory['entities'] = {'people': [], 'organizations': [], 'locations': [], 'skills': []}
                if 'time' not in memory or not isinstance(memory['time'], dict):
                    memory['time'] = {'start': None, 'end': None}
                if 'source_documents' not in memory:
                    memory['source_documents'] = []
                
                # Add source document if provided
                if source_document:
                    if 'source' not in memory or not memory['source']:
                        memory['source'] = source_document
                    if source_document not in memory['source_documents']:
                        memory['source_documents'].append(source_document)
                
                validated_memories.append(memory)
            
            return validated_memories
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Attempting recovery on: {json_str[:500] if json_str else 'None'}...")
            # Try a regex-based recovery for common trailing comma issues
            try:
                # Remove trailing commas before closing braces/brackets
                cleaned = re.sub(r',\s*([\]}])', r'\1', json_str)
                memories_data = json.loads(cleaned)
                if not isinstance(memories_data, list):
                    memories_data = [memories_data]
                # Re-run validation
                return self._parse_memories_from_response(json.dumps(memories_data), source_document)
            except Exception as recovery_error:
                print(f"Recovery failed: {recovery_error}")
                return []
        except Exception as e:
            print(f"Error parsing memories: {e}")
            print(f"Response type: {type(response)}, Length: {len(response) if response else 0}")
            return []
    
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """
        Extract JSON string from LLM response, handling markdown code blocks and raw bounds.
        Enhanced with more robust extraction and validation.
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
            json_str = response_str[start_array:end_array+1]
            # Validate it looks like JSON
            if self._looks_like_json(json_str):
                return json_str
            
        # 4. Look for outer object bounds { ... }
        start_obj = response_str.find('{')
        end_obj = response_str.rfind('}')
        if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
            # Wrap single object in list
            json_str = f"[{response_str[start_obj:end_obj+1]}]"
            if self._looks_like_json(json_str):
                return json_str
            
        # 5. If nothing worked, try to clean the entire response
        cleaned = self._clean_json_response(response_str)
        if cleaned and self._looks_like_json(cleaned):
            return cleaned
            
        return None
    
    def _looks_like_json(self, text: str) -> bool:
        """
        Quick heuristic check if text looks like JSON.
        """
        if not text:
            return False
        text = text.strip()
        # Must start with [ or {
        if not (text.startswith('[') or text.startswith('{')):
            return False
        # Must end with ] or }
        if not (text.endswith(']') or text.endswith('}')):
            return False
        # Basic balance check
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        return open_braces == close_braces and open_brackets == close_brackets
    
    def _clean_json_response(self, response: str) -> Optional[str]:
        """
        Clean common JSON formatting issues from LLM response.
        """
        if not response:
            return None
            
        cleaned = response.strip()
        
        # Remove common conversational prefixes
        prefixes_to_remove = [
            r'^Here is the JSON:?\s*',
            r'^The extracted memories are:?\s*',
            r'^JSON output:?\s*',
            r'^Result:?\s*',
            r'^Output:?\s*',
        ]
        
        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
        
        # Remove trailing conversational text
        suffixes_to_remove = [
            r'\s*Here are the memories\.',
            r'\s*I hope this helps\.',
            r'\s*Let me know if you need anything else\.',
        ]
        
        for suffix in suffixes_to_remove:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        # Extract JSON if embedded in text
        # Find the first [ or { and last ] or }
        first_bracket = cleaned.find('[')
        first_brace = cleaned.find('{')
        
        if first_bracket == -1 and first_brace == -1:
            return None
            
        start = min(first_bracket, first_brace) if first_bracket != -1 and first_brace != -1 else max(first_bracket, first_brace)
        
        if start == first_bracket:
            end = cleaned.rfind(']')
        else:
            end = cleaned.rfind('}')
            
        if end != -1 and end > start:
            return cleaned[start:end+1]
        
        return cleaned
    
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
