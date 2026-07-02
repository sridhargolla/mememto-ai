import os
import pickle

import numpy as np


class EmbeddingService:
    """Service for generating and managing embeddings using local sentence-transformers model."""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the embedding service with a local model."""
        if self._model is None:
            self._load_model()

    def _load_model(self):
        """Load the local sentence-transformers model."""
        # Check if embeddings are disabled, running on Render, or if system RAM is very low (< 1.5 GB)
        disable_embeddings = os.getenv("DISABLE_EMBEDDINGS", "false").lower() == "true"
        on_render = os.getenv("RENDER", "false").lower() == "true"

        if on_render:
            print(
                "Running on Render container environment. Automatically disabling sentence-transformers to save memory."
            )
            disable_embeddings = True

        try:
            import psutil

            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            if total_ram_gb < 1.5:
                print(
                    f"Warning: Low RAM detected ({total_ram_gb:.2f} GB). Disabling sentence-transformers to prevent Out-Of-Memory crashes."
                )
                disable_embeddings = True
        except Exception:
            pass

        if disable_embeddings:
            print(
                "Embedding model loading skipped (disabled or insufficient RAM). Falling back to keyword search."
            )
            self._model = None
            return

        try:
            from sentence_transformers import SentenceTransformer

            # Use a lightweight model that works offline
            model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            self._model = SentenceTransformer(model_name)
            print(f"Embedding model loaded: {model_name}")
        except Exception as e:
            print(f"Warning: Failed to load embedding model: {e}")
            self._model = None

    def generate_embedding(self, text: str) -> np.ndarray | None:
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
