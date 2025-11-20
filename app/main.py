"""FastAPI application for AI-powered Google Slides generation"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from googleapiclient.errors import HttpError
from anthropic import APIError

from app.config import settings
from app.utils.auth import get_google_services
from app.services.agent_service import AgentService
from app.services.slides_service import SlidesService
from app.services.drive_service import DriveService
from app.models.schemas import (
    PresentationRequest,
    PresentationResponse,
    ErrorResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="AI Google Slides Generator",
    description="AI Agent that generates Google Slides presentations using Anthropic Claude with tool calling",
    version="2.0.0"
)

# Initialize services (will be initialized on first request)
agent_service = None
slides_service = None
drive_service = None


def initialize_services():
    """Initialize Google and Agent services"""
    global agent_service, slides_service, drive_service
    
    try:
        # Validate settings
        settings.validate()
        
        # Initialize Google services
        slides_api, drive_api = get_google_services()
        slides_service = SlidesService(slides_api)
        drive_service = DriveService(drive_api)
        
        # Initialize Agent service (requires Google services)
        agent_service = AgentService(slides_service, drive_service)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize services: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    try:
        initialize_services()
    except Exception as e:
        print(f"Warning: Could not initialize services on startup: {e}")
        print("Services will be initialized on first request")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Google Slides Generator API - Agent-based",
        "version": "2.0.0",
        "architecture": "AI Agent with tool calling",
        "endpoints": {
            "generate_presentation": "/generate-presentation (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if services are initialized
        if agent_service is None or slides_service is None or drive_service is None:
            initialize_services()
        
        return {"status": "healthy", "services": "initialized", "agent": "ready"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/generate-presentation", response_model=PresentationResponse)
async def generate_presentation(request: PresentationRequest):
    """
    Generate a Google Slides presentation from a prompt using AI Agent
    
    The AI agent will:
    1. Reason about the presentation structure
    2. Create the presentation
    3. Add slides one by one
    4. Optionally review and refine
    5. Finalize and share the presentation
    
    Args:
        request: PresentationRequest with user prompt
        
    Returns:
        PresentationResponse with presentation ID, shareable link, title, and slide count
        
    Raises:
        HTTPException: If any step fails
    """
    # Initialize services if not already done
    if agent_service is None or slides_service is None or drive_service is None:
        try:
            initialize_services()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize services: {str(e)}"
            )
    
    try:
        # Use AI Agent to generate presentation
        try:
            result = agent_service.generate_presentation(request.prompt)
        except APIError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Anthropic API error: {str(e)}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Agent error: {str(e)}"
            )
        
        # Return response
        return PresentationResponse(
            presentation_id=result["presentation_id"],
            shareable_link=result["shareable_link"],
            title=result["title"],
            slide_count=result["slide_count"]
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=None
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).dict()
    )

