"""Google Slides API service for creating presentations"""
from typing import List, Dict, Any, Tuple, Optional
from googleapiclient.errors import HttpError

from app.models.schemas import PresentationStructure, SlideContent
from app.config import settings


class SlidesService:
    """Service for interacting with Google Slides API"""
    
    def __init__(self, slides_service):
        """
        Initialize with authenticated Google Slides service
        
        Args:
            slides_service: Authenticated Google Slides API service object
        """
        self.service = slides_service
    
    def clear_all_slides(self, presentation_id: str) -> None:
        """
        Clear all slides from an existing presentation
        
        Args:
            presentation_id: ID of the presentation
            
        Raises:
            HttpError: If Google API call fails
        """
        try:
            # Get the presentation to find all slide IDs
            presentation = self.service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            slides = presentation.get('slides', [])
            if not slides:
                return  # No slides to delete
            
            # Build delete requests for all slides (delete all, we'll add new ones)
            requests = []
            # Delete slides in reverse order to maintain indices
            for slide in reversed(slides):
                requests.append({
                    'deleteObject': {
                        'objectId': slide.get('objectId')
                    }
                })
            
            # Execute delete requests
            if requests:
                body = {'requests': requests}
                self.service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body=body
                ).execute()
                    
        except HttpError as error:
            raise error
    
    def create_presentation(self, title: str) -> str:
        """
        Use existing presentation template and clear it for new content
        
        Args:
            title: Title for the presentation (used for reference, not to rename)
            
        Returns:
            str: Presentation ID of the existing template
            
        Raises:
            HttpError: If Google API call fails
        """
        from app.config import settings
        
        try:
            presentation_id = settings.DEFAULT_PRESENTATION_ID
            
            # Clear all existing slides
            self.clear_all_slides(presentation_id)
            
            return presentation_id
        except HttpError as error:
            raise error
    
    def add_slides_with_content(self, presentation_id: str, presentation_structure: PresentationStructure) -> int:
        """
        Add slides with content to the presentation
        
        Args:
            presentation_id: ID of the presentation
            presentation_structure: Structured presentation content
            
        Returns:
            int: Number of slides created
            
        Raises:
            HttpError: If Google API call fails
        """
        requests = []
        
        # First, create title slide
        if presentation_structure.slides:
            title_slide = presentation_structure.slides[0]
            requests.append({
                'createSlide': {
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE'
                    },
                    'placeholderIdMappings': [
                        {
                            'objectId': 'title_slide_title',
                            'layoutPlaceholder': {
                                'type': 'TITLE',
                                'index': 0
                            }
                        }
                    ]
                }
            })
            
            requests.append({
                'insertText': {
                    'objectId': 'title_slide_title',
                    'text': presentation_structure.title
                }
            })
            
            # Add subtitle if available
            if title_slide.content:
                requests.append({
                    'createParagraphBullets': {
                        'objectId': 'title_slide_title',
                        'textRange': {
                            'type': 'ALL'
                        },
                        'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                    }
                })
            
            # Add content slides
            for i, slide in enumerate(presentation_structure.slides[1:], start=1):
                # Generate unique object IDs for each slide
                slide_title_id = f'slide_title_{i}'
                slide_body_id = f'slide_body_{i}'
                
                # Create slide with TITLE_AND_BODY layout
                requests.append({
                    'createSlide': {
                        'slideLayoutReference': {
                            'predefinedLayout': 'TITLE_AND_BODY'
                        },
                        'placeholderIdMappings': [
                            {
                                'objectId': slide_title_id,
                                'layoutPlaceholder': {
                                    'type': 'TITLE',
                                    'index': 0
                                }
                            },
                            {
                                'objectId': slide_body_id,
                                'layoutPlaceholder': {
                                    'type': 'BODY',
                                    'index': 0
                                }
                            }
                        ]
                    }
                })
                
                # Insert title
                requests.append({
                    'insertText': {
                        'objectId': slide_title_id,
                        'text': slide.title
                    }
                })
                
                # Insert body content
                if slide.content:
                    # Format content - handle line breaks
                    content = slide.content.replace('\\n', '\n')
                    requests.append({
                        'insertText': {
                            'objectId': slide_body_id,
                            'text': content
                        }
                    })
            
            # Execute batch update
            try:
                body = {'requests': requests}
                self.service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body=body
                ).execute()
                
                return len(presentation_structure.slides)
            
            except HttpError as error:
                raise HttpError(
                    f"Failed to add slides: {error.resp.status} - {error.content}",
                    error.resp
                )
        else:
            raise ValueError("No slides to add to presentation")
    
    def create_presentation_with_content(self, presentation_structure: PresentationStructure) -> Tuple[str, int]:
        """
        Create a presentation and add all slides with content
        
        Args:
            presentation_structure: Structured presentation content
            
        Returns:
            tuple[str, int]: Presentation ID and number of slides created
            
        Raises:
            HttpError: If Google API call fails
        """
        presentation_id = self.create_presentation(presentation_structure.title)
        slide_count = self.add_slides_with_content(presentation_id, presentation_structure)
        
        return presentation_id, slide_count
    
    def add_slide(self, presentation_id: str, layout: str, title: str, content: str) -> Dict[str, Any]:
        """
        Add a single slide to the presentation (for agent use)
        
        Args:
            presentation_id: ID of the presentation
            layout: Layout type (TITLE, TITLE_AND_BODY, etc.)
            title: Slide title
            content: Slide content
            
        Returns:
            dict: Information about the created slide
            
        Raises:
            HttpError: If Google API call fails
        """
        import re
        import time
        
        # Generate valid object IDs (must start with word char, only [a-zA-Z0-9_-:])
        # Use timestamp and sanitize title
        timestamp = int(time.time() * 1000) % 1000000  # Use last 6 digits of timestamp
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title[:10])  # Replace invalid chars with underscore
        slide_title_id = f'slide_title_{layout}_{timestamp}_{safe_title}'
        slide_body_id = f'slide_body_{layout}_{timestamp}_{safe_title}'
        
        requests = []
        
        # Create slide based on layout
        placeholder_mappings = []
        
        if layout == "TITLE":
            placeholder_mappings.append({
                'objectId': slide_title_id,
                'layoutPlaceholder': {
                    'type': 'TITLE',
                    'index': 0
                }
            })
        elif layout in ["TITLE_AND_BODY", "TITLE_AND_TWO_COLUMNS"]:
            placeholder_mappings.extend([
                {
                    'objectId': slide_title_id,
                    'layoutPlaceholder': {
                        'type': 'TITLE',
                        'index': 0
                    }
                },
                {
                    'objectId': slide_body_id,
                    'layoutPlaceholder': {
                        'type': 'BODY',
                        'index': 0
                    }
                }
            ])
        else:  # BLANK layout
            placeholder_mappings.append({
                'objectId': slide_title_id,
                'layoutPlaceholder': {
                    'type': 'TITLE',
                    'index': 0
                }
            })
        
        requests.append({
            'createSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': layout
                },
                'placeholderIdMappings': placeholder_mappings
            }
        })
        
        # Insert title
        requests.append({
            'insertText': {
                'objectId': slide_title_id,
                'text': title
            }
        })
        
        # Insert content if body exists
        if layout in ["TITLE_AND_BODY", "TITLE_AND_TWO_COLUMNS"] and content:
            content_formatted = content.replace('\\n', '\n')
            requests.append({
                'insertText': {
                    'objectId': slide_body_id,
                    'text': content_formatted
                }
            })
        
        try:
            body = {'requests': requests}
            response = self.service.presentations().batchUpdate(
                presentationId=presentation_id,
                body=body
            ).execute()
            
            # Get the created slide ID from response
            slide_id = None
            if response.get('replies'):
                for reply in response['replies']:
                    if 'createSlide' in reply:
                        slide_id = reply['createSlide'].get('objectId')
                        break
            
            return {
                'success': True,
                'slide_id': slide_id,
                'layout': layout,
                'title': title
            }
        except HttpError as error:
            # Re-raise the original error properly
            raise error
    
    def get_presentation_info(self, presentation_id: str) -> Dict[str, Any]:
        """
        Get information about the presentation and all slides (for agent review)
        
        Args:
            presentation_id: ID of the presentation
            
        Returns:
            dict: Presentation information including all slides
            
        Raises:
            HttpError: If Google API call fails
        """
        try:
            presentation = self.service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            slides_info = []
            slides = presentation.get('slides', [])
            
            for idx, slide in enumerate(slides):
                slide_data = {
                    'index': idx,
                    'slide_id': slide.get('objectId'),
                    'layout': slide.get('slideProperties', {}).get('layoutObjectId', 'unknown')
                }
                
                # Try to extract text from page elements
                page_elements = slide.get('pageElements', [])
                title_text = ""
                body_text = ""
                
                for element in page_elements:
                    shape = element.get('shape', {})
                    text = shape.get('text', {})
                    text_elements = text.get('textElements', [])
                    
                    for text_elem in text_elements:
                        if 'textRun' in text_elem:
                            text_content = text_elem['textRun'].get('content', '')
                            # Heuristic: first text is usually title
                            if not title_text:
                                title_text = text_content.strip()
                            else:
                                body_text += text_content
                
                slide_data['title'] = title_text
                slide_data['content'] = body_text.strip()
                slides_info.append(slide_data)
            
            return {
                'presentation_id': presentation_id,
                'title': presentation.get('title', ''),
                'total_slides': len(slides),
                'slides': slides_info
            }
        except HttpError as error:
            raise HttpError(
                f"Failed to get presentation info: {error.resp.status} - {error.content}",
                error.resp
            )
    
    def update_slide_content(self, presentation_id: str, slide_index: int, new_content: str, new_title: str = None) -> Dict[str, Any]:
        """
        Update the content of an existing slide (for agent refinement)
        
        Args:
            presentation_id: ID of the presentation
            slide_index: Index of the slide to update (0-based)
            new_content: New content for the slide
            new_title: Optional new title for the slide
            
        Returns:
            dict: Update result
            
        Raises:
            HttpError: If Google API call fails
        """
        try:
            # First, get the presentation to find the slide
            presentation = self.service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            slides = presentation.get('slides', [])
            if slide_index >= len(slides):
                raise ValueError(f"Slide index {slide_index} out of range. Presentation has {len(slides)} slides.")
            
            slide = slides[slide_index]
            slide_id = slide.get('objectId')
            
            requests = []
            
            # Find text elements in the slide
            page_elements = slide.get('pageElements', [])
            title_element_id = None
            body_element_id = None
            
            for element in page_elements:
                shape = element.get('shape', {})
                if shape.get('shapeType') == 'TEXT_BOX':
                    # Try to identify title vs body by position or properties
                    # Simple heuristic: first element is usually title
                    if not title_element_id:
                        title_element_id = element.get('objectId')
                    else:
                        body_element_id = element.get('objectId')
            
            # Update title if provided
            if new_title and title_element_id:
                requests.append({
                    'deleteText': {
                        'objectId': title_element_id,
                        'textRange': {
                            'type': 'ALL'
                        }
                    }
                })
                requests.append({
                    'insertText': {
                        'objectId': title_element_id,
                        'text': new_title
                    }
                })
            
            # Update content
            if new_content and body_element_id:
                requests.append({
                    'deleteText': {
                        'objectId': body_element_id,
                        'textRange': {
                            'type': 'ALL'
                        }
                    }
                })
                content_formatted = new_content.replace('\\n', '\n')
                requests.append({
                    'insertText': {
                        'objectId': body_element_id,
                        'text': content_formatted
                    }
                })
            
            if requests:
                body = {'requests': requests}
                self.service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body=body
                ).execute()
            
            return {
                'success': True,
                'slide_index': slide_index,
                'message': 'Slide updated successfully'
            }
        except HttpError as error:
            raise HttpError(
                f"Failed to update slide: {error.resp.status} - {error.content}",
                error.resp
            )

