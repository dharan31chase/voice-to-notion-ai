"""
OpenAI Client Singleton with Retry Logic and Rate Limiting
Provides a shared, resilient OpenAI client for all scripts.
"""

import os
import time
import logging
from typing import Optional, Any, Callable
import openai
from openai import OpenAI, RateLimitError, APIError, APIConnectionError, APITimeoutError

logger = logging.getLogger(__name__)

# Retry configuration (industry standard)
MAX_RETRIES = 3
INITIAL_DELAY = 1  # seconds
BACKOFF_MULTIPLIER = 2  # exponential backoff
REQUEST_TIMEOUT = 60  # seconds per request


class ResilientOpenAIClient:
    """
    Singleton OpenAI client with automatic retry logic and rate limiting.
    
    Features:
    - Singleton pattern (one shared instance)
    - Exponential backoff retry (1s → 2s → 4s)
    - HTTP 429 rate limit handling
    - Timeout protection
    - Detailed error logging
    """
    
    _instance: Optional['ResilientOpenAIClient'] = None
    _client: Optional[OpenAI] = None
    
    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the OpenAI client if not already initialized"""
        if self._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                error_msg = (
                    "❌ CRITICAL ERROR: OPENAI_API_KEY not found in environment\n"
                    "   Please add it to your .env file\n"
                    "   Script cannot continue without API access"
                )
                logger.critical(error_msg)
                raise ValueError(error_msg)
            
            self._client = OpenAI(
                api_key=api_key,
                timeout=REQUEST_TIMEOUT,
                max_retries=0  # We handle retries ourselves for better control
            )
            logger.info("✅ OpenAI client initialized successfully")
    
    @property
    def client(self) -> OpenAI:
        """Get the underlying OpenAI client"""
        return self._client
    
    def call_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Call an OpenAI API function with automatic retry logic.
        
        Args:
            func: The API function to call (e.g., client.chat.completions.create)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        
        Returns:
            The API response
        
        Raises:
            Exception: If max retries exceeded or non-retryable error
        """
        last_exception = None
        
        for attempt in range(MAX_RETRIES + 1):  # +1 for initial attempt
            try:
                if attempt > 0:
                    logger.debug(f"Retry attempt {attempt}/{MAX_RETRIES}")
                
                # Call the actual API function
                response = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✅ API call successful after {attempt} retries")
                else:
                    logger.debug("✅ API call successful (first attempt)")
                
                return response
                
            except RateLimitError as e:
                last_exception = e
                
                # Extract retry-after header if available
                retry_after = getattr(e, 'retry_after', None)
                if retry_after:
                    wait_time = int(retry_after)
                    logger.warning(f"⚠️ Rate limit hit (HTTP 429) - Retry-After: {wait_time}s")
                else:
                    wait_time = INITIAL_DELAY * (BACKOFF_MULTIPLIER ** attempt)
                    logger.warning(f"⚠️ Rate limit hit (HTTP 429) - Using exponential backoff: {wait_time}s")
                
                if attempt < MAX_RETRIES:
                    logger.info(f"⏸️ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ Max retries exceeded for rate limit error")
                    raise
            
            except APITimeoutError as e:
                last_exception = e
                wait_time = INITIAL_DELAY * (BACKOFF_MULTIPLIER ** attempt)
                logger.warning(f"⚠️ API timeout after {REQUEST_TIMEOUT}s")
                
                if attempt < MAX_RETRIES:
                    logger.info(f"⏸️ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ Max retries exceeded for timeout error")
                    raise
            
            except APIConnectionError as e:
                last_exception = e
                wait_time = INITIAL_DELAY * (BACKOFF_MULTIPLIER ** attempt)
                logger.warning(f"⚠️ API connection error: {str(e)}")
                
                if attempt < MAX_RETRIES:
                    logger.info(f"⏸️ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ Max retries exceeded for connection error")
                    raise
            
            except APIError as e:
                last_exception = e
                # Some API errors are not retryable (e.g., invalid request)
                if e.status_code and 400 <= e.status_code < 500 and e.status_code != 429:
                    logger.error(f"❌ Non-retryable API error (HTTP {e.status_code}): {str(e)}")
                    raise
                
                # For 5xx errors, retry
                wait_time = INITIAL_DELAY * (BACKOFF_MULTIPLIER ** attempt)
                logger.warning(f"⚠️ API error (HTTP {e.status_code}): {str(e)}")
                
                if attempt < MAX_RETRIES:
                    logger.info(f"⏸️ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ Max retries exceeded for API error")
                    raise
            
            except Exception as e:
                # Unexpected error, don't retry
                logger.error(f"❌ Unexpected error in API call: {str(e)}")
                raise
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise Exception("API call failed after all retries")


# Singleton instance
_resilient_client = None

def get_openai_client() -> OpenAI:
    """
    Get the shared OpenAI client instance.
    
    This function returns the underlying OpenAI client from the singleton.
    For simple use cases, use this directly.
    
    Returns:
        OpenAI: The shared OpenAI client instance
    
    Example:
        client = get_openai_client()
        response = client.chat.completions.create(...)
    """
    global _resilient_client
    if _resilient_client is None:
        _resilient_client = ResilientOpenAIClient()
    return _resilient_client.client


def call_openai_with_retry(func: Callable, *args, **kwargs) -> Any:
    """
    Call an OpenAI API function with automatic retry logic.
    
    This is a convenience function for when you need explicit retry control.
    
    Args:
        func: The API function to call
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        The API response
    
    Example:
        response = call_openai_with_retry(
            client.chat.completions.create,
            model="gpt-4",
            messages=[...]
        )
    """
    global _resilient_client
    if _resilient_client is None:
        _resilient_client = ResilientOpenAIClient()
    return _resilient_client.call_with_retry(func, *args, **kwargs)

