import os
from typing import Optional
from whisper_cpp import Whisper
from structured_memory_extractor import MemoryExtractorService
from model_wrapper import LocalLLM


class AudioProcessorService:
    """Service for processing audio files with local Whisper.cpp transcription."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the audio processor service.
        
        Args:
            model_path: Path to Whisper model (default: base.en)
        """
        self.model_path = model_path or os.getenv("WHISPER_MODEL", "base.en")
        self.whisper_model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            self.whisper_model = Whisper(self.model_path)
            print(f"Whisper model loaded: {self.model_path}")
        except Exception as e:
            print(f"Warning: Failed to load Whisper model: {e}")
            self.whisper_model = None
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using local Whisper.cpp.
        
        Args:
            audio_path: Path to audio file (.wav, .mp3)
        
        Returns:
            Transcribed text
        """
        if self.whisper_model is None:
            raise RuntimeError("Whisper model not loaded")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Transcribe audio
            segments = self.whisper_model.transcribe(audio_path, n_threads=4)
            
            # Combine segments into full text
            transcript = ""
            for segment in segments:
                transcript += segment.text + " "
            
            return transcript.strip()
        except Exception as e:
            raise RuntimeError(f"Audio transcription failed: {e}")
    
    def extract_memories(self, transcript: str, source_document: str = None, max_memories: int = 5, llm: Optional[LocalLLM] = None):
        """
        Extract structured memories from audio transcript.
        
        Args:
            transcript: Transcribed text from audio
            source_document: Name of the source audio file
            max_memories: Maximum number of memories to extract
            llm: LocalLLM instance for memory extraction
        
        Returns:
            List of MemorySchema objects
        """
        if not llm:
            raise RuntimeError("LLM is required for memory extraction")
        
        if not transcript or len(transcript) < 50:
            return []
        
        # Use the structured memory extractor
        memory_extractor = MemoryExtractorService(llm)
        memories = memory_extractor.extract_structured_memories(
            transcript,
            source_document=source_document,
            max_memories=max_memories
        )
        
        return memories
    
    def process_audio(self, audio_path: str, source_document: str = None, max_memories: int = 5, llm: Optional[LocalLLM] = None):
        """
        Complete pipeline: transcribe audio and extract memories.
        
        Args:
            audio_path: Path to audio file
            source_document: Name of the source audio file
            max_memories: Maximum number of memories to extract
            llm: LocalLLM instance for memory extraction
        
        Returns:
            Tuple of (transcript, memories)
        """
        # Step 1: Transcribe audio
        transcript = self.transcribe_audio(audio_path)
        
        # Step 2: Extract memories from transcript
        memories = self.extract_memories(transcript, source_document, max_memories, llm)
        
        return transcript, memories
    
    def is_loaded(self) -> bool:
        """Check if Whisper model is loaded."""
        return self.whisper_model is not None
