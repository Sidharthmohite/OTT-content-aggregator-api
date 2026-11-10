
from fastapi import FastAPI
from src.api.titles import router as titles_router 

app = FastAPI(
    title="OTT Content Aggregator API",
    description="API to explore movies, web series and OTT platforms",
    version="1.0.0"
)app.include_router(titles_router) 

@app.get("/")
def home():
    return {
        "message": "Welcome to OTT Content Aggregator API"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
   