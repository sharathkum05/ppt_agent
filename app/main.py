"""FastAPI application for AI-powered Google Slides generation"""
import sys
import logging

# MONKEY PATCH: Fix APIError instantiation issue BEFORE importing anything else
# This must be done before any anthropic imports
try:
    import anthropic
    from anthropic import APIError as OriginalAPIError
    
    # Wrapper that handles missing 'request' argument
    class SafeAPIError(OriginalAPIError):
        def __init__(self, *args, **kwargs):
            # If 'request' is missing and not enough args provided, add a dummy request
            if 'request' not in kwargs and len(args) < 2:
                kwargs['request'] = None
            try:
                super().__init__(*args, **kwargs)
            except (TypeError, AttributeError):
                # If it still fails, create a minimal error object
                self.message = str(args[0]) if args else "API Error"
                self.status_code = getattr(kwargs.get('request'), 'status_code', None) or 500
                self.body = kwargs.get('body', {})
    
    # Replace in the module
    anthropic.APIError = SafeAPIError
    sys.modules['anthropic'].APIError = SafeAPIError
    
    # Import the patched version
    from anthropic import APIError, AuthenticationError, NotFoundError, PermissionDeniedError, RateLimitError
except Exception as e:
    # If monkey patch fails, use original imports
    logging.warning(f"Failed to apply APIError monkey patch: {e}")
    from anthropic import APIError, AuthenticationError, NotFoundError, PermissionDeniedError, RateLimitError

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from googleapiclient.errors import HttpError

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

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Google Slides Generator",
    description="AI Agent that generates Google Slides presentations using Anthropic Claude with tool calling",
    version="2.0.0"
)


# CRITICAL: Safe Exception Middleware - catches ALL exceptions BEFORE FastAPI handlers
class SafeExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware that catches all exceptions without touching the exception object"""
    
    async def dispatch(self, request: Request, call_next):
        print("="*50)
        print("MIDDLEWARE STARTED")
        print(f"Request: {request.method} {request.url.path}")
        print("="*50)
        
        try:
            response = await call_next(request)
            print("MIDDLEWARE: Request completed successfully")
            return response
        except Exception as e:
            print("="*50)
            print(f"MIDDLEWARE CAUGHT EXCEPTION: {type(e).__module__}.{type(e).__name__}")
            print("="*50)
            
            # Use sys.exc_info() to get type info without touching the exception
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            if exc_type:
                try:
                    error_module = getattr(exc_type, '__module__', '')
                    error_name = getattr(exc_type, '__name__', 'Unknown')
                except:
                    error_module = 'unknown'
                    error_name = 'Unknown'
                
                print(f"MIDDLEWARE: Exception type: {error_module}.{error_name}")
                
                # Check if it's an Anthropic error by module name
                if 'anthropic' in error_module:
                    print("MIDDLEWARE: Returning Anthropic error response")
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": "CAUGHT BY MIDDLEWARE - Anthropic API request failed",
                            "type": error_name,
                            "detail": "An error occurred while communicating with the AI service"
                        }
                    )
                
                # For HTTPException, try to extract info safely
                if error_name == 'HTTPException':
                    try:
                        status_code = getattr(exc_value, 'status_code', 500) if exc_value else 500
                        detail = getattr(exc_value, 'detail', 'An error occurred') if exc_value else 'An error occurred'
                        print(f"MIDDLEWARE: Returning HTTPException response: {status_code}")
                        return JSONResponse(
                            status_code=status_code,
                            content={
                                "error": f"CAUGHT BY MIDDLEWARE - {detail}",
                                "type": error_name,
                                "detail": None
                            }
                        )
                    except:
                        pass
            
            # Other exceptions - generic response
            print("MIDDLEWARE: Returning generic error response")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "CAUGHT BY MIDDLEWARE - An unexpected error occurred",
                    "type": error_name if exc_type else "Unknown",
                    "detail": None
                }
            )


# Add middleware FIRST - before any routes or handlers
app.add_middleware(SafeExceptionMiddleware)

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


@app.post("/test-exception")
async def test_exception():
    """Test endpoint to verify middleware is working"""
    print("ENDPOINT CALLED: /test-exception")
    raise ValueError("TEST EXCEPTION")

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
    
    # Use sys.exc_info() to safely check exception type without accessing the exception object
    import sys
    import traceback
    
    # Use AI Agent to generate presentation
    # Let all exceptions propagate to FastAPI exception handlers
    result = agent_service.generate_presentation(request.prompt)
    
    # Return response
    return PresentationResponse(
        presentation_id=result["presentation_id"],
        shareable_link=result["shareable_link"],
        title=result["title"],
        slide_count=result["slide_count"]
    )


# REMOVED ALL @app.exception_handler decorators
# The SafeExceptionMiddleware handles all exceptions before they reach FastAPI's handlers

