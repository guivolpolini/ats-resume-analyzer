import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from app.routes.analysis import router as analysis_router

load_dotenv()


class VercelPathMiddleware:
    """Restaura o caminho original da requisição na Vercel através do cabeçalho x-matched-path."""
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            raw_matched = headers.get(b"x-matched-path", b"").decode("utf-8")
            if raw_matched and not raw_matched.endswith(".py"):
                scope["path"] = raw_matched
        await self.app(scope, receive, send)


app = FastAPI(
    title="ATS Resume Analyzer API",
    description="API para análise e otimização de currículos com IA",
    version="0.1.0",
)

# Adiciona middleware de restauração de path da Vercel
app.add_middleware(VercelPathMiddleware)

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

# Diretório de arquivos estáticos compilados empacotados com a aplicação
static_dir = Path(__file__).resolve().parent / "static"

# Monta arquivos de assets estáticos (JS, CSS, imagens)
if (static_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")


@app.get("/health")
def health_check():
    """Health check usado para monitoramento e validação de conexão do frontend."""
    return {"status": "healthy"}


@app.get("/")
def read_root():
    """Retorna o frontend React se compilado, ou mensagem de status da API."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "ok", "service": "ATS Resume Analyzer API"}


@app.get("/{full_path:path}")
def serve_frontend_spa(full_path: str):
    """Serve arquivos estáticos adicionais ou o index.html para roteamento SPA."""
    file_path = static_dir / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "ok", "service": "ATS Resume Analyzer API"}
