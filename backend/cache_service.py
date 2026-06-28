import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import wraps


class ResponseCache:
    """Simple in-memory cache for LLM responses."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize the response cache.
        
        Args:
            max_size: Maximum number of cached responses
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate a cache key from prompt and parameters."""
        key_data = f"{prompt}:{max_tokens}:{temperature}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """
        Get cached response if available and not expired.
        
        Args:
            prompt: Input prompt
            max_tokens: Max tokens used
            temperature: Temperature used
        
        Returns:
            Cached response or None
        """
        key = self._generate_key(prompt, max_tokens, temperature)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if datetime.utcnow() - entry['timestamp'] < self.ttl:
                self.hits += 1
                return entry['response']
            else:
                # Remove expired entry
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, prompt: str, response: str, max_tokens: int = 512, temperature: float = 0.7):
        """
        Cache a response.
        
        Args:
            prompt: Input prompt
            response: Generated response
            max_tokens: Max tokens used
            temperature: Temperature used
        """
        key = self._generate_key(prompt, max_tokens, temperature)
        
        # Evict oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.utcnow()
        }
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


# Global cache instance
response_cache = ResponseCache(max_size=500, ttl_seconds=1800)  # 30 minutes TTL


def cached_response(func):
    """Decorator to cache LLM responses."""
    @wraps(func)
    def wrapper(prompt: str, max_tokens: int = 512, temperature: float = 0.7, *args, **kwargs):
        # Try to get from cache
        cached = response_cache.get(prompt, max_tokens, temperature)
        if cached is not None:
            return cached
        
        # Generate response
        response = func(prompt, max_tokens, temperature, *args, **kwargs)
        
        # Cache the response
        response_cache.set(prompt, response, max_tokens, temperature)
        
        return response
    return wrapper
