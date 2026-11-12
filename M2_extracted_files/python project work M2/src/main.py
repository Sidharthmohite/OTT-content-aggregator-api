"""Main entry point for the OTT Content Aggregator API.
"""

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    HAS_FASTAPI = True
except ImportError:  # pragma: no cover
    HAS_FASTAPI = False

from src.core.config import settings

if HAS_FASTAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Unified OTT Content Aggregator API catalog service.",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Auth Router (M2)
    from src.api.routes.auth import router as auth_router
    if auth_router:
        app.include_router(auth_router)

    @app.get("/", tags=["General"])
    def root() -> dict[str, str]:
        """Root welcome endpoint."""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "docs_url": "/docs",
        }

    @app.get("/health", tags=["General"])
    def health_check() -> dict[str, str]:
        """Application health check endpoint."""
        return {"status": "healthy"}

else:  # pragma: no cover
    app = None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
