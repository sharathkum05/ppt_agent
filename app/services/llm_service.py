"""Anthropic Claude API integration for generating presentation content"""
import json
from typing import Dict, Any
import anthropic
from anthropic import AnthropicError, APIError

from app.config import settings
from app.models.schemas import PresentationStructure
from app.utils.anthropic_safe import safe_anthropic_call


class LLMService:
    """Service for interacting with Anthropic Claude API"""
    
    def __init__(self):
        """Initialize Anthropic client"""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def generate_presentation_content(self, user_prompt: str) -> PresentationStructure:
        """
        Generate presentation structure from user prompt
        
        Args:
            user_prompt: User's prompt describing the presentation
            
        Returns:
            PresentationStructure: Structured presentation content
            
        Raises:
            APIError: If Anthropic API call fails
            ValueError: If response cannot be parsed
        """
        system_prompt = """You are an expert presentation designer. Your task is to create a well-structured presentation based on user prompts.

Generate a JSON response with the following structure:
{
    "title": "Presentation Title",
    "slides": [
        {
            "title": "Slide Title",
            "content": "Slide content with bullet points or paragraphs. Use \\n for line breaks and \\n\\n for paragraph breaks."
        }
    ]
}

Guidelines:
- Create 5-10 slides for a comprehensive presentation
- First slide should be a title slide
- Each slide should have a clear title and relevant content
- Use bullet points or short paragraphs for content
- Make the presentation informative and well-organized
- Ensure content flows logically from slide to slide"""

        user_message = f"""Create a presentation about: {user_prompt}

Please provide the response as valid JSON only, without any markdown formatting or code blocks."""

        try:
            # Use safe wrapper - never raises exceptions, returns None on error
            response_data = safe_anthropic_call(
                client=self.client,
                messages=[{"role": "user", "content": user_message}],
                model="claude-3-haiku-20240307",  # Use working model
                max_tokens=4096,
                system=system_prompt
            )
            
            if response_data is None:
                raise ValueError("Anthropic API error: Unable to process request. Please check your API key.")
            
            # Extract content from response_data
            content_blocks = response_data.get("content", [])
            if not content_blocks:
                raise ValueError("Anthropic API returned empty response")
            
            # Create a simple message-like object
            class SimpleMessage:
                def __init__(self, content_blocks):
                    self.content = [type('ContentBlock', (), {'text': block.get('text', '')})() 
                                   if isinstance(block, dict) else block 
                                   for block in content_blocks]
            
            message = SimpleMessage(content_blocks)
            
            # Extract text content from response
            # Handle both dict and object responses
            if isinstance(message.content, list) and len(message.content) > 0:
                if isinstance(message.content[0], dict):
                    content = message.content[0].get('text', '')
                else:
                    content = getattr(message.content[0], 'text', '')
            else:
                content = ""
            
            # Clean the response (remove markdown code blocks if present)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON response
            try:
                parsed_data = json.loads(content)
                
                # Validate and create PresentationStructure
                return PresentationStructure(**parsed_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {content[:200]}")
        
        except Exception as e:
            # Catch everything from API call and convert to ValueError
            # This prevents APIError from propagating
            # Don't touch the exception object - just convert to ValueError
            exc_type = type(e)
            exc_module = getattr(exc_type, '__module__', '')
            exc_name = getattr(exc_type, '__name__', 'Unknown')
            
            # Check if it's an Anthropic error - NEVER call str() on it
            is_anthropic_error = (
                exc_module == 'anthropic' and 
                ('Error' in exc_name or exc_name.endswith('Error'))
            )
            
            if is_anthropic_error:
                # Don't try to convert to string - just use generic message
                raise ValueError("Anthropic API error: Unable to process request. Please check your API key.")
            else:
                try:
                    error_msg = str(e)
                except:
                    error_msg = f"{exc_name}: An error occurred"
                raise ValueError(f"Unexpected error generating presentation content: {error_msg}")

