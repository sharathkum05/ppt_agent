"""Minimal FastAPI app for Vercel - bootstrap version"""
import sys
import logging

# Configure logging to stderr (Vercel captures this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

logger.info("=" * 50)
logger.info("Starting application bootstrap...")
logger.info("=" * 50)

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

# Step 3: Add basic routes
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

# Step 4: Create handler (CRITICAL for Vercel)
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
    logger.info("✅ Mangum handler created")
except Exception as e:
    logger.error(f"❌ Failed to create Mangum handler: {e}", exc_info=True)
    # Last resort - create minimal ASGI app
    async def minimal_handler(scope, receive, send):
        from starlette.responses import JSONResponse
        response = JSONResponse({"error": "Handler initialization failed"})
        await response(scope, receive, send)
    handler = minimal_handler
    logger.warning("⚠️ Using fallback handler")

logger.info("=" * 50)
logger.info("Application bootstrap complete!")
logger.info(f"Handler type: {type(handler)}")
logger.info("=" * 50)

