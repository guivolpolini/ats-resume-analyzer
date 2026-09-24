import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analysis import router as analysis_router

load_dotenv()

app = FastAPI(
    title="ATS Resume Analyzer API",
    description="API para análise e otimização de currículos com IA",
    version="0.1.0",
)

# Origens permitidas
allowed_origins_env = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

# Garante inclusão de origens de desenvolvimento locais comuns
for local_origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
    if local_origin not in origins:
        origins.append(local_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra rotas da aplicação
app.include_router(analysis_router)


@app.get("/")
def read_root():
    """Endpoint simples para confirmar que a API está no ar."""
    return {"status": "ok", "service": "ATS Resume Analyzer API"}


@app.get("/health")
def health_check():
    """Health check usado para monitoramento e validação de conexão do frontend."""
    return {"status": "healthy"}
