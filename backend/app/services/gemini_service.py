"""Serviço de integração com Google Gemini Pro para análise e otimização de currículos."""

import json
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

load_dotenv()

# Modelos recomendados e estáveis (gemini-3.5-flash-lite é o mais rápido e estável no tier gratuito)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash"]

SYSTEM_PROMPT_ATS = """Você é um especialista sênior em Recrutamento e Seleção Técnica e Sistemas de Rastreamento de Candidatos (ATS - Applicant Tracking Systems).

REGRA CRÍTICA INEGOCIÁVEL (ANTI-ALUCINAÇÃO):
- Você NUNCA pode inventar ou presumir qualificações, tecnologias, ferramentas, certificações, empresas ou experiências que não estejam explicitamente presentes no currículo original.
- Você só pode reorganizar, reformular com clareza e verbos de ação orientados a impacto, e alinhar o vocabulário com a descrição da vaga quando o candidato já possuir tal competência.
- Se uma tecnologia ou habilidade pedida na vaga NÃO estiver presente no currículo, ela DEVE ser listada obrigatoriamente como palavra-chave ausente (missing_keywords). NUNCA adicione essa competência ao currículo otimizado.
"""


# ---- Schemas Estruturados (Pydantic) ----

class ResumeAnalysis(BaseModel):
    """Schema estruturado para o diagnóstico de aderência ATS do currículo."""
    ats_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Pontuação de compatibilidade ATS de 0 a 100 calculada com base na vaga",
    )
    matched_keywords: List[str] = Field(
        default_factory=list,
        description="Palavras-chave e habilidades da vaga que foram encontradas no currículo",
    )
    missing_keywords: List[str] = Field(
        default_factory=list,
        description="Palavras-chave e requisitos da vaga que estão ausentes no currículo",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Principais pontos fortes e aderências do candidato frente aos requisitos da vaga",
    )
    improvements: List[str] = Field(
        default_factory=list,
        description="Pontos e lacunas onde o candidato precisa evoluir ou clarificar no currículo",
    )


class OptimizedResume(BaseModel):
    """Schema estruturado para a versão reescrita e otimizada do currículo."""
    optimized_text: str = Field(
        ...,
        description="Currículo completo reescrito, formatado e alinhado aos termos da vaga sem inventar dados",
    )
    changes_summary: List[str] = Field(
        default_factory=list,
        description="Resumo claro das reformulações, reorganizações e melhorias aplicadas no currículo",
    )


# ---- Inicialização e Helpers ----

def get_gemini_client() -> genai.Client:
    """Instancia o cliente oficial do Google Gemini utilizando a chave configurada no ambiente.

    Raises:
        ValueError: Se GEMINI_API_KEY não estiver definida ou estiver vazia.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Variável de ambiente GEMINI_API_KEY não configurada no arquivo .env.")
    return genai.Client(api_key=api_key)


def clean_json_text(raw_text: str) -> str:
    """Sanitiza o texto de resposta removendo marcações de bloco de código Markdown se houver."""
    cleaned = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def _call_gemini_with_fallback(
    client: genai.Client,
    contents: str,
    response_schema: Any,
    temperature: float = 0.2,
) -> str:
    """Executa a chamada à API do Gemini com suporte a fallback de modelos estáveis e tratamento de erros."""
    models_to_try = [DEFAULT_MODEL]
    for model in FALLBACK_MODELS:
        if model not in models_to_try:
            models_to_try.append(model)

    last_error: Optional[Exception] = None

    for model_name in models_to_try:
        try:
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT_ATS,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=temperature,
            )
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            if response and response.text:
                return response.text
        except errors.ClientError as ce:
            error_str = str(ce).lower()
            if "api_key" in error_str or "invalid" in error_str or "403" in error_str:
                raise ValueError("Chave GEMINI_API_KEY inválida ou sem permissão de acesso.") from ce
            if "429" in error_str or "quota" in error_str or "resource_exhausted" in error_str:
                raise RuntimeError("Limite de cota da API do Google Gemini excedido. Tente novamente mais tarde.") from ce
            last_error = ce
        except errors.APIError as ae:
            error_str = str(ae).lower()
            if "429" in error_str or "quota" in error_str:
                raise RuntimeError("Limite de cota da API do Google Gemini excedido. Tente novamente mais tarde.") from ae
            last_error = ae
        except Exception as e:
            last_error = e

    error_message = str(last_error) if last_error else "Resposta vazia da API do Gemini"
    raise RuntimeError(f"Falha na comunicação com a API do Google Gemini: {error_message}")


# ---- Funções Principais de Integração ----

def analyze_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Analisa o currículo contra a descrição da vaga usando o Gemini Pro com saída estruturada.

    Args:
        resume_text: Texto extraído do currículo do candidato.
        job_description: Texto contendo os requisitos e descrição da vaga.

    Returns:
        Dicionário contendo ats_score, matched_keywords, missing_keywords, strengths e improvements.

    Raises:
        ValueError: Em caso de parâmetros inválidos ou chave de API ausente/inválida.
        RuntimeError: Em caso de erro na comunicação ou parse da resposta da IA.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("O texto do currículo não pode estar vazio para a análise.")
    if not job_description or not job_description.strip():
        raise ValueError("A descrição da vaga não pode estar vazia para a análise.")

    client = get_gemini_client()

    prompt = f"""Analise tecnicamente o currículo em relação aos requisitos da vaga.

