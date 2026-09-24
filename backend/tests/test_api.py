from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from tests.test_extractor import create_sample_pdf_bytes

client = TestClient(app)


def test_health_check():
    """Valida o endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root():
    """Valida o endpoint raiz."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"


def test_analyze_job_description_too_short():
    """Valida erro 400 quando a descrição da vaga é muito curta."""
    pdf_bytes = create_sample_pdf_bytes("Currículo com conteúdo relevante para análise técnica.")
    response = client.post(
        "/api/analyze",
        data={"job_description": "Vaga Dev"},  # Menor que 20 caracteres
        files={"file": ("curriculo.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 400
    assert "descrição da vaga fornecida é muito curta" in response.json()["detail"]


@patch("app.routes.analysis.analyze_resume_with_gemini")
def test_analyze_success_with_mock(mock_analyze):
    """Valida fluxo completo do endpoint /api/analyze com retorno mockado do Gemini."""
    mock_payload = {
        "ats_score": 88,
        "summary": "Candidato possui excelente aderência com a vaga de backend.",
        "matched_keywords": ["Python", "FastAPI"],
        "missing_keywords": ["Docker"],
        "strengths": ["Experiência sólida em APIs REST"],
        "improvements": ["Destacar conhecimentos em containerização"],
        "optimized_resume": {
            "full_name": "Candidato Teste",
            "contact_info": "teste@email.com",
            "professional_summary": "Desenvolvedor Backend experiente.",
            "skills": ["Python", "FastAPI"],
            "experiences": [],
            "education": [],
        },
    }
    mock_analyze.return_value = mock_payload

    # Mais de 50 caracteres para passar na validação de tamanho mínimo
    pdf_text = "João Silva - Engenheiro de Software com experiência em Python, FastAPI e desenvolvimento de APIs REST."
    pdf_bytes = create_sample_pdf_bytes(pdf_text)

    response = client.post(
        "/api/analyze",
        data={"job_description": "Desenvolvedor Python Backend com experiência em APIs REST e FastAPI."},
        files={"file": ("curriculo.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ats_score"] == 88
    assert "FastAPI" in data["matched_keywords"]
    assert data["optimized_resume"]["full_name"] == "Candidato Teste"


def test_generate_pdf_endpoint():
    """Valida geração do PDF através do endpoint /api/generate-pdf."""
    payload = {
        "optimized_resume": {
            "full_name": "Carlos Souza",
            "contact_info": "carlos@email.com",
            "professional_summary": "Especialista em automação e dados.",
            "skills": ["Python", "Pandas"],
            "experiences": [],
            "education": [],
        }
    }

    response = client.post("/api/generate-pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
