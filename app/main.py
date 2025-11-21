"""FastAPI application for AI-powered Google Slides generation - Fixed version"""
import sys
import logging

# Configure logging to stderr (Vercel captures this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("Starting application...")
logger.info("=" * 60)

# Step 1: Import FastAPI (most critical)
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    logger.info("✅ FastAPI imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import FastAPI: {e}", exc_info=True)
    sys.exit(1)

# Step 2: Create app
try:
    app = FastAPI(
        title="AI Google Slides Generator",
        description="AI Agent that generates Google Slides presentations",
        version="2.0.0"
    )
    logger.info("✅ FastAPI app created")
except Exception as e:
    logger.error(f"❌ Failed to create FastAPI app: {e}", exc_info=True)
    sys.exit(1)

# Step 3: Add basic routes (no dependencies on other modules)
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

logger.info("✅ Basic routes added")

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

# Final check
if handler is None:
    logger.error("❌ CRITICAL: Handler is None!")
    sys.exit(1)

logger.info("=" * 60)
logger.info("Application startup complete!")
logger.info(f"Handler type: {type(handler)}")
logger.info("=" * 60)
