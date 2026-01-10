"""
Rate Limiter Module for EatWise

Provides client-side rate limiting for Azure OpenAI API calls.
Implements a sliding window algorithm with per-user tracking.
"""
import time
import logging
import threading
from typing import Dict, Optional, Tuple
from functools import wraps
from collections import defaultdict
import streamlit as st

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(self, message: str, retry_after: float = 60.0):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter for API calls.
    
    Tracks calls per user with a sliding time window.
    Thread-safe for concurrent access.
    """
    
    def __init__(
        self, 
        max_calls: int = 50,
        window_seconds: int = 60,
        name: str = "api"
    ):
        """
        Initialize the rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed per window
            window_seconds: Size of the sliding window in seconds
            name: Name of this limiter (for logging)
        """
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.name = name
        self._calls: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
    
    def _cleanup_old_calls(self, user_id: str, now: float) -> None:
        """Remove calls outside the current window"""
        cutoff = now - self.window_seconds
        self._calls[user_id] = [
            call_time for call_time in self._calls[user_id] 
            if call_time > cutoff
        ]
    
    def is_allowed(self, user_id: str) -> Tuple[bool, Optional[float]]:
        """
        Check if a call is allowed for the given user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (is_allowed, seconds_until_allowed or None)
        """
        now = time.time()
        
        with self._lock:
            self._cleanup_old_calls(user_id, now)
            
            current_count = len(self._calls[user_id])
            
            if current_count >= self.max_calls:
                # Calculate when the oldest call will expire
                oldest_call = min(self._calls[user_id])
                retry_after = (oldest_call + self.window_seconds) - now
                return False, max(0, retry_after)
            
            return True, None
    
    def record_call(self, user_id: str) -> None:
        """
        Record a successful API call.
        
        Args:
            user_id: User identifier
        """
        now = time.time()
        
        with self._lock:
            self._cleanup_old_calls(user_id, now)
            self._calls[user_id].append(now)
    
    def acquire(self, user_id: str) -> bool:
        """
        Attempt to acquire permission for an API call.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if call is allowed, raises RateLimitExceeded otherwise
        """
        allowed, retry_after = self.is_allowed(user_id)
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for user {user_id} on {self.name}. "
                f"Retry after {retry_after:.1f}s"
            )
            raise RateLimitExceeded(
                f"Too many requests. Please wait {int(retry_after)} seconds.",
                retry_after=retry_after
            )
        
        self.record_call(user_id)
        return True
    
    def get_remaining(self, user_id: str) -> int:
        """
        Get remaining calls for a user in current window.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of remaining calls allowed
        """
        now = time.time()
        
        with self._lock:
            self._cleanup_old_calls(user_id, now)
            current_count = len(self._calls[user_id])
            return max(0, self.max_calls - current_count)
    
    def get_usage_info(self, user_id: str) -> Dict:
        """
        Get detailed usage information for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with usage statistics
        """
        now = time.time()
        
        with self._lock:
            self._cleanup_old_calls(user_id, now)
            current_count = len(self._calls[user_id])
            
            return {
                "used": current_count,
                "remaining": max(0, self.max_calls - current_count),
                "limit": self.max_calls,
                "window_seconds": self.window_seconds,
                "reset_in": self.window_seconds if current_count > 0 else 0
            }
    
    def reset(self, user_id: str = None) -> None:
        """
        Reset rate limit for a user or all users.
        
        Args:
            user_id: User identifier, or None to reset all
        """
        with self._lock:
            if user_id:
                self._calls[user_id] = []
            else:
                self._calls.clear()


# ============================================================================
# Global Rate Limiter Instance
# ============================================================================

# Single shared rate limiter for all AI API calls
# 50 calls per minute per user (Azure OpenAI default is 60 RPM)
ai_rate_limiter = SlidingWindowRateLimiter(
    max_calls=50,
    window_seconds=60,
    name="azure_openai"
)


# ============================================================================
# Decorator for Rate Limited Functions
# ============================================================================

def rate_limited(limiter: SlidingWindowRateLimiter = None, user_id_param: str = None):
    """
    Decorator to apply rate limiting to a function.
    
    Args:
        limiter: Rate limiter instance (defaults to ai_rate_limiter)
        user_id_param: Parameter name that contains user_id, or None to use session state
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the rate limiter
            rl = limiter or ai_rate_limiter
            
            # Get user ID
            user_id = None
            if user_id_param and user_id_param in kwargs:
                user_id = kwargs[user_id_param]
            elif hasattr(st, 'session_state') and 'user_id' in st.session_state:
                user_id = st.session_state.user_id
            else:
                user_id = "anonymous"
            
            # Check rate limit
            try:
                rl.acquire(user_id)
            except RateLimitExceeded as e:
                logger.warning(f"Rate limit blocked call to {func.__name__}")
                return None, e.message
            
            # Call the function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# Helper Functions
