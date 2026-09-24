from typing import Any, Dict
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.services.gemini_service import analyze_resume_with_gemini
from app.services.pdf_generator import generate_resume_pdf
from app.utils.extractor import extract_resume_text

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post("/analyze")
async def analyze_resume_endpoint(
    file: UploadFile = File(..., description="Arquivo do currículo (.pdf ou .docx)"),
    job_description: str = Form(..., description="Texto da descrição da vaga de trabalho"),
):
    """Analisa um currículo contra uma vaga usando IA (Gemini Pro)."""
    cleaned_job = job_description.strip()
    if len(cleaned_job) < 20:
        raise HTTPException(
            status_code=400,
            detail="A descrição da vaga fornecida é muito curta (mínimo de 20 caracteres).",
        )

    # 1. Extrair texto do PDF ou DOCX
    resume_text = await extract_resume_text(file)

    if len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="O currículo fornecido contém muito pouco texto legível para uma análise satisfatória.",
        )

    # 2. Executar análise via Gemini Pro
    try:
        analysis_result = analyze_resume_with_gemini(
            resume_text=resume_text,
            job_description=cleaned_job,
        )
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno durante a análise do currículo: {str(exc)}",
        )

    return analysis_result


@router.post("/generate-pdf")
async def generate_pdf_endpoint(payload: Dict[str, Any]):
    """Gera e retorna o PDF do currículo otimizado para download."""
    # Se o payload vier encapsulado com a chave 'optimized_resume' ou diretamente
    resume_data = payload.get("optimized_resume", payload)

    if not isinstance(resume_data, dict) or not resume_data:
        raise HTTPException(
            status_code=400,
            detail="Dados inválidos para geração do currículo em PDF.",
        )

    pdf_buffer = generate_resume_pdf(resume_data)

    filename = "curriculo_otimizado.pdf"
    candidate_name = resume_data.get("full_name")
    if candidate_name and isinstance(candidate_name, str):
        safe_name = "".join(c for c in candidate_name if c.isalnum() or c in (" ", "_", "-")).strip()
        if safe_name:
            filename = f"curriculo_{safe_name.replace(' ', '_').lower()}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
