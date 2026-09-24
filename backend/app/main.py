import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra rotas da aplicação
app.include_router(analysis_router)


# Localiza a pasta dist do frontend compilado
possible_dist_dirs = [
    Path(__file__).resolve().parent.parent / "dist",  # backend/dist
    Path(__file__).resolve().parent.parent.parent / "dist",  # dist raiz
    Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",  # frontend/dist
]

dist_dir = next((d for d in possible_dist_dirs if (d / "index.html").exists()), None)

# Monta arquivos de assets estáticos (JS, CSS, imagens) se existirem
if dist_dir and (dist_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")


@app.get("/health")
def health_check():
    """Health check usado para monitoramento e validação de conexão do frontend."""
    return {"status": "healthy"}


@app.get("/")
def read_root():
    """Retorna o frontend React se compilado, ou mensagem de status da API."""
    if dist_dir and (dist_dir / "index.html").exists():
        return FileResponse(dist_dir / "index.html")
    return {"status": "ok", "service": "ATS Resume Analyzer API"}


@app.get("/{full_path:path}")
def serve_frontend_spa(full_path: str):
    """Serve arquivos estáticos adicionais ou o index.html para roteamento SPA."""
    if dist_dir:
        file_path = dist_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        index_file = dist_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
    return {"status": "ok", "service": "ATS Resume Analyzer API"}
