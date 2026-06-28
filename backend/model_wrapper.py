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
        
        # Performance metrics
        self.last_inference_time = 0.0
        self.last_token_count = 0
        self.last_tokens_per_second = 0.0
        self.last_time_to_first_token = 0.0
        
        if not lazy_load:
            self._load_model()
    
    def _load_model(self):
        """Load the GGUF model into memory."""
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=0,  # CRITICAL: Disable GPU offloading, enforce CPU-only AI
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
        import time
        
        # Check cache first
        cached = response_cache.get(prompt, max_tokens, temperature)
        if cached is not None:
            self.last_inference_time = 0.001
            self.last_token_count = len(cached.split())
            self.last_tokens_per_second = self.last_token_count / self.last_inference_time
            return cached
        
        if self.model is None:
            if self.lazy_load:
                self._load_model()
            else:
                raise RuntimeError("Model not loaded")
        
        try:
            start_time = time.perf_counter()
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["User:", "Assistant:", "user:", "assistant:"],
                echo=False
            )
            end_time = time.perf_counter()
            
            response = output['choices'][0]['text'].strip()
            
            # Update metrics
            self.last_inference_time = end_time - start_time
            self.last_token_count = output['usage']['completion_tokens']
            self.last_tokens_per_second = (
                self.last_token_count / self.last_inference_time 
                if self.last_inference_time > 0 else 0.0
            )
            self.last_time_to_first_token = self.last_inference_time  # approximation for non-streaming
            
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
        import time
        
        if self.model is None:
            if self.lazy_load:
                self._load_model()
            else:
                raise RuntimeError("Model not loaded")
        
        try:
            start_time = time.perf_counter()
            first_token_time = None
            token_count = 0
            
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
                        if first_token_time is None:
                            first_token_time = time.perf_counter()
                            self.last_time_to_first_token = first_token_time - start_time
                        
                        token_count += 1
                        yield token
            
            end_time = time.perf_counter()
            
            # Update metrics
            self.last_inference_time = end_time - start_time
            self.last_token_count = token_count
            self.last_tokens_per_second = (
                token_count / self.last_inference_time 
                if self.last_inference_time > 0 else 0.0
            )
            
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

