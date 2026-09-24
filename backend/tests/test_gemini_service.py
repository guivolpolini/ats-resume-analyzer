import json
from unittest.mock import MagicMock, patch
import pytest

from app.services.gemini_service import (
    analyze_resume,
    clean_json_text,
    generate_optimized_resume,
    get_gemini_client,
)


def test_clean_json_text():
    """Valida se clean_json_text remove markdown blocks e espaços extras."""
    plain = '{"key": "value"}'
    assert clean_json_text(plain) == '{"key": "value"}'

    fenced = '```json\n{"key": "value"}\n```'
    assert clean_json_text(fenced) == '{"key": "value"}'


def test_get_gemini_client_missing_key(monkeypatch):
    """Garante que get_gemini_client lança ValueError quando a chave não está definida."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(ValueError) as exc:
        get_gemini_client()
    assert "GEMINI_API_KEY não configurada" in str(exc.value)


def test_analyze_resume_empty_inputs():
    """Valida que entradas vazias disparam ValueError antes de chamar a API."""
    with pytest.raises(ValueError, match="currículo não pode estar vazio"):
        analyze_resume("", "Descrição da vaga")

    with pytest.raises(ValueError, match="vaga não pode estar vazia"):
        analyze_resume("Currículo existente", "")


def test_generate_optimized_resume_empty_inputs():
    """Valida validação de campos vazios para geração do currículo otimizado."""
    with pytest.raises(ValueError, match="currículo original é obrigatório"):
        generate_optimized_resume("", "Descrição da vaga")

    with pytest.raises(ValueError, match="descrição da vaga é obrigatória"):
        generate_optimized_resume("Currículo existente", "")


@patch("app.services.gemini_service.get_gemini_client")
def test_analyze_resume_success(mock_get_client):
    """Testa chamada bem-sucedida de analyze_resume validando schema estruturado."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    sample_output = {
        "ats_score": 85,
        "matched_keywords": ["Python", "FastAPI"],
        "missing_keywords": ["Docker"],
        "strengths": ["Experiência comprovada em APIs assíncronas"],
        "improvements": ["Adicionar projetos práticos com containers"],
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(sample_output)
    mock_client.models.generate_content.return_value = mock_response

    result = analyze_resume("Dev Python com 3 anos de experiência em FastAPI.", "Vaga Python FastAPI e Docker.")

    assert result["ats_score"] == 85
    assert result["matched_keywords"] == ["Python", "FastAPI"]
    assert result["missing_keywords"] == ["Docker"]
    assert len(result["strengths"]) == 1
    assert len(result["improvements"]) == 1


@patch("app.services.gemini_service.get_gemini_client")
def test_generate_optimized_resume_success(mock_get_client):
    """Testa chamada bem-sucedida de generate_optimized_resume validando schema estruturado."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    sample_output = {
        "optimized_text": "João Silva - Engenheiro de Software especializado em Python e FastAPI...",
        "changes_summary": [
            "Reestruturação dos tópicos de experiência com verbos de ação",
            "Destaque de métricas de entrega em FastAPI",
        ],
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(sample_output)
    mock_client.models.generate_content.return_value = mock_response

    result = generate_optimized_resume(
        resume_text="João Silva, dev Python...",
        job_description="Buscamos desenvolvedor Python sênior...",
        analysis={"missing_keywords": ["Kubernetes"], "strengths": ["Python"]},
    )

    assert "João Silva" in result["optimized_text"]
    assert len(result["changes_summary"]) == 2