# ============================================================================

def check_rate_limit(user_id: str = None) -> Tuple[bool, Optional[str]]:
    """
    Check if a user can make an API call.
    
    Args:
        user_id: User identifier, or None to use session state
        
    Returns:
        Tuple of (is_allowed, error_message or None)
    """
    if user_id is None:
        if hasattr(st, 'session_state') and 'user_id' in st.session_state:
            user_id = st.session_state.user_id
        else:
            user_id = "anonymous"
    
    allowed, retry_after = ai_rate_limiter.is_allowed(user_id)
    
    if not allowed:
        return False, f"Rate limit exceeded. Please wait {int(retry_after)} seconds."
    
    return True, None


def get_rate_limit_status(user_id: str = None) -> Dict:
    """
    Get rate limit status for display in UI.
    
    Args:
        user_id: User identifier, or None to use session state
        
    Returns:
        Dictionary with usage information
    """
    if user_id is None:
        if hasattr(st, 'session_state') and 'user_id' in st.session_state:
            user_id = st.session_state.user_id
        else:
            user_id = "anonymous"
    
    return ai_rate_limiter.get_usage_info(user_id)


def show_rate_limit_warning():
    """Display rate limit warning in Streamlit UI"""
    status = get_rate_limit_status()
    
    if status["remaining"] <= 5:
        st.warning(
            f"⚠️ API rate limit: {status['remaining']}/{status['limit']} requests remaining. "
            f"Resets in {status['reset_in']} seconds."
        )


# ============================================================================
# Context Manager for Rate Limited Blocks
# ============================================================================

class RateLimitContext:
    """
    Context manager for rate-limited code blocks.
    
    Usage:
        with RateLimitContext(user_id) as allowed:
            if allowed:
                # Make API call
                pass
    """
    
    def __init__(self, user_id: str = None, limiter: SlidingWindowRateLimiter = None):
        self.user_id = user_id
        self.limiter = limiter or ai_rate_limiter
        self.allowed = False
        self.error = None
    
    def __enter__(self):
        if self.user_id is None:
            if hasattr(st, 'session_state') and 'user_id' in st.session_state:
                self.user_id = st.session_state.user_id
            else:
                self.user_id = "anonymous"
        
        try:
            self.limiter.acquire(self.user_id)
            self.allowed = True
        except RateLimitExceeded as e:
            self.allowed = False
            self.error = e.message
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Don't suppress exceptions
        return False


# ============================================================================
# Wrapper for API Calls with Error Handling
# ============================================================================

def call_with_rate_limit(
    api_func,
    user_id: str = None,
    on_rate_limit: str = "Too many requests. Please try again in a moment.",
    *args,
    **kwargs
):
    """
    Call an API function with rate limiting.
    
    Args:
        api_func: Function to call
        user_id: User identifier
        on_rate_limit: Message to return if rate limited
        *args, **kwargs: Arguments to pass to api_func
        
    Returns:
        Result of api_func or (None, error_message) if rate limited
    """
    if user_id is None:
        if hasattr(st, 'session_state') and 'user_id' in st.session_state:
            user_id = st.session_state.user_id
        else:
            user_id = "anonymous"
    
    allowed, error = check_rate_limit(user_id)
    
    if not allowed:
        logger.warning(f"Rate limit prevented call: {error}")
        return None, on_rate_limit
    
    # Record the call before making it
    ai_rate_limiter.record_call(user_id)
    
    try:
        result = api_func(*args, **kwargs)
        return result
    except Exception as e:
        # Don't count failed calls against rate limit
        # (This is debatable - you might want to count them)
        logger.error(f"API call failed: {e}")
        raise
