import time
import logging
import hashlib
import json
from typing import Dict, Any, Optional, Callable
from functools import wraps
from collections import defaultdict
from threading import Lock
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AdaptiveRateLimiter:
    """
    Intelligent rate limiter that adapts to API response patterns without breaking functionality.
    """

    def __init__(
        self,
        base_delay: float = 0.5,
        max_delay: float = 30,
        jitter_factor: float = 0.1,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter_factor = jitter_factor
        
        # Per-endpoint tracking
        self.endpoint_delays = defaultdict(lambda: base_delay)
        self.endpoint_last_request = defaultdict(float)
        self.endpoint_failures = defaultdict(int)
        
        # Request deduplication cache
        self.request_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.cache_lock = Lock()
        
        # Rate limit header tracking
        self.rate_limit_headers = {}
        
    def get_request_hash(self, url: str, payload: str, headers: Dict) -> str:
        """Generate hash for request deduplication."""
        cache_key = f"{url}:{payload}"
        return hashlib.md5(cache_key.encode()).hexdigest()
    
    def check_cache(self, request_hash: str) -> Optional[Dict]:
        """Check if identical request was recently made."""
        with self.cache_lock:
            if request_hash in self.request_cache:
                cached_time, cached_response = self.request_cache[request_hash]
                if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                    logger.debug(f"Cache hit for request {request_hash}")
                    return cached_response
                else:
                    del self.request_cache[request_hash]
            return None
    
    def update_cache(self, request_hash: str, response: Dict):
        """Update request cache."""
        with self.cache_lock:
            self.request_cache[request_hash] = (datetime.now(), response)
    
    def update_from_headers(self, url: str, headers: Dict):
        """Extract rate limit info from response headers."""
        rate_limit_remaining = headers.get("x-rate-limit-remaining")
        rate_limit_reset = headers.get("x-rate-limit-reset")
        retry_after = headers.get("retry-after")
        
        if retry_after:
            delay = int(retry_after)
            self.endpoint_delays[url] = min(delay, self.max_delay)
            logger.warning(f"Rate limited on {url}, delay set to {delay}s")
        
        if rate_limit_remaining and int(rate_limit_remaining) < 5:
            # Approaching limit, increase delay
            current_delay = self.endpoint_delays[url]
            self.endpoint_delays[url] = min(current_delay * 1.5, self.max_delay)
            logger.warning(f"Approaching rate limit on {url}, increased delay")
    
    def calculate_backoff(self, url: str, attempt: int = 0) -> float:
        """Calculate intelligent backoff delay."""
        base = self.endpoint_delays[url]
        exponential = base * (2 ** min(attempt, 5))  # Cap exponential growth
        
        # Add random jitter
        jitter = exponential * self.jitter_factor * (2 * (time.time() % 1) - 1)
        delay = exponential + jitter
        
        return min(delay, self.max_delay)
    
    def wait_for_endpoint(self, url: str):
        """Intelligent wait before hitting endpoint."""
        last_request = self.endpoint_last_request[url]
        time_since_last = time.time() - last_request
        delay = self.endpoint_delays[url]
        
        if time_since_last < delay:
            wait_time = delay - time_since_last
            logger.debug(f"Waiting {wait_time:.2f}s before {url}")
            time.sleep(wait_time)
        
        self.endpoint_last_request[url] = time.time()
    
    def record_failure(self, url: str):
        """Record failure and increase delay."""
        self.endpoint_failures[url] += 1
        failures = self.endpoint_failures[url]
        
        if failures >= 2:
            current_delay = self.endpoint_delays[url]
            new_delay = min(current_delay * 1.3, self.max_delay)
            self.endpoint_delays[url] = new_delay
            logger.warning(f"Failure #{failures} on {url}, delay increased to {new_delay:.2f}s")
    
    def record_success(self, url: str):
        """Record success and gradually decrease delay."""
        self.endpoint_failures[url] = 0
        current_delay = self.endpoint_delays[url]
        
        # Gradually decay back to base delay
        if current_delay > self.base_delay:
            new_delay = max(current_delay * 0.95, self.base_delay)
            self.endpoint_delays[url] = new_delay


# Global rate limiter instance
_rate_limiter = AdaptiveRateLimiter()


def rate_limited(func: Callable) -> Callable:
    """Decorator to apply adaptive rate limiting to any function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract URL from args/kwargs
        url = kwargs.get("url") or (args[1] if len(args) > 1 else "unknown")
        
        # Wait before request
        _rate_limiter.wait_for_endpoint(url)
        
        try:
            result = func(*args, **kwargs)
            
            # Extract headers if available
            if hasattr(result, 'headers'):
                _rate_limiter.update_from_headers(url, result.headers)
            
            _rate_limiter.record_success(url)
            return result
        except Exception as e:
            _rate_limiter.record_failure(url)
            raise
    
    return wrapper


def get_rate_limiter() -> AdaptiveRateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter