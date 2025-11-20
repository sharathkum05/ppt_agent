"""Tool executor for the AI agent - executes tool calls and manages state"""
from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError

from app.services.slides_service import SlidesService
from app.services.drive_service import DriveService


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
            return {
                'error': str(e),
                'success': False
            }
    
    def _create_presentation(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create_presentation tool"""
        if not self.state.presentation_id:
            title = tool_input.get('title', 'Untitled Presentation')
            presentation_id = self.slides_service.create_presentation(title)
            self.state.presentation_id = presentation_id
            self.state.presentation_title = title
            return {
                'success': True,
                'message': f'Presentation "{title}" created successfully',
                'presentation_id': presentation_id
            }
        else:
            return {
                'success': False,
                'error': f'Presentation already created. Current presentation: {self.state.presentation_title}',
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
            return {
                'success': False,
                'error': f'Failed to review presentation: {str(e)}'
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
            return {
                'success': False,
                'error': f'Failed to refine slide: {str(e)}'
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
            return {
                'success': False,
                'error': f'Failed to finalize presentation: {str(e)}'
            }
    
    def reset_state(self):
        """Reset the agent state"""
        self.state.reset()

