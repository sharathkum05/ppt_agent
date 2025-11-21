"""FastAPI application for AI-powered Google Slides generation"""
import sys
import logging
import os

# Configure logging FIRST to catch any errors
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Try to import and setup everything safely
try:
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
        logger.warning(f"Failed to apply APIError monkey patch: {e}")
        try:
            from anthropic import APIError, AuthenticationError, NotFoundError, PermissionDeniedError, RateLimitError
        except ImportError:
            # If anthropic is not available, create dummy classes
            class APIError(Exception): pass
            class AuthenticationError(Exception): pass
            class NotFoundError(Exception): pass
            class PermissionDeniedError(Exception): pass
            class RateLimitError(Exception): pass

    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware
    from googleapiclient.errors import HttpError

    # Import app modules - wrap in try-except to prevent crashes
    # DO NOT re-raise - we need the app to start even if some imports fail
    import_error = None
    try:
        from app.config import settings
    except Exception as e:
        logger.error(f"Failed to import app.config: {e}", exc_info=True)
        import_error = e
    
    try:
        from app.utils.auth import get_google_services
    except Exception as e:
        logger.error(f"Failed to import app.utils.auth: {e}", exc_info=True)
        if not import_error:
            import_error = e
    
    try:
        from app.services.agent_service import AgentService
        from app.services.slides_service import SlidesService
        from app.services.drive_service import DriveService
    except Exception as e:
        logger.error(f"Failed to import services: {e}", exc_info=True)
        if not import_error:
            import_error = e
    
    try:
        from app.models.schemas import (
            PresentationRequest,
            PresentationResponse,
            ErrorResponse
        )
    except Exception as e:
        logger.error(f"Failed to import schemas: {e}", exc_info=True)
        if not import_error:
            import_error = e

    # If we had import errors, log them but continue
    if import_error:
        logger.warning(f"Some imports failed, but continuing: {import_error}")

except Exception as e:
    # If ANY import fails, we need to handle it gracefully
    # But we can't import FastAPI if it failed above, so we need a different approach
    import traceback
    error_trace = traceback.format_exc()
    logger.error(f"CRITICAL: Failed to import required modules: {e}\n{error_trace}")
    
    # Try to create minimal app anyway - if FastAPI import failed, this will fail too
    # but at least we'll have better error messages
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        app = FastAPI(title="Error", version="1.0.0")
        
        @app.get("/")
        async def error_root():
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Application failed to start",
                    "detail": str(e),
                    "type": type(e).__name__,
                    "message": "Check Vercel logs for full traceback"
                }
            )
    except Exception as import_error:
        # If we can't even create a minimal app, we're in serious trouble
        logger.error(f"CRITICAL: Cannot create minimal app: {import_error}")
        # Create a dummy app object so handler can be created
        class DummyApp:
            pass
        app = DummyApp()
    
    # Try to create handler anyway
    handler = None
    try:
        from mangum import Mangum
        handler = Mangum(app, lifespan="off")
    except:
        pass
    
    # DO NOT re-raise - we need handler to be defined
    # Log the error but continue so handler can be created
    logger.error(f"Import failed but continuing to create handler: {e}")

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
        print("✅ Services initialized successfully")
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"❌ Failed to initialize services: {error_type}: {error_msg}")
        # Re-raise with more context
        raise ValueError(f"Service initialization failed: {error_type}: {error_msg}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    # Don't initialize on startup for serverless - initialize on first request instead
    # This prevents cold start failures if env vars are missing
    print("FastAPI app started. Services will be initialized on first request.")


@app.get("/")
async def root():
    """Root endpoint - simple health check without initialization"""
    return {
        "status": "ok",
        "message": "AI Google Slides Generator API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "generate": "/generate-presentation (POST)",
            "debug": "/debug/env"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if services are initialized
        if agent_service is None or slides_service is None or drive_service is None:
            try:
                initialize_services()
            except Exception as init_error:
                # Return detailed error for debugging
                error_msg = str(init_error)
                error_type = type(init_error).__name__
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "error": error_msg,
                        "error_type": error_type,
                        "message": "Failed to initialize services. Check environment variables.",
                        "hint": "Visit /debug/env to check which environment variables are set"
                    }
                )
        
        return {"status": "healthy", "services": "initialized", "agent": "ready"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "hint": "Visit /debug/env to check which environment variables are set"
            }
        )


