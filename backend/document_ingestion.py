import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from typing import Optional
import tempfile
from structured_memory_extractor import MemoryExtractorService
from audio_processor import AudioProcessorService


class DocumentExtractor:
    """Extract text from various document formats."""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file using PyMuPDF."""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {e}")
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise RuntimeError(f"Failed to read TXT file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to read TXT file: {e}")
    
    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """Extract text from image file using Tesseract OCR."""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {e}")
    
    @staticmethod
    def extract_text(file_path: str, file_type: str, audio_processor: Optional[AudioProcessorService] = None) -> str:
        """
        Extract text from a file based on its type.
        
        Args:
            file_path: Path to the file
            file_type: File type (pdf, txt, png, jpg, jpeg, wav, mp3, etc.)
            audio_processor: AudioProcessorService for audio transcription
        
        Returns:
            Extracted text
        """
        file_typelower = file_type.lower()
        
        if file_typelower == 'pdf':
            return DocumentExtractor.extract_text_from_pdf(file_path)
        elif file_typelower == 'txt':
            return DocumentExtractor.extract_text_from_txt(file_path)
        elif file_typelower in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']:
            return DocumentExtractor.extract_text_from_image(file_path)
        elif file_typelower in ['wav', 'mp3']:
            if audio_processor is None:
                raise RuntimeError("Audio processor required for audio transcription")
            return audio_processor.transcribe_audio(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


class MemoryExtractor:
    """Extract memories from document text using local LLM (legacy wrapper)."""
    
    def __init__(self, llm):
        """
        Initialize memory extractor with local LLM.
        
        Args:
            llm: LocalLLM instance
        """
        self.llm = llm
        self.structured_extractor = MemoryExtractorService(llm)
    
    def extract_memories(self, text: str, source_document: str = None, max_memories: int = 5) -> list:
        """
        Extract key memories from document text using structured extraction.
        
        Args:
            text: Document text
            source_document: Name of the source document
            max_memories: Maximum number of memories to extract
        
        Returns:
            List of extracted memories (title, content, tags, source_document)
        """
        if not text or len(text) < 50:
            return []
        
        try:
            # Use the new structured extractor
            structured_memories = self.structured_extractor.extract_structured_memories(
                text, 
                source_document, 
                max_memories
            )
            
            # Convert to legacy format for backward compatibility
            memories = []
            for memory_schema in structured_memories:
                memories.append({
                    'title': memory_schema.title,
                    'content': memory_schema.summary,
                    'tags': memory_schema.type,
                    'source_document': source_document,
                    'structured_data': memory_schema  # Include full structured data
                })
            
            return memories
            
        except Exception as e:
            print(f"Error extracting memories: {e}")
            return []
    
    def extract_structured_memories(self, text: str, source_document: str = None, max_memories: int = 5) -> list:
        """
        Extract structured memories from document text.
        
        Args:
            text: Document text
            source_document: Name of the source document
            max_memories: Maximum number of memories to extract
        
        Returns:
            List of MemorySchema objects
        """
        return self.structured_extractor.extract_memories(text, source_document, max_memories)
