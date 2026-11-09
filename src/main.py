
from fastapi import FastAPI

app = FastAPI(
    title="OTT Content Aggregator API",
    description="API to explore movies, web series and OTT platforms",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to OTT Content Aggregator API"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
