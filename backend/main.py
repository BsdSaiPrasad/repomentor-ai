from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RepoMentor AI",
    description="GenAI TA Toolkit for CMSC389A",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "RepoMentor AI"}

@app.get("/api/v1/status")
def status():
    return {"status": "running", "version": "0.1.0"}

@app.post("/api/v1/review")
def review_repo():
    return {"status": "not_implemented"}
