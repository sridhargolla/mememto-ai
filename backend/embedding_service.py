import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional
import os


class EmbeddingService:
    """Service for generating and managing embeddings using local sentence-transformers model."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the embedding service with a local model."""
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the local sentence-transformers model."""
        try:
            # Use a lightweight model that works offline
            model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            self._model = SentenceTransformer(model_name)
            print(f"Embedding model loaded: {model_name}")
        except Exception as e:
            print(f"Warning: Failed to load embedding model: {e}")
            self._model = None
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text to embed
        
        Returns:
            Numpy array of embeddings (384-dim for MiniLM-L6-v2)
        """
        if self._model is None:
            return None
        
        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """
        Serialize numpy array to bytes for database storage.
        
        Args:
            embedding: Numpy array
        
        Returns:
            Serialized bytes
        """
        return pickle.dumps(embedding)
    
    def deserialize_embedding(self, data: bytes) -> np.ndarray:
        """
        Deserialize bytes back to numpy array.
        
        Args:
            data: Serialized bytes
        
        Returns:
            Numpy array
        """
        return pickle.loads(data)
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
        
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        try:
            # Cosine similarity
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def is_loaded(self) -> bool:
        """Check if the embedding model is loaded."""
        return self._model is not None
