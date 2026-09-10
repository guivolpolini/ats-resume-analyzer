import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="ATS Resume Analyzer API",
    description="API para análise e otimização de currículos com IA",
    version="0.1.0",
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Endpoint simples para confirmar que a API está no ar."""
    return {"status": "ok", "service": "ATS Resume Analyzer API"}


@app.get("/health")
def health_check():
    """Health check usado para monitoramento/deploy."""
    return {"status": "healthy"}