=== DESCRIÇÃO DA VAGA ===
{job_description.strip()}

=== CURRÍCULO DO CANDIDATO ===
{resume_text.strip()}

Identifique a pontuação ATS (0-100), as palavras-chave da vaga presentes e ausentes, os pontos fortes reais e as oportunidades de melhoria.
Lembre-se: NUNCA presuma ou invente competências não citadas no currículo original.
"""

    raw_response = _call_gemini_with_fallback(
        client=client,
        contents=prompt,
        response_schema=ResumeAnalysis,
        temperature=0.2,
    )

    try:
        sanitized_json = clean_json_text(raw_response)
        validated_data = ResumeAnalysis.model_validate_json(sanitized_json)
        return validated_data.model_dump()
    except Exception as exc:
        raise RuntimeError(f"Falha ao validar a estrutura da resposta da análise do Gemini: {str(exc)}") from exc


def generate_optimized_resume(
    resume_text: str,
    job_description: str,
    analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Gera uma versão otimizada do currículo com base na análise e descrição da vaga.

    Args:
        resume_text: Texto original do currículo do candidato.
        job_description: Texto da vaga alvo.
        analysis: Dicionário opcional contendo a análise prévia (ex: missing_keywords, strengths).

    Returns:
        Dicionário com 'optimized_text' (texto reescrito) e 'changes_summary' (lista de alterações).

    Raises:
        ValueError: Em caso de entradas vazias ou chave de API inválida.
        RuntimeError: Em caso de erro de API ou inconsistência no formato de saída.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("O texto do currículo original é obrigatório para otimização.")
    if not job_description or not job_description.strip():
        raise ValueError("A descrição da vaga é obrigatória para otimização.")

    client = get_gemini_client()

    analysis_context = ""
    if analysis:
        missing = ", ".join(analysis.get("missing_keywords", [])) or "Nenhuma"
        strengths = ", ".join(analysis.get("strengths", [])) or "Geral"
        analysis_context = f"""
=== DADOS DA ANÁLISE PRÉVIA ===
- Palavras-chave ausentes (NÃO INVENTAR NO CURRÍCULO): {missing}
- Pontos fortes a valorizar: {strengths}
"""

    prompt = f"""Reescreva e otimize o currículo do candidato para maximizar o alinhamento com a vaga.

=== DESCRIÇÃO DA VAGA ===
{job_description.strip()}

=== CURRÍCULO ORIGINAL ===
{resume_text.strip()}
{analysis_context}
INSTRUÇÕES ESPECÍFICAS:
1. Reorganize e aprimore a redação de cada experiência, destacando resultados e utilizando termos da vaga compatíveis com o que o candidato realmente fez.
2. NUNCA invente ferramentas, cargos, datas ou responsabilidades não presentes no currículo original.
3. Forneça o texto completo e polido do currículo em 'optimized_text'.
4. Forneça a lista de principais melhorias aplicadas em 'changes_summary'.
"""

    raw_response = _call_gemini_with_fallback(
        client=client,
        contents=prompt,
        response_schema=OptimizedResume,
        temperature=0.3,
    )

    try:
        sanitized_json = clean_json_text(raw_response)
        validated_data = OptimizedResume.model_validate_json(sanitized_json)
        return validated_data.model_dump()
    except Exception as exc:
        raise RuntimeError(f"Falha ao validar a estrutura do currículo otimizado gerado pelo Gemini: {str(exc)}") from exc


# ---- Alias de compatibilidade ----

def analyze_resume_with_gemini(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Alias para manter retrocompatibilidade com endpoints que chamavam analyze_resume_with_gemini."""
    return analyze_resume(resume_text=resume_text, job_description=job_description)
