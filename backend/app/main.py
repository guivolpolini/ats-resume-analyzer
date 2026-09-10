from fastapi import FastAPI

app = FastAPI(
    title="ATS Resume Analyzer API",
    description="API para análise e otimização de currículos com IA",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Endpoint simples para confirmar que a API está no ar."""
    return {"status": "ok", "service": "ATS Resume Analyzer API"}


@app.get("/health")
def health_check():
    """Health check usado para monitoramento/deploy."""
    return {"status": "healthy"}
