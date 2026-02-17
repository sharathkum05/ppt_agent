"""FastAPI application for AI-powered Google Slides generation - Fixed version"""
import os
import sys
import logging
import traceback

# CRITICAL: Wrap everything in try-except to prevent Python from exiting
# Vercel requires a handler to be defined, so we MUST ensure it exists no matter what

# Initialize app and handler as None - will be set below
app = None
handler = None
FastAPI_available = False
logger = None

# Create a minimal emergency handler FIRST (before any imports)
# This ensures handler is ALWAYS defined, even if everything else fails
async def emergency_handler(scope, receive, send):
    """Emergency fallback handler - always available"""
    try:
        from starlette.responses import JSONResponse
        response = JSONResponse(
            {"error": "Application initialization failed", "status": "error"},
            status_code=500
        )
    except Exception:
        # If even JSONResponse fails, use plain text
        from starlette.responses import PlainTextResponse
        response = PlainTextResponse("Internal Server Error", status_code=500)
    await response(scope, receive, send)

# Set handler to emergency handler initially (will be upgraded if possible)
handler = emergency_handler

try:
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
    logger.info("Logger initialized")
except Exception as e:
    # If logging fails, at least handler is defined
    pass

# Step 1: Import FastAPI (most critical) - NEVER exit, always create handler
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    FastAPI_available = True
    if logger:
        logger.info("✅ FastAPI imported successfully")
    print("✅ FastAPI imported successfully", file=sys.stderr)
except Exception as e:
    FastAPI_available = False
    print(f"❌ Failed to import FastAPI: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    if logger:
        logger.error(f"❌ Failed to import FastAPI: {e}", exc_info=True)
        # Don't exit - handler already defined

# Step 2: Create app - NEVER exit, always create handler
if FastAPI_available:
    try:
        app = FastAPI(
            title="AI Google Slides Generator",
            description="AI Agent that generates Google Slides presentations",
            version="2.0.0"
        )
        print("✅ FastAPI app created", file=sys.stderr)
        if logger:
            logger.info("✅ FastAPI app created")
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        if logger:
            logger.error(f"❌ Failed to create FastAPI app: {e}", exc_info=True)
        # Create a minimal FastAPI app as fallback (required for uvicorn)
        try:
            app = FastAPI(title="PPT Agent (Minimal Mode)", version="1.0.0")
            print("✅ Created minimal FastAPI app as fallback", file=sys.stderr)
        except Exception:
            # If even minimal app fails, app will be None (handled below)
            pass
else:
    print("⚠️ FastAPI not available, will use minimal handler", file=sys.stderr)
    if logger:
        logger.warning("⚠️ FastAPI not available, will use minimal handler")

# Step 3: Add CORS and basic routes (no dependencies on other modules)
# Only add routes if app was created successfully
if app:
    # Allow frontend (localhost + Vercel) to call the API
    try:
        from fastapi.middleware.cors import CORSMiddleware
        _origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        _frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
        if _frontend_url and _frontend_url not in _origins:
            _origins.append(_frontend_url)
        # Allow any Vercel deployment (production + preview URLs)
        _origin_regex = r"^https://[a-zA-Z0-9-_.]+\.vercel\.app$"
        app.add_middleware(
            CORSMiddleware,
            allow_origins=_origins,
            allow_origin_regex=_origin_regex,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        if logger:
            logger.info("✅ CORS middleware added")
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ CORS middleware failed: {e}")
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
        if logger:
            logger.info("✅ Basic routes added")
    except Exception as e:
        print(f"⚠️ Failed to add basic routes: {e}", file=sys.stderr)
        if logger:
            logger.warning(f"⚠️ Failed to add basic routes: {e}")
else:
    print("⚠️ App not created, skipping routes", file=sys.stderr)
    if logger:
        logger.warning("⚠️ App not created, skipping routes")

# Step 4: Try to import and add full functionality (only if app exists)
if app:
    try:
        from fastapi import HTTPException
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
                if logger:
                    logger.info("✅ Services initialized successfully")
            except Exception as e:
                if logger:
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
        
        print("✅ Full functionality imported and routes added", file=sys.stderr)
        if logger:
            logger.info("✅ Full functionality imported and routes added")
        
    except Exception as e:
        print(f"⚠️ Could not import full functionality: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        if logger:
            logger.warning(f"⚠️ Could not import full functionality: {e}")
            logger.warning("⚠️ App will run in basic mode (root and health endpoints only)")
        # App still works with basic routes
else:
    print("⚠️ App not available, skipping full functionality", file=sys.stderr)
    if logger:
        logger.warning("⚠️ App not available, skipping full functionality")

# Step 5: Create handler (CRITICAL for Vercel) - ALWAYS create handler
try:
    from mangum import Mangum
    if app:
        handler = Mangum(app, lifespan="off")
        print("✅ Mangum handler created successfully", file=sys.stderr)
        if logger:
            logger.info("✅ Mangum handler created successfully")
    else:
        # App is None, create minimal handler
        print("⚠️ App is None, using minimal handler", file=sys.stderr)
        async def minimal_handler(scope, receive, send):
            from starlette.responses import JSONResponse
            response = JSONResponse({"error": "FastAPI app not initialized"}, status_code=500)
            await response(scope, receive, send)
        handler = minimal_handler
        print("✅ Minimal handler created", file=sys.stderr)
except Exception as e:
    print(f"❌ Failed to create Mangum handler: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    if logger:
        logger.error(f"❌ Failed to create Mangum handler: {e}", exc_info=True)
    # Handler already set to emergency_handler at top, so we're safe
    print("⚠️ Using emergency handler", file=sys.stderr)
    if logger:
        logger.warning("⚠️ Using emergency handler")

# Final check - ALWAYS ensure app exists (required for uvicorn when running locally)
if app is None and FastAPI_available:
    print("⚠️ App is None but FastAPI is available, creating minimal app", file=sys.stderr)
    try:
        app = FastAPI(title="PPT Agent (Fallback Mode)", version="1.0.0")
        @app.get("/")
        async def root_fallback():
            return {"error": "Application initialization failed", "status": "error"}
        @app.get("/health")
        async def health_fallback():
            return {"status": "error", "message": "Initialization failed"}
        print("✅ Created fallback FastAPI app", file=sys.stderr)
    except Exception as e:
        print(f"❌ Failed to create fallback app: {e}", file=sys.stderr)

# Final check - ALWAYS ensure handler exists (should never be None, but double-check)
if handler is None:
    print("❌ CRITICAL: Handler is None! Using emergency handler", file=sys.stderr)
    if logger:
        logger.error("❌ CRITICAL: Handler is None! Using emergency handler")
    handler = emergency_handler

print("=" * 60, file=sys.stderr)
print("Application startup complete!", file=sys.stderr)
print(f"Handler type: {type(handler)}", file=sys.stderr)
print(f"App type: {type(app) if app else 'None'}", file=sys.stderr)
print("=" * 60, file=sys.stderr)

if logger:
    logger.info("=" * 60)
    logger.info("Application startup complete!")
    logger.info(f"Handler type: {type(handler)}")
    logger.info(f"App type: {type(app) if app else 'None'}")
    logger.info("=" * 60)

# Vercel's runtime checks for `handler` first and does issubclass(handler, BaseHTTPRequestHandler).
# Our handler is a Mangum instance (not a class), so that crashes. Remove `handler` so the
# runtime falls through to the `app` branch and uses our FastAPI ASGI app.
if app is not None:
    try:
        del handler
    except NameError:
        pass
