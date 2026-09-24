import io
from app.services.pdf_generator import generate_resume_pdf


def test_generate_resume_pdf_valid():
    """Gera um PDF válido a partir de dados estruturados do currículo."""
    sample_data = {
        "full_name": "João da Silva",
        "contact_info": "joao.silva@email.com | (11) 99999-8888 | linkedin.com/in/joaosilva",
        "professional_summary": "Desenvolvedor de Software com 4 anos de experiência com Python e FastAPI.",
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "experiences": [
            {
                "role": "Desenvolvedor Backend",
                "company": "Tech Solutions",
                "period": "Jan/2022 - Presente",
                "highlights": [
                    "Desenvolveu microserviços escaláveis com FastAPI e Celery.",
                    "Otimizou consultas SQL reduzindo tempo de resposta em 35%.",
                ],
            }
        ],
        "education": [
            {
                "degree": "Bacharelado em Ciência da Computação",
                "institution": "Universidade de São Paulo",
                "period": "2018 - 2021",
            }
        ],
    }

    pdf_buffer = generate_resume_pdf(sample_data)

    assert isinstance(pdf_buffer, io.BytesIO)
    content = pdf_buffer.getvalue()
    assert len(content) > 1000
    assert content.startswith(b"%PDF")


def test_generate_resume_pdf_minimal():
    """Valida geração de PDF com apenas os campos essenciais sem quebrar."""
    minimal_data = {
        "full_name": "Maria Oliveira",
        "contact_info": "maria@email.com",
    }

    pdf_buffer = generate_resume_pdf(minimal_data)
    assert isinstance(pdf_buffer, io.BytesIO)
    content = pdf_buffer.getvalue()
    assert content.startswith(b"%PDF")