@app.post("/test-exception")
async def test_exception():
    """Test endpoint to verify middleware is working"""
    print("ENDPOINT CALLED: /test-exception")
    raise ValueError("TEST EXCEPTION")


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (without exposing sensitive data)"""
    import os
    
    # Check all possible environment variable names
    def check_var(*names):
        """Check if any of the given variable names are set"""
        for name in names:
            value = os.getenv(name)
            if value:
                return "SET", len(value) if value else 0
        return "MISSING", 0
    
    def get_var(*names, default="MISSING"):
        """Get value of first found variable, or default"""
        for name in names:
            value = os.getenv(name)
            if value:
                return value
        return default
    
    env_status = {
        "anthropic": {
            "ANTHROPIC_API_KEY": check_var("ANTHROPIC_API_KEY"),
        },
        "google_credentials": {
            "project_id": check_var("GOOGLE_PROJECT_ID", "project_id"),
            "private_key": check_var("GOOGLE_PRIVATE_KEY", "private_key"),
            "client_email": check_var("GOOGLE_CLIENT_EMAIL", "client_email"),
            "token_uri": check_var("GOOGLE_TOKEN_URI", "token_uri"),
            "private_key_id": check_var("GOOGLE_PRIVATE_KEY_ID", "private_key_id"),
            "client_id": check_var("GOOGLE_CLIENT_ID", "client_id"),
            "auth_uri": check_var("GOOGLE_AUTH_URI", "auth_uri"),
            "auth_provider_x509_cert_url": check_var("GOOGLE_AUTH_PROVIDER_X509_CERT_URL", "auth_provider_x509_cert_url"),
            "client_x509_cert_url": check_var("GOOGLE_CLIENT_X509_CERT_URL", "client_x509_cert_url"),
            "universe_domain": check_var("GOOGLE_UNIVERSE_DOMAIN", "universe_domain"),
        },
        "application": {
            "DEFAULT_PRESENTATION_ID": get_var("DEFAULT_PRESENTATION_ID"),
            "GOOGLE_DRIVE_FOLDER_ID": get_var("GOOGLE_DRIVE_FOLDER_ID"),
            "AGENT_MODEL": get_var("AGENT_MODEL", default="claude-3-5-sonnet-20241022"),
            "AGENT_MAX_ITERATIONS": get_var("AGENT_MAX_ITERATIONS", default="20"),
        },
        "validation": {
            "using_env_vars": settings.is_using_env_vars(),
            "validation_errors": []
        }
    }
    
    # Try to validate and capture errors
    try:
        settings.validate()
        env_status["validation"]["status"] = "PASSED"
    except Exception as e:
        env_status["validation"]["status"] = "FAILED"
        env_status["validation"]["validation_errors"] = str(e)
    
    # Count missing required vars
    missing_required = []
    if env_status["anthropic"]["ANTHROPIC_API_KEY"][0] == "MISSING":
        missing_required.append("ANTHROPIC_API_KEY")
    
    if env_status["validation"]["using_env_vars"]:
        if env_status["google_credentials"]["project_id"][0] == "MISSING":
            missing_required.append("GOOGLE_PROJECT_ID or project_id")
        if env_status["google_credentials"]["private_key"][0] == "MISSING":
            missing_required.append("GOOGLE_PRIVATE_KEY or private_key")
        if env_status["google_credentials"]["client_email"][0] == "MISSING":
            missing_required.append("GOOGLE_CLIENT_EMAIL or client_email")
        if env_status["google_credentials"]["token_uri"][0] == "MISSING":
            missing_required.append("GOOGLE_TOKEN_URI or token_uri")
    
    env_status["summary"] = {
        "total_checked": len(env_status["anthropic"]) + len(env_status["google_credentials"]) + len(env_status["application"]),
        "missing_required": missing_required,
        "all_required_set": len(missing_required) == 0
    }
    
    return env_status

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
            error_msg = str(e)
            error_type = type(e).__name__
            print(f"❌ Service initialization error in endpoint: {error_type}: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize services: {error_msg}. Please check environment variables and Vercel logs."
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

# Vercel serverless handler - MUST be at module level and always defined
# This is critical - Vercel's @vercel/python looks for 'handler' variable
# The handler must be a Mangum instance wrapping the FastAPI app
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")  # Disable lifespan for serverless
    logger.info("✅ Mangum handler initialized for Vercel")
except ImportError as e:
    logger.error(f"CRITICAL: Mangum not available: {e}")
    # Create a minimal Mangum-like wrapper
    # Vercel requires handler to exist, so we create a basic one
    from mangum import Mangum
    # If we get here, Mangum should be installed, but just in case...
    handler = None
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize Mangum handler: {e}", exc_info=True)
    handler = None

# CRITICAL: Handler MUST be defined for Vercel
if handler is None:
    logger.error("CRITICAL: Handler is None - attempting to create minimal handler")
    try:
        from mangum import Mangum
        handler = Mangum(app, lifespan="off")
        logger.info("✅ Created Mangum handler as fallback")
    except Exception as e:
        logger.error(f"CRITICAL: Cannot create handler: {e}", exc_info=True)
        # Last resort - export app directly (Vercel might handle it)
        handler = app

# Serve React frontend (after building with: cd ppt-agent-frontend && npm run build)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Check if frontend build exists
FRONTEND_BUILD_PATH = os.path.join(os.path.dirname(__file__), "..", "ppt-agent-frontend", "dist")
FRONTEND_INDEX_PATH = os.path.join(FRONTEND_BUILD_PATH, "index.html")

if os.path.exists(FRONTEND_BUILD_PATH):
    # Serve static assets (must be before catch-all route)
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_BUILD_PATH, "assets")), name="assets")
    
    # Serve frontend for root route (must be AFTER all API routes are defined)
    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        if os.path.exists(FRONTEND_INDEX_PATH):
            return FileResponse(FRONTEND_INDEX_PATH)
        return {"message": "Frontend not built. Run: cd ppt-agent-frontend && npm run build"}
    
    # Catch-all route for React Router (must be last, after all API routes)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def catch_all(full_path: str):
        # Don't catch root, API routes, or static assets
        if (full_path == "" or
            full_path == "docs" or 
            full_path == "openapi.json" or
            full_path.startswith("api/") or 
            full_path.startswith("generate-presentation") or 
            full_path.startswith("health") or
            full_path.startswith("debug") or
            full_path.startswith("test-exception") or
            full_path.startswith("assets/") or
            full_path.startswith("docs/") or
            full_path.startswith("redoc")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve React app for all other routes
        if os.path.exists(FRONTEND_INDEX_PATH):
            return FileResponse(FRONTEND_INDEX_PATH)
        return {"message": "Frontend not built"}
else:
    # Frontend build doesn't exist, root endpoint already defined above
    pass

