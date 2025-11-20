"""Safe wrapper for Anthropic API calls that never raises exceptions"""
from typing import Optional, Dict, Any, List
import anthropic
from anthropic import Anthropic


def safe_anthropic_call(
    client: Anthropic,
    messages: List[Dict[str, Any]],
    model: str,
    max_tokens: int = 4096,
    system: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Safely call Anthropic API and return dict or None.
    Never raises exceptions - returns None on any error.
    
    Args:
        client: Anthropic client instance
        messages: List of message dicts
        model: Model name
        max_tokens: Maximum tokens
        system: System prompt (optional)
        tools: Tools list (optional)
        **kwargs: Additional arguments
        
    Returns:
        Dict with response data or None if error occurred
    """
    print("="*50)
    print("SAFE_ANTHROPIC_CALL STARTED")
    print(f"Model: {model}")
    print(f"Messages count: {len(messages)}")
    print("="*50)
    
    try:
        # Build call arguments
        call_kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            **kwargs
        }
        
        if system:
            call_kwargs["system"] = system
        if tools:
            call_kwargs["tools"] = tools
        
        # Make the API call
        print("SAFE_ANTHROPIC_CALL: Making API call...")
        response = client.messages.create(**call_kwargs)
        print("SAFE_ANTHROPIC_CALL: API call successful")
        
        # Extract response data safely
        # Handle both dict and object responses
        if isinstance(response.content, list):
            content = response.content
        else:
            content = getattr(response, 'content', [])
        
        result = {
            "content": content,
            "model": getattr(response, 'model', model),
            "usage": getattr(response, 'usage', None),
            "id": getattr(response, 'id', None),
        }
        
        print("SAFE_ANTHROPIC_CALL: Returning result")
        return result
        
    except Exception as e:
        # Log but don't raise - just return None
        print("="*50)
        print(f"SAFE_ANTHROPIC_CALL CAUGHT: {type(e).__name__}")
        print(f"Module: {type(e).__module__}")
        print("="*50)
        error_type = type(e).__name__
        error_module = type(e).__module__
        print(f"Anthropic API call failed: {error_module}.{error_type}")
        print("SAFE_ANTHROPIC_CALL: Returning None")
        return None

