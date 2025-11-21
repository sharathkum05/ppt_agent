"""FastAPI application for AI-powered Google Slides generation - Fixed version"""
import sys
import logging
import traceback

# Print to stderr immediately (Vercel captures this)
print("=" * 60, file=sys.stderr)
print("Starting application...", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Configure logging to stderr (Vercel captures this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize app and handler as None - will be set below
app = None
handler = None

# Step 1: Import FastAPI (most critical) - NEVER exit, always create handler
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    print("✅ FastAPI imported successfully", file=sys.stderr)
    logger.info("✅ FastAPI imported successfully")
except Exception as e:
    print(f"❌ Failed to import FastAPI: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    logger.error(f"❌ Failed to import FastAPI: {e}", exc_info=True)
    # Don't exit - create minimal handler instead

# Step 2: Create app - NEVER exit, always create handler
try:
    if FastAPI:
        app = FastAPI(
            title="AI Google Slides Generator",
            description="AI Agent that generates Google Slides presentations",
            version="2.0.0"
        )
        print("✅ FastAPI app created", file=sys.stderr)
        logger.info("✅ FastAPI app created")
except Exception as e:
    print(f"❌ Failed to create FastAPI app: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    logger.error(f"❌ Failed to create FastAPI app: {e}", exc_info=True)
    # Don't exit - will create minimal handler

# Step 3: Add basic routes (no dependencies on other modules)
# Only add routes if app was created successfully
if app:
    try:
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "status": "ok",
                "message": "AI Google Slides Generator API",
                "version": "2.0.0"
            }

        @app.get("/health")
        async def health():
            """Health check"""
            return {"status": "healthy"}
        
        print("✅ Basic routes added", file=sys.stderr)
        logger.info("✅ Basic routes added")
    except Exception as e:
        print(f"⚠️ Failed to add basic routes: {e}", file=sys.stderr)
        logger.warning(f"⚠️ Failed to add basic routes: {e}")
else:
    print("⚠️ App not created, skipping routes", file=sys.stderr)
    logger.warning("⚠️ App not created, skipping routes")

# Step 4: Try to import and add full functionality
try:
    from app.config import settings
    from app.utils.auth import get_google_services
    from app.services.agent_service import AgentService
    from app.services.slides_service import SlidesService
    from app.services.drive_service import DriveService
    from app.models.schemas import PresentationRequest, PresentationResponse
    
    # Initialize services (will be done on first request)
    agent_service = None
    slides_service = None
    drive_service = None
    
    def initialize_services():
        """Initialize Google and Agent services"""
        global agent_service, slides_service, drive_service
        try:
            settings.validate()
            slides_api, drive_api = get_google_services()
            slides_service = SlidesService(slides_api)
            drive_service = DriveService(drive_api)
            agent_service = AgentService(slides_service, drive_service)
            logger.info("✅ Services initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}", exc_info=True)
            raise
    
    @app.post("/generate-presentation")
    async def generate_presentation(request: PresentationRequest):
        """Generate a Google Slides presentation"""
        if agent_service is None or slides_service is None or drive_service is None:
            try:
                initialize_services()
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize services: {str(e)}"
                )
        
        result = agent_service.generate_presentation(request.prompt)
        return PresentationResponse(
            presentation_id=result["presentation_id"],
            shareable_link=result["shareable_link"],
            title=result["title"],
            slide_count=result["slide_count"]
        )
    
    @app.get("/debug/env")
    async def debug_env():
        """Debug endpoint to check environment variables"""
        import os
        env_status = {
            "anthropic": {
                "ANTHROPIC_API_KEY": "SET" if os.getenv("ANTHROPIC_API_KEY") else "MISSING",
            },
            "google_credentials": {
                "project_id": "SET" if (os.getenv("GOOGLE_PROJECT_ID") or os.getenv("project_id")) else "MISSING",
                "private_key": "SET" if (os.getenv("GOOGLE_PRIVATE_KEY") or os.getenv("private_key")) else "MISSING",
                "client_email": "SET" if (os.getenv("GOOGLE_CLIENT_EMAIL") or os.getenv("client_email")) else "MISSING",
                "token_uri": "SET" if (os.getenv("GOOGLE_TOKEN_URI") or os.getenv("token_uri")) else "MISSING",
            },
            "application": {
                "DEFAULT_PRESENTATION_ID": os.getenv("DEFAULT_PRESENTATION_ID", "MISSING"),
                "GOOGLE_DRIVE_FOLDER_ID": os.getenv("GOOGLE_DRIVE_FOLDER_ID", "MISSING"),
            }
        }
        return env_status
    
    logger.info("✅ Full functionality imported and routes added")
    
except Exception as e:
    logger.warning(f"⚠️ Could not import full functionality: {e}")
    logger.warning("⚠️ App will run in basic mode (root and health endpoints only)")
    # App still works with basic routes

# Step 5: Create handler (CRITICAL for Vercel)
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
    logger.info("✅ Mangum handler created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create Mangum handler: {e}", exc_info=True)
    # Last resort - create minimal ASGI app
    async def minimal_handler(scope, receive, send):
        from starlette.responses import JSONResponse
        response = JSONResponse({"error": "Handler initialization failed", "detail": str(e)})
        await response(scope, receive, send)
    handler = minimal_handler
    logger.warning("⚠️ Using fallback handler")

# Final check - ALWAYS ensure handler exists (NEVER exit)
if handler is None:
    print("❌ CRITICAL: Handler is None! Creating emergency handler", file=sys.stderr)
    logger.error("❌ CRITICAL: Handler is None! Creating emergency handler")
    
    # Emergency fallback handler
    async def emergency_handler(scope, receive, send):
        from starlette.responses import JSONResponse
        response = JSONResponse(
            {"error": "Handler not properly initialized", "status": "error"},
            status_code=500
        )
        await response(scope, receive, send)
    handler = emergency_handler
    print("✅ Emergency handler created", file=sys.stderr)

print("=" * 60, file=sys.stderr)
print("Application startup complete!", file=sys.stderr)
print(f"Handler type: {type(handler)}", file=sys.stderr)
print(f"App type: {type(app) if app else 'None'}", file=sys.stderr)
print("=" * 60, file=sys.stderr)

logger.info("=" * 60)
logger.info("Application startup complete!")
logger.info(f"Handler type: {type(handler)}")
logger.info(f"App type: {type(app) if app else 'None'}")
logger.info("=" * 60)
