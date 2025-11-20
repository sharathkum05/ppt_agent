"""AI Agent service using Anthropic tool use API"""
import json
from typing import List, Dict, Any, Optional
import anthropic
from anthropic import APIError

from app.config import settings
from app.agent.tools import get_tools
from app.agent.executor import ToolExecutor
from app.services.slides_service import SlidesService
from app.services.drive_service import DriveService
from app.utils.anthropic_safe import safe_anthropic_call


class AgentService:
    """AI Agent service that uses Anthropic tool use to create presentations"""
    
    def __init__(self, slides_service: SlidesService, drive_service: DriveService):
        """
        Initialize the agent service
        
        Args:
            slides_service: SlidesService instance
            drive_service: DriveService instance
        """
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.executor = ToolExecutor(slides_service, drive_service)
        self.tools = get_tools()
    
    def generate_presentation(self, user_prompt: str) -> Dict[str, Any]:
        """
        Generate a presentation using the AI agent with tool calling
        
        Args:
            user_prompt: User's prompt describing the presentation
            
        Returns:
            dict: Final result with presentation_id, shareable_link, title, and slide_count
            
        Raises:
            ValueError: If agent fails to complete task or API error occurs
        """
        # Reset executor state
        self.executor.reset_state()
        
        # Let APIError propagate to FastAPI exception handler - don't convert it
        return self._generate_presentation_internal(user_prompt)
    
    def _generate_presentation_internal(self, user_prompt: str) -> Dict[str, Any]:
        """
        Internal method to generate presentation (actual implementation)
        """
        
        # System prompt for the agent
        system_prompt = """You are an expert AI agent that creates Google Slides presentations.

Your task is to:
1. Create a presentation using the create_presentation tool
2. Add slides one by one using the add_slide tool
3. Optionally review the presentation using review_presentation
4. Optionally refine slides using refine_slide if needed
5. Finalize the presentation using finalize_presentation when done

Guidelines:
- Create 5-10 comprehensive slides
- First slide should be a title slide (use TITLE layout)
- Use TITLE_AND_BODY layout for content slides
- Make content informative and well-organized
- Ensure logical flow between slides
- Review your work before finalizing if you want to improve it
- Always call finalize_presentation as your last action

Think step by step and use the tools available to you."""

        # Initialize conversation
        messages: List[Dict[str, Any]] = [
            {
                "role": "user",
                "content": f"Create a presentation about: {user_prompt}"
            }
        ]
        
        iteration = 0
        max_iterations = settings.AGENT_MAX_ITERATIONS
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                # Use safe wrapper - never raises exceptions, returns None on error
                response_data = safe_anthropic_call(
                    client=self.client,
                    messages=messages,
                    model=settings.AGENT_MODEL,
                    max_tokens=4096,
                    system=system_prompt,
                    tools=self.tools
                )
                
                if response_data is None:
                    raise ValueError("Anthropic API error: Unable to process request. Please check your API key and model name.")
                
                # Create a simple response-like object from the dict
                class SimpleResponse:
                    def __init__(self, data):
                        self.content = data.get("content", [])
                        self.model = data.get("model", settings.AGENT_MODEL)
                        self.usage = data.get("usage")
                        self.id = data.get("id")
                
                response = SimpleResponse(response_data)
                
                # Process the response
                for content_block in response.content:
                    if content_block.type == "text":
                        # Agent is providing text response (reasoning or completion)
                        text_content = content_block.text
                        messages.append({
                            "role": "assistant",
                            "content": text_content
                        })
                        
                        # Check if agent says it's done
                        if "finalize" in text_content.lower() or "complete" in text_content.lower():
                            # Agent might be done, but check for tool calls first
                            continue
                    
                    elif content_block.type == "tool_use":
                        # Agent wants to use a tool
                        tool_use = content_block
                        tool_name = tool_use.name
                        tool_input = tool_use.input
                        tool_use_id = tool_use.id
                        
                        # Execute the tool
                        tool_result = self.executor.execute_tool(tool_name, tool_input)
                        
                        # Add tool use and result to conversation
                        messages.append({
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": tool_use_id,
                                    "name": tool_name,
                                    "input": tool_input
                                }
                            ]
                        })
                        
                        messages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": json.dumps(tool_result)
                                }
                            ]
                        })
                        
                        # Check if finalize was called successfully
                        if tool_name == "finalize_presentation" and tool_result.get("success"):
                            # Agent has finalized the presentation
                            return {
                                "presentation_id": tool_result.get("presentation_id"),
                                "shareable_link": tool_result.get("shareable_link"),
                                "title": tool_result.get("title"),
                                "slide_count": tool_result.get("total_slides", 0),
                                "iterations": iteration
                            }
                
                # Check if we should stop (no tool calls in this iteration)
                if not any(block.type == "tool_use" for block in response.content):
                    # Agent might be done reasoning, but hasn't finalized
                    # Give it one more chance or check state
                    if self.executor.state.presentation_id and self.executor.state.slides_created > 0:
                        # Presentation exists but not finalized, prompt agent to finalize
                        messages.append({
                            "role": "user",
                            "content": "Please finalize the presentation using the finalize_presentation tool."
                        })
                        continue
                    else:
                        # No presentation created yet, continue
                        continue
            
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
                    raise ValueError("Anthropic API error: Unable to process request. Please check your API key and model name.")
                else:
                    try:
                        error_msg = str(e)
                    except:
                        error_msg = f"{exc_name}: An error occurred"
                    raise ValueError(f"Error in agent loop on iteration {iteration}: {error_msg}")
        
        # Max iterations reached
        if self.executor.state.presentation_id:
            # Try to finalize what we have
            try:
                finalize_result = self.executor.execute_tool("finalize_presentation", {})
                if finalize_result.get("success"):
                    return {
                        "presentation_id": finalize_result.get("presentation_id"),
                        "shareable_link": finalize_result.get("shareable_link"),
                        "title": finalize_result.get("title"),
                        "slide_count": finalize_result.get("total_slides", 0),
                        "iterations": iteration,
                        "warning": "Max iterations reached, presentation finalized automatically"
                    }
            except Exception:
                pass
        
        raise ValueError(
            f"Agent did not complete the task within {max_iterations} iterations. "
            f"Presentation may be incomplete. State: {self.executor.state.to_dict()}"
        )

