import io
import pytest
from docx import Document
from fastapi import HTTPException, UploadFile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet

from app.utils.extractor import (
    extract_resume_text,
    extract_text_from_docx,
    extract_text_from_pdf,
)


def create_sample_pdf_bytes(text: str) -> bytes:
    """Cria um PDF simples em memória para testes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(text, styles["Normal"])]
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def create_sample_docx_bytes(text: str) -> bytes:
    """Cria um DOCX simples em memória para testes."""
    buffer = io.BytesIO()
    doc = Document()
    doc.add_paragraph(text)
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def test_extract_text_from_pdf_success():
    expected_text = "Desenvolvedor Python com experiência em FastAPI e Docker."
    pdf_bytes = create_sample_pdf_bytes(expected_text)

    result = extract_text_from_pdf(pdf_bytes)
    assert "Desenvolvedor Python" in result


def test_extract_text_from_docx_success():
    expected_text = "Engenheiro de Software com foco em sistemas distribuídos."
    docx_bytes = create_sample_docx_bytes(expected_text)

    result = extract_text_from_docx(docx_bytes)
    assert "Engenheiro de Software" in result


@pytest.mark.anyio
async def test_extract_resume_text_invalid_extension():
    upload_file = UploadFile(filename="curriculo.txt", file=io.BytesIO(b"conteudo"))
    with pytest.raises(HTTPException) as exc_info:
        await extract_resume_text(upload_file)

    assert exc_info.value.status_code == 400
    assert "Formato de arquivo inválido" in exc_info.value.detail


@pytest.mark.anyio
async def test_extract_resume_text_empty_file():
    upload_file = UploadFile(filename="curriculo.pdf", file=io.BytesIO(b""))
    with pytest.raises(HTTPException) as exc_info:
        await extract_resume_text(upload_file)

    assert exc_info.value.status_code == 400
    assert "Arquivo enviado está vazio" in exc_info.value.detail
