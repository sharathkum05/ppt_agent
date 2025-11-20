"""Pydantic models for request/response validation"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class SlideContent(BaseModel):
    """Model for individual slide content"""
    title: str = Field(..., description="Slide title")
    content: str = Field(..., description="Slide content (bullet points or paragraphs)")


class PresentationStructure(BaseModel):
    """Model for complete presentation structure from LLM"""
    title: str = Field(..., description="Presentation title")
    slides: List[SlideContent] = Field(..., description="List of slides")


class PresentationRequest(BaseModel):
    """Request model for presentation generation"""
    prompt: str = Field(..., min_length=1, description="User prompt describing the presentation")


class PresentationResponse(BaseModel):
    """Response model for presentation generation"""
    presentation_id: str = Field(..., description="Google Slides presentation ID")
    shareable_link: str = Field(..., description="Shareable link to the presentation")
    title: str = Field(..., description="Presentation title")
    slide_count: int = Field(..., description="Number of slides created")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


# Agent-specific models
class AgentState(BaseModel):
    """Agent state model"""
    presentation_id: Optional[str] = Field(None, description="Current presentation ID")
    presentation_title: Optional[str] = Field(None, description="Current presentation title")
    slides_created: int = Field(0, description="Number of slides created")
    slide_history: List[Dict] = Field(default_factory=list, description="History of slides created")


class ToolCall(BaseModel):
    """Tool call model"""
    name: str = Field(..., description="Tool name")
    input: dict = Field(..., description="Tool input parameters")


class ToolResult(BaseModel):
    """Tool execution result model"""
    success: bool = Field(..., description="Whether tool execution was successful")
    result: dict = Field(..., description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if execution failed")

