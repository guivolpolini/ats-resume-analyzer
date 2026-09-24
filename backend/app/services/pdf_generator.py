import io
from typing import Any, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    ListFlowable,
    ListItem,
)


def generate_resume_pdf(resume_data: Dict[str, Any]) -> io.BytesIO:
    """Gera um PDF elegante e compatível com ATS a partir dos dados do currículo otimizado."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    styles = getSampleStyleSheet()

    # Estilos customizados
    name_style = ParagraphStyle(
        "CandidateName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),  # slate-900
        alignment=1,  # Center
    )

    contact_style = ParagraphStyle(
        "CandidateContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569"),  # slate-600
        alignment=1,  # Center
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=3,
        textTransform="uppercase",
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),  # slate-700
    )

    job_title_style = ParagraphStyle(
        "JobTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
    )

    job_meta_style = ParagraphStyle(
        "JobMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#64748b"),
    )

    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        leftIndent=14,
        firstLineIndent=-10,
    )

    story = []

    # Cabeçalho: Nome e Contatos
    full_name = resume_data.get("full_name") or "Candidato"
    contact_info = resume_data.get("contact_info") or ""

    story.append(Paragraph(full_name, name_style))
    if contact_info:
        story.append(Spacer(1, 3))
        story.append(Paragraph(contact_info, contact_style))

    story.append(Spacer(1, 8))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#cbd5e1"),
            spaceBefore=2,
            spaceAfter=8,
        )
    )

    # Resumo Profissional
    summary = resume_data.get("professional_summary")
    if summary:
        story.append(Paragraph("Resumo Profissional", section_heading))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#e2e8f0"),
                spaceBefore=1,
                spaceAfter=5,
            )
        )
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 6))

    # Habilidades Técnicas
    skills = resume_data.get("skills")
    if skills and isinstance(skills, list):
        story.append(Paragraph("Habilidades & Competências", section_heading))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#e2e8f0"),
                spaceBefore=1,
                spaceAfter=5,
            )
        )
        for skill in skills:
            story.append(Paragraph(f"• {skill}", bullet_style))
        story.append(Spacer(1, 6))

    # Experiências Profissionais
    experiences = resume_data.get("experiences")
    if experiences and isinstance(experiences, list):
        story.append(Paragraph("Experiência Profissional", section_heading))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#e2e8f0"),
                spaceBefore=1,
                spaceAfter=5,
            )
        )

        for exp in experiences:
            role = exp.get("role", "")
            company = exp.get("company", "")
            period = exp.get("period", "")

            role_line = f"<b>{role}</b>"
            meta_line = f"{company} | {period}" if company and period else (company or period)

            story.append(Paragraph(role_line, job_title_style))
            if meta_line:
                story.append(Paragraph(meta_line, job_meta_style))
            story.append(Spacer(1, 2))

            highlights = exp.get("highlights", [])
            if isinstance(highlights, list):
                for h in highlights:
                    story.append(Paragraph(f"• {h}", bullet_style))
            story.append(Spacer(1, 6))

    # Formação Acadêmica
    education = resume_data.get("education")
    if education and isinstance(education, list):
        story.append(Paragraph("Formação Acadêmica", section_heading))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#e2e8f0"),
                spaceBefore=1,
                spaceAfter=5,
            )
        )

        for edu in education:
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            period = edu.get("period", "")

            edu_text = f"<b>{degree}</b> — {institution} ({period})" if period else f"<b>{degree}</b> — {institution}"
            story.append(Paragraph(edu_text, body_style))
            story.append(Spacer(1, 3))

    doc.build(story)
    buffer.seek(0)
    return buffer
