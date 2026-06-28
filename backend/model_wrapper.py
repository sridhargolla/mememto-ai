import os
from llama_cpp import Llama
from typing import Optional, Iterator
from cache_service import response_cache


class LocalLLM:
    def __init__(self, model_path: str, n_ctx: int = 2048, n_threads: int = 4, lazy_load: bool = False):
        """
        Initialize the local LLM with a GGUF model.
        
        Args:
            model_path: Path to the GGUF model file
            n_ctx: Context window size
            n_threads: Number of threads to use for inference
            lazy_load: If True, model is loaded on first use instead of initialization
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.model: Optional[Llama] = None
        self.lazy_load = lazy_load
        
        if not lazy_load:
            self._load_model()
    
    def _load_model(self):
        """Load the GGUF model into memory."""
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=False
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
        
        Returns:
            Generated text response
        """
        # Check cache first
        cached = response_cache.get(prompt, max_tokens, temperature)
        if cached is not None:
            return cached
        
        if self.model is None:
            if self.lazy_load:
                self._load_model()
            else:
                raise RuntimeError("Model not loaded")
        
        try:
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["User:", "Assistant:", "user:", "assistant:"],
                echo=False
            )
            
            response = output['choices'][0]['text'].strip()
            
            # Cache the response
            response_cache.set(prompt, response, max_tokens, temperature)
            
            return response
        except Exception as e:
            raise RuntimeError(f"Generation failed: {e}")
    
    def generate_stream(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Iterator[str]:
        """
        Generate a response from the model with streaming.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
        
        Yields:
            Generated text tokens one by one
        """
        if self.model is None:
            if self.lazy_load:
                self._load_model()
            else:
                raise RuntimeError("Model not loaded")
        
        try:
            output_stream = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["User:", "Assistant:", "user:", "assistant:"],
                echo=False,
                stream=True
            )
            
            for chunk in output_stream:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    token = chunk['choices'][0].get('text', '')
                    if token:
                        yield token
        except Exception as e:
            raise RuntimeError(f"Streaming generation failed: {e}")
    
    def chat(self, message: str, chat_history: Optional[list] = None) -> str:
        """
        Generate a chat response.
        
        Args:
            message: User message
            chat_history: List of previous messages (optional)
        
        Returns:
            Assistant's response
        """
        # Build prompt with chat history
        prompt = self._build_chat_prompt(message, chat_history)
        
        # Generate response
        response = self.generate(prompt, max_tokens=512, temperature=0.7)
        
        return response
    
    def _build_chat_prompt(self, message: str, chat_history: Optional[list] = None) -> str:
        """
        Build a chat prompt from message and history.
        
        Args:
            message: Current user message
            chat_history: List of previous messages
        
        Returns:
            Formatted prompt string
        """
        prompt = ""
        
        if chat_history:
            for msg in chat_history:
                if msg.get('role') == 'user':
                    prompt += f"User: {msg.get('content')}\n"
                elif msg.get('role') == 'assistant':
                    prompt += f"Assistant: {msg.get('content')}\n"
        
        prompt += f"User: {message}\nAssistant:"
        
        return prompt
