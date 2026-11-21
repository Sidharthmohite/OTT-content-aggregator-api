from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.auth import router as auth_router
from src.api.titles import router as titles_router

app = FastAPI(
    title="OTT Content Aggregator API",
    description="API to explore movies, web series and OTT platforms",
    version="1.0.0",
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(titles_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "Welcome to OTT Content Aggregator API"}


@app.get("/health")
def health():
    return {"status": "healthy"}