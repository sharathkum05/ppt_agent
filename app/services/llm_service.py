"""Anthropic Claude API integration for generating presentation content"""
import json
from typing import Dict, Any
import anthropic
from anthropic import AnthropicError, APIError

from app.config import settings
from app.models.schemas import PresentationStructure


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
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extract text content from response
            content = message.content[0].text if message.content else ""
            
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
        
        except APIError as e:
            raise APIError(f"Anthropic API error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error generating presentation content: {str(e)}")

