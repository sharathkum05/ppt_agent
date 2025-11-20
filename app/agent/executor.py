"""Tool executor for the AI agent - executes tool calls and manages state"""
from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError

from app.services.slides_service import SlidesService
from app.services.drive_service import DriveService
from app.config import settings


class AgentState:
    """Manages the agent's state during presentation creation"""
    
    def __init__(self):
        self.presentation_id: Optional[str] = None
        self.presentation_title: Optional[str] = None
        self.slides_created: int = 0
        self.slide_history: List[Dict[str, Any]] = []
    
    def reset(self):
        """Reset the agent state"""
        self.presentation_id = None
        self.presentation_title = None
        self.slides_created = 0
        self.slide_history = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            'presentation_id': self.presentation_id,
            'presentation_title': self.presentation_title,
            'slides_created': self.slides_created,
            'slide_history': self.slide_history
        }


class ToolExecutor:
    """Executes tool calls from the AI agent"""
    
    def __init__(self, slides_service: SlidesService, drive_service: DriveService):
        """
        Initialize the tool executor
        
        Args:
            slides_service: SlidesService instance
            drive_service: DriveService instance
        """
        self.slides_service = slides_service
        self.drive_service = drive_service
        self.state = AgentState()
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call from the agent
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            dict: Tool execution result
        """
        try:
            if tool_name == "create_presentation":
                return self._create_presentation(tool_input)
            elif tool_name == "add_slide":
                return self._add_slide(tool_input)
            elif tool_name == "review_presentation":
                return self._review_presentation(tool_input)
            elif tool_name == "refine_slide":
                return self._refine_slide(tool_input)
            elif tool_name == "finalize_presentation":
                return self._finalize_presentation(tool_input)
            else:
                return {
                    'error': f"Unknown tool: {tool_name}",
                    'success': False
                }
        except Exception as e:
            # Safely convert exception to string, avoiding APIError issues
            from anthropic import APIError
            
            # Check if it's an Anthropic error by module/class name (not isinstance)
            exc_type = type(e)
            exc_module = getattr(exc_type, '__module__', '')
            exc_name = getattr(exc_type, '__name__', 'Unknown')
            
            is_anthropic_error = (
                exc_module == 'anthropic' and 
                ('Error' in exc_name or exc_name.endswith('Error'))
            )
            
            if is_anthropic_error:
                error_msg = "Anthropic API error occurred"
            else:
                try:
                    error_msg = str(e)
                except:
                    error_msg = f"{exc_name}: An error occurred"
            return {
                'error': error_msg,
                'success': False
            }
    
    def _create_presentation(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create_presentation tool - uses existing template and clears it"""
        if not self.state.presentation_id:
            title = tool_input.get('title', 'Untitled Presentation')
            # This will use the hardcoded presentation ID and clear existing slides
            presentation_id = self.slides_service.create_presentation(title)
            
            self.state.presentation_id = presentation_id
            self.state.presentation_title = title
            return {
                'success': True,
                'message': f'Presentation template ready. All existing slides cleared. Ready to add new slides for "{title}"',
                'presentation_id': presentation_id
            }
        else:
            return {
                'success': False,
                'error': f'Presentation already initialized. Current presentation: {self.state.presentation_title}',
                'presentation_id': self.state.presentation_id
            }
    
    def _add_slide(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute add_slide tool"""
        if not self.state.presentation_id:
            return {
                'success': False,
                'error': 'No presentation created yet. Call create_presentation first.'
            }
        
        layout = tool_input.get('layout', 'TITLE_AND_BODY')
        title = tool_input.get('title', '')
        content = tool_input.get('content', '')
        
        result = self.slides_service.add_slide(
            self.state.presentation_id,
            layout,
            title,
            content
        )
        
        if result.get('success'):
            self.state.slides_created += 1
            self.state.slide_history.append({
                'index': self.state.slides_created - 1,
                'layout': layout,
                'title': title,
                'content': content
            })
        
        return result
    
    def _review_presentation(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute review_presentation tool"""
        if not self.state.presentation_id:
            return {
                'success': False,
                'error': 'No presentation created yet. Call create_presentation first.'
            }
        
        try:
            info = self.slides_service.get_presentation_info(self.state.presentation_id)
            return {
                'success': True,
                'presentation_info': info,
                'state': self.state.to_dict()
            }
        except HttpError as e:
            # Safely convert HttpError to string
            try:
                error_msg = str(e)
            except:
                error_msg = f"HttpError: {type(e).__name__}"
            return {
                'success': False,
                'error': f'Failed to review presentation: {error_msg}'
            }
    
    def _refine_slide(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute refine_slide tool"""
        if not self.state.presentation_id:
            return {
                'success': False,
                'error': 'No presentation created yet. Call create_presentation first.'
            }
        
        slide_index = tool_input.get('slide_index')
        new_content = tool_input.get('new_content', '')
        new_title = tool_input.get('new_title')
        
        if slide_index is None:
            return {
                'success': False,
                'error': 'slide_index is required'
            }
        
        try:
            result = self.slides_service.update_slide_content(
                self.state.presentation_id,
                slide_index,
                new_content,
                new_title
            )
            
            # Update state
            if result.get('success') and slide_index < len(self.state.slide_history):
                if new_title:
                    self.state.slide_history[slide_index]['title'] = new_title
                self.state.slide_history[slide_index]['content'] = new_content
            
            return result
        except Exception as e:
            # Safely convert exception to string, avoiding APIError issues
            from anthropic import APIError
            if isinstance(e, APIError):
                error_msg = "Anthropic API error occurred"
            else:
                try:
                    error_msg = str(e)
                except:
                    error_msg = f"{type(e).__name__}: An error occurred"
            return {
                'success': False,
                'error': f'Failed to refine slide: {error_msg}'
            }
    
    def _finalize_presentation(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute finalize_presentation tool"""
        if not self.state.presentation_id:
            return {
                'success': False,
                'error': 'No presentation created yet. Call create_presentation first.'
            }
        
        try:
            shareable_link = self.drive_service.share_and_get_link(self.state.presentation_id)
            return {
                'success': True,
                'message': 'Presentation finalized and shared successfully',
                'presentation_id': self.state.presentation_id,
                'shareable_link': shareable_link,
                'title': self.state.presentation_title,
                'total_slides': self.state.slides_created
            }
        except HttpError as e:
            # Safely convert HttpError to string
            try:
                error_msg = str(e)
            except:
                error_msg = f"HttpError: {type(e).__name__}"
            return {
                'success': False,
                'error': f'Failed to finalize presentation: {error_msg}'
            }
    
    def reset_state(self):
        """Reset the agent state"""
        self.state.reset()

